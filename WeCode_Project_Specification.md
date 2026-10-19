# WeCode — Project Specification and Brainstorming Record

Date: 19 October 2026. Submission target: 20 October 2026 (Asia/Almaty); exact submission time unknown.
Status: frontend-stage specification. The original brainstorming summary below is preserved. Current owner decisions and delegated defaults are recorded in docs/decisions.md and supersede earlier proposals. Backend behavior remains a later-stage requirement.

## 1. Goal and audience

WeCode is an English-language application for learning programming and improving IT skills through lessons and practice. Learners choose Python, SQL or Git and select their experience level. The project is individual and, according to the user, differs from Part I.

## 2. Confirmed MVP scope

- Registration and login.
- Python, SQL and Git learning tracks.
- Beginner, Intermediate and Advanced levels, separately stored for each track and editable later.
- Short lessons with explanations and examples.
- Quiz: choose an answer.
- Fix the Bug: correct a targeted fragment.
- Complete the Code: fill a missing fragment.
- Results and explanatory feedback after submission.
- Repeated attempts, hints after an incorrect attempt and a separate Show Solution action.
- Saved learning progress and attempt results.
- English interface and educational content.

## 3. Selected frontend rules

Owner-confirmed target: 9 short units (one per track/level), with one lesson and three exercise types each: 27 exercises. Marking the lesson read and correctly submitting all three exercises completes a unit. Assisted work counts toward completion but is labeled separately from independent work. Retries do not duplicate credit; there is no XP/scoring.

Hints follow an incorrect answer; Show Solution is a separate action. Answer checking uses authored rules and never executes learner code. Detailed normalization, history, progress formulas and explicitly delegated mock authentication defaults are in [docs/decisions.md](docs/decisions.md). Design is selected under owner delegation in [docs/design-system.md](docs/design-system.md).

## 4. Screens

Proposed screens: sign up, sign in, track/level onboarding, dashboard, learning path, lesson and practice, progress/profile. Loading, empty, invalid input and server-error states should be visible and recoverable. Use a coherent design reference or a design tool as required by the assignment.

## 5. Acceptance criteria

- A learner can register, log in and log out; duplicate accounts and invalid credentials show useful errors.
- One learner cannot access another learner's private attempts or progress.
- Track and level choices survive page reload and backend restart.
- All three tracks and levels expose the advertised initial content; unfinished content is not presented as complete.
- Each exercise type supports correct and incorrect submissions with relevant feedback.
- Wrong answers allow retries and hints; Show Solution is a separate action.
- Attempts and assisted status persist, and repeated submissions do not duplicate completion credit.
- Track switching and level changes do not erase history.
- The progress display matches its documented formula.
- Database data remains available after a backend restart.
- User-facing text and authored learning content are in English.
- Tests and manual checks have recorded actual results; no unexecuted check is labeled passed.

## 6. Technical approach and assignment process

Selected direction: React/TypeScript with Vite frontend; Python/FastAPI backend; SQLAlchemy ORM and SQLite for later stages. Only the frontend with mockService is authorized in this stage. All frontend backend access goes through a service layer. Configure database connection through an environment variable; avoid unnecessary database-specific behavior.

Follow the assignment's iteration order:
1. Interactive frontend using mockService.
2. Root openapi.yml describing API requests, responses and authentication.
3. Backend implementing that contract with an in-memory store.
4. Replace in-memory storage with SQLite through an ORM.
5. Connect the frontend to the real backend and test end to end.

Use GitHub Issues as the active backlog with mvp, post-mvp and user-test-bug labels. PM refines each issue with Goal, Acceptance criteria, Out of scope and Constraints. Engineer implements it and records actual checks. QA independently checks each criterion and records PASS or FAIL; failed work returns for correction. Follow the assignment's requirement that only QA closes issues after PASS, including completed mvp and user-test-bug issues. Save agent instructions and evolving Markdown documentation in the repository. This specification itself does not implement the application. Repository setup and the canonical issue backlog are documented in README.md and docs/planning.md.

## 7. Proposed post-MVP scope

- Arbitrary code execution with an appropriately isolated runner.
- AI tutor and open-ended AI feedback.
- Larger curriculum, extended practical missions and project submissions.
- Additional languages and learning tracks.

## 8. Verification plan

Check registration, login, authorization boundaries, all exercise types, normalization edge cases, retries, hints, solution reveals, progress calculation, track/level switching and persistence after restart. Exercise the actual UI and record reproduction steps for defects. File real discovered defects with user-test-bug; do not invent bugs to populate the tracker.

## 9. Brainstorming record

This is an honest summary of the visible discussion, not a verbatim full chat export. The full original planning transcript still needs to be added for the assignment. The original transcript is not available in this checkout; the owner must supply a genuine export. Do not reconstruct or fabricate missing conversation.

1. The user requested that the assignment be divided into steps and completed gradually.
2. Several unrelated app ideas were discussed and rejected.
3. The user chose an application that teaches programming and improves IT skills.
4. Lessons, exercises and practical tasks were discussed, including Python, SQL and Git. The user's response was “все”; the assistant proposed including all three tracks.
5. The user confirmed individual work, completion by tomorrow, and that the idea differs from Part I.
6. The user selected English for the application.
7. The user requested choosing an experience level after registration: beginner, medium and good. English labels Beginner, Intermediate and Advanced were proposed.
8. The user accepted a separate editable level for each learning track.
9. The user accepted Quiz, Fix the Bug and Complete the Code.
10. The user accepted repeat attempts, hints and Show Solution.
11. The assistant initially suggested DevQuest as a working name. The user explicitly named the application WeCode; that is the current name.
12. The user agreed to proceed to documentation. Detailed content counts, completion rules, scoring, technology selection and design remain proposed implementation decisions.

## 10. Sources and precedence

- Primary product decisions: the visible conversation with the user on 19 October 2026.
- Assignment: supplied screenshot, “Снимок экрана 2026-10-19 в 14.51.59.png”.
- Process reference: https://aishippingblog.com/p/ai-native-development-specifications
- Build reference: https://aishippingblog.com/p/build-and-ship-a-full-stack-app-with

The user's assignment takes precedence where its integration sequence or issue-closing responsibility differs from the articles. This specification does not assert market demand, uniqueness or implementation completion.
