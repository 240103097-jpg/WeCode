"""Validate OpenAPI, local refs, all examples and the actual frontend boundary.

No server or frontend client is implemented or executed. Requires the isolated
requirements.txt plus the existing frontend TypeScript dependency for AST reads.
"""
from __future__ import annotations
import copy
import json
import os
from pathlib import Path
import subprocess
import sys
import yaml
from jsonschema import FormatChecker
from openapi_schema_validator import OAS30Validator
from openapi_spec_validator import validate_spec

ROOT=Path(__file__).resolve().parents[2]
# Reject duplicate YAML keys instead of silently taking the last occurrence.
class UniqueLoader(yaml.SafeLoader):
    pass
def mapping(loader,node,deep=False):
    result={}
    for key_node,value_node in node.value:
        key=loader.construct_object(key_node,deep=deep)
        if key in result:
            raise ValueError(f'Duplicate YAML key: {key}')
        result[key]=loader.construct_object(value_node,deep=deep)
    return result
UniqueLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,mapping)
doc=yaml.load((ROOT/'openapi.yml').read_text(),Loader=UniqueLoader)
validate_spec(doc)
print('PASS OpenAPI 3.0.3 specification validator')
ref_count=0
def dereference(node,stack=()):
    global ref_count
    if isinstance(node,list):return [dereference(v,stack) for v in node]
    if not isinstance(node,dict):return node
    if '$ref' in node:
        ref_count+=1
        ref=node['$ref']
        assert set(node)=={'$ref'}, f'Unsupported ref siblings: {ref}'
        assert ref.startswith('#/'),f'Nonlocal reference: {ref}'
        assert ref not in stack,f'Cyclic reference: {ref}'
        current=doc
        for piece in ref[2:].split('/'):
            current=current[piece.replace('~1','/').replace('~0','~')]
        return dereference(current,stack+(ref,))
    return {key:dereference(value,stack) for key,value in node.items()}
resolved=dereference(doc)
print(f'PASS {ref_count} local reference occurrences resolved; no unresolved/external/cyclic refs')
formatter=FormatChecker()
checked=0
def check(value,schema,label):
    global checked
    errors=list(OAS30Validator(schema,format_checker=formatter).iter_errors(value))
    assert not errors,f'{label}: '+ '; '.join(f'{list(e.path)} {e.message}' for e in errors)
    checked+=1
schema_types={'object','array','string','number','integer','boolean'}
def examples(node,label='$'):
    if isinstance(node,list):
        for i,value in enumerate(node):examples(value,f'{label}[{i}]')
    elif isinstance(node,dict):
        typ=node.get('type')
        if 'example' in node and ((isinstance(typ,str) and typ in schema_types) or 'oneOf' in node or 'allOf' in node):
            check(node['example'],node,label+'.example')
        if 'schema' in node:
            if 'example' in node:check(node['example'],node['schema'],label+'.example')
            for name,value in node.get('examples',{}).items():
                assert 'value' in value,f'Example needs a literal value: {label}.{name}'
                check(value['value'],node['schema'],label+'.examples.'+name)
        for key,value in node.items():
            if key not in {'example','examples'}:examples(value,label+'.'+key)
examples(resolved)
print(f'PASS {checked} schema/media/parameter/header example occurrences with format validation')

node=os.environ.get('NODE_BIN','node')
shape=json.loads(subprocess.check_output([node,str(ROOT/'tools/contract/frontend-shape.mjs')],text=True))
operations={}
for path,item in doc['paths'].items():
    for method,op in item.items():
        if method not in {'get','post','put','patch','delete'}:continue
        service=op['x-frontend-service']
        assert service not in operations,f'Duplicate service mapping: {service}'
        operations[service]=(path,method,resolved['paths'][path][method])
assert len({op[2]['operationId'] for op in operations.values()})==len(operations),'Duplicate operationId'
mock_only=set(doc['x-mock-only-service-methods'])
assert mock_only=={'simulateFailure'}
assert set(shape['methods'])==set(operations)|mock_only,'Frontend method coverage mismatch'
mock_source=(ROOT/'frontend/src/services/mockService.ts').read_text()
import re
mock_methods=set(re.findall(r'^  (\w+):',mock_source,re.M))
assert mock_methods==set(shape['methods']),'Mock implementation method coverage mismatch'
assert set(shape['consumers'])<=set(shape['methods']),'Unmapped consumer call'
assert all(name in shape['consumers'] for name in shape['methods']),'Method missing actual consumer review'
for name,enum in [('Track','tracks'),('Level','levels')]:assert doc['components']['schemas'][name]['enum']==shape['enums'][enum]
S=resolved['components']['schemas']
for name in ['Learner','Unit','Attempt','ExerciseProgress','UnitProgress','Snapshot','Feedback']:
    fields=shape['interfaces'][name]
    assert set(S[name]['properties'])=={f['name'] for f in fields},f'{name} fields drifted from TS'
    assert set(S[name]['required'])=={f['name'] for f in fields if not f['optional']},f'{name} required fields drifted'
for variant in S['Exercise']['oneOf']:
    props={f['name'] for f in shape['interfaces']['Exercise']}
    assert set(variant['properties'])<=props
    assert {'id','type','prompt'}<=set(variant['required'])
