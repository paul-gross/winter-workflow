# Review axes

Each axis is a caller-neutral review methodology. The shared review process selects one axis and supplies its semantic inputs; both inline executors and isolated reviewer runtimes execute the same axis document.

| Axis | Methodology | Concern |
|------|-------------|---------|
| `code` | [Code review](./code.md) | correctness, architectural quality, and design-principle adherence |
| `context` | [Context review](./context.md) | agent-facing markdown against documented authoring conventions |
| `harness` | [Harness review](./harness.md) | the application-to-agentic-harness seam |
| `documentation` | [Documentation review](./documentation.md) | external-facing public documentation |

All axes use the shared [reporting contract](../reporting.md).
