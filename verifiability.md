# Verifiability matrix

The verification methods available for winter-workflow itself — the concrete ways a change to this extension's skills,
agents, and methodology is verified. Shape per `canon:verifiability-matrix`.

## Commands

Run from the workspace root.

| Method                           | Command                                                                                                                                                                                                                                                                                                       |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `winter-workflow:lint`           | `winter lint winter-workflow` — the agent-frontmatter check (`scripts/lint-agents.py`) and the methodology-boundary check (`scripts/lint-methodology.py`), wired through the `lint` field in `winter-ext.toml`; fenced code and any block carrying `<!-- winter-lint:example -->` are treated as illustrative |
| `winter-workflow:lint-tests`     | `python3 tests/test_lint_agents.py && python3 tests/test_lint_methodology.py && python3 tests/test_context_usage.py` — exercises the two lints and the `optimize-context` measurement script with stdlib-only fixtures                                                                                        |
| `winter-workflow:markdown-style` | `dprint check` and `rumdl check .` from this repo's worktree — the mechanical markdown gates `dprint.json` and `.rumdl.toml` declare, contributed to `winter lint` by `winter-context`. `dprint fmt` and `rumdl check . --fix` write the fixes. Needs both binaries on `PATH`                                 |

## Manual testing

`winter-workflow:manual` — the cold-spawn behavioral eval owed by `canon:cold-eval` for any change that adds or reshapes
context an agent is expected to act on: a new or changed rule, a routing change, a skill or agent description, a
broadened trigger. Declare each behavioral expectation as a scenario, spawn a fresh subagent with only the cue, and
record `reached` and `behaved` per scenario. Only a session that can spawn cold subagents may run it; a non-spawning
agent hands it up.

## Tools

`tool:eval-fixture` — a scratch directory of freshly written fixture prose exhibiting the anti-pattern under test, for
enforcement-flavored cold-eval scenarios; create it under the session scratchpad, never by copying the convention's own
examples.