for method,(_,_,op) in operations.items():
    fields=shape['methods'][method]['input']
    if fields:
        frontend={f['name'] for f in fields}
        api=set(op.get('requestBody',{}).get('content',{}).get('application/json',{}).get('schema',{}).get('properties',{}))|{p['name'] for p in op.get('parameters',[])}
        if method=='register':assert api==frontend|{'password'}
        elif method=='login':assert api==(frontend-{'passphrase'})|{'password'}
        else:assert api==frontend,f'{method} input drift'
    security=op.get('security',doc['security'])
    assert security==([] if method in {'register','login'} else [{'bearerAuth':[]}]),f'{method} security mismatch'
    if security:assert '401' in op['responses']
    for parameter in op.get('parameters',[]):assert parameter['name'] in {'unitId','exerciseId'} and parameter['required']
print(f'PASS actual frontend AST: {len(shape["methods"])} methods = {len(operations)} HTTP operations + {len(mock_only)} mock-only; {len(shape["interfaces"])} interface declarations reviewed')

# Validate the real authored curriculum as public Unit responses, not just toy YAML.
source=(ROOT/'frontend/src/data/curriculum.ts').read_text()
units=json.loads(source.split('export const units: Unit[] = ',1)[1].split(';\n',1)[0])
assert len(units)==9 and len({(u['track'],u['level']) for u in units})==9
assert sum(len(u['exercises']) for u in units)==27
for unit in units:
    check(unit,S['Unit'],unit['id'])
    assert {ex['type'] for ex in unit['exercises']}=={'Quiz','Fix the Bug','Complete the Code'}

def schema_props(schema):
    keys=set(schema.get('properties',{}))
    for value in schema.get('properties',{}).values():keys|=schema_props(value)
    if isinstance(schema.get('items'),dict):keys|=schema_props(schema['items'])
    for key in ['oneOf','allOf','anyOf']:
        for value in schema.get(key,[]):keys|=schema_props(value)
    return keys
assert not schema_props(S['Unit']) & {'answer','solution','hint','accepted','rejected','explanation','correct','answerRules','password','accessToken'}
assert not schema_props(S['Learner']) & {'password','passphrase','accessToken'}
assert len(S['Snapshot']['example']['units'])==9
snapshot=S['Snapshot']['example'];unit_lookup={u['id']:u for u in units}
for unit_id,state in snapshot['progress'].items():
    unit=unit_lookup[unit_id]
    assert set(state['exercises'])<={e['id'] for e in unit['exercises']}
    for ex_state in state['exercises'].values():assert not ex_state['independent'] or ex_state['correct']
complete=sum(state['read'] and all(state['exercises'].get(e['id'],{}).get('correct',False) for e in unit_lookup[id]['exercises']) for id,state in snapshot['progress'].items())
assert complete==1,'Snapshot example completion inconsistent'
assert sum(s['independent'] for p in snapshot['progress'].values() for s in p['exercises'].values())==2
assert all(a['exerciseId'] in {e['id'] for u in units for e in u['exercises']} for a in snapshot['attempts'])
print('PASS actual 9-unit/27-exercise payload coverage, secret-field exclusion and example completion semantics')

negative_count=0
def rejects(schema,value,label):
    global negative_count
    assert list(OAS30Validator(schema,format_checker=formatter).iter_errors(value)),f'Negative accepted: {label}'
    negative_count+=1
for variant in ['QuizExercise','TextExercise']:
    for secret in ['answer','accepted','solution','hint','correctOptionId']:
        bad=copy.deepcopy(S[variant]['example']);bad[secret]='leaked-key';rejects(S[variant],bad,variant+'.'+secret)
for name in ['RegisterInput','LoginInput','ProfileInput','PreferencesInput','SubmissionInput','LessonReadInput']:
    bad=copy.deepcopy(S[name]['example']);bad['userId']='another-user';rejects(S[name],bad,name+'.userId')
rejects(S['PreferencesInput'],{'track':'Java','level':'Beginner'},'unknown track')
rejects(S['PreferencesInput'],{'track':'Python','level':'Expert'},'unknown level')
rejects(S['SubmissionInput'],{'answer':'  '},'blank answer')
rejects(S['SubmissionInput'],{'answer':'x'*4001},'wire size cap')
rejects(S['LessonReadInput'],{'read':False},'unread reset')
rejects(S['Attempt'],dict(S['Attempt']['example'],createdAt='yesterday'),'bad timestamp format')
rejects(S['ExerciseProgress'],{'correct':False,'independent':True,'revealed':False,'hintCount':0},'false independent mastery')
rejects(S['Snapshot'],dict(snapshot,units=units[:1]),'incomplete curriculum inventory')
rejects(S['AuthSession'],dict(S['AuthSession']['example'],password='leaked-credential'),'password in auth output')
rejects(S['ProfileInput'],{'name':'Valid','email':'changed@example.test'},'email edit not supported')
print(f'PASS {negative_count} negative schema checks (key leakage, impersonation fields, invalid enum/format/state/payload)')
print('PASS contract checks complete; no backend/client/application code executed')
