# Harness model maturity rubric — v1

| Field | Value |
|-------|-------|
| Rubric version | **v1** |
| Snapshot date | 2026-05-25 |
| Source | The Harness Model — AI Engineering Maturity Matrix |
| Source URL | https://handsonarchitects.com/blog/2026/the-harness-model-ai-engineering-maturity-matrix/ |
| Authors | Maciej Laskowski, Tomasz Michalak |
| Publication date | 2026-04-16 |

Attribution: stage names and per-dimension descriptions in this rubric are paraphrased from the source article above. Diagnostic questions and "evidence to look for" lists are this rubric's own elaboration, chosen to make the stage descriptions operational for a codebase scoring skill.

## The frozen-rubric rule

Mixing rubric versions invalidates deltas. A score at v1 and a score at v2 cannot be compared to each other — the dimensions are not promised to map across versions, and a "stage 3" in one version is not the same artifact as a "stage 3" in another.

Concretely:

- Every harness-score run emits the rubric version in its report (HTML metadata + JSON sidecar) — whether the run was triggered via the `harness-score` skill or by an agent executing [`./process.md`](./process.md) directly.
- Delta computation compares the new score only against the **most recent prior report with the same rubric version**. Older reports at a different version are ignored for delta purposes.
- Edits to this file are deliberate version bumps, not opportunistic improvements. Tightening a stage description, swapping a dimension, or adding diagnostic questions all warrant a `v2` bump and a fresh baseline.

## The 5 stages

Verbatim names and one-line definitions from the source article:

1. **No AI Process** — Organizations without AI integration.
2. **Chatbot-Assisted** — Basic AI tool usage with human review.
3. **Human-in-the-Loop** — Deliberate agent use with human oversight.
4. **Systematic Harness** — Designed control systems around agents.
5. **Agentic Flywheel** — Agents improving the systems that govern them.

## The 10 dimensions

Organized into four clusters (Foundation, Governance, Delivery, Outcomes & Learning), as in the source article.

---

### FOUNDATION CLUSTER

#### 1. Context Engineering

| Stage | Description |
|-------|-------------|
| 1 | N/A — no AI in use. |
| 2 | Humans copy-paste snippets of code and docs into chat. |
| 3 | A human-maintained `AGENTS.md` (or `CLAUDE.md`) collects context; loading is manual per task. |
| 4 | The repository is the system of record. Context is structured for progressive disclosure (root index → cluster index → leaf docs). Agents pull only what they need. |
| 5 | Humans design the context structure; agents maintain and evolve it (add, update, deprecate documents) as the codebase changes. |

**Diagnostic questions:**

- What documents do agents read before starting work, and where do they live?
- Are humans and agents reading the same source of truth?
- When the codebase changes, who updates the agent-facing documentation — and is the change required to merge?

**Evidence to look for:**

- Presence and currency of `CLAUDE.md`, `AGENTS.md`, or equivalent at the repo root.
- A dedicated directory or named cluster of agent-facing documentation (the convention varies — `context/`, `docs/agents/`, `.cursor/rules/`, `AGENTS/`, `.github/copilot/`, etc.).
- Cross-referencing between docs (one document linking to another by stable path).
- Index documents that route to leaves rather than dumping everything in one file.
- Git history showing humans updating docs by hand vs. agents updating docs as part of regular changes.
- Stale references in agent-facing docs (renamed files, moved modules) — a stage 4 claim that is contradicted by stale references is actually a stage 3.

#### 2. Team (Humans + Agents)

| Stage | Description |
|-------|-------------|
| 1 | Large specialist team. Humans execute. Standard tools. |
| 2 | Same specialist team. Humans execute with AI suggestions in their editor. |
| 3 | Leaner, more delivery-minded team. Agents have file and terminal access; humans direct each task. |
| 4 | Small generalist team per initiative. Agents run the full stack (write code, run tests, drive verifiers). |
| 5 | The same generalists span multiple initiatives simultaneously; agents self-provision the resources (environments, fixtures, test data) they need. |

**Diagnostic questions:**

- If a specialist on this team disappeared tomorrow, can agents cover their role?
- How many concurrent initiatives can one human reasonably direct given current agent capability?
- Do agents have terminal access, or only editor-suggestion access?

**Evidence to look for:**

- Agent definitions covering multiple roles (developer, verifier, reviewer, planner) that can be composed.
- Skills or commands that compose agents into end-to-end workflows.
- Workspace tooling that lets one human run multiple agent sessions in parallel (worktrees, port assignment, environment isolation).
- Provisioning hooks (extension `on_env_init` or equivalent) that let agents bring up their own working environment.

---

### GOVERNANCE CLUSTER

#### 3. Security & Trust

| Stage | Description |
|-------|-------------|
| 1 | No AI-specific security concerns — no AI in the loop. |
| 2 | Human reviews AI output for obvious security issues by eye. |
| 3 | AI output goes through existing SAST / DAST tooling alongside human-written code. |
| 4 | Agents have scoped, auditable access. AI-specific threat modeling has been performed (prompt injection, exfiltration, secret leakage). |
| 5 | Agents enforce and evolve security policies (e.g., propose new lint rules from observed near-misses); humans govern the trust boundary itself. |

