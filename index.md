# Winter workflow

Agentic build skills and role-pure subagents that drive feature development in winter workspaces, from one-shot fixes to
coordinated team builds.

**IMPORTANT: When planning or building software, you MUST first read
[methodology/philosophy.md](./methodology/philosophy.md)** — it governs *how* every build skill and agent approaches the
work, not just what they produce.

**IMPORTANT: No process references in anything you write** — code and agent-facing markdown alike. Never an issue/PR
number or tracker URL, never a review-finding id or review vocabulary (*"per the review"*, *"as requested"*); the commit
message carries provenance, the file does not. Delete a provenance-only comment rather than rephrasing it.

## Reference

| Topic                                                          | Read when…                                                                                                                                                   |
| -------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| [methodology/index.md](./methodology/index.md)                 | …you are about to plan, build, review, deliver, or score work with this extension — the hub routes to the specific process                                   |
| [methodology/orchestration.md](./methodology/orchestration.md) | …you are executing within the blizzard agent orchestration system — a fleet worker session working a chunk's node-step; owns the node-step → methodology map |
| [verifiability.md](./verifiability.md)                         | …you are verifying a change to winter-workflow itself — the declared verification methods and their ids                                                      |
