# UI changes 2026-09-15 — the clickable natal wheel

Branch `clickable-wheel-2026-09-15` off `main` at `a45e97a`. Item 11 of
`UI_FRAMEWORK_REVIEW_2026-09-15_SECOND_OPINION.md` (brief #6), after the engine
split and the fragments.

## What was asked

A wheel a reader can click: a planet, an angle or a sign, and a panel beside the
picture saying what the app already holds about it — its places, its dignities,
its connections, its receptions, the Lots it rules; for a sign, the sign's lords.
Components v2, the SVG passed in as data, a script that reports the click back,
`generate_hybrid_svg` kept pure and the SVG download kept as it is. `st.image`
gave the fullscreen wrapper for free and a component does not, so the component
carries an expand control of its own.

Three constraints govern the whole of it: the picture must not change, the panel
must invent no doctrine, and the click must rerun the fragment and not the page.

## What was built

### A. Handles in the SVG, and nothing else

`generate_hybrid_svg` now wraps each point's elements in
`<g class="pt" data-point="<name>" data-lon="<lon to six places>">` and each
sign's in `<g class="sign" data-sign="<0-11>">`. That is the convention the
revolution wheels have carried since 2026-09-10 (`_draw_ring_points`), borrowed
rather than invented. `_esc_attr` writes every value, as the four renderers have
done since a Lot name with a double quote closed an attribute and broke a wheel.

Fourteen handles: the seven planets, both nodes, the Lot of Fortune, and the four
angles under the names the Calculated Points table prints — Ascendant, Midheaven,
Descendant, Imum Coeli — so a click on an angle box reaches the same panel.

**The proof that nothing else moved** is a normalisation: strip `<g ...>` and
`</g>` from the branch's SVG and compare with `main`'s, string for string. Equal
for the default chart at five combinations of the flags (plain, wide, bounds ring,
wide with bounds, dark). The handles cost 1,266 bytes: 51,425 → 52,691 for the
plain square wheel.

### B. The component

Registered **once, at the module level** of `app.py` as `NATAL_WHEEL`
(`st.components.v2.component("natal_wheel", css=..., js=...)`), which is what the
API asks for: a registration wrapped up with its own mounting re-registers the
name on every instance. It is mounted inside `_wheel_block()`, the Chart page's
fragment, in place of both `st.image` calls, with `key="natal_wheel"` and
`on_picked_change=lambda: None` so that a click causes a rerun — of the fragment,
since the mount stands inside it.

**The envelope** is three keys and no more:

| key | value |
|---|---|
| `svg` | the SVG the renderer produced on this fragment rerun — the wide one at Wide, the square one at Square |
| `width` | `560` at Square, `"stretch"` at Wide |
| `signs` | the twelve signs' hover text, worked out in Python from `sign_summary` |

**The trigger values** are one string: `planet:<name>` for anything carrying
`data-point` (planets, nodes, the Lot of Fortune, the four angles) and
`sign:<0-11>` for a sign sector. `picked` is a trigger, not state, so the panel
stands for the rerun the click causes and no longer.

**The frontend** creates a child div under the component's own root (writing
`innerHTML` on the root itself would overwrite the CSS and HTML the component was
registered with), drops the SVG into it, sizes it from the envelope, and attaches
the click listeners. Hovering a sign raises a small absolutely-positioned div with
that sign's bounds and triplicity lords — the text was computed in Python and sent
in the envelope, so a hover is answered in the browser and never reaches the
server. The expand control is a button in the corner: it puts the wrapper at
`position: fixed; inset: 0` with the SVG fitted to the viewport's height, and the
button or the Escape key closes it. The keydown listener is taken off again by the
cleanup function the frontend returns.

`isolate_styles` is left at its default, so the component's CSS lives in a shadow
root and reaches nothing in the app. It styles the wrapper, the expand control and
the tooltip; the only rule that touches the picture is `cursor: pointer` on the
handles. **No fill and no stroke anywhere in it**: the palette is inside the SVG,
light or dark by the reader's own Dark wheel preference, and a component that
recoloured it would be overruling that preference. The Download button is
untouched.

