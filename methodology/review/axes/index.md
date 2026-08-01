# Review axes

Each axis is a caller-neutral review methodology. The shared review process selects one axis and supplies its semantic inputs; both inline executors and isolated reviewer runtimes execute the same axis document.

| Axis | Methodology | Concern |
|------|-------------|---------|
| `code` | [Code review](./code.md) | correctness, architectural quality, and design-principle adherence in one pass |
| `correctness` | [Correctness review](./correctness.md) | broken behavior, broken neighbors, and false claims |
| `architecture` | [Architecture review](./architecture.md) | conformance to the target's declared code-shape principles — layers, boundaries, abstractions |
| `qualities` | [Quality attribute review](./qualities.md) | the change against the target's declared software-quality trade-offs and their magnitudes |
| `tests` | [Test review](./tests.md) | the change's tests against the target's declared testing requirements |
| `context` | [Context review](./context.md) | agent-facing markdown against documented authoring conventions |
| `harness` | [Harness review](./harness.md) | the application-to-agentic-harness seam |
| `documentation` | [Documentation review](./documentation.md) | external-facing public documentation |

`code` is the single-pass generalist; `correctness`, `architecture`, `qualities`, and `tests` decompose its ground into focused axes so each reviewer holds one concern — run the generalist or the decomposition over a change-set, not both.

All axes use the shared [reporting contract](../reporting.md).
