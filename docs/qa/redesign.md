# Retro visual redesign verification — issue #20

Date: October 19, 2026, Asia/Almaty. Scope: frontend visual redesign only. [Issue #20](https://github.com/240103097-jpg/WeCode/issues/20) remains the canonical task and QA verdict location.

## Reference and baseline

The owner-supplied image `codex-clipboard-b91ef10d-8811-485c-9169-d93c9f661faf.png` was inspected locally. No public source URL was supplied/invented, no source image assets were republished, and its branding/wording/game/financial content was not copied. Concrete reference patterns and selected tokens are in [the design system](../design-system.md).

Independent QA captured the existing mock learner before app edits at baseline 84d3fa0: display name QA Verified, active Git Advanced; levels Python Beginner, SQL Advanced, Git Advanced; 1/9 units complete (11%), Python 1/3 (33%), SQL/Git 0/3; 2/27 independently solved; 2 solution views; 13 saved submissions; Python Beginner complete with 2/3 independent exercises. Only normal session sign-in/out was used; no storage clearing, progress or profile mutation.

## Engineer checks at 71abf99

Environment: macOS, bundled Node 24.19.0, pnpm 11.25.0, Chrome.

- `pnpm --dir frontend contrast`: PASS, 26 text/control/state combinations. Muted on background/surface/elevated: 9.40/8.66/7.66:1; selected muted 7.35:1; disabled text 7.79:1; filled-button dark ink >13:1; control boundary minimum 4.39:1. The check reads actual CSS tokens.
- `pnpm --dir frontend typecheck`: PASS.
- `pnpm --dir frontend test`: PASS, 19/19 across five files. Original 16 behavior tests retained; three additions check all-level accessibility/current-vs-completed distinction, real semantic progress values and Continue Learning/path current-position consistency.
- `pnpm --dir frontend build`: PASS, including the local display font asset. No new application dependencies or runtime font network requests.
- `git diff --check`: PASS; 25 relative Markdown targets checked, zero broken.
- Source preservation diff against baseline: services/types/mockService, curriculum, Auth/TrackPreferences/Workspace/Settings handlers unchanged. No backend/OpenAPI/SQLite changes.
- Parent Chrome inspection: desktop dashboard, angular paths, mobile 320px lesson and Fix the Bug panel. Mobile lesson document clientWidth = scrollWidth = 320; internal code scrolling allowed. Viewport restored afterward.

## Independent QA verdict

**PASS** at 71abf9994b4945878b3c1759f131970100f301d4. The separate QA agent recorded all eight criteria and closed [issue #20 after PASS](https://github.com/240103097-jpg/WeCode/issues/20#issuecomment-6266352473).

QA independently reran all 19 tests, typecheck/build and 26 contrast checks. Browser checks covered desktop and 320px mobile dashboard, learning paths, progress, settings, authentication, onboarding and lesson/practice. Keyboard Menu/Tab/Enter navigation and visible focus worked; the local display font loaded; inspected pages had no horizontal overflow, with code scrolling internally as needed.

The original learner's name, active track, all three level choices, 1/9 unit completion, 2 independent solves, 2 solution views and 13 saved submissions remained unchanged after redesign and reload. QA exercised wrong/correct answers, hints, retries, separate solution reveal and text submissions on a separate disposable mock account, preserving the original records. Source comparison confirmed no service/curriculum/authentication/storage handler changes. No defects were observed, so no user-test-bug issues were invented.

QA restored normal viewport and the original learner session on Overview. No backend/OpenAPI/SQLite stage work was started.

## Preview

The pre-existing Vite development server stays running at http://127.0.0.1:5173/ as explicitly requested. Local mock data is browser-specific and is neither erased nor seeded by this redesign.
