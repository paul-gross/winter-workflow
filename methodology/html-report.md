# HTML report standard

The shared baseline contract every winter-workflow skill must satisfy when it emits an HTML report; report-emitting skills extend this baseline rather than reinvent it. The requirements exist so reports render anywhere, look right in any theme, diff cleanly across runs, and stay readable when printed or pasted into a ticket. This is a contract rather than a style guide: every requirement is phrased so it has a verifier-friendly check.

The layout and component requirements are semantic — what the report must contain and convey. They may be realized with framework utilities, the framework-free [baseline CSS](#baseline-css) below, or a mix; the look may vary while the semantics may not.

## Naming

- Report filenames are `YYYY-MM-DD.html` for single-target skills, and `YYYY-MM-DD-<suffix>.html` where the suffix disambiguates by target — typically the project name, as in `2026-05-25-winter-workflow.html`.
- Same-day duplicate runs use `YYYY-MM-DD-HHMM.html`, or `YYYY-MM-DD-HHMM-<suffix>.html` with a target suffix.
- Sidecar files mirror the HTML basename with a `.json` extension.

## Document skeleton

Every report begins with `<!DOCTYPE html>` and `<html lang="en">`, and its `<head>` contains the charset and viewport metas, the generator meta, a skill-defined title, and the inline style:

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="generator" content="winter-workflow/<skill-name> v<skill-version>">
  <title><!-- skill-defined --></title>
  <style>/* baseline CSS, then skill-specific selectors */</style>
</head>
```

The report is self-contained:

- Any JavaScript is inlined in `<script>` blocks.
- Images are embedded as base64 data URIs, or preferably as inline SVG.
- Remote webfonts are allowed: link one from a pinned font CDN when it sharpens the report, and it may replace the default sans stack.

## Framework

- The styling framework is Tailwind CSS via the Play CDN pinned to version 3.4.16 — `<script src="https://cdn.tailwindcss.com/3.4.16"></script>` — so that one framework at one pinned version keeps every winter-workflow report visually consistent. Never load Tailwind from a floating `@latest` or otherwise unversioned endpoint.
- Theme extensions such as category hues are defined inline via `tailwind.config`.
- Skill-specific CSS beyond utility classes goes in a single `<style>` block in `<head>`, placed after the Tailwind script so cascade order is unambiguous.
- With Tailwind specifically: set `darkMode: 'class'`, seed the initial `.dark` class from `prefers-color-scheme` in a small inline script, flip it with the manual toggle, define needed category hues inline via `tailwind.config`, and realize the print rules — hidden sidebar, dropped shadows, no mid-section page breaks — with the `print:` variant.

## Determinism

Byte-identical markup across runs is not promised — an LLM will not reproduce it, and an agent cannot reliably verify byte equality by diffing renders — so the standard instead removes gratuitous churn, so that successive reports differ only where content actually changed:

- No random IDs, no UUIDs, no `Math.random()`-derived class names; ids are stable and meaningful, in the shape of `#d1` through `#d10`.
- Every collection is ordered by a documented key, numeric or alphabetical, so sequences do not shuffle between runs.
- Each report contains exactly one visible timestamp, in the footer, and none inside CSS or inline styles.

## App shell and typography

- Reports use a two-region app shell — a navigation sidebar plus a content column — and never render as a single narrow column down the middle of a wide screen. Prose is kept to a readable measure of roughly 72ch, but the whole page is never constrained to that measure — that would strand most of the screen: the full-width shell holds a centered content region capped around 75 to 80rem.
- Within its region, the content column keeps a readable measure capped around 60 to 64rem, centered, with prose at roughly 72ch.
- The sidebar stays sticky (scrolling independently) on wide viewports and lists every major section as an in-page anchor link; the page collapses to a single column on narrow viewports and in print.
- Body font size is 16 to 18 pixels with line height 1.5 to 1.6.

## Theming

- Reports support both light and dark themes; with Tailwind this means `darkMode: 'class'`, with the initial `.dark` class set from the OS `prefers-color-scheme` preference before first paint to avoid a flash.
- Every report provides a manual theme toggle button that overrides the OS default and persists the choice in `localStorage`; the toggle is hidden in print.

## Semantics and accessibility

- Reports use landmark elements — `<header>`, `<main>`, `<section>`, `<article>`, `<footer>` — with exactly one `<main>` per document.
- Heading levels run in document order: `<h1>` once, then `<h2>`/`<h3>` nested, never skipping levels for styling effect.
- Every `<table>` includes a `<caption>` and uses `<th scope="col">` / `<th scope="row">` on header cells.
- Controls with no visible text get an `aria-label`, and `aria-*` attributes that duplicate semantics the chosen element already provides are avoided.
- Interactive elements show visible focus rings, in the shape of `:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; }`.
- All text meets WCAG AA contrast — 4.5:1 for body text, 3:1 for large text — in both themes, verified with a contrast checker against the chosen palette values rather than a rendered screenshot.
- Color is never the only signal: any meaning conveyed by tint (for example a regressed delta in red) also carries a textual cue such as ↓, the word regressed, or a tag, so colorblind readers and grayscale prints keep the information.

## Components

- **Footer** — visibly lists the skill name, the skill version, the generation date (the report's single timestamp), and the target project name or path.
- **Headline metric** — a section's headline metric renders as a header flexbox: title on the left, a large value (around 3rem, bold, tabular numerals) on the right, colored by goodness from green (great) to red (poor) and always paired with a short text label such as a rating or grade so the meaning survives grayscale and color blindness.
- **Category hues** — when sections belong to named categories, each category gets one hue applied consistently as a left-border accent on the section, a dot in the sidebar link, and a pill or tag on the section header. The hue is defined for both light and dark, stays AA-contrast as text on the background, and the category name always also appears as text — color reinforces but never replaces it.
- **Callouts** — disclaimers, notes, and recommendations (baseline-run notes, no-overall-score caveats, next-step actions) go in tinted, left-accented callout panels with an uppercase kicker; prefer a callout over a bare paragraph for anything the reader must not miss.

## Print

- Every report has an `@media print` rule that forces a white background with dark ink (`background: #fff; color: #000;`), removes gradients and shadows, adds `page-break-inside: avoid` to each major section such as a card or finding so sections do not split across pages, and hides any interactive affordances.
- A printed report must remain fully readable on a black-and-white printer.

## Baseline CSS

The standard ships this copy-pasteable baseline; skills extend it by adding component-specific selectors after it rather than rewriting it, because divergence between skills is what makes reports look off.

```css
/* Theme custom properties */
:root {
  --bg: #ffffff; --surface: #f6f7f9; --fg: #1a1a1a; --muted: #5a5a5a;
  --accent: #0a5bd3; --border: #d9dce1; --code-bg: #eef0f3;
  --good: #117a3f; --okay: #3f7a2e; --mod: #b5630c; --warn: #8a5a00; --bad: #a4243b;
  --shadow: 0 1px 2px rgba(0,0,0,.06), 0 6px 18px rgba(0,0,0,.05);
}
@media (prefers-color-scheme: dark) {
  :root {
    --bg: #0e0f12; --surface: #16181d; --fg: #e8e8ea; --muted: #9aa0a6;
    --accent: #6aa1ff; --border: #2a2d33; --code-bg: #1b1e24;
    --good: #4ad081; --okay: #8fd38a; --mod: #f0a35a; --warn: #f0c36d; --bad: #ff8a99;
    --shadow: 0 1px 2px rgba(0,0,0,.4), 0 6px 18px rgba(0,0,0,.35);
  }
}

/* Base */
* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
html, body {
  margin: 0; padding: 0;
  background: var(--bg); color: var(--fg);
  font-family: ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto,
    "Helvetica Neue", Arial, sans-serif;
  font-size: 17px; line-height: 1.55;
}
h1, h2, h3, h4 { line-height: 1.25; margin: 1.5rem 0 0.5rem; }
h1 { font-size: 1.7rem; }
h2 { font-size: 1.3rem; }
h3 { font-size: 1.05rem; }
code, pre {
  font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
  background: var(--code-bg); border-radius: 4px;
}
code { padding: 0.1em 0.35em; font-size: 0.92em; }
pre { padding: 0.75rem 1rem; overflow-x: auto; }
table { width: 100%; border-collapse: collapse; margin: 0.75rem 0 1.25rem; }
caption {
  text-align: left; caption-side: top; font-weight: 600;
  margin-bottom: 0.35rem; color: var(--muted);
}
th, td {
  text-align: left; padding: 0.5rem 0.6rem;
  border-bottom: 1px solid var(--border); vertical-align: top;
}
th { font-weight: 600; }
a { color: var(--accent); }
a:focus-visible, button:focus-visible {
  outline: 2px solid var(--accent); outline-offset: 2px;
}

/* App shell */
.layout { display: grid; grid-template-columns: 16rem minmax(0, 1fr); align-items: start; }
.sidebar {
  position: sticky; top: 0; align-self: start; height: 100vh; overflow: auto;
  background: var(--surface); border-right: 1px solid var(--border);
  padding: 1.25rem 1rem;
}
.sidebar .nav-title { font-size: 0.95rem; font-weight: 700; margin: 0 0 0.75rem; }
.sidebar .nav-group {
  font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.06em;
  color: var(--muted); margin: 0.9rem 0 0.4rem;
}
.sidebar ol { list-style: none; margin: 0; padding: 0; }
.sidebar li { margin: 0.1rem 0; }
.sidebar a {
  display: flex; align-items: center; gap: 0.5rem;
  text-decoration: none; color: var(--fg);
  padding: 0.3rem 0.4rem; border-radius: 6px; font-size: 0.9rem;
}
.sidebar a:hover { background: var(--code-bg); }
.dot {
  width: 0.6rem; height: 0.6rem; border-radius: 50%; flex: none;
  background: var(--cat, var(--muted));
}
.nav-metric {
  margin-left: auto; font-variant-numeric: tabular-nums;
  color: var(--muted); font-size: 0.82rem;
}
.content { min-width: 0; }
header, main, footer { max-width: 64rem; margin: 0 auto; padding: 1.5rem 2rem; }
header { border-bottom: 1px solid var(--border); }
footer { border-top: 1px solid var(--border); color: var(--muted); font-size: 0.9rem; }

/* Cards */
.card {
  background: var(--surface); border: 1px solid var(--border);
  border-left: 5px solid var(--cat, var(--accent)); border-radius: 10px;
  padding: 1.25rem 1.5rem; margin: 2rem 0;
  box-shadow: var(--shadow); scroll-margin-top: 1rem;
}
.card-head {
  display: flex; align-items: center; justify-content: space-between;
  gap: 1.5rem; margin: 0 0 0.75rem;
}
.card-head h2 { margin: 0; font-size: 1.3rem; }
.category-tag {
  display: inline-block; margin-top: 0.35rem; font-size: 0.7rem;
  text-transform: uppercase; letter-spacing: 0.05em;
  color: var(--cat, var(--muted)); border: 1px solid var(--cat, var(--border));
  padding: 0.1rem 0.5rem; border-radius: 999px;
}

/* Scores */
.score-wrap { text-align: right; flex: none; line-height: 1; }
.score { display: block; font-size: 3.25rem; font-weight: 800; font-variant-numeric: tabular-nums; }
.score-band { display: block; font-size: 0.78rem; color: var(--muted); margin-top: 0.2rem; }
/* Color bands run good to bad; always paired with the .score-band text label */
.score--excellent { color: var(--good); }
.score--good { color: var(--okay); }
.score--fair { color: var(--warn); }
.score--moderate { color: var(--mod); }
.score--weak { color: var(--bad); }
.good { color: var(--good); }
.bad { color: var(--bad); }
.warn { color: var(--warn); }

/* Evidence and callouts */
.label { font-weight: 600; margin: 0.6rem 0 0.1rem; }
.evidence { margin: 0.25rem 0 0.5rem; padding-left: 1.1rem; }
.evidence li { margin: 0.3rem 0; }
.path {
  font-family: ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace;
  background: var(--code-bg); border-radius: 4px;
  padding: 0.05em 0.3em; font-size: 0.9em;
}
.note { color: var(--muted); }
.callout {
  background: var(--code-bg); border: 1px solid var(--border);
  border-left: 4px solid var(--accent); border-radius: 8px;
  padding: 0.7rem 1rem; margin: 0.85rem 0;
}
.callout--info { border-left-color: var(--accent); }
.callout--next { border-left-color: var(--good); }
.callout--warn { border-left-color: var(--warn); }
.callout-title {
  font-size: 0.72rem; text-transform: uppercase; letter-spacing: 0.05em;
  font-weight: 700; color: var(--muted); margin: 0 0 0.2rem;
}

/* Narrow viewports */
@media (max-width: 60rem) {
  .layout { grid-template-columns: 1fr; }
  .sidebar {
    position: static; height: auto;
    border-right: none; border-bottom: 1px solid var(--border);
  }
  header, main, footer { padding: 1.25rem 1rem; }
}

/* Print */
@media print {
  :root {
    --bg: #ffffff; --surface: #ffffff; --code-bg: #ffffff;
    --fg: #000000; --muted: #333333; --accent: #000000; --border: #888888;
    --good: #000000; --okay: #000000; --mod: #000000;
    --warn: #000000; --bad: #000000; --cat: #000000;
    --shadow: none;
  }
  html, body { background: #fff; color: #000; }
  a { color: #000; text-decoration: underline; }
  .layout { display: block; }
  .sidebar { display: none; }
  header, main, footer { max-width: none; padding: 0.5rem 0; }
  .card {
    box-shadow: none; border: 1px solid #888;
    break-inside: avoid; page-break-inside: avoid;
  }
  section, article { page-break-inside: avoid; }
  .score { color: #000 !important; }
  pre, code { background: #fff; border: 1px solid #888; }
}
```

## Verification

When a skill emits a report, the skill or its caller must be able to answer yes to every requirement above as a verification checklist — including that the report renders correctly when opened in a browser and that the filename matches the naming convention. A skill that cannot answer yes to any item is not conforming and is fixed before its report is published.
