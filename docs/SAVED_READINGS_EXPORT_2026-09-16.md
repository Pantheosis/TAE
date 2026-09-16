# The readings a chart is saved with, and the analysis export -- 2026-09-16

Branch `saved-readings-export-2026-09-16` off `main` at `1fba0cc`. Findings
**F03** and **F08** of the independent UI review of 2026-09-16, with **E04**
as the acceptance case. It builds on `docs/RECORD_LIFECYCLE_2026-09-16.md`
(a record's identity, Replace / Keep both, the delete confirmation,
`chart_record_fault`) and `docs/HOSTILE_FIXES_2026-09-16.md` (nothing from
disk reaches a widget key unvalidated).

No doctrine, no evaluator, no table of results changed. `tests/fixtures/tables.json`
moves by exactly one column on exactly one table; the diff is described at
the end.

## The ruling

> A saved chart is a **chart record** and, from this branch, also carries the
> **readings in force** when it was saved. On load the app says which it is
> doing: restore the saved readings, or keep the current ones -- an explicit
> choice, never a silent migration. And an **Export analysis** action writes a
> versioned file binding what was entered, what was in force, what was
> computed, and what computed it.

E04 is what the ruling answers. The review saved a chart with the shared
connection rule on **Abu Ma'shar**, set the rule to **Sahl**, and loaded the
chart again: Sahl stayed in force, the control and the caption said Sahl, and
nothing anywhere said that the chart had been read one way and was now being
read another. The record held a nativity and nothing about how it had been
read.

## The record, schema 2

`_chart_record()` writes the ten fields it always wrote, and two more:

```json
{
  "date_string": "1982-11-19",
  "time_string": "11:44:00",
  "time_standard": "Standard time (pytz)",
  "utc_offset": null,
  "location_query": "Petoskey, MI (US)",
  "lat": 45.37334,
  "lon": -84.95533,
  "target_mode": "Date",
  "target_date": "2026-09-15",
  "target_age": 43,
  "readings": {
    "_connection_rule": "Abu Ma'shar",
    "_eastern_rule": "hemisphere",
    "_fitting_infortune": false,
    "_moon_rays_15": false,
    "_mars_west_18": false,
    "_domain_rule": "Abu Ma'shar",
    "_lot_house_cusp": "whole-sign place",
    "_pn4_monthly_turn": "Dykes: always forward",
    "_reading_depth": "Course text"
  },
  "saved_with": {"app": "1.4.0-dev", "schema": 2}
}
```

- **`readings`** is one entry per row of `READINGS_REGISTRY`, keyed by the
  store key, holding the value the top level reads a moment later
  (`_reading(widget_key, store_key, default)`). Display preferences are *not*
  here: the bounds ring, the dark wheels and the wheel layout change what is
  drawn, not what is computed, and a record that restored them would be
  restoring someone's eyesight rather than their doctrine.
- **`saved_with`** names the app that wrote the record and the schema it is in.

A record written before this branch has neither key and is **schema 1**. It
is told apart by what it holds, never by what it claims:
`chart_record_schema()` reads the presence of a `readings` mapping, and
nothing is written into an old record until the reader saves it again.

`READINGS_REGISTRY` and `_reading()` moved up in `app.py`, above the
saved-chart picker: a record now has to be built, compared and restored
before the sidebar has drawn anything, so the registry has to exist there.

## Modified, and which side moved

`_records_match()` is now two comparisons with one answer:

| helper | what it compares |
|---|---|
| `_record_inputs_match` | the nativity, on the stored record's own fields, as before (`saved_with` is never compared: a record saved by an earlier build has not been edited for having been saved by it) |
| `_record_readings_match` | only the readings the STORED record carries -- a schema-1 record carries none and so cannot disagree with any |

The strip reads `<name> (modified)` for either, and the caption under the
picker names the side:

- **`Edited since it was saved.`** -- the nativity moved (as before);
- **`Saved with other readings.`** -- only the readings moved;
- both lines when both moved.

## The load, and its two branches

`_restore_chart()` writes the nativity into the widget keys exactly as it
did, and then **changes no reading at all**. What it leaves behind is the
question:

