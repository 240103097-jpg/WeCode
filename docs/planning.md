# Planning record

Reviewed October 19, 2026 (Asia/Almaty). Delivery target is October 20, 2026; exact submission time is unknown. This checkout started empty with an unborn main branch. Existing remote main was fetched before editing; its specification and brainstorming summary were preserved. There were no existing AGENTS.md files or GitHub Issues at inspection. No application code or dependencies were added.

## Original planning-stage decisions (historical)

- Owner selection of stack and test/toolchain choices. Current proposal: React/TypeScript, Python/FastAPI, SQLAlchemy, SQLite. SQLite through an ORM is required by the assignment; specific frameworks remain proposed.
- Owner selection of a coherent design reference/tool result, visual tokens, layout and accessibility baseline.
- Initial curriculum inventory per track/level; the specification's 9 units and 27 exercises are proposals.
- Scoring or no points; completion formula and lesson-read action; assisted credit, solution reveal effects, retry/repeated-submission credit and hint timing.
- Exercise-specific answer normalization and acceptable variants; level-change and track-switch history behavior.
- Session/authentication policy, frontend mock reload behavior and contract details during PM refinement.
- Genuine full original planning transcript/export from the owner. The existing brainstorming record is a summary, not a verbatim chat export; no missing conversation was fabricated.
- Exact submission time and final submission instructions.

Product decisions require owner confirmation and a specification update linked from the affected issue. Proposed screens and behavior in specification sections 3–5 must be refined against those decisions; no proposed count or formula is an accepted requirement merely because it appears in acceptance examples.

## Source review and precedence

Both requested articles were accessible and read during planning:

- [AI-Native Development: Specifications, Loop and Graph Engineering](https://aishippingblog.com/p/ai-native-development-specifications): informs specification-first work, small GitHub tasks with explicit criteria, contextual agent documents and independent PM/engineer/QA handoffs. GitHub Issues become the canonical active backlog. We do not install an orchestrator or start a development loop during planning. The assignment overrides the article's orchestrator closure: **only QA closes after PASS**.
- [Build and Ship a Full-Stack App with AI Coding Assistants](https://aishippingblog.com/p/build-and-ship-a-full-stack-app-with): informs an interactive mocked frontend, centralized service boundary and explicit API contract. The assignment overrides early frontend/backend integration: finish in-memory backend, then ORM/SQLite, then connect UI and thoroughly test. Use the required filename `openapi.yml`, retain it under version control, and do not adopt the example stack as an owner decision.

The referenced assignment screenshot and original conversation export are not present in this checkout. This plan uses the assignment requirements supplied directly in the current request and preserves the specification's provenance statements without claiming independent inspection of those missing artifacts.

## Backlog and publication

[GitHub Issues](https://github.com/240103097-jpg/WeCode/issues) are the canonical active backlog. Decision tasks block dependent implementation; stage gates enforce the required sequence. No local active backlog is maintained. Labels distinguish MVP, post-MVP and actual observed user-test defects. No bugs were observed or invented during this documentation stage.

Role documents are instructions for agents, not executable programs. Planning completion does not constitute implementation QA or close any newly created issue. The next step is PM refinement and owner selection of stack, design and product rules before frontend work is authorized.

Publication verified: 19 open issues, each with Goal, Acceptance criteria, Out of scope and Constraints. All three requested labels exist. Decision entry points: [stack](https://github.com/240103097-jpg/WeCode/issues/1), [design](https://github.com/240103097-jpg/WeCode/issues/2), [product rules](https://github.com/240103097-jpg/WeCode/issues/3), and [original transcript](https://github.com/240103097-jpg/WeCode/issues/4). Consult GitHub for current status and dependencies; this is a publication record, not an active local backlog.

## Frontend-stage update

The owner has now selected React/TypeScript/Vite and later Python/FastAPI/SQLAlchemy/SQLite, delegated detailed dark yellow/green visual design, confirmed 9 units/27 exercises and completion with assisted work, and authorized explicit implementation defaults. See [current decisions](decisions.md) and [design references](design-system.md). Earlier unselected items above are historical, not current blockers. Genuine original transcript and exact submission time remain missing. No OpenAPI/backend/SQLite implementation is authorized in the frontend stage.

## Original-material follow-up

The owner subsequently supplied the actual assignment screenshot and a genuine ten-message manual partial ChatGPT copy. See [partial transcript](brainstorming-transcript.md) and [actual screenshot comparison](submission-checklist.md#actual-assignment-screenshot-comparison). Earlier absence statements above describe the historical planning inspection. The screenshot does not mandate automated export or explicitly say full transcript; the later owner-authorized [PM reconciliation](requirements-reconciliation.md) explicitly corrects that former extra gate to substantive genuine brainstorming evidence with honest partial scope. #4/#18 subsequently passed independent source-aligned QA and closed. No missing wording is reconstructed.
