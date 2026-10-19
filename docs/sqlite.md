# SQLite persistence lifecycle

The owner authorizes persistence only. The frontend/mockService, root API contract and UI remain unchanged. Issue [#15](https://github.com/240103097-jpg/WeCode/issues/15) establishes accounts/preferences/sessions; dependent [#16](https://github.com/240103097-jpg/WeCode/issues/16) completes learning/curriculum persistence and selects it at runtime.

## Account foundation gate

`backend/wecode/sql_storage.py` implements the existing State transaction boundary with SQLAlchemy ORM. Accounts have normalized unique email, hash-only passwords, profile/active track/onboarding; preferences are uniquely keyed by account/track; sessions store only token digest/account/UTC expiry. Logout deletes just the authenticated session row. The original password/token and contract rules remain unchanged.

Every transaction updates a singleton guard row before reading mutable State. SQLite's database write lock then serializes independent connections/adapters, including duplicate-account checks, commits and snapshot reads. Commit/rollback is managed by SQLAlchemy Session contexts. Constraints add unique normalized email, foreign-key ownership, valid enums and Boolean integrity. Errors are translated to the existing safe 503 without echoing SQL values. This simple whole-State adapter favors correctness for the academic scope; it is not a high-throughput design.

Python sqlite3 connection settings enable proper transactions, thread handoff and a 30-second lock wait. The only hand-written SQLite SQL is necessary `PRAGMA foreign_keys=ON` on connection; data queries and writes use ORM/SQLAlchemy expressions. Only SQLite has been tested; no other database compatibility is claimed.

## Configuration and initialization

From the repository root, install pinned backend requirements as in [README](../README.md). Export DATABASE_URL from the secret-free [.env.example](../.env.example), or choose another SQLite file path with an existing parent directory:

```sh
export DATABASE_URL=sqlite:////tmp/wecode.sqlite3
/tmp/wecode-backend-venv/bin/python backend/scripts/init_db.py
```

Four slashes indicate an absolute SQLite path. Environment files are not automatically read. No credentials are needed for a local SQLite URL. DB and local environment files are ignored, and no data is committed. Initialization creates missing tables/the singleton guard without dropping or resetting existing records. Schema evolution is not a destructive reset: this is the first schema; later changes must explicitly plan migrations. `create_all` does not migrate altered existing columns.

At the #15 gate, the runtime deliberately remains on MemoryStorage until the full #16 adapter is ready. Learning writes on the partial SQL adapter fail safely instead of disappearing. Isolated temporary SQLite tests cover account/preferences/session reopen, expiry/revocation, constraints, rollback, duplicate registration across independent adapters and user isolation. The original in-memory regression suite remains available. Full curriculum and learning persistence evidence follows only after the dependent implementation/QA gate.

Primary references inspected: [SQLAlchemy Session transactions](https://docs.sqlalchemy.org/en/20/orm/session_basics.html) and [SQLite dialect/connection behavior](https://docs.sqlalchemy.org/en/20/dialects/sqlite.html). No API contract change is needed.
