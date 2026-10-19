# Final submission audit — issue #18

Date: October 19, 2026, Asia/Almaty. **Overall submission audit: BLOCKED (QA FAIL for unmet required criterion), not submission-ready.** Technical application checks pass. The initial audit lacked original planning messages; a subsequent genuine partial manual copy is now preserved, but full-history completeness remains unresolved under #4. Neither the existing summary nor this conversation summary is represented as the original transcript. #4 and #18 remain required `mvp` issues and open; no unfinished requirement was relabeled post-MVP.

## Scope, environment and revisions

Engineer inspected the actual checkout, remote issues, Git objects, prior QA reports and current source. Independent reviewer `final_qa` did not implement the app. The audit began at `457b6c396a716000f5ea44ca7ed6f913c41c0756`; corrected app/test-tooling reviewed at published `cc53f0cbb1a5769611ffd9458e676cd6182033c0`. Audit documentation gets its own committed handoff/review below; do not confuse a documentation draft with a passed submission gate.

Verified environment: macOS, Python3.13.0, bundled Node24.19.0/pnpm11.25.0, SQLAlchemy2.0.44/SQLite, installed Google Chrome driven by Playwright. Only this environment/SQLite was tested, not other OS/database/deployment configurations. This was agent-operated browser verification, not an invented session with an external human or instructor.

The original assignment screenshot is absent from the repository. This audit maps the supplied textual assignment/project requirements and specification; unseen screenshot-only requirements cannot be certified. Exact October20 submission time/instructor delivery instructions remain unknown. No deployment or submission was attempted.

## Clean remote checkout and setup

A separate remote clone, fresh Python environment and installed frontend dependencies were used; existing node_modules/venv/database/browser profiles were not copied. Exact commands executed:

```sh
git clone https://github.com/240103097-jpg/WeCode.git /tmp/wecode-final-audit/checkout
python3 -m venv /tmp/wecode-final-audit/venv
/tmp/wecode-final-audit/venv/bin/python -m pip install -r /tmp/wecode-final-audit/checkout/backend/requirements-dev.txt
pnpm --dir /tmp/wecode-final-audit/checkout/frontend install --frozen-lockfile
```

Clone was initially clean at457b6c3. After publishing the actual mobile correction/all-unit audit tooling, `git -C /tmp/wecode-final-audit/checkout pull --ff-only` updated it to clean cc53f0c without copying uncommitted files. Python installation succeeded; pinned direct dependencies were installed into the new environment. pip/pnpm reused downloaded/content-addressed package caches, which is disclosed rather than claiming an uncached download. Frozen lockfile passed and installed120 frontend packages. `pip check` reported no broken requirements.

From the clean checkout, DATABASE_URL pointed to that checkout's own ignored data/wecode.sqlite3; `prepare_local.py` ran twice without reset. Additional init_db.py ran twice on a separate disposable DB, followed by actual HTTP smoke through a real started backend and all11 response contract checks. No normal project database or browser learner data was modified/deleted. Independent QA inspected the clean clone/fresh installed binaries/environment and also verified pipcheck.

## Executed automated checks

The clean checkout executed these commands with its own fresh Python environment and documented Node/pnpm PATH:

```sh
pnpm --dir frontend typecheck
pnpm --dir frontend test
pnpm --dir frontend build
pnpm --dir frontend check:bundle
pnpm --dir frontend contrast
/tmp/wecode-final-audit/venv/bin/python -m pytest backend/tests -q
/tmp/wecode-final-audit/venv/bin/openapi-spec-validator openapi.yml
/tmp/wecode-final-audit/venv/bin/python tools/contract/validate.py
/tmp/wecode-final-audit/venv/bin/python -m pip check
python3 backend/scripts/sync_curriculum.py
/tmp/wecode-final-audit/venv/bin/python backend/scripts/check_restart.py
```

Results:

| Check | Actual result |
| --- | --- |
| Frontend behavior | **PASS27/27**, including original mock cases, all real API mappings/private-state/auth races. |
| Type check and production build | **PASS** after mobile correction; CSS artifact index-Dx6OpIQN.css. |
| Real production bundle | **PASS**, no mock service/storage or authored answer fixtures. |
| Contrast | **PASS26** text/control/focus combinations; palette unchanged. |
| Backend API/behavior/ORM tests | **PASS162/162**, isolated memory/SQLite variants; one upstream Starlette/AnyIO TestClient deprecation warning, not a failure. |
| OpenAPI validator | **OK**, root contract unchanged. |
| Contract coverage/reference/example checks | **PASS348** local reference occurrences, **409** example occurrences,12 frontend methods/11HTTP+1mock-only,9units/27exercises and26 negative checks. Counts are occurrences across reused schemas. |
| Curriculum export and dependency consistency | **PASS**, exact existing authored content/rules; pipcheck no broken requirements. |
| Actual backend HTTP smoke | **PASS all11** operations with schema/status/header validation from the clean environment. |
| Backend restart script | **PASS**, three distinct real processes/same temporaryDB, profile/preferences/read/9attempts/hints/reveal/assistance/completion/sessions/ownership retained. Expiry test moves one disposable timestamp into the past while stopped; no claim of waiting24hours. |

