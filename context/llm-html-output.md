# HTML output standard for winter-workflow skills

Requirements any `winter-workflow` skill must satisfy when emitting an HTML report. Report-emitting skills extend this shared baseline rather than reinvent it.

The goal is reports that **render anywhere, look right in any theme, diff cleanly across runs, and stay readable when printed or pasted into a ticket**. Treat this document as a contract, not a style guide — every requirement below has a verifier-friendly check.

## Requirements

### Assets & dependencies

- **Styling framework: Tailwind CSS via the Play CDN, pinned to `3.4.16`** — `<script src="https://cdn.tailwindcss.com/3.4.16"></script>`. One framework, one pinned version across every winter-workflow report so they stay visually consistent. Never use a floating `@latest` or unversioned endpoint. Extend the theme (category hues, etc.) inline via `tailwind.config`.
- Skill-specific CSS beyond utilities goes in a **single** `<style>` block in `<head>`, placed *after* the Tailwind script so cascade order is unambiguous. Inline any JS in `<script>` blocks.
- **Remote webfonts are allowed** — link one from a pinned font CDN when it sharpens the report. Embed images as base64 data URIs or, preferred, inline SVG.

### Theme-aware

- Support light and dark. With Tailwind use `darkMode: 'class'`; set the initial `.dark` class from the OS preference (`prefers-color-scheme`) before first paint to avoid a flash.
- Provide a **manual theme toggle** (a button) that overrides the OS default and persists the choice in `localStorage`. The toggle is hidden in print.
- WCAG AA contrast (4.5:1 for body text, 3:1 for large text) in **both** themes. Verify with a contrast checker against the chosen palette, not the rendered screenshot.

### Typography

- Default to the system font stack: `ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif` (mono for code: `ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace`). A pinned remote webfont (see *Assets & dependencies*) may replace the sans stack when it sharpens the report.
- Body font size 16–18px. Line height 1.5–1.6.
- Keep **prose** to a readable measure (~72ch). Do **not** constrain the whole page to 72ch — that strands most of the screen. Reports use the full-width app shell in *Layout & components* (sticky sidebar + a content column capped around 75–80rem and centered).

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
  - Adds `page-break-inside: avoid` to each major section (e.g. per-card or per-finding) so they do not split across pages.
  - Hides any interactive affordances (none expected for v1; the rule still belongs in place).
- A printed report on a black-and-white printer must remain fully readable.

### Stable across runs

An LLM won't reproduce byte-identical markup from one run to the next, and the agent has no reliable way to verify byte-equality by diffing two renders — so don't promise determinism. Instead, remove *gratuitous* churn so successive reports differ only where the content actually changed:

- No random IDs, no UUIDs, no `Math.random()`-derived classes. Use stable, meaningful ids (e.g. `#d1`…`#d10`).
- Exactly **one** visible timestamp per report, in the footer; none inside CSS or inline styles.
- Order every collection by a documented key (numeric, alphabetical) so the sequence doesn't shuffle between runs.

### Metadata

Every report begins with:

```html
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="generator" content="winter-workflow/<skill-name> v<skill-version>">
    <title><!-- skill-defined --></title>
    <style><!-- inline --></style>
  </head>
  …
</html>
```

The footer must visibly list: skill name, skill version, generation date (single timestamp from above), and the target (project name or path).

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
  --surface: #f6f7f9;
  --fg: #1a1a1a;
  --muted: #5a5a5a;
  --accent: #0a5bd3;
  --border: #d9dce1;
  --code-bg: #eef0f3;
  --good: #117a3f;
  --okay: #3f7a2e;
  --mod:  #b5630c;
  --warn: #8a5a00;
  --bad:  #a4243b;
  --shadow: 0 1px 2px rgba(0,0,0,.06), 0 6px 18px rgba(0,0,0,.05);
}

@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0e0f12;
    --surface: #16181d;
    --fg: #e8e8ea;
    --muted: #9aa0a6;
    --accent: #6aa1ff;
    --border: #2a2d33;
    --code-bg: #1b1e24;
    --good: #4ad081;
    --okay: #8fd38a;
    --mod:  #f0a35a;
    --warn: #f0c36d;
    --bad:  #ff8a99;
    --shadow: 0 1px 2px rgba(0,0,0,.4), 0 6px 18px rgba(0,0,0,.35);
  }
}

