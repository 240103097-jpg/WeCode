# Agent instructions

Read [the specification](WeCode_Project_Specification.md), [process](docs/process.md) and the current GitHub issue before working. Inspect the checkout, Git status, nested AGENTS.md files and remote state each session; never assume another session's files or commits exist. Preserve unrelated work. Never force-push or overwrite remote changes.

Current stage: planning only. Do not scaffold application code, install application dependencies or create `openapi.yml` yet. Stack choices remain proposed until the owner selects them. Future implementation requires a separate instruction and a PM-refined issue.

Use [GitHub Issues](https://github.com/240103097-jpg/WeCode/issues) as the only active backlog. Read [task template](docs/task-template.md). Search all existing issues before creating tasks. Labels: `mvp`, `post-mvp`, `user-test-bug`; the last is only for observed defects.

Follow assignment order: interactive frontend + centralized `mockService`; root `openapi.yml`; in-memory backend; ORM + SQLite; integration + thorough tests. Never silently adopt the articles' earlier integration order or orchestrator closure rule. Only independent QA closes an issue after PASS. Engineer and PM leave it open; avoid automatic closing keywords in commits/PRs.

Roles are Markdown instructions, not executable programs: [PM](docs/team/pm.md), [engineer](docs/team/software-engineer.md), [QA](docs/team/qa-engineer.md). Use an independent reviewer/session for QA; the implementing agent cannot certify its own work.

Before UI work read [design guidance](docs/design-system.md); before tests read [testing guidelines](docs/testing-guidelines.md). All application UI and educational content must be English. Use authored answer rules, never execute arbitrary learner code. Do not add an AI tutor to MVP. Do not promote proposed content counts or progress/scoring rules into requirements.

Documentation checks: check relative Markdown links and run `git diff --check`. No application test commands exist yet; do not report unrun tests as passed. Commit with the actual current timestamp; do not backdate. Push only after fetching and preserving remote changes.
