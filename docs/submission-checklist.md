# Submission evidence checklist

Audit date: October 19, 2026, Asia/Almaty. **Overall: BLOCKED — not submission-ready.** The genuine full original brainstorming/planning transcript is missing ([required issue #4](https://github.com/240103097-jpg/WeCode/issues/4)); the preserved summary is not a verbatim export. [Final audit #18](https://github.com/240103097-jpg/WeCode/issues/18) stays open until every required criterion passes. No deployment or instructor submission was performed.

Scope: requirements supplied in the owner's assignment/project instructions and [specification](../WeCode_Project_Specification.md). The original assignment screenshot is not in this repository, so direct comparison with an unseen original rubric is **BLOCKED/unverified**, not silently claimed. This is an evidence limitation, not a newly invented requirement to publish a screenshot. Exact October 20 submission time/delivery instructions are unknown. Status PASS below means the specified evidence was actually inspected/rechecked, not that overall submission readiness passes.

## Requirement mapping

| Requirement | Status | Concrete evidence and actual verification |
| --- | --- | --- |
| Specification/app identity/individual project and English scope | PASS | [Specification](../WeCode_Project_Specification.md), [decisions](decisions.md); current source and real Chrome UI inspected. App is WeCode; due date/timezone recorded without invented exact time. |
| Preserve brainstorming summary and label it honestly | PASS | Specification section 9 explicitly says summary, not verbatim export; original summary remains in Git from `e1e5dd3`. No reconstruction was added. |
| Add genuine full original planning transcript/provenance | **BLOCKED** | [#4](https://github.com/240103097-jpg/WeCode/issues/4) open `mvp`; `git ls-files` has no transcript/conversation export; spec and planning record acknowledge missing owner artifact. Owner must supply genuine export and provenance for review. |
| Review reference articles and follow assignment precedence | PASS (historical evidence) | [Planning source review](planning.md#source-review-and-precedence), commit `adc3cf7`; documented accessible/read articles and explicit assignment override for stage sequence/QA-only closure. Audit checks this record, not a claim of a new article-access session. |
| PM-refined focused GitHub backlog and labels | PASS | [Issues](https://github.com/240103097-jpg/WeCode/issues), [task template](task-template.md), [task issue template](../.github/ISSUE_TEMPLATE/task.md); all issue bodies/statuses inspected. `mvp`, `post-mvp`, `user-test-bug` retained; #4/#18 remain required. |
| PM → Engineer → independent QA; QA-only closure | PASS | [Process](process.md), [role instructions](team/pm.md), [engineer](team/software-engineer.md), [QA](team/qa-engineer.md); stage QA reports and actual GitHub QA comments. Roles are Markdown instructions, not executable programs. #23 independently verified before QA closure. |
| Required planning/process/testing/design/role Markdown docs | PASS | Document inventory below; tracked in Git, linked from README, relative targets/fragments checked. |
| Owner-selected visual reference and coherent design decisions | PASS | [Design system](design-system.md#owner-selected-retro-computing-reference), owner image filename/provenance without invented URL; locally supplied image re-inspected during this audit. Retro palette, grid, square borders, pixel headings, typography/focus/contrast documented. [Redesign QA](qa/redesign.md), commit `71abf99`, issue #20. |
| Stage 1: interactive frontend with centralized mockService | PASS | `820433f` contains frontend/services/mockService; no backend/OpenAPI then. `5456eb7`, `726ce81`, `46fd8b5`, `eba7015` add features; [frontend QA](qa/frontend.md), issues #5–10. Current mock regressions still pass; explicit dev-only mock mode remains. |
| Stage 2: root API contract | PASS | `ad6837e:openapi.yml`, no backend yet; [mapping](api-mapping.md), [contract QA](qa/api-contract.md), #11. Actual validator/schema/example/reference/AST checks rerun PASS. |
| Stage 3: contract implementation with in-memory backend | PASS | `41f6567`, `1b63c41`, `2b95299`; `backend/wecode/storage.py` and no sql_storage.py at this stage. [Backend QA](qa/backend.md), #12–14. Memory adapter behaviors rerun as part of current backend suite. |
| Stage 4: SQLite through ORM | PASS | `f90aa23`, `7a32ee8`; SQLAlchemy models/storage, no real frontend API adapter yet. [SQLite lifecycle](sqlite.md), [QA](qa/sqlite.md), #15–16. Current SQLite/constraints/rollback/restart checks PASS. |
| Stage 5: connect frontend and thoroughly test | PASS (technical checks) | `4557423` real API adapter, [integration evidence](qa/integration.md), #17/#21/#22. Final fresh-checkout audit at `cc53f0c` runs all nine units/all 27 exercises via real browser/API/SQLite, 296 observed responses. Overall submission remains transcript-blocked. |
| Registration/login/logout and real session ownership | PASS | `apiService.ts`, backend auth handlers, Argon2id/session models; 27 frontend/162 backend tests and actual browser signup/login/logout/401/expiry/second-account checks. No passwords/raw bearer credentials stored in DB or committed. |
| Python/SQL/Git × editable Beginner/Intermediate/Advanced | PASS | Exact 9-unit/27-exercise authored export, [curriculum review](curriculum-review.md); all nine real UI track/level selections and history retention checked. No artificial locking. |
| Short English lessons and all three exercise types/feedback | PASS | All nine lesson views/read flags plus wrong/correct Quiz/Fix the Bug/Complete the Code through real API; authored expected feedback verified. Backend all 27 accepted/rejected cases and content equality PASS. |
| Retries, hints after wrong, separate Show Solution | PASS | UI/API checks for every exercise; hints count, solution-reveal action and saved attempts verified. No automatic replay of writes on network failure. |
| Saved progress, assistance vs independent work, no duplicate credit | PASS | Final all-unit test: 9/9 complete, 18/27 independent, nine revealed solutions, 70 saved submissions; repeated correct attempts do not duplicate completion. Exact snapshot survives reload and real process restart. No XP/scoring added. |
| Persistent accounts/preferences/history/state and data isolation | PASS | Isolated SQLite tests, actual backend stop/restart with same DB/fresh login, empty second account, session expiry/revocation tests. Composite/unique/FK/check constraints and concurrent adapter tests PASS. |
| Real-mode server curriculum/checking and no key leakage/execution | PASS | Root contract/public schemas, separate public ORM curriculum/private rules, real bundle exclusion check, network module check and ordinary snapshots. No `eval`/execution of submitted learner text; tests verify malicious text stays text. AI tutor remains post-MVP #19. |
| Real default, explicit mock only, env/proxy and preserved mock data | PASS | `service.ts`, Vite proxy, [.env.example](../.env.example), [frontend env](../frontend/.env.example); real browser requests observed, outage never chooses mocks, mock sentinel preserved. Normal DB is ignored project data/wecode.sqlite3. |
| Loading/validation/network/server-error recovery | PASS | Browser wrong login/duplicate signup/invalid-expired session/outage+Retry; adapter tests and backend strict errors. Interrupted-write uncertainty explained; Refresh workspace reads server state. |
| Responsive desktop/mobile, readable controls/focus | PASS after fix | Real 1440/320/375px checks, 26 contrast combinations; observed [#23](https://github.com/240103097-jpg/WeCode/issues/23) mobile Progress overlap corrected in `ad7f6fa`, independent geometry/visual QA PASS and closed. |
| Meaningful automated checks and clean reproducible setup | PASS | [Final evidence](qa/final-audit.md): remote clone into separate directory, fresh venv/frozen pnpm install, isolated DB, 27 frontend/162 backend tests, type/build/bundle/contrast/contract/content checks and 296-response browser journey. Package caches reused; no old project node_modules/venv/learner records copied. |
| Actual observed bug workflow and open-issue inspection | PASS (process) | #21/#22 previously QA-closed; newly observed #23 PM-refined/fixed/QA-regressed/closed. No invented bug or external human user-test session. Remaining required #4/#18 stay open; no required work relabeled post-MVP. |
| Reproducible demonstration guide and commands | PASS | [Demo guide](demo-guide.md), [README](../README.md); verified startup, safe isolated automated demonstration and manual sequence. |
| Commit/push, preserve unrelated data; no deploy/submit | PASS for published reviewed revisions | Ordered actual-timestamp commits and remote origin verified. Only data/.gitkeep tracked; normal learner DB/mock records untouched. Final audit docs commit is reported in GitHub #18 evidence and final response. No force-push/deployment/submission. |

## Stage-order verification from actual Git objects

Executed `git cat-file -e <revision>:<path>`, `git ls-tree -r --name-only <revision>` and `git merge-base --is-ancestor` for each successive stage:

| Order | Revision | Object and exclusion checked |
| --- | --- | --- |
| 1 | [820433f](https://github.com/240103097-jpg/WeCode/commit/820433f) | frontend mockService exists; backend/ and openapi.yml absent. |
| 2 | [ad6837e](https://github.com/240103097-jpg/WeCode/commit/ad6837e) | root openapi.yml exists; backend/ absent. |
| 3 | [2b95299](https://github.com/240103097-jpg/WeCode/commit/2b95299) | in-memory Storage/API exists; SQL adapter absent. |
| 4 | [7a32ee8](https://github.com/240103097-jpg/WeCode/commit/7a32ee8) | SQLAlchemy adapter exists; frontend real API adapter absent. |
| 5 | [4557423](https://github.com/240103097-jpg/WeCode/commit/4557423) | real frontend API adapter exists after SQLite. |

All ancestry/object/exclusion checks passed. Historical QA report scopes are preserved rather than rewritten as new-stage claims.

## Required document inventory

Committed original documents: README.md, AGENTS.md, WeCode_Project_Specification.md; docs/process.md, task-template.md, testing-guidelines.md, design-system.md; docs/team/pm.md, software-engineer.md, qa-engineer.md; GitHub task/observed-bug templates. Supplemental decisions/planning/curriculum/mock/API/SQLite/integration docs and every prior stage QA report are linked in README. This audit adds this checklist, demo-guide.md and qa/final-audit.md. Their actual publication/review revision is recorded by the audit handoff, not assumed before commit.

## Open issues and owner-provided materials

- **#4 mvp — BLOCKED:** genuine original transcript/export and provenance still needed. Preserve the summary. Only independent QA may close after genuine artifact review.
- **#18 mvp — BLOCKED overall:** technical checks may pass, but full audit cannot pass until the transcript criterion and any remaining verification limits are resolved.
- **#19 post-mvp:** deliberate AI/execution research exclusion, not relabeled unfinished MVP.
- No open user-test-bug after #23 independent PASS. [Final independent #18 verdict](https://github.com/240103097-jpg/WeCode/issues/18#issuecomment-6273418192): criteria1/2/4/5/6/7 PASS,3/8 BLOCKED, overall QA FAIL. Re-query GitHub for changes; this is an audit snapshot, not an alternative active backlog.

Owner still needs to supply the genuine transcript. The original assignment screenshot, exact submission time and final delivery instructions are unavailable for independent comparison/operational scheduling; no submission action is authorized. No claim of instructor acceptance, deployment, external human testing or other-database compatibility is made.
