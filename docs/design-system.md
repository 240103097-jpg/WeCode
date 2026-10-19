# WeCode design system

Selected October 19, 2026 under owner-delegated visual design. Direction: a quiet programming workspace, warm yellow for the primary action, green for confirmed success, readable content and useful progress only.

## Inspected public references

- [freeCodeCamp curriculum](https://www.freecodecamp.org/learn): inspected in Chrome, including its visible curriculum page on October 19. Its centered, plainly titled curriculum and stacked full-width learning rows inform WeCode's Learning Paths and practice index. WeCode adds the requested Continue Learning area and actual learner progress; no private dashboard or statistics were inspected/copied.
- [VS Code user interface](https://code.visualstudio.com/docs/editing/getting-started/userinterface): inspected in Chrome, including Basic layout and the visible editor illustration. A persistent left context sidebar, clear active view and split content/editor regions inform the desktop shell and lesson/exercise workspace. On mobile the split stacks vertically and navigation collapses into a labeled menu.
- Exercism /dashboard redirected to sign-in; its private dashboard was inaccessible and is not a design source. Initial text-fetch attempts for freeCodeCamp and VS Code were empty/timed out, then the public pages were successfully inspected visually in Chrome.

These are references for general layout patterns only. No screenshots, logos, code, text or other third-party assets are redistributed. WeCode's layout, CSS and curriculum are authored independently. Public reference inspection satisfies the reference requirement without implying permission to reuse protected assets.

## Owner-selected retro computing reference

The owner supplied `codex-clipboard-b91ef10d-8811-485c-9169-d93c9f661faf.png` directly in chat on October 19, 2026. The image was visually inspected at its supplied local attachment path. **No public source URL was supplied or invented.** The earlier missing-image blocker is resolved. The reference itself is not bundled or republished in the application.

Concrete patterns adopted from the image: near-black navy canvas; thin, square green frames over a faint graph grid; blocky short display headings; small square corner/number markers; right-angle route connectors; aligned rectangular panels; segmented bars. WeCode translates these into learning tracks, unit states, real completion fractions and a focused lesson/practice workspace. The reference's wording, branding, account handle, game rules, rewards and financial content are not copied.

The original freeCodeCamp/VS Code references above remain background for functional learning/navigation patterns. This owner-selected image supersedes the earlier rounded olive visual system.

## Tokens and contrast

| Token | Value | Use |
| --- | --- | --- |
| Background | #080B15 | Canvas, code blocks and filled-button ink |
| Surface | #101622 | Solid lesson, exercise and form panels |
| Elevated | #182231 | Secondary controls |
| Text | #EFF3EA | Main copy |
| Muted | #ADB6AA | Secondary copy, placeholders, metadata |
| Primary/current | #F4D35E | Primary actions, current learning position, keyboard focus |
| Complete/success | #59F54A | Completed nodes, filled progress cells, correct feedback |
| Error | #FFB4A6 | Invalid input and incorrect feedback |
| Structural line | #36563F | Quiet panel frames and connecting rails |
| Control boundary | #708D75 | Interactive control outlines and empty progress cells |

Structural frames are not the only indicator of an interactive control. Form/radio/control boundaries use the brighter control token. Selected/current and completed states have visible text and semantic attributes in addition to color. Disabled controls use #C2C9BD on #263044 instead of faded opacity, preserving readable text. Dark #080B15 text on yellow/green fills preserves contrast. Keyboard focus is a 3px yellow outline with 4px offset; radio groups expose the visible parent focus ring.

Measured results: main text on background/surface/elevated = 17.47/16.10/14.24:1; muted = 9.40/8.66/7.66:1; dark ink on yellow/green = 13.40/13.64:1; control outlines = 5.38/4.96/4.39:1. Selected muted = 7.35:1; disabled text = 7.79:1; yellow focus on hover = 8.58:1.

Run `pnpm contrast` in frontend/ for actual token/state calculations: normal text minimum 4.5:1; control boundaries/focus minimum 3:1. The script reads current CSS tokens and checks main/muted/feedback/accent text against all solid backgrounds plus selected, hover and disabled states. Decorative grid lines use green at 4.5% opacity with 24px spacing; sustained reading uses solid surfaces.

## Typography and assets

Short identity/page headings, track names and numbers use locally bundled **Silkscreen Regular**, with Courier New/ui-monospace/monospace fallbacks and font-display: swap. [Font source](https://github.com/google/fonts/tree/main/ofl/silkscreen), [retained SIL Open Font License](../frontend/src/assets/fonts/OFL.txt). The font is bundled with the app, so no external font request or runtime dependency is required. No source image assets are copied.

Long lesson titles, explanations, form headings and body text use system sans-serif at 15–16px and 1.65–1.85 line-height. Code uses ui-monospace/SFMono-Regular/Menlo/Consolas. Long paragraphs never use a pixel font. Code blocks scroll internally, and solution/attempt fragments wrap when appropriate.

## Composition and states

- Desktop: 232px sidebar, solid navigation, numbered views, main content with deliberate spacing and a faint canvas grid. Overview has a large WeCode identity/concise learning headline, one yellow-framed Continue Learning section, actual totals and numbered Python/SQL/Git track panels.
- Segmented bars retain semantic progressbar labels and exact saved value/max. Each unit/step contributes four visual cells; these show an aggregate fraction, not a claim that a particular ordered unit was completed. Completion fills green; no invented activity or XP.
- Learning Paths: three numbered track sections, each with an angular connecting rail and three numbered lesson nodes. Complete nodes are green; the Continue Learning unit has yellow frame and aria-current=step. This follows the existing resume choice: selected track/level unless complete, then the next incomplete unit in that track; if the track is complete it marks the selected review unit. Other nodes say Available. Every node remains linked; no locks or new learning rules.
- Lessons: solid, readable lesson beside the focused exercise panel, square tabs/radio/text controls, green correct feedback and clear incorrect feedback; hints/retries/Show Solution preserve existing behavior and assistance semantics.
- Authentication, onboarding, progress and settings use the same square frames, typography hierarchy, palette and focus treatment. The mock authentication explanation and flow remain unchanged.
- Below 1100px, the lesson workspace stacks; below 900px, track cards stack; below 700px, the sidebar becomes an expandable labeled mobile menu. Layout must remain usable at 320px without horizontal page overflow. Long code can scroll inside its own panel.

Corners are square. Spacing uses 4/8/12/16/24/32/40/48px. There is no glow, flicker, animated background, fake terminal output or pill-heavy decoration. The static grid is structural, not a moving background; transitions respect reduced motion. All UI and curriculum remain English.

## Preservation and verification

Issue #20 is visual-only: curriculum, service interface, mockService, authentication handlers/flow and storage schema/key/records stay unchanged. Independent QA captures an existing account's visible baseline before edits, reruns behavior tests/typecheck/build and checks saved progress after redesign/reload. Browser coverage includes dashboard, angular learning paths, lesson/practice, authentication, onboarding, progress and settings on desktop/mobile, focus, navigation and page overflow. QA alone closes the issue after PASS.
