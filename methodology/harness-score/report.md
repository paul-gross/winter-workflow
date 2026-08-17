# Harness score — HTML report

This document owns everything particular to the harness-score HTML report. The generic, reusable requirements are owned by [`../html-report.md`](../html-report.md); a harness-score report is built by applying that generic standard and adding these specifics on top.

## Cluster colors

The Tailwind theme config is set inline immediately after the Tailwind script tag, extending the theme with exactly:

```js
tailwind.config = {
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        foundation: { DEFAULT: '#0a5bd3', dark: '#6aa1ff' },
        governance: { DEFAULT: '#7a3fb8', dark: '#c69cff' },
        delivery:   { DEFAULT: '#0d7373', dark: '#4fd6d6' },
        outcomes:   { DEFAULT: '#a85d18', dark: '#f0b173' },
      },
      maxWidth: { content: '80rem' },
    },
  },
}
```

The `darkMode: 'class'` setting and the `content` max-width come from the generic standard; the four cluster colors are the harness-score-specific part. The rubric cluster display names map to the Tailwind color keys as Foundation → `foundation`, Governance → `governance`, Delivery → `delivery`, and Outcomes & Learning → `outcomes`. Dark mode uses each cluster color's `-dark` suffixed variant via the `dark:` prefix.

Each cluster's single hue is applied in three places — the section's left-border accent (`border-l-<key>`), the sidebar dot (`bg-<key>`), and the header tag (`text-<key> border-<key>`) — and the cluster color is always paired with the cluster name as visible text.

## Section order

Inside the generic app shell (sticky sidebar plus content column), the report's sections run in this fixed order:

1. **Sidebar nav** — a link to the profile summary, then the 10 dimensions grouped under their four cluster headers (Foundation, Governance, Delivery, Outcomes & Learning), each link carrying the cluster `bg-<key>` dot and the right-aligned stage value.
2. **Header** — the title in the form "Harness score — \<project\>", the target path, the generation date, the rubric version, and the manual theme toggle, plus a baseline-run callout when there is no prior report.
3. **Profile summary** — a table with one row per dimension showing name, cluster, stage, and delta, with an em dash as the delta on a baseline run; the disclaimer that there is no overall stage sits in a callout in this section.
4. **Per-dimension detail cards** — one card per dimension with `id="dN"` and the cluster's `border-l-<key>` accent; the anchors are the deterministic ids `#d1` through `#d10`. The card header is a flexbox with the dimension title and cluster tag on the left and, on the right, the large stage score colored per the band below with the stage-name label beneath it. The body holds the evidence list with file paths rendered as visible code text, then the rationale, then the next-stage suggestion presented in a callout.
5. **Deltas** — present only when a prior report exists: a table of per-dimension stage movement followed by a list of stale evidence citations. Delta indicators keep the textual ↑/↓/= cue alongside any color.
6. **Footer** — names the generator as `winter-workflow/harness-score` together with the rubric version, the generation date, and the target. <!-- winter-lint:example -->

## Stage color bands

| Stage | Color | Stage-name label |
|-------|-------|------------------|
| ≥ 4.5 | `text-emerald-700` (`dark:text-emerald-300`) | Agentic Flywheel |
| 4.0–4.49 | `text-emerald-600` (`dark:text-emerald-400`) | Systematic Harness |
| 3.5–3.99 | `text-amber-600` (`dark:text-amber-400`) | Approaching Systematic |
| 3.0–3.49 | `text-orange-600` (`dark:text-orange-400`) | Human-in-the-Loop |
| < 3.0 | `text-red-600` (`dark:text-red-400`) | Below Human-in-the-Loop |

Each dimension's stage value is colored by goodness and is always paired with its stage-name text label beneath it, so the meaning survives grayscale rendering and color blindness.
