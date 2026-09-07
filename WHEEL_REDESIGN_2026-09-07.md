# Chart wheel redesign — analysis and plan (2026-09-07)

Status: **BUILT 2026-09-07 on branch `wheel-2026-09-07`** (off `main` at
9b76b45), not yet merged. Commits: `980330b` true node; `06dd4e2` the wheel,
page and `tests/test_wheel.py`; a third moves the layout control beside the
square wheel. All decisions D1–D10 are in §4. Departures from the plan as
written, all measured in the browser: the Wheel layout radio sits in the
right-hand column beside the square wheel (a row above it pushed the wheel's
foot 24 px below the fold at 1280×720), and the layout is read from the
control's state before the control is drawn so that placement works; the
label-spreading pass keeps gaps signed on an unwrapped sequence because the
modular version leapfrogged neighbours in a tight stellium (caught by the new
tests); `LABEL_MIN_SEP` is 10.5°. Verified in the browser at 1280×720: the
square wheel is fully visible on load, the fullscreen arrows expand it, the
Wide layout fills the window width with the positions panel, the 1240 chart's
Gemini stellium and the 1982 chart's Scorpio cluster read, the hub names the
loaded chart and reads "Transits" otherwise. A throwaway prototype was built in the session scratchpad to prove
the three uncertain points; its code is in Appendix A so the record survives.

Owner's request (verbatim in spirit): a more robust, more legible wheel, closer to
the two reference charts (a Solar-Fire-style natal wheel: whole-sign house numbers
on the outer rim, Alchabitius quadrant numbers on an inner ring, planet labels
running radially glyph → degree → sign → minute). Keep the dashed Alchabitius
cusp convention. Let the wheel expand to the window like the tables do. Replace
"Whole-Sign Hybrid Chart" with the entered chart name.

---

## 1. How the wheel is built today

