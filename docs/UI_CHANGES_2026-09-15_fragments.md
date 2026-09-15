# UI changes 2026-09-15 — the picture controls as fragments

Branch `fragments-2026-09-15` off `main` at `6bc4116`. Item 9 of
`UI_FRAMEWORK_REVIEW_2026-09-15_SECOND_OPINION.md`, and one leftover from the
short-headings branch.

## What was asked

Every control on a wheel reran the whole script. On the Chart page that is the layout radio,
the Bounds ring, the Dark wheel and the download; on Timing it is the view selectbox, the
layout radio and the five controls in the Options popover — and the Timing page draws **67
tables**, all of which were redrawn so that a toggle could move a tick on a picture. A
`@st.fragment` reruns only its own function on its own widgets' changes. The engine is cheap —
a whole run is about a fifth of a second — so this is about the redraw and the flicker, not
the compute.

Two fragments, one per page; the SVG generated **inside** each, from the widgets' own values;
`_persist()` still leaving the store keys in the state a full rerun would have produced; and
nothing the fragment draws outside its own body.

## What was built

### The Chart page: `_wheel_block()`

One `@st.fragment` holding, in order: the read-before-draw of `wheel_layout`, the two
`generate_hybrid_svg` calls, the centred `st.image(svg_code, width=560)` (Square) or
`st.image(svg_wide, width='stretch')` (Wide), and `_layout_control()` with the radio, the two
checkboxes and the download button. `_layout_control()` is unchanged in what it draws and now
nests inside the fragment, so the whole of the block is one function.

**The three intro captions, the circumpolar warning, `Calculation` and everything below stay
outside**, which is the point: they are what a click on the Bounds ring used to redraw.

### The SVG moved off the top level, and the top-level build is gone

`svg_code` and `svg_wide` were built at the top level from `CHART_BOUNDS` and `WHEEL_THEME`.
A fragment rerun does not re-run the top level, so a wheel built there is the **previous full
run's** wheel: the reader would click Bounds ring and see nothing move. Both calls are inside
the fragment now.

The top-level build was **dropped rather than kept beside it**. The consumers were checked
first and there are two, both on the Chart page: the `st.image` and the download button. No
other page and no other element reads either name. A by-product: the eight pages that never
draw a natal wheel no longer generate two of them on every run.

### What the fragment reads, and why it is read the way it is

The two checkboxes sit **under** the picture, and the picture has to exist before them, so the
fragment reads their values before drawing, exactly as the layout has been read since the
wheel took the centre of the page:

    _bounds = bool(st.session_state.get("chart_bounds", CHART_BOUNDS))
    _dark = bool(st.session_state.get("wheel_dark", WHEEL_DARK))
    _theme = VIEWER_THEME if _dark else None

The widget key holds the new value from the start of the rerun a click causes, so the wheel
the click asks for is the wheel drawn on that same fragment rerun. Behind it is **this run's
own top-level reading**, `CHART_BOUNDS` and `WHEEL_DARK`, which is what every other reader of
those two preferences sees: that is the value on the page's first render, before the checkbox
has a key at all, and after navigating back to the page, where Streamlit has dropped the
widget's state. On a fragment rerun the two constants are the last full run's values and the
widget key in front of them is what moves. Keeping them as the fallback also keeps
`CHART_BOUNDS` a live name: with the top-level SVG gone it had no other reader left.

`_theme` applies the rule the top level applies for `WHEEL_THEME` — the viewer's own theme
when the preference is on, `None` when it is off — so with the preference off the picture is
drawn exactly as it always has been.

### The Timing page: `_timing_wheel_block()`

One `@st.fragment` holding the whole of the "The charts, drawn" section: the subheader with
its tooltip, the three-column row (View selectbox, Wheel layout radio, Options popover with
its five controls), the `_ring_extras` helper, the ring and badge assembly, the
`generate_multiwheel_svg` call, the picture, its download button and the caption that states
PN IV's conventions. **The direction strips and all 67 tables stay outside.**

The revolution data is not recomputed: `pn4`, the natal chart, `lat`, `local_dt` and the rest
are the top level's, computed once per run before the tabs, and the fragment reads them from
the enclosing scope. What it regenerates is the SVG.

