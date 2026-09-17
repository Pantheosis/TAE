# UI changes 2026-09-17 — the navigation sections and the Timing split (branch N)

Branch `readability-n-2026-09-17` off `main` at `1b21e2f` (the merge of PR #73,
branch H). Branch N of `UI_READABILITY_PLAN_2026-09-17_rev2.md` §4, with rev 1's
§8 as the design. Three commits: the labels and captions; the split; this note
with the new test file. `engine.py` is byte-identical to `main`. The app's
Streamlit is 1.62.0.

## What was asked

**The bar.** The three `st.navigation` sections renamed from "Part 1: the
nativity", "Part 2: prediction" and "Reference" to "The Nativity",
"Prediction" and "Reference"; bold tried and kept only if it renders in the
top bar; a Material icon per section tried and kept only if the bar reads
better. No CSS on the header, no theme change. The three tests that pin the
old strings changed in the same commit, and the three page texts that echoed
the numbering (the Findings and Timing captions, the Chart page's intro
sentence) reworded.

**The split.** Three of the Timing page's six client-side tabs become pages
under Prediction, in the bar's order Timing, The releaser, Days and months,
Fardar and ages: Timing keeps The Revolution, Indicators of the Year and
Distributions as tabs; The releaser is the Releaser tab's body; Days and
months the Days & Months tab's; Fardar and ages the Fardar, Ages & Reference
Tables tab's. Each new page opens with the `chart_ok` guard and
`_recovery_panel`, its header, the chart strip, its own caption, the sources
scope line, and then the year block, `_year_under_examination()`, lifted out
of `page_timing` with its widget keys unchanged. Text moves; it is not
restructured. Only the sentences named under "Copy" in the brief are
reworded: the two captions, the Chart intro, the Sources page's sentence on
bare locators, the year block's help, and every cross-reference that named
a tab as a chapter or tab.

**The harness.** `PAGES` gains the three pages; `tables.json` regenerated
once, with a multiset proof that nothing was lost, duplicated or re-keyed;
the five-fragment count unchanged and the fragment pins moved; the tests
that rendered `page="timing"` to reach a moved table re-pointed and listed;
`ALLOWED_LONG` re-keyed, not grown; a new test file for the four pages, the
carry of the target across the Nativity pages, and the year block once per
page; the export's Timing headings unchanged; the nothing-lost script's
misses limited to the reworded sentences and classified here.

## What was done

### Commit 1: the labels and the captions

