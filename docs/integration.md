# Real frontend integration

Issue [#17](https://github.com/240103097-jpg/WeCode/issues/17), October 19, 2026, Asia/Almaty. This stage connects the existing retro UI to the SQLite backend; it does not certify the final submission audit (#18).

## Boundary and configuration

`frontend/src/services/apiService.ts` implements the existing asynchronous LearningService interface. Optional registration password is the only input extension needed for mock compatibility: real mode requires it and Auth collects it privately, while mock mode keeps name/email-only registration. Login's compatibility field `passphrase` maps to wire `password`. The HTTP contract is unchanged. All 11 operations use the exact methods/paths documented in [API mapping](api-mapping.md).

`service.ts` chooses API mode by default. `VITE_API_BASE_URL` defaults to `/api/v1`; Vite's same-origin `/api` proxy targets port8000, configurable by API_PROXY_TARGET. Explicit VITE_SERVICE_MODE=mock is development/test only; no HTTP failure changes modes. Production rejects mock mode. Default real build excludes mock service/storage and authored curriculum/rules, checked by the bundle script. Mock UI explanation text is not an answer fixture. Public instructional sample code is intentionally retained.

The opaque API token/expiry are kept only under `wecode.api.session.v1` in tab-scoped sessionStorage. Passwords are never persisted. This token store is accessible to same-origin scripts, so HTTPS and protection against script injection remain necessary outside local development. API401/local expiry/logout clears token and private React snapshot/learner state. Generation checks reject old-account pending responses and obsolete startup updates. Failed anonymous auth preserves the form and its safe error. Logout clears local private state even offline, while reporting unconfirmed server revocation; that server token expires normally if it could not be revoked.

No learner components fetch directly or access storage. Curriculum, private history/progress, feedback, hints and explicit solutions come from the server. Errors show safe English text without raw proxy/server/debug output. Retry/Refresh workspace reads authoritative state; writes are never automatically replayed. An interrupted write may have saved, so the message asks the learner to refresh before another submission. Boolean completion still prevents duplicate credit when a user deliberately retries. Real Settings has no mock failure injection.

Normal local DATABASE_URL uses ignored project `data/wecode.sqlite3`, prepared idempotently by `backend/scripts/prepare_local.py`. Existing DBs are not deleted/reset/replaced. The old `/tmp` DB and browser `wecode.mock.v1` records are left untouched, not imported. Mock and real accounts are separate. Test databases remain isolated and temporary. See [complete-app commands](../README.md#run-the-complete-app-locally).

## Engineer verification

Actual commands/results at the integration handoff:

- `pnpm --dir frontend test`: 27 passed, including six API adapter cases and two real auth/private-state UI regressions; original 19 tests retained.
- `pnpm --dir frontend typecheck`: PASS.
- `pnpm --dir frontend build`: PASS; CSS asset unchanged (`index-8rC1T3ME.css`).
- `pnpm --dir frontend check:bundle`: PASS, no mock storage/service or authored answer fixtures in real production JS.
- `pnpm --dir frontend contrast`: PASS, 26 existing text/control/focus combinations.
- `/tmp/wecode-backend-venv/bin/python -m pytest backend/tests -q`: 162 passed, one upstream Starlette/AnyIO TestClient deprecation warning.
- `/tmp/wecode-backend-venv/bin/openapi-spec-validator openapi.yml`: OK.
- `/tmp/wecode-backend-venv/bin/python tools/contract/validate.py`: PASS, 348 local reference occurrences, 409 example occurrences, actual 12-method boundary and 26 negative schema checks. Counts reflect reused schema occurrences, not unique examples.
- `python3 backend/scripts/sync_curriculum.py`: PASS exact existing nine units/27 exercises and authored rules.
- `/tmp/wecode-backend-venv/bin/python -m pip check`: no broken requirements.
- `git diff --check`: PASS. 53 relative Markdown targets/four heading fragments checked before this evidence file. Root OpenAPI, CSS, authored curriculum and mockService source unchanged from baseline `cca5255`.

## Actual browser and network journey

`node frontend/scripts/check-integration.cjs` used an isolated real headless Google Chrome, Vite proxy, FastAPI and temporary SQLite file. It drove visible UI controls, not a mock service. The successful full run observed 55 API responses; evidence records only method/path/status, no tokens/passwords. Screenshots and redacted traffic were written to `/tmp/wecode-integration-evidence`. The harness creates and cleans only its own processes/temp DB, preserving the normal project DB and existing browser profile.

Verified: wrong login visibly401; fresh real signup201; Python/Beginner onboarding204; lesson read204; wrong and correct submissions201 for Quiz, Fix the Bug and Complete the Code; hint after wrong200; separate solution reveal200; assisted status correct; repeated correct submission saved without duplicate completion. Progress was one unit complete, two independently solved exercises, one revealed solution, seven saved submissions. All public units remained key-free.

Page reload restored session and exact snapshot. The actual backend process was stopped and restarted against the same database, and the browser restored the same snapshot. Desktop1440px and mobile320px Progress/Settings navigation were usable with no horizontal page overflow; normal code panels may scroll internally. Profile change204 survived login. Logout204 removed private client state; duplicate signup409 stayed on registration with an alert; re-login200 restored saved work. A second real account had empty attempts/progress and a distinct learner ID.

Stopping the backend and reloading produced a visible failure, no dashboard fabricated from mock data and no mock authentication fallback. Restart plus Retry restored real state. Locally expired and server-invalid credentials both cleared the token/private state and returned to authentication. A pre-existing mock sentinel remained byte-for-byte unchanged; no mock service/curriculum module was requested in real mode. Inspecting the real screenshots confirmed the retro palette/layout persisted.

## Observed defects and corrections

- [#21](https://github.com/240103097-jpg/WeCode/issues/21): incorrect anonymous login reset the form before error rendering. PM documented actual reproduction; engineer invalidates only an existing private credential, retaining anonymous auth form mode/error. UI regression plus actual browser wrong-login/duplicate-registration checks added.
- [#22](https://github.com/240103097-jpg/WeCode/issues/22): overlapping startup401/stale responses could replace the signed-out screen. PM documented reproduction; engineer guards App load/refresh results with a session generation and clears pending/error/private state on invalidation. UI regression plus actual invalid/expired reload checks added.

Both observed issues remain for independent QA verification/closure at handoff; engineer does not self-certify PASS. QA evidence will record final disposition separately. No unrelated defect or final-audit completion is invented.
