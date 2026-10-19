"""SQLAlchemy implementation of the existing atomic State storage boundary.

Only SQLite is supported/tested. A guard-row UPDATE obtains the database write
lock before loading State, serializing independent connections and processes.
The adapter favors correctness over scale: full State is read each transaction.
"""
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timezone
import os

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, String, create_engine, delete, event, select, update
from sqlalchemy.engine import make_url
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

from .storage import State, StorageUnavailable

TRACK_CHECK = "track IN ('Python', 'SQL', 'Git')"
LEVEL_CHECK = "level IN ('Beginner', 'Intermediate', 'Advanced')"


class Base(DeclarativeBase):
    pass


class TransactionGuard(Base):
    __tablename__ = 'transaction_guard'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    epoch: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    __table_args__ = (CheckConstraint('id = 1'),)


class Account(Base):
    __tablename__ = 'accounts'
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(60), nullable=False)
    password_hash: Mapped[str] = mapped_column(String, nullable=False)
    active_track: Mapped[str] = mapped_column(String, nullable=False)
    onboarded: Mapped[bool] = mapped_column(Boolean(create_constraint=True), nullable=False)
    __table_args__ = (
        CheckConstraint('email = lower(trim(email))'),
        CheckConstraint('length(name) BETWEEN 2 AND 60'),
        CheckConstraint("active_track IN ('Python', 'SQL', 'Git')"),
    )


class Preference(Base):
    __tablename__ = 'preferences'
    account_id: Mapped[str] = mapped_column(ForeignKey('accounts.id'), primary_key=True)
    track: Mapped[str] = mapped_column(String, primary_key=True)
    level: Mapped[str] = mapped_column(String, nullable=False)
    __table_args__ = (CheckConstraint(TRACK_CHECK), CheckConstraint(LEVEL_CHECK))


class AuthSession(Base):
    __tablename__ = 'auth_sessions'
    token_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    account_id: Mapped[str] = mapped_column(ForeignKey('accounts.id'), nullable=False, index=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


def database_url():
    value = os.environ.get('DATABASE_URL')
    if not value:
        raise RuntimeError('Set DATABASE_URL to a SQLite file URL before starting the backend.')
    return value


class SQLStorage:
    def __init__(self, url):
        parsed = make_url(url)
        if parsed.drivername not in {'sqlite', 'sqlite+pysqlite'} or not parsed.database or parsed.database == ':memory:':
            raise ValueError('This stage requires a file-backed SQLite DATABASE_URL; other databases are not verified.')
        self.engine = create_engine(parsed, echo=False, hide_parameters=True, connect_args={
            'check_same_thread': False, 'timeout': 30, 'autocommit': False,
        })

        @event.listens_for(self.engine, 'connect')
        def foreign_keys(connection, _):
            # Necessary SQLite connection setup; all data reads/writes use ORM.
            previous = connection.autocommit
            connection.autocommit = True
            cursor = connection.cursor()
            cursor.execute('PRAGMA foreign_keys=ON')
            cursor.close()
            connection.autocommit = previous

        Base.metadata.create_all(self.engine)
        try:
            with Session(self.engine) as db, db.begin():
                if db.get(TransactionGuard, 1) is None:
                    db.add(TransactionGuard(id=1, epoch=0))
        except IntegrityError:
            # Another initializer already inserted the singleton row.
            pass

    def close(self):
        self.engine.dispose()

    def _load(self, db):
        state = State()
        for row in db.scalars(select(Account)):
            learner = {'id': row.id, 'email': row.email, 'name': row.name, 'activeTrack': row.active_track,
                       'onboarded': row.onboarded, 'levels': {}}
            state.accounts[row.id] = {'learner': learner, 'password_hash': row.password_hash, 'progress': {}, 'attempts': []}
            state.emails[row.email] = row.id
        for row in db.scalars(select(Preference)):
            state.accounts[row.account_id]['learner']['levels'][row.track] = row.level
        for row in db.scalars(select(AuthSession)):
            state.sessions[row.token_hash] = {'account': row.account_id, 'expires': row.expires_at.replace(tzinfo=timezone.utc)}
        self._load_learning(db, state)
        return state

    def _save(self, db, state):
        for account in state.accounts.values():
            learner = account['learner']
            db.merge(Account(id=learner['id'], email=learner['email'], name=learner['name'],
                             password_hash=account['password_hash'], active_track=learner['activeTrack'], onboarded=learner['onboarded']))
        db.flush()
        for account in state.accounts.values():
            learner = account['learner']
            for track, level in learner['levels'].items():
                db.merge(Preference(account_id=learner['id'], track=track, level=level))
        for token, session in state.sessions.items():
            db.merge(AuthSession(token_hash=token, account_id=session['account'], expires_at=session['expires'].astimezone(timezone.utc).replace(tzinfo=None)))
        db.execute(delete(AuthSession).where(AuthSession.token_hash.not_in(list(state.sessions))))
        self._save_learning(db, state)

    def _load_learning(self, db, state):
        # Account foundation only. The dependent #16 adds durable learning entities.
        pass

    def _save_learning(self, db, state):
        if any(account['progress'] or account['attempts'] for account in state.accounts.values()):
            raise StorageUnavailable('Learning persistence is not initialized at this foundation gate.')

    @contextmanager
    def transaction(self):
        try:
            with Session(self.engine) as db, db.begin():
                # Acquire the database writer lock BEFORE reading any mutable state.
                db.execute(update(TransactionGuard).where(TransactionGuard.id == 1).values(epoch=TransactionGuard.epoch + 1))
                state = self._load(db)
                yield state
                self._save(db, state)
        except SQLAlchemyError:
            # DB exception details may contain learner values. Do not log/echo them.
            raise StorageUnavailable('Database transaction could not complete.') from None
