"""Every test response is checked against the reviewed root operation schema."""
import re
import pytest
from fastapi.testclient import TestClient
from openapi_schema_validator import OAS30Validator
from jsonschema import FormatChecker
from backend.wecode.app import create_app
from backend.wecode.contract import DOCUMENT, resolve


class ContractClient(TestClient):
    def request(self, method, url, **kwargs):
        response = super().request(method, url, **kwargs)
        path = str(url).split('?')[0].removeprefix('/api/v1')
        for template, operations in DOCUMENT['paths'].items():
            if re.fullmatch(re.sub(r'\{[^}]+\}', '[^/]+', template), path) and method.lower() in operations:
                operation = operations[method.lower()]
                assert str(response.status_code) in operation['responses'], (method, path, response.status_code, response.text)
                definition = resolve(operation['responses'][str(response.status_code)])
                assert response.headers['cache-control'] == 'no-store'
                for name, header in definition.get('headers', {}).items():
                    OAS30Validator(header['schema']).validate(response.headers[name])
                if 'content' in definition:
                    assert response.headers['content-type'].startswith('application/json')
                    OAS30Validator(definition['content']['application/json']['schema'], format_checker=FormatChecker()).validate(response.json())
                else:
                    assert response.content == b''
                break
        return response


@pytest.fixture
def client(request, tmp_path):
    from backend.wecode.storage import MemoryStorage
    from backend.wecode.sql_storage import SQLStorage
    storage = SQLStorage('sqlite:///' + str(tmp_path / 'api.sqlite3')) if getattr(request, 'param', 'memory') == 'sqlite' else MemoryStorage()
    try:
        with ContractClient(create_app(storage=storage)) as instance:
            yield instance
    finally:
        if hasattr(storage, 'close'):
            storage.close()


def pytest_generate_tests(metafunc):
    # Run the unchanged API behaviors against both adapters; every SQLite DB is isolated.
    if 'client' in metafunc.fixturenames:
        metafunc.parametrize('client', ['memory', 'sqlite'], indirect=True)


@pytest.fixture
def register(client):
    def create(email='learner@example.test'):
        response = client.post('/api/v1/auth/register', json={'name': 'Test Learner', 'email': email, 'password': 'test-only-password-42'})
        assert response.status_code == 201
        return response.json(), {'Authorization': 'Bearer ' + response.json()['accessToken']}
    return create
