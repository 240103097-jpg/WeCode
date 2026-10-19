from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from datetime import datetime, timezone
import pytest
from backend.scripts.sync_curriculum import authored
from backend.wecode.app import create_app
from backend.wecode.contract import DOCUMENT
from backend.wecode.storage import MemoryStorage, StorageUnavailable
from .conftest import ContractClient

DATA=authored()
CASES=[(unit['id'], exercise['id']) for unit in DATA['units'] for exercise in unit['exercises']]


def path(unit, exercise, action):
    return f'/api/v1/me/units/{unit}/exercises/{exercise}/{action}'


def snapshot(client,auth):
    return client.get('/api/v1/me/snapshot',headers=auth).json()


def submit(client,auth,unit,exercise,answer):
    return client.post(path(unit,exercise,'submissions'),headers=auth,json={'answer':answer})


@pytest.mark.parametrize('unit,exercise',CASES)
def test_all_authored_rules_retries_hints_and_solution(client,register,unit,exercise):
    _,auth=register()
    rule=DATA['answerRules'][exercise]
    assert client.post(path(unit,exercise,'hints'),headers=auth).status_code == 409
    assert snapshot(client,auth)['progress'] == {}
    for answer in rule['rejected']:
        result=submit(client,auth,unit,exercise,answer)
        assert result.status_code == 201
        assert result.json() == {'correct':False,'text':rule['incorrect'],'assisted':False}
    for _ in range(2):
        assert client.post(path(unit,exercise,'hints'),headers=auth).json() == rule['hint']
    for answer in rule['accepted']:
        result=submit(client,auth,unit,exercise,' \r\n'+answer+'\r\n ')
        assert result.json() == {'correct':True,'text':rule['explanation'],'assisted':False}
    for _ in range(2):
        reveal=client.put(path(unit,exercise,'solution-reveal'),headers=auth)
        assert reveal.json() == {'answer':rule['accepted'][0],'explanation':rule['explanation']}
    result=submit(client,auth,unit,exercise,rule['accepted'][0])
    assert result.json()['assisted'] is True
    assert client.post(path(unit,exercise,'hints'),headers=auth).status_code == 200  # Still unlocked after later correct.
    data=snapshot(client,auth)
    state=data['progress'][unit]['exercises'][exercise]
    assert state == {'correct':True,'independent':True,'revealed':True,'hintCount':3}
    assert len(data['attempts']) == len(rule['accepted'])+len(rule['rejected'])+1
    assert len({attempt['id'] for attempt in data['attempts']}) == len(data['attempts'])
    assert data['attempts'][-2]['answer'] == rule['accepted'][-1]
    assert data['units'] == DATA['units']  # A reveal never injects a key into ordinary curriculum.


def test_assisted_completion_all_units_no_duplicate_credit(client,register):
    _,auth=register()
    for unit in DATA['units']:
        uid=unit['id']
        for exercise in unit['exercises']:
            eid=exercise['id']
            reveal=client.put(path(uid,eid,'solution-reveal'),headers=auth).json()
            state=snapshot(client,auth)
            if uid == DATA['units'][0]['id'] and eid == unit['exercises'][0]['id']:
                assert state['attempts'] == []
            assert not state['progress'][uid]['exercises'][eid]['correct']
            for _ in range(2):
                assert submit(client,auth,uid,eid,reveal['answer']).json()['assisted'] is True
            assert submit(client,auth,uid,eid,'wrong-after-correct').json()['correct'] is False
        assert not snapshot(client,auth)['progress'][uid]['read']
        for _ in range(2):
            assert client.put(f'/api/v1/me/units/{uid}/lesson-read',headers=auth,json={'read':True}).status_code == 204
    data=snapshot(client,auth)
    completed=[unit for unit in DATA['units'] if data['progress'][unit['id']]['read'] and all(data['progress'][unit['id']]['exercises'][ex['id']]['correct'] for ex in unit['exercises'])]
    assert len(completed) == 9
    for track in ('Python','SQL','Git'):
        assert len([unit for unit in completed if unit['track']==track]) == 3
    assert len(data['attempts']) == 81  # Each POST is saved, credit still9/9.
    assert sum(ex['independent'] for unit in data['progress'].values() for ex in unit['exercises'].values()) == 0
    before_progress, before_attempts=data['progress'],data['attempts']
    assert client.patch('/api/v1/me/preferences',headers=auth,json={'track':'SQL','level':'Advanced','onboarded':True}).status_code == 204
    assert client.patch('/api/v1/me',headers=auth,json={'name':'Updated Name'}).status_code == 204
    data=snapshot(client,auth)
    assert data['progress'] == before_progress and data['attempts'] == before_attempts
    assert data['units'] == DATA['units']


