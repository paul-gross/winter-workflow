# HTML output standard for winter-workflow skills

Requirements any `winter-workflow` skill must satisfy when emitting an HTML report. The first consumer is `/harness-score`; future report-emitting skills extend the same baseline rather than reinvent it.

The goal is reports that **render anywhere, look right in any theme, diff cleanly across runs, and stay readable when printed or pasted into a ticket**. Treat this document as a contract, not a style guide — every requirement below has a verifier-friendly check.

## Requirements

### Self-contained

- No external assets — no remote CSS, no remote JS, no remote fonts, no remote images.
- Inline all CSS in a **single** `<style>` block in `<head>`. The baseline CSS goes first; skill-specific selectors are appended **inside the same block** (not a second `<style>` block) so cascade order is unambiguous and the file stays single-source-of-styles. Inline any JS in `<script>` blocks (skills should not need JS; treat any JS as a deliberate exception).
- Embed images as base64 data URIs or, preferred, inline SVG.
- The file must render fully offline. Verification: open from disk with the network disabled — layout, colors, and content remain intact.

### Theme-aware

- Light and dark via `@media (prefers-color-scheme: dark)`, driven by CSS custom properties (`--bg`, `--fg`, `--muted`, `--accent`, `--border`, …).
- No manual toggle. The operating system / user-agent preference is the single source of truth.
- WCAG AA contrast (4.5:1 for body text, 3:1 for large text) in **both** themes. Verify with a contrast checker against the chosen palette, not the rendered screenshot.

### Typography

- System font stack only: `ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif`. Mono stack for code: `ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace`.
- Body font size 16–18px. Line height 1.5–1.6.
- Content column max-width ~72ch. Center horizontally on wide viewports.
- No font shipping, no `@font-face`.

### Semantic and accessible

- Landmark elements: `<header>`, `<main>`, `<section>`, `<article>`, `<footer>`. One `<main>` per document.
- Heading levels in document order (`<h1>` once, then `<h2>`/`<h3>` nested; do not skip levels for styling).
- `<table>` must include `<caption>` and `<th scope="col">` / `<th scope="row">` on header cells.
- Visible focus rings on interactive elements (`:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }`).
- **Color is never the only signal.** If you mark a delta as "regressed" by tinting it red, also add a textual cue (`↓`, `regressed`, or a `[regressed]` tag) so colorblind readers and grayscale prints retain the information.
- Use `aria-label` on controls that have no visible text. Avoid `aria-*` attributes that duplicate semantics already provided by the chosen element.

### Print-friendly

- `@media print` rule that:
  - Forces white background and dark ink (`background: #fff; color: #000;`).
  - Removes gradients and shadows.
  - Adds `page-break-inside: avoid` to per-dimension or per-finding sections so they do not split across pages.
  - Hides any interactive affordances (none expected for v1; the rule still belongs in place).
- A printed report on a black-and-white printer must remain fully readable.

### Deterministic

- Identical inputs produce **byte-identical** HTML. Verification: run the skill twice with no source change in between; the two HTML files match under `diff`.
- No random IDs, no UUIDs in markup, no `Math.random()`-derived classes.
- No per-run timestamps inside CSS rules or inline styles.
- Exactly **one** visible timestamp per report, in the footer. Sort and order all collections deterministically (alphabetical, numeric, or by a documented key) so re-renders match.

### Metadata

Every report begins with:

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="generator" content="winter-workflow/<skill-name> v<rubric-or-skill-version>">
    <title><!-- skill-defined --></title>
    <style><!-- inline --></style>
  </head>
  …