The dictionary keys of `pages` are `"**The Nativity**"`, `"**Prediction**"`
and `"**Reference**"`. `st.navigation`'s docstring says section labels take
GitHub-flavoured Markdown, and the preview on the clone confirmed it in the
top bar: the label renders as a `<strong>` at computed `font-weight: 600`
beside the page entries at 400 (measured by `getComputedStyle` on the bar's
elements), with no stray asterisks. **Bold is kept.** A Material icon per
section (`:material/explore:`, `:material/schedule:`,
`:material/table_chart:`) was tried in the same preview and rendered, but the
section icons duplicated the page icons under them (schedule is Timing's
own, table_chart the Reference tables page's) and made the three group heads
look like three more page buttons; without them the bold label alone marks a
group and the page icons stand in the menu. **Icons are not kept.** At a
phone width and at the 200 % width Streamlit folds the bar into the sidebar,
where the same three bold section labels head the same lists.

The Findings caption loses "Part 1: the nativity. " and the Timing caption
"Part 2: prediction. "; the rest of each stands. The Chart page's third intro
sentence now reads "Enter or load a nativity in the sidebar. The Nativity
sets out what the chart contains, Prediction what the year holds; the
reference tables and the sources close the page list. The judgment is the
astrologer's." Tests: `test_top_navigation_2026_09_15.py:21` and
`test_reference_page.py:12` pin the three bold labels;
`test_chart_layout_2026_09_15.py`'s `INTRO` pins the reworded sentence
verbatim; the Timing caption's `ALLOWED_LONG` entry was re-keyed to its new
first 48 characters (857 characters at that commit, over the ceiling until
the split carried its releaser clause away).

### Commit 2: the split

**The four page functions.** `page_timing` keeps its head and the three
tabs; `_tab_labels` is `("The Revolution", "Indicators of the Year",
"Distributions")`. `page_releaser` (`url_path="releaser"`, title "The
releaser", icon `:material/route:` -- the direction through the bounds),
`page_days` (`days`, "Days and months", `:material/calendar_month:`) and
`page_fardar` (`fardar`, "Fardar and ages", `:material/timeline:` -- the
periods over the life) are the three tab bodies, carved out unchanged with
their fragments, widget keys and expanders and dedented once; nothing in a
tab body depended on a local of another tab (checked by AST before the
carve: every name a later tab loads from an earlier one it also assigns
itself). The two expanders that stood at the foot of the old page, outside
the tabs -- "What Persian Nativities IV does not settle" (`:material/help:`)
and "Sources and editorial notes" -- go to the foot of Fardar and ages, as
rev 1 §8.2's line range puts them (the brief says "at the foot of the Fardar
tab"; in the code they were the page's foot, after the sixth tab, and the
Fardar page is where they now stand). No `st.dataframe` follows the
help-icon expander before the next subheader, so the walker keys nothing
under it.

**The timing wheel** and its View selectbox, Wheel layout radio and Options
popover stand where they stood: inside `_timing_wheel_block()` in The
Revolution tab of the Timing page, as the brief believed. `_timing_wheel_view`
and every preference key are unchanged; nothing new is stored.

**`_year_under_examination()`.** The block from the "The year under
examination" subheader to the read-back line: the mode radio, the age or
date box with its re-seed and `_persist`, the range error, the read-back.
Same widget keys (`target_mode`, `target_age`, `target_date`); rendered at
the head of all four Prediction pages, after `_sources_scope_line()`. Its
help says "Every table on the Prediction pages keys on completed civil
anniversaries" for "on this page". The timing bundle stays computed at the
top level, untouched.

**Two departures from "carved out unchanged", both in the seeding of the
block's widgets.** Both were found by the carry test, one under `AppTest`
and one in the browser on the clone, and both are pinned by tests in commit
3.

1. *A direct hop between two Prediction pages.* Streamlit gives a keyed
   widget a new element id on each page
   (`compute_and_register_element_id` adds the active script hash), and a
   switch from one Prediction page straight to another left the value under
   the old element id, where the new widget could not see it: the age box
   came up 0 and the mode radio "Date", and `_persist` copied those defaults
   into the store. The two `st.session_state.setdefault` calls are replaced
   by `_carry(widget_key, seed)`, which writes the key back to itself (or to
   the seed when it has no value) before the widget is created, and the same
   is done for the mode radio before `_reading_radio`'s own setdefault. The
   write lands in the run's session-state layer, which the new element reads
   first; on a rerun the same page's widget triggers, the key already holds
   the new value and is written back to itself. `persist_state="session"`
   (new in 1.62) was tried first and does not answer: it adopts the carried
   value only at the end of the run, in `_remove_stale_widgets`, after
   `_persist` has already written the default into the store.
2. *A loaded record's target coming back.* On the clone with the owner's
   saved chart, an age set on Timing reverted to the record's age after a
   visit to the Chart page -- on this branch and on `main`. The saved-chart
   loader `_restore_chart` and `_new_chart_form` wrote the widget keys as
   plain session values on a run where the year block is not rendered (the
   app opens on Chart), and Streamlit's state compaction never refreshes a
   plain value under a key that later maps to a widget
   (`SessionState._keys` converts a mapped key to its element id first), so
   the record's value stood in `_old_state` under the bare key and came back
   as the widget's value, through `_reading`'s preference for the widget
   key, whenever the widget went stale on a Nativity page. Both now write
   the store keys only and `pop` the widget keys; `_carry` seeds the widgets
   from the store on the next render. `test_record_lifecycle_2026_09_16`'s
   new-chart test pins `_target_mode == "Date"` and the widget key absent,
   in place of `target_mode == "Date"`. This is a fix of a bug on `main`,
   made here because the brief's own preview check (the age carrying Timing
   -> Chart -> The releaser) fails without it on any session that opened on a
   saved chart.

