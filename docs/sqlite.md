# SQLite persistence lifecycle

This document records the completed persistence stage; integration #17 now connects the real frontend service while preserving design and product rules. Issue [#15](https://github.com/240103097-jpg/WeCode/issues/15) establishes accounts/preferences/sessions; dependent [#16](https://github.com/240103097-jpg/WeCode/issues/16) completes learning/curriculum persistence and selects it at runtime.

## Persisted entities

`backend/wecode/sql_storage.py` implements the existing State transaction boundary with SQLAlchemy ORM. Accounts have normalized unique email, hash-only passwords, profile/active track/onboarding; preferences are uniquely keyed by account/track; sessions store only token digest/account/UTC expiry. Logout deletes just the authenticated session row. The original password/token and contract rules remain unchanged.

Every transaction updates a singleton guard row before reading mutable State. SQLite's database write lock then serializes independent connections/adapters, including duplicate-account checks, commits and snapshot reads. Commit/rollback is managed by SQLAlchemy Session contexts. Constraints add unique normalized email, foreign-key ownership, valid enums and Boolean integrity. Errors are translated to the existing safe 503 without echoing SQL values. This simple whole-State adapter favors correctness for the academic scope; it is not a high-throughput design.

Python sqlite3 connection settings enable proper transactions, thread handoff and a 30-second lock wait. The only hand-written SQLite SQL is necessary `PRAGMA foreign_keys=ON` on connection; data queries and writes use ORM/SQLAlchemy expressions. Only SQLite has been tested; no other database compatibility is claimed.

## Configuration and initialization

From the repository root, install pinned backend requirements as in [README](../README.md). Export DATABASE_URL from the secret-free [.env.example](../.env.example), or choose another SQLite file path with an existing parent directory:

```sh
mkdir -p data
export DATABASE_URL="sqlite:///$PWD/data/wecode.sqlite3"
/tmp/wecode-backend-venv/bin/python backend/scripts/init_db.py
```

Four slashes indicate an absolute SQLite path. Environment files are not automatically read. No credentials are needed for a local SQLite URL. DB and local environment files are ignored, and no data is committed. Initialization creates missing tables/the singleton guard without dropping or resetting existing records. Schema evolution is not a destructive reset: this is the first schema; later changes must explicitly plan migrations. `create_all` does not migrate altered existing columns.

The #15 foundation passed independent QA before #16 began. The completed default runtime uses SQLStorage; MemoryStorage is an explicit test adapter. Default app creation is a factory, so importing backend modules does not open a real learner DB during tests.

Curriculum units store public lesson payloads with unique track/level and position. Exercise rows hold public prompt fields separately from private authored rules, with parent/position uniqueness. Initialization inserts missing stable IDs and rejects conflicts or unexpected inventory instead of overwriting content/history. Ordinary API curriculum remains secret-free.

Lesson state is uniquely keyed by account/unit. Exercise state is uniquely keyed by account/unit/exercise, with composite foreign keys enforcing the authored parent and learner lesson row, nonnegative hint counts and independent-implies-correct constraints. Attempt UUIDs and account/sequence uniqueness preserve full commit order, including timestamp ties. Correct, independent, reveal and read are Boolean historical facts; no completion counter can accumulate duplicate credit. Retries append attempts, while progress retains the documented historical flags. SQLite stores UTC timestamps without timezone decoration and the adapter restores UTC on output.

The unchanged State storage boundary reconstructs all accounts/preferences/sessions/progress/attempts inside the serialized DB transaction. Only logout removes its session row; profile/track edits never clear learning history. SQL failures and failed writes roll back the whole operation. SQL echo is disabled, parameter values hidden, errors generic. The adapter reads whole State per transaction and favors correctness over scalability; use the documented one-worker setup. Independent adapters/connections are tested for concurrent requests, without claiming distributed-database scalability.

## Verification and restart

Run the full backend suite against temporary SQLite and memory regression variants using the README command. SQL-specific tests check reopen persistence of every learning field, 9/27 repeated initialization, cross-user ownership, two-adapter concurrent writes, sequence/parent/progress constraints and rollback after flushed learning writes. The root contract and frontend files remain unchanged.

`backend/scripts/check_restart.py` starts three distinct real Uvicorn processes, stopping each fully and reusing one isolated DB. It creates accounts, updates profile/all track levels, reads a lesson, submits wrong/correct/retry answers, requests hints and reveals one solution. It saves the expected snapshot in process memory, restarts the backend, logs in again and checks the exact snapshot, live/revoked/expired sessions and another user's empty history. One test expiry timestamp is moved into the past via ORM while stopped; this does not claim a literal 24-hour elapsed wait. Repeated startup retains 9 units, 27 exercises and nine attempts. Credentials are never printed or written to files; the temporary DB is deleted after checks.

No browser-local mock records are migrated or touched, and mock data is never automatically imported by integration. Persistence and API tests do not claim final UI/API/database integration verification.

Primary references inspected: [SQLAlchemy Session transactions](https://docs.sqlalchemy.org/en/20/orm/session_basics.html) and [SQLite dialect/connection behavior](https://docs.sqlalchemy.org/en/20/dialects/sqlite.html). No API contract change is needed.

Full criterion evidence and reviewed revisions are recorded in [independent SQLite QA](qa/sqlite.md). Both issues are closed by QA after PASS.
