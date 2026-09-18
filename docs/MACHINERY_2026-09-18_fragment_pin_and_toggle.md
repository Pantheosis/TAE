# Machinery fix branch F11 (2026-09-18): the fragment-rerun readings pin and the coordinate toggle

Branch `f11-machinery-2026-09-18` off `main` 9476d8b. The first fix branch
of the doctrine audit's fix phase. No doctrine is decided here; the
machinery is made to serve the readings it already has. `engine.py` is
untouched.

## What was asked

1. Every `@st.fragment` body must run under the run's own readings on a
   fragment-only rerun: an evaluator called from a fragment rerun gives
   the same answer as the full run (G18 of the audit, cards L8-G18-2 and
   L8-G18-R2-3, both readers, one recipe).
2. The readers' behavioural test on Streamlit's own server path, failing
   on `main` first, and an AST guard so that a future fragment cannot
   regress silently.
3. F02's `_manual_coords_switched` staleness, pre-existing on `main` and
   recorded in `docs/UI_CHANGES_2026-09-17_here_and_now.md` under "Seen in
   passing", fixed on the model of the "Set as home" fix.

## The fault

Since PR #45 the seven engine readings belong to a run and to its thread:
`app.py` pins them with `engine.set_readings` at the top of each run, and
every evaluator asks through `engine.reading()`, which falls back to the
module constant in a thread that has pinned nothing. Since the fragments
of 2026-09-15 a click on a widget inside a fragment reruns the fragment's
body alone, and Streamlit runs that body in a fresh ScriptRunner thread
whenever the previous run's runner has stopped -- the ordinary case, the
reader clicking after the page has rendered (`AppSession.request_rerun`
creates a new runner once the old one's queue has emptied). The script
does not execute on such a rerun: `ScriptRunner._run_script` looks the
stored fragment up and calls it. So nothing pinned, and the one fragment
path that reaches an evaluator reading a reading -- the Timing wheel's
Lots ring, `_ring_extras` -> `lot_by_id` -> `_lot_point` ->
`reading('LOT_HOUSE_CUSP')` -- drew the house-based Lots at the whole-sign
cusps under a 'quadrant cusp' run. On 1240-05-23 Florence at a target of
2026-09-17 (the Year view, one ring, Ascendant 190.503427): assets_lord2
15.246 -> 1.806, travel 177.557 -> 163.862, enemies_hermes 263.275 ->
253.862; the two death Lots, which carry their own cusp rule, unmoved. The
other four fragments reach no such evaluator (three reach no engine
function at all), confirmed by an AST walk before the fix.

## The mechanism

- **`_pin_readings(**values)`**, at both pin sites (the six at the top of
  the run, `SOFTENED_INFORTUNE` under `chart_ok`): calls
  `engine.set_readings` and records the values in `_RUN_READINGS`, the
  run's record of what it pinned.
- **`_pinned_fragment(func)`**: `st.fragment` over a `functools.wraps`
  wrapper whose first statement is `engine.set_readings(**_RUN_READINGS)`
  and whose second calls the body. Every one of the five fragments is
  declared with it; no bare `@st.fragment` remains.

Why it is right: the body Streamlit stores for a fragment rerun is a
closure over the full run that declared it (each full run re-registers
the fragment with a new closure over the new module dict), so
`_RUN_READINGS` read inside the wrapper is that run's record -- exactly
the values that run pinned. No doctrinal reading's control stands inside
a fragment (guarded), so nothing between the full run and the fragment
rerun can have moved a reading; the readings' widgets are outside the
fragments, and moving one is a full run. During the full run the wrapper
pins the same values again in the same thread. `functools.wraps` keeps
the body's `__qualname__` and `__module__`, from which Streamlit computes
the fragment id, so the ids are unchanged. Reruns that happen to land in
the still-alive thread already carry the pin and are unchanged.

The alternatives the brief allowed, and why not: re-pinning by hand at the
head of each body is the same thing with five sites to forget; a fallback
inside `engine.reading()` to session state would couple the engine to
Streamlit, and the brief asked that the engine stay as it is unless the
mechanism needed a hook -- it does not.

## The coordinate toggle (F02)

The `on_change` callback of "Enter coordinates directly" wrote the fields
from `_resolved_lat` / `_resolved_lon`, the previous run's place. A city
typed over the box and the toggle clicked without Enter delivers the edit
and the switch in one run (the mouse-down blurs the box, which commits the
text), so the fields started at the place the box no longer showed --
the same staleness the adversarial pass found in "Set as home".

On that fix's model -- handle at the site, from this run's values -- the
callback now only flags that the toggle moved (`_coords_switched`, popped
at the toggle's site), and the site starts the fields from this run's
values before they are drawn: the box's committed text, which is in its
key on that run whether or not the box is drawn, resolved as the box
resolves it (a typed pair through `parse_lat_lon`, else the atlas's first
match) when the text has moved since it was last resolved
(`_resolved_text`, now recorded beside `_resolved_lat` / `_resolved_lon`);
the last resolution -- its choice among the matches included -- when the
text has not moved, or when the moved text resolves to nothing (the place
the reader was working from, as on `main`). No foot rerun is needed: the
fields stand below the site, so the keys are written before the widgets
are drawn. The atlas query is now `_atlas_matches`, the one lookup the
box's branch and `_place_the_box_holds` share, its two sentences the
constants `ATLAS_MISSING_MESSAGE` and `ATLAS_NO_MATCH_MESSAGE`; the box's
branch is otherwise as it was.

One behaviour is deliberately kept from `main`: a moved text with no match
starts the fields at the last place that resolved rather than at what the
fields last held (pinned by a test, so the choice is visible).

## Tests

`tests/test_fragment_readings_2026_09_18.py` (11):

- `test_the_timing_wheels_lots_are_the_runs_on_a_fragment_rerun` -- the
  readers' C-FR recipe as written: a full run under AppTest with
  `_lot_house_cusp='quadrant cusp'`, `_timing_lots=True`, the target
  2026-09-17; then a second `LocalScriptRunner` on the same session state
  and a shared `MemoryFragmentStorage` (every runner's `__init__` patched
  to share one) with `RerunData(page_script_hash=at._page_hash,
  fragment_id_queue=[the wheel's id])`, `Runtime._instance` mocked as
  `AppTest._run` mocks it, in a new thread; `engine.lot_by_id` wrapped
  after `make_app` to record (thread, `reading('LOT_HOUSE_CUSP')`,
  (lot id, ring Ascendant), longitude). Asserts the thread differs, every
  (lot, ascendant) longitude equal to the full run's to 1e-6 over the
  39 keys, the three cusp-based Lots and the two death Lots among them,
  and every reading seen 'quadrant cusp'. On `main`: "Lots that moved on
  the fragment rerun (full run, fragment rerun): {('assets_lord2',
  190.503427): (15.246…, 1.806…), ('travel', 190.503427): (177.557…,
  163.862…), ('enemies_hermes', 190.503427): (263.275…, 253.862…)}".
- `test_the_chart_wheels_renderer_runs_under_the_runs_readings` -- the
  Chart page's fragment reaches one engine function,
  `generate_hybrid_svg`; with every reading off its default it is wrapped
  to read back all seven; on the fragment rerun the readback equals the
  full run's. On `main`: the defaults against the run's ('Sahl' vs "Abu
  Ma'shar", 12.0 vs 15.0, …).
- `test_every_fragment_pins_the_runs_readings_in_its_own_thread[chart |
  configurations | dignities | timing]` -- `engine.set_readings` wrapped
  to log (thread, values, readback); each fragment of the page (1, 2, 1,
  1 -- the brief's "Findings grids" are the Dignities page's planets
  block and the Configurations page's two tick grids) rerun alone; the
  pin happens in a new thread with exactly the run's record, and the
  thread answers with it. On `main`: "the fragment rerun on <page> pinned
  nothing in its thread".
- The guards: `test_every_fragment_is_declared_with_the_pinning_decorator`
  (the five names, each with the bare `_pinned_fragment` and nothing else
  naming a fragment), `test_st_fragment_is_used_once_inside_the_pinning_decorator`
  (every `.fragment` / `fragment` reference in `app.py` is the one call
  inside the wrapper; no import of one),
  `test_the_pinning_decorator_pins_the_record_before_the_body` (the inner
  function's two statements, `**_RUN_READINGS` and nothing else, handed to
  `st.fragment`), `test_every_pin_in_the_file_goes_through_the_record`
  (`engine.set_readings` called only inside `_pin_readings` and the
  wrapper; `_pin_readings` pins then records; its two callers carry the
  seven names), `test_no_doctrinal_readings_control_stands_inside_a_fragment`
  (no `READINGS_REGISTRY` widget key as a literal in any fragment body --
  the premise; passes on `main` too).

`tests/test_coords_toggle_2026_09_18.py` (6): Berlin resolved, "Madrid"
set and the toggle switched in one `run()` -> the fields at 40.4165,
-3.7026 and the box "Manual [40.4165, -3.7026]" (on `main`: 52.5244,
13.4105, Berlin); a pair "10.5, -20.25" likewise (on `main`: Berlin); the
third match "Madrid, 33 (CO)" chosen then the toggle alone -> the chosen
match's 4.7325, -74.2642 (passes on `main`); a moved text with no match
-> Berlin (passes on `main`); nothing ever resolved -> the seeds (passes
on `main`); and the callback's one-flag shape, `_atlas_matches` called
from exactly the box's branch and the helper, the query written once.

The two `_fragment_defs` helpers of `test_fragments_2026_09_15.py` and
`test_row_detail_2026_09_15.py` now key on `_pinned_fragment`.

On an archive of `main` (9476d8b) with the two files copied in: 13 of the
17 fail, 4 pass -- the four being behaviours `main` already had.

## Gates

- Harness differential: `harness.py --sha 3ada7b6` with the app venv and
  `PYTHONPATH` at this worktree, against
  `process/adjudication/harness_run_2026-09-17_3a90fe3.txt`: the 77
  predicate lines identical (the harness runs no fragments; `engine.py`
  is unchanged).
- `tests/tools/prose_preserved.py 9476d8b --engine`: 3745 sentences, 193
  locators, 0 misses, 0 count drops; the reverse (`3ada7b6 --engine --tree
  <archive of main>`): the same, 0 misses -- the two atlas sentences moved
  into constants and nothing was added or lost.
- The corpus checker from a scratch copy of
  `process/citation_check_2026-09-17/` on `main` and on the branch
  (`CITE_CORPUS`, `CITE_APP`): `citations.tsv` identical apart from line
  numbers (2897 rows); `quote_check` verbatim 468, near 9, absent 46,
  no-quotation 2342, unresolved 32 on both, the near and absent rows the
  same rows.
- `python tests/test_text_lengths_2026_09_17.py`: silent.
- Full suite `-n 8`: 3753 passed, 1 skipped, 1 failed --
  `test_pages_render.py::test_page_renders_expected_tables[timing-1240-09-18]`,
  which fails on the archive of `main` today as well: the 1240-09-18
  chart's Timing page renders 38 tables with the target at 2026-09-17 (the
  fixture's day) and 37 at 2026-09-18 or 2026-09-19 -- one of the three
  findings under "The image of the revolution of the year: its points"
  empties when the target moves to the revolution of a different year, and
  the fixture slot depends on the day the suite runs. Not this branch's;
  the fixture was not regenerated.

## Departures

None from the brief. The mechanism chosen is the decorator, one of the
three the brief offered. The behavioural test covers "one evaluator reached
by each other fragment site" as far as the sites reach one: the Chart
wheel's renderer is probed directly; the planets block and the two tick
grids reach no engine function, so their probe is the pin in the rerun's
thread, which is what any evaluator they may come to call would read.
