# Frontend service → API agreement

Contract authored October 19, 2026; implementation status updated during the in-memory stage. [Root openapi.yml](../openapi.yml) is the versioned agreement now implemented by the in-memory FastAPI backend (see README setup and backend QA evidence). No SQLite, real frontend API client or UI/authentication changes are implemented. The current application still uses its existing browser-local mockService.

The PM-refined task is [issue #11](https://github.com/240103097-jpg/WeCode/issues/11). Protocol defaults below are explicit engineering choices needed to describe real HTTP/authentication; they are not claims about the original brainstorming conversation.

## Coverage against actual consumers

All paths below are relative to `/api/v1`. Every operation has `x-frontend-service` metadata checked against the actual TypeScript interface, mock implementation and non-test consumers.

| LearningService method | API operationId | HTTP operation | Existing consumer and result mapping |
| --- | --- | --- | --- |
| `session()` | `session` | `GET /me` | App startup: 200 Learner; future adapter maps 401 to null and clears its credential. Other errors remain recoverable errors. |
| `register({name,email})` | `register` | `POST /auth/register` | Auth: 201 AuthSession; future adapter retains credential and returns `learner`. **Real request also requires a private password**, absent from today's mock registration interface/UI. |
| `login({email,passphrase})` | `login` | `POST /auth/login` | Auth: 200 AuthSession. Real wire field is `password`, not the fixed mock passphrase. Collecting genuine credentials requires an explicitly authorized later integration change; do not silently send `practice-only`. |
| `logout()` | `logout` | `DELETE /auth/session` | App Sign out: revoke current token, 204 → void. Future adapter clears its credential; 401 also means locally signed out. No learner history is deleted. |
| `snapshot()` | `snapshot` | `GET /me/snapshot` | App initial load and refresh after writes. Exact Snapshot shape: learner, all public units, own progress map, own complete attempt history. Dashboard, paths, practice index, workspace, progress and settings read these values. |
| `preferences({track,level,onboarded?})` | `preferences` | `PATCH /me/preferences` | TrackPreferences onboarding/edits and App track buttons. 204 → void, then refresh. One track level/active track changes; all other levels/history remain. False/omitted onboarded does not undo onboarding. |
| `profile({name})` | `profile` | `PATCH /me` | Settings display-name form: 204 → void, then refresh. No email/ID/history update. |
| `markRead(unitId)` | `markRead` | `PUT /me/units/{unitId}/lesson-read` | Workspace: unit ID becomes path parameter; future adapter supplies constant JSON `{read:true}`. 204 → void. Idempotent read flag, no un-read operation. |
| `submit({unitId,exerciseId,answer})` | `submit` | `POST /me/units/{unitId}/exercises/{exerciseId}/submissions` | Workspace: IDs are path parameters; body contains answer only. 201 Feedback `{correct,text,assisted}`. Wrong answers are saved successful HTTP requests with correct=false, not validation errors. |
| `hint({unitId,exerciseId})` | `hint` | `POST /me/units/{unitId}/exercises/{exerciseId}/hints` | Workspace Get a hint: no body; 200 JSON **string**, matching the current return type. A previous wrong attempt on the same exercise by this learner is required; 409 otherwise. |
| `solution({unitId,exerciseId})` | `solution` | `PUT /me/units/{unitId}/exercises/{exerciseId}/solution-reveal` | Separate Workspace Show Solution: no body; 200 `{answer,explanation}` after recording revealed=true. Idempotent state transition; not a submission. |
| `simulateFailure()` | None | **No endpoint** | Settings demonstration control sets a one-call mock-only failure. Never expose a production failure-injection API. |

Thus **12 methods = 11 backend-facing methods/HTTP operations + 1 mock-only method**, across 10 paths (`/me` has GET and PATCH). No standalone curriculum/lesson/progress/attempt-list endpoint is needed by today's consumers: `snapshot()` already reads all of them. Frontend `#unit/...` is a local view selection from `snapshot.units`, not a missing backend GET. No curriculum editing endpoints are added.

## Authentication and authorization

Contract default: real registration/login require a private password (12–128 characters, no password trimming), with server-side adaptive hashing and no plaintext persistence/logging/echo. The public mock passphrase has **no universal/special credential status**. Name/email-only signup plus a shared public passphrase cannot implement real authentication safely; the current frontend remains deliberately mocked until later authorization to add credential input and update its integration boundary. The contract makes this mismatch visible rather than pretending a drop-in real client exists.

Successful auth returns a Learner plus opaque access token, tokenType=Bearer and expiresAt. The server issues a cryptographically random credential with at least 256 bits of entropy, expires it after 24 hours, and revokes the current token on logout. No refresh, reset, email verification or administrator feature is added. HTTPS is required outside local development. These contract defaults are implemented in the in-memory backend; the frontend remains mocked.

Only register/login are anonymous (`security: []`). Every `/me` operation and logout inherit bearer authentication. The server validates the credential and derives the account identity from that session. There are no private-user-ID path/query parameters. Request objects reject unknown fields such as userId, learner.id, correct, assisted or progress; no caller can nominate another learner or award credit. Unit/exercise path IDs select authored content only, and an exercise must belong to its parent unit; unknown/mismatched IDs return 404. A learner ID is output metadata, not an accepted private selector. A failed/missing/expired/revoked credential returns 401, and does not mutate private learning state.

The frontend's `session(): Learner|null` is an adapter convention: `GET /me` returns a Learner or HTTP 401, never anonymous private data. Only session lookup converts 401 to null; other calls must surface sign-in-required. Repeating logout after revocation may return 401 and still leaves the client locally signed out. No cross-user access endpoint exists, so this contract does not invent a separate 403/user lookup API.

## Data and authoring boundaries

The public response shapes exactly retain the interface fields for Learner, Unit, Attempt, ExerciseProgress, UnitProgress, Snapshot and Feedback. Exercise is a closed Quiz/Text union matching current optional options/code usage. Track and Level enums match the actual frontend constants. Snapshot always includes the nine track/level units with three exercise types each, all in English and available without locks.

Unit contains lesson paragraphs, instructional example and takeaway, plus public exercise IDs/type/prompts and quiz options or starting code. Closed object schemas exclude accepted/rejected variants, answerRules, correct-option IDs, hint metadata, authored solutions and hidden explanations. No ordinary snapshot/curriculum response is enriched with those secrets after a reveal. General lesson examples may teach the same concept; they are not an answer-key export. Learners' own submitted answers and feedback in private attempt history are intentionally visible. Only the explicit solution operation returns authored `{answer,explanation}`; hints return a pedagogical string after their gate.

All backend answer checking is server-side against authored rules. The client sends only answer text/option ID, never correctness/assistance/credit. No learner code is executed, no AI tutor is invoked and no general semantic-equivalence claim is made.

## Exact current learning rules

- Input normalization: CRLF → LF, then surrounding whitespace trimmed; other internal whitespace, case and punctuation are unchanged. Accepted SQL casing variants remain authored variants, not a global SQL normalizer. Future adapter normalizes before the wire; server repeats it authoritatively. Wire answer max is 4,000 characters; normalized answers must be nonblank and 1–4,000. The current text input already caps at 4,000, and the mock service's limit is on normalized text; trimming before serialization preserves valid mock-boundary results even when a non-UI caller adds outer padding. Name/email are trimmed, email lowercased before serialization, then validated/normalized again server-side.
- Quiz submission uses stable option ID strings. A nonblank unknown option ID is an incorrect saved answer, as in mockService; malformed request/blank answer is 422 without a new attempt.
- Every valid submission POST records one attempt and returns feedback, including incorrect answers. Retrying wrong work is unrestricted. A transport retry can append another attempt; the contract does **not** claim attempt-request deduplication/idempotency keys. Attempts and completion credit are different.
- Correct-ever and independent-ever flags are monotonic. A correct submission sets correct. It sets independent only if no prior solution reveal; later wrong answers cannot clear either flag. Independent implies correct. A later reveal preserves an earlier independent solve but is still displayed as viewed. The attempt's assisted Boolean records reveal state at that attempt's check time.
- A successful hint requires any earlier wrong submission on this learner/exercise, even if there was a later correct submission. It increments hintCount, including repeated hint requests. Hints do not set the solution-assisted flag or award credit.
- Solution reveal sets revealed=true, with no prerequisite wrong answer; repeats are idempotent. It does not set correct or create an attempt. Correct work after reveal can complete the unit but is not a new independent solve.
- Lesson read sets read=true idempotently. Unit completion is derived once as read AND the three exercises' correct-ever flags. Assisted correct work counts. Repeated read, correct submission or reveal cannot add duplicate completed units. No separate numeric credit counter, XP or score exists.
- Snapshot progress omits untouched entries (interpreted as false flags/zero hints). Overall completed units/9, each track completed units/3, independent exercises/27, and current unit checklist steps/4 are derived exactly as existing consumers do. There is no extra server-scoring formula.
- Switching tracks/editing levels changes only preferences, never historic unit state or attempts. Snapshot returns **all** current learner attempts, oldest-first in stable commit order, including ties in timestamps. The existing progress view uses total length and displays the last ten in reverse order; silently paginating/truncating would change its behavior. No new pagination feature is introduced here.
- Writes and submit/reveal ordering are atomic/serialized for each learner. The server saves before success and returns coherent snapshots. Assistance is determined at submission time, not by a racing client flag. Validation/auth/locked-hint failures do not alter attempts or progress.

## Error/transport mapping

All error bodies use `{error:{code,message}}`, with safe English text. The future adapter can construct a ServiceError-like error so existing consumers continue reading `error.message`. No stack trace, token/password, private data or answer key is exposed. Responses use Cache-Control: no-store. Protected 401 responses include WWW-Authenticate: Bearer.

| HTTP | Code | Meaning |
| --- | --- | --- |
| 400 | validation | Malformed JSON |
| 415 | validation | Wrong request Content-Type |
| 422 | validation | Missing/extra/invalid fields, enum, path format or invalid answer |
| 401 | credentials | Login email/password mismatch, same message for unknown email |
| 401 | unauthorized | Missing/invalid/expired/revoked session |
| 404 | not-found | Unknown unit/exercise or mismatched parent |
| 409 | duplicate | Normalized email already registered |
| 409 | hint-locked | No previous incorrect attempt for this learner/exercise |
| 500 | internal | Generic server failure; no storage internals exposed |
| 503 | unavailable | Temporary service failure; retry is appropriate |

Browser-local storage errors, shared demo passphrase, local session IDs, frontend delay and failure injection are mock-only. There is no real API `storage` error code or failure switch. A network failure has no HTTP body; the future adapter will report a recoverable transport error and must not invent success. A committed submission whose response is lost may be retried as a second attempt, but never as duplicate completion credit. No automatic retry middleware is implemented here.

## Validation

Contract-only dependencies are isolated in [tools/contract/requirements.txt](../tools/contract/requirements.txt); these are not backend dependencies. Existing frontend TypeScript is used for **AST inspection**, not to run application or learner code. On a clean checkout install the existing frozen frontend dependencies first if absent: `pnpm --dir frontend install --frozen-lockfile`. Use the bundled Node/pnpm PATH from [README](../README.md) on this desktop.

From the repository root:

```sh
python3 -m venv /tmp/wecode-openapi-venv
/tmp/wecode-openapi-venv/bin/python -m pip install -r tools/contract/requirements.txt
/tmp/wecode-openapi-venv/bin/openapi-spec-validator openapi.yml
/tmp/wecode-openapi-venv/bin/python tools/contract/validate.py
```

Node must be on PATH, or set `NODE_BIN` to its executable. The custom check invokes the pinned OpenAPI validator, resolves every local reference, rejects duplicate YAML keys, checks schema/media/parameter/header examples with format validation, compares method/input/output fields and enums to the frontend AST, checks actual non-test consumers and mock methods, validates the real nine-unit/27-exercise data, reviews secret-field exclusion and example completion semantics, and runs negative checks for key leakage, impersonation fields and invalid payload/state/format. References to external files/URLs are intentionally disallowed to keep this root agreement self-contained.

Primary tooling references: [OpenAPI 3.0.3 specification](https://spec.openapis.org/oas/v3.0.3.html), [openapi-spec-validator](https://openapi-spec-validator.readthedocs.io/en/latest/), [JSON Schema validation](https://python-jsonschema.readthedocs.io/en/stable/validate/). Schema validation establishes shape/format and examples, not runtime password security, transaction ordering or authored answer correctness; independent QA must also review those semantics against the frontend/product rules. Runtime API conformance tests now live in backend/tests; persistent storage and real frontend integration remain later stages.
