# UI changes 2026-09-15 — the pictures in the viewer's theme, and escaping at the point of writing

Branch `theme-pictures-2026-09-15` off `main` at `a10709e`. Brief: item 5 of
`UI_FRAMEWORK_REVIEW_2026-09-15_SECOND_OPINION.md` — both halves of it, the palette and the
escaping — plus one line carried over from PR #41.

## What was asked

**5, first half.** Every picture is drawn on an opaque white rectangle with black and dark-grey
ink, and a picture is an SVG inside an `<img>`, where no page CSS reaches it: in the viewer's
dark theme each wheel is a white square on a dark page. Give the four renderers a palette,
keep every existing call and every existing test green, and check the result in the actual
colours rather than by reading the code.

**5, second half.** A Lot name with double quotes broke the revolution wheel (CI on PR #15);
`7faae89` removed the quotes from the name instead of fixing the generator. Escape every name,
label, place, chart name and date string where it is written, once.

**Carried over from PR #41.** `_chart_strip()` printed `f"{location_query} {lat:.2f},
{lon:.2f}"`, and a place entered as coordinates is already labelled `Manual [43.7792,
11.2463]`, so the strip read the coordinates twice.

## What was built

### The two palettes

One dict per theme, in the engine half beside the pictures' own constants, read once at the top
of each renderer (`pal = _wheel_palette(theme)`); the geometry does not know which palette it
is drawing in. `theme=None` — and anything the browser does not report as dark — is
`_PALETTE_LIGHT`, which is the constants the app has always drawn with, named rather than
changed:

| role | light | dark |
|---|---|---|
| `bg` the ground | `#ffffff` | `#0e1117` |
| `panel` the opaque fills on it (rim band, angle boxes, hub, a bound's cell) | `#ffffff` | `#0e1117` |
| `ink` text | `#000` | `#fafafa` |
| `rule` circles, spokes, the degree scale, a strip's axis | `#000000` | `#d2d6de` |
| `leader` / `leader_ring` the hairline from a tick to its glyph | `#666666` / `#777777` | `#8b919b` / `#9aa1ac` |
| `label` column heads, the sign-of-year lettering | `#444444` | `#b4b9c2` |
| `note` a bound's lord, the hub's added lines, a strip's partner | `#333333` | `#c2c7d0` |
| `axis_note` the strip's axis caption | `#555555` | `#a8adb6` |
| `tints` the sign band by triplicity | `#f7f7f7 #dedede #ededed #cdcdcd` | `#161a22 #2f3440 #202530 #40485a` |
| `shade` the sign of the year | `#e2e2e2` | `#2b313d` |
| `bound_tint` the bound the distribution stands in | `#ffe08a` | `#584717` |
| `horizon` Ascendant, Descendant, the distribution's arc | `#0000cc` | `#7aa7ff` |
| `meridian` MC and IC | `#1e7b1e` | `#5fcf5f` |
| `cusp` the dashed Alchabitius cusps and their numbers | `#a94442` | `#e0736f` |
| `badge` the marks and the distributor letters | `#b8860b` | `#e3b341` |
| `rings` inner, middle, outer ring text | `#000000 #1f3a93 #8b1a1a` | `#fafafa #8ab4ff #f08a80` |
| `now` the present on a strip | `#c00000` | `#ff5f56` |
| `strip_tint` the seven planets' bars | Saturn `#d9d9d9`, Jupiter `#cfe0f5`, Mars `#f5cdc7`, Sun `#fbe9a6`, Venus `#d4efd0`, Mercury `#f8ddb8`, Moon `#e2d9f3`, other `#eeeeee` | `#3a3a3a`, `#25384f`, `#4d2e2a`, `#4d431c`, `#26402a`, `#4a3a23`, `#37304a`, other `#2a2a2a` |

The dark ground is Streamlit's own default. `st.context.theme` was read in the installed
package before the value was chosen: it is a `StreamlitTheme` carrying `type` and nothing else
— `"dark"`, `"light"`, or `None` — built from the frontend's `color_scheme`, so there is no
background colour to read at runtime and the framework's default is the honest substitute.

The semantic colours move only as far as a dark ground requires: the horizon stays blue, the
meridian green, the cusps red, the badge gold, and the four triplicity tints stay four steps
apart, each at the distance from the ground its light counterpart keeps from white. `panel`
equals `bg` in the dark palette by choice: those fills exist to mask what is under them (the
shaded sector, the spokes, the sign band), not to be seen, and a lighter hub would read as a
second ring.

### The owner's ruling: white by default, the dark palette on request

Reviewing the first version of this branch, the owner ruled that the wheels keep their white
ground in **every** theme — that is what a chart on paper is — and that the dark palette is
offered rather than imposed. So the viewer's theme is no longer what a picture is drawn in; it
is consulted only when the reader asks for it.

**The preference**, modelled exactly on the bounds ring: widget key `wheel_dark`, store key
`_wheel_dark`, default `False`, added to `PREFERENCE_KEYS` so it survives the session — and
deliberately **not** added to `READINGS_REGISTRY`, because it is a display preference like the
bounds ring and the wheel layout, not a doctrinal reading. It does not appear in the Sources
page's table of readings in force, and the Reset there does not reach it.

**The control**, `_reading_checkbox("Dark wheel", "wheel_dark", "_wheel_dark", ...)`, sits
directly under the Bounds ring checkbox in two places: the Chart page's wheel block
(`_layout_control()`) and the Timing page's Options popover. The same widget key on both, as
the wheel layout radio already does — only one page renders per run, so there is no collision —
so the two wheels follow one setting and a reader who turns it on where the wheel is turns it
on everywhere. One sentence of help, written once as `WHEEL_DARK_HELP` and passed to both.

**What reaches a renderer** is one value, read beside the other readings:

    WHEEL_DARK = bool(_reading("wheel_dark", "_wheel_dark", False))
    WHEEL_THEME = VIEWER_THEME if WHEEL_DARK else None

Off — the default — every picture is handed `None` and draws exactly as it always has, in the
light theme and the dark. On, it is handed the viewer's own theme: `"dark"` takes the dark
palette; `"light"` reaches the renderer and resolves to the light palette, so the toggle
changes nothing in the light theme, which is what its help text says; `None`, which is what a
browser that has not reported yet and every `AppTest` run give, is the white wheel rather than
a guess.

### Where the theme comes from

In the UI half, at the top level, once:

    _context_theme = getattr(st.context, "theme", None)
    VIEWER_THEME = getattr(_context_theme, "type", None) if _context_theme is not None else None

Two `getattr`s rather than a `try`, so a Streamlit without the attribute and a theme reported
as `None` take the same road, which is the light palette. Under `AppTest` there is no browser
to report one and `VIEWER_THEME` is `None`; the pages render exactly as they did.

`theme=WHEEL_THEME` then goes to all nine renderer calls: the Chart page's two wheels (square and
wide), the Timing page's wheel — which is all five views, one call — and the six direction
strips (the Ascendant, a meridian point, the releaser, the house-master's hits, the small days,
the mighty days). The SVG download buttons are handed the same string that is on screen, so a
download keeps what the reader saw.

