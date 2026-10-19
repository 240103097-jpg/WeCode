# Frontend decisions — October 19, 2026

## Owner decisions

WeCode uses English UI and curriculum, a dark theme with yellow/green accents, and React + TypeScript + Vite. Python/FastAPI, SQLAlchemy and SQLite are selected for later stages, not implemented now. Detailed visual design is delegated to the agent.

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
- Plain React state and hash navigation avoid extra routing/state dependencies. CSS uses system sans-serif and monospace fonts; no UI library or external asset dependency. Vitest, Testing Library and jsdom are selected for behavioral tests; TypeScript and Vite check/build.

## Stack tradeoff

React/Vite matches the owner's selection and supports a small static mock app without server rendering. Vue/Vite would also support this scope but introduces a different component model without a project benefit. FastAPI + SQLAlchemy fits the selected later Python direction; Django would supply more built-in account/admin machinery but adds conventions unnecessary for the current frontend stage. These alternatives are recorded for traceability, not reopened choices.

## Deferred and missing

OpenAPI, backend auth, server ownership checks and SQLite restart guarantees belong to later issues #11–18. The genuine original planning transcript remains missing (#4); the existing summary is preserved, not reconstructed. Exact October 20 submission time remains unknown.