**Captions.** Timing, Days and months and Fardar and ages open with the
first sentence of the old Timing caption, unchanged: "Every rule on this page
comes from Abu Ma'shar, *On the Revolutions of the Years of Nativities*
(*Persian Nativities* IV), cited as Book.chapter, sentence." The releaser's
caption is the rest of the old caption, split at the clause: "The releaser
and the house-master PN IV leaves to another book of Abu Ma'shar's: ... not
the *Great Introduction*, which has only the Lot of the releaser. They are
taken from Sahl, *On Nativities* (cited on this page by that book's chapter
and sentence). Al-Qabisi's own account ... not built. What neither book
settles is listed at the foot of the Fardar and ages page rather than filled
in." Two phrases changed inside it: "(the chapter named The Releaser, cited
by ...)" is "(cited on this page by ...)", and "at the foot of the page" is
"at the foot of the Fardar and ages page", where the expander now is. No new
sentence was written. The same PN IV sentence on three pages is as true as
it was on one: the Fardar page's triplicity-lords and planetary-years
sections cite Sahl and Abu 'Ali beside PN IV exactly as they did under the
old caption.

**Cross-references, before and after** (the UI half grepped for "chapter",
"tab", "Timing page", "Part 2", the six tab labels, and "above"/"below"
inside the three moved bodies):

| # | Where | Before | After |
|---|---|---|---|
| 1 | Timing, lord of the orb caption | "are method 2 of the Days tab (This week / Today / This hour)." | "are method 2 on the Days and months page (This week / Today / This hour)." |
| 2 | Timing, the governor caption | "(Sahl, On Nativities 1.15, in The releaser chapter) when that finds one, #4" | "(Sahl, On Nativities 1.15, on The releaser page) when that finds one, #4" |
| 3 | Timing, the luminary proxies caption | "(Sahl, On Nativities 1.15, in The releaser chapter) when that finds one, and reads" | "(Sahl, On Nativities 1.15, on The releaser page) when that finds one, and reads" |
| 4 | Timing, VI.2 turning caption | "directed as the planets are in The distribution chapter (" | "directed as the planets are in the Distributions tab (" |
| 5 | Timing, the distribution analysed caption | "reaches an infortune, in The releaser chapter. No worked example" | "reaches an infortune, on The releaser page. No worked example" |
| 6 | Timing, the wheel caption | "(the Lot of Fortune's profection is in the month's indicators below)." | "(the Lot of Fortune's profection is in the month's indicators on the Days and months page)." |
| 7 | The releaser, the stand-in | "The Ascendant's distribution in the tab \"from the Ascendant\" is \"the first of them\" (13)" | "The Ascendant's distribution on the Timing page, \"from the Ascendant\", is \"the first of them\" (13)" |
| 8 | The releaser, the releaser distributed | "as the Ascendant is in the Distributions chapter" | "as the Ascendant is on the Timing page's Distributions tab" |
| 9 | The releaser, the Now line | "the luminary proxies in the Indicators of the year chapter." | "the luminary proxies on the Timing page's Indicators of the Year tab." |
| 10 | Days and months, small days help | "the Ascendant's distribution above runs across the years." | "the Ascendant's distribution on the Timing page runs across the years." |
| 11 | Fardar and ages, the measure caption | "The **Ascendant** and the **meridian** are the distributions above, each applied" | "The **Ascendant** and the **meridian** are the distributions on the Timing page, each applied" |
| 12 | Fardar and ages, Chronocrator Matrix help | "The ascensional method he prefers is the jar bakhtar table above." | "The ascensional method he prefers is the jar bakhtar table on the Timing page." |
| 13 | Fardar and ages, Planetary years help | "the house-master the Timing page names from On Nativities 1.15" | "the house-master The releaser page names from On Nativities 1.15" |
| 14 | Fardar and ages, "does not settle" expander | "The Timing page leaves these items open." | "The Prediction pages leave these items open." |
| 15 | same expander | "per 1.23, 2 (Masha'allah), in the chapter named The releaser, with every reading" | "per 1.23, 2 (Masha'allah), on The releaser page, with every reading" |
| 16 | same expander | "granted from 1.20 in The releaser chapter, placed by the division" | "granted from 1.20 on The releaser page, placed by the division" |
| 17 | Fardar and ages, editorial notes expander | "the house-master's years on the Releaser tab are Sahl's 1.20 in full" | "the house-master's years on The releaser page are Sahl's 1.20 in full" |
| 18 | Sources, how citations are written | "-- and on the Timing page, whose rules all come from that book, its locators are bare" | "-- and on the Prediction pages other than The releaser, whose rules all come from that book, its locators are bare" |
| 19 | Reference, Egyptian bounds help | "The bounds every distribution of Part 2 runs through (III.1, 11)." | "The bounds every distribution on the Prediction pages runs through (III.1, 11)." |
| 20 | Reference, Planetary years help | "is on the Timing page's Releaser tab." | "is on The releaser page." |
| 21 | Reference, The Ages of Man help | "The Timing page marks the native's own age in it." | "The Fardar and ages page marks the native's own age in it." |

