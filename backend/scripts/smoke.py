"""Real HTTP checks; generated disposable credentials stay in memory, never printed."""
import secrets
import re
import sys
from pathlib import Path
from uuid import uuid4
import httpx
from openapi_schema_validator import OAS30Validator
from jsonschema import FormatChecker

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from backend.wecode.contract import DOCUMENT, resolve


def check_contract(response):
    request=response.request
    path=request.url.path.removeprefix('/api/v1')
    for template, operations in DOCUMENT['paths'].items():
        if re.fullmatch(re.sub(r'\{[^}]+\}', '[^/]+', template), path) and request.method.lower() in operations:
            responses=operations[request.method.lower()]['responses']
            assert str(response.status_code) in responses, 'Undocumented HTTP response status'
            definition=resolve(responses[str(response.status_code)])
            response.read()
            for name, header in definition.get('headers',{}).items():
                assert OAS30Validator(header['schema']).is_valid(response.headers.get(name)), 'HTTP response header violates contract'
            if 'content' in definition:
                schema=definition['content']['application/json']['schema']
                assert OAS30Validator(schema,format_checker=FormatChecker()).is_valid(response.json()), 'HTTP response body violates contract'
            else:
                assert not response.content, 'Unexpected HTTP response body'
            break


def smoke(base='http://127.0.0.1:8000'):
    email = f'smoke-{uuid4()}@example.test'
    password = secrets.token_urlsafe(24)
    with httpx.Client(base_url=base,event_hooks={'response':[check_contract]}) as client:
        assert client.get('/docs').status_code == 200
        assert client.get('/openapi.json').json()['openapi'] == '3.0.3'
        assert client.get('/api/v1/me').status_code == 401
        response=client.post('/api/v1/auth/register',json={'name':'HTTP Smoke','email':email,'password':password})
        assert response.status_code == 201
        auth={'Authorization':'Bearer '+response.json()['accessToken']}
        assert client.get('/api/v1/me',headers=auth).json()['email'] == email
        assert client.patch('/api/v1/me',headers=auth,json={'name':'HTTP Verified'}).status_code == 204
        assert client.post('/api/v1/auth/login',json={'email':email,'password':password}).status_code == 200
        assert client.patch('/api/v1/me/preferences',headers=auth,json={'track':'SQL','level':'Advanced','onboarded':True}).status_code == 204
        snapshot=client.get('/api/v1/me/snapshot',headers=auth).json()
        assert len(snapshot['units']) == 9 and snapshot['learner']['levels']['SQL'] == 'Advanced'
        assert client.put('/api/v1/me/units/python-beginner/lesson-read',headers=auth,json={'read':True}).status_code == 204
        assert client.get('/api/v1/me/snapshot',headers=auth).json()['progress']['python-beginner']['read'] is True
        prefix='/api/v1/me/units/python-beginner/exercises/'
        for eid, answer in [('python-beginner-quiz','a'),('python-beginner-bug','int(age) + 1'),('python-beginner-fill','print')]:
            exercise=prefix+eid
            assert client.post(exercise+'/hints',headers=auth).status_code == 409
            assert client.post(exercise+'/submissions',headers=auth,json={'answer':'wrong'}).json()['correct'] is False
            assert isinstance(client.post(exercise+'/hints',headers=auth).json(),str)
            assert client.put(exercise+'/solution-reveal',headers=auth).json()['answer'] == answer
            for _ in range(2):
                result=client.post(exercise+'/submissions',headers=auth,json={'answer':answer})
                assert result.status_code == 201 and result.json() == {'correct':True,'text':result.json()['text'],'assisted':True}
        progress=client.get('/api/v1/me/snapshot',headers=auth).json()
        state=progress['progress']['python-beginner']
        assert state['read'] and len(state['exercises']) == 3
        assert all(ex['correct'] and not ex['independent'] for ex in state['exercises'].values())
        assert len(progress['attempts']) == 9
        assert client.delete('/api/v1/auth/session',headers=auth).status_code == 204
        assert client.get('/api/v1/me',headers=auth).status_code == 401
    print('PASS real HTTP all 11 operations and three exercise types over HTTP; completion/retries/hints/reveals/docs; all API responses contract-checked; no credentials printed')


if __name__ == '__main__':
    smoke()
