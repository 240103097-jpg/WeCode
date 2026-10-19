# WeCode

An English learning workspace for Python, SQL and Git. Individual academic project due October 20, 2026 (Asia/Almaty); exact submission time unknown.

## Current stage

Interactive frontend with a centralized typed mockService. React, TypeScript and Vite power the frontend; Python/FastAPI powers the backend, with SQLAlchemy/SQLite persistence in this stage. The root OpenAPI contract defines the FastAPI backend; issues #15–16 add persistence after the independently verified in-memory stage. The frontend still uses mockService; no real frontend API client is implemented.

## Local development

With Node.js 22.12+ and pnpm 11.25+ installed:

```sh
cd frontend
pnpm install
pnpm dev
```

Preview after starting Vite: http://127.0.0.1:5173 (use the actual URL printed by Vite if occupied). Use `pnpm dev` to start the preview if it is not already running.

On this Codex desktop installation, Node/pnpm are bundled but not on the default shell PATH. Before the commands above, this environment can use:

```sh
export PATH="$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin:$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/fallback:$PATH"
```

This fallback is specific to this desktop installation; other machines should install Node.js and pnpm normally.

```sh
pnpm contrast
pnpm typecheck
pnpm test
pnpm build
```

## API contract validation

The [API mapping](docs/api-mapping.md) covers all service methods and explicitly documents real authentication differences from mock accounts. To validate the root agreement (with Node on PATH):

```sh
python3 -m venv /tmp/wecode-openapi-venv
/tmp/wecode-openapi-venv/bin/python -m pip install -r tools/contract/requirements.txt
/tmp/wecode-openapi-venv/bin/openapi-spec-validator openapi.yml
/tmp/wecode-openapi-venv/bin/python tools/contract/validate.py
```

Validation tooling is isolated from application/backend dependencies. The custom check also reads the existing frontend TypeScript AST, resolves references and checks examples/coverage. See the mapping for prerequisites and limitations.

## Demo accounts and learning data

Create an account with a made-up email and display name. To sign in again, use the same local email and the public demo passphrase **practice-only**. No real password is requested or stored. This is mock authentication, not secure authentication; local data and bundled answer keys are inspectable. Accounts and progress stay in this browser, with no server sync. Clearing browser data removes them.

The curriculum includes 9 units and 27 exercises across all three tracks and levels. Mark a lesson read and correctly answer its three exercises to complete a unit. Assisted answers count toward completion and are labeled separately from independent solving. No XP or scoring is used. Checking uses authored fragments, not arbitrary code execution or general semantic validation.

All data operations go through [the typed service boundary](docs/mock-service.md). Settings includes a clearly labeled failure simulation; Retry restores the workspace without changing saved progress.

## Project documents

- [Specification and preserved brainstorming summary](WeCode_Project_Specification.md)
- [Agent instructions](AGENTS.md)
- [Selected stack and delegated defaults](docs/decisions.md)
- [Design system and inspected visual references](docs/design-system.md)
- [Process](docs/process.md), [task template](docs/task-template.md), [testing guidelines](docs/testing-guidelines.md)
- [Frontend QA evidence](docs/qa/frontend.md)
- [Retro redesign verification](docs/qa/redesign.md)
- [Independent API contract verification](docs/qa/api-contract.md)
- [In-memory backend architecture](docs/backend.md)
- [Independent in-memory backend QA](docs/qa/backend.md)
- [Canonical GitHub backlog](https://github.com/240103097-jpg/WeCode/issues)

PM refines issues, engineer implements and tests, independent QA verifies every criterion and alone closes after PASS. Stage order: mocked frontend → root openapi.yml → in-memory backend → ORM/SQLite → integration and thorough testing. The full original planning transcript is still needed; the summary is not a verbatim export.

## SQLite backend

Python 3.13, SQLAlchemy 2.0.44 and SQLite were verified. From the repository root:

```sh
python3 -m venv /tmp/wecode-backend-venv
/tmp/wecode-backend-venv/bin/python -m pip install -r backend/requirements-dev.txt
export DATABASE_URL=sqlite:////tmp/wecode.sqlite3
/tmp/wecode-backend-venv/bin/python backend/scripts/init_db.py
/tmp/wecode-backend-venv/bin/python -m uvicorn backend.wecode.app:create_app --factory --host 127.0.0.1 --port 8000 --workers 1 --no-access-log
```

Use another shell for tests while the server runs. Runtime-only installs can use `backend/requirements.txt`. The secret-free [.env.example](.env.example) shows DATABASE_URL; export it explicitly (no automatic dotenv loading). Choose an existing parent directory; four slashes indicate an absolute SQLite file path. Missing DATABASE_URL fails startup rather than silently using temporary memory. Local DB/environment files are ignored by Git. Only file-backed SQLite is supported/tested; no other database compatibility is claimed.

API base: http://127.0.0.1:8000/api/v1. [Interactive API docs](http://127.0.0.1:8000/docs); root agreement at http://127.0.0.1:8000/openapi.json. Use HTTPS outside localhost. The frontend still uses mockService and is not connected to this API. Real registration needs a private 12–128 character password; the public mock passphrase grants no special access.

Accounts, Argon2id password hashes, preferences, hashed-token sessions, authored curriculum, lesson/exercise state and attempts now survive backend restart. Sessions retain 24-hour expiry and current-token logout revocation. No raw password or bearer token is stored in SQLite. The explicit MemoryStorage adapter remains available only for regression tests; its old restart-loss behavior does not describe the default runtime.

Initialization creates missing tables and inserts the exact nine existing units/27 exercises by stable IDs; repeat startup preserves learner state. Conflicting stored/authored curriculum fails explicitly for migration review. `create_all` is initial schema setup, not an automatic column-migration mechanism. See [SQLite lifecycle and constraints](docs/sqlite.md) and [backend architecture](docs/backend.md). Previously running in-memory/browser-local mock records are not automatically imported; browser storage is untouched.

Verification commands:

```sh
/tmp/wecode-backend-venv/bin/python -m pytest backend/tests -q
/tmp/wecode-backend-venv/bin/python -m pip check
python3 backend/scripts/sync_curriculum.py
/tmp/wecode-backend-venv/bin/openapi-spec-validator openapi.yml
/tmp/wecode-backend-venv/bin/python tools/contract/validate.py
/tmp/wecode-backend-venv/bin/python backend/scripts/smoke.py
/tmp/wecode-backend-venv/bin/python backend/scripts/check_restart.py
```

Contract AST validation requires Node and existing frontend TypeScript dependencies as documented above; the running backend does not. Smoke needs the server at port 8000; the restart check independently launches/stops three real backend processes with an isolated temporary database/ports and removes that database afterward. It generates credentials only in memory and does not print them. Its expired-session case moves one disposable session timestamp into the past while stopped; it does not claim to wait 24 hours.

Existing API behaviors run against both MemoryStorage and isolated temporary SQLite files, validating response status/headers/schemas against root OpenAPI. Additional checks cover durable state, constraints, cross-adapter concurrency, initialization/drift, rollback, ownership, expiry/revocation and process restart. One upstream Starlette/AnyIO TestClient deprecation warning is emitted; it does not affect results. No learner code executes. No real frontend client, UI change or unrelated feature is included.
