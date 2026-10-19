# OpenAPI contract verification — issue #11

Date: October 19, 2026, Asia/Almaty. Scope: contract and documentation only.

## Reviewed revision and verdict

Independent QA **PASS** at `ad6837ebaabc0751447012a34a5695cbb3d02c17`. The separate QA agent recorded all eight criteria and [closed issue #11 after PASS](https://github.com/240103097-jpg/WeCode/issues/11#issuecomment-6270911604). QA independently verified that the exact revision was published using `git ls-remote`.

## Actual checks

Environment: macOS, Python 3.13, isolated `/tmp/wecode-openapi-venv`, bundled Node 24.19.0 and the existing frontend TypeScript dependency. Reproducible setup is in [README](../../README.md#api-contract-validation); pinned validator dependencies are in [requirements.txt](../../tools/contract/requirements.txt).

```sh
/tmp/wecode-openapi-venv/bin/openapi-spec-validator openapi.yml
/tmp/wecode-openapi-venv/bin/python tools/contract/validate.py
```

Both engineer and independent QA ran these commands successfully. Results:

- OpenAPI 3.0.3 specification validation: PASS.
- 348 local reference occurrences resolved; no unresolved, external or cyclic references.
- 409 schema/media/parameter/header example occurrences validated, including formats. These are occurrences across reused schemas, not 409 unique examples.
- Actual TypeScript AST and service consumer coverage: 12 methods, comprising 11 HTTP operations and one mock-only failure simulation; eight interface declarations reviewed.
- Actual nine-unit, 27-exercise payload coverage, secret-field exclusion and example completion semantics: PASS.
- 26 negative schema checks covering answer-key leakage, impersonation fields, invalid enums/formats/state and invalid payloads: PASS.
- QA checked all 31 relative Markdown targets present at the reviewed revision; `git diff --check` passed.
- `git diff 5b3c407b7c36daaa0a43acb4a92dd8fccfc1afdc ad6837ebaabc0751447012a34a5695cbb3d02c17 -- frontend` was empty. The entire frontend, mockService, curriculum and learner storage behavior were preserved.

## Independent semantic review

QA manually inspected the service interface, mockService and actual consumers against [the mapping](../api-mapping.md) and [root contract](../../openapi.yml). All eight issue criteria passed: PM refinement; operation/schema coverage; authenticated identity and secret exclusion; retries, assistance and completion rules; documented real/mock differences; meaningful validation; preservation and publication; independent evidence and QA-only closure.

Review specifically covered protected `/me` identity, strict request fields, secret-free ordinary curriculum, server-authored answer checking, complete ordered attempt history, monotonic completion and independent-solving flags, hints after incorrect attempts, separate solution reveals and prevention of duplicate completion credit. Real credential handling differs explicitly from the public mock passphrase and requires a later frontend authentication adaptation.

No backend, database or real API client was implemented or executed. This stage verifies a contract, not runtime authentication, authorization, transactions or future server conformance. Frontend runtime tests were not rerun for this documentation-only stage; preservation was verified by an empty frontend diff. No contract defects or stage blockers remained at PASS.
