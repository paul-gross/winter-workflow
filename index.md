# Winter workflow

Agentic build skills and role-pure subagents for winter workspaces. Installs `glacier`, `iceberg`, `snowball`, `flurry`, and other skills that drive feature development — from one-shot fixes to coordinated team builds — plus the role-pure agents those skills spawn.

**IMPORTANT: When planning or building software, you MUST first read [context/philosophy.md](./context/philosophy.md)** — the hybrid harness/software-engineer identity, core philosophy, and doc-first approach behind this extension. It governs *how* every build skill and agent approaches the work, not just what they produce.

| Topic | Read when… |
|-------|------------|
| [context/choosing-a-build-skill.md](./context/choosing-a-build-skill.md) | …you need to pick a skill for the work at hand — the routing guide between `snowball`, `flurry`, `glacier`, and `iceberg` |
| [context/definition-of-done.md](./context/definition-of-done.md) | …you want the shared tested-and-docs-updated bar that every build skill enforces |
| [context/winter-space.md](./context/winter-space.md) | …a skill needs to locate where its generated artifacts go — the `winter space <kind>` contract for scores, manifests, workflow docs, and retrospectives |
| [context/review.md](./context/review.md) | …you need to run an ad-hoc change-set review directly (no skill) — the shared review engine: the review axes, scope vocabulary, change-set discovery, execution mode, model, and the reviewer spawn-prompt scaffold every review skill and `pre-push` share |
