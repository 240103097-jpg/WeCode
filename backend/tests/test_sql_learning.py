from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import datetime, timezone
import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from backend.wecode.app import create_app
from backend.wecode.sql_storage import SQLStorage, AuthoredUnit, AuthoredExercise, LessonState, ExerciseState, SavedAttempt
from backend.wecode.storage import StorageUnavailable
from .conftest import ContractClient


def account(client,email='saved@example.test'):
    data={'name':'Saved Learner','email':email,'password':'test-only-password-42'}
    result=client.post('/api/v1/auth/register',json=data)
    assert result.status_code == 201
    return {'Authorization':'Bearer '+result.json()['accessToken']}


BASE='/api/v1/me/units/python-beginner/exercises/'


def test_all_learning_reopen_and_repeatable_curriculum(tmp_path,monkeypatch):
    url='sqlite:///'+str(tmp_path/'learning.sqlite3')
    monkeypatch.setenv('DATABASE_URL',url)
    app=create_app()  # Actual runtime default must use DATABASE_URL SQLStorage.
    assert isinstance(app.state.storage,SQLStorage)
    with ContractClient(app) as client:
        auth=account(client)
        other=account(client,'other@example.test')
        assert client.patch('/api/v1/me/preferences',headers=auth,json={'track':'Git','level':'Advanced','onboarded':True}).status_code == 204
        for eid,answer in [('python-beginner-quiz','a'),('python-beginner-bug','int(age) + 1'),('python-beginner-fill','print')]:
            target=BASE+eid
            assert client.post(target+'/submissions',headers=auth,json={'answer':'wrong'}).status_code == 201
            assert client.post(target+'/hints',headers=auth).status_code == 200
            if eid.endswith('bug'):
                assert client.put(target+'/solution-reveal',headers=auth).status_code == 200
            for _ in range(2):
                assert client.post(target+'/submissions',headers=auth,json={'answer':answer}).status_code == 201
        assert client.put('/api/v1/me/units/python-beginner/lesson-read',headers=auth,json={'read':True}).status_code == 204
        expected=client.get('/api/v1/me/snapshot',headers=auth).json()
    app.state.storage.close()
    for _ in range(3):
        storage=SQLStorage(url)
        with ContractClient(create_app(storage=storage)) as client:
            assert client.get('/api/v1/me/snapshot',headers=auth).json() == expected
            other_state=client.get('/api/v1/me/snapshot',headers=other).json()
            assert other_state['progress'] == {} and other_state['attempts'] == []
        with Session(storage.engine) as db:
            assert len(list(db.scalars(select(AuthoredUnit)))) == 9
            assert len(list(db.scalars(select(AuthoredExercise)))) == 27
            assert len(list(db.scalars(select(SavedAttempt)))) == 9
            assert len(list(db.scalars(select(LessonState)))) == 1
            assert len(list(db.scalars(select(ExerciseState)))) == 3
        storage.close()
    state=expected['progress']['python-beginner']
    assert state['read'] and all(item['correct'] for item in state['exercises'].values())
    assert sum(item['independent'] for item in state['exercises'].values()) == 2
    assert state['exercises']['python-beginner-bug']['revealed']
    assert all(item['hintCount']==1 for item in state['exercises'].values())


