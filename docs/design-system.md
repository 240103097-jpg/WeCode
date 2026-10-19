# WeCode design system

Selected October 19, 2026 under owner-delegated visual design. Direction: a quiet programming workspace, warm yellow for the primary action, green for confirmed success, readable content and useful progress only.

## Inspected public references

- [freeCodeCamp curriculum](https://www.freecodecamp.org/learn): inspected in Chrome, including its visible curriculum page on October 19. Its centered, plainly titled curriculum and stacked full-width learning rows inform WeCode's Learning Paths and practice index. WeCode adds the requested Continue Learning area and actual learner progress; no private dashboard or statistics were inspected/copied.
- [VS Code user interface](https://code.visualstudio.com/docs/editing/getting-started/userinterface): inspected in Chrome, including Basic layout and the visible editor illustration. A persistent left context sidebar, clear active view and split content/editor regions inform the desktop shell and lesson/exercise workspace. On mobile the split stacks vertically and navigation collapses into a labeled menu.
- Exercism /dashboard redirected to sign-in; its private dashboard was inaccessible and is not a design source. Initial text-fetch attempts for freeCodeCamp and VS Code were empty/timed out, then the public pages were successfully inspected visually in Chrome.

These are references for general layout patterns only. No screenshots, logos, code, text or other third-party assets are redistributed. WeCode's layout, CSS and curriculum are authored independently. Public reference inspection satisfies the reference requirement without implying permission to reuse protected assets.

## Tokens and contrast

| Token | Value | Use |
| --- | --- | --- |
| Background | #101210 | App canvas and button ink |
| Surface | #1A1E19 | Sidebar and panels |
| Elevated | #242A23 | Inputs and secondary regions |
| Text | #F2F4ED | Main copy |
| Muted | #AAB3A5 | Secondary copy |
| Primary | #F4D35E | Main actions and focus |
| Success | #8DDB80 | Correct outcomes |
| Error | #FFB4A6 | Invalid input and failure copy |

Use dark #101210 text on yellow/green filled buttons. Calculate WCAG contrast with the repository contrast check; normal text needs 4.5:1. Borders are restrained separators, not the sole indication of interactive state; form controls get a brighter outline. Success/error always include words. Focus is a visible yellow outline with offset.

## Layout and type

Desktop sidebar 228px; main width up to 1280px, 40px padding. Header gives page context and profile. Overview has one prominent Continue Learning panel with a small code excerpt, three concise track summaries, and real checklist/progress. Learning paths and progress favor rows over repetitive grids. Lessons use a readable 60–70 character text column beside a focused exercise panel. Below 1100px stack the workspace; below 700px replace sidebar with an expandable labeled navigation menu. Maintain usable 320px width and allow code blocks to scroll locally.

System sans-serif for UI; ui-monospace/SFMono-Regular/Menlo for code. Body 16px, line-height 1.6; page headings 32–44px. Spacing scale 4/8/12/16/24/32/40/56px, corners 8–16px. No gradients, glow, decorative achievements, fake activity or XP. Transitions are subtle and respect reduced motion.

Every route and action must work. Empty progress is honest. Auth screens label local mock accounts and the public demo passphrase. Pending actions disable repeat submission and announce loading. Validation/recoverable failures use accessible alerts and Retry. Hints appear after an incorrect submission; Show Solution is a separate button and assisted work remains labeled. See [defaults](decisions.md) for exact completion semantics.

Independent QA contrast calculation at decision review: main text on background/surface/elevated = 16.97/15.23/13.24:1; muted = 8.69/7.80/6.78:1; dark ink on yellow = 12.84:1, on green = 11.27:1. All pass 4.5:1 without token adjustment.
