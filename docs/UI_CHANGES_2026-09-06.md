# UI changes for almuten_engine — implementation brief (2026-09-06)

This brief is self-contained. It records the outcome of a UI/UX evaluation done on
2026-09-06 and the owner's decisions on it, and specifies the changes to make. The
implementing session does not need the evaluation transcript.

**Scope: interface only.** Do not change any astrological rule, orb, formula, or
verdict. Every engine edit below is additive (a new column, a list returned
alongside an existing string, a new derived value). A regression check at the end
verifies that existing table contents are unchanged.

---

## 1. What the app is, who it is for

A Streamlit study companion for TNAC (Traditional Natal Astrology Course, Benjamin
Dykes). The user is a student partway through Part 1, working the homework by hand
and using the app to check it and to see doctrine applied to real charts. It is not
a delineation product and not a general astrology app.

**Sahl's *Introduction* is the course textbook; Abu Ma'shar's *Great Introduction*
VII is supplementary.** That asymmetry is deliberate and must stay visible: Sahl is
the default view, labelled "course text"; Abu Ma'shar is labelled "supplement".

The Part 1 lesson sequence (from the course's Handy Tables) is what the page
structure mirrors:

| Lessons | Topic | App page |
|---|---|---|
| 3–5 | Chart tour, reference frames, calculation | Chart |
| 9 | Dignities, shares, management | Dignities and places |
| 10 | Sect | Dignities and places (currently no table) |
| 11–12 | Places | Dignities and places |
| 13 | Dynamics, quadrant divisions | Chart |
| 14 | Configurations, looking, aspects | Configurations |
| 15 | Aversion | Configurations |
| 16 | Configurations from the Sun | Chart (Solar phase column) / Configurations |
| 17 | Configurations part 2 (Sahl's sixteen, prevented connections, strength/weakness) | Configurations |
| 18 | Lots | Lots |
| 19 | Triplicity lords (prenatal lunation) | Lunation and victors |
| 20 | Victors | Lunation and victors |
| Part 2 | Prediction | Timing |

The lesson PDFs, homework docs, and Handy Tables live in `/home/apothic/Documents/TNAC/`.
The Lesson 5 homework worksheet (`Lesson 5 homework as Word file.docx`) is the
reference for the Calculation table in §4.A2.

---

## 2. Files, running, and three traps

- **The app is `/home/apothic/almuten_engine/Executable/app.py`** (6,584 lines at
  commit `b8d3f59`, branch `main`, clean). Engine first; Streamlit UI begins at the
  marker `# 4. STREAMLIT UI INTEGRATION` (line ~5859). `Executable/` is the git repo.
- **`/home/apothic/almuten_engine/app.py` is a stale, abandoned copy.** Never edit
  or read it. Use absolute paths.
- Line numbers in this brief are as of `b8d3f59`. Each item also gives a grep
  anchor; trust the anchor over the number.
- Launch config: `/home/apothic/almuten_engine/.claude/launch.json`, name
  `traditional-astrology-engine`, port 8501, venv `/home/apothic/almuten_engine/.venv` (the same one
  `requirements.txt` pins and the test suite uses). Start it with
  the preview tooling, never with a foreground `streamlit run`. If port 8501 is
  already held by another session's server, just navigate to
  `http://localhost:8501` — it hot-reloads on file save.

- A project skill `developing-with-streamlit` exists under `Executable/.claude/skills`
  and is marked required for Streamlit work. Invoke it before editing the UI half.

Traps:

1. **`st.dataframe` renders to a canvas.** Cell values are not in the DOM. Read
   tables from screenshots, or hover the table and use its toolbar search box to
   confirm a string is present.
2. **Sidebar inputs need Enter.** Date and city are text inputs: type, then press
   Enter. The time input is two spin fields: click the hour, type `20`, type `32`,
   press Enter (sometimes twice). Nav clicks made while the app is rerunning are
   dropped; wait a few seconds after a change before clicking a page.
3. **Stale server.** After many hot reloads the sidebar can stop rendering and the
   page collapses to a near-empty body with no server error. Restart the preview
   server; it is not an app bug.

Test charts, all Florence, LMT, 14:30 unless stated:

| Date | Why |
|---|---|
| 1240-05-23 | Default. Many tables are empty; do not judge density here |
| 1240-05-26 | Reflection of Light, Favor & Recompense, Enclosure present |
| 1240-05-25 | Reception by nature under the Abu Ma'shar connection rule |
| 1240-09-18 | Dense Returning and Prevented connections |
| 1240-10-05 | Retreating quadrants, retrograde Jupiter, Collection of Light |
| Minneapolis, 2020-07-14, 20:32, **Standard time (pytz)** | The Lesson 5 homework test nativity; syzygy is Preventional (Full Moon), victor is Mars in all four grids |

---

## 3. Decisions already made by the owner (do not re-ask)

1. **The lesson gate stays** (other students may use it), but its stops must match
   the pages (§4.B1).
2. **Author convention stays**: Sahl default, "course text" / "supplement" labels,
   "Both" stacks the Sahl block above the Abu Ma'shar block. **The Connection rule
   control moves** from the sidebar onto the Configurations page (§4.C2).
3. **Manual calculation continues through the course**: add the Lesson 5
   worksheet intermediates (§4.A2).
4. **Delineation text goes behind expanders**; structural columns stay in the
   tables (§4.D2, D3).
5. **Strength and Weakness become a tick grid**, with the current sentence-per-planet
   table kept below it in a collapsed "Answer key" expander (§4.C4).
6. The user works with their own chart, five class charts, and others. Saved charts
   matter; the chart-entry sidebar stays as it is.
7. **Citations and source notes are learning tools and stay.** Two items *move*
   text without deleting it: cell citations become table captions (§4.A4, C5), and
   the long Connection-rule essay moves to the Sources page (§4.C2, G1).
8. **Each configurable reading moves to the page and table it affects** (§4.H).

---

## 4. The changes

Work through them in order; A and B first, since B1 removes the syzygy gating
problem that A1 also addresses. Commit per section.

### A. Chart page (`def page_chart`, anchor `st.header("Chart")`)

**A1. Prenatal lunation summary on the Chart page.** Lesson 5 homework asks
"conjunctional or preventional?"; today the only answer is the syzygy table on the
victors page, gated at Lesson 20. Replace the "Calculated JD" metric (anchor
`hdr1.metric("Calculated JD"`) with a metric **"Prenatal lunation"** whose value is
`syzygy['event_label']` (e.g. "Preventional (Full Moon)") and whose delta/caption is
the position and natal house (`get_degree_string(syzygy['syzygy_longitude'])`,
`House N`). JD moves into the Calculation table (A2). The full syzygy table on the
victors page is unchanged.

**A2. Calculation table (Lesson 5 worksheet lines).** New two-column table
"Calculation" under the header metrics (which themselves sit below the wheel, see
A3), rows in the worksheet's order:

| Row | Source |
|---|---|
| Local time and standard | `local_dt`, `tz_name` |
| Universal time (worksheet line 8) | `dt_utc` |
| Julian Day | `chart_data['julian_day']`, 4 decimals |
| Greenwich sidereal time at birth (line 11) | `swe.sidtime(jd)` hours → h m s |
| Local sidereal time (line 13) | GST + lon/15 (mod 24) → h m s |
| RAMC (line 14) | `ascmc[2]` from the `swe.houses` call in `calculate_traditional_chart` (anchor `cusps, ascmc = swe.houses(jd, lat, lon, b'B')`, line ~108); return it in the chart dict as `'armc'`. Show as ° ' " |
| Obliquity of the ecliptic (line 15) | `swe.calc_ut(jd, swe.ECL_NUT)[0][0]` → ° ' " |
| MC, Ascendant | already in `chart_data` |

Caption: "Matches the Lesson 5 worksheet: lines 8, 11, 13, 14, 15 and Step 2–3
results." Do not change `calculate_traditional_chart`'s existing outputs; only add
`'armc'` and `'obliquity'` keys.

**A3. Page order and layout. The chart wheel comes first.** Looking at the chart
is the primary act; the owner has said so explicitly. New order: page caption →
**chart wheel** → header metrics → Calculation table → Planetary Positions →
Calculated Points and Quadrant divisions **side by side** in `st.columns(2)` →
Special Degrees (via `_finding`) → `_absent(_gap)`. The wheel must be visible
without scrolling on first load at 1280 px height 720 px; if the orientation text
(A6) pushes it down, place the orientation text below the wheel or make it a
one-line caption.
Set `width='content'` on the two narrow tables. The wheel iframe (anchor
`st.iframe(svg_code, height=720)`) shows an inner scrollbar; the SVG is square
(`viewBox="0 0 {size} {size}"`, anchor at line ~170). Pick a height that removes the
inner scrollbar at 1280 px and 1440 px widths, or wrap the SVG in a container with
`overflow:hidden`.

**A4. Quadrant cell text.** Anchor `"Quadrant": f"{q} (`. Cell becomes
`"8, advancing"` / `"3, retreating"`. Move the citation into the Planetary
Positions caption: `st.caption("Quadrant column: Alchabitius house, advancing or
retreating in Sahl's sense (The Introduction Ch.3, 4-5): stake or succedent versus
falling.")`.

**A5. "Sees the Ascendant" column in Planetary Positions.** After "WS place", add
`"Sees ASC"` = "No (averse)" when the WS place is 2, 6, 8 or 12, else "Yes". This is
whole-sign aversion to the first place, the Handy Tables' Lesson 15 standing
instruction.

**A6. Orientation text.** Under `st.title`, on the Chart page only, three lines:
what the app is (a TNAC study companion for checking hand-worked homework), where
to enter a chart (sidebar; saved charts at the top), and that pages follow the
course's lesson order with Sahl's *Introduction* as the course text and Abu
Ma'shar's *Great Introduction* VII as supplement.

**A7. Title consistency.** `st.set_page_config(page_title="Traditional Astrology
Engine")` and `st.title("Traditional Astrological Engine")` disagree. Use
"Traditional Astrology Engine" for both.

**A8. Hide the Streamlit Deploy toolbar.** Create
`/home/apothic/almuten_engine/.streamlit/config.toml` (the launch config's working
directory) containing:

```toml
[client]
toolbarMode = "minimal"
```

If the Deploy button still shows, also place a copy at
`/home/apothic/almuten_engine/Executable/.streamlit/config.toml`.

### B. Sidebar

**B1. Lesson gate: stops match pages, and it moves to the top.** Anchor
`LESSONS = [`. Replace with:

```python
LESSONS = [("Lessons 3-5: chart and calculation", 5),
           ("Lessons 9-13: dignities, sect, places", 9),
           ("Lessons 14-17: configurations", 14),
           ("Lesson 18: Lots", 18),
           ("Lessons 19-20: lunation and victors", 19),
           ("Part 2: timing", 99)]
```

and the page thresholds (anchor `if gate >= 9:` … `if gate >= 99:`) become 9, 14,
18, 19, 99. Default stays the last stop. Render the widget **before**
`st.sidebar.header("Calculation Parameters")` so it sits directly under the page
navigation (st.navigation always draws the nav at the top of the sidebar; other
sidebar elements follow in call order). Give it `key="lesson_gate"`. Keep the
existing help text. A `st.selectbox` is acceptable in place of the `select_slider`;
the slider currently shows only its two endpoint labels.

Remove the `st.sidebar.markdown("---")` that precedes the old position.

**B2. Remove the Doctrine block and the Configurable readings expander from the
sidebar.** Anchors `st.sidebar.header("Doctrine"` and `with
st.sidebar.expander("Configurable readings"`. Their controls are re-homed in §C2 and
§H. At the top level, where those widgets were, read the values from persistent
session state instead:

```python
CONNECTION_PROFILE   = st.session_state.get("_connection_rule", "Sahl")
FIVE_DEGREE_ALL_CUSPS = st.session_state.get("_five_degree_all_cusps", False)
EASTERN_RULE         = st.session_state.get("_eastern_rule", "hemisphere")
MOON_RAYS_ORB        = 15.0 if st.session_state.get("_moon_rays_15", False) else 12.0
DOMAIN_RULE          = st.session_state.get("_domain_rule", "Abu Ma'shar")
LOT_HOUSE_CUSP       = st.session_state.get("_lot_house_cusp", "whole-sign place")
```

These globals are read by engine functions at call time (`CONNECTION_PROFILES[CONNECTION_PROFILE]`
at line ~1275, `FIVE_DEGREE_ALL_CUSPS` ~3105, `EASTERN_RULE` ~4953, `MOON_RAYS_ORB`
~606, `DOMAIN_RULE` ~696, `LOT_HOUSE_CUSP` ~3719), all of which run *before* the page
functions, so the assignment must stay at the top level where it is now.

**B3. Persist pattern for page-level widgets.** Streamlit drops a widget's state
when the widget is not rendered on a run, which is why the Configurations "Show"
control resets to Sahl after navigating away (it already has
`key="configurations_view"`; the key alone does not help). Add one helper near
`_finding`:

```python
def _persist(widget_key, store_key, default):
    """Render-independent memory for a page widget. Call AFTER the widget:
    copies its current value into a store key that survives navigation.
    Pass st.session_state.get(store_key, default) as the widget's default."""
    if widget_key in st.session_state:
        st.session_state[store_key] = st.session_state[widget_key]
    return st.session_state.get(store_key, default)
```

Use it for Show (§C1), Connection rule (§C2) and all five readings (§H). Because
the engine has already run with the stored value by the time the page widget
renders, a change triggers Streamlit's rerun and the new value is picked up on that
rerun; on the first render the widget's default equals the stored value, so the
page and the engine agree.

### C. Configurations page (`def page_configurations`)

**C1. Show control persists.** Anchor `view = st.segmented_control(`. Set
`default=st.session_state.get("_configurations_view", "Sahl (course text)")`, then
`view = _persist("configurations_view", "_configurations_view", "Sahl (course text)")`.
Acceptance: choose "Both", go to Chart, return: still "Both".

**C2. Connection rule moves beside Show.** Put Show and the rule in
`st.columns([2, 1])`. Radio label: "Connection test used in the shared tables";
options `list(CONNECTION_PROFILES.keys())`, horizontal, `key="connection_rule"`,
`index` from the stored value, then `_persist("connection_rule",
"_connection_rule", "Sahl")`. Help text (≤ 250 characters): "Which author's test
decides Connected in the aspects, reception, prevented-connections and wildness
tables. Sahl: the applying planet's own light. Abu Ma'shar: 15° in one sign, 12° for
aspects. Full comparison on the Sources page." The existing 1,971-character help
string moves verbatim to the Sources page (§G1). Keep the existing captions that say
"— {CONNECTION_PROFILE} rule in force" and the "Reception — {rule}" heading.

**C3. Aspects table: fixed column order, and a "Rules differ" column.** In
`evaluate_ptolemaic_aspects` (anchor `def evaluate_ptolemaic_aspects`, ~1337) the
aversion rows (anchor `'Aspect': 'Aversion'`, ~1364) and the configured rows
(~1396) build their dicts in different key orders; pandas takes the first row's
order, so the column order changes from chart to chart. Fix: build every row with
the same key order, and in the UI pass `columns=[...]` explicitly. Add a final
column `"Rules differ"` = "Yes" when `_is_connected_sahl(row)` and
`_is_connected_abu_mashar(row)` disagree, else "". Both functions exist (anchor
`CONNECTION_PROFILES = {`). This makes flipping the rule visible.

**C4. Strength and Weakness as tick grids.** Engine (anchors `'Strength
Testimonies': ', '.join(labels)` ~4468 and `'Weakness Testimonies'` ~4599): add a
key `'Labels': labels` (the list) to each result row; leave the joined string in
place. UI: for each of the two tables, build a grid with one row per planet, one
column per testimony, cell "✓" when the planet's `Labels` contains a label ending
in that paragraph number (labels already end in "(78)" … "(100)"; match on the
number in parentheses), plus the existing Count column last. Column headers, short:

- Strength: `78 excellent place`, `79 own dignity`, `80 direct`, `81 not in infortune stakes`, `82 not with fallen`, `83 advancing`, `84 eastern, masculine`, `85 of sect`, `86 fixed sign`, `87 heart of Sun`, `88 gender match`.
- Weakness: `91 falling, averse ASC`, `92 retrograde`, `93 under rays`, `94 connects infortune`, `95 enclosed`, `96 own fall`, `97 averse / lost receiver`, `98 alien`, `99 with nodes`, `100 inverted`.

Keep the subheader, the citation caption and the notes expander exactly as they
are. Directly under each grid add `st.expander("Answer key: testimonies in
words")` containing the current three-column table. Show all seven rows without
inner scrolling (§C8).

**C5. Prevented connections: citation out of the cells.** Anchor `'Source': 'Sahl
Ch.3, 31-48; VII.5, 90-94'` and the second `'Source':` a few lines below. Drop the
Source key from the rows; the table's caption already cites both passages. Widen
"Because" by that freed width.

**C6. Planetary Condition: drop the constant column, fix the caption.** Anchor
`"Standing": "app arithmetic, not VII.6"`: remove that key. Move `Net` and
`Verdict` to the end of the row dict (after the two label columns). Caption anchor
`They are kept only because the Rhetorius/PN4 delineations below`: change "below"
to "on the Dignities page".

**C7. Four tooltips end mid-sentence.** Rewrite each `glance=` as one complete
sentence under 250 characters, and delete from the matching `notes=` any fragment
that was the tail of the cut sentence:

- Non-reception (anchor `_finding(_gap, 'Non-reception'`): glance ends "…in the other's sign of". 
- Strength (anchor `_finding(_gap, 'Strength of the Planets'`): glance ends "…in its own glow, a".
- Weakness (anchor `_finding(_gap, 'Weakness of the Planets'`): glance ends "(i.e."; its notes begin "the 6th or 12th), retrograde, …" — that fragment belongs to the glance.
- Planetary Condition (anchor `st.subheader('Planetary Condition', help=`): help ends "HIS OWN eleven"; the notes expander begins "corruptions of her (63-74)…" — same split.

**C8. Tables show all their rows.** Add a helper `_rows_height(n)` returning
`35 * (n + 1) + 3` and pass `height=_rows_height(len(df))` for: Aspects (21 rows),
Strength and Weakness grids and answer keys (7), Topical House Lords (12, §D3),
Topical Lots (§E2). Leave the default height on tables that can exceed ~40 rows.

### D. Dignities page (`def page_dignities`)

**D1. Lordship Mapping gains position and own-dignity columns.** After "Planet"
insert `"Position": get_degree_string(data['longitude'])`; after "Face lord"
insert `"Own dignity here"`: the planet's `essential[p]['Essential Labels']` joined
with ", ", with the "(+5)"-style score suffixes stripped, or "Peregrine" when
`essential[p]['Peregrine']` is true. Anchor `lordship_list.append({`. These labels
are computed already (anchor `'Essential Labels': labels`, ~486).

**D2. Topical Planets in Houses: readings behind an expander.** Anchor
`st.subheader('Topical Planets in Houses'`. The visible table keeps `Planet`,
`Placed in (WS place)`, `Lean`. Everything else (`Net`, `Standing`, `If Well
Placed`, `If Badly Placed`) goes into `st.expander("Rhetorius / PN4 readings for
these placements")` rendered with `st.table` so the text wraps. The existing
"Sources and editorial notes" expander stays after it.

**D3. Topical House Lords: aversion flag, readings behind an expander.** Anchor
`st.subheader("Topical House Lords (Masha'allah)"`. Visible columns: `Topical
House`, `Cusp Sign`, `Domicile Lord`, `Placed in (WS place)`, new `Averse to its
place` = "Yes" when `(placed_in - house) % 12 in (1, 5, 7, 11)` else "No" (that
is, the lord sits in the 2nd, 6th, 8th or 12th sign from the house it rules).
`Masha'allah Signification` moves into `st.expander("Masha'allah readings for lord
placements")` via `st.table`. Height per §C8 so all twelve rows show.

**D4. Sect status table (Lesson 10).** New table "Sect" between Lordship Mapping
and Topical Planets in Houses: `Planet`, `Planet's sect` (diurnal/nocturnal; the
engine already knows this — `planet_is_diurnal` near anchor `# --- Sect / Hayz`,
~653), `Above horizon` (Yes/No), `Of the chart's sect` (Yes/No — reuse exactly the
test Strength testimony 85 uses, anchor `In its own glow, i.e. of the sect (85)`,
~4429; do not write a new one), `Domain (hayz)` = `accidental[p]['Hayz']`. Caption:
"Sect: Sahl, The Introduction Ch.3, 85. Domain: Abu Ma'shar VII.1, 37 and VII.6, 13
(or Masha'allah, On Nativities 1.23, 17, per the switch)." Chart sect stays in the
header metric on the Chart page. The Domain switch renders beside this table (§H).

**D5. Dignity Evaluation expander.** Anchor `"Standing": "app scoring model"`:
remove that key. Leave the expander collapsed and otherwise unchanged.

### E. Lots page (`def page_lots`)

**E1. Remove the duplication.** Classical Lots gains a `Formula` column (the same
text Topical Lots shows for the same lot — take it from `LOT_DEFINITIONS`, anchor
`LOT_DEFINITIONS`). Topical Lots drops its rows for Fortune, Spirit and Exaltation.
Anchors `st.subheader('Classical Lots'` and `st.subheader('Topical Lots (Sahl, On
Nativities)'`.

**E2. Topical Lots columns.** Visible order: `Topic`, `Lot`, `Position`, `WS
place`, `Lord`, `Formula`, `Active`. `Standing`, `Source`, `Editor's note` move to
an expander "Provenance and standing per Lot" (`st.table`, same rows). Height per
§C8 so the table does not scroll internally. Both "Sources and editorial notes"
expanders stay.

### F. Lunation and victors page (`def page_victors`)

**F1. Two grids by default.** Anchor `for scheme_name, res in victors_data.items():`.
Render the two schemes whose name contains "matched preset" as now; render the
other two inside `st.expander("Cross-check: the two unmatched weight/place
pairings")`. The heading line with victor and runner-up stays for all four. The
notes expander stays.

### G. Sources and coverage page (`def page_sources`)

**G1. Connection rule essay.** New `st.subheader("Connection rule: Sahl and Abu
Ma'shar")` followed by `st.markdown` of the text that was the radio's `help=`
(anchor `"Which author's rule decides whether a pair counts as Connected.`), verbatim.

**G2. Configurable readings reference.** New `st.subheader("Configurable
readings")` with one short paragraph per switch: its label, the full help text it
had in the sidebar (verbatim), and the tables it affects (the list in §H). The
on-page controls then carry only a one-line help.

### H. Re-homing the five configurable readings

Each control renders on the page beside the first table it changes, with a
one-line help that names every table it affects, and uses the persist pattern
(§B3). Store keys are the ones read in §B2.

| Control | Widget | Renders beside | Also affects |
|---|---|---|---|
| Five-degree carryover at all twelve cusps | checkbox, key `five_degree_all_cusps` | Strength of the Planets (testimony 83), Configurations page | — |
| Eastern/western rule (VII.6, 27/45) | radio, key `eastern_rule` | Planetary Condition, Configurations page (Abu Ma'shar block) | — |
| Moon under the rays to 15° | checkbox, key `moon_rays_15` | Planetary Positions (Solar phase column), Chart page | Weakness (93), Planetary Condition, Moon defects |
| Domain (hayz) rule | radio, key `domain_rule` | Sect table (§D4), Dignities page | Dignity Evaluation, Planetary Condition (13) |
| House-based Lots measure to | radio, key `lot_house_cusp` | Topical Lots, Lots page | — |

Each help string: the first sentence of the old help (the rule), then "Affects: …".
Full text lives on the Sources page (§G2). Note for the Moon-rays and Domain
controls: they change tables on other pages; say so in the help.

### I. Small fixes

- Anchor `hdr1.metric("Calculated JD"`: handled by A1/A2 (JD moves to the table;
  it truncated to "2174111.0…" at 1280 px).
- Anchor `"Standing": "app arithmetic, not a source verdict"` in
  `evaluate_planets_in_houses` (~5795): keep in the engine (it is harmless data),
  hide it via D2.
- The Chart page's "Not present in this chart: Special Degrees & Conditions" line
  currently prints below the wheel; A3 moves it above.

---

## 5. Do not change (the parts that already work)

- Pages follow the Handy Tables' lesson order and the captions name the lessons.
- Sahl is the default view labelled "course text"; Abu Ma'shar is "supplement"; the
  page caption states the asymmetry.
- The victor grids reproduce ibn Ezra's worksheet row for row (Sun, Moon, ASC, Lot
  of Fortune, prenatal syzygy, Lord of the Day (7), Lord of the Hour (6), Places,
  Totals) with the seven planets as columns. Do not reorder or rename those rows.
- Planetary Positions carries exactly the Lesson 3 homework columns: position,
  absolute longitude, WS place, quadrant with advancing/retreating, motion, solar
  phase. Only add (A5), never remove.
- Prevented connections stays one merged table on the Handy Tables' grouping, with
  Abu Ma'shar's revoking/resistance/escape kept in his own block (the code comment
  there explains why).
- Empty findings keep collapsing into one "Not present in this chart: …" caption
  per group (`_finding` / `_absent`).
- Every citation caption under a heading, and every "Sources and editorial notes"
  expander, stays. "app scale" / "app arithmetic" honesty labels stay in captions.
- Sidebar chart entry: LMT default with the computed UTC offset, UT shown for
  standard time, DST ambiguity errors, saved-chart load/save. Unchanged.
- The Lots Formula text ("Ascendant + (Moon − Sun) [day order]") stays as is.
- Tables remain `st.dataframe` (its toolbar search and fullscreen are how a student
  copes with any remaining truncation), except the reading-text tables moved into
  expanders, which use `st.table` so they wrap.

---

## 6. Regression check (run before and after)

The engine half can be executed without Streamlit. Before touching anything, dump
the tables that must not change:

```python
# save as Executable/_regress.py ; run with Executable/.venv/bin/python _regress.py before.json
import sys, json
src = open('app.py').read().split('# 4. STREAMLIT UI INTEGRATION')[0]
exec(src, globals())
from datetime import datetime, timedelta
out = {}
for label, (y, m, d, hh, mm, lat, lon, lmt) in {
    'default':  (1240, 5, 23, 14, 30, 43.7792, 11.2463, True),
    '0526':     (1240, 5, 26, 14, 30, 43.7792, 11.2463, True),
    '0525':     (1240, 5, 25, 14, 30, 43.7792, 11.2463, True),
    '0918':     (1240, 9, 18, 14, 30, 43.7792, 11.2463, True),
    '1005':     (1240, 10, 5, 14, 30, 43.7792, 11.2463, True),
    'mpls':     (2020, 7, 15, 1, 32, 44.98, -93.2638, False),   # 20:32 CDT = 01:32 UT next day
}.items():
    local = datetime(y, m, d, hh, mm)
    dt_utc = local - timedelta(hours=lon / 15.0) if lmt else local
    c = calculate_traditional_chart(dt_utc, lat, lon)
    p, sect = c['planetary_data'], c['sect']
    ess = evaluate_essential_dignities(p, sect)
    acc = evaluate_accidental_dignities(p, c['houses'], sect, c['julian_day'])
    sim = _simulate_forward(p, c['julian_day'])
    out[label] = {
        'aspects':   evaluate_ptolemaic_aspects(p),
        'reception': evaluate_reception(p, sect, sim),
        'strength':  evaluate_strength_of_planets(p, ess, acc, c['ascendant'], sect, c['houses']),
        'weakness':  evaluate_weakness_of_planets(p, ess, acc, c['ascendant'], sect),
        'lords':     evaluate_house_lords(p, c['ascendant']),
        'lots':      calculate_topical_lots(p, c['ascendant'], c['houses'], sect),
        'victors':   {k: v['grid'] for k, v in evaluate_victors(p, c['ascendant'], c['lot_of_fortune'],
                        calculate_prenatal_syzygy(c['julian_day'], lat, lon, c['houses'])['syzygy_longitude'],
                        sect, calculate_chronocrats(c['julian_day'], lat, lon, local, lon/15.0 if lmt else -5.0)).items()},
    }
json.dump(out, open(sys.argv[1], 'w'), indent=1, default=str)
```

After the changes, run it again to `after.json` and diff. The only permitted
differences: new keys (`Labels`, `Rules differ`, `armc`, `obliquity`) and removed
`Source`/`Standing` keys where §C5/§C6/§D5 say so. Any changed *value* is a bug.
Delete `_regress.py` and the JSON files before committing, or add them to
`.gitignore`.

---

## 7. Acceptance checklist (in the browser)

Use the six test charts. Sizes 1280 px and 1440 px.

1. Chart page, Minneapolis chart: **the wheel is the first thing on the page and
   is fully visible on load without scrolling**, with no inner scrollbar; below it
   the header shows "Prenatal lunation: Preventional (Full Moon)"; Calculation
   table shows UT 2020-07-15 01:32:00, JD 2459045.5639, GST, LST, RAMC, obliquity;
   Quadrant cells read "7, advancing"; a "Sees ASC" column exists.
2. Sidebar: "Show material through" sits directly under the page list. Setting it
   to "Lessons 9-13" hides Configurations, Lots, Lunation and victors, Timing. No
   Doctrine block, no Configurable readings expander remain in the sidebar.
3. Configurations: Show and the Connection rule sit side by side; choose "Both" and
   Abu Ma'shar, go to Chart, return: both selections survive. Aspects table column
   order is identical on 1240-09-18 and 1240-10-05; flipping the rule turns at
   least one "Rules differ" cell to Yes on 1240-05-25. Strength and Weakness are
   tick grids with the answer-key expander below; all seven rows visible.
4. Dignities: Lordship Mapping has Position and Own-dignity columns; a Sect table
   exists; House Lords shows twelve rows without inner scrolling and an "Averse to
   its place" column; reading text is only inside expanders.
5. Lots: Fortune/Spirit/Exaltation appear once (Classical, with Formula); Topical
   Lots shows all rows without inner scrolling; provenance is in an expander.
6. Victors: two grids visible, two in an expander; Mars wins all four on the
   Minneapolis chart.
7. Sources: the Connection-rule essay and the five readings' full texts are present.
8. No tooltip ends mid-sentence (hover each "?" on Configurations).
9. Regression diff (§6) shows no changed values.

Commit on a branch off `main` named `ui-2026-09-06`, one commit per section A–I,
then report which checklist items passed, with screenshots of items 1, 3 and 4.
