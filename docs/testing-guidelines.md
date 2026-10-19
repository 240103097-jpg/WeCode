# Testing guidelines

Frontend verification commands: in frontend/, run pnpm typecheck, pnpm test and pnpm build. See README.md for setup. Test user behavior and boundaries rather than mirroring implementation. Engineer supplies meaningful tests; independent QA runs them and checks every acceptance criterion. An unverified check cannot pass.

## By stage

- Frontend/mock: interactive flows through one centralized mockService; success, invalid input, loading, empty and recoverable failure states; keyboard use and English content. Verify mocks expose the same asynchronous service boundary used later.
- Contract: validate root openapi.yml; cover request/response schemas, authentication, status/error responses and service-operation mapping. Keep solution keys separate from ordinary exercise responses.
- In-memory backend: contract tests, registration/login failures, protected resources, cross-user isolation, authored-rule positive/negative/normalization cases, attempts, retries, hints, solution access and selected progress rules. No arbitrary submitted code execution.
- Persistence: run the same behavioral tests against ORM storage; use a temporary isolated SQLite database; verify saved accounts, per-track levels, attempts and progress after restart, ownership, transaction failures and repeat-submission behavior under approved rules.
- Integration: real UI → API → SQLite journeys across all three tracks, all levels and exercise types. Verify reload/restart, logout, errors, retries, hints and separate Show Solution. Recheck history after changing levels/tracks according to the owner-approved rule. No mocked service may stand in for final end-to-end evidence.

Content inventory and progress assertions use the owner-confirmed 9 units/27 exercises and completion rule in docs/decisions.md. Assisted completion counts, independent mastery is separate, and no XP/scoring is present. Review authored lessons and accepted/rejected examples for educational correctness and English.

## User testing and evidence

Record date, revision, environment, scenario, expected and actual outcomes. File only observed defects using the user-test bug template; include reproduction, severity/impact and evidence with private data removed. Search for duplicates. Suggestions and anticipated risks are planning tasks, not user-test-bug reports.

For documentation, verify local Markdown link targets and fragments, review external references, and run git diff --check. Report the exact scope of checks; document validation is not application validation.
