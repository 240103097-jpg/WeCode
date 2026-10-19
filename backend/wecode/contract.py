"""Use the reviewed root agreement as the strict request-schema source of truth."""
from copy import deepcopy
from pathlib import Path
import yaml
from openapi_schema_validator import OAS30Validator
from jsonschema import FormatChecker

ROOT = Path(__file__).resolve().parents[2]
DOCUMENT = yaml.safe_load((ROOT / 'openapi.yml').read_text())


def resolve(value):
    if isinstance(value, dict):
        if '$ref' in value:
            target = DOCUMENT
            for part in value['$ref'][2:].split('/'):
                target = target[part.replace('~1', '/').replace('~0', '~')]
            return resolve(target)
        return {key: resolve(item) for key, item in value.items()}
    if isinstance(value, list):
        return [resolve(item) for item in value]
    return value


SCHEMAS = {name: resolve(schema) for name, schema in DOCUMENT['components']['schemas'].items()}


def valid(name, value):
    return OAS30Validator(SCHEMAS[name], format_checker=FormatChecker()).is_valid(value)


def normalize_input(value):
    value = deepcopy(value)
    if isinstance(value, dict):
        for key in ('name', 'email'):
            if isinstance(value.get(key), str):
                value[key] = value[key].strip()
        if isinstance(value.get('email'), str):
            value['email'] = value['email'].lower()
    return value
