from datetime import datetime, timedelta, timezone
import pytest
from backend.wecode.app import create_app
from backend.wecode.storage import MemoryStorage, StorageUnavailable
from .conftest import ContractClient

PASSWORD = 'test-only-password-42'


def test_register_login_profile_logout_isolation(client, register):
    one, auth = register()
    two, other = register('other@example.test')
    assert one['learner']['id'] != two['learner']['id']
    assert len(one['accessToken']) >= 43
    assert one['tokenType'] == 'Bearer'
    assert one['learner']['levels'] == dict.fromkeys(['Python', 'SQL', 'Git'], 'Beginner')
    assert one['learner']['onboarded'] is False
    assert client.patch('/api/v1/me', headers=auth, json={'name': '  Updated Name  '}).status_code == 204
    assert client.get('/api/v1/me', headers=auth).json()['name'] == 'Updated Name'
    assert client.get('/api/v1/me', headers=other).json()['name'] == 'Test Learner'
    login = client.post('/api/v1/auth/login', json={'email': ' LEARNER@EXAMPLE.TEST ', 'password': PASSWORD}).json()
    assert login['accessToken'] != one['accessToken']
    assert client.delete('/api/v1/auth/session', headers=auth).status_code == 204
    assert client.get('/api/v1/me', headers=auth).status_code == 401
    assert client.delete('/api/v1/auth/session', headers=auth).status_code == 401
    assert client.get('/api/v1/me', headers={'Authorization': 'Bearer ' + login['accessToken']}).status_code == 200
    assert client.get('/api/v1/me', headers=other).status_code == 200


def test_duplicate_normalized_email_and_credentials(client, register):
    register()
    assert client.post('/api/v1/auth/register', json={'name':'Another', 'email':' LEARNER@EXAMPLE.TEST ', 'password':PASSWORD}).status_code == 409
    wrong = client.post('/api/v1/auth/login', json={'email':'learner@example.test', 'password':'incorrect-password'})
    unknown = client.post('/api/v1/auth/login', json={'email':'unknown@example.test', 'password':'incorrect-password'})
    assert wrong.status_code == unknown.status_code == 401
    assert wrong.json() == unknown.json() == {'error': {'code':'credentials', 'message':'Email or password is incorrect.'}}
    assert client.post('/api/v1/auth/login', json={'email':'learner@example.test','password':'practice-only'}).status_code == 401


@pytest.mark.parametrize('change', [ {'name':' '}, {'name':'a'}, {'name':12}, {'email':'bad'}, {'password':'short'}, {'password':'x'*129}, {'password':None}, {'userId':'other'}, {'correct':True} ])
def test_invalid_registration(client, change):
    data = {'name':'Learner', 'email':'valid@example.test','password':PASSWORD} | change
    assert client.post('/api/v1/auth/register', json=data).status_code == 422


def test_missing_fields_and_transport(client):
    for path in ('/auth/register','/auth/login'):
        assert client.post('/api/v1'+path, json={}).status_code == 422
        assert client.post('/api/v1'+path, content='{', headers={'Content-Type':'application/json'}).status_code == 400
        assert client.post('/api/v1'+path, content='{}').status_code == 415
    for raw in ('{"name":"A","name":"B"}', '{"x":NaN}'):
        assert client.post('/api/v1/auth/register', content=raw, headers={'Content-Type':'application/json'}).status_code == 400


@pytest.mark.parametrize('value', [None, '', 'Basic abc', 'Bearer', 'Bearer invalid', 'Bearer a b'])
def test_missing_malformed_auth(client, value):
    headers={} if value is None else {'Authorization':value}
    for method, path, kwargs in [('GET','/me',{}), ('PATCH','/me',{'json':{'name':'Valid Name'}}), ('DELETE','/auth/session',{})]:
        response = client.request(method,'/api/v1'+path,headers=headers,**kwargs)
        assert response.status_code == 401
        assert response.headers['www-authenticate'] == 'Bearer'


def test_hashes_expiry_restart_and_password_whitespace():
    now = datetime(2026,10,19,tzinfo=timezone.utc)
    storage = MemoryStorage()
    app = create_app(storage=storage, clock=lambda:now)
    with ContractClient(app) as client:
        data={'name':'Learner','email':'learner@example.test','password':'  keep-spaces-42  '}
        result=client.post('/api/v1/auth/register',json=data).json()
        auth={'Authorization':'Bearer '+result['accessToken']}
        assert datetime.fromisoformat(result['expiresAt'].replace('Z','+00:00')) == now + timedelta(hours=24)
        with storage.transaction() as state:
            account=state.accounts[result['learner']['id']]
            assert account['password_hash'].startswith('$argon2id$')
            assert app.state.hasher.verify(account['password_hash'],data['password'])
            assert result['accessToken'] not in state.sessions
            assert 'password' not in account
        assert client.post('/api/v1/auth/login',json={'email':data['email'], 'password':data['password'].strip()}).status_code == 401
        now += timedelta(hours=24)
        assert client.get('/api/v1/me',headers=auth).status_code == 401
    with ContractClient(create_app(storage=MemoryStorage())) as restarted:
        assert restarted.get('/api/v1/me',headers=auth).status_code == 401
        assert restarted.post('/api/v1/auth/login',json={'email':data['email'],'password':data['password']}).status_code == 401


def test_profile_rejects_extras_and_preserves_state(client,register):
    initial, auth=register()
    for data in ({'name':'Valid','email':'other@example.test'}, {'name':'Valid','id':'other'}, {'name':True}, {'name':' '}):
        assert client.patch('/api/v1/me',headers=auth,json=data).status_code == 422
    assert client.get('/api/v1/me',headers=auth).json() == initial['learner']


def test_storage_rollback():
    store=MemoryStorage()
    with pytest.raises(RuntimeError):
        with store.transaction() as state:
            state.accounts['partial']={}
            raise RuntimeError('rollback')
    with store.transaction() as state:
        assert state.accounts == {}


@pytest.mark.parametrize('error,status,code', [(StorageUnavailable,503,'unavailable'), (RuntimeError,500,'internal')])
def test_safe_storage_errors(error,status,code):
    class Broken:
        def transaction(self):
            raise error('sensitive internal secret')
    with ContractClient(create_app(storage=Broken())) as client:
        response=client.get('/api/v1/me',headers={'Authorization':'Bearer test'})
        assert response.status_code == status
        assert response.json()['error']['code'] == code
        assert 'sensitive' not in response.text
