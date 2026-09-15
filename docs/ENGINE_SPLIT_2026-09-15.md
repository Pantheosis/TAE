# The engine into engine.py -- 2026-09-15

Branch `engine-split-2026-09-15` off `main` at `9d14aa6`. Item 8 of
`UI_FRAMEWORK_REVIEW_2026-09-15_SECOND_OPINION.md` (brief #7): everything
above the marker `# 4. STREAMLIT UI INTEGRATION` becomes `engine.py`, and
`app.py` keeps the pages and takes the engine whole. Cut in the quiet window
the review asked for, with no doctrinal branch open anywhere.

## What was asked

A split with **no observable change**: the same tables on every page, the
same SVG bytes, the same preferences and saved-charts behaviour, both halves
byte-for-byte what they were. `conftest.engine` becomes an import,
`build.spec` gains the module, the suite green.

## What it turned out to be

A pure star import is **not** behaviour-free here, for two reasons, both
found by building it and measuring rather than by reading it. Both have the
same root: **the engine half used to be re-executed, into a namespace of its
own, on every single run of the script.** An imported module is executed
once. Everything that relied on the re-execution broke quietly.

### Blocker 1 -- the star import killed all seven configurable readings

The review's premise -- "the page functions are closures over top-level
names, and a star import keeps them" -- is true in one direction only. The
UI does not only *read* engine names, it **writes** seven of them, at its
own top level (`app.py` lines 351-357, and `SOFTENED_INFORTUNE` at D-13).
`from engine import *` copies values into `app.py`'s namespace, so those
assignments stopped reaching the ten engine functions that read them:

| reading | engine functions that read it |
|---|---|
| `CONNECTION_PROFILE` | `_is_connected`, `_ray_activation_distance`, `doctrine`, `evaluate_reception` |
| `MOON_RAYS_ORB`, `MARS_WEST_RAYS_18` | `solar_rays_orb` |
| `DOMAIN_RULE` | `evaluate_accidental_dignities` |
| `EASTERN_RULE` | `evaluate_abu_mashar_condition` |
| `LOT_HOUSE_CUSP` | `_lot_point`, `calculate_topical_lots` |
| `SOFTENED_INFORTUNE` | `effective_infortunes` |

Measured, not inferred: on `main`'s engine, `evaluate_ptolemaic_aspects` for
the default chart returns **5 of 21 rows different** between `Sahl` and
`Abu Ma'shar`. Under the first cut of the split, `engine.CONNECTION_PROFILE`
still read `'Sahl'` after a run with the switch set to Abu Ma'shar, and the
rendered aspect rows were identical under both. Every one of the app's seven
doctrinal switches was dead.

### Blocker 2 -- the star catalogue detached after the first thread

`_FIXED_STAR_STATE['checked']` latches on first use. While the engine was
re-executed per run, `swe.set_ephe_path()` ran again each time.
**pyswisseph keeps its ephemeris path in thread-local state**, and Streamlit
gives each session's script its own thread. Measured: 28 of Sahl's stars
placed in the thread that attached the catalogue, **1 placed and 27 missing
in every other thread**. The Timing page's fixed stars would have been
present for the first session of a server process and absent for all the
rest. This is what the five failing `test_pages_render.py::timing` cases
were reporting.

## The ruling (2026-09-15)

Doctrine first, then what best serves the engine now and later: **the
readings become per-run state inside `engine.py`, thread-local, pinned once
at the top of each run; the fixed-star attach is keyed by thread.**

Not a sync block writing module globals from `app.py`. Module globals are
shared across every session in one process, and Streamlit runs sessions'
scripts in concurrent threads, so a sync could hand an evaluator another
reader's rule in the middle of a run -- a doctrinal fault worse than the one
being fixed, and one no test would reliably catch. `main` had per-run
isolation because each run executed the engine into its own namespace;
thread-local state keeps exactly that with the engine as a real module.

## What moved

### `engine.py`

The body is `main`'s `app.py` lines 1-15850, with a module docstring above it
and an `__all__` below it that exports every top-level name including the
underscore-prefixed ones (`_VS`, `_simulate_forward`, `_wheel_palette` and
the rest), which a star import would otherwise leave behind. Against those
15,850 lines the body carries **76 changed lines, all plumbing**:

**New, at the top** (37 lines): `import threading`, `_RUN =
threading.local()`, the `READINGS` tuple, `set_readings(**values)` and
`reading(name)`. `set_readings` raises `KeyError` on a name the engine does
not read -- a reading the engine ignores is a reading the page only *thinks*
it has changed. `reading(name)` returns the calling thread's value or falls
back to the module constant, so each reading's constant **stays where it
always was, next to the doctrine that explains it**, and an engine imported
with no run behind it (the harness's own use) answers with the course text's
reading exactly as before.

**Routed through `reading(...)`** -- thirteen sites in ten functions, a
one-token change at each except the last two:

| function | site |
|---|---|
| `solar_rays_orb` | `MOON_RAYS_ORB` (twice), `MARS_WEST_RAYS_18` |
| `evaluate_accidental_dignities` | `DOMAIN_RULE` |
| `_is_connected` | `CONNECTION_PROFILE` |
| `_ray_activation_distance` | `CONNECTION_PROFILE` |
| `evaluate_reception` | `CONNECTION_PROFILE` |
| `_lot_point` | `LOT_HOUSE_CUSP` |
| `calculate_topical_lots` | `LOT_HOUSE_CUSP` (in the row's own note) |
| `evaluate_abu_mashar_condition` | `EASTERN_RULE` |
| `effective_infortunes` | `SOFTENED_INFORTUNE`, read once into a local |
| `doctrine` | pins and restores through `set_readings` instead of `global` |

`doctrine` -- the context manager that pins an author's own rule for the
length of his own table -- was the one place that *wrote* the global. It now
writes the calling thread's reading, which also makes it safe between
sessions: on `main` one session entering `doctrine("Abu Ma'shar")` rewrote
the rule under every other session's evaluators for the duration.

**The fixed stars**: `_fixed_star_catalogue_ready()` now gates on
`_FIXED_STAR_STATE['checked'] and getattr(_RUN, 'fixed_stars_attached',
False)`, so each thread attaches the catalogue for itself. The module's own
`checked` flag stays and is still the outer gate, so a test that clears it
still forces the whole search again (`test_doctrine_fixtures.py` does).

**`st.cache_data`**: four engine functions are cached --
`_simulate_forward_pure`, `_sin_altitude`, `calculate_chronocrats`,
`calculate_prenatal_syzygy`. **None reads a reading**, directly or through
anything it calls (checked by a call-graph walk, not by eye). So no reading
has to become an argument of a cached function; had one, its cache would
have been keyed on arguments that did not include the rule.

### `app.py`

A short docstring, the imports the pages need, `import engine`, `from engine
import *`, then the marker and the UI half. Against `main`'s lines
15851-end the UI body carries **10 added lines and nothing changed or
removed** -- two insertions:

- after the seven `_reading(...)` assignments (main's UI line 335), a
  six-line comment and the `engine.set_readings(CONNECTION_PROFILE=...,
  EASTERN_RULE=..., MOON_RAYS_ORB=..., MARS_WEST_RAYS_18=...,
  DOMAIN_RULE=..., LOT_HOUSE_CUSP=...)` call;
- after D-13's `SOFTENED_INFORTUNE = ...` (main's UI line 482), one line:
  `engine.set_readings(SOFTENED_INFORTUNE=SOFTENED_INFORTUNE)`.

`FITTING_INFORTUNE` is deliberately **not** pinned: no engine function reads
it. The page reads it to compute `SOFTENED_INFORTUNE`, which is what the
engine reads, and `set_readings` refuses the name outright so the mistake
cannot be made quietly later.

The imports `app.py` needs, worked out from the UI half's free names and
confirmed by the suite: `re`, `sqlite3`, `datetime`/`time`/`timedelta`,
`Path`, `xml.sax.saxutils.escape` (**not** `html.escape` -- the pages use the
saxutils one), `pandas as pd`, `pytz`, `streamlit as st`, `swisseph as swe`,
`TimezoneFinder`.

Paths are unchanged: `Path(__file__).parent` in `engine.py` resolves to the
same directory as in `app.py`, the two files being side by side, so
`ephe/sefstars.txt` and the legacy saved-charts path still resolve, and
`atlas.db` is read from the UI half as before.

## The tests

### `tests/conftest.py`

`engine` is now an import -- `vars(importlib.import_module("engine"))` --
keeping the mapping shape the fixture always had, so **no test that uses it
was touched**. `EXECUTABLE_DIR` goes on `sys.path` at import, which is what
Streamlit does for a running script's own directory. `UI_MARKER` and
`APP_PATH` stay; `ENGINE_PATH` is new. `runner.magicEnabled` and
`pytest_configure` are untouched.

The source helpers moved rather than the tests that call them:

| helper | reads |
|---|---|
| `engine_source()` | `engine.py` |
| `ui_source()` | `app.py`, from the marker on |
| `app_source()` | **both** -- `engine.py` plus `app.py`'s UI half |

`app_source()` reads both because the UI half is not free of doctrine: it
carries 84 `VII.n` citations, 29 `Ch. 3, n` and 88 `Nativities`. Pointing
the citation scans at `engine.py` alone would have left those unchecked
while every test still passed -- the same class of silent hole as blocker 1.

One further consequence, fixed in the harness rather than the app:
`SAVED_CHARTS_PATH` and `PREFERENCES_PATH` are resolved at import, and an
imported module is cached where the re-executed half was not, so a test that
re-points `XDG_DATA_HOME` at a `tmp_path` got the previous test's directory.
`sync_engine_to_environment()` re-imports the engine when the environment
behind those paths has moved -- something tests do and a served app never
does, its environment being fixed for the life of the process.

### Which test file reads which path

| file | reads |
|---|---|
| `test_abu_mashar_citations.py`, `test_sahl_citations.py`, `test_nativities_citations.py`, `test_eye_degrees_abubakr_2026_09_15.py` | both (`app_source`) |
| `test_prose_counts.py` | `ui_source` for page text; `engine_source` for the station tolerance and the dead-function AST; `app_source` for the whole-app guards |
| `test_doctrine_fixtures.py`, `test_decisions_2026_09_08.py` | `engine_source` and `ui_source`, each where it did |
| `test_configurations_tabs.py`, `test_reference_page.py`, `test_wheel.py`, `test_top_navigation_2026_09_15.py`, `test_chart_layout_2026_09_15.py`, `test_theme_pictures_2026_09_15.py` | `ui_source` -> `app.py` |
| `test_config_2026_09_15.py` | both files by path (the bare-expression AST scan), and `ui_source` for the UI-only one |
| `test_preferences.py` | `APP_PATH` -- it runs the app |
| `test_base_tables.py`, `test_chart_input.py` | neither; they read the corpus and the saved-charts file |

One assertion changed, in `test_prose_counts.py`: the guard that the engine
compares a switch against its `_OPTIONS` tuple rather than a typed-out
string now expects `reading('EASTERN_RULE') == EASTERN_RULE_OPTIONS[1]`.
What it guards -- the right-hand side -- is untouched.

### `tests/test_engine_split_2026_09_15.py` (new, 18 tests, 11 s)

**A. The doctrine differential.** Every `evaluate_*`/`calculate_*` the top
level calls (49 of them, arguments resolved by parameter name the way the
top level assembles them) plus `pn4_timing_bundle`, run on `main`'s engine
half and on `engine.py`, over all six fixture charts at Florence 14:30 LMT
and both values of all seven switches: **84 (chart, state) pairs, every one
equal.** The test skips where the checkout cannot produce `main`'s `app.py`
(a shallow CI clone); these are the numbers from the branch's own run.

**B. The readings, by value and by thread** -- the gap that let the first cut
pass 2,269 tests with every switch dead, because the switch tests read table
shape and widget labels and never a cell. One test per reading asserting the
two values give *different* output, and a second running both values in two
threads at once (a barrier, so both are pinned before either reads) and
asserting each thread gets its own:

| reading | chart | evaluator |
|---|---|---|
| `CONNECTION_PROFILE` | 1240-05-23 | `evaluate_ptolemaic_aspects` |
| `MOON_RAYS_ORB` | 1240-05-23 | `solar_rays_orb` |
| `MARS_WEST_RAYS_18` | 1240-05-23 | `solar_rays_orb` |
| `DOMAIN_RULE` | 1240-05-23 | `evaluate_accidental_dignities` |
| `EASTERN_RULE` | **1240-09-18** | `evaluate_abu_mashar_condition` |
| `LOT_HOUSE_CUSP` | 1240-05-23 | `calculate_topical_lots` |
| `SOFTENED_INFORTUNE` | 1240-05-23 | `effective_infortunes` |

`EASTERN_RULE` is the one that needed a chart other than the default: it
moves VII.6, 27 and 45, which the default chart does not reach. Of the six
fixture charts it changes **1240-09-18, 1240-10-05 and 1240-01-04**, and the
first is the one taken. Two further tests: a thread that pins nothing reads
the module constants, and `set_readings` refuses `FITTING_INFORTUNE`.

**C. The fixed stars in a second thread**: the main thread places 28 of
Sahl's stars and a fresh thread must place 28 too. Before the per-thread
attach it placed 1.

## What was proved, and what was not

- **The SVG bytes.** `generate_hybrid_svg` on the default chart: 51,439
  bytes from `main`'s exec'd engine half, 51,439 from `engine.py`, strings
  equal.
- **`tests/fixtures/tables.json` unchanged**, no regeneration, no
  `UPDATE_TABLE_FIXTURE` run.
- **The suite**: `2287 passed, 6 xfailed in 26.74s`, `-n auto`. 2,269 to
  2,287 is the 18 new tests and nothing else.
- **The live server**: `streamlit run app.py --server.port 8518
  --server.headless true`, `/_stcore/health` returned `ok` and `/` served
  the page. AppTest does not exercise Streamlit's module watcher; the live
  run does.
- **The frozen build was NOT run.** No PyInstaller build was made on this
  branch. What would prove the frozen import works is a build whose
  `_internal` holds `engine.py` beside `app.py` and whose launcher opens the
  Timing page. The local analogue was run instead, from a scratch directory
  outside the checkout: `python -c "import sys;
  sys.path.insert(0, '<Executable>'); import engine"` imports it, reports
  its seven readings and places 28 stars. `desktop_launcher.py` is
  untouched.
- **`.github/workflows/tests.yml` needs no change** (`python -m pytest -q -n
  auto`, no path in it). `.claude/launch.json` is not in this worktree and
  was not touched, nor was anything else under `.claude/` or `.agents/`.

## A note for QA

The first cut of this branch passed the entire suite -- 2,264 of 2,269, the
five failures being the fixed stars -- with **all seven doctrinal switches
silently dead**. Nothing in the suite compared a cell of a table between a
switch's two values; the switch tests checked that the widget was on its
page, that its options came from the right tuple, and that the tables
rendered with the expected shape. `tests/fixtures/tables.json` pins which
tables appear and with which columns, not what is in them, so it could not
catch it either. The new file closes that for these seven readings. **Every
reading added from here on wants a value-level test of the same kind**, and
it is worth asking what else in the app is configurable and guarded only by
shape.