- readings present and different from the ones in force -->
  `st.session_state["_readings_pending"] = name`;
- readings present and equal --> nothing: the load is silent, as it should be;
- no readings (schema 1) --> `_readings_legacy`, one caption, once.

Under the picker:

> **'Live F03' was saved under other readings.**
> [ Open saved readings ] [ Keep current readings ]

**Open saved readings** does not write from where it is asked. It records
`_readings_open_now` and the writing happens at the foot of the sidebar,
beside the delete, for the reason that branch learned in the browser: a
`st.rerun()` from beside the picker abandons the run before the date, time
and place widgets are drawn, and Streamlit discards the state of a widget a
run did not draw -- the boxes come back holding the example nativity. At the
foot, each reading goes in through `_set_reading()`, which is the path
`_persist()` uses when a reader moves the control themselves: the store key
the top level reads, the widget key the control will be drawn from, and the
preferences file. So the control on its own page shows it, the evaluators
compute under it, and the next session opens under it.

**Keep current readings** writes nothing and clears the question in its own
placeholder, without a rerun. The chart then stands `(modified)` by its
readings, with `Saved with other readings.` under the picker -- which is the
truth of it, and the reason the branch is not silent either.

A schema-1 record gets one sentence instead of a question, because it has
nothing to restore:

> Saved before readings were stored with a chart; results use the current
> readings.

The autoload of `last_chart` at launch runs through the same
`_restore_chart()`, so a session that opens on a chart saved under other
readings opens with the question shown and nothing changed.

The harness never sees any of it: `make_app()` seeds the widget keys
directly and never fires the picker's `on_change`, which
`test_the_harness_never_has_the_prompt` pins.

## Validation

`chart_record_fault()` (engine.py, section 0) gains the readings:

- a record with **no** `readings` is schema 1 and is not a fault;
- a value the widget could not take is a fault -- `'Ptolemy'` for the
  connection rule, `"yes"` for a checkbox -- because seeding one into a
  widget key raises where the widget reads it, which is H3's lesson about
  every other field. The sentence reads *"its connection rule is not a
  reading this app offers."*;
- a key this app does not know is **ignored, not refused**: a record from a
  later build, or one with a reading since withdrawn, is still this reader's
  nativity. The key stays in the file and is not acted on.

The legal values live in `CHART_RECORD_READINGS`, which names each store key
and the module-level options tuple (or `bool`) it may hold, resolved at call
time because most of those tuples are defined further down `engine.py`.
`test_the_registry_and_the_engines_reading_schema_agree` holds that list and
`READINGS_REGISTRY` in step, so a reading added to one cannot go unvalidated
in the other.

## The Sources page

The *Readings in force* table gains one column, **Saved with this chart**,
between *In force* and *Default*, showing what the record the picker names was
saved under, and `–` where there is nothing to show: no record selected, or a
schema-1 record. Nothing on that page sets anything -- the choice is offered
on the load, beside the picker -- and Reset is untouched.

## Export analysis (F08)

