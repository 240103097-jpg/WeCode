"""SQLAlchemy implementation of the existing atomic State storage boundary.

Only SQLite is supported/tested. A guard-row UPDATE obtains the database write
lock before loading State, serializing independent connections and processes.
The adapter favors correctness over scale: full State is read each transaction.
"""
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime, timezone
import os
import json
from pathlib import Path

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, ForeignKeyConstraint, Integer, JSON, String, UniqueConstraint, create_engine, delete, event, select, update
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


class AuthoredUnit(Base):
    __tablename__ = 'curriculum_units'
    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False, unique=True)
    track: Mapped[str] = mapped_column(String, nullable=False)
    level: Mapped[str] = mapped_column(String, nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    __table_args__ = (UniqueConstraint('track', 'level'), CheckConstraint(TRACK_CHECK), CheckConstraint(LEVEL_CHECK))


class AuthoredExercise(Base):
    __tablename__ = 'curriculum_exercises'
    id: Mapped[str] = mapped_column(String(100), primary_key=True)
    unit_id: Mapped[str] = mapped_column(ForeignKey('curriculum_units.id'), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    rule: Mapped[dict] = mapped_column(JSON, nullable=False)
    __table_args__ = (UniqueConstraint('unit_id', 'id'), UniqueConstraint('unit_id', 'position'))


class LessonState(Base):
    __tablename__ = 'lesson_state'
    account_id: Mapped[str] = mapped_column(ForeignKey('accounts.id'), primary_key=True)
    unit_id: Mapped[str] = mapped_column(ForeignKey('curriculum_units.id'), primary_key=True)
    read: Mapped[bool] = mapped_column(Boolean(create_constraint=True), nullable=False)


class ExerciseState(Base):
    __tablename__ = 'exercise_state'
    account_id: Mapped[str] = mapped_column(String(36), primary_key=True)
    unit_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    exercise_id: Mapped[str] = mapped_column(String(100), primary_key=True)
    correct: Mapped[bool] = mapped_column(Boolean(create_constraint=True), nullable=False)
    independent: Mapped[bool] = mapped_column(Boolean(create_constraint=True), nullable=False)
    revealed: Mapped[bool] = mapped_column(Boolean(create_constraint=True), nullable=False)
    hint_count: Mapped[int] = mapped_column(Integer, nullable=False)
    __table_args__ = (
        ForeignKeyConstraint(['account_id', 'unit_id'], ['lesson_state.account_id', 'lesson_state.unit_id']),
        ForeignKeyConstraint(['unit_id', 'exercise_id'], ['curriculum_exercises.unit_id', 'curriculum_exercises.id']),
        CheckConstraint('hint_count >= 0'), CheckConstraint('NOT independent OR correct'),
    )


class SavedAttempt(Base):
    __tablename__ = 'attempts'
    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    account_id: Mapped[str] = mapped_column(ForeignKey('accounts.id'), nullable=False)
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    exercise_id: Mapped[str] = mapped_column(ForeignKey('curriculum_exercises.id'), nullable=False)
    answer: Mapped[str] = mapped_column(String(4000), nullable=False)
    correct: Mapped[bool] = mapped_column(Boolean(create_constraint=True), nullable=False)
    assisted: Mapped[bool] = mapped_column(Boolean(create_constraint=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    feedback: Mapped[str] = mapped_column(String, nullable=False)
    __table_args__ = (UniqueConstraint('account_id', 'sequence'), CheckConstraint('sequence > 0'), CheckConstraint('length(answer) BETWEEN 1 AND 4000'))


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
        self._initialize_curriculum()

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

    def _initialize_curriculum(self):
        data = json.loads((Path(__file__).resolve().parents[1] / 'data/curriculum.json').read_text())
        with Session(self.engine) as db, db.begin():
            db.execute(update(TransactionGuard).where(TransactionGuard.id == 1).values(epoch=TransactionGuard.epoch + 1))
            for index, unit in enumerate(data['units']):
                payload = {key: value for key, value in unit.items() if key != 'exercises'}
                row = db.get(AuthoredUnit, unit['id'])
                if row is None:
                    db.add(AuthoredUnit(id=unit['id'], position=index, track=unit['track'], level=unit['level'], payload=payload))
                elif row.payload != payload or row.position != index or row.track != unit['track'] or row.level != unit['level']:
                    raise RuntimeError('Stored curriculum differs from authored content; explicit migration required.')
            db.flush()
            for unit in data['units']:
                for index, exercise in enumerate(unit['exercises']):
                    rule = data['answerRules'][exercise['id']]
                    row = db.get(AuthoredExercise, exercise['id'])
                    if row is None:
                        db.add(AuthoredExercise(id=exercise['id'], unit_id=unit['id'], position=index, payload=exercise, rule=rule))
                    elif row.unit_id != unit['id'] or row.position != index or row.payload != exercise or row.rule != rule:
                        raise RuntimeError('Stored curriculum differs from authored content; explicit migration required.')
            db.flush()
            if len(list(db.scalars(select(AuthoredUnit)))) != 9 or len(list(db.scalars(select(AuthoredExercise)))) != 27:
                raise RuntimeError('Unexpected curriculum inventory; explicit migration required.')

    def curriculum(self):
        from .curriculum import Curriculum
        with Session(self.engine) as db, db.begin():
            units = []
            rules = {}
            for row in db.scalars(select(AuthoredUnit).order_by(AuthoredUnit.position)):
                unit = deepcopy(row.payload)
                unit['exercises'] = []
                for exercise in db.scalars(select(AuthoredExercise).where(AuthoredExercise.unit_id == row.id).order_by(AuthoredExercise.position)):
                    unit['exercises'].append(deepcopy(exercise.payload))
                    rules[exercise.id] = deepcopy(exercise.rule)
                units.append(unit)
        return Curriculum({'units': units, 'answerRules': rules})

    def _load_learning(self, db, state):
        for row in db.scalars(select(LessonState)):
            state.accounts[row.account_id]['progress'][row.unit_id] = {'read': row.read, 'exercises': {}}
        for row in db.scalars(select(ExerciseState)):
            state.accounts[row.account_id]['progress'][row.unit_id]['exercises'][row.exercise_id] = {
                'correct': row.correct, 'independent': row.independent, 'revealed': row.revealed, 'hintCount': row.hint_count}
        for row in db.scalars(select(SavedAttempt).order_by(SavedAttempt.account_id, SavedAttempt.sequence)):
            state.accounts[row.account_id]['attempts'].append({
                'id': row.id, 'exerciseId': row.exercise_id, 'answer': row.answer, 'correct': row.correct,
                'assisted': row.assisted, 'createdAt': row.created_at.replace(tzinfo=timezone.utc).isoformat(timespec='milliseconds').replace('+00:00', 'Z'),
                'feedback': row.feedback})

    def _save_learning(self, db, state):
        for account_id, account in state.accounts.items():
            for unit_id, progress in account['progress'].items():
                db.merge(LessonState(account_id=account_id, unit_id=unit_id, read=progress['read']))
        db.flush()
        for account_id, account in state.accounts.items():
            for unit_id, progress in account['progress'].items():
                for exercise_id, exercise in progress['exercises'].items():
                    db.merge(ExerciseState(account_id=account_id, unit_id=unit_id, exercise_id=exercise_id,
                                           correct=exercise['correct'], independent=exercise['independent'],
                                           revealed=exercise['revealed'], hint_count=exercise['hintCount']))
            for index, attempt in enumerate(account['attempts'], 1):
                db.merge(SavedAttempt(id=attempt['id'], account_id=account_id, sequence=index, exercise_id=attempt['exerciseId'],
                                      answer=attempt['answer'], correct=attempt['correct'], assisted=attempt['assisted'],
                                      created_at=datetime.fromisoformat(attempt['createdAt'].replace('Z', '+00:00')).astimezone(timezone.utc).replace(tzinfo=None),
                                      feedback=attempt['feedback']))

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
