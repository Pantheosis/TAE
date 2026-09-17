# UI changes 2026-09-17 — the renderer contract and the P1 blocks (branch A)

Branch `readability-a-2026-09-17` off `main` at `49f9a68` (the merge of PR #74,
branch N). Branch A of `UI_READABILITY_PLAN_2026-09-17_rev2.md` §5, built to
`A_BRIEF_2026-09-17.md`. Nine commits: the renderer; one commit per P1 block in
the brief's order (prosperity, Topical Planets in Houses, the releaser, the
syzygy governor and the victor worksheet, Sources, Planetary Condition); the
`PROSE_WIDTH` measurement with the Sources page's two wide tables; this note.
`engine.py` is byte-identical to `main` (`git diff main -- engine.py` is
empty); `tests/fixtures/tables.json` is byte-identical to `main` (regenerated
once with `UPDATE_TABLE_FIXTURE=1`, 85 passed, no diff). Streamlit 1.62.0.

## What was asked

A presentation branch of existing text. Give `_finding` and `_tick_grid` a
structured explanatory contract and add `_prose()`; migrate the six P1 blocks
onto it, moving the existing sentences into a visible summary, visible
qualifications and headed notes, with comparison tables built only from
sentences the page already has and listed here per table; every quotation,
locator, qualification and alternative reading on `main` still reachable;
the engine untouched; `ALLOWED_LONG` losing every entry of a migrated block;
`analysis_markdown` unchanged; the nothing-lost script's misses classified;
`PROSE_WIDTH` settled by measurement on the clone.

## The renderer (commit 1)

`PROSE_WIDTH` (680, see the measurement below) and `_prose()` returning
`st.container(width=PROSE_WIDTH)`. No CSS, no `st.html`, no
`unsafe_allow_html`, no keyed container.

