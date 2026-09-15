# UI framework review, second opinion — 2026-09-15, revised the same day

An independent pass at the two questions in `UI_FRAMEWORK_REVIEW_BRIEF_2026-09-15.md`:
(1) is Streamlit the right framework, (2) if so, what to change. First reviewed on `main` at
`4f35b67`; revised on `main` at `1c3c4b9` after PRs #17–#37 landed (twenty merges: the
supplement findings, the prosperity classes, the semi-arcs, the years ladder, the widget
seeding, the self-hosted runner, the icon). Owner's venv (Python 3.14.7, Streamlit 1.62.0);
live server at 1400×900 and 900×600, light and dark, both reading depths; `AppTest` timed
directly. The prior brief was read after the code, not before it.

## Verdict — unchanged

**Stay on Streamlit.**

1. **The app is tables and prose.** UI half now: 90 `st.dataframe`, 92 `st.markdown`,
   60 `st.caption`, 19 `st.expander`, 57 `st.subheader`, ten pictures, 30 `_finding()` calls.
   Streamlit's native shape; every alternative makes the pictures easier and the tables and
   citations harder.
2. **The rerun model costs nothing perceptible.** A whole rerun — every evaluator, the
   timing bundle, a page — is 0.19–0.24 s without parsing, on the grown app. The live server
   keeps the compiled script, so a click is that fast.
3. **The suite is written against `AppTest`,** and `tables.json` is the doctrinal regression
   guard. No other framework has a headless harness the suite could move to without a rewrite.
4. **Streamlit 1.62 has the interactivity the app lacks**, verified in the installed package:
   `st.tabs(on_change="rerun")` with `TabContainer.open`; `st.dataframe(on_select=...)`;
   `st.dialog`; `st.fragment`; `st.html`; `st.context.theme`; `st.navigation(position="top")`;
   `streamlit.components.v2` with `bidi_component`.

**When the answer would change.** If the app is to become an interactive workstation — a time
slider with the wheel following it, click-driven exploration as the primary mode, animated 3D —
NiceGUI is the right move (event-driven, native window through the same pywebview, `ui.scene`
gives three.js). The price is the 3,100 UI lines and the harness. For a study companion whose
primary act is *cast, then read the cited tables*, that trade is wrong. The reference-frames
tool is JavaScript whichever framework carries the app, as a components-v2 component with
three.js bundled locally; it does not decide the question.

## What the twenty merges changed for the UI

The engine grew 2,550 lines (13,206 → 15,760); the UI half grew 290 (2,821 → 3,111), almost all
of it findings appended to pages. Measured in the browser on the owner's own chart:

| Page | Course text | With supplement |
|---|---|---|
| Chart: tables / subheaders / scroll height | 10 / 9 / 4,829 px | 15 / 14 / 6,763 px |
| Dignities | 5 / 5 / 2,532 px | 6 / 6 / 4,216 px |
| Configurations (all tabs in DOM) | 20 / 18 / 1,844 px | 20 / 18 / 4,214 px |
| Timing (all tabs in DOM) | 67 tables | 69 tables |

- **The Chart page is now the longest page at the supplement depth and half of it is not the
  chart.** Its first six sections are the cast (wheel, calculation, positions, points, cusps,
  special degrees). After them come eight delineation findings — the Moon on the third day,
  the fetus's stay, the seven classes of livelihood, Mercury's phase, Valens's Moon phases,
  Morin's aspect rules, the eyesight places, Rhetorius's affliction — each a subheader, a
  citation caption, a table and an expander, in build order rather than the course's. At the
  first review this page ended at the sign-category expander.
- **Headings carry their own metadata.** Fourteen findings say "(supplement, display only)" or
  "(display only)" in the h3 itself; the Configurations page has three h3s that run to a full
  line with the citation inside them. The harness keys `tables.json` on heading text, so this
  is also what any rename costs.
- **The app opens on the last chart** (`last_chart` preference), and nothing above the fold
  names it except the sidebar picker and the wheel's hub. The chart strip below matters more
  than it did.
