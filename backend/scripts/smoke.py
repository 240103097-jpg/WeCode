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
        assert client.delete('/api/v1/auth/session',headers=auth).status_code == 204
        assert client.get('/api/v1/me',headers=auth).status_code == 401
    print('PASS real HTTP auth/profile/docs smoke; no credentials printed')


if __name__ == '__main__':
    smoke()
