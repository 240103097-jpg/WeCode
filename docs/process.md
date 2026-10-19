# Development process

GitHub Issues are the canonical active backlog. Work on one focused issue at a time; dependency links identify blockers. `mvp` marks required delivery work, `post-mvp` deferred work, and `user-test-bug` an observed user-test defect. Search open and closed issues before filing. No local document is a competing active backlog.

## Lifecycle

1. PM follows [PM instructions](team/pm.md), refines the four required issue sections, obtains owner decisions where needed, and records dependencies and readiness in an issue comment.
2. Engineer follows [engineer instructions](team/software-engineer.md), implements the acceptance criteria and meaningful tests, commits, and hands off the exact revision and evidence. The issue stays open.
3. Independent QA follows [QA instructions](team/qa-engineer.md), checks every criterion and records PASS or FAIL with actual evidence.
4. Any failed or unverified criterion means FAIL. Return the issue to the engineer with reproduction steps. After correction, QA checks every criterion again at the new revision.
5. **Only QA closes the issue after PASS**, as the assignment requires. PM, engineer and coordinator do not close it. Do not use GitHub automatic issue-closing keywords. If QA cannot close it due to permissions, leave it open and report the blocker.

The roles are agent instructions, not executable programs or an installed orchestration system. For this individual project, independence means a different reviewer/session than the implementer. A coordinator may arrange handoffs but does not replace QA's verdict or closure authority.

## Stage gates

Planning decisions precede dependent work. All frontend issues must pass before the root `openapi.yml` contract; the contract passes before the in-memory backend; backend passes before ORM/SQLite persistence; persistence passes before live frontend/backend integration and final testing. Earlier backend tests may call the API directly without connecting the UI. Preserve and maintain the root contract through later stages.

Changes to criteria return to PM for explicit refinement; engineers must not weaken criteria to pass tests. Record owner decisions in the specification and link them from affected issues. Split oversized tasks and link follow-ups under Out of scope. Resolve deadline or scope risks with the owner; the October 20 submission time is unknown.

## QA evidence format

```text
QA: PASS or FAIL
Issue: #number; revision: full commit hash; environment: ...
Criterion 1: PASS/FAIL — steps and observed result
(repeat for every criterion)
Commands and actual results: ...
Manual checks and evidence: ...
Failures/unverified checks and reproduction: ...
Disposition: return to engineer / QA closes after PASS
```
