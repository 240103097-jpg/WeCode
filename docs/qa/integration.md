# Integration independent QA — issue #17 and observed bugs #21/#22

Date: October 19, 2026, Asia/Almaty. Independent reviewer: `integration_qa`, separate from the implementing agent. The reviewer's criterion evidence is preserved below. Reviewed implementation: `45574230a5c82b13a859454226fd3887561db401`, independently verified published on origin/main.

- [#17 integration PASS and QA closure](https://github.com/240103097-jpg/WeCode/issues/17#issuecomment-6272484202).
- [#21 incorrect-login feedback PASS and QA closure](https://github.com/240103097-jpg/WeCode/issues/21#issuecomment-6272481607).
- [#22 obsolete startup response PASS and QA closure](https://github.com/240103097-jpg/WeCode/issues/22#issuecomment-6272482785).

## Integration verdict

QA: PASS
Issue: #17; revision: 45574230a5c82b13a859454226fd3887561db401; environment: macOS, Python3.13, Node24.19.0, real installed headless Google Chrome through Playwright, FastAPI/Vite proxy, isolated temporary SQLite; October19,2026 Asia/Almaty. Independent reviewer did not implement application code.

Criterion1: PASS — reviewed service.ts, apiService.ts and Vite proxy. API mode defaults, VITE_API_BASE_URL honored; real production bundle excludes mock service/storage/answer fixtures. Own explicit VITE_SERVICE_MODE=mock development browser registered/onboarded without any API requests. No fallback on stopped backend.
Criterion2: PASS — all11 methods/paths/status/body mappings independently reviewed against openapi.yml; contract unchanged. Registration password extension and login passphrase→password explicit; normalization and bodyless assistance match. Real Settings has no failure injection.
Criterion3: PASS — real browser registration/login/logout, reload, local expiry, invalid bearer, second account and fresh login after invalidation passed. Credential-only sessionStorage isolated from preserved mock sentinel. Tests verify pending old-account snapshot rejection after logout; source generation guards reviewed. No password persistence or logging added.
Criterion4: PASS — UI wrong/correct Quiz/Fix the Bug/Complete the Code, hint, separate solution, assisted versus independent, deliberate correct retry and actual server snapshot:7attempts, one complete unit,2independent exercises,1hint, revealed bug solution. Independent extra UI level edits SQL Advanced/Git Intermediate/Python Beginner retained progress across restart/login; profile saved. Network writes are not automatically replayed; uncertainty and read-refresh recovery explicit.
Criterion5: PASS — independently ran engineer harness (55 real responses), own extended harness (58), then per-track variant (64). All owner12steps passed using real browser→Vite→FastAPI→SQLite, actual backend process PID change/same DB and exact snapshot equality. Desktop1440 and mobile320 authentication/dashboard/lesson/progress/settings checked; no horizontal page overflow. Screenshots visually inspected: readable solid lesson/form surfaces and retro design retained; keyboard Tab focuses real control, existing focus rules and26contrast checks pass. Offline visible failure/no dashboard or mocks, restart+Retry recovers; expired/invalid credentials clear and fresh login works.
Criterion6: PASS — inspected README/env/prepare_local.py, ignored project data/wecode.sqlite3, non-destructive schema setup and existing databases untouched. Only data/.gitkeep tracked. Tests/harness isolate temporary DBs. Existing mock sentinel byte-for-byte preserved, no import.
Criterion7: PASS — actual commands below. Root contract/CSS/authored curriculum/mockService have empty diff from cca5255 baseline. README/AGENTS/env/API mapping reviewed. git diff --check and clean status pass; HEAD and origin/main both 45574230a5c82b13a859454226fd3887561db401. Previews5173/8000 were left running. PM/engineer handoff revision published; no secrets/DB files tracked.
Criterion8: PASS — independent actual checks and this verdict; observed defects#21/#22 PM-refined, engineer fixed, independent regressions/browser verification passed. QA closes only after this PASS; final audit#18 remains unperformed/out of scope.

Commands/results independently executed:
- pnpm --dir frontend test:27passed including real Auth event-lifecycle and obsolete startup failure regressions; original mock tests retained.
- pnpm --dir frontend typecheck; build; check:bundle; contrast:allPASS (26contrast combinations).
- /tmp/wecode-backend-venv/bin/python -m pytest backend/tests -q:162passed, one upstream Starlette/AnyIO deprecation warning.
- /tmp/wecode-backend-venv/bin/openapi-spec-validator openapi.yml:OK.
- NODE_BIN=bundledNode /tmp/wecode-backend-venv/bin/python tools/contract/validate.py:PASS348localreference/409example occurrences,12method AST coverage,9units27exercises,26negative checks.
- python3 backend/scripts/sync_curriculum.py:PASS exact existing curriculum/rules.
- node frontend/scripts/check-integration.cjs:PASS55real network responses, restart/offline/isolation/expiry/mobile.
- node /tmp/qa17-extra.cjs and /tmp/qa17-levels.cjs:independent additional mobile/keyboard/post-expiry-login and per-track preference regressions PASS58/64 responses.
- node /tmp/qa17-mock.cjs:explicit development mock UI PASS with zero API requests.
- git diff --check:PASS; git status --short:empty; origin/main==HEAD==45574230a5c82b13a859454226fd3887561db401.

Evidence: independent screenshots/redacted method/path/status traffic in /tmp/wecode-independent-qa17, /tmp/wecode-independent-qa17-extra and /tmp/wecode-independent-qa17-levels; own mobile auth/dashboard/lesson screenshots /tmp/qa17-mobile-*.png. Temporary scripts extend browser assertions only and never modify application code or normal project DB/profile. No credentials printed.
Failures/unverified checks:none within#17 scope. Disposition:QA closes after PASS. This is integration verification, not final submission audit.

## Observed login bug verdict

QA: PASS
Issue:#21; revision:45574230a5c82b13a859454226fd3887561db401; independent QA environment:real isolated Chrome→Vite→FastAPI→temporary SQLite; October19,2026.
Criterion1:PASS — reviewed authenticate():anonymous form is not invalidated/remounted; existing credential replacement clears private session; pending previous-account response rejected by generation.
Criterion2:PASS — independent browser unknown-user login returns401 and retains Welcome back/error, duplicate registration409 remains signup with safe alert. Existing tests cover network failure/validation and no raw debug disclosure.
Criterion3:PASS — independently reran27frontendtests including real Auth+App lifecycle and pending old-account regression. Own additional actual-browser invalid/expired→fresh login and preserved progress checks passed;64real responses. Independent explicit mock UI remains functional.
Criterion4:PASS — reviewed same published revision as#17; QA records verdict and closes.
Commands:pnpm --dir frontend test(27PASS); node frontend/scripts/check-integration.cjs(55responsesPASS); node /tmp/qa17-levels.cjs(64responsesPASS). No application code changed by QA.
Failures/unverified:none. Disposition:QA closes after PASS; parent#17 evidence contains full independent results.

## Observed session race verdict

QA: PASS
Issue:#22; revision:45574230a5c82b13a859454226fd3887561db401; independent QA environment:real isolated Chrome/React StrictMode→Vite→FastAPI→temporary SQLite; October19,2026.
Criterion1:PASS — reviewed sessionGeneration checks in startup/refresh and invalidation clearing pending/error/learner/snapshot. Obsolete responses cannot replace current authentication state; adapter rejects old-account responses.
Criterion2:PASS — independent browser invalid future-expiry token and locally expired credential reload both cleared sessionStorage and returned authentication. Own additional successful fresh login after these states restored original exact saved snapshot (also after real processrestart), no stale startup error screen. Logout and second-account isolation passed.
Criterion3:PASS —27frontendtests independently rerun, including overlapping obsolete startup rejection regression; own browser extension adds post-invalidation successful login assertion and mobile checks.55/64actual responses PASS. QA records actual evidence and alone closes.
Commands:pnpm --dir frontend test(27PASS); node frontend/scripts/check-integration.cjs(55PASS); node /tmp/qa17-levels.cjs(64PASS). No application code changed by QA.
Failures/unverified:none. Disposition:QA closes after PASS; parent#17 evidence contains full independent results.

## Reproduction and stage boundary

The repeatable full browser harness is [check-integration.cjs](../../frontend/scripts/check-integration.cjs); setup, tooling paths and normal app commands are in [README](../../README.md#run-the-complete-app-locally). It creates its own isolated real browser and temporary frontend/backend/database processes, tests actual HTTP requests and stops/restarts the backend with the same temporary DB. It never clears existing user browser records or deletes the normal project database. Independent additional temporary scripts were regression assertions layered onto that harness; their actual commands/results are recorded above.

Screenshot/traffic artifacts remain local verification output. Traffic records contain only method/path/status, without credentials. Normal previews remain at http://127.0.0.1:5173/ and http://127.0.0.1:8000/docs using ignored project data/wecode.sqlite3. This final documentation commit changes no reviewed application code. No SQLite data/real secrets are committed.

All required integration checks passed; no integration blockers remain. The final submission audit, missing original planning transcript and actual submission are not certified by this integration PASS. [Issue #18](https://github.com/240103097-jpg/WeCode/issues/18) remains the next separate stage.