Every control in that block stands **before** the picture, so no read-before-draw is needed
there: each widget's own return is that fragment rerun's value, including the Dark wheel
checkbox, whose return becomes `_timing_theme` by the same rule as `_theme`. That is why
`theme=WHEEL_THEME` now appears six times in the UI half rather than nine — the six direction
strips, which are still drawn at the top level, are the six that remain.

### Persistence, which is the thing that could have broken quietly

`_persist()` writes the store key and, for a preference, the file, and it does that from
inside a fragment exactly as it does at the top level. This had to be checked rather than
assumed, because the store keys the fragment's widgets write — `_wheel_layout`,
`_chart_bounds`, `_wheel_dark`, `_timing_wheel_view`, `_wheel_order`, `_timing_bounds`,
`_timing_lots`, `_timing_rays`, `_timing_twelfths` — are read at the **top level on the next
full run**. A fragment that moved only its widget key would show the reader one wheel and hand
the rest of the app another, with every test still green.

It holds. Asserted the way the fault would show: set a checkbox inside the fragment, then
force a full rerun, then evaluate the app's **own** top-level expression — lifted out of the
UI half by AST, as `wheel_theme_rule()` in the theme tests already does — against the session
state that full rerun left. `CHART_BOUNDS` and `WHEEL_DARK` both come back with what the
fragment wrote.

### The leftover: the Planetary years heading

The Timing page's `Planetary years (Gr. Intr. VII.8, Figure 146) -- display only` was the one
heading the short-headings branch left carrying its own metadata. The heading is now
`Planetary years` and a caption under it reads

    Display only · Gr. Intr. VII.8, Figure 146

which is the shape `_finding()` prints from its `standing` and `citation` arguments
(`" · ".join(...)`), and `standing="Display only"` is the string four findings already use.
This is the only new page text on the branch.

## What the browser showed

The saving is observable only live: `AppTest` runs a fragment as part of a full run and cannot
show a partial rerun. The worktree's server ran on port 8519 and the preview tools reached it
by URL — `preview_start(url=...)` opens the pane without a launch file, which is how the
previous UI branch's measurement was blocked.

**One thing did not work and is worth recording.** Synthetic mouse clicks and key presses from
the pane did not reach the page at all — three attempts on the Bounds ring checkbox, by
element reference and by coordinate, at the emulated size and at the pane's own, left the box
checked and the picture unchanged. The widgets were driven from JavaScript instead
(`input.click()` on the checkboxes, a dispatched `ArrowDown` to open the BaseWeb select and a
dispatched click on its option), which produces a genuine widget change and a genuine rerun:
the checkbox state, the picture and the table count all moved as they should.

The method: take JavaScript references to every `[data-testid="stDataFrame"]` element, change
one control, wait, then count how many of those exact nodes are still
`document.contains(...)`-true, and whether the wheel `img` changed.

**A control first, because the measurement is worthless without one.** React can preserve DOM
nodes across a full rerun too, so the Chart page was measured with a control *outside* any
fragment — the "Moon under the rays to 15°" reading, further down the same page:

| Chart page, control changed | tables referenced | still attached | wheel `img` |
|---|---|---|---|
| **Bounds ring** (inside the fragment) | 7 | **7** | same element, `src` 93,730 → 68,458 bytes |
| Moon under the rays to 15° (outside it) | 7 | **0** | element replaced |

A full rerun detaches every table and replaces the picture element; the fragment rerun left all
seven tables in place and swapped the picture's bytes underneath it. The metric discriminates.

**Timing**, 67 tables in the DOM, the figure the review measured:

| Timing page, control changed | tables referenced | still attached | wheel `img` |
|---|---|---|---|
| **View**, Year over root → Month over year and root | 67 | **67** | same element, 106,562 → 122,402 bytes |
| **Options → Lots** | 67 | **67** | same element, 122,402 → 183,806 bytes |
| Also show the Ascendant's triplicity lords (outside it) | 67 | 62 | unchanged |

The Timing control is a weaker one than the Chart page's — it adds a table rather than changing
one in place, so React re-keys only around it and 62 of the 67 survive — but it moves in the
right direction, and the two fragment controls hold all 67 while changing the picture by
16 KB and 61 KB of SVG respectively. Options → Lots is exactly the case the review named: the
toggle that used to redraw 67 tables to add ticks to a wheel.

