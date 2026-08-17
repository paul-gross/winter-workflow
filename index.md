# Winter workflow

Agentic build skills and role-pure subagents for winter workspaces. Installs `glacier`, `iceberg`, `snowball`, `flurry`, and other skills that drive feature development — from one-shot fixes to coordinated team builds — plus the role-pure agents those skills spawn.

**IMPORTANT: When planning or building software, you MUST first read [methodology/philosophy.md](./methodology/philosophy.md)** — the hybrid harness/software-engineer identity, core philosophy, and doc-first approach behind this extension. It governs *how* every build skill and agent approaches the work, not just what they produce.

## IMPORTANT: no process references in what you write

Binds every line you write, code and agent-facing markdown alike — source, tests, configuration, comments, docstrings, agents, skills, and context docs:

- **Never write an issue, ticket, or PR number, or a tracker URL.** No `#42`, no `GH-42`, no link to the issue. The commit message carries provenance; the file does not.
- **Never write a review-finding id or review vocabulary.** No `M1`, no `C4`, no `must-fix #3`, no *"per the review"*, no *"round 2"*, no *"as requested"*.
- **Delete a provenance-only comment, don't rephrase it.** Strip the reference; if what remains describes neither the code in front of the reader nor the convention being stated, the reference *was* the content and goes with it.

## Reference

| Topic | Read when… |
|-------|------------|
| [methodology/index.md](./methodology/index.md) | …you are about to plan, build, review, deliver, or score work with this extension — the hub routes to the specific process |
| [methodology/orchestration.md](./methodology/orchestration.md) | …you are executing within the blizzard agent orchestration system — a fleet worker session working a chunk's node-step. Contains critical blizzard integration to workflows: the node-step → methodology map |
| [verifiability.md](./verifiability.md) | …you are verifying a change to winter-workflow itself — the declared verification methods and their ids |
