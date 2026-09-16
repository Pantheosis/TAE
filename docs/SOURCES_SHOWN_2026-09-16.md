# Sources shown -- 2026-09-16

Branch `sources-shown-2026-09-16` off `main` at `ad11ed4`. F12 of the
independent UI review of 2026-09-16 (Astra), evidence row E13, under the
owner's ruling. Page text and one widget: `engine.py` is byte-identical to
main and `tests/fixtures/tables.json` does not change.

## The finding and the ruling

The Sources page's two-state control selects between `READING_DEPTH_OPTIONS
= ("Course text", "Course text and supplement")`. Switching it takes the
Findings page from three tables to eight for the baseline chart, adds three
of Abu Ma'shar's topical Lots, adds a reference table, and folds the
Configurations page's Abu Ma'shar tab into the topic blocks, taking that
page from five tabs to four. The review's three points: it selects sources,
it does not deepen a reading; "Course text" presupposes a course the reader
may not have; and the effect was invisible on every page it changed, because
the control is set on a page it does not change.

The owner keeps the two states and keeps the tab fold -- the review's full
split into **Sources shown** and **Explanation detail** is not built -- and
rules three things: rename, display, and a scope line on every page the
setting changes.

**The stored values do not move.** `"Course text"` and `"Course text and
supplement"` are what the harness seeds, what the tests compare, what
`tables.json`'s slots are keyed by and what the readings table prints. The
rename is a rename of the label; the display strings are a `format_func`.

## Every site renamed

| Where | Was | Is |
|---|---|---|
| the radio's label (`page_sources`) | `"Reading depth"` | `"Sources shown"` |
| `READINGS_REGISTRY` entry | `("Reading depth", "reading_depth", ...)` | `("Sources shown", "reading_depth", ...)` |
| the readings table on Sources | row **Reading depth** | row **Sources shown** (its `In force` cell still the stored value) |
| `_readings_note()`'s exclusion | `if l != "Reading depth"` | `if l != "Sources shown"` |
| the radio's `help` | named the two stored values and used "depth" | rewritten, below |
| the "Readings in force" subheader's `help` | -- | gained one sentence saying what each stored value means |
| comment above the page list (app.py head) | "the reading depth on the Sources page" | "the Sources shown reading on the Sources page" |
| comment above `READING_DEPTH` | "The reading depth (...)" | "Which sources are shown (...)", with the format_func noted |
| comment in `page_configurations` | "the reading depth (Sources page) decides" | "the Sources shown reading (Sources page) decides" |

`grep -i "reading depth" app.py` returns nothing: no label, no help, no
caption and no comment carries the old name. The module-level name
`READING_DEPTH` and the store key `_reading_depth` are unchanged -- they are
the engine's own and the preferences file's own, and renaming either would
break a stored preference for no gain the reader can see.

## The display labels

`_reading_radio` gains one keyword, `format_func=None`, passed to `st.radio`
as `format_func=format_func or str` (Streamlit's own default is `str`, so
every other radio behaves exactly as before). Nothing else in the helper
moved. The Sources radio passes its map at the call site, keyed off the
OPTIONS tuple so the values are never typed out:

- `Course text` prints as **Sahl's course texts**
- `Course text and supplement` prints as **With Abu Ma'shar's supplement**

The readings table below the radio still shows the value as stored, which is
what the preferences file holds, and the subheader's help now says what each
stored name means.

## The radio's help, rewritten

> Sahl's course texts: the tables of Sahl's Introduction and On Nativities
> alone, with Abu Ma'shar's Great Introduction VII kept apart in its own tab
> on the Configurations page and behind closed expanders elsewhere. With Abu
> Ma'shar's supplement: his tables are laid beside Sahl's on the same topic
> -- further findings, three more topical Lots, a reference table and the
> supplementary expanders open -- and the Configurations page folds his tab
> into the topic blocks it belongs to.

One sentence per state, no counts that depend on the chart, and not the word
"depth".

## The scope line

One helper, `_sources_scope_line()`, called under each affected page's header
block. It takes no argument and prints nothing page-specific, so the
sentence cannot drift page by page:

- at `Course text`: *Sources shown: Sahl's course texts. Abu Ma'shar's
  supplement is off; switch it on under Sources and readings.*