**Diagnostic questions:**

- What can an agent access, and is each access auditable after the fact?
- What is the threat model for prompt injection in this workspace?
- How are secrets kept out of agent context?

**Evidence to look for:**

- Permission scoping in agent definitions (tools list, allowed-tools frontmatter).
- Logged transcripts or audit trails of agent actions.
- Documented secret-handling rules (`.env` exclusions, redaction in logs).
- Lint or pre-commit checks that catch leaked credentials in agent-authored diffs.
- Explicit documentation of the trust boundary between agent and shared infrastructure.

#### 4. Architectural Governance

| Stage | Description |
|-------|-------------|
| 1 | No AI-specific constraints. |
| 2 | Basic rules in prompt files ("don't use library X", "prefer pattern Y"). |
| 3 | Human-enforced architectural boundaries; the solution space is verbally constrained but not mechanically. |
| 4 | Custom linters / contract tests encode architectural taste with concrete remediation hints. Taste invariants are code. |
| 5 | Harnesses ship as org-wide templates other teams adopt; humans define the taste that the templates enforce. |

**Diagnostic questions:**

- Which architectural rules are encoded as linters vs. tribal knowledge?
- How quickly is an architectural violation surfaced — at commit, at PR, at production?
- When agents violate an architectural convention, does the violation get caught automatically or by a human reading the diff?

**Evidence to look for:**

- Custom linter configs (`ruff`, `eslint`, `import-linter`, `dependency-cruiser`, etc.) checked into the repo.
- Pre-commit / pre-push hooks that run these linters.
- CI runs that fail on architectural violations rather than warning.
- Convention documents that name the linter rule that enforces each convention (vs. convention documents that read like wishlist prose).

---

### DELIVERY CLUSTER

#### 5. Human-Agent Interaction

| Stage | Description |
|-------|-------------|
| 1 | N/A — no AI in use. |
| 2 | Chatbot Q&A: ask a question, paste back an answer. |
| 3 | Agent generates code; the human reviews every output line-by-line. |
| 4 | Human is **on** the loop (intervenes by exception) rather than in it. The human's primary work is building and tuning the harness. |
| 5 | Agents propose harness improvements (new lints, new agents, new docs). Humans direct the evolution. |

**Diagnostic questions:**

- What fraction of agent output reaches the codebase without a human reading every line?
- Where does the human spend most of their day — reviewing diffs or extending the harness?
- Is there a feedback channel from agent failures back into the harness itself?

**Evidence to look for:**

- Agent-driven workflows that compose verification, review, and self-correction without a human in each step.
- A documented "retrospect on what went wrong" practice that produces durable harness changes.
- Skills or commands that act on the harness itself (e.g., a "review the harness" skill, a "score the harness" skill, a docs-update agent).
- Commit log showing harness-targeting commits (`feat(harness)`, `docs(ai)`, `chore(agents)`) alongside application commits.

#### 6. Workflow & Process

| Stage | Description |
|-------|-------------|
| 1 | No AI anywhere in the workflow. |
| 2 | Occasional AI for specific isolated tasks. |
| 3 | Daily agent use. The human delegates parallel work but still stitches results together. |
| 4 | Agents are always running. The default for any new task is agent-first. The human sets priorities. |
| 5 | Agents handle the full delivery cycle (plan → implement → verify → ship). Humans steer outcomes, not steps. |

**Diagnostic questions:**

- What percent of working hours involve at least one running agent?
- For a typical change, how many human-driven sequential steps are there from "I want X" to "X is shipped"?
- Can multiple agent-driven workflows run in parallel without colliding?

**Evidence to look for:**

- Worktree / environment isolation that supports concurrent agent runs.
- End-to-end skills (e.g., `/blizzard`) that orchestrate plan-implement-verify without per-step human handoff.
- Commit cadence and authorship attribution.
- Persistent agent infrastructure (scheduled agents, queued work) rather than ad-hoc per-task spawning.

#### 7. Reliability & Operations

| Stage | Description |
|-------|-------------|
| 1 | Manual runbooks. Engineers triage and mitigate incidents. |
| 2 | Same ops team. Agents draft queries on request; humans mitigate. |
| 3 | Structured runbooks. Agents analyze alerts and propose hypotheses; humans mitigate. |
| 4 | Agents auto-triage low-severity alerts (cluster, dedupe, hypothesize). Humans handle critical incidents. |
| 5 | Agents auto-remediate known failures (restart, rollback, retry with known-good config). Humans own novel incidents and post-incident learning. |

**Diagnostic questions:**

- What does the runbook look like, and is it machine-readable?
- For the last five incidents, who first hypothesized cause?
- What classes of failure can be remediated without paging a human?

**Evidence to look for:**

- Structured runbooks (YAML, Markdown with stable section headers) rather than free-form wiki pages.
- Alert routing that includes an "agent triage" step.
- Automated remediation hooks for known failure modes (with auditable logs).
- Post-incident docs that feed back into agent context (new runbook entries, new alert rules).

