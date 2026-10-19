# WeCode demonstration guide

Technical demo verified October 19, 2026. **Submission readiness remains blocked by incomplete original planning history (#4; partial manual copy supplied); #18 is not a submission certificate.** Never demonstrate with an existing learner's credentials/data or delete a database to reset the demo.

## Start the complete app

From repository root (Python 3.13, Node22.12+ and pnpm11.25+):

```sh
python3 -m venv /tmp/wecode-demo-venv
/tmp/wecode-demo-venv/bin/python -m pip install -r backend/requirements-dev.txt
/tmp/wecode-demo-venv/bin/python backend/scripts/prepare_local.py
export DATABASE_URL="sqlite:///$PWD/data/wecode.sqlite3"
/tmp/wecode-demo-venv/bin/python -m uvicorn backend.wecode.app:create_app --factory --host 127.0.0.1 --port 8000 --workers 1 --no-access-log
```

Second shell, repository root:

```sh
pnpm --dir frontend install --frozen-lockfile
pnpm --dir frontend dev
```

Use [frontend](http://127.0.0.1:5173/) and [API docs](http://127.0.0.1:8000/docs). If these previews already run, use them rather than starting duplicate servers. Project data/wecode.sqlite3 is persistent/ignored; prepare_local creates missing schema/content without resetting it. Environment options/runtime fallback path are in [README](../README.md#run-the-complete-app-locally).

## Short manual sequence

1. Register a fresh made-up demo email with a private password of12–128 characters. Real and browser-mock accounts are separate; no imports occur.
2. Select Python/Beginner and open the first lesson. Read it, then Mark lesson as read.
3. Quiz: choose23 (wrong), request hint, then choose5. Observe explanatory feedback and independent solve.
4. Fix the Bug: enter `age + 1` (wrong), then Show Solution. Submit `int(age) + 1`; observe Correct · assisted.
5. Complete the Code: submit `echo` (wrong), then `print`. Submit correctly again. Progress shows one completed unit, two independent exercises and seven attempts, not extra completion credit.
6. Change SQL to Advanced and Git to Intermediate in Settings/Learning Paths, then return to Python. History remains. Reload and check saved state.
7. Stop only the backend process you started (Ctrl-C), restart with the same DATABASE_URL and verify state/login again. Do not delete/reinitialize the DB as a reset.
8. Sign out/in, then create a second fresh account; it starts empty. Sign out clears private client state.
9. For outage recovery, stop your backend, reload the frontend, observe visible error with no mock fallback. Restart and choose Retry. At320px/375px inspect Menu, lesson, Progress and Settings; titles/status rows remain separate. Desktop layout retains retro panels/focus.

Do not record or publish passwords/tokens. If a write is interrupted, Refresh workspace before another submission because it may have saved. To avoid touching the normal DB at all, use the automated isolated demo below.

## Repeatable isolated full demo/audit

```sh
BACKEND_PYTHON=/tmp/wecode-demo-venv/bin/python WECODE_AUDIT_ALL_UNITS=1 node frontend/scripts/check-integration.cjs
```

This verified harness launches its own real Chrome/Vite/FastAPI, isolated ports and temporary SQLite, checks all nine track/level units and all27 exercises, restart/isolation/offline recovery and mobile geometry, then stops its own processes and removes its own temporary DB. It preserves existing previews/browser/mock records. Playwright/Chrome setup and optional PLAYWRIGHT_MODULE/CHROME_BIN/BROWSER_ARTIFACT_DIR overrides are documented in README. No credential is printed. See [actual final-audit results](qa/final-audit.md).