Independent QA separately reran27frontend/162backend/type/build/bundle/26contrast/root-contract/content/restart/pip checks, rather than relying on engineer output. Initial sandbox localhost binding was denied, then the same check reran with authorized local-port access and passed; this was an environment restriction, not an application failure.

## Real UI → proxy → API → SQLite audit

Actual clean-checkout command:

```sh
BACKEND_PYTHON=/tmp/wecode-final-audit/venv/bin/python WECODE_AUDIT_ALL_UNITS=1 BROWSER_ARTIFACT_DIR=/tmp/wecode-final-audit/clean-browser node frontend/scripts/check-integration.cjs
```

**PASS:296 actual API responses.** The harness used real Chrome UI controls, its own Vite proxy/backend processes and an isolated SQLite file, never a mock service. For every Python/SQL/Git × Beginner/Intermediate/Advanced unit it changed the preference through UI, opened/read the lesson, submitted authored wrong and correct answers for Quiz/Fix the Bug/Complete the Code, requested hints, explicitly revealed the bug solution and retried correct work. Result:9/9 units complete,18/27 independently solved,9revealed solutions and70saved submissions, without extra completion credit. Saved private history/progress matches exactly after reload, actual backend PID change/sameDB restart, logout/fresh login and profile edit.

A second account had no attempts/progress. Backend shutdown produced a visible error with no mock fallback; restart+Retry recovered. Invalid and locally-expired credentials cleared private state. Existing mock sentinel remained byte-for-byte unchanged and mock curriculum/service modules were never requested in real mode. Desktop1440, mobile320/375 navigation/focus/readability and no page overflow were checked. Progress-row geometry now additionally verifies title/stat rectangles do not intersect and stay inside each row for all9 units; code may scroll internally.

Independent QA separately ran both the55-response baseline and296-response all-unit scenario at published cc53f0c, inspected original-resolution mobile lesson/Progress screenshots and added the geometric regression assertions. Engineer artifacts: `/tmp/wecode-final-audit/clean-browser`; independent artifacts: `/tmp/wecode-final-independent-all-units`. Redacted traffic records contain method/path/status only, no passwords/tokens. Harness-owned temporary DBs/processes were cleaned, normal previews stayed running.

Early audit-tool runs exposed test synchronization/expectation mistakes: the all-unit scenario still expected1/9, and a preference save needed to complete before navigating to the next unit/read action. These were corrected in `f5a724a`/`cc53f0c`; complete fresh published reruns passed. They are recorded as tooling corrections, not fabricated learner-facing bugs or hidden failed checks.

## Observed defect #23

