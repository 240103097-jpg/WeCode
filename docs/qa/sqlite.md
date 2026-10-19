# SQLite persistence independent QA — issues #15–16

Date: October 19, 2026, Asia/Almaty. Independent reviewer: `sqlite_qa`, separate from the PM/implementing agent. The reviewer's actual criterion evidence is preserved below. QA alone closed both issues after sequential PASS gates.

- [#15 foundation PASS](https://github.com/240103097-jpg/WeCode/issues/15#issuecomment-6271838553) at `f90aa23dbabc59a20b28bb84bb42ead1e765e4e7`.
- [#16 full persistence PASS](https://github.com/240103097-jpg/WeCode/issues/16#issuecomment-6271972660) at published `7a32ee86807c7549f96af6cca7751d71a46aaa82`.

## Foundation gate

QA: PASS
Issue: #15; revision: f90aa23dbabc59a20b28bb84bb42ead1e765e4e7; environment: macOS, Python 3.13, SQLAlchemy 2.0.44, isolated temporary SQLite files. Independent QA reviewer/session; no implementation edits.

Criterion 1: PASS — inspected ORM Account/Preference/AuthSession models, normalized unique email/Argon2id hash-only password and SHA-256 token digest storage, all profile/preference fields, UTC expiry; secret-free .env.example present. No tracked DB/environment secrets.
Criterion 2: PASS — SQL adapter implements existing transaction State boundary. Guard UPDATE occurs before load; SQLAlchemy transaction context commits/rolls back; FK/unique/check constraints and two-adapter concurrent registration tested. Only necessary SQLite PRAGMA handwritten; docs explicitly claim SQLite only.
Criterion 3: PASS — all auth/profile/preferences API tests run for memory and isolated SQLite; ContractClient validates actual status/body/headers against root schemas. SQL-specific reopen test preserves profile/preferences/valid sessions, revoked token stays revoked, 24-hour expiry rejects, login remains valid after recreation. Two-adapter concurrent duplicate registration yields one 201/five 409; other-user preferences isolated. Flushed-write failure rolls back with safe 503.
Criterion 4: PASS — documented initialization executed twice on isolated /tmp/wecode-qa15-init.sqlite3; both pass without reset. Reviewed schema lifecycle/no automatic destructive migration statement. Runtime remains memory at foundation gate. Independently exercised unsupported SQL lesson-read: safe 503 and subsequent snapshot progress empty (rollback).
Criterion 5: PASS — independent checks completed before dependent #16 gate; QA alone closes this issue.

Commands/results:
- /tmp/wecode-backend-venv/bin/python -m pytest backend/tests -q: 103 passed, one upstream Starlette/AnyIO deprecation warning.
- DATABASE_URL=sqlite:////tmp/wecode-qa15-init.sqlite3 /tmp/wecode-backend-venv/bin/python backend/scripts/init_db.py: PASS, repeated twice.
- /tmp/wecode-backend-venv/bin/python -m pip check: no broken requirements.
- Independent temporary-DB HTTP TestClient unsupported-learning rollback check: PASS (503, no progress saved).
- git diff 76f3aa7 -- frontend openapi.yml: empty; git diff --check: PASS; tracked DB/.env search: empty; working tree clean.

No failed or unverified acceptance criteria. Disposition: independent QA closes #15 after PASS; #16 may now proceed.

## Full persistence gate

QA: PASS
Issue: #16; revision: 7a32ee86807c7549f96af6cca7751d71a46aaa82; environment: macOS, Python 3.13, SQLAlchemy 2.0.44, file-backed temporary SQLite, bundled Node 24.19.0. Independent QA reviewer/session; no implementation edits.

Criterion 1: PASS — reviewed normalized ORM account/preferences/sessions, authored unit/exercise/rule, lesson/exercise state and stable per-account attempt sequence. Runtime create_app factory requires DATABASE_URL and defaults to SQLStorage. All mutable learner State reconstructed from DB per transaction; immutable curriculum loaded from ORM with public/private separation. No backend memory runtime fallback.
Criterion 2: PASS — reviewed repeatable stable-ID insert plus explicit content-drift/inventory rejection. FK/composite unique/check constraints protect ownership/state; guard UPDATE before mutable load serializes independent connections. Tests verify simultaneous reveal/submission/hint/read ordering, monotonic assistance flags, exact attempt sequences/counts and one exercise state; all-unit repeat attempts yield9/9 units, not duplicate credit.
Criterion 3: PASS — independently ran full unchanged API behavior/contract suite against both memory and isolated temporary SQLite fixtures:162passed. Covers all27 authored exercises/9 units, all auth operations/errors/isolation, reopen persistence, concurrency, initialization/drift, constraints, flushed-write rollback for account/progress/attempts. Every test response status/header/body schema checked against root contract. Frontend and root openapi.yml diff versus76f3aa7 empty.
Criterion 4: PASS — independently executed check_restart.py: three distinct real Uvicorn processes use one disposable SQLite DB. Profile/all-track preferences, lesson-read,9 attempts, hints/reveal/assistance and completion survive stop/restart and fresh login exactly. Live sessions persist, logged-out session remains revoked, offline-expired disposable session rejected; other account history/progress empty. Repeated startup keeps9units/27exercises without resets/duplicates. Expiry test edits only one disposable timestamp while stopped; no claim of waiting24hours. Independently ran actual HTTP smoke against running SQLite server: all11 operations/three types contract-checked PASS.
Criterion 5: PASS — reviewed README/AGENTS/spec/decisions/backend/API mapping/testing/SQLite lifecycle docs, example env and stage limits. Setup/init/factory/test/restart commands match actual commands. No real frontend client/UI/contract/content changes or tracked databases/.env secrets. Actual root validator/custom checks, curriculum equality, frontend regression checks, Markdown targets and diff checks pass. Published origin/main verified at reviewed7a32ee86807c7549f96af6cca7751d71a46aaa82; commit timestamp2026-10-19T21:24:30+05:00.
Criterion 6: PASS — independent verification completed after #15 QA gate. No failed/unverified criterion; QA alone closes #16.

Actual commands/results (repository root):
- /tmp/wecode-backend-venv/bin/python -m pytest backend/tests -q:162passed; one upstream Starlette/AnyIO deprecation warning.
- /tmp/wecode-backend-venv/bin/python backend/scripts/check_restart.py: PASS all three process/restart/session/state checks; temporary DB removed; no credentials printed.
- /tmp/wecode-backend-venv/bin/python backend/scripts/smoke.py: PASS all11 HTTP operations, all3exercise types and contract responses.
- /tmp/wecode-backend-venv/bin/openapi-spec-validator openapi.yml: OK.
- /tmp/wecode-backend-venv/bin/python tools/contract/validate.py: PASS348reference occurrences,409example occurrences,12service methods/11HTTP operations+1mock-only,9units/27exercises,26negative checks.
- python3 backend/scripts/sync_curriculum.py: PASS exact existing curriculum/rules.
- /tmp/wecode-backend-venv/bin/python -m pip check: no broken requirements.
- pnpm --dir frontend contrast/typecheck/test/build (bundled Node/pnpm PATH): allPASS;19tests across5files, production build succeeds.
- Independent relative Markdown target check:50targetsPASS; git diff --check PASS; git ls-files database/.env search empty; git diff76f3aa7 -- frontend openapi.yml empty.
- git ls-remote origin refs/heads/main matches reviewed fullhash; working tree clean.

Disposition: independent QA closes #16 after PASS. SQLite persistence stage complete; frontend integration remains unauthorized/deferred.

## Reproduction and limits

See [README setup/run/check commands](../../README.md#sqlite-backend) and [SQLite lifecycle](../sqlite.md). The actual process check is `/tmp/wecode-backend-venv/bin/python backend/scripts/check_restart.py`: three distinct Uvicorn processes reuse one temporary SQLite file, with complete stops, new logins and exact snapshot comparison. A disposable session is moved into the past while stopped to check durable expiry; no literal 24-hour wait is claimed. Credentials are not printed and the isolated temporary DB is removed afterward.

The full suite runs existing API behaviors for both explicit MemoryStorage regressions and isolated temporary SQLite databases. Actual statuses, headers and response schemas are checked against the unchanged root contract; real HTTP smoke covers all 11 operations. Persistence-specific checks verify every learner-state field, stable history order, ownership, two-adapter concurrency, duplicate protection, rollback and repeatable curriculum initialization. Only SQLite compatibility is verified.

No real frontend adapter, UI or curriculum authoring change is included. Browser-local mock records were not touched. Previously running in-memory records are not silently imported. Final evidence-only documentation changes do not alter the reviewed backend implementation.
