# WeCode

An English learning workspace for Python, SQL and Git. Individual academic project due October 20, 2026 (Asia/Almaty); exact submission time unknown.

## Current stage

WeCode connects its retro React/TypeScript frontend to FastAPI and SQLAlchemy/SQLite through one typed API service. Real API mode is the complete-app default. Integration issue #17 passed independent QA and is closed. Final audit technical evidence is recorded. Independent QA passed and closed #4/#18 after the documented PM correction of the unsupported full-archive gate. The genuine manual transcript remains explicitly partial, with gaps disclosed; #19 remains open post-MVP. No deployment or instructor submission is claimed.

## Run the complete app locally

Python 3.13 and Node.js 22.12+/pnpm 11.25+ are verified. From the repository root, first prepare the backend:

```sh
python3 -m venv /tmp/wecode-backend-venv
/tmp/wecode-backend-venv/bin/python -m pip install -r backend/requirements-dev.txt
/tmp/wecode-backend-venv/bin/python backend/scripts/prepare_local.py
export DATABASE_URL="sqlite:///$PWD/data/wecode.sqlite3"
/tmp/wecode-backend-venv/bin/python -m uvicorn backend.wecode.app:create_app --factory --host 127.0.0.1 --port 8000 --workers 1 --no-access-log
```

In another shell from the repository root:

```sh
pnpm --dir frontend install --frozen-lockfile
pnpm --dir frontend dev
```