def test_private_attempts_reveals_hints_and_identity_fields(client,register):
    one,auth=register()
    _,other=register('other@example.test')
    uid,eid=CASES[0]
    submit(client,auth,uid,eid,'wrong')
    client.put(path(uid,eid,'solution-reveal'),headers=auth)
    assert client.post(path(uid,eid,'hints'),headers=other).status_code == 409
    assert snapshot(client,other)['progress'] == {} and snapshot(client,other)['attempts'] == []
    result=submit(client,other,uid,eid,DATA['answerRules'][eid]['accepted'][0]).json()
    assert result['assisted'] is False
    assert snapshot(client,other)['progress'][uid]['exercises'][eid]['independent'] is True
    # Client-supplied private selectors are not used for authorization.
    assert client.get('/api/v1/me/snapshot?userId='+one['learner']['id'],headers=other).json()['learner']['id'] != one['learner']['id']
    for extra in ({'userId':one['learner']['id']},{'correct':True},{'assisted':False},{'progress':{}}):
        assert client.post(path(uid,eid,'submissions'),headers=other,json={'answer':'a'}|extra).status_code == 422


@pytest.mark.parametrize('answer',[None,True,1,{},[], '', ' \r\n\t ', 'x'*4001])
def test_invalid_submissions_have_no_side_effects(client,register,answer):
    _,auth=register()
    assert submit(client,auth,*CASES[0],answer).status_code == 422
    assert snapshot(client,auth)['attempts'] == [] and snapshot(client,auth)['progress'] == {}


def test_wire_limit_and_restricted_normalization_no_execution(client,register,tmp_path):
    _,auth=register()
    uid,eid='python-beginner','python-beginner-bug'
    assert submit(client,auth,uid,eid,'int(age)  + 1').json()['correct'] is False
    assert submit(client,auth,uid,eid,'INT(age) + 1').json()['correct'] is False
    assert submit(client,auth,uid,eid,'int(age) + 1;').json()['correct'] is False
    assert submit(client,auth,uid,eid,'x'*4000).status_code == 201
    assert submit(client,auth,uid,eid,' '*4000+'a').status_code == 422
    malicious=f'__import__("pathlib").Path({str(tmp_path / "executed")!r}).touch()'
    assert submit(client,auth,uid,eid,malicious).json()['correct'] is False
    assert not (tmp_path/'executed').exists()
    assert submit(client,auth,'sql-intermediate','sql-intermediate-bug','having').json()['correct'] is True
    assert submit(client,auth,'sql-intermediate','sql-intermediate-bug','Having').json()['correct'] is False
    assert submit(client,auth,'python-beginner','python-beginner-quiz','unknown-option').status_code == 201


@pytest.mark.parametrize('action,method',[('submissions','post'),('hints','post'),('solution-reveal','put')])
def test_practice_auth_ids_errors(client,register,action,method):
    _,auth=register()
    kwargs={'json':{'answer':'a'}} if action=='submissions' else {}
    request=getattr(client,method)
    for headers in ({},{'Authorization':'Bearer invalid'}):
        assert request(path(*CASES[0],action),headers=headers,**kwargs).status_code == 401
    for uid,eid,status in [('unknown-unit','unknown-exercise',404),('python-beginner','sql-beginner-quiz',404),('python-beginner','unknown',404),('Bad-ID','python-beginner-quiz',422),('python-beginner','Bad-ID',422)]:
        assert request(path(uid,eid,action),headers=auth,**kwargs).status_code == status
    assert snapshot(client,auth)['progress'] == {} and snapshot(client,auth)['attempts'] == []


