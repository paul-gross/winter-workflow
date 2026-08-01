# Harness score — HTML report guide

The harness-score-specific HTML output. Build on the generic standard in [`../html-report.md`](../html-report.md) and add the specifics below. This file owns everything particular to the harness score; the generic spec owns everything reusable.

## Tailwind config

Set this inline after the Tailwind script. `darkMode: 'class'` and the content width come from the generic standard; the four cluster colors are harness-specific.

```html
<script>
  tailwind.config = {
    darkMode: 'class',
    theme: { extend: {
      colors: {
        foundation: { DEFAULT: '#0a5bd3', dark: '#6aa1ff' },
        governance: { DEFAULT: '#7a3fb8', dark: '#c69cff' },
        delivery:   { DEFAULT: '#0d7373', dark: '#4fd6d6' },
        outcomes:   { DEFAULT: '#a85d18', dark: '#f0b173' }
      },
      maxWidth: { content: '80rem' }
    } }
  };
</script>
```

## Cluster colors

One hue per rubric cluster, applied as the section's left-border accent (`border-l-<key>`), the sidebar dot (`bg-<key>`), and the header tag (`text-<key> border-<key>`). Always pair the color with the cluster name as text. Use the `dark:` variant (`-dark` suffix) in dark mode.

| Cluster | Tailwind key | Light | Dark |
|---------|--------------|-------|------|
| Foundation | `foundation` | `#0a5bd3` | `#6aa1ff` |
| Governance | `governance` | `#7a3fb8` | `#c69cff` |
| Delivery | `delivery` | `#0d7373` | `#4fd6d6` |
| Outcomes & Learning | `outcomes` | `#a85d18` | `#f0b173` |

## Score → color band

Color each dimension's stage by goodness, and **always** pair the color with the stage-name text label beneath it (so the meaning survives grayscale / color blindness).

| Stage | Tailwind text class (light / dark) | Stage-name label |
|-------|-----------------------------------|------------------|
| ≥ 4.5 | `text-emerald-700` / `dark:text-emerald-300` | Agentic Flywheel |
| 4.0–4.49 | `text-emerald-600` / `dark:text-emerald-400` | Systematic Harness |
| 3.5–3.99 | `text-amber-600` / `dark:text-amber-400` | Approaching Systematic |
| 3.0–3.49 | `text-orange-600` / `dark:text-orange-400` | Human-in-the-Loop |
| < 3.0 | `text-red-600` / `dark:text-red-400` | Below Human-in-the-Loop |

## Structure

In order, inside the generic app shell (sticky sidebar + content column):

1. **Sidebar nav** — a link to the profile summary, then the 10 dimensions grouped under their four cluster headers (Foundation, Governance, Delivery, Outcomes & Learning). Each link carries the cluster `bg-<key>` dot and the right-aligned stage. Anchors are deterministic ids `#d1`…`#d10`.
2. **`<header>`** — title (`Harness score — <project>`), target path, generation date, rubric version; the manual theme toggle; a baseline-run callout when there is no prior report.
3. **Profile summary table** — one row per dimension: name, cluster, stage, delta (`—` on a baseline run). Keep the textual `↑`/`↓`/`=` cue alongside color. Put the "no overall stage" disclaimer in a callout.
4. **Per-dimension detail** — one card per dimension, `id="dN"`, with the cluster `border-l-<key>` accent. Header is a flexbox: dimension title + cluster tag on the left; on the right the large score (colored per the band table) with the stage-name label beneath. Body: evidence list (file paths as visible code text), rationale, and the next-stage suggestion in a callout.
5. **Deltas section** — when a prior report exists: a table of per-dimension stage movement, then a list of stale evidence citations.
6. **`<footer>`** — generator `winter-workflow/harness-score`, rubric version, generation date, target. <!-- winter-lint:example -->