* { box-sizing: border-box; }

html { scroll-behavior: smooth; }
html, body {
  margin: 0;
  padding: 0;
  background: var(--bg);
  color: var(--fg);
  font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  font-size: 17px;
  line-height: 1.55;
}

/* App shell: sticky sidebar + content column */
.layout { display: grid; grid-template-columns: 16rem minmax(0, 1fr); align-items: start; }
.sidebar {
  position: sticky;
  top: 0;
  align-self: start;
  height: 100vh;
  overflow: auto;
  background: var(--surface);
  border-right: 1px solid var(--border);
  padding: 1.25rem 1rem;
}
.content { min-width: 0; }
header, main, footer { max-width: 64rem; margin: 0 auto; padding: 1.5rem 2rem; }

header { border-bottom: 1px solid var(--border); }
footer { border-top: 1px solid var(--border); color: var(--muted); font-size: 0.9rem; }

h1, h2, h3, h4 { line-height: 1.25; margin: 1.5rem 0 0.5rem; }
h1 { font-size: 1.7rem; }
h2 { font-size: 1.3rem; }
h3 { font-size: 1.05rem; }

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
  padding: 0.5rem 0.6rem;
  border-bottom: 1px solid var(--border);
  vertical-align: top;
}
th { font-weight: 600; }

.good { color: var(--good); }
.bad  { color: var(--bad);  }
.warn { color: var(--warn); }

/* Sidebar navigation */
.sidebar .nav-title { font-size: 0.95rem; font-weight: 700; margin: 0 0 0.75rem; }
.sidebar .nav-group { margin: 0.9rem 0 0.4rem; font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.06em; color: var(--muted); }
.sidebar ol { list-style: none; margin: 0; padding: 0; }
.sidebar li { margin: 0.1rem 0; }
.sidebar a { display: flex; align-items: center; gap: 0.5rem; text-decoration: none; color: var(--fg); padding: 0.3rem 0.4rem; border-radius: 6px; font-size: 0.9rem; }
.sidebar a:hover { background: var(--code-bg); }
.dot { width: 0.6rem; height: 0.6rem; border-radius: 50%; flex: none; background: var(--cat, var(--muted)); }
.nav-metric { margin-left: auto; font-variant-numeric: tabular-nums; color: var(--muted); font-size: 0.82rem; }

/* Section card with category accent */
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-left: 5px solid var(--cat, var(--accent));
  border-radius: 10px;
  padding: 1.25rem 1.5rem;
  margin: 2rem 0;
  box-shadow: var(--shadow);
  scroll-margin-top: 1rem;
}

.card-head { display: flex; align-items: center; justify-content: space-between; gap: 1.5rem; margin: 0 0 0.75rem; }
.card-head h2 { margin: 0; font-size: 1.3rem; }
.category-tag {
  display: inline-block; margin-top: 0.35rem;
  font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.05em;
  color: var(--cat, var(--muted)); border: 1px solid var(--cat, var(--border));
  padding: 0.1rem 0.5rem; border-radius: 999px;
}

.score-wrap { text-align: right; flex: none; line-height: 1; }
.score { font-size: 3.25rem; font-weight: 800; font-variant-numeric: tabular-nums; display: block; }
.score-band { display: block; font-size: 0.78rem; color: var(--muted); margin-top: 0.2rem; }

/* Score color bands (good -> bad). Always paired with the .score-band text label. */
.score--excellent { color: var(--good); }
.score--good      { color: var(--okay); }
.score--fair      { color: var(--warn); }
.score--moderate  { color: var(--mod); }
.score--weak      { color: var(--bad); }

/* Callout / disclaimer panels */
.callout { background: var(--code-bg); border: 1px solid var(--border); border-left: 4px solid var(--accent); border-radius: 8px; padding: 0.7rem 1rem; margin: 0.85rem 0; }
.callout--info { border-left-color: var(--accent); }
.callout--next { border-left-color: var(--good); }
.callout--warn { border-left-color: var(--warn); }
.callout-title { font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700; color: var(--muted); margin: 0 0 0.2rem; }