</html>
```

The footer must visibly list: skill name, skill or rubric version, generation date (single timestamp from above), and the target (project name or path).

### Structured sidecar

When a report represents structured data downstream tools or agents may want to consume, write a `.json` sidecar **with the same basename** alongside the HTML. The HTML is for humans; the JSON is for machines and diffs.

- The sidecar's schema is the skill's responsibility; keep it stable across runs of the same rubric/skill version.
- Anything used to compute deltas in the next run belongs in the sidecar, not parsed out of the HTML.
- Skills that emit no machine-consumable structure may omit the sidecar; document the choice in the SKILL.

### Naming

- `YYYY-MM-DD.html` for single-target skills.
- `YYYY-MM-DD-<suffix>.html` where `<suffix>` disambiguates by target — typically the project name (e.g. `2026-05-25-winter-workflow.html`).
- `YYYY-MM-DD-HHMM.html` (or `YYYY-MM-DD-HHMM-<suffix>.html`) for same-day duplicate runs.
- Sidecars mirror the HTML basename with a `.json` extension.

## Baseline CSS

Copy-pasteable baseline. Skills **extend** this block (add component-specific selectors after the baseline) rather than rewriting it — divergence between skills is what makes reports look "off."

```css
:root {
  --bg: #ffffff;
  --fg: #1a1a1a;
  --muted: #5a5a5a;
  --accent: #0a5bd3;
  --border: #d6d6d6;
  --code-bg: #f4f4f5;
  --good: #117a3f;
  --bad:  #a4243b;
  --warn: #8a5a00;
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0e0f12;
    --fg: #e8e8ea;
    --muted: #9aa0a6;
    --accent: #6aa1ff;
    --border: #2a2d33;
    --code-bg: #16181d;
    --good: #4ad081;
    --bad:  #ff8a99;
    --warn: #f0c36d;
  }
}

* { box-sizing: border-box; }

html, body {
  margin: 0;
  padding: 0;
  background: var(--bg);
  color: var(--fg);
  font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  font-size: 17px;
  line-height: 1.55;
}

main, header, footer {
  max-width: 72ch;
  margin: 0 auto;
  padding: 1.25rem 1rem;
}

header { border-bottom: 1px solid var(--border); }
footer { border-top: 1px solid var(--border); color: var(--muted); font-size: 0.9rem; }

h1, h2, h3, h4 { line-height: 1.25; margin: 1.5rem 0 0.5rem; }
h1 { font-size: 1.6rem; }
h2 { font-size: 1.3rem; }
h3 { font-size: 1.1rem; }

a { color: var(--accent); }
a:focus-visible, button:focus-visible {
  outline: 2px solid var(--accent);
  outline-offset: 2px;
}

code, pre {
  font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
  background: var(--code-bg);
  border-radius: 4px;
}
code { padding: 0.1em 0.35em; font-size: 0.92em; }
pre  { padding: 0.75rem 1rem; overflow-x: auto; }

table {
  width: 100%;
  border-collapse: collapse;
  margin: 0.75rem 0 1.25rem;
}
caption {
  text-align: left;
  caption-side: top;
  font-weight: 600;
  margin-bottom: 0.35rem;
  color: var(--muted);
}
th, td {
  text-align: left;
  padding: 0.45rem 0.6rem;
  border-bottom: 1px solid var(--border);
  vertical-align: top;
}
th { font-weight: 600; }

.good { color: var(--good); }
.bad  { color: var(--bad);  }
.warn { color: var(--warn); }

@media print {
  :root {
    --bg: #ffffff;
    --fg: #000000;
    --muted: #333333;
    --accent: #000000;
    --border: #888888;
    --code-bg: #ffffff;
    --good: #000000;
    --bad:  #000000;
    --warn: #000000;
  }
  html, body { background: #fff; color: #000; }
  a { color: #000; text-decoration: underline; }
  header, main, footer { max-width: none; padding: 0.5rem 0; }
  section, article { page-break-inside: avoid; }
  pre, code { background: #fff; border: 1px solid #888; }
}
```

## Verification checklist

When a skill emits a report, the skill (or its caller) should be able to answer **yes** to each:

- [ ] Opens with network disabled and renders identically.
- [ ] Looks correct in both light and dark OS preferences without any user action.
- [ ] All text passes WCAG AA contrast in both themes.
- [ ] Uses landmark elements; headings in order; tables captioned and scoped.
- [ ] No use of color as the only signal (every color cue has a textual companion).
- [ ] Prints cleanly on a B/W printer with no gradients and no mid-section page breaks.
- [ ] Re-running the skill with the same inputs produces a byte-identical HTML file.
- [ ] `<meta name="generator">` and footer list skill, version, date, and target.
- [ ] Sidecar `.json` (when applicable) has the same basename and stable schema.
- [ ] Filename matches the naming convention.

A skill that cannot answer "yes" to any of these is not conforming and should be fixed before its report is published.