`_finding(...)` keeps every argument, both early returns (`absent=` keeps its
heading and scope caption; an ordinary empty finding joins the bucket),
`column_help=`, `caption=`, `standing=` and `notes=`. Added, all optional, in
this render order: the subheader with `help=glance`; the standing · citation
caption; `summary` (one or two sentences, `st.markdown` inside `_prose()`);
`qualifications` (a list of bold-led statements, each its own paragraph inside
`_prose()`, supplied by the call, never inferred); the table and `caption=` as
before; `detail` + `detail_key` (a `st.selectbox` labelled "Read details for",
listing that field of every row in the table's order, non-unique values
prefixed with their 1-based row number, `key=f"{slug}_detail"` with the slug
derived from the title by `_slug()` exactly as `_tick_grid` derives its grid
key, `index=None`, `placeholder=` the brief's default sentence or the block's
own, the chosen row printed by the callable inside `_prose()`; a value not
among the options renders nothing and raises nothing); the notes expander
under `notes_title` (default "Sources and editorial notes"), always
`icon=NOTES_ICON` (`:material/menu_book:`), holding `notes=` as before and/or
`note_sections=`, an ordered list of `(heading, markdown)` pairs rendered by
`_note_sections()` inside `_prose()`, each heading as `**Heading.**` on its
own line (the run-in convention: every section heading in this branch ends
with a period, so a heading that was a run-in sentence on `main`, "Three
measures, kept apart.", stands verbatim), each body one `st.markdown`.
`_notes_expander(title, sections)` renders a sibling topic expander the same
way for the pages that place one after a finding; never nested.
`_tick_grid` takes `key=` (default the old derivation, so the two grid keys
are unchanged) and `note_sections`. The three-depths comment above `_finding`
describes the layers and names the guard test's ceilings.

The selectbox's label is the widget's own visible label rather than a
collapsed label under a bold line: one element, and the label is the
accessible name the keyboard reader hears. The keyboard path was checked on
the clone (Tab to the box, ArrowDown, Enter).

`tests/test_finding_contract_2026_09_17.py` (eight tests) lifts the helpers'
source out of `app.py` by AST into a minimal script and checks: the layers
render in the contract's order; both early returns; every notes expander
carries the book icon and holds no `st.dataframe` (and, by AST over
`app.py`, no `st.dataframe` stands inside any book-icon expander but the
Chart page's sign-category lookup, which is not a notes expander); the
summary, qualifications and section bodies stand inside a flex container of
`PROSE_WIDTH`; the detail selectbox starts unselected, numbers duplicate
options, renders the chosen row and ignores garbage; `_tick_grid` keeps its
old key without `key=` and takes one with it.

## The six blocks

Common to every block: the visible summary and qualification are sentences
the block already had; every sentence of the old text stands verbatim under
a heading (the exceptions are classified under "Nothing-lost" below);
editorial ALL CAPS became bold or a heading; "the app" became "this app";
quotations of a sentence or more became `> ` blockquotes with the work and
locator on the line above, keeping their quotation marks inside the
blockquote so that each of `main`'s sentences is a substring of one string
constant; inline "(1) … (7)" lists became headed paragraphs or Markdown
lists; the block's `ALLOWED_LONG` entries were deleted in the same commit;
no locator or quotation left `app.py`.

### 2.1 Findings — "Sahl: indications of fortune and livelihood" (commit 2)

Tooltip: the old glance's two short sentences, "Sahl's indications of fortune
and livelihood. Display only; nothing scores it." Summary: the old glance's
long sentence ("The first row is this app's synthesis: the class it reads …
the parallel in the Book of Aristotle or Abu 'Ali."). Qualification:
"**This app's synthesis.** A single seven-class outcome is not specified for
every combination in Sahl's chapter, so the first row is this app's synthesis
and says "read by this app as class N" with its grounds." — the notes'
sentence, moved up. `column_help` on Class unchanged. Detail: the selectbox
lists Class (numbered on the owner's and the fixture charts, where Grade by
ascensions and Falling repeat) and prints Class, Ground, Sahl and Also as
"**Field.** text" paragraphs, verbatim. The finding has no notes expander of
its own; three sibling disclosures follow it, each with the book icon:

- **How the prosperity reading is assembled** — *The two triplicity lords.*
  (the old "The synthesis." paragraph less the moved sentence; 2.11, 1-3,
  2.11, 5 and 2.13, 40 as blockquotes) · *The partnering lord.* (2.11, 4 as a
  blockquote; 2.3, 22 inline as before) · *Three measures, kept apart.* (the
  table below, then the paragraph whole, 2.3, 17-18 and 2.13, 48-51 as
  blockquotes) · *When the Lot is considered.* (the first part of "The Lot
  step.": 2.3, 6 as a blockquote, the either-lord reading, both senses of
  "made unfortunate").
- **How the Lot and the triplicity lords are combined** — *What each source
  judges, and that Sahl gives no precedence.* ("At the Lot, Sahl's sentences
  are judgments of the native …" through "… and says the combination is this
  app's.", verbatim) · *Mixed: one lord strong, the other made unfortunate.*
  (2.11, 2 as a blockquote) · *Agreement, and conflict left unresolved.* (the
  one sentence that treats both, kept whole rather than split at its
  semicolon; the brief's "separate subsections" would have rewritten it) ·
  *The Lot's own sentences met at two levels.*
- **Source passages, alternatives and coverage** — *The seven approaches.*
  (2.1, 2-9 as a blockquote, Dykes's comment) · *2.20, 1-2, as this app reads
  the chain.* (both as blockquotes, the reading under each) · *Routes to
  middling livelihood.* · *Further indications, listed under the synthesis.* ·
  *Passages not evaluated.* (the table below) · *The worked-chart checks.*

**Table "Three measures, kept apart" (Measure / Its part in the reading)**,
built from: "The synthesis reads the whole-sign place from the Ascendant." ·
"Strong is a stake or what follows one, falling the third, sixth, ninth and
twelfth (fn 149 on "strong"), by whole sign." · "2.3, 17-18 -- "…" -- are a
second measure, the sign against the degree, read from the quadrant cusps
when the chart carries them and shown as their own rows ("By sign and by
degree"); they move nothing." · "The fifteen degrees -- "…" -- are a third,
measured from the axial degree by ascensions (fnn 82-83, 222): …; shown as
the grade row when the chart carries its meridian and latitude, and never
folded into strong or weak." All four stand verbatim beneath the table.

**Table "Passages not evaluated" (Passage / Extent not evaluated)**, built
from the one sentence: "Not read: 2.3, 3, 4-5 (except as the grade's footing,
fnn 82-83), 8, 10-11 (except as above), 13-16, 23-24; 2.11, 6-13 and 15-19;
2.13 apart from 39-40 and 48-51; 2.16, 3 except as the grade; 2.17, 6, 9,
12-14 and 2.18; 2.19, 3-4 and 7-9; 2.20, 3-6; 2.2's fixed stars; 2.4-2.10 and
2.12-2.15, which are the chapter's other topics." Twelve rows, every
exception kept; "(except as above)" reads "except as 2.16, 5's motley
mixture", which is what "above" referred to ("2.3, 10-11's further step … is
not computed here except as 2.16, 5's motley mixture", now in the second
disclosure). The sentence itself does not survive (it is the table).

### 2.2 Dignities — Topical Planets in Houses (commit 3)

Tooltip: the old tooltip's first sentence. Caption: the old caption's last
sentence (the third column's sources, the Moon's VII.8 table, every entry's
locator). Visible above the grid, at reading width: "**Natal adaptation.**
The Book II entries adapt PN IV's annual rules … with the qualifications
shown in each entry." (the old caption's first three sentences). The grid
stays selectable; under it the "Read details for" selectbox
(`topical_planets_in_houses_detail`, placeholder "Select a planet to read its
complete entries and sources") prints the planet and its place with the Lean,
the Net and the row's own Standing ("app arithmetic, not a source verdict"),
"**If in a suitable condition (PN IV).**" and "**If in a bad condition (PN
IV).**" whole, and every entry of the Rhetorius/Firmicus list under an
entries heading with the count. A row click writes the same key: a new grid
selection, seen before the selectbox is drawn, becomes its value (the brief
said "through its callback"; a callback would do the same, but AppTest cannot
fire a dataframe callback, and the in-script write is what the test drives —
`_topical_planets_in_houses_last_row` remembers the last grid selection so a
selectbox choice is not overridden by the standing grid state). The full
readings table stays in its expander. The old 4,474-character tooltip's
fifteen sentences stand verbatim in the notes under: *Which sources each
column represents.* · *How conditional entries are included.* · *Misplaced,
missing and supplemented passages.* · *How PN IV is adapted to natal
placements.* · *Why both condition readings remain visible.* (the old notes'
two paragraphs, LEAN to bold). No comparison table. Topical House Lords, The
Moon in the houses and Planetary Dignity Evaluation are untouched (B's).

### 2.3 The releaser (commit 4)

Tooltip: the old tooltip's first sentence. Visible, at reading width, a
method paragraph composed of clauses the block already stated: "Nawbakht's
procedure in Sahl, On Nativities 1.15: by day the Sun, then the meeting, then
the Ascendant; by night the Moon, then the fullness, then the Lot of Fortune,
then the Ascendant." (the old tooltip, verbatim) · "The places: "a stake or
what follows a stake" (1.15, 6-16) is read as a test of the planet's power
and counted by the Alchabitius divisions with the five-degree allowance at
the four axial degrees only" (the readings caption's (1), its opening clause,
THE PLACES in sentence case, the quotation lower-case as Sahl's phrase is
quoted on main) · "the Lot of
Fortune (a candidate by night, 1.15, 14) has no dynamic angularity and is
tested by its whole-sign place" (verbatim) · "the years the house-master
grants are granted from On Nativities 1.20, 7-34 read in full" (the YEARS
sentence's opening clause). Then the qualification "**Readings made here,
each one Sahl leaves open.**", the caption's first sentence. The result block
is as it was but for the house-master's years, whose three sentences are
three paragraphs ("Placed by division N (the **power** unit)."). The Abu 'Ali
additions finding (supplement only) takes the contract: a one-clause tooltip,
the old glance's long sentence as the summary, "**Display only:** no sum is
formed, and Sahl's grant above is not changed." as the qualification, and
four headed sections (Abu 'Ali's chapter whole, the quotations as
blockquotes; `JN_CH4_ADDITIONS_NOTE` whole; Abu Bakr; 'Umar, fn 87 kept
inline in its parenthesis). The 5,479-character readings caption became three
sibling disclosures after the results:

- **Place tests and candidate selection** — *The placement convention.* (the
  table below, then the whole (1) paragraph opening "The places: "a stake or
  what follows a stake" …", THE PLACES in sentence case and POWER and SIGNS to
  bold) · *The order of candidates by sect.* (the table
  below, then the old tooltip's "Each needs its place …" sentence, then (7)'s
  sentences) · *Not applied, and named.* (the `SAHL_RELEASER_NOT_APPLIED`
  clauses as a Markdown list).
- **Lunations, looking, and the house-master** — *The meeting and the
  fullness, and the fullness's degree.* ((5)) · *Looking.* ((2)) · *A
  candidate as its own house-master.* ((3) and the old tooltip's 1.16
  sentence) · *The triplicity lord.* ((4)) · *The lords ranked.* (the old
  tooltip's 1.20, 2-4 sentence) · *"In
  good places" for the Ascendant's lord.* ((6)).
- **Years granted and alternative procedures** — *The natal grant.* (the
  YEARS sentence, YEARS to bold) · *Other procedures in these texts, not
  built.*

**Table "The placement convention" (Point or test / Convention)**, four rows,
built from: ""a stake or what follows a stake" (1.15, 6-16) is read as a test
of the planet's POWER and counted by the Alchabitius divisions with the
five-degree allowance at the four axial degrees only -- …" · "The Lot of
Fortune (a candidate by night, 1.15, 14) has no dynamic angularity and is
tested by its whole-sign place." · "The meeting's and the fullness's degrees
(1.15, 6-8, 12) are neither planet nor Lot: the division is used for them, an
open reading." · ""In good places" for the Ascendant's lord (1.15, 16):
Sahl's seven praised places (…), counted by whole-sign place; no sentence of
Sahl's defines 16's phrase, so the identification is an interpretation …".
The five-degree allowance's direction, unit and extent ("a planet 0-5 degrees
past the Ascendant, Midheaven, setting degree or fourth into the cadent
division keeps the stake's power, measured from the axial degree, in
longitude") stand in the paragraph beneath, as does "here the five degrees
stay at the four stakes and the places are Sahl's".

**Table "The order of candidates by sect" (Sect / Candidates, in order)**,
built from: "Nawbakht's procedure in Sahl, On Nativities 1.15: by day the Sun,
then the meeting, then the Ascendant; by night the Moon, then the fullness,
then the Lot of Fortune, then the Ascendant." and "(7) The day chart consults
the Sun, the meeting, then the Ascendant (1.15, 9: …); the night chart the
Moon, the fullness, the Lot, then the Ascendant (10-14)." The sentence that
follows it — that it shows the order only and every candidate must pass the
tests — is the page's own: "Each needs its place -- by day "…" (6), by night
"…" (11) -- and "the lord of the bound, house, exaltation, triplicity, or
image looking at" it (11); "that one ... which is looking at the releaser,
is the house-master" (13)."

One cross-reference corrected while the sentence moved: "the Chart page's
Planetary years table shows 1.20's grade for every planet" reads "the Fardar
and ages page's Planetary years table …", where that table stands since N.
The year block above the subheader is untouched (`_year_under_examination()`,
`_carry()`, no fragment).

### 2.4 Lunation and victors (commit 5)

Under the syzygy table, visible at reading width: "**The verdict** names a
planet only where the text's clear subcases decide, and otherwise says
"unresolved" with each candidate's profile." The governor expander keeps its
label and its table and carries no icon (it is the table's heading for the
walker; the fixture is unchanged); after the table, four headed sections:
*How the governor is decided.* (the verdict sentence whole, THE VERDICT and
SUN to bold) · *Interpretive choices.* (the table below, then the READINGS
sentence whole, READINGS to the heading, DIVISION and NATAL to bold) · *The
three results compared.* ("The **approximation** row is " +
`SAHL_1_7_MODEL_DISCLOSURE` + "; the almuten row is …" and "Where the three
differ, the difference is the finding.") · *Source passages, and what is not
modelled.* (1.7, 3, 4 and 7 as blockquotes with their locators above, "[Sahl
I p. 265].", "Not modelled: " + `SAHL_1_7_UNMODELLED`). Sahl's governor is
explained by the first section, the other two rows by the third; the results
table itself names all three.

**Table "Interpretive choices" (Choice / Reading made here)**, built from the
one READINGS sentence: ""in a stake" is read by the DIVISION (Alchabitius, the
five degrees at the four axial degrees), the convention Dykes proposes for
strength language (…) -- the text's own word for the stakes is the counted
sign, …; the Moon's side is the same rising-before-the-Sun rule as the
planets', the texts not defining her easternness for this procedure (…); the
target degree is the lunation's and every condition is read in the NATAL
chart, extending the natal context of Dykes's comment to 3-7, whose moment
the text does not state." and, for the Sun's row, from the verdict sentence:
"the SUN is a claim-holder whose side relative to himself is not applicable,
so 3 neither prefers nor sets him aside".

The worksheet: the tooltip is its first sentence; visible at reading width,
the three steps as a numbered list (the old notes' first paragraph, AT THAT
POINT'S and ONCE to bold) and the two-by-two of the four computed
combinations; the two matched grids and the cross-check expander stay as the
detail; the notes are *The weights and the places.* (the old tooltip's
second sentence and "The seven planets are the columns.") · *Two independent
axes.* · *The "Older" attribution.* · *Dykes's critique of the weighting.*
(the old tooltip's third sentence) · *Ibn Ezra's later victor, not
implemented.*

**Table "Dignity weights / Older places / Newer places"** is built from data,
not sentences: each cell is the scheme's own `victor`, `total`, `tied` and
"matched preset" status read off `victors_data`, the scheme names being the
engine's ("Older weights + Older places (matched preset)" …). The wheels are
named as the engine names them (Older/Newer); the notes' sentence says which
is whose ("the Places wheel is ibn Ezra's own or Masha'allah's").

### 2.5 Sources and readings (commit 6)

Order: the caption ("This app <version>. What this app reads from, how it can
be read, and what it does not cover."); Readings in force (tooltip: its first
three sentences; the radio's tooltip: "Sahl's course texts: the tables of
Sahl's Introduction and On Nativities alone. With Abu Ma'shar's supplement:
his tables are laid beside Sahl's on the same topic. Full text under
Configurable readings below." — two clauses of its old sentences and a
pointer in the app's own "Full text on the Sources page" form), the table,
the reset button; "How citations are written" (a subheader; "A locator names
its volume, never the author alone." at reading width; the key as a
three-column Markdown table, Citation form / Work / Example, at the page's
width; then, at reading width,
"Both of Abu Ma'shar's volumes have a Book VII, which is why his name alone
no longer locates anything." and "On the Prediction pages other than The
releaser, whose rules all come from PN IV, its locators are bare
Book.chapter, sentence." — N's clause standing alone, "that book" named);
"Connection rule: Sahl and Abu Ma'shar" (the old opening two sentences at
reading width; the comparison as a three-column table at the page's width;
the scope sentences at reading width, BOTH and SEE to bold; a sibling
expander "The two rules in full, and the alternative reading" with *Sahl's
rule.* and *Abu Ma'shar's rule.* (the two old paragraphs, OWN and IS to bold)
and *Alternative reading: reciprocal light, not implemented.* (the DISSENTING
READING paragraph, its editorial capitals outside the quotation marks to
bold, the capitals inside its three quotations standing as on main, the 5%
sentence in place));
"Configurable readings" as one section per `READINGS_REGISTRY` entry in the
registry's order, at reading width: the reading's own paragraph as the page
carried it (its bold lead with the locator, its source and alternatives,
FEMALE to bold; the parentheticals naming the page a control stands on say
the page's title as the bar shows it, so "Dignities page" is "Dignities and
places page" twice, listed under cross-references below), its "Affects: …"
sentence as its own paragraph, and a
caption "In force: <value> · default: <default> · set on the <page> page"
read from the same `_reading()` the table prints. The connection test and
the monthly turn, for which the page had no paragraph, show their label and
the in-force caption; Sources shown shows the radio tooltip's two old
sentences and the readings-in-force tooltip's sentence on the two stored
names. Widget keys, values and persistence untouched; the one radio is the
one control; the Coverage expander closes the page.

**Table "How citations are written" (Citation form / Work / Example)**, ten
rows, built from: "A locator names its volume, never the author alone: *Sahl,
The Introduction Ch. 3, 85* and *Sahl, On Nativities 1.22, 9*; *Gr. Intr.
VII.6, 27* is Abu Ma'shar's Great Introduction (Dykes); *PN IV IX.1, 26* is
his On the Revolutions of the Years of Nativities, Persian Nativities IV
(Dykes) -- and on the Prediction pages other than The releaser, whose rules
all come from that book, its locators are bare Book.chapter, sentence." ·
"*ITA I.22 (al-Qabisi)* is Dykes's Introductions to Traditional Astrology,
its section and the author excerpted there (al-Qabisi's own numbering,
*al-Qabisi IV.4*, where it is given); *Abu Bakr, On Nativities II.5.14*,
*'Umar al-Tabari, Book of Nativities I.4.3*, *Masha'allah, Book of Aristotle
III.1.8* and *Abu 'Ali al-Khayyat, Judgments of Nativities Ch. 4* are the
four nativity treatises of Persian Nativities I and II (Dykes); *Abbr. II.27*
is Abu Ma'shar's Abbreviation as ITA prints it." Sahl's two rows carry no
"(Dykes)" because the page never said it of them.

**Table "Connection rule" (Question / Sahl, as implemented / Abu Ma'shar, as
implemented)**, three rows, built from: "**Sahl** (The Introduction Ch. 3,
6-21): the applying planet's OWN light governs (15/12/9/8/7 by planet), so
the test is asymmetric." · "A planet at the end of a sign that is not
connecting with anything, whose light strikes into the next sign, IS
connected to the first planet there by body (20-21) -- even though the two
do not see each other." · "**Abu Ma'shar** (Gr. Intr. VII.4-5): two flat
distances instead -- assembly within 15 degrees in one sign (VII.4, 3),
aspects within 12 degrees of exact (VII.5, 27, since aspect rays have no
bodies of their own)." · "No out-of-sign connection at all: across a boundary
the bodies merely 'mix their natures in a weak way' (VII.5, 14)." All four
stand verbatim in the sibling expander.

### 2.6 Configurations — Planetary Condition (commit 7)

The caption's qualification stands above the table at reading width,
":orange[**Net and Verdict are this app's heuristic, not Abu Ma'shar's.**] He
enumerates these conditions; …", verbatim but for correction 9a. A "Read
details for" selectbox (`planetary_condition_detail`, "Select a planet to
read its conditions in words", the planets in the order the table displays
them -- the rows re-ordered by `df_condition`'s index after its sort by Net,
since the contract promises the table's order) prints the planet's four
counts, the Moon
Defects count where the row has one, Net and Verdict on one line, then the
evaluator's own `Positive Labels` and `Negative Labels` arrays as bullet
lists under the table's two label headings (the arrays, never the joined cell
split on commas; no new grouping). Notes: *The two Moon checklists.* · *How
this app's count is formed.* (NET, VERDICT and NOT to bold) · *Enclosure
under this source.* (DISSOLVED and RAYS to bold). The tooltip's "HIS OWN" is
"his own"; `tests/test_prose_counts.py`'s pinned phrase `for the Moon only,
HIS OWN (\w+) corruptions` is `for the Moon only, his own (\w+) corruptions`
in the same commit. No comparison table. Aspects and Reception untouched
(B's).

**Copy correction 9a.** "a Net of zero is Indeterminate on both pages" (the
qualification) reads "a Net of −1, 0 or +1 is Indeterminate on both pages",
and the notes' "a Net of zero is Indeterminate in both places" reads "a Net
of −1, 0 or +1 is Indeterminate in both places": the engine's `abs(net) <= 1`
in `evaluate_abu_mashar_condition` and in `evaluate_planets_in_houses` (the
Dignities Lean), untouched. The Dignities page's own words ("reads
Indeterminate within a margin of one, which is the width of a single
testimony") already agreed.

## Consolidated duplicates

None. No sentence that stood twice on `main` was reduced to one copy; the
one sentence that now stands in two places is a clause reused as a visible
summary beside its whole sentence in the notes (the verdict sentence on the
victors page, and the prosperity qualification moved from the notes to the
visible layer, which is a move, not a copy).

## Re-pinned tests (same intent, new strings or places)

- `tests/test_row_detail_2026_09_15.py::test_the_grid_carries_on_select_and_a_key_from_its_title`:
  the key derivation moved into `_slug()`; the test reads
  `_grid_key = key or _slug(title) + '_grid'` and `_slug`'s body.
- `tests/test_prose_tables.py::test_the_help_and_caption_state_what_the_table_is`:
  the entry counts and the eight phrases are read from the block's notes
  expander (the old tooltip's sentences), the tooltip is its one sentence,
  the adaptation statement is the markdown "**Natal adaptation.** …", the
  caption starts with the third-column sentence.
- `tests/test_prose_tables.py::test_selecting_a_planets_row_prints_every_entry_of_its_list`:
  reads the new panel's lines (placement with Lean, the two PN IV halves, the
  entries heading and the entries), the row read back from the page's own
  grid and readings table; checks the row click set the selectbox's key.
- `tests/test_labels_nomenclature_2026_09_16.py::test_topical_planets_in_houses_is_headed_once`:
  the two paraphrase sentences are read from the notes.
- `tests/test_labels_nomenclature_2026_09_16.py::test_the_condition_caption_says_what_the_dignities_page_does`:
  the qualification is read from the markdown, not a caption.
- `tests/test_doctrine_fixtures.py::test_syzygy_governor_rows_are_on_the_victors_page_with_the_relabelled_almuten`:
  "THE VERDICT names", "the SUN is a claim-holder", "read in the NATAL chart"
  are pinned as "**The verdict** names", "the **Sun** is a claim-holder",
  "read in the **natal** chart".
- `tests/test_sources_shown_2026_09_16.py::test_the_readings_in_force_help_says_what_each_stored_value_means`
  and `::test_the_radio_help_describes_both_states_without_the_word_depth`:
  the two stored names and the two states' descriptions are read from the
  Sources shown section under Configurable readings, the tooltips checked
  for their opening sentences and the pointer.
- `tests/test_prose_counts.py::test_abu_mashar_moon_corruptions_eleven`: the
  phrase `for the Moon only, HIS OWN (\w+) corruptions` is `his own`.
- `tests/test_text_lengths_2026_09_17.py`: `ALLOWED_LONG` from 90 entries to
  78, twelve deleted, one per migrated string (the prosperity glance; the
  planets help and caption; the releaser help, the additions glance and the
  readings caption; the governor caption and the victor help; the Sources
  caption, the readings-in-force help and the Sources shown help; the
  condition caption). `python tests/test_text_lengths_2026_09_17.py` prints
  78 offenders, none in a migrated block; the xfail marker stays.

New tests: `tests/test_finding_contract_2026_09_17.py` (8) and
`tests/test_readability_a_2026_09_17.py` (18): per block, the layers in
order at both reading depths, the sibling disclosures with the icon, the
detail selectbox's options, the chosen row's cells verbatim, garbage
selections; the two planet-selection paths writing one key and every
planet's entries whole with the deferred count; the releaser's method
clauses, both tables' rows, the five-degree allowance's wording, every
reading's sentence, the years' paragraphs, the additions finding's layers;
the governor's un-iconed expander keeping its table's key, its four sections
and table, the constants whole; the worksheet's steps and every two-by-two
cell against the page's own grids; the Sources page's order, the citation
rows and both sentences, the connection table and scope, the alternative
reading's expander, every registry entry's section and in-force caption
against the table with a changed domain reading; the condition
qualification, panel and sections; correction 9a in both places, "a Net of
zero" nowhere, the engine's `abs(net) <= 1` in both evaluators.

## The width measurement

`PROSE_WIDTH = 680`, the owner's ruling on the preview: the app is
desktop-only, never a phone, and 450 px read far too narrow on a normal
screen. Measured on the clone (`almuten-readability-2`, port 8531, the
owner's chart) at a 1400 × 900 viewport, dark theme, the app's font loaded
(`document.fonts.check` true; computed `16px "Source Sans", sans-serif`,
line height 25.6 px): at **680 px** the prosperity summary paragraph's
rendered lines break at 110, 105, 100, 105, 102 characters
(`Range.getBoundingClientRect` per character; 105 on average over its full
lines), and `canvas.measureText` of the paragraph's own first 70 characters
at its computed font gives 112 characters a line (a 74-character reference
sentence gave 107). For the record, the branch first settled 450 px from the
plan's 65–75 target -- the same paragraph broke at 73, 69, 69, 69, 61, 71,
64 characters there (68 on average; the page's average character is 6.27 px,
so 65–75 characters is 408–470 px), and at the phone preset the paragraph
took the page's 343 px with no sideways scroll -- before the owner ruled
for 680. The page does not scroll sideways at 700 px either; tables scroll
inside themselves as before.

Every migrated block was opened on the owner's saved chart in the pane:
Findings (the detail selectbox by keyboard — ArrowDown, Enter — printing the
first row's four cells; the first sibling expander with its table and
blockquotes), Dignities (a row click on Mars writing the selectbox and the
panel; the selectbox alone), The releaser (the method paragraph, the
qualification, the verdict, the three disclosures; the additions finding is
supplement-only and the clone reads Course text), Lunation and victors (the
verdict sentence, the steps, the two-by-two: Mars (38) in all four cells on
the owner's chart), Sources (the four subheaders, the two tables at page
width, nine in-force captions), Configurations (Planetary Condition under
the supplement tab: the qualification with the corrected band, the
selectbox). Absent or bounded findings are covered by the contract test
(both early returns) and by the fixture charts in the block tests. The
clone's `preferences.json` differs from before only in `_launches`;
`saved_charts.json` is unchanged; the viewport was reset to desktop and the
colour scheme to dark.

## Nothing-lost

`python tests/tools/prose_preserved.py main --summary`: 1,263 base
sentences, 114 base locators, **41 misses, 0 locator misses, 0 locator count
drops**, exit 1 (21 + 2 + 8 + 3 + 6 + 2, less the one sentence that is both
a "the app" and a marker case). `analysis_markdown` for the default chart in Age and Date
mode is byte-identical to `main`'s but for the export timestamp (a scratch
worktree at `main`, since removed). Every miss, under its heading; the text
of each stands on the page verbatim but for what the heading names.

*ALL CAPS to bold (test_prose_counts edited for the one phrase it pins);
capitals inside quotation marks stand, as on main* — 21:
- "3, 6-21): the applying planet's OWN light governs …" (OWN)
- "A planet at the end of a sign … IS connected to the first planet there by body (20-21) …" (IS)
- "A DISSENTING READING is recorded in the code but not implemented." (DISSENTING READING)
- "Sahl 13 says that with 15 degrees between THE SUN and a planet … the HEAVIER body there … 'they are connected ONE TO THE OTHER'." (THE SUN, HEAVIER; ONE TO THE OTHER stands inside its quotation; the sentence "Against that, 19 states … ('it already struck WITH ITS OWN LIGHT') … 'the Moon is NOT YET in the power of Saturn's'" has its capitals inside quotations only and is verbatim)
- "This governs only the tables that deliberately present BOTH authors …" (BOTH)
- "Each author's own tables … which author you want to SEE." (SEE)
- "Masha'allah, On Nativities 1.23, 17: … in a FEMALE sign; …" (FEMALE)
- "The Net is shown as a LEAN instead, …" (LEAN)
- "The first five rows score each planet's essential-dignity claim AT THAT POINT'S degree …" (AT THAT POINT'S; now a numbered-list item)
- "Then Lord of the Day (+7), Lord of the Hour (+6) and Places are added ONCE each, …" (ONCE; a list item)
- "TWO INDEPENDENT AXES, and all four combinations are shown." (TWO INDEPENDENT AXES)
- "The YEARS the house-master grants are granted from On Nativities 1.20, 7-34 read in full, above: … the Chart page's Planetary years table …" (YEARS; and the cross-reference below)
- "VII.6, kept in his own four groups: … for the Moon only, HIS OWN eleven corruptions (63-74)." (HIS OWN; the phrase test_prose_counts pins, edited)
- "NET and VERDICT are a convenience of this app and NOT Abu Ma'shar's: …" (NET, VERDICT, NOT)
- "Enclosure here is Abu Ma'shar's own (56-62) … and it can be DISSOLVED: …" (DISSOLVED)
- "The by-sign type counts an encloser's RAYS as well as its body, …" (RAYS)
- "(1) THE PLACES: "a stake or what follows a stake" (1.15, 6-16) is read as a test of the planet's POWER …" (THE PLACES to "The places:", POWER; and the list marker below)
- "These texts' own vocabulary counts SIGNS -- …" (SIGNS)
- "READINGS: "in a stake" is read by the DIVISION (…) … (The Introduction Ch." (READINGS to the heading "Interpretive choices.", DIVISION)
- "VII.2, 4 names her right and left, … every condition is read in the NATAL chart, …" (NATAL)
- "THE VERDICT names a planet only where … the SUN is a claim-holder …" (THE VERDICT, SUN)

*Copy correction 9a* — 2:
- "They are kept beside the Dignities page, … a Net of zero is Indeterminate on both pages." → "a Net of −1, 0 or +1 is Indeterminate on both pages"
- "They are kept because Topical Planets in Houses … a Net of zero is Indeterminate in both places." → "a Net of −1, 0 or +1 is Indeterminate in both places"

*Rebuilt into the table <heading> from <sentence>* — 8:
- "Not read: 2.3, 3, 4-5 (…) … which are the chapter's other topics." → the table "Passages not evaluated" (twelve rows, listed above).
- "How citations are written." → the subheader "How citations are written" (the run-in heading's period dropped).
- "A locator names its volume, never the author alone: *Sahl, The Introduction Ch." · "3, 85* and *Sahl, On Nativities 1.22, 9*; *Gr." · "VII.6, 27* is Abu Ma'shar's Great Introduction (Dykes); *PN IV IX.1, 26* is his … -- and on the Prediction pages other than The releaser, whose rules all come from that book, its locators are bare Book.chapter, sentence." · "Both of Abu Ma'shar's volumes have a Book VII, … *ITA I.22 (al-Qabisi)* is Dykes's Introductions … *Abu 'Ali al-Khayyat, Judgments of Nativities Ch." · "4* are the four nativity treatises of Persian Nativities I and II (Dykes); *Abbr." · "II.27* is Abu Ma'shar's Abbreviation as ITA prints it." → the table "How citations are written" (the six fragments of the two old sentences; "A locator names its volume, never the author alone." and "Both of Abu Ma'shar's volumes have a Book VII, which is why his name alone no longer locates anything." stand verbatim around the table, and the Prediction-pages clause stands as its own sentence with "that book" read as PN IV).

*Cross-reference reworded (N's rule: a page named as the bar names it)* —
2, and a third counted above under ALL CAPS:
- "Domain (hayz) (Dignities page, Sect table) -- Gr." → "(Dignities and places page, Sect table)" (the Sources page's Domain section)
- "Affects: the Sect table and Dignity Evaluation on the Dignities page, and Planetary Condition (13) on the Configurations page." → "on the Dignities and places page" (the same section)
- "the Chart page's Planetary years table shows 1.20's grade for every planet" → "the Fardar and ages page's Planetary years table …", where the table has stood since N; the same sentence carries YEARS to bold (counted there).

*"the app" → "this app" (brief 2(e))* — 3 (two counted once more below):
- "What the app reads from, how it can be read, and what it does not cover."
- "The meeting's gate (1.15, 8) states a place test only; the looking-lord test the app applies to it is supplied from 15's general wording (a reading)."
- "(5) The meeting is the last New Moon … when both or neither is above the earth the app takes the Moon's degree." (also a list marker, below)

*Inline list marker "(n)" dropped, the sentence otherwise verbatim under its
own heading (brief 2(g); the seven readings are distributed over three
disclosures, where the caption's numbering would no longer count)* — 6:
- "(2) "Looking" is the whole-sign aspect, …" → under "Looking."
- "(3) A candidate is not its own house-master except in 1.16's four signs." → under "A candidate as its own house-master."
- "(4) The triplicity lord is the lord of the sect." → under "The triplicity lord."
- "(5) The meeting is the last New Moon and the fullness the last Full Moon before birth; …" → under "The meeting and the fullness, and the fullness's degree." (with "the app" → "this app")
- "(6) "In good places" for the Ascendant's lord (1.15, 16): …" → under ""In good places" for the Ascendant's lord."
- "(7) The day chart consults the Sun, the meeting, then the Ascendant (1.15, 9: …); …" → under "The order of candidates by sect."
- (and "(1) THE PLACES: …", counted under ALL CAPS.)

The last two headings are not among the harness note's six. They name the
two changes the brief itself directs (2(e) and 2(g)) that the script cannot
read as anything but a miss; each sentence is otherwise verbatim on the page
and the blind checker can find it by its text. Nothing else is a miss: no
locator token is missing and none lost a copy.

## What remains for B and C

- `ALLOWED_LONG` holds 78 entries, none in the six blocks. The remaining
  Dignities entries (The Moon in the houses help, Topical House Lords help
  and caption, Planetary Dignity Evaluation caption) are B's; the Prediction
  pages' 40-odd entries and The releaser page's opening caption ("The
  releaser and the house-master PN IV leaves t…") are C's; the Chart, Findings
  (the other findings), Configurations (Aspects, Reception, Strength) and
  Reference entries are B's.
- The contract is in place for them: `summary=`, `qualifications=`,
  `detail=` + `detail_key=`, `note_sections=`, `notes_title=` on `_finding`;
  `key=` and `note_sections=` on `_tick_grid`; `_prose()`, `_note_sections()`,
  `_notes_expander(title, sections)`, `_detail_selector(...)`, `_slug()`,
  `NOTES_ICON`, `NOTES_TITLE`. Section headings end with a period.
- Keep quotation marks inside blockquotes (`> "…"`) and keep a sentence in
  one string constant: the nothing-lost script matches a normalised sentence
  against each constant separately. A locator line before a blockquote keeps
  its colon or dash ("2.11, 4:", "2.11, 1-3 --") so the old fragment
  survives; a closing quotation mark that opened the next constant on `main`
  stays at the head of that constant.
- Three-column Markdown tables are best placed outside `_prose()` at the
  page's width (as the Sources page does); two-column tables read well
  inside.
- A detail selectbox inside a fragment stays inside it (the planets block);
  the pointer path writes the selectbox's key before the selectbox is drawn
  and remembers the last grid selection in a plain session key.
- The reverse check (nothing added) runs with the script's new `--tree`
  argument: `python tests/tools/prose_preserved.py readability-a-2026-09-17
  --tree <a worktree at main>` from this tree lists every sentence the
  branch holds that `main` does not (the headings, the placeholders, the
  in-force caption, the table rows and the reworded sentences above);
  without `--tree` the script reads its own tree on both sides.
- The contract test's synthetic findings cite "Source A, passage n", not a
  locator-shaped placeholder: tooling under `tests/` carries no locator.
- "the app" occurs 31 times in the UI half by N's count (33 on `main`,
  comments included), 16 of them in page strings (19 on `main`), none in
  the six blocks.
- The preview server `almuten-readability` on port 8530 was left running
  for the owner's look; the clone's files are as found but for `_launches`.
