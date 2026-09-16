# A draft, a committed nativity, and a shell that survives -- 2026-09-16

Branch `input-state-2026-09-16` off `main` at `732a8a9`. Findings F01, F02,
F05 and F17 of the independent UI review of 2026-09-16
(`traditional_astrology_engine_ui_ux_review.md`), with its own reproductions
E01, E02, E03, E07 and E15 as the acceptance cases. No doctrine, no
evaluator, no page prose beyond the sentences the brief names: `engine.py`
is byte-identical to main's (`git diff main -- engine.py` is empty).

## The principle the four findings share

The sidebar holds **draft** text. The chart is computed from a **committed,
validated** input. A saved record stores committed values only. The page
shell never disappears because a draft is invalid.

The review found all four halves of that sentence broken at once: the strip
printed the draft, the save wrote the draft, an impossible latitude reached
the engine under one time standard and not another, and any bad input at
all took the navigation with it.

## F01 -- one committed date, and nothing else written down

`date_string` is the draft; `input_date` is the committed date -- the draft
when it parses, the last one that did when it does not. The new name beside
it is `date_is_valid`, which is what the save and the notice read.

- **The strip** prints `input_date` in ISO and the committed time, where it
  used to print `date_string`: `not-a-date 14:30:00` named a chart that had
  never been cast.
- **The save** writes `input_date.isoformat()`, never the raw text. A record
  therefore reloads in a fresh session as the chart it was saved as, instead
  of falling to the 1240 default because that session has no
  `_date_last_good` behind it.
- **An invalid draft cannot be saved at all**: `st.sidebar.error("The date
  is not valid; nothing was saved.")`, and nothing is written -- not the
  in-memory dict, not the file. An unresolved or impossible place refuses
  the same way with `"No place is resolved; nothing was saved."` (a
  coordinate out of range resolves no place either, so it takes that same
  refusal rather than a sentence of its own).
- **A chart that has not moved says so.** `_stale_notice()`, called at the
  foot of `_chart_strip()`, puts one line directly under the strip on every
  page while the draft does not parse:
  `Results have not updated. Showing the last valid chart: <date> <time>.`
- A record written by the old version, with a malformed `date_string` in it,
  loads without crashing: the string goes into the date box and the sidebar
  treats it as it treats any malformed text -- the last good date, and its
  own error. Pinned by a test.

The save block's arms are now: no name, invalid date, no place, else write.

## F02 -- the coordinates

**(a) The toggle is a change of input method, not of place.** Each run that
resolves a valid pair records it in `st.session_state["_resolved_lat"]` and
`["_resolved_lon"]`. `_manual_coords_switched()`, the toggle's `on_change`,
writes that pair into `manual_lat_key` / `manual_lon_key` when the fields
are switched **on**. A callback runs before the widgets of the rerun it
triggers, which is the same window the saved-chart loader writes in. With
nothing resolved yet the Florence constants stand as the fields' default.

The regression harness seeds those keys directly and never changes the
toggle, so the callback never fires for it and every existing test's
Florence is untouched -- asserted, not assumed
(`test_the_harness_seeds_the_fields_and_the_callback_never_fires`).

**(b) One validation, before any time standard.** `coordinates_in_range()`
(finite; latitude in [-90, 90]; longitude in [-180, 180]) is applied once,
to the manual fields and to a `lat, lon` pair typed into the search box
alike, before the LMT / named-zone / manual-offset branch. Out of range:
`st.sidebar.error("Latitude must be between -90 and 90 and longitude
between -180 and 180.")`, no chart, and the shell stays (F05). The review's
latitude 91 gave tables under a manual offset and an uncaught
`Invalid latitude 91.0` under a named zone; it now gives the same one
sentence under all three. A polar but possible latitude still casts -- the
engine refuses for itself what it cannot compute there.

The two `number_input`s carry `min_value` / `max_value` as well, so the
widget refuses out-of-range typing. That is not enough on its own: a value
seeded into the key is silently pulled to a bound instead (Streamlit 1.62
turns a seeded 91.0 into -90.0), so the fields' **draft** values are read
before the widgets render and validated as they stand.

## F05 -- the shell survives an invalid input

`st.navigation(pages, position="top").run()` used to sit at the end of the
`if location_query and lat is not None ...:` / `if tz_name:` block, with
three `st.stop()` calls above it. An empty location, an unmatched city, an
impossible coordinate or an ambiguous DST hour rendered the sidebar and
nothing else.

Now:

- the sidebar's validation ends in **`chart_ok`** (bool) and **`chart_error`**
  (the one sentence, or None);
- the calculation block runs only under `if chart_ok:`;
- the three `st.stop()` calls are `chart_ok = False` with `chart_error` set
  to the same text the sidebar box prints (the box still prints it); the
  `try` arms that followed them are now `else:` arms, so nothing runs on a
  name `st.stop()` used to skip;
- the `else` of `if tz_name:` -- "Timezone boundary not found for
  coordinates." -- has moved up beside the branch it belongs to and feeds
  `chart_error` too;
- the page functions are defined **unconditionally**, at module level. They
  are closures over the top-level names and resolve them at call time, so a
  page that is not called never touches a name an invalid run left unbound;
- each of the seven pages that read the chart opens with
  `if not chart_ok: _recovery_panel("<its header>"); return`.
  `_recovery_panel()` renders the page's own `st.header`, then
  `st.error(chart_error)` and one caption: *Correct the nativity in the
  sidebar; the reference tables and the sources stay available.*