def test_concurrent_submit_reveal_history_and_completion():
    fixed=datetime(2026,10,19,tzinfo=timezone.utc)
    with ContractClient(create_app(clock=lambda:fixed)) as client:
        result=client.post('/api/v1/auth/register',json={'name':'Concurrent Learner','email':'concurrent@example.test','password':'test-only-password'}).json()
        auth={'Authorization':'Bearer '+result['accessToken']}
        uid,eid=CASES[0]
        def write(index):
            if index == 5:
                return client.put(path(uid,eid,'solution-reveal'),headers=auth).status_code
            if index == 8:
                return client.put(f'/api/v1/me/units/{uid}/lesson-read',headers=auth,json={'read':True}).status_code
            return submit(client,auth,uid,eid,'a').status_code
        with ThreadPoolExecutor(max_workers=6) as pool:
            assert set(pool.map(write,range(18))) == {200,201,204}
        data=snapshot(client,auth)
        assert len(data['attempts']) == 16
        assert len({item['createdAt'] for item in data['attempts']}) == 1
        flags=[item['assisted'] for item in data['attempts']]
        assert flags == sorted(flags)  # Commit order captures reveal exactly once.
        ex=data['progress'][uid]['exercises'][eid]
        assert ex['correct'] and ex['revealed']
        assert ex['independent'] == any(not flag for flag in flags)
        assert data['progress'][uid]['read'] is True
        assert sum(state['correct'] for state in data['progress'][uid]['exercises'].values()) == 1
        assert data['attempts'] == snapshot(client,auth)['attempts']  # Stable ordering including timestamp ties.


def test_failed_commit_rolls_back_attempt_and_reveal():
    class FailingCommit(MemoryStorage):
        fail=False
        @contextmanager
        def transaction(self):
            with super().transaction() as state:
                yield state
                if self.fail:
                    raise StorageUnavailable('private adapter detail')
    storage=FailingCommit()
    with ContractClient(create_app(storage=storage)) as client:
        response=client.post('/api/v1/auth/register',json={'name':'Learner','email':'rollback@example.test','password':'test-only-password'}).json()
        auth={'Authorization':'Bearer '+response['accessToken']}
        storage.fail=True
        assert submit(client,auth,*CASES[0],'a').status_code == 503
        assert client.put(path(*CASES[0],'solution-reveal'),headers=auth).status_code == 503
        storage.fail=False
        assert snapshot(client,auth)['progress'] == {} and snapshot(client,auth)['attempts'] == []


def test_every_contract_operation_implemented(client):
    expected={(method.upper(),'/api/v1'+path) for path,operations in DOCUMENT['paths'].items() for method in operations if method in {'get','post','put','patch','delete'}}
    actual={(method,route.path) for route in client.app.routes if route.path.startswith('/api/v1') for method in route.methods}
    assert actual == expected and len(actual) == 11


def test_protected_transport_validation_and_bodyless_actions(client,register):
    _,auth=register()
    for method,url in [('patch','/api/v1/me/preferences'),('put','/api/v1/me/units/python-beginner/lesson-read'),('post',path(*CASES[0],'submissions'))]:
        send=getattr(client,method)
        assert send(url,headers=auth,content='{}').status_code == 415
        assert send(url,headers=auth|{'Content-Type':'application/json'},content='{').status_code == 400
        assert send(url,headers=auth,json={}).status_code == 422
    for action,method in [('hints','post'),('solution-reveal','put')]:
        assert getattr(client,method)(path(*CASES[0],action),headers=auth,json={'userId':'other'}).status_code == 422
    assert snapshot(client,auth)['progress'] == {} and snapshot(client,auth)['attempts'] == []