### Escaping

`xml.sax.saxutils.escape` was doing the work, and it escapes `&`, `<` and `>` and *not* quotes:
a name with a double quote closed the attribute it was written into. Two helpers replace it in
the renderers — `_esc_attr` = `html.escape(s, quote=True)` for an attribute value, `_esc_text` =
`html.escape(s)` for text content — and each value is escaped once, at the single place it is
written. Every site (each `file:line` in `app.py` after the change):

| site | value | before → after |
|---|---|---|
| 668, 670, 671 | the hub's name, time standard, place | `escape` → `_esc_text` |
| 673, 717, 1087 | the sect, in the hub and in both wide panels | none → `_esc_text` |
| 698 | the wide panel's point names | none → `_esc_text` |
| 719-720 | the wide panel's lords of the day and hour | `escape` → `_esc_text` |
| 875 | `data-chart`, `data-point` on a ring's points | `escape` → `_esc_attr` |
| 889 | a distributor's badge letters | `escape` → `_esc_text` |
| 905-906 | `data-chart`, `data-point` on a ring's extras (the Lots' own road) | `escape` → `_esc_attr` |
| 910 | an extra's short label | `escape` → `_esc_text` |
| 999 | `data-point` on a mark | `escape` → `_esc_attr` |
| 1002 | a mark's letters | `escape` → `_esc_text` |
| 1022 | the sign-of-year and sign-of-month lettering | none → `_esc_text` |
| 1044, 1049, 1051, 1053 | the hub's name, ring heads, `when` lines, added lines | `escape` → `_esc_text` |
| 1065, 1067 | the wide columns' ring labels and `when` lines | `escape` → `_esc_text` |
| 1209, 1280 | a strip's title | `escape` → `_esc_text` |
| 1217-1218 | `data-distributor`, `data-partner`, `data-aspect` | `escape` → `_esc_attr` |
| 1271 | a direction target the label pattern does not match | `escape` → `_esc_text` |
| 1297 | `data-target` on a hit | `escape` → `_esc_attr` |

