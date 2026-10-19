"""Actual HTTP/process restart check using a disposable isolated SQLite database.

No credentials printed or written to files. Starts/stops real Uvicorn processes,
reuses the same temporary DB, checks state/session survival and repeat startup.
"""
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
import secrets
import socket
import subprocess
import sys
import tempfile
import time

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from backend.wecode.app import token_key
from backend.wecode.sql_storage import SQLStorage, AuthSession, AuthoredUnit, AuthoredExercise, SavedAttempt
from backend.scripts.smoke import check_contract


@contextmanager
def server(url):
    with socket.socket() as probe:
        probe.bind(('127.0.0.1',0))
        port=probe.getsockname()[1]
    process=subprocess.Popen([sys.executable,'-m','uvicorn','backend.wecode.app:create_app','--factory','--host','127.0.0.1','--port',str(port),'--workers','1','--no-access-log'],cwd=ROOT,env=os.environ|{'DATABASE_URL':url},stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    try:
        with httpx.Client(base_url=f'http://127.0.0.1:{port}',event_hooks={'response':[check_contract]}) as client:
            deadline=time.monotonic()+20
            while True:
                if process.poll() is not None:
                    raise RuntimeError('Restart-check backend exited before becoming ready.')
                try:
                    if client.get('/docs').status_code==200:
                        break
                except httpx.TransportError:
                    pass
                if time.monotonic()>deadline:
                    raise RuntimeError('Restart-check backend did not become ready.')
                time.sleep(.1)
            yield client,process.pid
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait(timeout=5)


def run():
    password=secrets.token_urlsafe(24)
    data={'name':'Restart Learner','email':'restart@example.test','password':password}
    with tempfile.TemporaryDirectory(prefix='wecode-process-restart-') as folder:
        url='sqlite:///'+str(Path(folder)/'restart.sqlite3')
        with server(url) as (client,first_pid):
            result=client.post('/api/v1/auth/register',json=data)
            assert result.status_code==201
            auth={'Authorization':'Bearer '+result.json()['accessToken']}
            login_input={'email':data['email'],'password':password}
            revoke=client.post('/api/v1/auth/login',json=login_input).json()['accessToken']
            expire=client.post('/api/v1/auth/login',json=login_input).json()['accessToken']
            assert client.delete('/api/v1/auth/session',headers={'Authorization':'Bearer '+revoke}).status_code==204
            other=client.post('/api/v1/auth/register',json=data|{'email':'other@example.test'}).json()
            other_auth={'Authorization':'Bearer '+other['accessToken']}
            assert client.patch('/api/v1/me',headers=auth,json={'name':'Restart Verified'}).status_code==204
            for track,level in [('Python','Intermediate'),('SQL','Advanced'),('Git','Advanced')]:
                assert client.patch('/api/v1/me/preferences',headers=auth,json={'track':track,'level':level,'onboarded':True}).status_code==204
            for eid,answer in [('python-beginner-quiz','a'),('python-beginner-bug','int(age) + 1'),('python-beginner-fill','print')]:
                prefix='/api/v1/me/units/python-beginner/exercises/'+eid
                assert client.post(prefix+'/submissions',headers=auth,json={'answer':'wrong'}).status_code==201
                assert client.post(prefix+'/hints',headers=auth).status_code==200
                if eid.endswith('bug'):
                    assert client.put(prefix+'/solution-reveal',headers=auth).status_code==200
                for _ in range(2):
                    assert client.post(prefix+'/submissions',headers=auth,json={'answer':answer}).json()['correct']
            assert client.put('/api/v1/me/units/python-beginner/lesson-read',headers=auth,json={'read':True}).status_code==204
            expected=client.get('/api/v1/me/snapshot',headers=auth).json()
            state=expected['progress']['python-beginner']
            assert state['read'] and all(ex['correct'] for ex in state['exercises'].values())
            assert sum(ex['independent'] for ex in state['exercises'].values())==2
            assert len(expected['attempts'])==9
        # Process is fully stopped. Move only one test session's timestamp into
        # the past; this verifies persisted expiry, without claiming a 24h wait.
        storage=SQLStorage(url)
        with Session(storage.engine) as db,db.begin():
            row=db.get(AuthSession,token_key(expire))
            row.expires_at=datetime.now(timezone.utc).replace(tzinfo=None)-timedelta(seconds=1)
        storage.close()
        pids={first_pid}
        for _ in range(2):
            with server(url) as (client,pid):
                assert pid not in pids
                pids.add(pid)
                assert client.get('/api/v1/me/snapshot',headers=auth).json()==expected
                for token in (revoke,expire):
                    assert client.get('/api/v1/me',headers={'Authorization':'Bearer '+token}).status_code==401
                result=client.post('/api/v1/auth/login',json=login_input)
                assert result.status_code==200
                assert client.get('/api/v1/me/snapshot',headers={'Authorization':'Bearer '+result.json()['accessToken']}).json()==expected
                other_state=client.get('/api/v1/me/snapshot',headers=other_auth).json()
                assert other_state['progress']=={} and other_state['attempts']==[]
        storage=SQLStorage(url)
        with Session(storage.engine) as db:
            assert len(list(db.scalars(select(AuthoredUnit))))==9
            assert len(list(db.scalars(select(AuthoredExercise))))==27
            assert len(list(db.scalars(select(SavedAttempt))))==9
        storage.close()
    print('PASS three real backend processes; same SQLite DB; login/profile/all-track preferences/read/9 attempts/hints/reveal/assistance/completion unchanged')
    print('PASS live sessions persist; logout stays revoked; offline-expired test session rejected; second account isolated; repeated startup keeps9units/27exercises')
    print('PASS actual HTTP responses contract-checked; temporary DB removed; no credentials printed')


if __name__=='__main__':
    run()