Also: `READINGS_REGISTRY` places "Monthly profections turn" on "Days and
months" (its radio stands there), which is what the Sources page's readings
table prints; and the year block's help, "Every table on this page keys on"
-> "Every table on the Prediction pages keys on". Rows 10-12 name no tab or
chapter but said "above" of a table that is now on another page; they were
reworded for that reason and are counted with the cross-references. Row 4
stays a tab reference because both ends are on the Timing page. One
sentence that says "above" of the month's indicators from the nine-methods
caption on Days and months ("the monthly profections above") was already so
on `main` and did not move relative to its neighbour, and stands.

**Harness.** `PAGES = [..., "timing", "releaser", "days", "fardar",
"reference", "sources"]`. The fixture was regenerated once, serially
(`UPDATE_TABLE_FIXTURE=1 python -m pytest tests/test_pages_render.py`,
84 passed). The multiset proof, a scratch script run against
`git show main:tests/fixtures/tables.json`:

```
1240-01-04: main timing 62 tables, 46 distinct keys; branch timing 37 + releaser 10 + days 6 + fardar 9 = 62; equal=True
1240-05-23: main timing 64 tables, 48 distinct keys; branch timing 39 + releaser 10 + days 6 + fardar 9 = 64; equal=True
1240-05-25: main timing 62 tables, 46 distinct keys; branch timing 37 + releaser 10 + days 6 + fardar 9 = 62; equal=True
1240-05-26: main timing 66 tables, 48 distinct keys; branch timing 39 + releaser 12 + days 6 + fardar 9 = 66; equal=True
1240-09-18: main timing 65 tables, 48 distinct keys; branch timing 38 + releaser 12 + days 6 + fardar 9 = 65; equal=True
1240-10-05: main timing 64 tables, 47 distinct keys; branch timing 37 + releaser 12 + days 6 + fardar 9 = 64; equal=True
charts: 6 == branch charts: 6 ALL EQUAL
```

For every chart, `Counter((heading, tuple(columns)))` over the four
Prediction slots on the branch equals the counter over `main`'s `timing`
slot -- nothing lost, nothing duplicated, no heading re-keyed -- and every
other slot (the six Nativity and Reference pages) is byte-equal to `main`'s.
`git diff --stat` on the fixture: 198 insertions, 162 deletions, the old
`timing` slot's entries redistributed over four slots.