def test_two_adapters_concurrent_order_credit_and_hints(tmp_path):
    url='sqlite:///'+str(tmp_path/'concurrent.sqlite3')
    stores=[SQLStorage(url),SQLStorage(url)]
    fixed=datetime(2026,10,19,tzinfo=timezone.utc)
    clients=[ContractClient(create_app(storage=store,clock=lambda:fixed)) for store in stores]
    auth=account(clients[0])
    target=BASE+'python-beginner-quiz'
    assert clients[0].post(target+'/submissions',headers=auth,json={'answer':'wrong'}).status_code == 201
    def write(index):
        client=clients[index%2]
        if index==3:
            return client.put(target+'/solution-reveal',headers=auth).status_code
        if index%5==0:
            return client.put('/api/v1/me/units/python-beginner/lesson-read',headers=auth,json={'read':True}).status_code
        if index%5==1:
            return client.post(target+'/hints',headers=auth).status_code
        return client.post(target+'/submissions',headers=auth,json={'answer':'a'}).status_code
    with ThreadPoolExecutor(max_workers=6) as pool:
        assert set(pool.map(write,range(24))) <= {200,201,204}
    data=clients[0].get('/api/v1/me/snapshot',headers=auth).json()
    assert data == clients[1].get('/api/v1/me/snapshot',headers=auth).json()
    flags=[attempt['assisted'] for attempt in data['attempts']]
    assert flags == sorted(flags)
    assert len(data['attempts']) == 14  # Initial wrong +13 successful submissions, excluding reveal/read/hint.
    ex=data['progress']['python-beginner']['exercises']['python-beginner-quiz']
    assert ex['hintCount'] == 5 and ex['correct'] and ex['revealed']
    assert ex['independent'] == any(attempt['correct'] and not attempt['assisted'] for attempt in data['attempts'])
    with Session(stores[0].engine) as db:
        assert len(list(db.scalars(select(ExerciseState)))) == 1
        assert [row.sequence for row in db.scalars(select(SavedAttempt).order_by(SavedAttempt.sequence))] == list(range(1,15))
    for client in clients:
        client.close()
    for store in stores:
        store.close()


def test_curriculum_drift_rejected_without_overwrite(tmp_path):
    url='sqlite:///'+str(tmp_path/'drift.sqlite3')
    storage=SQLStorage(url)
    with Session(storage.engine) as db,db.begin():
        unit=db.get(AuthoredUnit,'python-beginner')
        unit.payload=unit.payload|{'title':'Explicitly changed stored title'}
    storage.close()
    with pytest.raises(RuntimeError,match='explicit migration'):
        SQLStorage(url)
    # Direct inspection verifies startup did not silently rewrite the conflicting record.
    with Session(storage.engine) as db:
        assert db.get(AuthoredUnit,'python-beginner').payload['title']=='Explicitly changed stored title'
    storage.close()


def test_learning_commit_failure_rolls_back_progress_and_attempt(tmp_path):
    class Failing(SQLStorage):
        fail=False
        def _save_learning(self,db,state):
            super()._save_learning(db,state)
            db.flush()
            if self.fail:
                raise StorageUnavailable('private learning DB details')
    storage=Failing('sqlite:///'+str(tmp_path/'rollback-learning.sqlite3'))
    with ContractClient(create_app(storage=storage)) as client:
        auth=account(client)
        storage.fail=True
        assert client.post(BASE+'python-beginner-quiz/submissions',headers=auth,json={'answer':'a'}).status_code == 503
        assert client.put(BASE+'python-beginner-bug/solution-reveal',headers=auth).status_code == 503
        storage.fail=False
        data=client.get('/api/v1/me/snapshot',headers=auth).json()
        assert data['progress']=={} and data['attempts']==[]
    with Session(storage.engine) as db:
        assert list(db.scalars(select(SavedAttempt))) == []
        assert list(db.scalars(select(ExerciseState))) == []
    storage.close()


def test_database_learning_constraints(tmp_path):
    storage=SQLStorage('sqlite:///'+str(tmp_path/'constraints.sqlite3'))
    with ContractClient(create_app(storage=storage)) as client:
        auth=account(client)
        learner_id=client.get('/api/v1/me',headers=auth).json()['id']
        assert client.put('/api/v1/me/units/python-beginner/lesson-read',headers=auth,json={'read':True}).status_code == 204
    for unit,eid,correct,independent,hints in [('python-beginner','sql-beginner-quiz',True,True,0),('python-beginner','python-beginner-quiz',False,True,0),('python-beginner','python-beginner-quiz',False,False,-1)]:
        with Session(storage.engine) as db:
            with pytest.raises(IntegrityError):
                with db.begin():
                    db.add(ExerciseState(account_id=learner_id,unit_id=unit,exercise_id=eid,correct=correct,independent=independent,revealed=False,hint_count=hints))
                    db.flush()
    storage.close()
