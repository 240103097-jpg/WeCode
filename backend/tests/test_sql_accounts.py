from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from backend.wecode.app import create_app
from backend.wecode.sql_storage import SQLStorage, Account, Preference, AuthSession, database_url
from .conftest import ContractClient


def test_database_config_required(monkeypatch):
    monkeypatch.delenv('DATABASE_URL',raising=False)
    with pytest.raises(RuntimeError,match='DATABASE_URL'):
        database_url()
    with pytest.raises(RuntimeError,match='DATABASE_URL'):
        create_app()
    monkeypatch.setenv('DATABASE_URL','sqlite:////tmp/example.sqlite3')
    assert database_url() == 'sqlite:////tmp/example.sqlite3'


def test_account_preferences_session_reopen_expiry_revocation(tmp_path):
    url='sqlite:///'+str(tmp_path/'accounts.sqlite3')
    now=datetime(2026,10,19,tzinfo=timezone.utc)
    data={'name':'Persisted Learner','email':'persist@example.test','password':'test-only-password-42'}
    storage=SQLStorage(url)
    with ContractClient(create_app(storage=storage,clock=lambda:now)) as client:
        result=client.post('/api/v1/auth/register',json=data).json()
        auth={'Authorization':'Bearer '+result['accessToken']}
        second=client.post('/api/v1/auth/login',json={k:v for k,v in data.items() if k!='name'}).json()
        revoked={'Authorization':'Bearer '+second['accessToken']}
        assert client.patch('/api/v1/me/preferences',headers=auth,json={'track':'SQL','level':'Advanced','onboarded':True}).status_code == 204
        assert client.patch('/api/v1/me',headers=auth,json={'name':'Changed Name'}).status_code == 204
        assert client.delete('/api/v1/auth/session',headers=revoked).status_code == 204
        expected=client.get('/api/v1/me',headers=auth).json()
    storage.close()
    for _ in range(2):
        storage=SQLStorage(url)
        with ContractClient(create_app(storage=storage,clock=lambda:now)) as client:
            assert client.get('/api/v1/me',headers=auth).json() == expected
            assert client.get('/api/v1/me',headers=revoked).status_code == 401
            assert client.post('/api/v1/auth/login',json={k:v for k,v in data.items() if k!='name'}).status_code == 200
        storage.close()
    storage=SQLStorage(url)
    with ContractClient(create_app(storage=storage,clock=lambda:now+timedelta(hours=24))) as client:
        assert client.get('/api/v1/me',headers=auth).status_code == 401
    with Session(storage.engine) as db:
        account=db.scalars(select(Account)).one()
        assert account.password_hash.startswith('$argon2id$')
        assert all(row.token_hash != result['accessToken'] and len(row.token_hash)==64 for row in db.scalars(select(AuthSession)))
        assert len(list(db.scalars(select(Preference)))) == 3
    storage.close()


def test_two_adapters_duplicate_registration_and_isolation(tmp_path):
    url='sqlite:///'+str(tmp_path/'race.sqlite3')
    stores=[SQLStorage(url),SQLStorage(url)]
    clients=[ContractClient(create_app(storage=store)) for store in stores]
    data={'name':'Concurrent Learner','email':'race@example.test','password':'test-only-password-42'}
    def register(index):
        return clients[index%2].post('/api/v1/auth/register',json=data)
    with ThreadPoolExecutor(max_workers=4) as pool:
        responses=list(pool.map(register,range(6)))
    assert sorted(response.status_code for response in responses) == [201,409,409,409,409,409]
    auth={'Authorization':'Bearer '+next(r.json()['accessToken'] for r in responses if r.status_code==201)}
    other=clients[1].post('/api/v1/auth/register',json=data|{'email':'other@example.test'}).json()
    other_auth={'Authorization':'Bearer '+other['accessToken']}
    assert clients[0].patch('/api/v1/me/preferences',headers=auth,json={'track':'Git','level':'Advanced'}).status_code == 204
    assert clients[1].get('/api/v1/me',headers=auth).json()['levels']['Git'] == 'Advanced'
    assert clients[0].get('/api/v1/me',headers=other_auth).json()['levels']['Git'] == 'Beginner'
    for client in clients:
        client.close()
    for store in stores:
        store.close()


def test_sql_rollback_and_constraints(tmp_path):
    storage=SQLStorage('sqlite:///'+str(tmp_path/'rollback.sqlite3'))
    with pytest.raises(RuntimeError):
        with storage.transaction() as state:
            state.emails['uncommitted@example.test']='never'
            raise RuntimeError('rollback')
    with storage.transaction() as state:
        assert state.emails == {} and state.accounts == {}
    with Session(storage.engine) as db:
        with pytest.raises(IntegrityError):
            with db.begin():
                db.add(Preference(account_id='missing',track='Python',level='Beginner'))
                db.flush()
    with ContractClient(create_app(storage=storage)) as client:
        assert client.post('/api/v1/auth/register',json={'name':'Valid Name','email':'duplicate@example.test','password':'test-only-password'}).status_code == 201
    with Session(storage.engine) as db:
        with pytest.raises(IntegrityError):
            with db.begin():
                db.add(Account(id='other',email='duplicate@example.test',name='Other Name',password_hash='test-hash',active_track='Python',onboarded=False))
                db.flush()
    storage.close()


def test_api_sql_failed_write_rolls_back_flushed_account(tmp_path):
    from backend.wecode.storage import StorageUnavailable
    class FailingStorage(SQLStorage):
        fail=False
        def _save(self,db,state):
            super()._save(db,state)
            db.flush()
            if self.fail:
                raise StorageUnavailable('private DB detail')
    storage=FailingStorage('sqlite:///'+str(tmp_path/'failed.sqlite3'))
    with ContractClient(create_app(storage=storage)) as client:
        result=client.post('/api/v1/auth/register',json={'name':'Original Name','email':'failed@example.test','password':'test-only-password'}).json()
        auth={'Authorization':'Bearer '+result['accessToken']}
        storage.fail=True
        response=client.patch('/api/v1/me',headers=auth,json={'name':'Uncommitted Name'})
        assert response.status_code == 503 and 'private' not in response.text
        storage.fail=False
        assert client.get('/api/v1/me',headers=auth).json()['name'] == 'Original Name'
    storage.close()
