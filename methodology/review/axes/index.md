# Review axes

The registry of review axes. Each axis is a caller-neutral review methodology document: the shared review process at [../process.md](../process.md) selects one axis and supplies that axis's semantic inputs, and every axis reports through the shared contract at [../reporting.md](../reporting.md). The identical axis document is executed regardless of runtime — inline executors and isolated reviewer runtimes both run the same file.

| Axis | Concern |
|------|---------|
| [`code`](./code.md) | A source-code change reviewed in one generalist pass |
| [`correctness`](./correctness.md) | Broken behavior, broken neighbors, and false claims |
| [`architecture`](./architecture.md) | Conformance to the target's declared code-shape principles — layers, boundaries, abstractions |
| [`qualities`](./qualities.md) | The change measured against the target's declared software-quality trade-offs and their magnitudes |
| [`tests`](./tests.md) | The change's tests measured against the target's declared testing requirements |
| [`context`](./context.md) | Agent-facing markdown measured against documented authoring conventions |
| [`harness`](./harness.md) | The application-to-agentic-harness seam |
| [`documentation`](./documentation.md) | External-facing public documentation |
| [`plan`](./plan.md) | An implementation plan, reviewed before building |

## Selection rules

- `code` is the single-pass generalist; `correctness`, `architecture`, `qualities`, and `tests` decompose the same ground into focused single-concern axes. Over one change-set, run either the `code` generalist or its four-axis decomposition, never both.
- `harness` and `plan` are not selectable as facets of a faceted review; invoke both only through the shared review process.
