# Agent instructions

Read [the specification](WeCode_Project_Specification.md), [process](docs/process.md) and the current GitHub issue before working. Inspect the checkout, Git status, nested AGENTS.md files and remote state each session; never assume another session's files or commits exist. Preserve unrelated work. Never force-push or overwrite remote changes.

Current stage: owner-authorized frontend/backend integration only (#17). Preserve retro design/product rules and existing mock records. Real API is default; mock mode is explicit dev/test only, never a fallback. Use project data/wecode.sqlite3 for normal local SQLite, temporary DBs only for tests. DATABASE_URL and VITE_API_BASE_URL configure services; keep DB access behind Storage. Independent QA must verify actual browser/network/restart/offline/mobile flows. Do not claim final submission audit #18 complete.

Use [GitHub Issues](https://github.com/240103097-jpg/WeCode/issues) as the only active backlog. Read [task template](docs/task-template.md). Search all existing issues before creating tasks. Labels: `mvp`, `post-mvp`, `user-test-bug`; the last is only for observed defects.

Follow assignment order: interactive frontend + centralized `mockService`; root `openapi.yml`; in-memory backend; ORM + SQLite; integration + thorough tests. Never silently adopt the articles' earlier integration order or orchestrator closure rule. Only independent QA closes an issue after PASS. Engineer and PM leave it open; avoid automatic closing keywords in commits/PRs.

Roles are Markdown instructions, not executable programs: [PM](docs/team/pm.md), [engineer](docs/team/software-engineer.md), [QA](docs/team/qa-engineer.md). Use an independent reviewer/session for QA; the implementing agent cannot certify its own work.

Before UI work read [design guidance](docs/design-system.md); before tests read [testing guidelines](docs/testing-guidelines.md). All application UI and educational content must be English. Use authored answer rules, never execute arbitrary learner code. Do not add an AI tutor to MVP. Use the owner-confirmed 9-unit/27-exercise target and completion rules in docs/decisions.md; do not add XP or scoring.

Documentation checks: check relative Markdown links and run `git diff --check`. Use verified commands in README.md as they are added; do not report unrun tests as passed. Commit with the actual current timestamp; do not backdate. Push only after fetching and preserving remote changes.

Backend commands from repository root (Python 3.13 verified): create `/tmp/wecode-backend-venv` with `python3 -m venv /tmp/wecode-backend-venv`; install with `/tmp/wecode-backend-venv/bin/python -m pip install -r backend/requirements-dev.txt`; export `DATABASE_URL="sqlite:///$PWD/data/wecode.sqlite3"`, initialize with `/tmp/wecode-backend-venv/bin/python backend/scripts/init_db.py`, then run `/tmp/wecode-backend-venv/bin/python -m uvicorn backend.wecode.app:create_app --factory --host 127.0.0.1 --port 8000 --workers 1 --no-access-log`. Test with `/tmp/wecode-backend-venv/bin/python -m pytest backend/tests -q`; check exact content with `python3 backend/scripts/sync_curriculum.py`; with the server running, execute `/tmp/wecode-backend-venv/bin/python backend/scripts/smoke.py`. Also run root contract validation and existing relevant frontend checks as documented. Do not regenerate curriculum or clear learner/mock data. Follow README complete-app commands.

Persistence verification additionally runs `/tmp/wecode-backend-venv/bin/python backend/scripts/check_restart.py` (three real processes, isolated temporary SQLite database). API test fixtures run both memory regression and temporary SQLite variants; never point tests at real learner databases. Default runtime requires DATABASE_URL and uses SQLStorage. Only SQLite is verified; do not claim another database works.

Integration #17 and observed bugs #21/#22 passed independent QA at 45574230a5c82b13a859454226fd3887561db401 and are closed. Preserve this stage boundary; final submission audit #18 requires the next owner instruction. Evidence: docs/qa/integration.md.
