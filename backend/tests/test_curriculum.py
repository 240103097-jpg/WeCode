from concurrent.futures import ThreadPoolExecutor
from copy import deepcopy
import pytest
from backend.scripts.sync_curriculum import authored
from backend.wecode.storage import MemoryStorage
from backend.wecode.app import create_app
from .conftest import ContractClient


def test_exact_curriculum_empty_state_and_no_keys(client, register):
    _,auth=register()
    snapshot=client.get('/api/v1/me/snapshot',headers=auth).json()
    assert snapshot['units'] == authored()['units']
    assert len(snapshot['units']) == 9
    assert sum(len(unit['exercises']) for unit in snapshot['units']) == 27
    assert snapshot['progress'] == {} and snapshot['attempts'] == []
    for unit in snapshot['units']:
        for exercise in unit['exercises']:
            assert not {'accepted','rejected','hint','answerRules','answer','explanation','correct'} & exercise.keys()


def test_preferences_read_onboarding_and_isolation(client, register):
    _,auth=register()
    _,other=register('other@example.test')
    for track,level in [('Python','Advanced'),('SQL','Intermediate'),('Git','Advanced')]:
        assert client.patch('/api/v1/me/preferences',headers=auth,json={'track':track,'level':level,'onboarded':True}).status_code == 204
    assert client.patch('/api/v1/me/preferences',headers=auth,json={'track':'Python','level':'Advanced','onboarded':False}).status_code == 204
    for _ in range(2):
        assert client.put('/api/v1/me/units/python-beginner/lesson-read',headers=auth,json={'read':True}).status_code == 204
    first=client.get('/api/v1/me/snapshot',headers=auth).json()
    assert first['learner']['levels'] == {'Python':'Advanced','SQL':'Intermediate','Git':'Advanced'}
    assert first['learner']['onboarded'] is True
    assert first['learner']['activeTrack'] == 'Python'
    assert first['progress'] == {'python-beginner':{'read':True,'exercises':{}}}
    assert first['attempts'] == []
    second=client.get('/api/v1/me/snapshot',headers=other).json()
    assert second['progress'] == {}
    assert second['learner']['onboarded'] is False
    assert second['learner']['levels'] == dict.fromkeys(['Python','SQL','Git'],'Beginner')


@pytest.mark.parametrize('data', [{'track':'Rust','level':'Beginner'}, {'track':'Python','level':'Expert'}, {'track':'Git','level':'Beginner','onboarded':'true'}, {'track':'Git','level':'Beginner','userId':'other'}, {}])
def test_preferences_invalid_rollback(client,register,data):
    _,auth=register()
    before=client.get('/api/v1/me/snapshot',headers=auth).json()
    assert client.patch('/api/v1/me/preferences',headers=auth,json=data).status_code == 422
    assert client.get('/api/v1/me/snapshot',headers=auth).json() == before


def test_read_invalid_unknown_and_no_mutations(client,register):
    _,auth=register()
    for unit, data, status in [('Unknown',{'read':True},422), ('unknown-unit',{'read':True},404), ('python-beginner',{'read':False},422), ('python-beginner',{'read':1},422), ('python-beginner',{'read':True,'userId':'other'},422)]:
        assert client.put(f'/api/v1/me/units/{unit}/lesson-read',headers=auth,json=data).status_code == status
    assert client.get('/api/v1/me/snapshot',headers=auth).json()['progress'] == {}


@pytest.mark.parametrize('auth', [{}, {'Authorization':'Bearer invalid'}])
def test_curriculum_auth(client,auth):
    assert client.get('/api/v1/me/snapshot',headers=auth).status_code == 401
    assert client.patch('/api/v1/me/preferences',headers=auth,json={'track':'SQL','level':'Advanced'}).status_code == 401
    assert client.put('/api/v1/me/units/python-beginner/lesson-read',headers=auth,json={'read':True}).status_code == 401


def test_coherent_concurrent_preferences_and_read(client,register):
    _,auth=register()
    def write(index):
        if index % 2:
            return client.patch('/api/v1/me/preferences',headers=auth,json={'track':'SQL','level':'Advanced','onboarded':True}).status_code
        return client.put('/api/v1/me/units/python-beginner/lesson-read',headers=auth,json={'read':True}).status_code
    with ThreadPoolExecutor(max_workers=4) as pool:
        assert set(pool.map(write,range(12))) == {204}
    data=client.get('/api/v1/me/snapshot',headers=auth).json()
    assert data['progress']['python-beginner']['read'] is True
    assert data['learner']['levels']['SQL'] == 'Advanced'
