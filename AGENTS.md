# Agent instructions

Read [the specification](WeCode_Project_Specification.md), [process](docs/process.md) and the current GitHub issue before working. Inspect the checkout, Git status, nested AGENTS.md files and remote state each session; never assume another session's files or commits exist. Preserve unrelated work. Never force-push or overwrite remote changes.

Current stage: owner-authorized in-memory FastAPI backend only (issues #12–14 independently QA-passed and closed). Stop at this stage; later implementation requires separate owner authorization. Preserve the root OpenAPI contract and entire frontend/mockService. No SQLAlchemy/SQLite, real frontend API client, integration or UI changes. Use the verified backend setup/run/test commands in README.md. Storage is process-local and data is lost on restart; run one worker. See docs/decisions.md for product rules.

Use [GitHub Issues](https://github.com/240103097-jpg/WeCode/issues) as the only active backlog. Read [task template](docs/task-template.md). Search all existing issues before creating tasks. Labels: `mvp`, `post-mvp`, `user-test-bug`; the last is only for observed defects.

Follow assignment order: interactive frontend + centralized `mockService`; root `openapi.yml`; in-memory backend; ORM + SQLite; integration + thorough tests. Never silently adopt the articles' earlier integration order or orchestrator closure rule. Only independent QA closes an issue after PASS. Engineer and PM leave it open; avoid automatic closing keywords in commits/PRs.

Roles are Markdown instructions, not executable programs: [PM](docs/team/pm.md), [engineer](docs/team/software-engineer.md), [QA](docs/team/qa-engineer.md). Use an independent reviewer/session for QA; the implementing agent cannot certify its own work.

Before UI work read [design guidance](docs/design-system.md); before tests read [testing guidelines](docs/testing-guidelines.md). All application UI and educational content must be English. Use authored answer rules, never execute arbitrary learner code. Do not add an AI tutor to MVP. Use the owner-confirmed 9-unit/27-exercise target and completion rules in docs/decisions.md; do not add XP or scoring.

Documentation checks: check relative Markdown links and run `git diff --check`. Use verified commands in README.md as they are added; do not report unrun tests as passed. Commit with the actual current timestamp; do not backdate. Push only after fetching and preserving remote changes.

Backend commands from repository root (Python 3.13 verified): create `/tmp/wecode-backend-venv` with `python3 -m venv /tmp/wecode-backend-venv`; install with `/tmp/wecode-backend-venv/bin/python -m pip install -r backend/requirements-dev.txt`; run `/tmp/wecode-backend-venv/bin/python -m uvicorn backend.wecode.app:app --host 127.0.0.1 --port 8000 --workers 1 --no-access-log`. Test with `/tmp/wecode-backend-venv/bin/python -m pytest backend/tests -q`; check exact content with `python3 backend/scripts/sync_curriculum.py`; with the server running, execute `/tmp/wecode-backend-venv/bin/python backend/scripts/smoke.py`. Also run root contract validation and existing relevant frontend checks as documented. Do not regenerate content, clear learner data or connect the frontend in this stage.