**Fragments.** `test_these_five_are_the_only_fragments_in_the_app` stands at
five; `_timing_wheel_block` is still the third child of the Timing page's
first tab at path `(6, 0, 2)`. The two Planetary years tests render
`fardar` and read main's children directly (the table is no longer inside a
tab); the "no table inside the fragment" test's floor is 30 tables on the
Timing page (39 on the default chart) for the old 50 (67); the strips
docstring says three strips on this page.

**Re-pointed tests** (each rendered `page="timing"` to reach something that
moved):

- `test_pages_render.py`: the monthly-turn render test and the reversal
  test render `days` (the radio and the seven indicators of the month are
  there); the section comment says so.
- `test_preferences.py::test_option_values_renamed_by_the_citation_convention_still_load`
  renders `days` for the `pn4_monthly_turn` radio.
- `test_hostile_fixes_2026_09_16.py`: the two M4 day-point tests render
  `days` and hop chart -> days.
- `test_jn_years_additions_2026_09_15.py` and
  `test_years_ladder_2026_09_15.py`: `_timing_text` renders `releaser` (the
  name stays for its callers); the ladder file's tab-label assertion is a
  header assertion.
- `test_labels_nomenclature_2026_09_16.py`: the small-days note and the
  alternate-point control tests render `days`.
- `test_revolution_wheels.py`: the per-view test expects four pictures (the
  wheel and three strips; the releaser's strip is on its own page); the
  six-chapters test is `test_timing_page_has_three_chapters_and_every_table_inside_them`.
- `test_sources_shown_2026_09_16.py`: `SCOPED_PAGES` gains the three pages
  (each tests `READING_DEPTH`), which the one-helper test requires.
- `test_saved_readings_export_2026_09_16.py::test_the_timing_bundles_tables_are_under_the_pages_own_headings`:
  gathers the four Prediction pages' inventories before comparing with the
  export's Timing headings. The brief said this test must pass untouched;
  it renders `page="timing"` and required every exported heading on that
  one page, which the split makes impossible, so the gathering is the one
  change and the assertion is the same. The export's Timing section, its
  name and its headings, is unchanged (`analysis_markdown` reads the
  bundle), and every other test in that file passes untouched.
- `test_record_lifecycle_2026_09_16.py::test_new_chart_clears_the_form_to_the_example_nativity`:
  pins `_target_mode` (departure 2 above).

**`ALLOWED_LONG`.** One entry replaced, the count unchanged at 90: the
Timing caption's key (`'Part 2: prediction. Every rule on this page come'`,
re-keyed in commit 1 to `"Every rule on this page comes from Abu Ma'shar, "`)
is gone, that caption being 155 characters now, and The releaser caption's
key `'The releaser and the house-master PN IV leaves t'` (682 characters)
takes its place. The Findings caption and the year block's help were under
their ceilings before and after. Re-keying, not growth: the same text
stands on the branch under a new first line, and branch C migrates it.

### Commit 3: the new tests and this note

`tests/test_prediction_pages_2026_09_17.py`, twenty tests: (a) the four
pages render without exception at both reading depths, each with its one
header and at least one table; (b) the carry -- an age set through the
Timing page's box survives the Chart page and reaches The releaser with its
read-back line; the same age survives direct hops releaser -> days -> fardar
-> timing with the mode, the box, the store and the read-back checked on
each, and a change on the last page is still a change; a loaded record's
target (the ghost of departure 2, which fails on the old loader with
`43 == 30`) does not come back after the Chart page; a date target set on
Days and months reaches Fardar and ages and Timing through Findings, and
switching the mode there reads the date's completed years into the age box;
(c) the year block's subheader, radio and read-back stand exactly once on
each of the four pages, and on none of Chart, Findings, Reference or Sources.

## Nothing-lost

`python tests/tools/prose_preserved.py main --summary`: 1,262 base
sentences, 114 base locators, **27 misses, 0 locator count drops**, exit 1.
Every miss classified:

