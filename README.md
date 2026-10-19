# WeCode

An English learning workspace for Python, SQL and Git. Individual academic project due October 20, 2026 (Asia/Almaty); exact submission time unknown.

## Current stage

Interactive frontend with a centralized typed mockService. React, TypeScript and Vite are selected; Python/FastAPI, SQLAlchemy and SQLite are selected for later stages. The root OpenAPI contract defines the in-memory FastAPI backend, implemented in issues #12–14 with independent QA gates. The frontend still uses mockService; no real API client or database is implemented.

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
- [Canonical GitHub backlog](https://github.com/240103097-jpg/WeCode/issues)

PM refines issues, engineer implements and tests, independent QA verifies every criterion and alone closes after PASS. Stage order: mocked frontend → root openapi.yml → in-memory backend → ORM/SQLite → integration and thorough testing. The full original planning transcript is still needed; the summary is not a verbatim export.

## In-memory backend

Python 3.13 was verified. From the repository root:

```sh
python3 -m venv /tmp/wecode-backend-venv
/tmp/wecode-backend-venv/bin/python -m pip install -r backend/requirements-dev.txt
/tmp/wecode-backend-venv/bin/python -m uvicorn backend.wecode.app:app --host 127.0.0.1 --port 8000 --workers 1 --no-access-log
/tmp/wecode-backend-venv/bin/python -m pytest backend/tests -q
```

Run tests in another shell while the server is running. Runtime-only installations can use `backend/requirements.txt`; development requirements also install the contract validator. Dependencies follow the existing pinned Python requirements/isolated-environment convention.

API base: http://127.0.0.1:8000/api/v1. Interactive API docs: http://127.0.0.1:8000/docs. The reviewed root contract is served at http://127.0.0.1:8000/openapi.json. Use HTTPS outside local development. The browser frontend remains independently mocked and is not connected to this server.

**In-memory data is lost on restart:** accounts, sessions, preferences, attempts and progress exist only in one process. Run exactly one worker, without reload when retaining temporary data matters. No database or filesystem learner records are written. Real API registration requires a private 12–128 character password; the public mock passphrase grants no special access. Passwords use salted Argon2id hashes; opaque 256-bit session tokens expire after 24 hours and current-session logout revokes them. Never put credentials in URLs or logs. No access logging is enabled by the documented command.

The storage protocol exposes atomic transactions; the memory adapter serializes operations and rolls back failed writes. Domain/API code receives storage through `create_app(storage=...)`, ready for a separately authorized persistence adapter. Root contract validation supplies strict request types/fields without coercion. API tests validate actual statuses, headers and response payloads against that same contract.

The server loads [backend/data/curriculum.json](backend/data/curriculum.json), a literal export of the existing frontend curriculum, including private server answer rules. It does not require Node or the frontend at runtime. Public snapshots serialize only the separately held public units. Check authoring drift without executing TypeScript:

```sh
python3 backend/scripts/sync_curriculum.py
/tmp/wecode-backend-venv/bin/python backend/scripts/smoke.py
```

The smoke command needs the running local server and creates a disposable in-memory account, without printing its generated credentials. Only an authorized content change should regenerate the export with `--write`.

Backend validation commands from the root:

```sh
/tmp/wecode-backend-venv/bin/python -m pytest backend/tests -q
/tmp/wecode-backend-venv/bin/python -m pip check
python3 backend/scripts/sync_curriculum.py
/tmp/wecode-backend-venv/bin/openapi-spec-validator openapi.yml
/tmp/wecode-backend-venv/bin/python tools/contract/validate.py
```

The final command requires Node on PATH and existing frontend TypeScript dependencies, as described above; the running backend does not. Tests exercise every operation, all 27 exercises, ownership, strict errors, secret exclusion, authentication, assisted/independent history, retries, completion, concurrent writes and failed-commit rollback. TestClient checks response statuses, headers and schemas against root OpenAPI. One upstream Starlette/AnyIO TestClient deprecation warning is currently emitted; it does not affect results.
