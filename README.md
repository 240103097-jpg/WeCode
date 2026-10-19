# WeCode

Individual academic project for learning Python, SQL and Git through short English lessons and practice. Submission target: **October 20, 2026, Asia/Almaty**; exact time is unknown.

## Status

Repository setup and planning only. No application, dependency installation or runnable test suite exists yet. React/TypeScript, Python/FastAPI, SQLAlchemy and SQLite are **proposed**, not selected.

Confirmed scope: registration/login, an editable Beginner/Intermediate/Advanced level per track, lessons, Quiz, Fix the Bug, Complete the Code, explanatory feedback, retries, hints, a separate Show Solution button, saved attempts and progress. Checking uses authored rules. Arbitrary learner code execution and an AI tutor are post-MVP.

## Read first

- [Project specification and brainstorming summary](WeCode_Project_Specification.md)
- [Agent instructions](AGENTS.md)
- [Development process](docs/process.md)
- [Task template](docs/task-template.md)
- [Testing guidelines](docs/testing-guidelines.md)
- [Design planning](docs/design-system.md)
- [Planning decisions and source review](docs/planning.md)
- [Canonical active backlog: GitHub Issues](https://github.com/240103097-jpg/WeCode/issues)

Content counts, scoring, completion, assisted progress, normalization and design require decisions before dependent implementation. The full original planning transcript still needs to be supplied; the preserved summary is not a verbatim export.

## Required development order

1. Interactive frontend with a centralized `mockService`.
2. Root `openapi.yml` API contract derived from the frontend service boundary.
3. Backend implementing the contract with in-memory storage.
4. SQLite persistence through an ORM.
5. Connect frontend and backend, then thoroughly test.

Each stage must pass QA before the next stage begins. The assignment takes precedence over the articles. The root API contract will remain versioned. Future implementation issues must add verified setup/run/test commands here when those commands exist.
