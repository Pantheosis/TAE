# Hostile pass of 2026-09-16 -- a falsification report

An adversarial sweep of the Traditional Astrology Engine's whole input
surface, run by an agent with no build context against a worktree server on
its own port (8525), with `XDG_DATA_HOME` pointed at a **scratch copy** of
`~/.local/share/TraditionalAstrologyEngine/` so the owner's charts and
preferences were never touched. The mandate was to falsify, not to confirm.
The checklist followed is `HOSTILE_PASS_CHECKLIST.md`. Every finding below is
reproduced under `streamlit.testing.v1.AppTest` and kept in the suite as
`tests/test_hostile_pass_2026_09_16.py` (the open defects as strict `xfail`
asserting the right behaviour, the coverage as ordinary tests).

Branch cut from `origin/main` at `ab497fd` per the brief, then **rebased onto
current `origin/main` (`49a531b`)** and every finding re-verified there,
because five PRs merged after the brief was written: the F04 record-lifecycle
fix (#53), the checklist (#54), an aspects/horizon/lots pass (#55), the
retirement of the moving-target proofs (#56), and #52 before them. That
rebasing matters twice over:

- The entire **F04 lifecycle** -- picker-after-save, the *(modified)* mark,
  New-clears, the replace and delete confirmations, and corrupt-store
  preservation -- is now on main and **holds** (re-verified; see Coverage).
- The report's original **M2** (a finite 200-day search folded into the
  unbounded "Not present" line) was **resolved by #55** ("the forward
  search's horizon said where its zero rows are") while this pass was under
  way; it is recorded under Coverage, not as an open finding.

None of that is reported as a defect. What remains are calculation- and
shell-level defects that this later work did not touch.

Severity by consequence, per the brief: a misleading **stored record** is
critical; a **lost shell** or a **wrong qualification** is high; friction is
medium.

## Counts

| Severity | Count | Findings |
|---|---|---|
| Critical | 0 | (none reachable through normal use; H5 escalates to critical-class only when an already-invalid record is re-saved) |
| High | 5 | H1, H2, H3, H4, H5 |
| Medium | 3 | M1, M3, M4 |

The five High findings share one root cause: **the sidebar validates the
draft against form, never against what the ephemeris or the engine can
actually consume, and the calculation and the target bundle run at module
level *before* `st.navigation(...).run()`.** So an input that passes the
form checks but raises inside `calculate_traditional_chart_jd`,
`pn4_timing_bundle`, or a widget seeded from a stored value takes the whole
script down before any page -- or the top navigation itself -- is drawn. This
is precisely the class F05 (the shell that survives a bad input) was built to
prevent, for inputs its validation does not cover.

---

## H1 -- a valid birth date the ephemeris cannot reach kills the whole app (High: lost shell)

- **Input:** Date `3100-06-01` (any year from **3002 to 9999**; the Date help
  and `parse_iso_date` both accept years 1-9999).
- **What the page showed:** a raw `swisseph.Error: ... SwissEph file
  'sepl_30.se1' not found` traceback in the page body. The sidebar renders,
  but the main area is the traceback -- no header, no tables, and **no
  recovery panel**. Clicking *Reference* or *Sources* in the top bar does
  nothing: the URL stays `/`, the exception persists, no page loads. The
  navigation bar is present but **inert**, because the crash is at module
  level (`chart_data = calculate_traditional_chart_jd(jd_ut, lat, lon)`,
  app.py) and `st.navigation(...).run()` at the foot of the file is never
  reached. Re-entering a reachable date recovers.
- **What the store holds:** nothing is written (the crash precedes Save).
- **Right behaviour:** a date the engine cannot compute is an invalid input
  like an impossible latitude -- it should set `chart_ok = False` with a
  sentence naming the limit, so the shell, Reference and Sources stay. The
  Swiss Ephemeris span shipped is roughly year -3000 to 3001; the date field
  should refuse (or the calculation should be guarded) outside it.
- **Reproduction:**
  ```python
  at = make_app(date="3100-06-01", page="chart").run(); assert not at.exception
  ```

## H2 -- the Timing target reaches the same limit, from the widget or a typed date (High: lost shell)

- **Input, path (a):** Timing page, *Target by* = **Age**, Age = **2000** on
  the 1240 default chart. The Age `number_input` has `min_value=0` and **no
  upper bound**, so any age whose birthday-year exceeds ~3001 (age > ~1761 on
  the 1240 chart; age > ~1019 on a 1982 chart) is accepted.
- **Input, path (b):** *Target by* = **Date**, Target date = **`3500-01-01`**
  (any date past ~3001).
- **What the page showed:** the same uncaught `swisseph.Error` from
  `pn4_timing_bundle` -> `pn4_solar_revolution_jd`; the whole app dies as in
  H1.
- **Right behaviour:** the target already keeps its last valid value when it
  fails to *parse* (F17); it should likewise refuse a target the ephemeris
  cannot reach, with a sentence, and keep the shell. The Age widget wants a
  `max_value` as well.
- **Reproduction:**
  ```python
  at = make_app(date="1240-05-23", page="timing"); at.session_state["_target_mode"]="Age"; at.session_state["_target_age"]=2000; at.run(); assert not at.exception
  ```

## H3 -- a saved record with a type-wrong field crashes on load, and dead-on-open when it is the last chart (High: lost shell)

- **Input:** a saved-chart entry whose fields are the wrong *type* (not just
  out of range). `_validate_chart_mapping` in engine.py checks that names are
  strings and entries are dicts -- never the field types the sidebar and
  engine consume. Confirmed to crash the whole script on load:

  | field | value | exception |
  |---|---|---|
  | `time_string` | `1144` (int) | `'int' object has no attribute 'split'` |
  | `date_string` | `19821119` (int) | `bad argument type for built-in operation` |
  | `date_string` | `["1982-11-19"]` (list) | `bad argument type ...` |
  | `lat`/`lon` | `"45.3"` (str) | `'<' not supported between 'str' and 'float'` |
  | `utc_offset` | `"abc"` (str) | `'<' not supported between 'str' and 'float'` (in the widget) |
  | `utc_offset` | `NaN` | `cannot convert float NaN to integer` |
  | `target_age` | `"abc"` | `invalid literal for int()` |

- **What the page showed:** on selecting the record, a raw traceback and no
  page. If such a record is the `last_chart`, the app **autoloads it on
  launch** and is dead-on-open -- a raw traceback with no page reachable at
  all, on a fresh start.
- **What the store holds:** the record is unchanged (read-only path); the
  crash is on consumption.
- **Right behaviour:** a record is loaded into the sidebar as *draft*; a
  malformed draft is already handled for the date box (last-good + an error).
  Loading should coerce or reject each field the same way, so a bad record
  degrades to an error, never a crash -- and never a dead launch.
- **Reproduction:**
  ```python
  _saved_path().write_text(json.dumps({"Rec": {**PETOSKEY, "time_string": 1144}}))
  at = make_app(page="chart").run(); at.sidebar.selectbox(key="chart_picker").select("Rec").run(); assert not at.exception
  ```

## H4 -- a corrupt preferences file crashes the app on open (High: lost shell)

- **Input:** `preferences.json` with `_launches` a non-int (`"many"`), or
  `last_chart` a non-string (`["a"]`). The preferences loader keeps only the
  known keys but never checks their types, and the launch block does
  `int(... _launches ...)` and indexes `saved_charts` by `last_chart`.
- **What the page showed:** `invalid literal for int(): 'many'`, or
  `cannot use 'list' as a dict key`, at module level on **every page** -- the
  app will not open.
- **Right behaviour:** the app writes this file itself, so it is normally
  well-formed; but a hand-edit or a downgrade should not brick the app.
  Coerce `_launches` to int defensively and ignore a non-string `last_chart`,
  as the loader already ignores unknown keys.
- **Reproduction:**
  ```python
  (d/"preferences.json").write_text(json.dumps({"_launches": "many"}))
  at = _fresh_launch("chart").run(); assert not at.exception
  ```

## H5 -- a saved UTC offset outside +-14 is silently pulled to the wrong bound (High: silently wrong chart; critical-class on re-save)

- **Input:** a saved record, `time_standard` = *Manual UTC offset*,
  `utc_offset` = **99** (any value outside +-14; from a hand-edit, a legacy
  file, or a bad import).
- **What the page showed:** the chart cast at **`UTC-14:00`** with **no
  warning** -- a seeded out-of-range value is silently clamped by Streamlit
  to the widget's **minimum** (-14), the *wrong* direction, not the maximum.
  This is exactly the seeded-clamp class F02 fixed for latitude/longitude
  (where 91 became -90) by reading the draft before the widget clamps it --
  but the same guard was **not** applied to the offset. The strip also reads
  `Rec (modified)` on load without the user touching anything, because the
  stored 99 no longer matches the clamped -14.
- **What the store holds:** 99 until the first re-save; a **re-save writes
  `-14.0`**, silently rewriting the record to a different (and
  wrong-direction) nativity -- a misleading stored record.
- **Right behaviour:** validate the offset draft before the widget clamps it,
  as the coordinates are validated (`coordinates_in_range`), and refuse an
  out-of-range offset with the shell intact -- never cast a confident wrong
  chart, and never persist the clamp.
- **Reproduction:**
  ```python
  _saved_path().write_text(json.dumps({"Rec": {**PETOSKEY, "time_standard": "Manual UTC offset", "utc_offset": 99}}))
  at = make_app(page="chart").run(); at.sidebar.selectbox(key="chart_picker").select("Rec").run()
  assert "UTC-14:00" not in next(c.value for c in at.main.caption if " · " in c.value)
  ```

---

## M1 -- Verdict and Lean read one Net and name it two ways at |Net| = 1 (Medium: same fact in two places; owner's to rule)

- **Input:** the owner's own nativity (1982-11-19, Petoskey), and every
  fixture chart.
- **What the pages showed:** the Configurations *Planetary Condition* table's
  **Verdict** and the Dignities *Topical Planets in Houses* table's **Lean**
  are both derived from the same VII.6 **Net**. The owner's F06 ruling
  (2026-09-16) made a Net of **0** read *Indeterminate* in both places -- and
  it does. But at **|Net| = 1** they disagree: Verdict says **Good** or
  **Bad** (strict sign), while Lean says **Indeterminate** (a documented
  "margin of one"). E.g. 1982-11-19 Sun (Net +1): Configurations *Good*,
  Dignities *Indeterminate*; 2000-06-21 Mars (Net -1): *Bad* vs
  *Indeterminate*. Same number, opposite words, same planet, same chart.
- **Right behaviour:** the checklist asks that a Net "be named the same way
  everywhere." Whether the Verdict should also adopt the margin-of-one, or
  the two are meant to differ, is a doctrinal choice -- **reported, not
  fixed**, for the owner's ruling, as the natural follow-on to F06.
- **Reproduction:** `test_verdict_and_lean_agree_on_the_same_net` iterates the
  two tables and asserts *Indeterminate* agrees between them.

## M3 -- a chart named exactly "-- New Chart --" collides with the picker sentinel (Medium: friction)

- **Input:** Save with the chart-name box set to the literal string
  `-- New Chart --`.
- **What the page showed:** the save succeeds (`Saved '-- New Chart --'.`)
  and the file gets a key `"-- New Chart --"`, so the picker lists
  `-- New Chart --` **twice** -- and the saved one can never be selected
  (selecting it is indistinguishable from "new chart") nor deleted through
  the UI.
- **Right behaviour:** refuse (or transparently suffix) a chart name equal to
  the `-- New Chart --` sentinel, the way an empty name is already refused.
- **Reproduction:** save `"-- New Chart --"` and assert the picker options
  are unique.

## M4 -- one Timing control does not persist across navigation, unlike every other page control (Medium: friction)

- **Input:** on Timing, change *"Also direct, for the small days ... from"*
  (the `pn4_day_point` selectbox), navigate away, and return.
- **What the page showed:** the choice resets to its default. It is a plain
  `st.selectbox(key="pn4_day_point")` with no `_persist`, so Streamlit drops
  its state when the page is not rendered -- the exact failure the `_persist`
  helper exists to prevent, and which every other page control uses. Its
  effect is only an extra informational line, so the consequence is friction,
  not a wrong chart.
- **Right behaviour:** route it through `_reading_select` / `_persist` like
  the *View*, *Wheel layout* and *Inner wheel* controls beside it, or note in
  the code why it deliberately does not persist.

---

## Coverage -- what the pass tried and could not break

Pinned as ordinary (passing) tests in
`tests/test_hostile_pass_2026_09_16.py`, and checked live in the browser
where noted:

**Every field, garbage and boundaries.**
- Date: `not-a-date`, `1240-13-01`, blank, `1900-02-29`, `10000-01-01`,
  `0000-01-01`, `1240-05-23T14:30` -> the committed date stands, the strip
  shows it (never the draft), the warning band "Results have not updated..."
  appears, and Save is refused (F01). `1240-5-3` and `" 1240-05-23 "` parse.
  `1300-02-29` (a Julian leap day) is accepted and casts.
- The **1582 Julian/Gregorian gap**: `1582-10-04` vs `1582-10-15` carry the
  right calendar label and the right UT on each side; `1582-10-10` (a day
  that never existed) is read as Julian, consistently.
- Time: `00:00:00` and `23:59:59` cast correctly (the widget cannot hold
  garbage). `1300-02-29` under **Standard time** shows the recovery panel and
  the shell holds.
- Place: blank, `zzzz-no-such-city`, `New York, NY` (a resolved *label*, no
  match -- expected), `91, 0`, `0, 181`, `nan, nan`, `1e2, 0`, a trailing
  comma -> one sidebar error and the recovery panel, no exception, nothing
  saved. `'; DROP TABLE cities;--` -> "No matches" (the query is
  parametrised; safe). A typed `45.3733, -84.9553` resolves. `+-90/+-180`
  cast; polar 66.6-90 on midsummer/midwinter: Chart and Victors render, and
  Timing shows **bounded** "Refused at this latitude..." warnings (a finite,
  well-qualified refusal, not a crash).
- Time standard: LMT, named zone and Manual offset all cast; `+-14` in range;
  a typed `+-14.25` is clamped in-range by the widget; a point at sea
  (`0, -30`) under a named zone resolves to `Etc/GMT+2`.
- **DST**: New York `2025-03-09 02:30` (spring-forward gap) and
  `2025-11-02 01:30` (fall-back overlap) under Standard time -> named errors,
  the recovery panel, the shell intact.

**The whole F04 record lifecycle (PR #53) re-verified on main and holds.**
- Save refuses an invalid date or an unresolved place and writes nothing
  (F01).
- A successful save selects the record in the picker, and the strip names it;
  editing a loaded chart marks it `<name> (modified)` in the strip and
  "Edited since it was saved." under the picker (fields the stored record
  lacks are not compared, so pre-time-standard records are not falsely
  accused).
- **New Chart** puts the example nativity back in every sidebar key.
- Saving under a name in use writes nothing on the first press and asks
  ("'<name>' exists. Replace it?" with *Replace* / *Keep both*, or "'<name>'
  is already saved as it is."); the bin asks "Delete '<name>'?" with
  *Delete* / *Keep*, and a confirmed delete no longer resets the sidebar to
  1240.
- A malformed / empty / list-shaped / string-root `saved_charts.json` is
  **preserved**: copied aside as `saved_charts.json.unreadable-<timestamp>`
  and announced once as "Saved charts could not be read. The original file
  was kept as ...", with the in-memory set empty -- no silent data loss.
- Every write goes to disk first; the in-memory dict follows only on success
  (a read-only file gives "Could not write saved_charts.json to disk." and
  keeps the prior state).
- Names with quotes, `<`, `&`, emoji, 300 chars and a newline save and are
  HTML-escaped in the strip; an all-spaces name is refused; leading/trailing
  spaces are trimmed.

**A finite search no longer reads as an unbounded absence (report's M2, resolved by #55).** Forward-Looking Conditions (Revoking/Resistance/Escape), a 200-day search, is no longer folded into the generic "Not present in this chart" line beside unbounded absences (Collection of Light, Enclosure, Wildness, Reflection of Light); it renders in place with its own heading and states where its zero rows are. Pinned by a guard test.

**Lifecycle across sessions.**
- A full round trip -- date, time to the second, time standard, manual
  offset, place, and Age *and* Date targets -- reloads identically in a fresh
  session (Manual offset `-5.5` and Age `30` verified).
- Two browser tabs / two AppTest sessions on one server each follow their own
  readings; the shared preferences *file* is last-writer-wins across
  sessions, which is expected -- per-session state is independent and correct.

**Every page control** (Chart, Dignities, Configurations, Lots, Timing,
Sources) toggled once: the store key, the preferences file, and a fresh
session all agree, except M4 above and the two deliberately non-persisted
"comparison" toggles (`life_lords_ascendant`, which is a within-session
convenience, not a preference).

**The same fact in two places.**
- The strip, the sidebar boxes and the Chart *Calculation* table agree on
  date, time, offset, UT and place.
- Sect / day lord / hour lord / lunation agree between the strip and the
  Victors and Timing tables; sect **at the horizon minute** (Florence
  1983-11-19, sunrise ~06:17 LMT) agrees between the strip and the Dignities
  *Sect* table -- the altitude-based sect fix holds. The circumpolar
  "Lord of the Hour is not a temporal hour" caveat is stated on the Chart
  page where it applies.

**Provenance spot-checks against the corpus** (`consolidated_texts_final/`).
Ten citations across five pages were read to chapter and sentence and all
matched the app's text: Sahl *On Nativities* 1.7, 3-7 (the governor of the
degree) and 1.38, 39-41 / Figure 57 (nobility degrees); Sahl *Introduction*
Ch.3, 85 (own glow / sect); *Choices* Ch.1, 12 (fitting infortune); *Fifty
Aphorisms* #44 / 87 (the five-degree rule); Masha'allah *On Nativities* 1.23,
17 (domain by hemisphere); *PN IV* II.3, 1 ("for every year the native has
completed"), I.2, 1 & 4 (the revolution and its Ascendant), IX.8, 123 ("the
book which we worked on concerning nativities" -- matches the Timing caption
verbatim), and *Gr. Intr.* VIII.3, 28-29 (the Lot of Spirit). Help texts
checked describe the controls actually on the page; headings that name a
source show only that source's rule (the Chart page's four-footed/voice/
barren table shows both *Introduction* and *On Nativities* columns and says
so). The delineation tables are labelled as the *TNAC Reference Guide*'s own
summaries, and the Topical-Planets help states plainly that Rhetorius Ch. 57
and *Mathesis* III.2-13 "have not yet been checked against" the Guide -- an
honest qualification, not a defect.

---

## Not covered

- A full run of the corpus citation-check harness (only ten citations were
  spot-checked by hand). No provenance defect surfaced in the sample.
- The five High findings all stem from module-level computation ahead of
  `st.navigation(...).run()`; a single structural fix -- guarding the
  calculation and the target bundle behind the same `chart_ok` gate the
  sidebar validation already produces, and extending that validation to the
  ephemeris span and to loaded/stored field types -- would close H1-H5
  together. That fix is the owner's / the branch's to make; this pass only
  reports and reproduces.