| Item | Where | What |
|---|---|---|
| Renderer | `generate_hybrid_svg()` at `app.py:186-474` | One pure function, no Streamlit calls, returns an SVG string. ~290 lines with comments. |
| Call | `app.py:6551` | `svg_code = generate_hybrid_svg(chart_data, location_query, lat, lon, local_dt, tz_name)` — the chart name is not passed. |
| Display | `page_chart()` at `app.py:6686` | `st.iframe(srcdoc html, height=WHEEL_HEIGHT)` with `WHEEL_HEIGHT = 400`, left column of a `[1, 1]` split. The 400 px was measured on 2026-09-06 as the most that is fully visible on load at 1280×720. |
| Canvas | viewBox 900×900 | Circles at r = 410 (outer), 345 (zodiac), 210 (houses), 110 (hub). |
| Sign band | r 345–410 | 65 px; sign glyph 16 px bold; ticks every 5° *outside* the zodiac circle, no 1° scale. |
| House-number band | r 110–210 | **100 px, a third of the radius**, holding twelve whole-sign numbers at 13 px. This is the band the owner calls wasted real estate. |
| Planet zone | r 210–345 | 135 px, the narrowest usable zone on the wheel. |
| Orientation | `lon_to_angle()` | The **sign boundary** of the rising sign sits at 9 o'clock (`asc_sign_start`), so the horizon line is tilted by the Ascendant's degree within its sign. Both reference charts put the **Ascendant degree** at 9 o'clock. |
| Labels | lines 380–470 | Two horizontal text lines per point (glyph+degree over sign+minute). Points within 6° form a cluster; members are stacked **vertically in screen pixels** (30 px apart) from an anchor. On the 1982 chart this stacks Jupiter/Mercury/Sun/Venus down across the 11th–12th house boundary, well away from their degrees. Dashed grey leaders. |
| Angles | lines 424–436 | Asc/Des blue, MC/IC green, 2 px **dashed** from the hub to the label — visually the same weight as the cusp lines. |
| Cusps | lines 346–356 | `#a94442`, 1.5 px, `stroke-dasharray="4"`, drawn **only inside the house band** (r 110–210); they never reach the zodiac ring. |
| Hub | lines 490–501 | Hard-coded `Whole-Sign Hybrid Chart`, then place, lat/lon, date-time [tz], `Sect:`, `Layout: Whole Sign + Alchabitius Cusps`, `Zodiac: Tropical`. |
| Fonts | line 203 | System fonts by name: `'Noto Sans Symbols', 'Segoe UI Symbol', 'DejaVu Sans'`; glyphs are Unicode with U+FE0E. Nothing is bundled (`build.spec` datas: `app.py`, `atlas.db`, icon). The desktop build shows the page through pywebview, i.e. the OS web engine, so the same system-font dependency applies there. Installed here: Noto Sans Symbols, Noto Sans Symbols 2, DejaVu Sans. |
| Chart name sources | `app.py:6306`, `app.py:6391` | `st.session_state["chart_picker"]` (a saved chart's name, or the sentinel `-- New Chart --`) and the `Chart Name (for saving)` text input `new_chart_name`. Nothing else names a chart. |
| Tests | `Executable/tests` | No test reads the SVG. `test_pages_render.py` inventories `st.dataframe` only, so swapping the iframe for an image element does not touch `tests/fixtures/tables.json`. A probe confirmed `AppTest` runs `st.image(<svg string>)` without exception. |

One incidental finding: the app plots the **mean** node (`swe.MEAN_NODE`,
`app.py:118`), the references use the **true** node (04♋39 vs the app's 06♋05 on
the 1982 chart). Decided the same day: switch to the true node (D7).

---

## 2. Feasibility, question by question

**Radial labels (glyph, degree, sign, minute along the radius).** Yes. The
references do not rotate text: each element is upright, placed at a decreasing
radius on the same bearing. That is four `<text>` elements per point at fixed
radii. Proven in the prototype (Appendix A, Fig. 1).

**Whole-sign numbers on the outer rim, quadrant numbers on a narrow inner ring.**
Yes. New rings: rim band for WS numbers, sign band with a 1° scale, a wide planet
zone, a 30 px quadrant ring, a hub. The planet zone grows from 135 px to about
250 px (in a 1000 viewBox), which is where the legibility comes from.

**Expand to full window like the tables.** Yes, and it is a one-line change.
`st.image()` accepts an SVG string (Streamlit 1.62, `elements/image.py:75`) and
renders it inside the same `withFullScreenWrapper` the dataframe uses (verified in
the built frontend chunk `ImageList.*.js`). The prototype shows the hover button,
and clicking it fills the window height. `st.iframe` has no such wrapper, which
is why the current wheel cannot expand. Two consequences of the swap:
the SVG is served as an `<img>` data URI, so it cannot use page CSS, web fonts
or scripts — the wheel uses none — and it stays vector, so the fullscreen view is
crisp. `width=400` (an integer) keeps the on-load-visible constraint measured on
2026-09-06.

**Keep the dashed Alchabitius lines.** Kept, extended to run from the quadrant
ring to the zodiac ring so each cusp is readable against the degree scale.

**Chart name in the hub.** Yes: one new parameter to the renderer and a
three-line derivation at the call site (§5, step 2).

---

## 3. Target design

Viewbox 1000 × 1000, centre (500, 500). All text upright. Font stack unchanged.

| Ring | Radii | Content |
|---|---|---|
| Rim band | 462–492 | Whole-sign house numbers 1–12, 17 px bold, centred on each sign. Sign-boundary spokes cross this band and the sign band. |
| Sign band | 402–462 | Sign glyph 30 px at mid-sign. Fill by triplicity, four greys (D3). Degree scale on the inner edge: 1° = 5 px, 5° = 10 px, 10° = 14 px. |
| Angle boxes | on the sign band | Small white boxes at the Asc, MC, Des, IC bearings showing `dd°` over `mm'`, coloured as the axis (blue horizon, green meridian), as the references draw the Asc and MC. |
| Planet zone | 152–402 | Per point, on one bearing: glyph 34 px at r 344, degree 18 px bold at 306, sign 19 px at 272, minute 15 px at 242, `℞` 15 px black at 214 when the ephemeris speed is negative (nodes included, D9). A 10 px tick on the zodiac ring at the true degree and a hairline from the tick to the glyph. Alternate members of a crowded run step 30 px inward (D8). |
| Quadrant ring | 122–152 | Alchabitius house numbers 1–12 at each house's mid-arc, 14 px bold, in the cusp colour `#a94442`. |
| Cusps | 122 → 402 | Dashed `#a94442` 1.4 px (`6 4`); cusps 1/7 solid blue 2.6 px, 10/4 solid green 2.6 px (D4). |
| Hub | r < 122 | Chart name (17 px bold), "Natal chart", date and time, time standard, place, lat/long in D°M′, sect (bold), "Whole sign · Alchabitius", "Tropical · True node". Nine lines at 14 px spacing fit the 244 px hub. |

**Orientation.** The rising sign's boundary at 9 o'clock, zodiac increasing
counter-clockwise, as today (D1). Sign glyphs step aside from an angle box.

**Collision handling.** Sort points by bearing; relax pairwise on the circle until
every neighbouring pair is ≥ `MIN_SEP` apart (9.5° in prototype v2; 10–11° in
the build), then stagger every other member of a displaced run 30 px inward,
which is what Solar Fire does for stellia (D8).
The 1240 test chart has five points within 20° in Taurus–Gemini and the 1982 chart
four within 9° in Scorpio; both spread within their half of the wheel. A seven-body
conjunction still fits (7 × 10° = 70°).

**Points drawn.** Seven planets, north node, south node, Lot of Fortune (D2 taken). Angles are drawn as axis lines and boxes, not as labelled
points, so they no longer compete with planets for label space (today "Asc" and
"MC" are members of the clusters, which is what pushed the Scorpio stack down).

---

## 4. Decisions (all taken 2026-09-07)

- **D1 Orientation. DECIDED: keep the current convention** — the rising
  sign's boundary at 9 o'clock, zodiac counter-clockwise, whole-sign sectors on
  the twelve clock positions. Consequence: the angle boxes sit wherever the
  Ascendant and MC fall within their signs, so a sign glyph within 7° of an angle
  box steps 8° aside along the band (prototype v3).
- **D2 South node. DECIDED: draw ☋.**
- **D3 Sign-band shading. DECIDED: by triplicity.** The three signs of each
  triplicity share one tint: fire `#f7f7f7`, earth `#dedede`, air `#ededed`,
  water `#cdcdcd` (greys, so the wheel stays black and white; the tints are four
  constants if colour is ever wanted).
- **D4 Axis colours. DECIDED: keep** blue horizon, green meridian, solid and
  heavier than the dashed cusps.
- **D5 Hub name fallback. DECIDED: "Transits".** With no saved chart selected
  and no name typed, the name line reads `Transits`; the place line stays.
- **D6 Retrograde glyph. DECIDED: ℞ in black.**

- **D7 Node. DECIDED 2026-09-07: true node.** One constant at `app.py:118`
  (`swe.MEAN_NODE` → `swe.TRUE_NODE`). Blast radius: the Calculated Points table,
  the wheel, and four doctrines that measure a planet's distance from the Head or
  Tail (Weakness 99 at ~4941, Abu Ma'shar's condition at ~5543, the Moon's
  eclipse test at ~5712, Corruption of the Moon at ~5893). The doctrine fixtures
  build their own node positions, so no test breaks; the tables fixture holds
  headings and columns only. Check the six test charts' node-dependent rows by
  eye after the switch (the 1982 chart moves from 06♋05 to 04♋40, matching the
  reference).

- **D8 Label depth. DECIDED: deeper.** The stack moves inward to 0.86, 0.76,
  0.68, 0.60 and 0.53 of the ring radius (glyph 344, degree 306, sign 272, minute
  242, ℞ 214 in the 1000 viewBox), with a hairline from the ring tick to the
  glyph, as the references do. Crowded runs stagger alternate members 30 px
  inward. `MIN_SEP` 9.5° in prototype v2; tune 10–11° in the build.

- **D9 Retrograde marks. DECIDED: every point, by actual motion.** ℞ (red, at
  the foot of the stack) for any point whose longitude speed from the ephemeris
  is negative; the south node shares the north node's speed. Today the wheel
  excludes the nodes from the mark (`app.py:335`). Finding: the **true** node is
  not always retrograde. Swisseph gives it +0.013°/day on 1982-11-19 16:44 UT,
  so under this rule the node shows no ℞ on that chart, while a mean node would
  always show one. If the owner prefers the traditional "nodes are always
  retrograde" mark, that is a one-line override; the honest ephemeris motion is
  the default.

- **D10 Full window width.** A square wheel in Streamlit's fullscreen is bound
  by the window height (720 px tall at 1280×720; ~1060 at 1920×1080); no square
  can use more width than that. To use the width, the composition itself must
  be wide. Prototype v2 adds a wide variant (1760×1000 viewBox: the same wheel
  plus a positions panel with WS place, quadrant house, motion, the twelve
  cusps and the sect line). Its fullscreen fills the width, and the wheel is
  the same size as the square's fullscreen, so the gain is the panel, not a
  bigger wheel. Proposed: a **Layout** radio on the Chart page, "Square" (the
  400 px column wheel, default) or "Wide" (full-width image under the caption,
  ~700 px tall at 1280, so it scrolls); the fullscreen button expands whichever
  is shown. Streamlit's fullscreen wrapper expands one element only, so a
  single element cannot be square on the page and wide in fullscreen.

---

## 5. Implementation plan

Branch `wheel-2026-09-07` off `main`. One commit per step. `main` untouched until
the branch is reviewed in the browser.

0. **Baseline.** `cd Executable && ../.venv/bin/python -m pytest -q -m "not matrix"`;
   record the count (expected green).
1. **Switch to the true node** (D7) first, as its own commit, and eyeball the
   node rows on the six charts.
1. **Rewrite the renderer** in place, same name, new signature
   `generate_hybrid_svg(chart_data, chart_name, location_query, lat, lon, dt_local, tz_name)`,
   per §3 and D8–D10 (a `wide=False` flag selects the panel variant). Keep it a pure function inside `app.py`: `build.spec` bundles `app.py`
   as *data* (not analysed), so a sibling module would silently be missing from
   the frozen build unless added to `datas`. Give the `<svg>` explicit
   `width`/`height` equal to the viewBox (Streamlit asks for this on SVGs) and a
   white `<rect>` background rather than a CSS background, since `<img>` rendering
   ignores inline `style` less reliably than attributes. Escape every user string.
2. **Chart name at the call site** (`app.py:6551`):
   ```python
   picked = st.session_state.get("chart_picker")
   chart_name = (picked if picked and picked != "-- New Chart --"
                 else new_chart_name.strip() or "Transits")   # D5
   ```
   Known edge: load a saved chart, then edit the date — the hub keeps the saved
   name. Acceptable; note it in the comment.
3. **Display.** In `page_chart()`, replace the `st.iframe(...)` and the
   `WHEEL_HEIGHT` constant with `st.image(svg_code, width=400)`; keep the
   two-column layout and update the measured-height comment (the 400 px budget
   still holds; the fullscreen button is now the path to the big view).
4. **Tests.** New `tests/test_wheel.py`, run on every chart in `conftest.CHARTS`:
   the SVG parses as XML; the chart name and all point glyphs are present; twelve
   rim numbers and twelve quadrant numbers; `Whole-Sign Hybrid Chart` is gone; and
   a unit test of the spread function (no neighbouring bearings closer than
   `MIN_SEP`, order preserved, input already-separated returned unchanged). The
   tables fixture needs no regeneration.
5. **Browser acceptance** at 1280×720 and 1440×900, six test charts: wheel first
   and fully visible on load; fullscreen button expands it; 1240 (Gemini stellium)
   and 1982 (Scorpio cluster) legible in fullscreen; glyphs render (no tofu);
   dark theme looks intentional (white wheel on dark, as the prototype).
6. **Desktop build check.** Windows `Segoe UI Symbol` carries every glyph used
   (planets, signs, nodes, ⊗, ℞), so the frozen build needs no font. Optional
   hardening if identical rendering everywhere is wanted: subset Noto Sans Symbols
   to the ~25 glyphs and embed it as a data-URI `@font-face` inside the SVG
   (allowed inside `<img>`, ~20 KB).
7. **Record.** Update this file's status line, the memory note, and the tests
   README paragraph in `test_pages_render.py`'s docstring if the fixture rule
   changes (it should not).

Estimate: the renderer rewrite is ~250 lines; with tests and two browser passes,
one working day.

---

## 6. Risks and mitigations

- **Crowded stellia** — handled by the spread; verify on 1240 and 1982, and add a
  synthetic seven-body test if wanted.
- **Hub text is small at 400 px** — by design; fullscreen is the reading view.
  Do not enlarge the hub at the planet zone's expense.
- **`<img>` sandbox** — no CSS variables, no scripts, no external fonts. None used.
- **Column width** — at 1280 px the left column is ~560 px, so an integer
  `width=400` is honoured; at narrower windows Streamlit shrinks it and the
  fullscreen button remains.
- **Fonts on other machines** — system-font dependency is unchanged from today;
  step 6 is the fix if it ever bites.

---

## Appendix A — prototype v1 (scratchpad, not part of the app)

Superseded by v2 (Appendix B) on the same day; kept because the diff shows the
label-depth change.

Built 2026-09-07 to prove §2. Computes the 1982 chart with swisseph directly and
writes `proto.svg`; a two-line Streamlit host showed it via `st.image(svg, width=400)`
and the fullscreen button worked. Positions matched the reference (Asc 18♑31,
MC 16♏54, cusps 18♑ 25♒ 06♈ 16♉ 08♊ 28♊ 18♋ 25♌ 06♎ 16♏ 08♐ 28♐).

```python
"""Throwaway prototype of the redesigned wheel. Standalone: computes the
Jason Armfield chart with swisseph directly, no import of app.py."""
import math
from html import escape
from pathlib import Path

import swisseph as swe

LAT, LON = 45.37334, -84.95533
jd = swe.julday(1982, 11, 19, 16 + 44 / 60.0, swe.GREG_CAL)
IDS = {'Sun': swe.SUN, 'Moon': swe.MOON, 'Mercury': swe.MERCURY, 'Venus': swe.VENUS,
       'Mars': swe.MARS, 'Jupiter': swe.JUPITER, 'Saturn': swe.SATURN, 'North Node': swe.MEAN_NODE}
pdata = {n: swe.calc_ut(jd, i)[0] for n, i in IDS.items()}
cusps, ascmc = swe.houses(jd, LAT, LON, b'B')
ASC, MC = ascmc[0], ascmc[1]
sun, moon = pdata['Sun'][0], pdata['Moon'][0]
diurnal = (sun - ASC) % 360 > 180
fortune = (ASC + moon - sun) % 360 if diurnal else (ASC + sun - moon) % 360

SIZE = 1000
C = 500
R_RIM = 492
R_WS_IN = 462
R_SIGN_IN = 402
R_GLYPH, R_DEG, R_SIGN, R_MIN, R_RX = 366, 334, 308, 284, 262
R_Q_OUT, R_Q_IN = 152, 122
FONT = "'Noto Sans Symbols', 'Segoe UI Symbol', 'DejaVu Sans', sans-serif"
SIGNS = ['♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑', '♒', '♓']
GLYPH = {'Sun': '☉', 'Moon': '☽', 'Mercury': '☿', 'Venus': '♀', 'Mars': '♂',
         'Jupiter': '♃', 'Saturn': '♄', 'North Node': '☊', 'Lot of Fortune': '⊗'}
VS = '︎'

def ang(lon):
    """Ascendant at 9 o'clock, zodiac increasing counter-clockwise."""
    return (lon - ASC + 180.0) % 360.0

def xy(r, a):
    t = math.radians(a)
    return C + r * math.cos(t), C - r * math.sin(t)

def sector(r_in, r_out, a0, a1):
    x0o, y0o = xy(r_out, a0); x1o, y1o = xy(r_out, a1)
    x0i, y0i = xy(r_in, a0); x1i, y1i = xy(r_in, a1)
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return (f'M{x0o:.1f},{y0o:.1f} A{r_out},{r_out} 0 {large} 0 {x1o:.1f},{y1o:.1f} '
            f'L{x1i:.1f},{y1i:.1f} A{r_in},{r_in} 0 {large} 1 {x0i:.1f},{y0i:.1f} Z')

def text(x, y, s, size, weight='normal', fill='#000', anchor='middle'):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" dominant-baseline="central" '
            f'font-size="{size}" font-weight="{weight}" fill="{fill}">{s}</text>')

def dms(lon):
    d = int(lon % 30); m = int(round((lon % 1) * 60))
    if m == 60: d, m = d + 1, 0
    return d, m

out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {SIZE} {SIZE}" width="{SIZE}" height="{SIZE}" '
       f'style="font-family:{FONT}">', f'<rect width="{SIZE}" height="{SIZE}" fill="#fff"/>']

# sign band, rim numbers, boundary spokes
asc_sign = int(ASC // 30)
for i in range(12):
    a0, a1 = ang(i * 30), ang(i * 30 + 30)
    out.append(f'<path d="{sector(R_SIGN_IN, R_WS_IN, a0, a1)}" fill="{"#ececec" if i % 2 else "#f7f7f7"}"/>')
    out.append(f'<path d="{sector(R_WS_IN, R_RIM, a0, a1)}" fill="#fff"/>')
    gx, gy = xy((R_SIGN_IN + R_WS_IN) / 2, ang(i * 30 + 15)); out.append(text(gx, gy, SIGNS[i] + VS, 30))
    hx, hy = xy((R_WS_IN + R_RIM) / 2, ang(i * 30 + 15)); out.append(text(hx, hy, str((i - asc_sign) % 12 + 1), 17, 'bold'))
    x0, y0 = xy(R_SIGN_IN, a0); x1, y1 = xy(R_RIM, a0)
    out.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="#000" stroke-width="1.2"/>')

# degree scale
for d in range(360):
    ln = 14 if d % 10 == 0 else 10 if d % 5 == 0 else 5
    x0, y0 = xy(R_SIGN_IN, ang(d)); x1, y1 = xy(R_SIGN_IN + ln, ang(d))
    out.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="#000" stroke-width="{0.9 if ln > 5 else 0.5}"/>')

for r, w in ((R_RIM, 2.5), (R_WS_IN, 1.2), (R_SIGN_IN, 1.6), (R_Q_OUT, 1.2), (R_Q_IN, 1.6)):
    out.append(f'<circle cx="{C}" cy="{C}" r="{r}" fill="none" stroke="#000" stroke-width="{w}"/>')

# cusps: dashed, angles solid; quadrant numbers at mid-house
AXIS = {0: '#0000cc', 6: '#0000cc', 9: '#1e7b1e', 3: '#1e7b1e'}
for i, cl in enumerate(cusps):
    x0, y0 = xy(R_Q_IN, ang(cl)); x1, y1 = xy(R_SIGN_IN, ang(cl))
    if i in AXIS:
        out.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="{AXIS[i]}" stroke-width="2.6"/>')
    else:
        out.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="#a94442" stroke-width="1.4" stroke-dasharray="6 4"/>')
    mid = cl + ((cusps[(i + 1) % 12] - cl) % 360) / 2
    mx, my = xy((R_Q_OUT + R_Q_IN) / 2, ang(mid)); out.append(text(mx, my, str(i + 1), 14, 'bold', '#a94442'))

# angle boxes
for lon, col in ((ASC, '#0000cc'), (MC, '#1e7b1e'), ((ASC + 180) % 360, '#0000cc'), ((MC + 180) % 360, '#1e7b1e')):
    d, m = dms(lon); bx, by = xy((R_SIGN_IN + R_WS_IN) / 2, ang(lon))
    out.append(f'<rect x="{bx-19:.1f}" y="{by-17:.1f}" width="38" height="34" rx="3" fill="#fff" stroke="{col}" stroke-width="1.2"/>')
    out.append(text(bx, by - 8, f'{d:02d}°', 13, 'bold', col)); out.append(text(bx, by + 8, f"{m:02d}'", 13, 'bold', col))

# planets: radial stack, spread in bearing until neighbours are MIN_SEP apart
points = [(n, pdata[n][0], pdata[n][3]) for n in IDS] + [('Lot of Fortune', fortune, 1.0)]
points.sort(key=lambda p: ang(p[1]))
disp = [ang(p[1]) for p in points]
MIN_SEP = 8.0
for _ in range(200):
    moved = False
    for k in range(len(disp)):
        j = (k + 1) % len(disp)
        gap = (disp[j] - disp[k]) % 360
        if gap < MIN_SEP:
            push = (MIN_SEP - gap) / 2
            disp[k] = (disp[k] - push) % 360; disp[j] = (disp[j] + push) % 360; moved = True
    if not moved:
        break
for (name, lon, speed), a_disp in zip(points, disp):
    x0, y0 = xy(R_SIGN_IN, ang(lon)); x1, y1 = xy(R_SIGN_IN - 10, ang(lon))
    out.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="#000" stroke-width="1.6"/>')
    x2, y2 = xy(R_GLYPH + 20, a_disp)
    out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#555" stroke-width="0.8"/>')
    d, m = dms(lon)
    gx, gy = xy(R_GLYPH, a_disp); out.append(text(gx, gy, GLYPH[name] + VS, 34))
    dx_, dy_ = xy(R_DEG, a_disp); out.append(text(dx_, dy_, f'{d:02d}°', 18, 'bold'))
    sx, sy = xy(R_SIGN, a_disp); out.append(text(sx, sy, SIGNS[int(lon // 30) % 12] + VS, 19))
    mx, my = xy(R_MIN, a_disp); out.append(text(mx, my, f"{m:02d}'", 15))
    if speed < 0 and name not in ('Sun', 'Moon', 'North Node', 'Lot of Fortune'):
        rx, ry = xy(R_RX, a_disp); out.append(text(rx, ry, '℞' + VS, 15, fill='#a94442'))

# hub
out.append(f'<circle cx="{C}" cy="{C}" r="{R_Q_IN - 1}" fill="#fff"/>')
lines = [('Jason Armfield', 17, 'bold'), ('Natal chart', 12, 'normal'), ('19 Nov 1982  11:44', 12, 'normal'),
         ('EST (UTC−5)', 11, 'normal'), ('Petoskey, MI (US)', 12, 'normal'), ('45°22′N  84°57′W', 11, 'normal'),
         ('Diurnal', 12, 'bold'), ('Whole sign · Alchabitius', 10, 'normal'), ('Tropical · Mean node', 10, 'normal')]
y = C - 7 * len(lines)
for s, size, w in lines:
    out.append(text(C, y, escape(s), size, w)); y += 14
out.append('</svg>')
Path(__file__).with_name('proto.svg').write_text(''.join(out))
```

Host used to prove the fullscreen button:

```python
import streamlit as st
from pathlib import Path
st.set_page_config(layout="wide")
svg = Path(__file__).with_name('proto.svg').read_text()
left, right = st.columns([1, 1])
with left:
    st.image(svg, width=400)   # hover: Streamlit's own Fullscreen button
```


## Appendix B — prototype v2 (true node, deeper stack, stagger, wide variant)

```python
"""Throwaway prototype v2: true node, south node, planet stack moved inward
with staggering, and a WIDE variant (wheel + positions panel) for fullscreen.
Standalone: no import of app.py. Writes proto.svg and proto_wide.svg."""
import math
from html import escape
from pathlib import Path

import swisseph as swe

LAT, LON = 45.37334, -84.95533
jd = swe.julday(1982, 11, 19, 16 + 44 / 60.0, swe.GREG_CAL)
IDS = {'Sun': swe.SUN, 'Moon': swe.MOON, 'Mercury': swe.MERCURY, 'Venus': swe.VENUS,
       'Mars': swe.MARS, 'Jupiter': swe.JUPITER, 'Saturn': swe.SATURN, 'North Node': swe.TRUE_NODE}
pdata = {n: swe.calc_ut(jd, i)[0] for n, i in IDS.items()}
cusps, ascmc = swe.houses(jd, LAT, LON, b'B')
ASC, MC = ascmc[0], ascmc[1]
sun, moon = pdata['Sun'][0], pdata['Moon'][0]
diurnal = (sun - ASC) % 360 > 180
fortune = (ASC + moon - sun) % 360 if diurnal else (ASC + sun - moon) % 360
south = (pdata['North Node'][0] + 180) % 360

SIZE = 1000
C = 500
R_RIM = 492
R_WS_IN = 462
R_SIGN_IN = 402
# v2: the stack sits well inside the zone, as the reference does (0.86 .. 0.53 of ring radius)
R_GLYPH, R_DEG, R_SIGN, R_MIN, R_RX = 344, 306, 272, 242, 214
STAGGER = 30          # every other member of a crowded run moves this much inward
R_Q_OUT, R_Q_IN = 152, 122
FONT = "'Noto Sans Symbols', 'Segoe UI Symbol', 'DejaVu Sans', sans-serif"
SIGNS = ['♈', '♉', '♊', '♋', '♌', '♍', '♎', '♏', '♐', '♑', '♒', '♓']
GLYPH = {'Sun': '☉', 'Moon': '☽', 'Mercury': '☿', 'Venus': '♀', 'Mars': '♂', 'Jupiter': '♃',
         'Saturn': '♄', 'North Node': '☊', 'South Node': '☋', 'Lot of Fortune': '⊗'}
VS = '︎'
asc_sign = int(ASC // 30)


def ang(lon):
    return (lon - ASC + 180.0) % 360.0


def xy(r, a, cx=C):
    t = math.radians(a)
    return cx + r * math.cos(t), C - r * math.sin(t)


def sector(r_in, r_out, a0, a1):
    x0o, y0o = xy(r_out, a0); x1o, y1o = xy(r_out, a1)
    x0i, y0i = xy(r_in, a0); x1i, y1i = xy(r_in, a1)
    large = 1 if (a1 - a0) % 360 > 180 else 0
    return (f'M{x0o:.1f},{y0o:.1f} A{r_out},{r_out} 0 {large} 0 {x1o:.1f},{y1o:.1f} '
            f'L{x1i:.1f},{y1i:.1f} A{r_in},{r_in} 0 {large} 1 {x0i:.1f},{y0i:.1f} Z')


def text(x, y, s, size, weight='normal', fill='#000', anchor='middle'):
    return (f'<text x="{x:.1f}" y="{y:.1f}" text-anchor="{anchor}" dominant-baseline="central" '
            f'font-size="{size}" font-weight="{weight}" fill="{fill}">{s}</text>')


def dms(lon):
    d = int(lon % 30); m = int(round((lon % 1) * 60))
    if m == 60: d, m = d + 1, 0
    return d, m


def ws_place(lon):
    return (int(lon // 30) - asc_sign) % 12 + 1


def alch_house(lon):
    for i in range(12):
        a, b = cusps[i], cusps[(i + 1) % 12]
        if (lon - a) % 360 < (b - a) % 360:
            return i + 1
    return 12


points = [(n, pdata[n][0], pdata[n][3]) for n in IDS] + [('South Node', south, pdata['North Node'][3]), ('Lot of Fortune', fortune, 0.0)]


def wheel():
    out = []
    for i in range(12):
        a0, a1 = ang(i * 30), ang(i * 30 + 30)
        out.append(f'<path d="{sector(R_SIGN_IN, R_WS_IN, a0, a1)}" fill="{"#ececec" if i % 2 else "#f7f7f7"}"/>')
        out.append(f'<path d="{sector(R_WS_IN, R_RIM, a0, a1)}" fill="#fff"/>')
        gx, gy = xy((R_SIGN_IN + R_WS_IN) / 2, ang(i * 30 + 15)); out.append(text(gx, gy, SIGNS[i] + VS, 30))
        hx, hy = xy((R_WS_IN + R_RIM) / 2, ang(i * 30 + 15)); out.append(text(hx, hy, str((i - asc_sign) % 12 + 1), 17, 'bold'))
        x0, y0 = xy(R_SIGN_IN, a0); x1, y1 = xy(R_RIM, a0)
        out.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="#000" stroke-width="1.2"/>')
    for d in range(360):
        ln = 14 if d % 10 == 0 else 10 if d % 5 == 0 else 5
        x0, y0 = xy(R_SIGN_IN, ang(d)); x1, y1 = xy(R_SIGN_IN + ln, ang(d))
        out.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="#000" stroke-width="{0.9 if ln > 5 else 0.5}"/>')
    for r, w in ((R_RIM, 2.5), (R_WS_IN, 1.2), (R_SIGN_IN, 1.6), (R_Q_OUT, 1.2), (R_Q_IN, 1.6)):
        out.append(f'<circle cx="{C}" cy="{C}" r="{r}" fill="none" stroke="#000" stroke-width="{w}"/>')
    AXIS = {0: '#0000cc', 6: '#0000cc', 9: '#1e7b1e', 3: '#1e7b1e'}
    for i, cl in enumerate(cusps):
        x0, y0 = xy(R_Q_IN, ang(cl)); x1, y1 = xy(R_SIGN_IN, ang(cl))
        if i in AXIS:
            out.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="{AXIS[i]}" stroke-width="2.6"/>')
        else:
            out.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="#a94442" stroke-width="1.4" stroke-dasharray="6 4"/>')
        mid = cl + ((cusps[(i + 1) % 12] - cl) % 360) / 2
        mx, my = xy((R_Q_OUT + R_Q_IN) / 2, ang(mid)); out.append(text(mx, my, str(i + 1), 14, 'bold', '#a94442'))
    for lon, col in ((ASC, '#0000cc'), (MC, '#1e7b1e'), ((ASC + 180) % 360, '#0000cc'), ((MC + 180) % 360, '#1e7b1e')):
        d, m = dms(lon); bx, by = xy((R_SIGN_IN + R_WS_IN) / 2, ang(lon))
        out.append(f'<rect x="{bx-19:.1f}" y="{by-17:.1f}" width="38" height="34" rx="3" fill="#fff" stroke="{col}" stroke-width="1.2"/>')
        out.append(text(bx, by - 8, f'{d:02d}°', 13, 'bold', col)); out.append(text(bx, by + 8, f"{m:02d}'", 13, 'bold', col))

    pts = sorted(points, key=lambda p: ang(p[1]))
    disp = [ang(p[1]) for p in pts]
    MIN_SEP = 9.5
    for _ in range(300):
        moved = False
        for k in range(len(disp)):
            j = (k + 1) % len(disp)
            gap = (disp[j] - disp[k]) % 360
            if gap < MIN_SEP - 1e-6:
                push = (MIN_SEP - gap) / 2
                disp[k] = (disp[k] - push) % 360; disp[j] = (disp[j] + push) % 360; moved = True
        if not moved:
            break
    # stagger: within a run of displaced neighbours, every other one steps inward
    displaced = [abs((d - ang(p[1]) + 180) % 360 - 180) > 0.05 for d, p in zip(disp, pts)]
    offs = [0] * len(pts)
    k = 0
    while k < len(pts):
        if displaced[k]:
            run = k
            while run < len(pts) and displaced[run]:
                run += 1
            for n, idx in enumerate(range(k, run)):
                offs[idx] = STAGGER if n % 2 else 0
            k = run
        else:
            k += 1
    for (name, lon, speed), a_disp, off in zip(pts, disp, offs):
        x0, y0 = xy(R_SIGN_IN, ang(lon)); x1, y1 = xy(R_SIGN_IN - 10, ang(lon))
        out.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="#000" stroke-width="1.6"/>')
        x2, y2 = xy(R_GLYPH - off + 22, a_disp)
        out.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#666" stroke-width="0.8"/>')
        d, m = dms(lon)
        gx, gy = xy(R_GLYPH - off, a_disp); out.append(text(gx, gy, GLYPH[name] + VS, 34))
        dx_, dy_ = xy(R_DEG - off, a_disp); out.append(text(dx_, dy_, f'{d:02d}°', 18, 'bold'))
        sx, sy = xy(R_SIGN - off, a_disp); out.append(text(sx, sy, SIGNS[int(lon // 30) % 12] + VS, 19))
        mx, my = xy(R_MIN - off, a_disp); out.append(text(mx, my, f"{m:02d}'", 15))
        if speed < 0:   # any point moving backwards, nodes included
            rx, ry = xy(R_RX - off, a_disp); out.append(text(rx, ry, '℞' + VS, 15, fill='#a94442'))

    out.append(f'<circle cx="{C}" cy="{C}" r="{R_Q_IN - 1}" fill="#fff"/>')
    lines = [('Jason Armfield', 17, 'bold'), ('Natal chart', 12, 'normal'), ('19 Nov 1982  11:44', 12, 'normal'),
             ('EST (UTC−5)', 11, 'normal'), ('Petoskey, MI (US)', 12, 'normal'), ('45°22′N  84°57′W', 11, 'normal'),
             ('Diurnal', 12, 'bold'), ('Whole sign · Alchabitius', 10, 'normal'), ('Tropical · True node', 10, 'normal')]
    y = C - 7 * len(lines)
    for s, size, w in lines:
        out.append(text(C, y, escape(s), size, w)); y += 14
    return ''.join(out)


def panel(x0):
    """Positions panel for the wide variant, starting at x0."""
    out = [text(x0, 60, 'Positions', 22, 'bold', anchor='start')]
    cols = [(0, 'Point'), (150, 'Position'), (330, 'WS place'), (460, 'Quadrant'), (590, 'Motion')]
    for dx, h in cols:
        out.append(text(x0 + dx, 100, h, 15, 'bold', '#444', anchor='start'))
    out.append(f'<line x1="{x0}" y1="112" x2="{x0 + 680}" y2="112" stroke="#000" stroke-width="1"/>')
    y = 140
    for name, lon, speed in points:
        d, m = dms(lon)
        motion = '℞ retrograde' if speed < 0 else ('–' if name == 'Lot of Fortune' else 'direct')
        out.append(text(x0, y, GLYPH[name] + VS, 22, anchor='start'))
        out.append(text(x0 + 34, y, name, 16, anchor='start'))
        out.append(text(x0 + 150, y, f'{d:02d}° {SIGNS[int(lon // 30) % 12]}{VS} {m:02d}′', 16, anchor='start'))
        out.append(text(x0 + 330, y, str(ws_place(lon)), 16, anchor='start'))
        out.append(text(x0 + 460, y, str(alch_house(lon)), 16, anchor='start'))
        out.append(text(x0 + 590, y, motion, 15, anchor='start'))
        y += 36
    y += 20
    out.append(text(x0, y, 'Angles and cusps (Alchabitius)', 18, 'bold', anchor='start')); y += 34
    for i, cl in enumerate(cusps):
        d, m = dms(cl)
        label = {0: 'Asc', 3: 'IC', 6: 'Des', 9: 'MC'}.get(i, '')
        col = x0 + (0 if i < 6 else 340)
        yy = y + (i % 6) * 32
        out.append(text(col, yy, f'{i + 1:2d}', 15, 'bold', '#a94442', anchor='start'))
        out.append(text(col + 40, yy, f'{d:02d}° {SIGNS[int(cl // 30) % 12]}{VS} {m:02d}′', 15, anchor='start'))
        if label:
            out.append(text(col + 190, yy, label, 15, 'bold', '#0000cc' if label in ('Asc', 'Des') else '#1e7b1e', anchor='start'))
    y += 6 * 32 + 20
    out.append(text(x0, y, 'Sect: Diurnal · Lord of the day: Venus · Lord of the hour: Mars', 15, anchor='start'))
    return ''.join(out)


head = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {{w}} {SIZE}" width="{{w}}" height="{SIZE}" style="font-family:{FONT}">'
square = head.format(w=SIZE) + f'<rect width="{SIZE}" height="{SIZE}" fill="#fff"/>' + wheel() + '</svg>'
W = 1760
wide = head.format(w=W) + f'<rect width="{W}" height="{SIZE}" fill="#fff"/>' + wheel() + panel(1040) + '</svg>'
here = Path(__file__).parent
(here / 'proto.svg').write_text(square)
(here / 'proto_wide.svg').write_text(wide)
print('node true', dms(pdata['North Node'][0]), SIGNS[int(pdata['North Node'][0] // 30)])
```


## Appendix C — prototype v3 deltas (D1, D3, D6 applied)

```python
# D1
def ang(lon):
    return (lon - asc_sign * 30 + 180.0) % 360.0
# D3
TRIPLICITY_TINT = ['#f7f7f7', '#dedede', '#ededed', '#cdcdcd']   # fire, earth, air, water; sign i uses i % 4
# D1 side-effect: a sign glyph within 7 deg of an angle box steps 8 deg aside
glyph_lon = i * 30 + 15
for angle_lon in (ASC, MC, (ASC + 180) % 360, (MC + 180) % 360):
    gap = (angle_lon - glyph_lon + 180) % 360 - 180
    if abs(gap) < 7:
        glyph_lon = i * 30 + 15 - (8 if gap > 0 else -8)
# D6: the retrograde glyph is black (no fill argument)
```