Nothing is escaped twice: a ring's label, for instance, is written in the hub and again into
`data-chart`, and each write escapes the raw value it was handed, not the other's output.
`from xml.sax.saxutils import escape` stays at the head of the file — the sidebar's own
location box still uses it, and that line is not a picture.

### The strip's place

When `location_query` starts with `Manual [` the strip prints `f"{lat:.2f}, {lon:.2f}"` alone;
any other place keeps its name and its coordinates. A geocoded place is unaffected.

## What the tests and the pictures showed

**The light palette is the old one, to the byte.** Every picture was rendered from `main`'s
`app.py` and from this branch's and the strings compared: identical, with one exception, which
is the point of the branch — `data-target="Saturn's square (left)"` is now
`data-target="Saturn&#x27;s square (left)"`. The apostrophe was raw inside the attribute
before; it parses back to the same string, which is why the existing hit-strip test, which
reads through `ElementTree`, never saw it. No test compares a whole SVG string, so no expected
string had to be updated.

**The dark pictures, rasterised.** `rsvg-convert` 2.62.3 was present and all six variants (the
natal wheel square and wide, the revolution wheel square and wide, a distribution strip, the
hit strip) were rasterised at 900 and 1200 px and looked at. The wheels read: the sign band
separates into four steps, the bounds ring and its lords are legible, the blue horizon and
green meridian carry, the dashed cusps and their numbers stand out without glare, the gold
bound tint under the distribution is visible, and the three rings of a tri-wheel stay told
apart by colour. A census of every `fill=` and `stroke=` in the dark output finds no `#ffffff`,
no `#fff`, no `#000000` and no `#000` in any of the six: the only near-white is `#fafafa`,
which is the ink, and the only near-black is `#0e1117`, which is the ground and the masks on
it. Nothing is deliberately left white or black.

**`tests/fixtures/tables.json` did not change**, and neither did `tests/conftest.py`: the
pictures are not tables, and no heading moved.

**One existing assertion was updated**, `test_top_navigation_2026_09_15.py`'s check on the
strip's place: `place.endswith("43.78, 11.25")` → `place == "43.78, 11.25"`. The old assertion
would have passed either way, which is why it is tightened rather than replaced; the harness
enters coordinates directly, so the manual case is the one it renders. Nothing else in the
existing tests changed.

**Two new files, eighteen tests.**

`tests/test_svg_escaping_2026_09_15.py`, eight: each of the four pictures rendered with a chart
name, a place, a time standard, ring labels, a strip title, a distributor, a direction target
and a Lot name that each carry `"`, `'`, `&`, `<` and `>`; each output must parse, no attribute
value may contain a bare `&` or an angle bracket, and every name must come back out of the
parser as it went in. The Lot case is built the way the app builds it — a `LOT_DEFINITIONS` row
through `lot_by_id` into the ring's extras, as the Timing page's `_ring_extras` does — not by
editing the SVG.

`tests/test_theme_pictures_2026_09_15.py`, seventeen: `theme=None`, `"light"`, `""` and `"Light"` all
return the old picture byte for byte; the dark pictures parse, carry no white or black, and
have the dark ground on their backing rectangle; the two palettes answer for the same keys with
the same shapes; the geometry is identical between the palettes once the colours are struck out
(the strongest guard that the palette cannot move a line); the UI half reads the theme once
with the two `getattr`s and passes `theme=WHEEL_THEME` nine times and `VIEWER_THEME` never; and
the Chart and Timing pages render under `AppTest`, where no theme is reported. Seven of the
seventeen are the preference: the `WHEEL_THEME` expression is lifted out of the UI half by AST
and evaluated — the app's own rule, not a copy — against each theme with the preference off
(always `None`, always the light palette) and on (`"dark"` → the dark palette, `"light"` → the
light one, `None` → the light one); `_wheel_dark` is in `PREFERENCE_KEYS` and not in
`READINGS_REGISTRY`; and on each of the two pages the Dark wheel checkbox is found, is off, and
writes `_wheel_dark` when checked.

Full suite: **2213 passed, 6 xfailed in 95.91 s**, with `-n auto` on the owner's venv. 2188 to
2213 is those twenty-five new tests and nothing else. The engine half's whole share of the
preference is one line: `'_wheel_dark'` at the end of `PREFERENCE_KEYS`, which is a list of
display and reading keys, not doctrine.
