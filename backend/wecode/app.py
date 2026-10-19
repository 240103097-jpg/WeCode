"""Contract-first API. Run from repository root with one Uvicorn worker."""
from copy import deepcopy
from datetime import datetime, timedelta, timezone
import hashlib
import json
import secrets
from uuid import uuid4

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError, InvalidHashError
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, Response
from starlette.exceptions import HTTPException

from .contract import DOCUMENT, normalize_input, valid
from .storage import MemoryStorage, StorageUnavailable
from .curriculum import Curriculum


class ApiError(Exception):
    def __init__(self, status, code, message):
        self.status, self.code, self.message = status, code, message


def error_response(status, code, message):
    headers = {'Cache-Control': 'no-store'}
    if status == 401:
        headers['WWW-Authenticate'] = 'Bearer'
    return JSONResponse({'error': {'code': code, 'message': message}}, status_code=status, headers=headers)


def utcnow():
    return datetime.now(timezone.utc)


def stamp(time):
    return time.isoformat(timespec='milliseconds').replace('+00:00', 'Z')


def token_key(token):
    return hashlib.sha256(token.encode()).hexdigest()


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('Duplicate JSON key')
        result[key] = value
    return result


def create_app(storage=None, clock=utcnow):
    app = FastAPI(title='WeCode API', openapi_url='/openapi.json')
    app.openapi = lambda: deepcopy(DOCUMENT)
    app.state.storage = storage if storage is not None else MemoryStorage()
    app.state.clock = clock
    app.state.curriculum = Curriculum()
    app.state.hasher = PasswordHasher()  # Argon2id defaults; random salt per hash.
    app.state.dummy_hash = app.state.hasher.hash(secrets.token_urlsafe(32))

    @app.middleware('http')
    async def transport(request, call_next):
        try:
            # Only operations with JSON request bodies require media/JSON parsing.
            request.state.body = None
            if (request.method, request.url.path) in {
                ('POST', '/api/v1/auth/register'), ('POST', '/api/v1/auth/login'),
                ('PATCH', '/api/v1/me'), ('PATCH', '/api/v1/me/preferences'),
            } or (request.method == 'PUT' and request.url.path.endswith('/lesson-read')) or (
                request.method == 'POST' and request.url.path.endswith('/submissions')):
                if request.headers.get('content-type', '').split(';')[0].strip().lower() != 'application/json':
                    raise ApiError(415, 'validation', 'Use application/json for this request.')
                try:
                    request.state.body = json.loads(await request.body(), object_pairs_hook=unique_object,
                                                    parse_constant=lambda _: (_ for _ in ()).throw(ValueError()))
                except (ValueError, UnicodeDecodeError):
                    raise ApiError(400, 'validation', 'Request body must contain valid JSON.')
            if (request.method == 'POST' and request.url.path.endswith('/hints')) or (
                request.method == 'PUT' and request.url.path.endswith('/solution-reveal')):
                if await request.body():
                    raise ApiError(422, 'validation', 'This operation does not accept a request body.')
            response = await call_next(request)
        except ApiError as error:
            response = error_response(error.status, error.code, error.message)
        except StorageUnavailable:
            response = error_response(503, 'unavailable', 'The service is temporarily unavailable. Please retry.')
        except Exception:
            # Never echo/log exception details, request values, credentials or learner answers.
            response = error_response(500, 'internal', 'The service could not complete this request.')
        response.headers['Cache-Control'] = 'no-store'
        return response

    @app.exception_handler(ApiError)
    async def api_error(_, error):
        return error_response(error.status, error.code, error.message)

    @app.exception_handler(StorageUnavailable)
    async def unavailable(_, error):
        return error_response(503, 'unavailable', 'The service is temporarily unavailable. Please retry.')

    @app.exception_handler(HTTPException)
    async def http_error(_, error):
        return error_response(error.status_code, 'not-found', 'This resource is unavailable.')

    def body(request, schema):
        value = normalize_input(request.state.body)
        if not valid(schema, value):
            raise ApiError(422, 'validation', 'Request fields are missing or invalid.')
        return value

    def current(request, state):
        parts = request.headers.get('authorization', '').split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            raise ApiError(401, 'unauthorized', 'Sign in with a valid session.')
        session = state.sessions.get(token_key(parts[1]))
        if not session or session['expires'] <= clock() or session['account'] not in state.accounts:
            raise ApiError(401, 'unauthorized', 'Sign in with a valid session.')
        return state.accounts[session['account']], token_key(parts[1])

    def session(state, account):
        token = secrets.token_urlsafe(32)
        expires = clock() + timedelta(hours=24)
        state.sessions[token_key(token)] = {'account': account['learner']['id'], 'expires': expires}
        return {'learner': deepcopy(account['learner']), 'accessToken': token, 'tokenType': 'Bearer', 'expiresAt': stamp(expires)}

    @app.post('/api/v1/auth/register', status_code=201)
    def register(request: Request):
        data = body(request, 'RegisterInput')
        hashed = app.state.hasher.hash(data['password'])
        with app.state.storage.transaction() as state:
            if data['email'] in state.emails:
                raise ApiError(409, 'duplicate', 'An account already uses this email. Sign in instead.')
            learner = {'id': str(uuid4()), 'name': data['name'], 'email': data['email'], 'activeTrack': 'Python',
                       'levels': {track: 'Beginner' for track in ('Python', 'SQL', 'Git')}, 'onboarded': False}
            account = {'learner': learner, 'password_hash': hashed, 'progress': {}, 'attempts': []}
            state.accounts[learner['id']] = account
            state.emails[data['email']] = learner['id']
            result = session(state, account)
        return result

    @app.post('/api/v1/auth/login')
    def login(request: Request):
        data = body(request, 'LoginInput')
        with app.state.storage.transaction() as state:
            account = state.accounts.get(state.emails.get(data['email']))
            hashed = account['password_hash'] if account else app.state.dummy_hash
            try:
                app.state.hasher.verify(hashed, data['password'])
            except (VerificationError, InvalidHashError):
                raise ApiError(401, 'credentials', 'Email or password is incorrect.')
            if not account:
                raise ApiError(401, 'credentials', 'Email or password is incorrect.')
            if app.state.hasher.check_needs_rehash(hashed):
                account['password_hash'] = app.state.hasher.hash(data['password'])
            result = session(state, account)
        return result

    @app.get('/api/v1/me')
    def me(request: Request):
        with app.state.storage.transaction() as state:
            account, _ = current(request, state)
            return deepcopy(account['learner'])

    @app.delete('/api/v1/auth/session', status_code=204)
    def logout(request: Request):
        with app.state.storage.transaction() as state:
            _, key = current(request, state)
            del state.sessions[key]
        return Response(status_code=204)

    @app.patch('/api/v1/me', status_code=204)
    def profile(request: Request):
        with app.state.storage.transaction() as state:
            account, _ = current(request, state)
            data = body(request, 'ProfileInput')
            account['learner']['name'] = data['name']
        return Response(status_code=204)

    def unit_id(request):
        value = request.path_params['unitId']
        if not valid('Identifier', value):
            raise ApiError(422, 'validation', 'Unit identifier is invalid.')
        if not app.state.curriculum.has_unit(value):
            raise ApiError(404, 'not-found', 'This unit is unavailable.')
        return value

    @app.patch('/api/v1/me/preferences', status_code=204)
    def preferences(request: Request):
        with app.state.storage.transaction() as state:
            account, _ = current(request, state)
            data = body(request, 'PreferencesInput')
            learner = account['learner']
            learner['activeTrack'] = data['track']
            learner['levels'][data['track']] = data['level']
            if data.get('onboarded'):
                learner['onboarded'] = True
        return Response(status_code=204)

    @app.get('/api/v1/me/snapshot')
    def snapshot(request: Request):
        with app.state.storage.transaction() as state:
            account, _ = current(request, state)
            return {'learner': deepcopy(account['learner']), 'units': app.state.curriculum.public_units(),
                    'progress': deepcopy(account['progress']), 'attempts': deepcopy(account['attempts'])}

    @app.put('/api/v1/me/units/{unitId}/lesson-read', status_code=204)
    def mark_read(request: Request):
        with app.state.storage.transaction() as state:
            account, _ = current(request, state)
            unit = unit_id(request)
            body(request, 'LessonReadInput')
            account['progress'].setdefault(unit, {'read': False, 'exercises': {}})['read'] = True
        return Response(status_code=204)

    def exercise(request):
        unit = unit_id(request)
        exercise_id = request.path_params['exerciseId']
        if not valid('Identifier', exercise_id):
            raise ApiError(422, 'validation', 'Exercise identifier is invalid.')
        rule = app.state.curriculum.rule(unit, exercise_id)
        if rule is None:
            raise ApiError(404, 'not-found', 'This exercise is unavailable.')
        return unit, exercise_id, rule

    def exercise_state(account, unit, exercise_id):
        progress = account['progress'].setdefault(unit, {'read': False, 'exercises': {}})
        return progress['exercises'].setdefault(exercise_id, {
            'correct': False, 'independent': False, 'revealed': False, 'hintCount': 0})

    @app.post('/api/v1/me/units/{unitId}/exercises/{exerciseId}/submissions', status_code=201)
    def submit(request: Request):
        with app.state.storage.transaction() as state:
            account, _ = current(request, state)
            unit, exercise_id, rule = exercise(request)
            data = body(request, 'SubmissionInput')
            answer = data['answer'].replace('\r\n', '\n').strip()
            if not answer or len(answer) > 4000:
                raise ApiError(422, 'validation', 'Enter an answer between 1 and 4,000 characters.')
            progress = exercise_state(account, unit, exercise_id)
            correct = answer in rule['accepted']
            assisted = progress['revealed']
            if correct:
                progress['correct'] = True
                if not assisted:
                    progress['independent'] = True
            text = rule['explanation'] if correct else rule['incorrect']
            account['attempts'].append({'id': str(uuid4()), 'exerciseId': exercise_id, 'answer': answer,
                                        'correct': correct, 'assisted': assisted,
                                        'createdAt': stamp(clock()), 'feedback': text})
            result = {'correct': correct, 'text': text, 'assisted': assisted}
        return result

    @app.post('/api/v1/me/units/{unitId}/exercises/{exerciseId}/hints')
    def hint(request: Request):
        with app.state.storage.transaction() as state:
            account, _ = current(request, state)
            unit, exercise_id, rule = exercise(request)
            if not any(attempt['exerciseId'] == exercise_id and not attempt['correct'] for attempt in account['attempts']):
                raise ApiError(409, 'hint-locked', 'Try an answer first. Hints unlock after an incorrect submission.')
            exercise_state(account, unit, exercise_id)['hintCount'] += 1
            result = rule['hint']
        return result

    @app.put('/api/v1/me/units/{unitId}/exercises/{exerciseId}/solution-reveal')
    def solution(request: Request):
        with app.state.storage.transaction() as state:
            account, _ = current(request, state)
            unit, exercise_id, rule = exercise(request)
            exercise_state(account, unit, exercise_id)['revealed'] = True
            result = {'answer': rule['accepted'][0], 'explanation': rule['explanation']}
        return result

    return app


app = create_app()