## What the tests showed

**`tests/fixtures/tables.json`: six lines, one per chart in the fixture, each the same
rename** — `"Planetary years (Gr. Intr. VII.8, Figure 146) -- display only"` becomes
`"Planetary years"`, the column list beside it unchanged. Nothing added, nothing lost, no
table moved page. Regenerated serially, as `conftest` requires under the flag.

**Four existing test files changed, and none of them weakened.** A fragment renders as a block
of its own, so the Chart page's picture and controls row are now that block's two children
rather than two of `main`'s, and what stands outside moved up one index:

| test | before | after |
|---|---|---|
| `test_chart_layout_2026_09_15.py`, six assertions | `_kids(at)[2]` / `[3]` for the wheel row and the controls row, captions at `[4:7]`, `Calculation` at `[7]` | `_frag_kids(at)[0]` / `[1]` through the new `_fragment(at)` helper; captions at `[3:6]`, `Calculation` at `[6]` |
| `test_chart_layout_2026_09_15.py::test_the_layout_is_read_before_the_control_is_drawn` | `"            _layout_control()\n"` | the same line at the fragment's indentation |
| `test_wheel.py::test_chart_page_names_the_wheel_and_offers_both_layouts` | the read-before-draw at its old indentation | the same, one level deeper |
| `test_theme_pictures_2026_09_15.py::test_the_ui_reads_the_theme_once_and_hands_one_value_to_every_picture` | `src.count("theme=WHEEL_THEME") == 9` | `== 6` (the six strips), plus `theme=_theme` twice and `theme=_timing_theme` once, plus both filtering expressions asserted verbatim; `"theme=VIEWER_THEME" not in src` kept, so no picture takes the viewer's theme unfiltered |

The theme test is the one that gained rather than lost: it used to check that nine pictures
took one value, and now checks that six take it and the other three apply the same rule to
their own fragment's checkbox, with the rule written out.

**One new file, twenty-seven tests.** `tests/test_fragments_2026_09_15.py`:

- both functions exist and carry `@st.fragment`, found by walking the UI half's AST for the
  decorator, and **they are the only two in the app** — so a third cannot appear without this
  file being read, a fragment that draws outside its body being a runtime fault the harness
  cannot see;
- the Chart fragment's body contains both `generate_hybrid_svg` calls and the UI half contains
  no others, with the two fallbacks (`CHART_BOUNDS`, `WHEEL_DARK`) asserted in the body; the
  Timing fragment contains its one `generate_multiwheel_svg` call and reads `pn4` rather than
  recomputing the bundle;
- the wheel still renders on both pages, at both layouts and both reading depths, decoded back
  out of the `st.image` data URL and checked to be an SVG;
- both wheels answer their own controls: the SVG changes when the Bounds ring is cleared and
  when the Timing view is changed;
- the store-key round trip, for `chart_bounds`/`CHART_BOUNDS` and `wheel_dark`/`WHEEL_DARK`,
  set inside the fragment and read back after a full rerun through the app's own expression;
  all six of the Timing fragment's store keys present and correct after one;
- the layout set on one page still reaches the other;
- containment: the Chart fragment holds the picture and the controls row and nothing else
  (the picture is a centring flex row at Square and the bare image at Wide), the four controls
  are the controls row's four children, the page's other two checkboxes are outside it, and
  the page around it is header, strip, fragment, three captions, `Calculation`;
- the Timing fragment holds exactly Subheader, the three-column controls row, Image,
  DownloadButton, Caption — **no `st.dataframe` inside it at all**, while the page still draws
  more than fifty outside it, and five of the page's six other pictures stay outside;
- the Planetary years heading carries no citation and no standing, its caption is the
  `_finding()` string, and the caption stands between the heading and the table.

Full suite: **2314 passed, 6 xfailed in 26.88s**, with `-n auto` on the owner's venv. 2287 to
2314 is those twenty-seven and nothing else.

`engine.py` is byte-identical to `main` at `6bc4116`, compared with `git diff` rather than by
reading it.