- `_chart_strip()` prints nothing when there is no chart, so a recovery page
  has no strip;
- `st.navigation(...).run()` is at module level, always reached.

**Reference tables and Sources and readings are not guarded.** Both read the
engine's tables, not the chart: an AST pass over every name the calculation
block binds found neither page using one (the Sources page's readings table
included), and both render the same number of tables on an invalid run as on
a valid one -- 7 and 2 -- which a test now pins.

### The dedent proof

`test_the_page_functions_are_mains_own_one_guard_line_apart` takes main's
`app.py` from git, finds the nine `page_*` functions in each file wherever
they are nested, drops the guard statement from the seven that have one
(asserting its exact text), and compares `ast.unparse` of the bodies.
Every one is main's function, unchanged, with two qualifications recorded in
the test itself:

- **two docstrings** carry a continuation line, and a continuation line
  inside a triple-quoted string loses eight spaces when the code around it
  is dedented. Docstrings' internal whitespace is collapsed before the
  comparison; they are the only strings whose text moves at all, every other
  literal in the range being a single-line token.
- **`page_timing` has one deliberate difference**, F17's, and the test
  replaces exactly that one statement with main's before comparing (and
  asserts it occurred exactly once).

`tests/fixtures/tables.json` is unchanged -- proved twice: by
`test_pages_render.py` passing against it, and by a test that compares it
with main's copy.

## F17 -- the Timing target keeps the last valid target

An unparseable target date fell to *today*, so an invalid request silently
analysed a different period. It now keeps the last target that parsed:
`_target_last_good` in session state, seeded from the initial default, set
on every successful parse, read on every failure. Today is used only by a
session that has never had a valid target.

The top-level reading follows the same rule
(`_date_target = _target_parsed or parse_iso_date(_target_last_good) or _today`),
and the message in the target row is `st.error("Not a YYYY-MM-DD date;
keeping <last valid date>.")` where it was a caption saying *using
&lt;today&gt;*.

## What the browser showed (port 8523, this worktree)

- Typing `not-a-date` into the Date field: the strip read
  **"Unsaved chart · 1240-05-23 14:30:00 · LMT +00:44:59 · Florence, 16 (IT)
  43.78, 11.25"** -- the committed date, not the draft -- and directly under
  it the warning band **"Results have not updated. Showing the last valid
  chart: 1240-05-23 14:30:00."**, with the sidebar's own "Date must be
  YYYY-MM-DD ... Showing 1240-05-23." beside the field. The wheel below was
  still the last valid chart's.
- Clearing the city: the header bar (Part 1 / Part 2 / Reference) stayed;
  the Chart page showed **"No place is resolved."** over the caption about
  the reference tables; **Reference tables** opened from that state and drew
  Dignities by sign, the Egyptian bounds and the rest in full. Restoring
  `Florence` brought the chart back.
- F02 in passing: searching `New York`, then switching **Enter coordinates
  directly** on, left the fields at **40.7143, -74.0060** -- New York, where
  the old build jumped to Florence.

Nothing was saved from the browser; the owner's `saved_charts.json` was not
touched. `preferences.json` differs from its pre-check hash by
`_launches` alone, 1 -> 2, as any launch increments it.

## What the tests pin

`tests/test_input_state_2026_09_16.py`, 37 tests:

| Reproduction | What is pinned |
|---|---|
| E01 / F01 | the strip's committed date and the warning line; the sidebar error; Save refused and **nothing** written (neither the dict nor a file); an ISO `date_string` in the record; a fresh session loading it computes the date it was saved as; a legacy malformed record loads without crashing |
| E02, E03 / F02 | the toggle keeps New York; the harness's seeded Florence is unchanged; latitude 91 gives one identical sidebar error and a recovery panel under each of the three time standards, with no exception and no table; +-90 still casts; the widgets' own bounds |
| E07 / F05 | empty location, `zzzz-no-such-city`, New York `2025-11-02 01:30` and `2025-03-09 02:30` under Standard time: a header on every page, Reference and Sources drawing the valid run's table count, the recovery panel and no strip on Chart, the DST sentences still in the sidebar, no exception |
| E15 / F17 | an invalid target keeps `1282-05-23` and names it; the read-back line still reads the kept target; today appears nowhere; `_target_last_good` is what it should be, including the session that never had one |
| the dedent | every page function is main's, one guard line apart; the pages are top-level; the navigation is a module-level statement; `tables.json` equals main's |

Three existing tests had an expectation edited, all three for the same
reason -- they pin a slice of `app.py`'s **source text**, and the dedent
moved eight spaces:

- `tests/test_prose_counts.py::test_configurations_chapters_match_the_code`
  (the `_labels` continuation line);
- `tests/test_chart_layout_2026_09_15.py::test_the_layout_is_read_before_the_control_is_drawn`
  (`_layout_control()`'s indentation);
- `tests/test_wheel.py::test_chart_page_names_the_wheel_and_offers_both_layouts`
  (the `wheel_layout` read's continuation line).

No test that pins behaviour changed. The full suite:
**2461 passed, 1 skipped, 6 xfailed**.

## What was not done

The review's other findings in this area are untouched by design: F03 (the
method profile in a saved record), F04 (the saved-chart lifecycle: the
picker built before the save, Modified, New, replace and delete, the
unreadable store) and F18 (the wording of the location and time controls).
F04's "success while the strip still says Unsaved chart" is visible in the
live check above and stays for its own branch.
