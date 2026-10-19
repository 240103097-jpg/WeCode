# WeCode

An English learning workspace for Python, SQL and Git. Individual academic project due October 20, 2026 (Asia/Almaty); exact submission time unknown.

## Current stage

Interactive frontend with a centralized typed mockService. React, TypeScript and Vite are selected; Python/FastAPI, SQLAlchemy and SQLite are selected for later stages. No backend, OpenAPI contract or database is implemented in this stage.

## Local development

With Node.js 22.12+ and pnpm 11.25+ installed:

```sh
cd frontend
pnpm install
pnpm dev
```

Preview: http://127.0.0.1:5173 (use the actual URL printed by Vite if occupied).

```sh
pnpm typecheck
pnpm test
pnpm build
```

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
- [Canonical GitHub backlog](https://github.com/240103097-jpg/WeCode/issues)

PM refines issues, engineer implements and tests, independent QA verifies every criterion and alone closes after PASS. Stage order: mocked frontend → root openapi.yml → in-memory backend → ORM/SQLite → integration and thorough testing. The full original planning transcript is still needed; the summary is not a verbatim export.