Independent QA actually observed320px Progress title/status overlap despite no horizontal overflow. [Issue #23](https://github.com/240103097-jpg/WeCode/issues/23) received Goal/criteria/out-of-scope/constraints before correction. Engineer changed only the narrow-screen row layout to an explicit grid in `ad7f6fa`; palette/content/rules/backend remained unchanged. Independent QA added actual geometric browser assertions at1440/320/375, visually inspected the fix, reran27frontend tests/type/build/bundle/26contrast and [closed #23 after PASS](https://github.com/240103097-jpg/WeCode/issues/23#issuecomment-6273328058). No additional actual defect was observed. Prior #21/#22 fixes remain covered and closed.

## Documents, stage history and issue inventory

[Submission checklist](../submission-checklist.md) maps each supplied requirement to files/commits/issues/checks. Stage order was verified directly with Git object presence/absence and ancestry, not solely old reports:820433f mock frontend → ad6837e contract → 2b95299 memory backend →7a32ee8 ORM/SQLite →4557423 real integration. Prior QA stage scopes are retained as historical evidence.

Required Markdown/process/role/testing/design files and issue templates were inspected as tracked objects. README now links the previously indirect role, mock/curriculum/planning/API/SQLite docs plus the new checklist/demo/final-audit artifacts. Relative Markdown targets/fragments and git diff --check are checked before each audit documentation commit. Stale current-stage wording in mock/curriculum documentation was clarified; historical QA facts were not rewritten as new passes. Owner-supplied reference image was locally re-inspected; filename/provenance/adopted patterns remain in design-system.md with no fabricated URL or copied reference wording.

Open-issue inspection after #23 closure: **#4 mvp** missing transcript, **#18 mvp** final audit, **#19 post-mvp** deliberately deferred AI/execution research. No open user-test-bug. All required unfinished work retains mvp labels. #4 is a material blocker; #18 cannot be closed merely because tests pass. GitHub remains the canonical active backlog.

## Independent final verdict

Independent reviewer completed the document/publication review at `a501ccbe17b22175c67c58647e4c062f6e3f28d0`, with application/test-tooling at `cc53f0cbb1a5769611ffd9458e676cd6182033c0`. [Actual final QA comment](https://github.com/240103097-jpg/WeCode/issues/18#issuecomment-6273418192) records **QA FAIL — BLOCKED by missing required owner material; technical application checks PASS**. QA left #18 OPEN.

| #18 criterion | Independent verdict |
| --- | --- |
| 1 Requirement mapping/stage order | PASS |
| 2 Committed documents/design reference | PASS |
| 3 Genuine original transcript/source limits | BLOCKED |
| 4 Clean setup/checks | PASS |
| 5 Full real application audit | PASS |
| 6 Issue/observed-defect workflow | PASS |
| 7 Final documents/results/publication | PASS |
| 8 Every criterion passed/submission readiness | BLOCKED — therefore overall QA FAIL under process rules |

The reviewer independently verified29 tracked Markdown files and103 relative targets/fragments with no broken links, clean HEAD matching origin/main, empty application/backend/contract diff from the reviewed implementation and actual-timestamp publication. Open required issues remain #4/#18, no user-test-bug open; #19 remains deliberately post-MVP. The following final evidence-only addendum changes no application/test code and preserves that verdict.

## Remaining requirements and limitations

- **BLOCKED — partial evidence supplied:** owner provided ten original messages as a manual partial copy with provenance; omitted earlier ideation/selection and other missing turns still prevent the existing full-history criterion passing (#4). The summary remains separate and non-verbatim.
- **RESOLVED source-access limit:** original assignment screenshot is now preserved in docs/references/assignment.png and every visible clause compared in the submission checklist. Initial screenshot-absence statements above record the earlier audit, not current availability.
- Exact submission time and instructor delivery instructions remain unknown. No operational submission deadline/hour or delivery method is invented.
- No external human usability session, instructor acceptance, deployment, other-OS/database support or 24-hour wall-clock expiry wait is claimed.
- Normal frontend/backend previews may demonstrate technical behavior, but do not establish submission readiness. No deployment/submission was performed.

## Supplied original materials re-review

Owner supplied `codex-clipboard-3639f1c8-7eb5-4005-824a-35bb2ca6fba3.png` and explicitly described the conversation text as a manually copied, partial transcript. Engineer inspected the actual screenshot, copied it byte-for-byte, and saved ten alternating User/Assistant messages in [brainstorming-transcript.md](../brainstorming-transcript.md), preserving Russian wording, line order and literal table tabs. It begins with post-registration levels and ends with WeCode naming; no omitted dialogue was invented. This is not an automated export.

The [screenshot comparison](../submission-checklist.md#actual-assignment-screenshot-comparison) resolves the prior rubric-access limit. Newly explicit checks include nontrivial/different-from-PartI (owner attestation, not invented independent artifact evidence), design-reference alternative, all-mvp closure, all-.md publication, ORM and exact iteration order, and actual observed-bug workflow. Screenshot asks for brainstorming chat history as .md; it does not prescribe automated export or expressly say full. Existing #4/#18 criteria do expressly require full history, so saving an excerpt cannot silently satisfy that stricter gate.

Missing coverage: original beginning/ideation, alternative rejection/app selection/initial track discussion, individual/deadline/PartI exchange and original English-language decision; the summary's later agreement to document is also not in the excerpt. This describes absent coverage, not fabricated wording or exact missing turn counts. No new app/UI/storage/contract code was changed, so prior technical test evidence remains historical rather than falsely reported as rerun. Independent materials QA must review transcript fidelity, actual clauses and existing issue criteria before any closure; verdict is recorded in the follow-up handoff.

### Independent supplied-material verdict

Reviewed published `6afa25a0d35f97bde5493a698e3d9c4eb65406a6` by independent `materials_qa`. [Issue #4 verdict](https://github.com/240103097-jpg/WeCode/issues/4#issuecomment-6273958303) and [remaining #18 verdict](https://github.com/240103097-jpg/WeCode/issues/18#issuecomment-6273958781): **QA FAIL overall / BLOCKED by incomplete full original history**, both issues remain OPEN mvp.

- Transcript fidelity, ten-message speaker order, exact wording/tabs and partial manual provenance: PASS. This is not an automated export, and none is required for acceptable provenance.
- Actual assignment screenshot inspection, unchanged source/copy SHA-256, every visible clause comparison and README/spec links: PASS. Prior screenshot-access limitation is resolved. Screenshot asks for chat history; the stricter full-history gate is in the existing #4/#18 criteria and was not silently weakened.
- #4 criterion1 and complete-artifact portion of criterion2: BLOCKED. #18 criterion3 and overall criterion8: BLOCKED. Missing earlier/omitted conversation coverage is enumerated in the checklist; no missing wording/turn count was invented.
- #18 criteria1/2/6/7: PASS for updated materials/docs/status/publication. Prior independent technical criteria4/5 remain historical PASS; no application/browser rerun is claimed for this documentation-only review.
- Independent checks:30 tracked Markdown files,116 relative target occurrences/12 fragments, zero broken links; `git diff --check` PASS; screenshot byte hashes equal; empty frontend/backend/root-contract diff from6ddfd0a; reviewed HEAD matched origin/main. No database/secrets added or learner data changed.

The final evidence-only follow-up commit preserves this independent verdict. No all-mvp-closed, submission-readiness or instructor-submission claim is made. Owner action: supply actual omitted original messages in order with scope/provenance, or a genuine complete manual copy, for another criteria review.
