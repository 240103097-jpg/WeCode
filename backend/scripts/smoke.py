"""Real HTTP checks; generated disposable credentials stay in memory, never printed."""
import secrets
from uuid import uuid4
import httpx


def smoke(base='http://127.0.0.1:8000'):
    email = f'smoke-{uuid4()}@example.test'
    password = secrets.token_urlsafe(24)
    with httpx.Client(base_url=base) as client:
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
        assert client.delete('/api/v1/auth/session',headers=auth).status_code == 204
        assert client.get('/api/v1/me',headers=auth).status_code == 401
    print('PASS real HTTP auth/profile/curriculum/preferences/read/docs smoke; no credentials printed')


if __name__ == '__main__':
    smoke()
