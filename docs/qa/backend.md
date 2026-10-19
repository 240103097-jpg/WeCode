# In-memory backend independent QA — issues #12–14

Date: October 19, 2026, Asia/Almaty. Independent reviewer: `backend_qa`, separate from the PM/implementing agent. The following criterion evidence was produced by that reviewer and is preserved without self-certification.

All three issues passed sequential dependency gates and were closed by independent QA:

- [#12 authentication PASS](https://github.com/240103097-jpg/WeCode/issues/12#issuecomment-6271465987) at `41f656718e3798df511e4bd13deb52c60081e7e0`.
- [#13 curriculum/preferences/read PASS](https://github.com/240103097-jpg/WeCode/issues/13#issuecomment-6271513325) at `1b63c411d8fc9978a54b801742435d21d8422f12`.
- [#14 full in-memory stage PASS](https://github.com/240103097-jpg/WeCode/issues/14#issuecomment-6271609514) at published `2b9529985210a8d42c2f4bce8de4918e8df5d60d`.

## Authentication gate

QA: PASS
Issue: #12; revision: 41f656718e3798df511e4bd13deb52c60081e7e0; independent reviewer: backend_qa (not implementing agent); environment: macOS, Python 3.13, isolated /tmp/wecode-backend-venv.

Criterion 1: PASS — reviewed and exercised all five auth/profile operations, root-contract response schemas, expected statuses, normalized fields, malformed JSON, wrong media, extra fields and no-store headers. Strict non-object raw JSON requests additionally returned 422.
Criterion 2: PASS — inspected Argon2id implementation, independently verified equal passwords receive different salted hashes; registry holds SHA-256 token digests, tokens use secrets.token_urlsafe(32), expiry is 24 hours. Tests exercised missing/malformed/unknown/expired/revoked tokens, Bearer challenge, generic incorrect/unknown login response, separate sessions and logout. No credential logging or password/hash response serialization found.
Criterion 3: PASS — reviewed injectable Storage protocol, locked copy-on-commit adapter and failed transaction rollback; API tests verified normalized duplicate accounts, cross-account profile isolation and fresh-instance loss of accounts/sessions. README explicitly documents restart loss and one worker. No frontend or root-contract diff against baseline 2b12a4c; no ORM/database/client changes.
Criterion 4: PASS — independently ran `/tmp/wecode-backend-venv/bin/python -m pytest backend/tests -q`: 23 passed (one third-party AnyIO deprecation warning). Response checking validates schema/status/headers using root contract. Independently ran `/tmp/wecode-backend-venv/bin/python backend/scripts/smoke.py` against running localhost server: PASS real HTTP auth/profile/docs; local socket access required the environment's network permission, then succeeded. README/AGENTS setup/run/test instructions reviewed. `git diff --check` passed.
Criterion 5: PASS — PM readiness and engineer committed handoff precede this independent review; every criterion now verified.

No defects or unverified criteria remain for #12. Later curriculum/practice operations remain explicitly scoped to dependent #13/#14, not claimed here.
Disposition: independent QA closes #12 after PASS.

## Curriculum gate

QA: PASS
Issue: #13; revision: 1b63c411d8fc9978a54b801742435d21d8422f12; independent reviewer: backend_qa; environment: macOS/Python 3.13, /tmp/wecode-backend-venv.

Criterion 1: PASS — independently exercised all three new operations and reviewed authenticated-identity/transaction usage. API tests validate status, body and headers against root OpenAPI on actual responses.
Criterion 2: PASS — independently ran `/tmp/wecode-backend-venv/bin/python backend/scripts/sync_curriculum.py`: exact nine-unit/27-exercise and authored-rule match. Reviewed startup backend-only JSON loading and public-unit copy separate from answer rules. Seeded revealed exercise state did not enrich ordinary curriculum with secrets.
Criterion 3: PASS — tests checked independent levels, monotonic onboarding/read and repeated read behavior. Additional independent fixture seeded 12 tied-timestamp attempts plus a revealed exercise, edited preferences and verified complete stable-order history and progress unchanged; all nine units still returned. This tests snapshot preservation, not claims about as-yet-unimplemented practice writes.
Criterion 4: PASS — independently ran `/tmp/wecode-backend-venv/bin/python -m pytest backend/tests -q`: 34 passed, one upstream AnyIO deprecation warning. Coverage includes unknown/malformed IDs, invalid/extra fields/enums, missing/invalid auth, empty state, cross-user isolation, rollback and concurrent coherent preferences/read. Independently ran live `backend/scripts/smoke.py`: PASS auth/profile/curriculum/preferences/read/docs over real localhost HTTP (network permission enabled). `git diff --check` passed.
Criterion 5: PASS — dependency #12 closed by independent QA before PM readiness/implementation. Frontend and root openapi.yml have no diff versus 2b12a4c. Engineer committed handoff reviewed; reviewer did not implement code.

No failures or unverified criteria for #13. Practice mutation behavior remains dependent #14.
Disposition: independent QA closes #13 after PASS.

## Full in-memory stage gate

QA: PASS
Issue: #14; revision: 2b9529985210a8d42c2f4bce8de4918e8df5d60d; independent reviewer: backend_qa; environment: macOS/Python 3.13, /tmp/wecode-backend-venv, bundled Node 24/pnpm.

Criterion 1: PASS — reviewed server-only exact authored accepted-variant membership and CRLF/trim normalization. Independently ran all 27 exercise parameter cases across Quiz/Fix the Bug/Complete the Code, including authored rejected/accepted answers and feedback. Wrong answers save attempts; malicious learner text is treated only as text and no execution occurs.
Criterion 2: PASS — tests independently exercised own exact-exercise prior-wrong hint gate, repeated count increments, later-correct hint access, separate/idempotent reveals without attempt/correct credit, invalid/parent-mismatched IDs, impersonation/correctness fields and bodyless action validation. Other users' attempts cannot unlock hints or assistance.
Criterion 3: PASS — reviewed locked copy-on-commit transaction scope across every read/write. Tests exercised concurrent submit/reveal/read with tied timestamps, monotonic correct/independent flags, preservation of prior independent solve, reveal-before-correct assistance, all-attempt retention and commit-failure rollback. All nine units complete once despite repeated successful/wrong submissions; no credit/XP counter exists. Preference/profile edits retain history.
Criterion 4: PASS — independently ran `/tmp/wecode-backend-venv/bin/python -m pytest backend/tests -q`: 79 passed (one upstream AnyIO deprecation warning). Actual API statuses, headers and payloads validated against root contract. Independently ran `backend/scripts/smoke.py` against running localhost backend: PASS all 11 HTTP operations, all three exercise types, hints/reveal/retries/completion; actual real HTTP responses contract-checked. Independently reran curriculum drift check: exact match. Root `openapi-spec-validator openapi.yml`: OK; custom validator: 348 reference occurrences, 409 example occurrences, 12 frontend methods and 26 negative checks PASS. Independently reran frontend typecheck, 19 tests, production build and 26 contrast checks: PASS.
Criterion 5: PASS — reviewed README/AGENTS and docs/backend.md commands, abstraction, authentication, one-worker/restart-loss limits and later-stage boundaries. Live /docs and /openapi.json succeeded via smoke. Root contract and entire frontend diff against 2b12a4c empty. No SQLite/ORM/real client/UI changes. `pip check`: no broken requirements; 41 relative Markdown targets exist; `git diff --check` PASS; clean working tree. Fetched origin; HEAD and origin/main both equal reviewed 2b9529985210a8d42c2f4bce8de4918e8df5d60d; author/committer actual current timestamp 2026-10-19T21:05:11+05:00.
Criterion 6: PASS — independent reviewer did not implement backend; dependency #13 was closed after independent PASS before #14 readiness. Full in-memory stage independently rechecked, including earlier authentication/curriculum regression suites. Every criterion verified.

No blockers, defects or unverified criteria remain for the in-memory backend stage. The single warning is a dependency deprecation, not a failing check. SQLite/restart persistence and live frontend integration remain later stages.
Disposition: independent QA closes #14 after PASS.

## Repeatable commands and scope

See [README setup](../../README.md#in-memory-backend) and [architecture](../backend.md). From the repository root, with the documented environment and Node on PATH:

```sh
/tmp/wecode-backend-venv/bin/python -m pytest backend/tests -q
/tmp/wecode-backend-venv/bin/python -m pip check
python3 backend/scripts/sync_curriculum.py
/tmp/wecode-backend-venv/bin/openapi-spec-validator openapi.yml
/tmp/wecode-backend-venv/bin/python tools/contract/validate.py
pnpm --dir frontend typecheck
pnpm --dir frontend test
pnpm --dir frontend build
pnpm --dir frontend contrast
```

With the documented one-worker backend running, `/tmp/wecode-backend-venv/bin/python backend/scripts/smoke.py` exercises all 11 operations over real HTTP and validates their responses against root OpenAPI. It generates disposable credentials without printing them. Both engineer and independent QA executed the relevant commands successfully. Reference/example counts are occurrences across reused schemas, not counts of unique examples.

No SQLite, ORM, frontend API client or UI changes were made. In-memory restart loss is intentional and tested; persistent restart guarantees remain later work. Existing browser learner data was not touched. The final evidence-only documentation commit does not change the reviewed backend or frontend code.
