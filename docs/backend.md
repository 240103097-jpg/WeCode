# In-memory backend

The independently QA-passed stage-three FastAPI server implements all 11 HTTP operations in [root OpenAPI](../openapi.yml). [The mapping](api-mapping.md) retains the frontend's service boundary and explains why real credential collection belongs to later frontend integration. [README](../README.md#in-memory-backend) has verified setup/run/test commands. No frontend networking, UI, mockService, SQLAlchemy or SQLite changes are included.

## Boundaries

- `backend/wecode/app.py`: HTTP transport, contract input checks, authentication and account-owned operations. Identity always comes from the bearer session, never a request learner ID. Closed input schemas reject extra fields. Hints/solution actions reject unexpected request bodies. Malformed JSON is 400, unsupported request media 415, field/path validation 422; errors use the contract envelope and no-store headers. A 401 includes the Bearer challenge.
- `backend/wecode/contract.py`: loads/resolves reviewed root schemas and validates without type coercion. The exact root agreement is served as `/openapi.json`, including its original contract-stage explanatory descriptions; no semantic contract change was needed. `/docs` uses this agreement.
- `backend/wecode/storage.py`: injectable transaction protocol and memory adapter. A lock serializes operations; a working copy commits only on success. Reads are coherent and returned values cannot mutate committed state. All data disappears on restart. This intentionally simple single-process adapter can be replaced under the later persistence issues; no persistence implementation is hidden here.
- `backend/wecode/curriculum.py` and `backend/data/curriculum.json`: existing authored content loaded locally, with public units separate from private rules. The export script parses JSON literals without executing TypeScript. Normal snapshots never include rules/hints/solutions, including after reveal. Own answers and feedback remain intentional private history.
- `backend/tests`: every API test response is checked for documented status, headers and schema. Semantic tests cover all 27 exercises, normalization, histories, assistance, completion, isolation and concurrent/failed transactions. `backend/scripts/smoke.py` checks real HTTP responses against the same agreement and exercises every operation.

## Authentication and learning state

Registration/login use salted Argon2id hashes and normal private passwords. Unknown-email login verifies a dummy hash and returns the same generic credentials error as an incorrect password. Each new session receives 32 cryptographically random bytes encoded as an opaque bearer token; the registry stores its SHA-256 digest, account ID and 24-hour expiry. Logout revokes only the presented session. No token/password is logged, written to disk or returned in errors; tokens intentionally appear only in successful auth issuance. Use HTTPS outside localhost. No password reset, refresh, email verification or admin API is added.

Submissions are compared to exact authored variants after CRLF normalization and trim; learner code is never executed. Each valid POST saves a distinct attempt even on retry; wrong answers are successful submissions. Read/correct/independent/revealed flags are historical Boolean facts. Completion remains read plus all three correct-ever flags, so repeats cannot duplicate credit. A solution reveal sets assistance for subsequent attempts, preserves earlier independent solving and creates no attempt itself. Hints require the same learner's prior wrong attempt on that exercise and do not set assisted status. Writes are serialized so submit/reveal ordering and snapshot history agree, including identical timestamps.

No totals/XP counter is stored: frontend formulas derive completed units /9, each track /3 and independent exercises /27 from the returned progress. All levels remain accessible, and preference/profile edits retain complete oldest-first history. Failed validation, authentication, locked hints or failed commits leave learning state unchanged.

## Stage limits

Tests and real HTTP checks establish the in-memory server behavior. Restart persistence, distributed workers, a live frontend API client and UI credential changes remain separately authorized later stages. The frontend still uses browser-local mock accounts with its public passphrase; they are not imported into real backend accounts. Restarting this temporary API does not touch browser storage.

Primary implementation references inspected: [FastAPI password authentication guidance](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/) and [argon2-cffi PasswordHasher API](https://argon2-cffi.readthedocs.io/en/stable/api.html). The selected contract uses opaque revocable sessions rather than the tutorial's JWT example.

Actual criterion-by-criterion results are preserved in [independent backend QA evidence](qa/backend.md).