- **Widget seeding (PR #31)** moved every sidebar and target widget to session-state seeding
  with no `value=` argument. That is the shape a relocated nativity form needs, and it removed
  the default-versus-seed warning; harness keys unchanged.
- **The suite runs on the self-hosted runner with xdist in under two minutes** (33 minutes
  hosted). Parsing is still over half of every `AppTest` render — Chart 0.45 → 0.20 s, Timing
  0.50 → 0.24 s with magic off — but the payoff is now about a minute per CI run, not five.
- **Still true from the first pass:** the sidebar is page list then form, Date at ¾ of the
  window and Save below the fold at 1400×900, the whole form below the fold at 900×600; two
  headings per page; every picture on an opaque white rectangle (`fill="#ffffff"`) so dark
  mode shows a white square; no `column_config` (0 hits) and cut-off Value columns; `/chart`
  says "Page not found" because a default page ignores its `url_path`; there is no
  `.streamlit/config.toml` in `Executable/` (the Deploy button shows for that reason).

## Recommendations, revised

Numbered against the first brief where they correspond.

### A. First, each under a day

1. **Split the Chart page into the cast and the findings.** *New; the additions made it the
   top item.* Keep "Chart" as the cast: wheel, metrics row, calculation, positions, points,
   cusps, sign categories. Move the eight delineation findings (and Dignities' Mars-by-sect
   row, which is a finding too) to a page of their own in Part 1 — "Findings", between
   Dignities and Configurations, or a "Delineation" page — ordered by the course's chapter, not
   by the date each was built. Two cheaper variants if a page is too much: tabs on the Chart
   page ("The cast" / "Findings"), or the findings behind one expander group. **Harness:**
   this moves table slots between pages; regenerate `tables.json` with
   `UPDATE_TABLE_FIXTURE=1` and read the diff — every line should be a move, none a loss.
   Add the new `url_path` to `conftest.PAGES`.

2. **Short headings, metadata in the caption.** Replace "(supplement, display only)" in h3s
   with a one-line caption under the heading — "Supplement · display only · Sahl, On
   Nativities 1.29, 11-12" — so the heading is the finding's name. `_finding()` already takes
   `citation`; add a `standing` argument and print both in the caption. **Harness:** heading
   renames change `tables.json`; do it in the same branch as item 1 so the fixture moves once.

3. **Navigation to the top; the sidebar becomes the nativity form.** Brief #3, different
   remedy. `st.navigation(pages, position="top")`: the page list becomes a header bar, the
   sidebar starts with Date, Save is inside the fold at 1400×900, and the repeated `st.title`
   goes. A dialog would hide the chart while the time is edited, which is what a rectification
   pass watches. Harness keys untouched; `AppTest` selects pages by hash, not by the widget.

4. **A one-line chart strip under the header on every page** — brief #3's strip: the loaded
   chart's name, date, time, standard, place, sect, day and hour lords. The app opens on a
   saved chart now, and the page should say which.

5. **Theme-aware pictures.** Read `st.context.theme.type` at the top level and pass a
   background/ink pair into `generate_hybrid_svg` and the three revolution renderers (pure
   functions; a parameter with the current colours as default keeps every test green). Before
   any wheel interactivity: a wheel unreadable in the user's theme is the larger defect.
   **Same branch: attribute escaping.** The renderers write names into SVG attributes
   unescaped, and a Lot name with double quotes broke the revolution wheel (CI on #15, noted
   in `7faae89`). Escape every attribute and text value at the one place each renderer
   writes it, with a test that renders a chart whose Lot and place names carry quotes,
   ampersands and angle brackets.

6. **`Executable/.streamlit/config.toml`, with magic off** — brief #1, demoted. `[runner]
   magicEnabled = false`, `[client] toolbarMode = "minimal"`, a `[theme]` block. Also set it in
   `tests/conftest.py` via `streamlit.config.set_option` before the first `AppTest`, so the
   suite does not depend on the CWD. Worth doing for the minute per run and the Deploy button;
   no longer the headline. No bare expressions exist, so nothing changes on a page.

7. **`column_config` on the tables — brief #4**, with the caution: widths and `help=` change
   nothing the harness inspects; turning "Yes"/"No" into booleans changes values the doctrine
   fixtures compare, so do widths first, booleans table by table with the fixture diff read.

### B. Next, medium

8. **Engine into its own module — brief #7, ranked higher again.** Everything above the
   marker becomes `engine.py`; `app.py` opens with `from engine import *` (zero behaviour
   change: the page functions are closures over top-level names, and a star import keeps
   them). The engine half is where every doctrinal PR lands, so **schedule this in the gap
   after a merge wave, with no doctrinal branch open** — an open branch rebased across the
   split is a 15,000-line conflict. `conftest.engine` becomes an import; `build.spec` gains
   the module. Full suite after.

9. **Fragments for the picture controls, not lazy tabs.** Brief #2 needs `on_change="rerun"`
   on the tabs — `TabContainer.open` is `None` without it — which is the rerun-per-click the
   owner rejected on 2026-09-10, for a fraction of 0.24 s. What reruns too much today is the
   wheel Options popover on Timing: every toggle redraws 67 tables. Wrap "The charts, drawn"
   (selector, layout, popover, picture, download) in `@st.fragment`, and the Chart page's
   wheel block likewise, generating the SVG inside the fragment. `_persist()` works inside a
   fragment. **Watch:** `CHART_BOUNDS` is read at the top level today; inside the fragment the
   SVG must be regenerated from the widget's own value.

10. **Fix the Chart URL.** Drop `url_path="chart"` and accept root-only, or make no page the
    default so `/chart` works and `/` redirects; check `make_app(page="chart")` still resolves.

### C. Later, large

11. **A clickable wheel — brief #6**, after 5 and 8. Components v2, inline HTML around the
    SVG, a script that reports the clicked point back; a panel beside it with the planet's
    dignities, connections, receptions, lots and places, each cited. Keep `generate_hybrid_svg`
    pure and the SVG download. `st.image` gives the fullscreen wrapper for free and a component
    does not, so the component carries its own expand control. This is the frame the
    reference-frames tool later drops into.

12. **"Why this fired" row detail — brief #5, scoped down.** Most evaluators return display
    strings, not the satisfying values. Start with Strength & Weakness, which already carries
    paragraph-numbered labels and an answer key; `on_select="rerun",
    selection_mode="single-row"` there alone. The rest is engine work, one table at a time.

13. **Fonts — brief #8's second half.** A bundled symbol font through
    `server.enableStaticServing` needs a `static/` dir and a flag in `desktop_launcher.py`
    (the frozen build reads no config file). Test whether it retires the variation-selector
    rule before relying on it.

## Order of work

**Sequential, not parallel** (QA's point, 2026-09-15): items 1+2 rewrite the Chart-page region
every doctrinal build appends to, and item 8 moves 15,000 lines, so no doctrinal branch is
opened while a UI branch is open, and the UI branches run one at a time rather than in
worktrees side by side. The text-only rulings go before or after, not during.

1+2 (one branch, one fixture regeneration) → 3+4+10 (one branch: header, navigation, strip,
URL) → 5 → 6 → 7, each with the full suite. Then 8 alone, in a quiet window. Then 9. 11–13
when wanted. Items 3, 5, 9 and 11 need the live browser as they are built; the preview pane's
mouse-wheel scroll does not reach the page, `scrollTo` on `section[data-testid="stMain"]` does.

Model per branch, from the same-day discussion: 1+2, 6, 7 and 10 are Sonnet or Opus work;
3+4, 5, 8 and 11 Opus at high or xhigh effort; 9 and 12 are where a second opinion from the
larger model pays, since a wrong reading of the fragment model or of an evaluator's return
shape passes the tests and shows only in the browser.