- at `Course text and supplement`: *Sources shown: Sahl's course texts with
  Abu Ma'shar's supplement.*

**The six pages that carry it** -- every page that tests `READING_DEPTH`:
Findings, Dignities and places, Configurations, Lots, Timing, Reference
tables. On the three with an opening sentence of their own (Findings, Timing,
Reference tables) the line follows that sentence; on the three without
(Dignities, Configurations, Lots) it follows the chart strip directly. On
every one of them it stands above `_readings_note()`.

**The three that do not** -- nothing on them moves when the setting moves:
Chart, Lunation and victors, and Sources and readings itself, which is where
it is set.

## Tests

New: `tests/test_sources_shown_2026_09_16.py`, 42 tests -- the label and the
two stored options on the rendered radio, the two display strings both on the
rendered widget's own `format_func` and by AST on the call that passes it,
`_reading_radio`'s new keyword and its pass-through, the registry line, the
readings table's row and the subheader's help, `_readings_note()`'s exclusion
proved live with another reading off its default, the radio's help against
both states and against the word "depth", the scope line present on each of
the six pages at each state and absent on the three others, its position
after the strip, the one-helper shape, and that "reading depth" appears
nowhere in `app.py` in any case.

Repointed, label only:

- `tests/test_preferences.py::test_sources_lists_the_readings_in_force_and_reset_restores_the_defaults`
  -- `rows["Reading depth"]` -> `rows["Sources shown"]`.
- `tests/test_preferences.py::test_the_reading_depth_is_a_reading_on_the_sources_page`
  -- `find_page_widget(at, "radio", "Reading depth")` -> `"Sources shown"`.

`conftest.SWITCHES` has no entry for this reading, so no switch-matrix test
needed repointing.

Repointed, index only -- the scope line is one more element in the Timing
page's header block, so main's tabs moved from main's sixth child to its
seventh:

- `tests/test_fragments_2026_09_15.py` -- `TIMING_FRAGMENT` `(5, 0, 2)` ->
  `(6, 0, 2)`, and `_node(at, (5, 5))` -> `(6, 5)` in
  `test_the_planetary_years_caption_follows_its_heading`. The paths INSIDE
  the tab are unchanged.
- `tests/test_chart_layout_2026_09_15.py::test_reading_radio_passes_label_visibility_through_and_defaults_to_visible`
  -- it pins the helper's signature line, which now ends
  `label_visibility="visible", format_func=None)`.

The full suite: 2621 passed, 1 skipped, 6 xfailed.

## The live check

Run from this worktree on port 8528 with `XDG_DATA_HOME` pointed at a scratch
copy of the owner's data directory, on the saved chart the preferences file
names (Jason Armfield, 1982-11-19).

**Sources and readings** shows the radio labelled **Sources shown** with the
two options printed **Sahl's course texts** and **With Abu Ma'shar's
supplement**, and the readings table's last row reading `Sources shown |
Course text | Course text | Sources and readings | (blank)`.

At the course-text state, **Findings** carries, in order, the chart strip,
its own "Part 1: the nativity" sentence, then *Sources shown: Sahl's course
texts. Abu Ma'shar's supplement is off; switch it on under Sources and
readings.*, and three source expanders; **Configurations** carries the strip,
the same line, and five tabs ending **Abu Ma'shar (Supplement)**.

Flipped on the radio input itself, the table's row reads `Course text and
supplement | Course text | ... | yes`, **Findings** carries *Sources shown:
Sahl's course texts with Abu Ma'shar's supplement.* and nine source
expanders, and **Configurations** carries the same line and four tabs, the
supplement tab gone into the topic blocks.

The flip wrote the scratch `preferences.json` only. The owner's two files
hash the same before and after:

- `preferences.json` `4070389306f868fe8cabd5c18c9a244b35b8361101d61a99326a748a32bf1519`
- `saved_charts.json` `dd817c155cb23a2cbb1d8b79b1e13d7fc33f798d6bce6c9290d211c924fd921d`

## What is not built

The review's own recommendation was a split into **Sources shown** and
**Explanation detail**, stable navigation across both, and an action on each
page to show the omitted sources. The owner ruled the two-state control and
the tab fold deliberate. No table, tab or evaluator moves on this branch,
and the fixture is untouched.
