# Curriculum review

The frontend ships nine authored units and 27 exercises. Each unit has two short lesson sections, an example, a takeaway and one exercise of each type. Keys/hints/explanations stay in mock data, outside UI components and normal service content responses. The mock bundle necessarily contains answer keys; this is not anti-cheat enforcement.

| Track | Beginner | Intermediate | Advanced |
| --- | --- | --- | --- |
| Python | Values, numeric conversion, print | Filtering comprehensions and return values | Generator suspension, consumption and next |
| SQL | Projection and inclusive row filters | Aggregation, HAVING, COUNT NULL semantics | Window partitions, deterministic row numbering, running frames |
| Git | Working tree/index/commit | Branch creation and merge destination | Reverting shared ordinary commits vs unstaging |

## Accuracy review

The examples are independently authored. Review distinguishes Python input strings from integers; comprehension filters from transformations; print from return; generator consumption from reusable collections. SQL uses SQLite-compatible syntax, explicit table schemas, deterministic unique-id ordering and explicit ROWS frames. Git examples specify current branch, ordinary non-merge commits and index vs working-tree effects. No command or learner program is executed by the app.

Primary references read during content preparation:

- [Python data structures](https://docs.python.org/3/tutorial/datastructures.html): comprehension and list behavior.
- [SQLite SELECT](https://www.sqlite.org/lang_select.html): grouping, filters and window behavior.
- [Git restore](https://git-scm.com/docs/git-restore): index/working-tree targets and default sources.

Each exercise has authored positive and negative examples; checking trims surrounding whitespace and normalizes CRLF only. SQL explicitly allows all-lowercase/all-uppercase versions of the authored fragment, not all possible equivalent queries. Prompts constrain exact replacement fragments and explain restricted checking. Tests verify inventory, unique IDs/types, feedback and keys, plus behavioral submissions through the service.
