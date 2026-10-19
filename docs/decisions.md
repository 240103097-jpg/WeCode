# Frontend decisions — October 19, 2026

## Owner decisions

WeCode uses English UI and curriculum, a dark theme with yellow/green accents, and React + TypeScript + Vite. Python/FastAPI now uses SQLAlchemy/SQLite in the owner-authorized persistence stage. Detailed visual design is delegated to the agent.

Initial delivery: one short unit per Python/SQL/Git × Beginner/Intermediate/Advanced combination: 9 units, each with a lesson, Quiz, Fix the Bug and Complete the Code (27 exercises).

A unit completes after marking its lesson read and submitting correct answers to all three exercises. Solution reveals are recorded as assistance. Assisted work counts toward completion but never independent mastery. Retries cannot duplicate completion credit. No XP or scoring. Hints become available after an incorrect answer. Show Solution remains a separate explicit action. Authored rules check answers; no learner code runs.

## Delegated implementation defaults

These are agent-selected defaults under the owner's instruction to resolve product rules, not claims about the original brainstorming decisions.

- Each track starts at Beginner; onboarding explicitly selects the active track and its level. Editing one level leaves other choices and all unit history intact. All levels remain accessible.
- Unit completion is Boolean; selected-track progress is completed units / 3, overall progress is completed units / 9. Workspace also shows checklist steps / 4 (lesson + three correct answers), labeled steps rather than completion percentage.
- Each exercise stores whether any solution was revealed, all submissions and hint requests. Hint use is recorded but does not itself set the solution-assisted label; independent solving here means without a prior solution reveal. A correct submission before any reveal is independently solved; after a reveal, future attempts remain assisted. A later reveal does not erase the historical independent solve, but the exercise displays that a solution was viewed. Completion and independent-solve counts are separate.
- Text checking trims surrounding whitespace and normalizes CRLF to LF only; every accepted variant is authored. SQL keyword casing variants are listed explicitly. Internal spacing, punctuation and case otherwise matter; UI explains the restricted checking. Quiz answers use stable option IDs.
- Mock authentication uses a fixed public demo passphrase `practice-only` for every local account, never a real password. Registration asks for display name/email only and explains the shared passphrase. Login accepts only that public demo value. No password or hash is stored. This is not secure authentication or a privacy boundary: browser-local data can be inspected/modified.
- Mock accounts, session and learner records persist in localStorage in this browser via the service only. Sign out clears the active session, not records. Separate local mock accounts get separate records; this is a simulation, not backend authorization. Storage errors produce a recoverable message; corrupted data is never silently reset. An explicit demo-failure control in Settings exercises retry without altering progress.
- Plain React state and hash navigation avoid extra routing/state dependencies. CSS uses system sans-serif/monospace plus a locally bundled, open-license Silkscreen display font for the owner-selected retro redesign; no UI library or external runtime asset dependency. Vitest, Testing Library and jsdom are selected for behavioral tests; TypeScript and Vite check/build.

## Stack tradeoff

React/Vite matches the owner's selection and supports a small static mock app without server rendering. Vue/Vite would also support this scope but introduces a different component model without a project benefit. FastAPI + SQLAlchemy fits the selected later Python direction; Django would supply more built-in account/admin machinery but adds conventions unnecessary for the current frontend stage. These alternatives are recorded for traceability, not reopened choices.

## Deferred and missing

OpenAPI (#11) and in-memory backend auth/ownership (#12–14) have separate stage evidence; SQLite persistence has separate #15–16 evidence; real integration/final-audit evidence is recorded for #17–18. A genuine manual partial transcript is preserved separately from the summary; #4/#18 passed independent source-aligned review after the owner-authorized requirements reconciliation. Additional archive turns remain disclosed gaps, not fabricated. Exact October 20 submission time remains unknown.

## In-memory backend engineering defaults

The owner authorized FastAPI with in-memory storage after contract QA. Argon2id uses argon2-cffi PasswordHasher defaults (random salt, adaptive work factor and rehash on login). The registry stores SHA-256 digests of cryptographically random 32-byte tokens; only issuance returns the bearer value. Expiry is 24 hours and logout revokes only its authenticated session. These implement the contract defaults, not the insecure mock passphrase flow.

A transaction protocol separates storage from handlers. The memory adapter uses a process-local lock and copy-on-commit state to serialize operations, ensure coherent reads and roll back exceptions, including failed writes. This deliberately favors simple correctness over scaling for this academic stage. At that historical in-memory gate, one worker was used and records were intentionally lost on restart. The following persistence-stage defaults supersede that runtime limitation. No CORS/frontend adapter or UI changes are introduced. No contract conflict or rule change was needed.

## SQLite persistence defaults

The owner authorizes SQLAlchemy ORM with SQLite, configured by required DATABASE_URL. A factory creates the runtime app with SQLStorage; MemoryStorage remains test-only by explicit injection. Account/password-hash/preferences and session digests/UTC expiry persist alongside authored curriculum, lesson/exercise flags, hints and stable-order attempts. Revocation remains deletion of the current session; old tokens cannot reappear after restart.

The existing atomic State boundary is retained. A guard-row UPDATE before State reads obtains SQLite's writer lock across adapter connections; Session transactions commit together or roll back. ORM PK/unique/FK/check constraints reinforce ownership, email uniqueness, parent IDs, attempt order and Boolean progress facts. Necessary SQLite connection configuration is isolated in the adapter. Only SQLite was tested. Initialization is repeatable and never resets learners; content drift requires an explicit migration rather than silently overwriting records. No API/product-rule change was needed.

## Integration defaults

The owner authorizes the real API adapter as default while preserving explicit mock development/tests. VITE_API_BASE_URL defaults to same-origin /api/v1; local Vite proxy targets port8000. No permissive CORS is required for that local route. Private password registration is added at the existing service boundary as optional for mock compatibility but required by real adapter/UI; login retains the interface credential field and maps it to wire password.

The real credential is tab-scoped sessionStorage with expiry, separate from browser-local mock records. It is not an XSS-resistant secret store; HTTPS is required outside localhost. Logout clears private state even if revocation cannot be confirmed offline, with visible failure. No API error triggers mock fallback and no write is automatically retried. A persistent ignored project data directory replaces /tmp for normal local DB; existing temporary/browser mock records are left untouched. These are documented integration engineering defaults, not changes to learning rules. Final audit #18 remains separate.