Two buttons in the sidebar, under Save, in a `st.sidebar.container()`
reserved there and filled at the foot of the script (the export is made of
the pages' own row lists, and those need the chart):

- **Export analysis (JSON)** -- `analysis_<name>_<date>.json`
- **Export analysis (Markdown)** -- `analysis_<name>_<date>.md`

Both carry the same header block. When `chart_ok` is False both are rendered
**disabled** with the caption *There is no chart to export; the input above
says why.* -- the action exists, and the reason it cannot run is the one the
sidebar already gives.

### The schema

`analysis_export()` is a pure function: every value it writes is passed in.
Its top-level keys are `schema`, `exported`, `app`, `chart`, `input`,
`entered`, `readings`, `display`, `target`, `results`, `status`, `precision`.
The header from the live run of this branch:

```json
{
  "schema": 1,
  "exported": "2026-09-16T06:19:30Z",
  "app": {
    "version": "1.4.0-dev",
    "streamlit": "1.62.0",
    "python": "3.14.7",
    "pyswisseph": "2.10.3.2",
    "ephemeris": "Moshier (built in)",
    "engine_file_sha256": "3730d6c0d435d854dc2fabdc04760a6aa2fa4b67734ec3254059e0583077e6a1"
  },
  "chart": "Live F03"
}
```

- **`input`** is the committed chart: date, time, time standard, the resolved
  UTC offset in hours, the zone, the place label, latitude, longitude, the
  Julian Day UT, and the calendar in force. **`entered`** is the record
  `_chart_record()` writes, `readings` and `saved_with` included -- what was
  typed, beside what it resolved to.
- **`readings`** is every `READINGS_REGISTRY` entry as
  `{label, store_key, value, default, set_on}`. **`display`** is the three
  preferences that change what is drawn: `chart_bounds`, `wheel_dark`,
  `wheel_layout`. They are kept apart deliberately, which is the distinction
  the review asked for.
- **`target`** is `{mode, date, age}`.
- **`results`** is keyed by page, then by the heading the reader sees, to a
  **list** of tables (several headings carry more than one), each
  `{columns, rows}` and a `citation` where the page prints one. On the
  default chart that is 78 tables over six pages: Chart, Dignities and
  places, Configurations, Lots, Lunation and victors, Timing.
- **`status`** is `chart_ok`, `chart_error`, `equal_hour_approximation` (the
  planetary hour where the Sun neither rises nor sets), `forward_search_days`
  (200, read from `_simulate_forward`'s own default rather than written down
  again), `stale` (the draft date does not parse and the tables are the last
  valid chart's), and `target_out_of_reach`.
- **`precision`** says in one line that the JSON holds the engine's own
  numbers at the precision it holds them, and that the Markdown carries the
  display strings the pages show.

The Markdown report has the same header and the same sections -- *What
computed this*, *What was entered*, *The moment and place the chart was cast
at*, *The readings in force*, *Display preferences*, *The target*, *Status*,
*Results* (page, then heading), *Precision* -- with every table as a Markdown
table. Citations are the ones the pages already print in their captions.
**No source text beyond that**: the translations are copyrighted and no
passage of them is in either file.

### Where the rows come from

The export never computes anything. Every evaluator already runs once a run
at the top level inside `if chart_ok:` -- the aspects, the receptions, the
strength and weakness rows with their `Testimonies`, the victors, the whole
`pn4_timing_bundle` -- so those are read where they stand. Nine row lists
were built **inside** a page function; they are built by a helper now, and
the page calls it:

`_positions_rows`, `_calculated_point_rows`, `_house_cusp_rows`,
`_lordship_rows`, `_sect_table_rows`, `_house_lord_rows`,
`_classical_lot_rows`, `_topical_lot_rows`, `_syzygy_rows`.

What each page renders is unchanged, which is why `tables.json` did not move
for any of them. The export carries the list the reader saw, so the two
cannot drift.

A table the pages do **not** draw is not in the export: `_finding()` prints
its "nothing found" sentence instead of a grid when a list is empty, and the
Timing page skips a bundle entry that came back `None` -- writing an empty
table down would claim a grid stood where a sentence did. The III.2
checklist is guarded on `pn4['iii2_type']`, exactly as the page guards it.

### The cost, and where it is paid

Measured under `AppTest` on the default chart, three runs each on the Chart,
Timing and Sources pages, steady state:

| stage | ms |
|---|---|
| building the analysis (row lists + assembly) | 1.9 -- 2.2 |
| `json.dumps` (419 KB) | 1.2 -- 1.3 |
| the Markdown report (194 KB) | 2.1 |
| **total per rerun** | **5.3 -- 5.7** |

Well under the ~50 ms the ruling set as the threshold, so **the export is
built on every rerun, in the sidebar, with no popover and no button in
front of it**. It is cheap because the expensive part is already done: the
evaluators and the timing bundle run at the top level whether the export
exists or not, and what the export adds is reshaping and two dumps.
`engine.py`'s sha256 is computed once per process and cached -- the file
cannot change under a running app.

Worth recording for whoever revisits this: `st.popover` would **not** have
saved the cost. Its body is rendered on every run and merely hidden, so the
alternative to paying it every rerun was a button in front of it, and at 5 ms
that would have been a click charged for nothing.

### The frozen build

`engine_file_sha256()` asks `Path(engine.__file__)`, not a path built from
`__file__`. In the packaged build `engine.py` is a **bundled data file**
(`build.spec`'s `datas` carries `("engine.py", ".")`), extracted beside the
executable's other data, and that is the file the import actually read. An
unreadable one is reported as `"unavailable"` rather than guessed at.

## The version constant

`APP_VERSION = "1.4.0-dev"` in `engine.py` section 0. There was none: a
record written by one build and an analysis exported from another could not
be told apart, which is half of what F08 asked for. It is written into every
saved record's `saved_with`, into every export's `app` block, and printed in
**one** place on the pages -- the Sources page's citation-key caption, which
now opens *"This app 1.4.0-dev."*

That is the owner's exception to the rule that page text carries no build
process (`docs/PAGE_TEXT` rule, guarded by
`tests/test_prose_counts.py::test_page_strings_carry_no_build_process`). The
reason it is an exception and not a breach: it is the identity an exported
analysis is signed with, and a reader holding an older export needs to be
able to read the current one off the app itself. Everywhere else the rule
stands unchanged.

`docs/RELEASING.md` gains step 2, **Set the version**: `APP_VERSION` is the
tag without its `v` and without `-dev`; set it and merge that before tagging,
then put it back to `<next>-dev`. The following steps renumber.

One guard was widened by exactly two strings.
`BUILD_PROCESS_MARKERS` includes `.md` to catch a page naming one of this
project's own documents; the Markdown report has to be called something, so
`".md"` and `"analysis.md"` -- the file's NAME in a save dialog, never text on
a page -- are exempted by value. A page saying "see SOURCES.md" still fails.

## Engine functions changed

`engine.py`, section 0 only, nothing doctrinal:

- **`APP_VERSION`** -- new module-level constant (the version identity);
- **`CHART_RECORD_SCHEMA`** -- new constant (2);
- **`CHART_RECORD_READINGS`** -- new table: each stored reading's store key
  and the options it may hold;
- **`_reading_options()`** -- new helper (resolves an options tuple or
  mapping by name, at call time);
- **`_reading_value_is_usable()`** -- new helper (one reading's value, or
  True for a key this app does not know);
- **`_readings_fault()`** -- new helper (the first stored reading this app
  cannot set);
- **`chart_record_fault()`** -- extended: a `readings` mapping, when present,
  is validated; its absence is schema 1 and not a fault. The signature and
  the return shape are unchanged;
- **`chart_record_schema()`** -- new (1 or 2, by what the record holds);
- **`chart_record_readings()`** -- new (the readings the app knows, as
  `{store key: value}`).

`load_saved_charts()`, `write_saved_charts()`, `_read_chart_mapping()` and
`_validate_chart_mapping()` are untouched.

## The fixture diff, in words

`tests/fixtures/tables.json`: six lines changed, one per chart. On the
**Sources and readings** page, the **Readings in force** table's column list
gains `"Saved with this chart"` between `"In force"` and `"Default"`. No
table was added, removed, renamed or reordered on any page, and no other
table's columns moved. Regenerated serially
(`UPDATE_TABLE_FIXTURE=1 python -m pytest tests/test_pages_render.py`, no
`-n`), as the harness requires.

## What the browser showed (port 8529, this worktree)

Run with `XDG_DATA_HOME` pointed at a scratch directory holding a **copy** of
the owner's `saved_charts.json` and `preferences.json`; the real directory
was never on the path. Input was DOM-driven.

- The connection rule set to **Abu Ma'shar** on the Configurations page, the
  Petoskey nativity saved as **Live F03**: the record reached the file with
  `"readings": {"_connection_rule": "Abu Ma'shar", ...}` and
  `"saved_with": {"app": "1.4.0-dev", "schema": 2}`.
- The rule flipped to **Sahl** with the record still selected: the strip read
  **Live F03 (modified)** and the caption under the picker **Saved with other
  readings.** -- and nothing else, the nativity being untouched.
- The chart loaded again: **'Live F03' was saved under other readings.** with
  **Open saved readings** and **Keep current readings** beside each other,
  the connection radio still on Sahl, and the aspects table's caption still
  *"Sahl rule in force"*. The load had changed nothing.
- **Keep current readings**: the question gone, the rule still Sahl, the
  strip still **Live F03 (modified)**, the caption still *Saved with other
  readings.*
- Loaded again, **Open saved readings**: the radio on **Abu Ma'shar**, the
  aspects caption *"Abu Ma'shar rule in force"*, the strip back to plain
  **Live F03**, the question gone -- and `preferences.json` in the scratch
  profile reading `"_connection_rule": "Abu Ma'shar"`, so the preference
  followed.
- The Sources page's caption read **This app 1.4.0-dev.** ahead of the
  citation key.
- Both export buttons stood under Save. Fetched from the media URLs the
  buttons registered: the JSON's `app` block is the one printed above, its
  `chart` **Live F03**, its `_connection_rule` reading
  `{"value": "Abu Ma'shar", "default": "Sahl"}`, its `results` over the six
  pages, its `status` `chart_ok: true`; the Markdown's first lines
  **`# Analysis: Live F03`** / *Exported 2026-09-16T06:19:30Z by this app
  1.4.0-dev.* -- the same header, 207 KB.

The owner's own directory before and after, unchanged:

| file | sha256 |
|---|---|
| `saved_charts.json` | `dd817c155cb23a2cbb1d8b79b1e13d7fc33f798d6bce6c9290d211c924fd921d` |
| `preferences.json` | `4070389306f868fe8cabd5c18c9a244b35b8361101d61a99326a748a32bf1519` |

Both hashes are identical before and after the check, and neither file's
mtime moved.

## What the tests pin

`tests/test_saved_readings_export_2026_09_16.py`, 44 tests.

| Case | What is pinned |
|---|---|
| E04 | the record carries every registry reading and its `saved_with`; loading it under another rule changes no store and shows the question with both buttons |
| E04, branch 1 | **Open saved readings** puts the store and the widget key on Abu Ma'shar, the question goes, and the aspects table is then the Abu Ma'shar table row for row (the two are shown to differ first, so a reading restored without reaching the evaluators fails here) |
| E04, branch 2 | **Keep current readings** leaves the store on Sahl, the strip reads `(modified)`, and the caption is `Saved with other readings.` alone; an edited nativity as well gives both lines |
| schema 1 | a record with no readings loads with the one caption, no question, and no accusation; a record with equal readings loads silently |
| the harness | no pending state and neither button, in a session that seeds its keys |
| saving again | the record's readings become the ones in force and the strip drops `(modified)` |
| `chart_record_fault` | an invalid reading value is a fault with a readable sentence; an unknown key is not, and is dropped from `chart_record_readings()`; a non-mapping `readings` is a fault |
| the two lists | `READINGS_REGISTRY` and `CHART_RECORD_READINGS` name the same store keys |
| the Sources column | `–` where nothing is selected; the record's own value beside the value in force where one is |
| the export's header | schema, an ISO-UTC `exported`, the exact twelve top-level keys, the app block with a 64-hex sha equal to a fresh sha256 of the imported `engine.py`, the committed input, every registry reading with its value and default, the display preferences kept apart, the target and the status flags |
| the export's results | fourteen named tables, each with the row count the page renders and (where the page's columns are the row's keys) its columns; strength and weakness rows carry their `Testimonies`; the Timing headings are all headings the Timing page renders; a table the page does not draw is absent, and is present on the chart where it is drawn |
| the files | the JSON round-trips through `json.loads`; the Markdown carries the same sections, the same page and heading levels and the same sha |
| the buttons | both present and enabled when `chart_ok`, both present and disabled with the caption when not |

Full suite: **2665 passed, 1 skipped, 6 xfailed**.

## What was not done

F09 (the chart strip's unqualified hour lord elsewhere) is named in the same
review item as F08 and is untouched here: the export records
`equal_hour_approximation`, but the strip's own wording is a separate
ruling. F16's Duplicate / Save-as vocabulary and F18's control wording remain
where `docs/RECORD_LIFECYCLE_2026-09-16.md` left them. The export carries no
stable per-result rule IDs -- the review asks for them, and they are a
doctrinal identifier the engine does not yet have; the citation each page
prints is what travels instead.
