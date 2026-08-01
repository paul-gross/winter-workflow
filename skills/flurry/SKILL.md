---
description: Deliver a batch of small, mostly-independent feature asks across multiple feature environments at once, in parallel. Use when you have several distinct small features to build together.
argument-hint: "[the small features to build; optionally the envs to run them in]"
allowed-tools: Bash, Read, Glob, Grep, Agent, AskUserQuestion
---

# Flurry

Bind `$ARGUMENTS` together with the human caller's conversation input to the **feature batch** input. Bind any named environments to the optional **environment pool** input, and preserve any stated task dependencies or target repositories in the batch description.

Read `winter-workflow:/methodology/build/flurry/process.md` and execute every step exactly as written. The linked process is authoritative; do not paraphrase, skip, or reorder its steps.