For codebases without a production deployment (libraries, CLIs, internal tools), score this dimension on the closest analogue: how the team handles **regressions and broken builds**. Manual debug → agent-assisted debug → structured failure analysis → auto-triage by agents → auto-remediation (e.g., bisect-and-revert bots).

---

### OUTCOMES & LEARNING CLUSTER

#### 8. Verification & Quality

| Stage | Description |
|-------|-------------|
| 1 | Manual testing. |
| 2 | Agent runs the test suite; human checks the results. |
| 3 | Custom linters and structural tests beyond the basic suite; human reviews results. |
| 4 | Agent-to-agent review with quality scoring (a reviewer agent grades a writer agent); human defines the criteria. |
| 5 | Agents detect and fix regressions autonomously; humans define standards and adjudicate disputes. |

**Diagnostic questions:**

- What runs automatically between "agent writes code" and "code lands in main"?
- Are verification criteria coded (linter rule, contract test, golden output) or implicit (reviewer judgment)?
- Does a reviewer agent exist, and does it block on findings or merely advise?

**Evidence to look for:**

- Reviewer agents in the agent roster.
- Skills that compose writer + reviewer + verifier roles.
- Custom linters that go beyond defaults (project-specific rules, not just `ruff` defaults).
- Structural tests (snapshot, golden file, schema, contract) checked into the repo.
- Reports or scores that quantify quality (rubric-driven, comparable across runs).

#### 9. Knowledge & Feedback Loops

| Stage | Description |
|-------|-------------|
| 1 | Tribal knowledge. Docs in wikis (or absent). |
| 2 | README-level docs. |
| 3 | Human structures the docs inside the repo. Retrospectives capture lessons agents have taught the team. |
| 4 | Versioned plans and quality grades live in the repo. Agent failures feed the harness (new rules, new docs, new guards). |
| 5 | Agents maintain docs and capture learnings autonomously; humans curate strategy. |

**Diagnostic questions:**

- Where does knowledge live: in the repo, in chat, in someone's head?
- When an agent makes a mistake, where does the lesson land?
- Are plans versioned (committed to the repo) or ephemeral (chat-only)?

**Evidence to look for:**

- Plan documents committed to the repo (not just chat transcripts).
- Retrospective documents committed to the repo.
- Commits that explicitly close a feedback loop ("after seeing agent X fail, added doc Y").
- Quality scores / harness scores / review reports preserved over time.
- Docs that are themselves versioned with the codebase (in-repo, not external wiki).

#### 10. Planning & Decision-Making

| Stage | Description |
|-------|-------------|
| 1 | Manual boards; experience-driven decisions. |
| 2 | AI helps write tickets and research options. |
| 3 | Agent triages issues; human prioritizes; decisions validated via PoCs. |
| 4 | Decision signals (metrics, evidence, prior reports) are equally reachable by humans and agents. Humans validate with prototypes. |
| 5 | Agents propose initiatives from observed signals; humans set direction from measured results. |

**Diagnostic questions:**

- Where do issues / plans live, and can agents read them as easily as humans?
- What evidence does a decision rest on, and is that evidence machine-accessible?
- Are decisions traceable from outcome back to the signal that triggered them?

**Evidence to look for:**

- Issue / backlog tooling integrated with the agent harness (CLI access, structured exports).
- Plan templates committed to the repo with stable schema.
- Prior decision documents (ADRs or equivalent) committed to the repo.
- Metrics surfaces (dashboards, reports) accessible to agents via the same path as humans.
- Skills that operate on plans (create, refine, score) — not just on code.

---

## Scoring rules

1. **Half-stages are allowed** (e.g., 3.5). Use a half-stage when the evidence straddles two stages — partially through the transition.
2. **Every stage assignment cites evidence.** A bare number is not a score; the citation is the score.
3. **When in doubt, pick the lower stage and explain.** A claim that is *almost* true is not the claim. Note what is missing to clear the next stage.
4. **Score the codebase as it is, not as the docs claim.** If conventions are documented but unenforced, the conventions are not enforced. Stage on the actual mechanism, not the aspirational one. A documented-but-unenforced convention does not promote a dimension above stage 3, regardless of how thoroughly the convention is written down.
5. **Do not average to a single overall stage.** The profile across dimensions is the message; collapsing it to one number is explicitly disallowed.
6. **Next-stage suggestions are concrete.** Name one file, one tool, or one change. "Improve documentation" is not concrete; "add `<doc-cluster>/decisions/0001-name.md` capturing the X discussion from `<commit-sha>`" is — substitute whatever directory the target project actually uses for agent-facing docs.
7. **Evidence is a file path or a command output**, not a feeling. If you cannot point at a file, the evidence does not exist for scoring purposes.
8. **Frozen-rubric discipline.** Do not improvise new dimensions, new stages, or rename existing ones at scoring time. If the rubric feels wrong for the target, that is a v2 conversation, not a scoring-run conversation.