[Frontend preview](http://127.0.0.1:5173/) · [Backend API docs](http://127.0.0.1:8000/docs). Keep both processes running. Vite proxies `/api` to port 8000, so local browser calls are same-origin and need no permissive backend CORS. `API_PROXY_TARGET` changes the development/preview proxy target. [frontend/.env.example](frontend/.env.example) documents `VITE_API_BASE_URL=/api/v1` and `VITE_SERVICE_MODE=api`; Vite can read a deliberately created frontend/.env.local. Never put secrets in VITE variables, which are public build inputs. For deployment use a same-origin `/api` reverse proxy; another origin requires explicit backend CORS configuration, not supplied by this local setup.

[.env.example](.env.example) documents DATABASE_URL. Backend environment files are not automatically loaded: export the variable. `prepare_local.py` creates the ignored project `data/` directory and missing schema/content without deleting, replacing or resetting an existing database. Normal local records live in `data/wecode.sqlite3`, not `/tmp`. An existing `/tmp/wecode.sqlite3` is left untouched; there is no automatic import. SQLite files/local environment files are ignored and must not be committed. Tests use isolated temporary databases.

On this Codex desktop, bundled Node/pnpm can be added to PATH first:

```sh
export PATH="$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin:$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/bin/fallback:$PATH"
```

This fallback is specific to this installation; other machines should install Node/pnpm normally.

## Authentication and separate mock mode

Real accounts use a private password (12–128 characters). Passwords are sent only for registration/login, hashed by the server and never stored in the frontend. Use HTTPS outside localhost. The opaque bearer token and expiry are stored in this tab's `sessionStorage`, separately from mock records; reload restores the session, closing the tab ends its local credential. This storage is accessible to same-origin scripts, so it is not an XSS-resistant vault. Server tokens expire after 24 hours; logout revokes the current token and clears private UI/token state. If the backend is unreachable during logout, local state still clears, but revocation cannot be confirmed; the orphaned server token expires normally.

For development/tests only, explicitly run:

```sh
VITE_SERVICE_MODE=mock pnpm --dir frontend dev
```

Mock accounts use a made-up email and public demo passphrase `practice-only`; their browser-local records remain separate from real API accounts. No existing mock records are imported, overwritten or cleared. Real mode never falls back to mocks on failures. Mock fixtures are dynamically imported only in explicit development mode and excluded from the default production bundle. Production mock mode is rejected. Real Settings hides the mock failure-injection control.

Network/server errors are visible. Read recovery uses Retry or Refresh workspace. Writes are never automatically replayed: after an interrupted submission, confirm saved state using Refresh workspace before retrying, since the server may have committed. Repeated intentional submissions remain separate attempts but cannot duplicate Boolean completion credit. All curriculum, hints/solutions, feedback and progress in real mode come from the server, using authored rules without executing code.

## Frontend checks and browser integration

```sh
pnpm --dir frontend typecheck
pnpm --dir frontend test
pnpm --dir frontend build
pnpm --dir frontend check:bundle
pnpm --dir frontend contrast
```

The browser harness starts its own Vite/FastAPI processes and isolated temporary SQLite database; it does not touch the normal project DB or the user's browser profile:

```sh
node frontend/scripts/check-integration.cjs
```

It uses Playwright plus installed Chrome. On this desktop it discovers bundled Playwright; elsewhere set `PLAYWRIGHT_MODULE` to an installed Playwright package, `CHROME_BIN` to Chrome/Chromium, and `BACKEND_PYTHON` to the installed backend environment Python. Playwright is verification tooling, not an application runtime dependency. The harness covers real UI/network flows, backend process restart with the same DB, outage/recovery, account isolation, expiry/invalid credentials and desktop/320px mobile. It writes screenshots and redacted method/path/status evidence to `/tmp/wecode-integration-evidence` (or `BROWSER_ARTIFACT_DIR`), prints no passwords/tokens and cleans only its own temporary DB/processes.

## API contract validation

The [API mapping](docs/api-mapping.md) covers all service methods and explicitly documents real authentication differences from mock accounts. To validate the root agreement (with Node on PATH):

```sh
python3 -m venv /tmp/wecode-openapi-venv
/tmp/wecode-openapi-venv/bin/python -m pip install -r tools/contract/requirements.txt
/tmp/wecode-openapi-venv/bin/openapi-spec-validator openapi.yml
/tmp/wecode-openapi-venv/bin/python tools/contract/validate.py
```

Validation tooling is isolated from application/backend dependencies. The custom check also reads the existing frontend TypeScript AST, resolves references and checks examples/coverage. See the mapping for prerequisites and limitations.

## Learning behavior

Nine units and 27 exercises cover Python, SQL and Git at all three levels. Mark a lesson read and correctly submit all three exercises to complete its unit. Assisted work counts toward completion and remains separate from independent solving. No XP/scoring is added. Checking uses authored fragments, not arbitrary execution or semantic equivalence.

## Project documents

- [Instructor versus planning requirements](docs/requirements-reconciliation.md)
- [Partial manual brainstorming transcript](docs/brainstorming-transcript.md)
- [Original assignment screenshot and comparison](docs/submission-checklist.md#actual-assignment-screenshot-comparison)
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
- [Independent SQLite persistence QA](docs/qa/sqlite.md)
- [Real integration architecture and engineer checks](docs/integration.md)
- [Independent integration and observed-bug QA](docs/qa/integration.md)
- [Submission checklist — source-aligned QA PASS](docs/submission-checklist.md)
- [Final audit results and limitations](docs/qa/final-audit.md)
- [Verified demo guide](docs/demo-guide.md)
- [PM](docs/team/pm.md), [software engineer](docs/team/software-engineer.md), [independent QA](docs/team/qa-engineer.md) role instructions
- [Historical planning/source review](docs/planning.md), [curriculum review](docs/curriculum-review.md), [mock service](docs/mock-service.md)
- [API mapping](docs/api-mapping.md), [SQLite lifecycle](docs/sqlite.md)
- [Task issue template](.github/ISSUE_TEMPLATE/task.md), [observed user-test-bug template](.github/ISSUE_TEMPLATE/user-test-bug.md)
- [Canonical GitHub backlog](https://github.com/240103097-jpg/WeCode/issues)

PM refines issues, engineer implements and tests, independent QA verifies every criterion and alone closes after PASS. Stage order: mocked frontend → root openapi.yml → in-memory backend → ORM/SQLite → integration and thorough testing. The [user-provided partial manual transcript](docs/brainstorming-transcript.md) is preserved with explicit gaps; the separate summary is not verbatim and the copy is not an automated export. The instructor does not demand an entire archive; see the [explicit PM reconciliation](docs/requirements-reconciliation.md).

## SQLite backend

The complete-app commands above use the persistent ignored project directory.

Python 3.13, SQLAlchemy 2.0.44 and SQLite were verified. From the repository root:

```sh
python3 -m venv /tmp/wecode-backend-venv
/tmp/wecode-backend-venv/bin/python -m pip install -r backend/requirements-dev.txt
export DATABASE_URL="sqlite:///$PWD/data/wecode.sqlite3"
/tmp/wecode-backend-venv/bin/python backend/scripts/init_db.py
/tmp/wecode-backend-venv/bin/python -m uvicorn backend.wecode.app:create_app --factory --host 127.0.0.1 --port 8000 --workers 1 --no-access-log
```

Use another shell for tests while the server runs. Runtime-only installs can use `backend/requirements.txt`. The secret-free [.env.example](.env.example) shows DATABASE_URL; export it explicitly (no automatic dotenv loading). Choose an existing parent directory; four slashes indicate an absolute SQLite file path. Missing DATABASE_URL fails startup rather than silently using temporary memory. Local DB/environment files are ignored by Git. Only file-backed SQLite is supported/tested; no other database compatibility is claimed.

API base: http://127.0.0.1:8000/api/v1. [Interactive API docs](http://127.0.0.1:8000/docs); root agreement at http://127.0.0.1:8000/openapi.json. Use HTTPS outside localhost. Real frontend mode connects through the service adapter; mock mode remains explicit development-only. Real registration needs a private 12–128 character password; the public mock passphrase grants no special access.

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

Existing API behaviors run against both MemoryStorage and isolated temporary SQLite files, validating response status/headers/schemas against root OpenAPI. Additional checks cover durable state, constraints, cross-adapter concurrency, initialization/drift, rollback, ownership, expiry/revocation and process restart. One upstream Starlette/AnyIO TestClient deprecation warning is emitted; it does not affect results. No learner code executes. The real frontend client is implemented; final technical audit results and missing-material blockers are recorded separately.

Final full-curriculum browser audit: `WECODE_AUDIT_ALL_UNITS=1 node frontend/scripts/check-integration.cjs` (with BACKEND_PYTHON pointing to the installed backend environment if needed). This covers all9 units/all27 exercises and independently authored desktop/mobile progress-row non-overlap checks; normal default harness retains the shorter integration demonstration. See docs/qa/final-audit.md for actual runs and limitations.
