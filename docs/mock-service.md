# Frontend service boundary

The `LearningService` interface in frontend/src/services/types.ts is the single asynchronous data/auth boundary. Components receive the interface; they do not import answer keys, storage APIs or a real network client. `mockService.ts` implements it with browser-local persistence. Explicit development mock mode runs without a backend; the complete app defaults to the real API adapter described in api-mapping.md.

## Mock operations (frontend-stage record)

| Operation | Input | Result / behavior |
| --- | --- | --- |
| session | None | Current local learner or null |
| register | display name, demo email | Creates local account and session |
| login | demo email, public demo passphrase | Opens local session |
| logout | None | Clears active session |
| snapshot | None | Learner, public units, private mock progress/attempts |
| preferences | track, level, optional onboarding completion | Updates independent per-track choice |
| profile | display name | Updates display name |
| markRead | unit ID | Idempotent lesson read flag |
| submit | unit/exercise IDs, answer | Authored feedback and stored attempt |
| hint | unit/exercise IDs | Hint after an incorrect attempt, recorded request |
| solution | unit/exercise IDs | Explicit authored solution/explanation, recorded reveal |
| simulateFailure | None | Mock-only next-call failure, not a future production endpoint |

Failures are typed ServiceError codes: validation, duplicate, credentials, unauthorized, not-found, hint-locked, unavailable and storage. The contract-stage endpoint/security decisions and real-vs-mock differences are now recorded in docs/api-mapping.md and root openapi.yml. The mock remains unchanged; this document is not a backend implementation. The frontend's public fixed passphrase must never become production authentication.

## Record and checking semantics

Accounts store a learner profile, unit progress and append-only attempt list. Each exercise tracks correct-ever, independently-correct-ever, revealed-ever and hint count. Completing a unit is computed from its read flag and three correct-ever flags; retries never add completion units. A solution reveal is tracked even without a later submission. An attempt records its own assistance status at submission time.

Mock answer rules are authored in curriculum data; ordinary Unit responses omit keys, hints and solution metadata. Text checking trims outer whitespace and normalizes CRLF only. No eval, Function constructor, interpreter or execution API handles learner input. Since this is a local frontend demo, bundled keys and local records are inspectable; no secure isolation or anti-cheat claim is made.

The service adapter owns localStorage access, errors and serialization. Existing damaged data is not silently replaced. Settings offers an explicit next-call failure simulation for recoverable error verification. Production storage/server authorization are now implemented in the separate backend/API adapter; this document describes only the retained development mock.