### C. The panel

Two pure functions in the engine, display only:

- `point_summary(name, chart_data, essential, accidental, aspects, reception_data,
  classical_lots, topical_lots)` — the Chart page's own top-level names, with
  `chart_data` standing in for the places, the Ascendant and the sect, which are
  read out of it. Returns `None` for a name the wheel does not draw.
- `sign_summary(index, sect)` — the lords of one sign.

The sections, for a **planet** (each a small `st.dataframe` with `hide_index=True`
and a caption naming the page that carries the full table):

| section | rows | caption points to |
|---|---|---|
| Places | position, sign, whole-sign place, quadrant division, motion | the Chart page's own Calculated Points and Quadrant divisions |
| Essential | the truthy flags of `essential[name]` | the Dignities page |
| Accidental | the truthy flags of `accidental[name]` | the Dignities page |
| Connections | the rows of `aspects` naming it, seven of their columns | the Configurations page |
| Receptions | the rows of `reception_data` naming it | the Configurations page, under the rule in force |
| Lots | the classical and topical Lots whose lord is it | the Lots page |

For a **sign**: the lords (domicile, exaltation, triplicity by the chart's sect,
the participating lord), the five Egyptian bounds with their lords in order, and
the three faces — three tables, all pointing at the Reference page.

A section with no rows draws nothing, which is the honest reading: the default
chart has no reception at all, and an angle holds no dignity and rules no Lot.
Every row is lifted from a table another page already draws, so **no row carries a
citation that its own source table does not**: the topical Lots' `Source` column
travels with the row, the classical Lots have none and are given none.

## What the browser showed

The worktree's server on port 8520, the Chart page at 1400×900. `preview_start(url=...)`
reaches it without a launch file. Pointer events from the pane still do not reach
the page, so each click was dispatched from JavaScript on the element itself —
which produces a genuine trigger and a genuine rerun. The measurement is the
fragments branch's: take references to every `[data-testid="stDataFrame"]`, click,
wait, then count how many of those exact nodes are still `document.contains(...)`.

| click | tables referenced | still attached | tables after | the wheel |
|---|---|---|---|---|
| `[data-point="Sun"]`, Square | 7 | **7** | 7 → 11 | same element, same `<svg>` node |
| `[data-sign="2"]` (Gemini), Square | 7 | **7** | 7 → 10 | same element |
| `[data-point="Moon"]`, Wide | 7 | **7** | 7 → 12 | same element |

The panel appeared each time under the controls row, with the pick as its
subheader — "Sun", then "Gemini", then "Moon" — and the page's seven tables were
never redrawn. The Sun's places read 27° Sco 03', Scorpio, whole-sign place 10,
quadrant division 10, direct; Gemini's lords read Mercury, no exaltation, Saturn
by day with Jupiter partnering, and the five bounds in order.

**The handles are all there in the DOM**: fourteen `[data-point]` and twelve
`[data-sign]` inside the shadow root, at both layouts.

**Expand and Escape**: the button put the wrapper at `position: fixed`, 1416×916
over the viewport, with the wheel fitted to 900 px of height; the Escape key
returned it to 560 px and `position: relative`; the button toggles it both ways.
The hover tooltip read
`Gemini · Air / Bounds: Mercury to 6°, Jupiter to 12°, Venus to 17°, Mars to 24°,
Saturn to 30° / Triplicity (Diurnal): Saturn, with Jupiter partnering`, and hid
itself on mouseleave. No console error from the component; the only errors on the
page are the 404 of `/chart`, which is item 10 and not this branch.

**The preferences were read before and after** and are unchanged
(`~/.local/share/TraditionalAstrologyEngine/preferences.json`, same checksum). A
click on the wheel writes nothing at all; the one control this check did touch was
the layout radio, which was set to Wide and then back to Square, leaving
`_wheel_layout` as it was found.