*Caption and intro rewordings (6):*
- "Part 1 sets out what the chart contains, Part 2 what the year holds; the reference tables and the sources close the page list." -- the Chart intro sentence, reworded to the section names.
- "Every rule on this page comes from Abu Ma'shar, ... -- except the releaser and the house-master, which PN IV leaves to another book of Abu Ma'shar's: ... his *Book of the Judgments of Nativities* (Bodleian Hunt." -- the old Timing caption's first sentence (the script's sentence rule splits it at "Hunt."), now two sentences on two pages: the PN IV sentence on Timing, Days and months and Fardar and ages, the exception clause opening The releaser's caption.
- "They are taken from Sahl, *On Nativities* (the chapter named The Releaser, cited by that book's chapter and sentence)." -- The releaser caption, "(cited on this page by ...)".
- "What neither book settles is listed at the foot of the page rather than filled in." -- The releaser caption, "at the foot of the Fardar and ages page".
- "Every table on this page keys on completed civil anniversaries (II.3, 1: \"for every year the native has completed\")." -- the year block's help, "on the Prediction pages".
- "Fardar, Ages & Reference Tables" -- the tab label, now the page title "Fardar and ages" (*heading shortened*; "The Releaser" and "Days & Months" are under 25 characters and silent).

*Cross-reference reworded (N) (21):* the twenty-one rows of the table above,
which the script prints as the sentences containing rows 1-21 (row 2 and 3
print as their whole captions; row 4 as the VI.2 caption's opening sentence;
row 6 as the whole wheel caption; row 7 as the stand-in's first sentence;
row 9 as the Now line's fragment after its f-string interpolation).

No `LOCATOR:` line and no `LOCATOR-COUNT:` line: every locator in a moved
caption appears as often as before. Locators that the reworded sentences
carry (IX.8, 123; ITA VIII.1.3; al-Qabisi IV.4-6; 1.15; 1.20; 1.23, 2;
III.1, 11; II.3, 1; IX.7, 7-9; III.2, 110-111) are all still present in the
same sentences.

## What the preview showed

On the clone (`almuten-readability`, port 8530, the owner's charts):

- The bar shows the three bold sections; Prediction opens on Timing, The
  releaser, Days and months, Fardar and ages with their icons.
- Each new page opens on the owner's chart with its header, strip, caption,
  scope line and year block; the Fardar page ends with the two expanders.
- The age set on Timing (30) carries through Chart to The releaser, and
  through direct hops to Days and months and Fardar and ages; on the branch
  before departure 2 it came back as the record's 43 after Chart, which is
  how that bug was found.
- Dark and light themes; the phone preset (the bar folds into the sidebar,
  sections and pages intact); a 700 px viewport standing in for 200 % zoom
  at 1400 px (the same fold; the year block keeps its three columns).
- Reference tables and Sources and readings open; the Sources sentence on
  bare locators reads "on the Prediction pages other than The releaser".
- The one preference toggled on the clone, `_target_mode`, was put back to
  "Date"; the clone's `_launches` count advanced with the reloads, as it
  does on every launch. No other file in `preview_data` changed.
- `N_BAR_2026-09-17.png` on the Desktop: the bar at 1400 px, light theme,
  rendered by headless Firefox through a wrapper page whose load waits for
  the app (the pane's own screenshot captured only part of a wide viewport
  during this session).

## What the tests showed

Full suite with `-n auto`: **3540 passed, 1 skipped, 1 xfailed** (the
allowlist-is-empty test). On `main` after H: 3352 passed; the difference is
the three new page slots in `test_pages_render` and the parametrised tests
that take `PAGES`, the three pages in `SCOPED_PAGES`, and the twenty tests
of the new file. `git diff main -- engine.py` is empty.

For later branches: the handoff's line numbers into `page_timing` are stale
from this branch on; the four page functions are `page_timing`,
`page_releaser`, `page_days` and `page_fardar`, and the year block is
`_year_under_examination()` above them. The two expanders at the foot of
Fardar and ages are where "What Persian Nativities IV does not settle" and
the Sources and editorial notes now live. The repo has no `CLAUDE.md`; the
brief lists one to read.