.label { font-weight: 600; margin: 0.6rem 0 0.1rem; }
.evidence { margin: 0.25rem 0 0.5rem; padding-left: 1.1rem; }
.evidence li { margin: 0.3rem 0; }
.path { font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace; background: var(--code-bg); border-radius: 4px; padding: 0.05em 0.3em; font-size: 0.9em; }
.note { color: var(--muted); }

@media (max-width: 60rem) {
  .layout { grid-template-columns: 1fr; }
  .sidebar { position: static; height: auto; border-right: none; border-bottom: 1px solid var(--border); }
  header, main, footer { padding: 1.25rem 1rem; }
}

@media print {
  :root {
    --bg: #ffffff; --surface: #ffffff; --fg: #000000; --muted: #333333;
    --accent: #000000; --border: #888888; --code-bg: #ffffff;
    --good: #000000; --okay: #000000; --mod: #000000; --warn: #000000; --bad: #000000;
    --cat: #000000;
    --shadow: none;
  }
  html, body { background: #fff; color: #000; }
  a { color: #000; text-decoration: underline; }
  .layout { display: block; }
  .sidebar { display: none; }
  header, main, footer { max-width: none; padding: 0.5rem 0; }
  .card { box-shadow: none; border: 1px solid #888; break-inside: avoid; page-break-inside: avoid; }
  section, article { page-break-inside: avoid; }
  .score { color: #000 !important; }
  pre, code { background: #fff; border: 1px solid #888; }
}
```

## Layout & components

These are **semantic** requirements — what the report must contain and convey. Realize them with framework utilities (Tailwind classes, etc.), the framework-free baseline above, or a mix. The look may vary; the semantics below do not.

### Wide app shell + sidebar

- Use a two-region layout: a navigation **sidebar** plus a **content column**. Do not render a single narrow column down the middle of a wide screen.
- The sidebar is **sticky** (stays put / scrolls independently) on wide viewports and lists every major section as an in-page anchor link. Collapse to a single column on narrow viewports and in print.
- Content column: readable measure (cap ~60–64rem) centered within its region; prose stays ~72ch.

### Category color coding

When sections belong to named categories, give each category a hue and apply it consistently: a left-border accent on the section, a dot in the sidebar link, and a pill/tag on the section header. Define the hue for both light and dark and keep it AA as text on the background. **The category name always appears as text** — color reinforces, never replaces it.

### Score / metric badge

Render a section's headline metric as a header **flexbox**: title on the left, a **large** value (~3rem, bold, tabular) on the right. Color the value by goodness (green = great → red = poor) **and always pair it with a short text label** (e.g. a rating or grade) so the meaning survives grayscale and color blindness.

### Callout panels

Use tinted, left-accented **callout panels** with an uppercase kicker for disclaimers, notes, and recommendations (baseline-run notes, "no overall score" caveats, next-step actions). Prefer a callout over a bare paragraph for anything the reader must not miss.

### Tailwind specifics

Tailwind is the standard (see *Assets & dependencies*). Set `darkMode: 'class'` and seed the initial `.dark` class from `prefers-color-scheme` in a small inline script, then flip it with the manual toggle. Define theme colors (any category hues a report needs) inline via `tailwind.config`. Realize the **print** rules — hide the sidebar, drop shadows, avoid mid-section page breaks — with the `print:` variant. Accessibility and color-never-the-only-signal still apply.

## Verification checklist

When a skill emits a report, the skill (or its caller) should be able to answer **yes** to each:

- [ ] Tailwind loaded from the **version-pinned** Play CDN; skill-specific CSS inlined after it.
- [ ] Renders correctly when opened in a browser.
- [ ] Uses a wide app shell with a sticky sidebar of in-page links — not a single narrow column.
- [ ] Defaults to the OS light/dark preference and offers a working manual toggle that overrides it (toggle hidden in print).
- [ ] All text passes WCAG AA contrast in both themes.
- [ ] Uses landmark elements; headings in order; tables captioned and scoped.
- [ ] No use of color as the only signal (every score/metric color has a textual companion).
- [ ] Prints cleanly on a B/W printer with the sidebar hidden, no gradients, and no mid-section page breaks.
- [ ] No random IDs; collections ordered by a documented key; exactly one timestamp (in the footer).
- [ ] `<meta name="generator">` and footer list skill, version, date, and target.
- [ ] Filename matches the naming convention.

A skill that cannot answer "yes" to any of these is not conforming and should be fixed before its report is published.