## What the tests showed

`tests/fixtures/tables.json` is **unchanged** — AppTest cannot click a component,
so no panel renders under the harness and the page's inventory of tables is what
it was.

**One new file, twenty-eight tests**, `tests/test_clickable_wheel_2026_09_15.py`:

- the normalised SVG equals `main`'s at five flag combinations (skipped where the
  checkout cannot produce `main`'s `engine.py`, as the engine-split file does);
- the only added markup is `<g>` elements carrying `class` and their `data-`
  attributes, nothing else;
- every point and every sign has its handle, and each `data-lon` is the point's
  own longitude to six places;
- the three lines that write a handle all call `_esc_attr`;
- the component is registered exactly once, in the module body, bound to
  `NATAL_WHEEL`, under the name `natal_wheel`;
- the `css` and `js` arguments are plain names bound to string literals — so no
  user string can reach the component's own code;
- the CSS colours nothing in the picture (no `fill`, no `stroke`; the rules that
  select a handle set the cursor and nothing else);
- the Chart page mounts the wheel at both layouts and draws no panel, no panel
  table and no panel heading;
- the envelope carries the three keys, the SVG with its handles, and the twelve
  signs' text with Gemini's bounds and triplicity lords in it;
- `point_summary` for the Sun and the Moon on the default chart: the places equal
  `get_wsh_house` and `get_effective_house`, the dignities equal the truthy
  entries of `essential`/`accidental`, the connections equal the aspect rows
  naming the planet column by column, the receptions equal the reception rows
  naming it (none, on the default chart), the Lots equal the rows of the two Lot
  tables whose lord it is, with each row's own citation and no other;
- an angle carries its places and claims no dignity; a name the wheel does not
  draw returns nothing;
- `sign_summary(2)` is Gemini with Mercury as domicile lord and the five Egyptian
  bounds with their lords in order, and all twelve signs at both sects are checked
  against `EGYPTIAN_TERMS`, the triplicity table and `get_essential_rulers`.

**Four existing files moved with the change, none of them weakened.** The Chart
page's picture is no longer an `st.image`, so the assertions that read one now
read the component instead: `tests/conftest.py` gained `component_mounts()` and
`natal_wheel_envelope()` (the mount's own JSON envelope, which is where the SVG is
read from now), and `test_chart_layout_2026_09_15.py`,
`test_fragments_2026_09_15.py` and `test_wheel.py` use them. The fragment tests
gained an assertion rather than losing one: the Chart page now draws **no**
`st.image` at all.

Full suite: **2342 passed, 6 xfailed in 28.31s**, `-n auto` on the owner's venv.
2314 to 2342 is the twenty-eight new tests and nothing else.

**The engine diff, by AST against `main`**: one function changed,
`generate_hybrid_svg`; two added, `point_summary` and `sign_summary`; none
removed.

## The security note

The component's `html`, `css` and `js` are trusted code that Streamlit does not
sanitise, and the JS runs with the app page's own DOM privileges. Every one of
them on this branch is a string literal written in `app.py` and passed by name.
Nothing the reader supplies goes near them.

What the reader supplies reaches the component in `data` only, and only after the
renderer escaped it: the chart's name comes from the sidebar's saved-chart picker
or its name field, the place label from the geocoder or the typed query, and both
are written into the wheel's hub through `_esc_text`; the point and Lot names come
from the engine's own tables and are written into the handles through `_esc_attr`.
The twelve hover strings are built from `sign_summary`, which reads the engine's
tables and nothing else. The trigger comes back the other way as one short string,
and the panel reads it as `planet:<name>` — passed to `point_summary`, which
answers `None` for a name the wheel does not draw — or `sign:<0-11>`, of which
only digits are read.

The frozen build needs nothing new: the component's assets are inline strings
inside `app.py`, which `build.spec` already ships beside `engine.py`. There is no
asset directory, no static file and no external resource of any kind — the app is
offline, and the component loads nothing.
