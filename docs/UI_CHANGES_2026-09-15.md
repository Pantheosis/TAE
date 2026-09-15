# UI changes 2026-09-15 — the Findings page, and short headings

Branch `findings-page-2026-09-15` off `main` at `183e0df`. Brief: items 1 and 2 of
`UI_FRAMEWORK_REVIEW_2026-09-15_SECOND_OPINION.md`, §A. One branch, one fixture regeneration,
as that document asks.

## What was asked

**1.** The Chart page had become the longest page at the supplement depth and half of it was
not the chart: six sections of the cast, then eight delineation findings appended in build
order. Split it — the cast stays on Chart, the findings go to a page of their own in Part 1,
between Dignities and places and Configurations, ordered by the source rather than by the
order they were built. Dignities' Mars-by-sect row is a finding too and goes with them.

**2.** Fourteen headings carried "(supplement, display only)" or "(display only)" inside the
h3, and three headings on Configurations ran to a full line with the citation inside them.
Give `_finding()` a `standing=` argument, print it and the citation as one caption under the
heading, and let the heading be the finding's name.

## What was built

**`page_findings()`**, registered as `st.Page(page_findings, url_path="findings",
title="Findings", icon=":material/menu_book:")` between Dignities and places and
Configurations. Eight findings moved off Chart and one off Dignities; each keeps its own
`_finding` call, its `_gap` handling, its `READING_DEPTH` gate and its notes expander
verbatim. `_readings_note()` is at the top, `_absent()` at the foot, and a one-line caption
under the header says what the page is.

The order is by source. The course text first, in the order of the Sahl chapter each cites:
the fetus's stay (*On Nativities* 1.8–1.9), the Moon on the third day (1.29, 11–12; 1.26, 7),
fortune and livelihood (2.1–2.21). Then the supplement, grouped by author in the order the
Sources page names the texts — the places harming the eyesight (Sahl 6.2, then Gr. Intr.
VI.20, then Abu Bakr II.7.3), then Mars in his own domicile by sect (Abu Bakr II.1.0) — and
after them the four texts the Sources page does not name, oldest first: Valens's eleven
phases of the Moon, Mercury's phase against the sect (Firmicus), affliction and fortification
after Rhetorius, Morin's rules for aspects. That tail order is this branch's own choice; the
brief prescribes only the texts the Sources page lists.

**Special Degrees & Conditions** and **Degrees of nobility and rank** stay on Chart: they are
conditions of the cast, not delineation. The Chart page's three introduction sentences name no
page that moved and are untouched.

**`standing=`.** `_finding()` now prints `standing · citation` as the caption under the
heading — "Supplement · display only · Firmicus, Mathesis III.7, 7-9 and 26-30 (Dykes's fnn
186, 194)". Eight `_finding` titles lost their parenthetical suffix (Mercury's phase, Valens's
Moon phases, Morin's aspects, the eyesight places, Rhetorius's affliction, Book V degrees, the
house-master's additions, al-Andarzaghar's triplicity lords); Mars by sect, which is an
`st.subheader` and not a `_finding`, had the same words prefixed to the caption it already
carried. On Configurations, three headings gave up the citation they carried inside them: the
sect light's first triplicity lord by ascensional band, Right-sidedness, the honor-guard. The
honor-guard's "Ptolemy in" moved into its caption with the rest of the locator, so nothing was
dropped. No citation, quotation or note was reworded.

One heading was left as it stands: "Planetary years (Gr. Intr. VII.8, Figure 146) -- display
only" on the Timing page. It is an `st.subheader`, not a `_finding`, and not on Configurations,
so it falls outside both halves of item 2's scope.

## What the tests showed

`tests/conftest.py` gained `"findings"` to `PAGES` in navigation order. Two heading lookups
were repointed and nothing else in the tests changed: `test_prosperity_2026_09_15.py` now
renders the `findings` page to find the seven-classes table, and
`test_jn_years_additions_2026_09_15.py` looks for the shortened title. No assertion, fixture
value or expected row was touched.

`tests/fixtures/tables.json` was regenerated and read line by line. Every date's total table
count is unchanged (116, 112, 117, 119, 115, 118): nothing lost, nothing duplicated. The
changes are three moves per chart from the `chart` slot to the new `findings` slot, three
renames per chart in the `configurations` slot, and one re-attribution on the Chart page —
the sign-categories table sits in an expander that carries an icon, which `AppTest` does not
type as an expander, so the harness gives it the nearest preceding subheader, which used to be
the last finding on the page and is now Quadrant divisions, Special Degrees or Degrees of
nobility, whichever rendered last. That is a heading attribution, not a table change. The
supplement findings do not appear in the fixture at all: it is generated at the default
reading depth.

A note for the next regeneration: `UPDATE_TABLE_FIXTURE=1 ... -n auto` writes a **truncated**
fixture. The writer is a session-scoped fixture, so each xdist worker writes only the slots it
collected and the last one to finish wins — six dates and eight slots came out as two dates
and three slots. Regenerate without `-n`; it takes 36 seconds.

Both reading depths were rendered through `AppTest` for `findings`, `chart` and `dignities`,
with no exception. Under *Course text* the findings page shows the three Sahl findings; under
*Course text and supplement* it shows those three and the five supplement findings that have
rows on the app's default chart, with the eyesight places named in the one-line `_absent()`
caption at the foot.

Full suite: **2172 passed, 6 xfailed in 91.12 s**, with `-n auto` on the owner's venv.
