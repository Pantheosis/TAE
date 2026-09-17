# UI changes 2026-09-17 — the four Prediction pages and the engine notes (branch C)

Branch `readability-c-2026-09-17` off `main` at `c8245c8` (the merge of PR #76,
branch B). Branch C of `UI_READABILITY_PLAN_2026-09-17_rev2.md` §2, built to
`C_BRIEF_2026-09-17.md`. Seven commits: the engine notes' display (with the
Reference page's seven-place table); one commit per page in the brief's order
(Revolutions, The releaser, Days and months, Fardar and ages); the closing of
the allowlist (with the sidebar's time-standard tooltip and the Chart page's
pick-panel cross-references); this note, and an eighth after the two gates (`C_ADVERSARIAL_REPORT_2026-09-17.md`,
`C_BLIND_TEXT_REPORT_2026-09-17.md`, nothing under Must change; the paragraphs
below read as the branch stands after it). **`engine.py` is byte-identical to
`main`** (`git diff main -- engine.py` and `git diff -w main -- engine.py` are
both empty — see "The engine constants" for why that is stricter than the
brief asked and what was done instead). `tests/fixtures/tables.json` is
byte-identical to `main` (regenerated once with `UPDATE_TABLE_FIXTURE=1`, 85
passed, no diff: no heading and no column changed). Streamlit 1.62.0.

## What was asked

The four Prediction pages migrated onto branch A's contract, one commit per
page: every tooltip a sentence, the visible summary and qualifications the
block's own sentences at reading width, the rest of each caption and tooltip
verbatim under headed sections in a book-icon expander, the comparison tables
the brief names built only from the pages' sentences and listed here per
table, the engine's six note constants shown in paragraphs under headings
the pages place, correction 9b, `ALLOWED_LONG` emptied with the strict xfail
marker removed, and — the coordinator's addition — the sidebar's time-standard
tooltip taken by the same discipline. Nothing added the page did not say; no
locator or quotation outside `app.py`; `analysis_markdown` unchanged; both
nothing-lost runs classified.

## The engine constants (commit 1, `58ca73a`) — a departure from the brief's letter

The brief and plan rule 1.6 asked for blank-line paragraph breaks inside the
six constants (`JN_YEARS_NOTE`, `JN_CH4_ADDITIONS_NOTE`, `SAHL_1_7_UNMODELLED`,
`SAHL_1_7_MODEL_DISCLOSURE`, `SEVEN_PLACE_RANKING_NOTE`,
`PN4_YEAR_INDICATOR_SCOPE_NOTE`) with `git diff -w engine.py` empty. **The two
cannot both be done.** All six are parenthesised runs of adjacent `"..."`
literals. A blank *source* line between two such literals — the one edit
`-w` hides — is whitespace between tokens and puts no newline into the
string's value; a `\n\n` escape inside a literal puts a break into the value
but is two non-whitespace characters, which `-w` shows; converting to a
triple-quoted string changes the quotes. So the paragraph breaks are made in
`app.py` instead, as the handoff's own §5.4 fallback puts it ("build a
separate display representation at the known semantic composition
boundaries"):

- `_paragraphs(text, *leads)` cuts a constant into paragraphs before each
  named lead phrase, in order, and joined back with one space the pieces
  are the constant. `tests/test_readability_c_2026_09_17.py` reads every
  `_paragraphs(CONSTANT, "lead", …)` call in `app.py` by AST and holds each
  to that (the part count, the rejoin, every part starting with its lead, no
  break inside a quotation), and holds `engine.py`'s six constants to
  carrying no newline escape.
- **`PN4_YEAR_INDICATOR_SCOPE_NOTE`** (Revolutions, Indicators of the Year):
  its `st.caption` is the expander "The lord of the year and the
  distributor, ranked by scope" — *Within one year, and across several.*
  (the table below, then the first sentence) · *Sahl's two sentences, as
  printed.* · *The editor's emendation, not adopted.* · *The disagreement,
  recorded and not resolved.* The Sahl quotations stay inline in their
  sentence: the sentence is the engine's and is not reformatted.
- **`JN_YEARS_NOTE`** is `_jn_years_note_sections()` — *When this ladder is
  shown.* · *Steps and impediments.* · *This app's definitions and
  exceptions.* (the four impediment definitions — "peregrine", "burned up",
  the Sun's orientality, "free from the bad ones" — as a list, one line each,
  then the Ch. 4 count sentence) · *Source disagreement.* On The releaser,
  under the ladder (shown when 1.20 is silent under the supplement), the
  first section stands visible at reading width, "Sahl's grade, where he
  gives one, is never overridden by it" in it, and the other three in the
  expander "The ladder's steps, this app's definitions, and the sources"; on
  Fardar and ages all four stand in "Abu 'Ali's ladder, where 1.20 is
  silent" under the Planetary years table, whose own sentence ("The last
  column, beside each "1.20 silent" cell only …") stays a caption. The angle
  brackets are escaped for Markdown as the caption escaped them.
- **`JN_CH4_ADDITIONS_NOTE`** is `_jn_ch4_note_sections()` on the additions
  finding: *What the rows state.* · *Abu Bakr and 'Umar, separate
  witnesses.* · *Grades left unchosen, and Mercury's conjecture.* · *The
  luminaries.* · *Conventions of this display.*, in place of the one section
  "What the rows state, and the conventions of this display." The finding
  takes `detail=` (`_additions_detail`, key
  `additions_and_subtractions_to_the_house_master_s_years_abu_ali_detail`,
  the planets in the table's order, `index=None`, placeholder "Select a
  planet to read its effect, grades, reading and witnesses"), printing the
  row's cells whole under the column headings the table carries: the planet
  and its aspect, **Effect (Ch. 4)**, **Conditional grades** (the three
  grade cells and the Grade cell), **This app's reading**, **Other
  witnesses**. Unresolved Mercury is what the row's Effect says ("not
  decided", "not specified", "unresolved"), distinct from "adds or subtracts
  nothing"; no modifier is synthesised.
- **`SEVEN_PLACE_RANKING_NOTE`** (Reference tables, B's page, the one block
  B left for C): the manuscripts table below, then the two sentences whole.
- **`SAHL_1_7_UNMODELLED` and `SAHL_1_7_MODEL_DISCLOSURE`** take no break: the
  engine composes them into the governor rows' own text (`how` and
  `model_how`, the export's cells), where a paragraph break would enter a
  table cell; the victors page shows them whole as branch A left it, and the
  new test says so.

The four test files that pin the constants (`test_decisions_2026_09_08.py`,
`test_jn_years_additions_2026_09_15.py`, `test_years_ladder_2026_09_15.py`,
`test_doctrine_fixtures.py`) pass unchanged — every phrase they pin lies
inside one sentence and the constants did not change. `analysis_markdown`
for 1240-05-23 and 1240-09-18 in Age and Date mode is byte-identical to
`main`'s but for the export timestamp (a detached worktree at `main` in the
scratchpad, since removed).

**Table "Within one year, and across several" (Scope / The stronger
indicator, and where it is stated)**, two rows, built from the constant's
first and last sentences: "The order above is PN IV's, which ranks the lord
of the year and the distributor BY SCOPE: within the year the lord of the
year is the stronger (II.1, 25; II.23, 1), across several years the
distribution (III.2, 2-3)." · "PN IV's within-the-year ranking agrees with
1.24, 2 and its across-years ranking with 1.23, 33; the disagreement stands
recorded, not resolved." Both stand whole beneath. "BY SCOPE" is the
engine's own capitals and stands.

**Table "The seven praised places' printed order" (Witness / The order's
end)**, three rows, built from: "Printed order (manuscripts H and L: ... 11,
9, 5)." · "Manuscript B reads ... 11, 5, 9; the printed text takes H/L's
order plus B's note that the ninth is the Sun's joy (Introduction Ch. 2, 42,
fn 42) -- Dykes's conflation, kept as printed." Both stand whole beneath.

## Revolutions (commit 2, `e58fae1`)

The page caption is the PN IV sentence shared with Days and months and
Fardar and ages, already one sentence under the ceiling; it is unchanged on
all three. The wheel fragment (`_timing_wheel_block`) and its controls stand
where they stood; the year block is untouched. Twenty-nine `ALLOWED_LONG`
entries deleted. The blocks (tooltip → visible → notes):

- **The revolution of the year.** Tooltip: I.2, 1 and I.2, 4. Visible: "**A
  true-Sun return.** The engine uses a **true**-Sun return; Abu Ma'shar
  computes a mean Sun …" (TRUE to bold). No notes.
- **The charts, drawn** (inside the fragment). Tooltip: the layout sentence
  ("The Wide layout adds a positions column per chart; hover the picture for
  the expand arrows."). The inner-wheel radio's tooltip keeps its two
  sentences on Figure 51 and IX.3, 4-6; its Dykes quotation joins the
  layers section. Caption: the default-points sentence ("Default points are
  Dykes's (p. 12) … the authority the picture is held to."). Expander "How
  the wheel is drawn": *The five views.* (the five view sentences, one per
  line) · *Chart layers.* (the "PN IV's own conventions" sentence, then "The
  inner wheel: Dykes: "Abu Ma'shar seems to prefer …" (p. 12).") · *Points
  shown.* (the Mark / Meaning key below, then the "TP marks …" sentence
  whole) · *Display conventions: whole signs drawn, cusps computed.* (the
  "Two things the text asks for …" sentence).
- **The image of the revolution: its points.** Tooltip: the I.6, 8 count
  clause and I.6, 9-10. Caption: the fixed-stars and Lots sentences.
  Expander "How the image table is built": *What I.6, 3-8 asks for.* (the
  old tooltip's one sentence) · *A table, by the revolution's cusps.* · *The
  twelfth-parts.* The fixed-stars paragraph is as it was but "the app ships"
  → "this app ships".
- **The reading checklist.** Tooltip: I.7, 1's sentence. Visible: "**Facts
  from this app's own evaluators**, run on the revolution's data … (a
  convention, as the image's notes say), and V.1, 2-3's grades for a
  return." Expander "The twenty-six things, and what is not read": *The
  checklist, I.7, 2-26.* (the 2-6, 7-24 and 25-26 sentences as a list) ·
  *Not read, and said so.* (`PN4_I7_NOT_READ` as a list) · *The Lots, the
  principle, and the worked example.*
- **Indicators of the year.** Tooltip: II.1, 5-24's sentence. Visible: "The
  first five are computed here; the rest are delineation material." and
  "**Note the order: within a year** the lord of the year outranks the
  distributor … (the notes under the table)." (WITHIN A YEAR to bold; "the
  caption under the table" → "the notes under the table", where the scope
  note now stands). Then the scope expander of commit 1.
- **The sign of the terminal point (II.3).** Tooltip: II.3, 2's sentence.
  Visible: "**Facts, not a verdict.** II.3, 5-6 name the factors … from this
  app's own evaluators … and Figure 55's cell is not chosen." Expander "How
  the factors are read": *What II.3, 3-18 asks.* · *Row conventions.* (the
  three convention sentences as a list) · *Not built.*
- **Indicators 6-19.** Tooltip: II.1, 11-24's sentence. Visible: "Each reads
  a fact … the judgments are not." and "**Facts, not judgments:** the
  delineation chapters … as natal readings." Expander "Row conventions of
  the fourteen indicators": *What each row reads.* (the seven # sentences
  as a list; "the app's static test" → "this app's static test").
- **The lord of the orb.** Tooltip: VI.1, 4 and 5-8, the sentence truncated
  at its dash. Visible: "Row 5 above is this year's. The table here is VI.1,
  18-19 …"; and, on a chart whose hour lord the Chart page flags as an
  equal-hour approximation (`pn4['hour_approximate']`, the Sun circumpolar),
  "**The natal hour lord is approximate here.** Their sequence from the day
  lord at sunrise … with a flagged equal-hour approximation where the Sun is
  circumpolar; …" — the caption's own sentence, otherwise in the notes only.
  Expander "The cycle of the hour lords, and the three answers to their
  names": *The continuing cycle.* · *The names of the lords: three answers,
  and what is built.* (the Reading / Here table below, then its four source
  sentences whole) · *What PN IV presupposes: the planetary hours.* · *Not
  built, and built elsewhere.*
- **The governor.** Tooltip: "IX.9, 1-9 name eight testimonies and IX.9, 10
  the rule; IX.2, 4 gives a second, sign-level governor for the first
  month." — two clauses of its two sentences. Visible: "**Partial by
  nature, and said so per row.** Testimony #3 and the releaser's half of #4
  need the longevity releaser … (Sahl, On Nativities 1.15, on The releaser
  page) …" The IX.9, 11-13 line has DIVISION and THIS APP'S CONVENTION as
  bold. Expander "How the governor is tallied": *The eight testimonies, and
  the rule.* (IX.9, 10 quoted) · *The meaning of "alone".* (ALONE to bold) ·
  *A reading of "the first lord".* · *The first month's governor (IX.2,
  4).* · *The condition of the primary planet, and what is not built.*
- **The Moon's connections (II.22).** Tooltip: the ephemeris sentence.
  Expander "How the Moon's connections are read": *The sentences of II.22.*
  · *Read into the sentences.* (the four clauses as a list) · *Not counted,
  and not built.* · *Where else this computation is used.* The fractional
  division stands in the page's own markdown as before.
- **The proxies.** Tooltip: II.14, 1, II.22, 1-5 and fn 237. Visible: "**The
  first proxy needs the releaser.** The first proxy in every version is the
  sign the longevity releaser's distribution stands in, which PN IV does not
  supply (IX.8, 123); it is filled from the releaser's distribution …"
  Expander "The proxies, and what each depends on": *II.13, 1, whole.* (a
  blockquote under its locator line) · *The Sun's proxies, as read.* · *The
  Moon's rows.*
- **The turning (VI.2).** Tooltip: "Only the **turning** is built …" (TURNING
  to bold). Visible: "**Two rows for a cusp in another sign.** VI.2, 21-24:
  …" Expander "The turning, the direction, and the twelve Lots": *VI.2, 1,
  whole.* (a blockquote, then "VI.2, 2-17 say what each is turned for.") ·
  *The direction "a year for every degree".* · *Which twelve Lots: not
  stated.* ("the app's Lots" → "this app's Lots") · *A substitution read from
  the editor.* · *The triplicity lords, and what is not built.*
- **The distribution from the Ascendant.** Tooltip: III.1, 12-13 and the
  name sentence III.1, 14 (together under the ceiling). Visible: the
  distributor and partner facts, III.1, 11 and 15-16. The partner-at-birth
  caption (III.1, 23-25; III.2, 103-104) is under the ceiling and stays.
- **The distribution analysed (III.2).** Tooltip: III.2, 4-9's sentence.
  Visible: "**Facts and classification, not judgment:** the conditions
  III.2's delineation turns on … are not judged, and the prose of III.2,
  18-54 is not built." Expander "How the distribution is classified":
  *Method: the checklist, the types, the transitions, the ranking.* ·
  *Classifications, and the three planets of neither nature.* · *The
  transitions, and the transits into the bound.* · *Qualifications on the
  quoted conclusions.* (the death gate) · *No worked example.*
- **The distribution from the Midheaven and the fourth.** Tooltip: III.1,
  12's sentence (296 characters). Visible: "Right ascension has no latitude
  in it …" and "**What PN IV does not supply here, stated rather than filled
  in.**" Expander "Five things the book leaves unsaid of this distribution":
  *No topic from the author.* · *Not among the year's indicators.* · *No
  worked example.* · *The partner at birth, by analogy.* · *"In", read as on
  the axial degree itself.* (ON THE AXIAL DEGREE ITSELF to bold; the two
  sentences that followed it and fn 14's sentence attached) — the five
  inline "(1)…(5)" qualifications, their markers dropped.
- **The planets, each with its measure.** Tooltip: "A planet **on** an axial
  degree is directed as that degree is. Every other planet is the third case,
  whose method PN IV defers to a book it does not reproduce." (ON to bold;
  the second sentence truncated at its colon). Expander "The third case:
  proportional semi-arcs": *III.1, 12, whole.* (a blockquote) · *The three
  positional cases.* (the table below, then the ON sentence) · *The
  formula.* (the whole sentence, then `PromMD - (SigMD / SigSA) * PromSA` on
  a line of its own) · *Definitions.* (DEGREE to bold) · *Sign conventions.*
  · *Not used, and not built.* The per-planet tables and refusals are as
  they were.

**Table "Points shown" (Mark / Meaning)**, ten rows, built from: "TP marks
the terminal point of the year (I.6, 5); the letters under a natal planet
mark I.6, 6's time lords -- D distributor, P partner, F lord of the fardar,
f its divider, O lord of the orb; the solid arc from the natal Ascendant is
the distribution, ending on the degree reached now with its bound tinted
(Figures 2, 65)." (TP, D, P, F, f, O, the solid arc) · "PN IV's own
conventions, read from its figures: … "the profected natal Ascendant ...
which I have shaded in grey" (fn 33) -- the sign of the terminal point of
the year -- with the profection drawn as a dashed arc from the natal
Ascendant (Figures 3, 33); … a ring of the Egyptian bounds on its wheels
(Figures 1, 22, 25, 26; not the simplified Figure 51)." (the dashed arc,
the shaded sign, the ring). The letters are expanded only as the first
sentence defines them; F and f are distinct rows; the test holds the rows
to the badge letters the wheel is drawn with (`_badges`: D, P, F, f, O).

**Table "The names of the lords: three answers, and what is built" (Reading
/ Here)**, four rows, built from: "VI.1, 10 fixes the name to the first
cycle; VI.1, 8's assignment ("the lord of the thirteenth hour from it
belongs to the Ascendant of the root and the thirteenth year") gives a
different planet for the same name from age 12 on; both are shown, neither
is stated for 18-19, and the reset Dykes proposes (Intro Sect. 13, "my
idea") is a third answer, his own." · "Dykes also floats a single-cycle
version in which each house keeps its first hour lord for life (Intro Figure
48), on the thought that the loop is Abu Ma'shar's own error; VI.1, 8
states the loop and the loop is built." · "His twelve-year "reset" of the
named lords is, in his words, his idea, and is not built." · "VI.1, 4: … so
the loop of seven runs on against the cycle of twelve and the pairing
changes every twelve years." All four stand whole beneath the table (the
last in the section above it).

**Table "The three positional cases" (Point directed / Measured in)** is
built from data, not sentences: the `Point directed` and `Measured in`
columns of `PN4_ASCENSION_ROWS`, the same rows the Fardar and ages page
tabulates under "III.1, 12 -- the measure, by position"; the test holds the
rows to the constant.

## The releaser (commit 3, `02ff991`)

Five `ALLOWED_LONG` entries deleted. Branch A's releaser block and additions
finding are as A left them but for commit 1's sections and detail.

- **The opening caption** (682 characters) is its two short sentences: "They
  are taken from Sahl, *On Nativities* (cited on this page by that book's
  chapter and sentence). What neither book settles is listed at the foot of
  the Fardar and ages page rather than filled in." The exception clause —
  "The releaser and the house-master PN IV leaves to another book of Abu
  Ma'shar's: … which has only the Lot of the releaser." — leads A's method
  block at reading width, before "Nawbakht's procedure …"; the al-Qabisi
  sentence ("Al-Qabisi's own account … not built.") joins *Other procedures
  in these texts, not built.* in the years disclosure. No sentence lost.
- **The house-master directed.** Tooltip: "This is the technique that needs
  no grant of years -- Masha'allah's alternative, absent from PN IV and
  present in Sahl." Visible: "**Facts, not judgment:** 1.23, 4's verdict is
  quoted in the notes and not pronounced." ("in the help" → "in the notes");
  the join and the denial as one paragraph at reading width ("**The join,
  and the denial beside it.** … selected by **Nawbakht's** rule … directed
  by **Masha'allah's** operation … Shown as Sahl's, with the denial beside
  it."); "IX.8, 30's turning, the one operation Abu Ma'shar licenses for the
  indicator, follows as PN IV's:" before the turning table; under it the
  planet-turned sentence with its IX.8, 30-31 quotations as body text at
  reading width, and its Read sentence as the caption. Expander "How the
  house-master is directed": *Masha'allah's operation, 1.23, 2-4.* (the
  quotation as a blockquote under "Masha'allah:", its locator after it as
  on main) · *Current direction: the readings.* · *Limitations: two limits
  of the denial.* (ROLE to bold) · *Not applied, and the redirection
  applied.* (APPLIED to bold). The conditional redirection block (1.23,
  13-14) is as it was.
- **The father's Lot.** Tooltip: 32's sentence. Visible at reading width:
  the conditional-method summary (the Lot's degree, the second point, fn 288
  quoted not applied, 31 applied as printed). Expander "The harmers, the
  points directed, and the readings": *Harmers, 4.20, 31.* · *Points
  directed, 4.20, 32.* · *The direction's verdict, and the ranking of two
  infortunes, 4.20, 33-36.* · *Interpretive choices.* (the old caption).

No comparison table on this page beyond A's two.

## Days and months (commit 4, `b53325a`)

Eight `ALLOWED_LONG` entries deleted.

- **The small days.** Tooltip: "A second distribution, running inside the
  year at its own rate; the Ascendant's distribution on the Revolutions page
  runs across the years." Visible: the Method table below. The day-point
  selector's tooltip has A READING as bold. Expander "How the small days are
  read": *The sentences, IX.7, 29-31.* · *Zodiacal, by the sentence.* ·
  *Source and approximation.* · *Read into the sentence.* · *The selector,
  and the worked example.* The table's columns are Method / As applied, and
  its Time origin row carries main's qualifier in the cell ("-- read into
  the sentence rather than stated by it"), since the sentence it is built
  from marks it so (the fix round).
- **The mighty days.** Tooltip: "The profected thirty degrees treated as a
  year, walked degree by degree." Visible: "**Applied rate: 12.175 days per
  degree** -- the author's parenthetical (IX.7, 25); the three figures that
  sentence holds are compared in the notes." (the figure read from
  `PN4_MIGHTY_DAYS_PER_DEGREE`) and the sentence on the thirty degrees
  running into the next sign's bounds. Expander "How the mighty days are
  read, and why this rate": *The sentences, IX.7, 23-28.* · *Why this rate.*
  (the table below, then the IX.7, 25 sentence and the three-figures
  sentence whole, OF A DAY and APPLIED to bold) · *Zodiacal by
  construction.* · *Read into the sentence.* · *The selector, and the worked
  example.*
- **The nine methods.** Tooltip: IX.7, 1 with IX.7, 56 and 79. Visible:
  "**The day.** A "day" is a whole 24-hour period from the birth moment …
  the target date at noon." Expander "The nine methods, one by one, and how
  they are counted": *The nine methods.* (the eight method sentences, one
  per line) · *The hours.* · *Methods 8 and 9.* · *The example's printed
  errors, and what is not built.* (`PN4_IX7_EXAMPLE_ERRATA` as a list).
- **The seven indicators of the month.** Tooltip: IX.1, 35-39's rooted-and-
  fresh sentence. Visible beside the radio: "They decrease in universality
  … months run from the revolution dates, not the calendar." The radio's
  tooltip: Dykes's reading (the default) and a pointer to the notes.
  Expander "The turning rule the radio chooses between": *Abu Ma'shar's
  rule, IX.1, 26-34.* (the section's own locator; BACKWARDS and OWN to bold)
  · *Dykes's reading, the default.*

**Table "Method" (the small days; Method / As applied)**, three rows, built from:
"IX.7, 29: "you look at the degree of the Ascendant of the revolution of the
year, so that you direct from it (for the knowledge of the conditions of the
days), a day for every 59' 08", until it returns to the degree of the
Ascendant at the end of the year."" (Start) · "Zodiacal, by the sentence:
59' 08" a day round the zodiac returns to the degree in 365.28 days, the
year to within an hour." (Rate) · "What is read into the sentence rather
than stated by it: the bodies and rays are the revolution's; the days count
from the moment of the revolution (fn 161 leaves a "day" undefined); …"
(Time origin). All three stand whole in the notes.

**Table "Why this rate" (Reading of IX.7, 25 / A degree is)**, three rows,
built from the one sentence: "Three figures stand in that sentence: the
manuscript's 12;10,30 days (10 minutes and 30 seconds as sexagesimal
fractions OF A DAY, 12.175 d); the author's parenthetical, 12 + 1/6 + 1/120
= 12.175 d, thirty of which are 365 1/4 days exactly (IX.7, 28); and
Dykes's hybrid 12 d 4 h 10 m 30 s (12.17396 d; thirty of them 365 d 5 h 15
m), his "<4 hours>" supplied and the minutes read as clock time -- fn 177
gives 12 d 4 h 12 m for a 365 1/4-day year, which is the author's fraction
again." It stands whole beneath the table.

## Fardar and ages (commit 5, `495f4f8`)

Ten `ALLOWED_LONG` entries deleted.

- **Directing.** The three compact tables stay in their two columns; the
  measure's caption is "The three cases do not stand alike." and the
  ladder's "An idealised year of twelve 30-day months (fn 17)." Expander
  "How a degree is directed, and what it is worth": *By position, III.1,
  12.* (the measure caption's other two sentences) · *By level of chart,
  III.1, 6.* ("PN IV keys the unit to the level of the chart (III.1, 6):" —
  the page's own clause from the scope index — then `PN4_UNIT_ROWS` as a
  list, data not prose) · *The rate ladder, III.1, 13.* (the ladder
  caption's other two sentences).
- **The triplicity lords.** Tooltip: the caption's first sentence (role and
  order). Visible: "**No period is assigned.** No text in hand assigns a
  number of years … A split into three thirty-year stretches, as some
  software prints, is stated nowhere." The checkbox's tooltip keeps its
  first and last sentences (ASCENDANT to bold). Expander "The source
  testimony on the lords over the life": *Sahl, On Nativities 2.11, 1-2 and
  4.* · *2.13, 39 and 2.19, 5.* · *PN IV VI.2, 4.* · *The Ascendant's
  triplicity lords, for comparison.* (the checkbox tooltip's first sentence
  as a copy, so "No text in hand does" has its subject, then its middle
  sentence).
- **The fardar.** Tooltip: its first two sentences. Visible: "**The nodes
  last, in both sects.** IV.7, 24: the Head and Tail come **last in both
  sects** … IV.7, 25: …" The sub-period caption is as it was.
- **When a natal indication comes out.** Tooltip: its first sentence.
  Visible: "**All three grades are shown and none is chosen.**" Expander
  "How the manifestation is read: the grade, the looking, the confirmation":
  *How often, and at what age, III.7, 35-42.* (HOW OFTEN and AT WHAT AGE to
  bold) · *The grade choice.* (SUM to bold) · *Looking.* (IF strong to bold;
  "NOT looking" inside its quotation stands) · *Confirmation.*
- **The Ages of Man.** Tooltip: its first sentence. Caption as it was.
  Expander "How the spans are counted": *The spans, I.8, 9.* · *The Moon's
  4, a witness.*
- **Chronocrator Matrix.** Tooltip: its first sentence ("Two rows: the lord
  of the year …", the phrase `test_prose_counts` pins). Visible: "**An
  approximation, by the author's own grading.** Abu Ma'shar names the
  shortcut himself and grades it: … The ascensional method he prefers is the
  jar bakhtar table on the Revolutions page."
- **Planetary years.** Tooltip: its first sentence (POWER to bold). Visible,
  under the table: "**Applied to one planet only:** the house-master The
  releaser page names …" (under the table, not above it, so
  `test_fragments`' caption-then-table pin holds). Then the ladder caption
  and the JN_YEARS_NOTE expander of commit 1.
- **The scope index.** "What Persian Nativities IV does not settle" keeps
  its label and `:material/help:` icon (a walker heading; no `st.dataframe`
  follows it). Inside, at reading width: the two opening sentences, the
  Topic / State table below, then the six explanations as headed sections
  (`_note_sections`), each paragraph verbatim but for correction 9b. The
  "Sources and editorial notes" expander is four headed sections at reading
  width — *The rate ladder's bottom rung, and the fardar order.* · *One
  printed error is not reproduced.* · *The lord of the year is the lord of
  the sign of the year.* · *Figure 146, On Times 4, 7 and On Nativities
  1.20, 10-17.* — its paragraphs verbatim. The two are the page's last
  elements. The scope index's last heading is "The Indian rule, reported and
  not adopted." (the fix round), its paragraph opening with main's run-in
  lead "The Indian rule for the lord of the year -- …" as before, so the
  phrase does not read twice in a row.

**Copy correction 9b.** "Both are stated in those texts, not built here; the
choice stays Sahl's." reads "Al-Qabisi's choice is stated in that text, not
built here; Abu 'Ali's additions and subtractions are displayed, row by row,
and not applied to Sahl's grant; the choice stays Sahl's." — the additions
are a display-only supplement on The releaser page (`jn_years_additions_rows`
prints them a planet a row; no total is formed), not wholly absent. The old
sentence is nowhere in `app.py` (the test says so).

**Table "Topic / State"**, six rows, one per explanation, each state in the
sentences' own terms and built from the paragraph it indexes: *The releaser
and the house-master* — "Abu Ma'shar says so himself: those "who look into
it are wandering around in the dark; …" (IX.8, 123) -- a book not in hand."
(source silence), "Here the choice is made from **Sahl**, *On Nativities*
1.15 (Nawbakht), and the house-master is directed per 1.23, 2 (Masha'allah),
on The releaser page …" (another source used), the corrected 9b sentence
(al-Qabisi's choice stated and not built; Abu 'Ali's additions displayed,
row by row, and not applied). *Where the greater years are granted* — "*On
Nativities* 1.20, 7-34 is the one natal grant in these texts … PN IV is
silent (IX.8, 123) …". *Directing anything that is not the Ascendant or the
meridian* — "III.1, 12 sends the reader to "what we stated in our book [on
that topic]" for every other point, and PN IV never states it. Dykes's fn 16
identifies the method as Ptolemy's proportional semi-arcs; it is applied
from the texts in hand that state it …". *Revolutions of the day and the
hour* — "Defined in principle (I.3, 10-13) and then declined by the author:
… (IX.7, 79)." ("not implemented" is the state's name for a technique the
author declined and the page does not compute). *The unit of a directed
degree by sign type, strength or planet* — "PN IV keys the unit to the level
of the chart (III.1, 6) and answers a different question …". *The Indian rule
for the lord of the year* — "PN IV reports it without adopting it, so it is
used here only as monthly indicator #2, which is where IX.1, 36 puts it."
Every paragraph stands whole beneath.

**List "By level of chart"** is built from data: `PN4_UNIT_ROWS` ("Root of
the nativity: a degree is years" …), the rows the table beside it shows.

## Closing the allowlist (commit 6, `ffc9072`)

`ALLOWED_LONG` is `()`; `test_the_allowlist_is_empty` passes plainly, its
`xfail(strict=True)` marker removed; `python
tests/test_text_lengths_2026_09_17.py` prints nothing. **The sidebar's
time-standard tooltip** (345 characters, no page's block; the coordinator's
addition to the brief) is one line composed of its three sentences' opening
clauses — "LMT (local mean time) for charts before standard time was adopted
(late 19th century); Standard time: the named zone at the birthplace;
Manual: type the offset the birth record states, east positive." — and the
three sentences whole stand in the sidebar under the resolved offset in a
book-icon expander "The three time standards", one per line (the
4-minutes-a-degree rule, the zone's daylight-saving history, the EST/CDT/IST
examples). **The Chart page's wheel pick panel** (`_pick_panel`, B's "What
remains for C"): "The Reference page carries" → "The Reference tables page
carries" (three sentences) and "The Dignities page carries" → "The Dignities
and places page carries" (two), the pages named as the bar names them.

## Consolidated duplicates

None reduced. Copies made: "Some software divides the life by the lords of
the Ascendant's triplicity." stands in the checkbox's tooltip and, since the
fix round, leads the notes section it is the antecedent of; the
lord-of-the-orb hours sentence ("Their
sequence from the day lord at sunrise …") stands in the notes on every chart
and, on a circumpolar chart, visibly above the table as well; the II.3
scope clause "PN IV keys the unit to the level of the chart (III.1, 6)" leads
the units' chart-level section as well as standing in its own sentence in the
scope index; "A planet on an axial degree is directed as that degree is" is
the tooltip and stands under the positional-cases table; "Dykes rejects the
whole rule …" is the radio's tooltip and a notes section; the monthly-turn
and three-time-standards pointer sentences ("Abu Ma'shar's rule is in the
notes under the table."; "the three figures that sentence holds are compared
in the notes") are boilerplate pointers, the only sentences on the branch
not composed of the pages' words.

## Re-pinned tests (same intent, new strings or places)

- `tests/test_readability_a_2026_09_17.py::test_the_house_masters_years_and_abu_alis_additions_keep_their_flags_and_display_only_status`:
  the additions notes' section "What the rows state, and the conventions of
  this display." is "What the rows state." and "Conventions of this
  display." (two of the five).
- `tests/test_readability_a_2026_09_17.py::test_the_releaser_shows_its_method_and_qualification_then_three_sibling_disclosures`:
  the method block's first paragraph is the caption's exception clause; the
  procedure is `block[1]`, the qualification `block[2]`.
- `tests/test_readability_b_2026_09_17.py::test_the_seven_place_note_is_the_engine_constant_whole`:
  the constant's normalised text in one markdown (under the manuscripts
  table, a paragraph break between its sentences), not the constant as one
  markdown.
- `tests/test_fragments_2026_09_15.py`: `TIMING_FRAGMENT = (6, 0, 3)` (the
  true-Sun qualification stands between the first tab's subheader and its
  table); `test_the_timing_fragment_holds_the_subheader_picture_and_controls_only`
  expects a `Status` ("How the wheel is drawn") after the caption and no
  table inside.
- `tests/test_doctrine_fixtures.py::test_fixed_star_catalogue_found_is_the_one_the_app_ships`:
  "the Swiss Ephemeris star catalogue this app ships".
- `tests/test_labels_nomenclature_2026_09_16.py::test_the_small_days_note_describes_the_control_that_exists`:
  the small days' sentences are read from the expander "How the small days
  are read".
- `tests/test_text_lengths_2026_09_17.py`: `ALLOWED_LONG` from 53 entries to
  none (Revolutions 29, The releaser 5, Days and months 8, Fardar and ages
  10, the sidebar 1); the xfail marker removed; the docstring says so.
- `tests/test_prose_counts.py`: unchanged — it pins "Two rows: the lord of
  the year", which the Chronocrator tooltip keeps, and no ALL CAPS phrase of
  these pages.

New: `tests/test_readability_c_2026_09_17.py` (54 tests): the engine
constants (`test_the_six_note_constants_carry_no_newline_escape` — named
for what it checks since the fix round; the byte-identity proof is this
note's, since a comparison against `main` fails on `main` after the merge; every `_paragraphs` site
rejoins; the two governor constants whole on victors; the scope note's
sections and rows; the seven-place table; the ladder note visible-then-headed
on 1240-02-02 with each impediment a line and the whole note recoverable;
the same sections on Fardar; the additions note's sections and every
planet's detail against its row); Revolutions (every block's tooltip,
visible openings, expander label and section headings; no offender inside
`page_timing`; the legend's letters against the badge letters and the
definition sentence; the positional cases against `PN4_ASCENSION_ROWS` and
the formula line; the approximation line on a 78.2 N chart only; the orb
table's four rows; the refused distribution keeps its notes); The releaser
(the caption's two sentences and the clause's place; the join's bold names;
the turned sentence as body text; the four sections; the father's Lot; no
offender); Days and months (every block; the Method table's rows; the rate
against the constant and the three rows; the nine lines and the errata; the
radio's tooltip and the rule's bold words; no offender); Fardar and ages
(every block; the units' captions and three sections; the scope index's
rows, headings, correction 9b present and the old sentence absent; the
editorial headings; the foot expanders last; no offender); the closing (the
tuple empty, no offender, no xfail; the time-standard tooltip and expander;
the pick panel's five sentences).

## The preview

On the clone (`almuten-readability-2`, port 8531, the owner's chart, the
pane hidden, measured by script), at 1400 × 900 dark and 1920 × 1080 light:
no page scrolls sideways (`scrollWidth == innerWidth` on all four pages at
both sizes); every reading-width paragraph and every two-column table inside
a notes expander is 680 px (the Mark / Meaning key, the Method table, the
Why-this-rate table, the Reading / Here table, the Topic / State index; the
scope table 557 px and the positional cases 490 px, their cells short);
blockquotes render with their left rule in both themes (text rgb(250,250,250)
on rgb(14,17,23); rgb(49,51,63) on white); the formula renders as a code
line; the `<4 hours>` cell renders literally. The Sources shown reading was
switched to the supplement for the additions finding and put back: its
"Read details for" selectbox was driven by keyboard (`input.focus()` from
JS, ArrowDown, Enter) and printed the first planet's four labelled lines at
680 px. The ladder itself is not on the owner's chart (his house-master is
graded by 1.20); it is pinned by the tests on 1240-02-02. The refused case:
the owner's chart moved to 78.2 N in the sidebar showed, on Revolutions, the
refusal warnings, "No current distribution to analyse", the visible
qualifications and the three Distributions expanders, and the
approximation line above the lord-of-the-orb table; the change was a widget
state of that session and did not persist (the next page load was the
saved chart again), and the releaser's refusals are pinned by
`test_readability_c`. The clone's `saved_charts.json` is unchanged (md5
`9538cc78…`); `preferences.json` ends with `_reading_depth: Course text`
and `_target_mode: Date` as found, `_launches` advanced. The viewport was
reset to desktop and the preview stopped.

## Nothing-lost, forward

`python tests/tools/prose_preserved.py main --engine --summary`: 3,626 base
sentences, 193 base locators, **44 misses, 0 locator misses, 0 locator
count drops**, exit 1. Every miss, under one heading; the text of each
stands on the page verbatim but for what the heading names (a second
change in the same sentence is in parentheses).

*ALL CAPS to bold (`test_prose_counts.py` pins none of these phrases;
capitals inside quotation marks stand, as on main)* — 23:
- "The engine uses a TRUE-Sun return; …" (TRUE)
- "Note the order: WITHIN A YEAR the lord of the year outranks the distributor (II.1, 25; II.23, 1)." (WITHIN A YEAR)
- "), as facts -- the conclusions quoted, not pronounced; 13's place half … judged by the Alchabitius DIVISION in the revolution … the unit is THIS APP'S CONVENTION …" (DIVISION, THIS APP'S CONVENTION; the fragment after the f-string's planet name)
- "The tally runs over what is available and names a governor ALONE only when …" (ALONE)
- "Only the TURNING is built: …" (TURNING)
- "A planet ON an axial degree is directed as that degree is." (ON)
- "Here the planet's DEGREE is the significator (…)." (DEGREE)
- "(5) III.1, 12 assigns … "in" is read as ON THE AXIAL DEGREE ITSELF, …" (ON THE AXIAL DEGREE ITSELF; and its "(5)" marker, below)
- "The house-master directed here is selected by NAWBAKHT'S rule (…) and directed by MASHA'ALLAH'S operation (…) …" (NAWBAKHT'S, MASHA'ALLAH'S)
- "Two limits of the denial: IX.8, 32 restricts the ROLE -- …" (ROLE)
- "Not applied: 4.12, 6 (…); … 1.23, 13-14's redirection … is APPLIED below when a 1.23, 12 flag fires; …" (APPLIED)
- "A READING: the "houses" are offered as the revolution's Alchabitius cusps, …" (A READING)
- "Three figures stand in that sentence: the manuscript's 12;10,30 days (10 minutes and 30 seconds as sexagesimal fractions OF A DAY, 12.175 d); …" (OF A DAY)
- "APPLIED: the author's parenthetical, 12.175 d a degree." (APPLIED)
- "IX.1, 26-34: Abu Ma'shar turns the monthly indicators BACKWARDS when the sign is convertible, …" (BACKWARDS)
- "IX.1, 31 applies the test to each indicator's OWN sign, individually." (OWN)
- "Some software divides the life by the lords of the ASCENDANT's triplicity." (ASCENDANT's)
- "IV.7, 24: the Head and Tail come LAST IN BOTH SECTS, …" (LAST IN BOTH SECTS)
- "HOW OFTEN is keyed to the quadruplicity of its natal sign: …" (HOW OFTEN)
- "AT WHAT AGE: "the number of ascensions …" (42)." (AT WHAT AGE)
- "Two things in Dykes's fn 191 are also absent: the SUM of the ascensions and the years, …" (SUM)
- "III.7, 35's "once" is for a fixed-sign planet "NOT looking at the position of the distribution"; … applies "whenever it distributes" IF strong, …" (IF; "NOT looking" is inside its quotation and stands)
- "The lesser, middle, greater and mighty years and the fardar of each planet, … (placed by the division, the POWER unit) …" (POWER)

*"the app" → "this app" (brief 2(e))* — 5:
- "Positions from the Swiss Ephemeris star catalogue the app ships (ephe/sefstars.txt)."
- "II.3, 5-6 name the factors of a suitable and a contrary condition … from the app's own evaluators …" (now "**Facts, not a verdict.** II.3, 5-6 … this app's own evaluators …")
- "Facts from the app's own evaluators, run on the revolution's data as on the root's: … (a convention, as the image's caption says), …" (and "the image's caption says" → "the image's notes say", where the twelfth-part sentence now stands)
- "Nine are lookups on the two charts. #7 is read from … #15 needs the house lords' connections read in the revolution, which the app's static test does not do, …" (this app's; and the three sentences are three list items — the script reads them as one sentence because "#" does not open a sentence)
- "Which "twelve Lots" VI.2, 1 means is not stated; … and the app's Lots are paired to them here, …"

*Cross-reference reworded (N's rule: a page or place named as it now is)* — 7:
- "Facts, not judgment: 1.23, 4's verdict is quoted in the help and not pronounced." → "quoted in the notes", where Masha'allah's sentence now stands
- "Across several years the distribution is the stronger (III.2, 2-3) … (the caption under the table)." → "(the notes under the table)", where the scope note now stands
- "The Reference page carries every sign." → "The Reference tables page carries every sign."
- "The Egyptian bounds, which the Reference page carries in full." → "the Reference tables page"
- "The three faces, which the Reference page carries beside the other dignities." → "the Reference tables page"
- "The Dignities page carries the full lordship table." → "The Dignities and places page"
- "The Dignities page carries them for every planet." → "The Dignities and places page"

*Copy correction 9b* — 1:
- "Both are stated in those texts, not built here; the choice stays Sahl's." → "Al-Qabisi's choice is stated in that text, not built here; Abu 'Ali's additions and subtractions are displayed, row by row, and not applied to Sahl's grant; the choice stays Sahl's."

*Heading shortened, or split from its paragraph* — 2:
- "What the rows state, and the conventions of this display." → the sections "What the rows state." and "Conventions of this display." (three more between them)
- "Where the greater years are granted. *On Nativities* 1.20, 7-34 is the one natal grant in these texts -- …" → the run-in bold lead is its own heading line and the paragraph follows verbatim (the script joined the two because "*On" does not open a sentence)

*Inline list marker "(n)" dropped, the sentence otherwise verbatim under its own heading (brief 2(g))* — 4, and a fifth counted under ALL CAPS:
- "(1) Abu Ma'shar gives this distribution no topic: …" → under "No topic from the author."
- "(2) It is not among the year's indicators: …" → under "Not among the year's indicators."
- "(3) No worked example of a meridian direction exists in PN IV -- …" → under "No worked example."
- "(4) The partner-at-birth rule of III.1, 23-25 is worded for the Ascendant and is carried here by analogy." → under "The partner at birth, by analogy."
- (and "(5) III.1, 12 assigns …", counted under ALL CAPS)

*Inline clauses set as a Markdown list, the sentence otherwise verbatim
(brief 5.2, "perfection/search conditions … as lists"; "row-specific
conventions into a numbered/keyed list")* — 2, and a third counted under
"this app":
- "Read into the sentences: a connection is a perfection by degree, …; the portions go to the planets …; the division is stated for the Moon's year …; "empty in course" is no such perfection before she leaves the sign." → the heading "Read into the sentences." and its four clauses as four list items
- "Facts, not judgments: the delineation chapters behind these rows (…) … as natal readings. #8 grades a transit as V.1, 2-3 does -- … #12 and #13 read both the terminal sign and the revolution's Ascendant, as VI.3-4 do." → the first sentence visible as the qualification, the four # sentences as list items (one sentence to the script, because "#" does not open a sentence)
- (and "Nine are lookups …", counted under "this app")

Nothing else is a miss: no locator token is missing and none lost a copy.

## Nothing-lost, reverse

`python tests/tools/prose_preserved.py readability-c-2026-09-17 --engine
--tree <a detached worktree at main>` from this tree: **156 branch sentences
not on main**, plus five `LOCATOR-COUNT` lines that in this direction say
the branch holds more copies of a token than main (Nativities 1.20 9 → 8,
Nativities 2.1 9 → 8, Nativities 2.11 3 → 2, Ch. 4 43 → 40, Ch. 2 29 → 28:
copies made by section headings, the scope index's rows and the seven-place
table; the forward run reports 0 count drops). Every branch-only sentence
classified:

*Table rows and headers (the comparison tables' and the index's, and the
script's fragments of them)* — 11: the "| Point directed | Measured in |"
header (its rows are the engine's); the Method table; the "Reading of IX.7,
25" table; the "Topic | State" index; the "Reading | Here" table; the "Mark
| Meaning" key; the "Scope" table; the "Witness | The order's end" table and
its three fragments (the script splits at "...", "Ch." and "2, 42").

*List items (the sentences' own words, each line one of main's sentences
or clauses)* — 9: the three time standards; the nine methods; the checklist's
2-6, 7-24 and 25-26; the II.3 row conventions; the fourteen indicators'
conventions; the Moon's four clauses; the Sun's proxies; the Moon's rows;
the five views.

*Section headings, disclosure titles and bold leads* — 91: the twenty-one
expander labels ("How the house-master is directed", "How the small days
are read", "How the mighty days are read, and why this rate", "The nine
methods, one by one, and how they are counted", "The turning rule the
radio chooses between", "How a degree is directed, and what it is worth",
"The source testimony on the lords over the life", "How the manifestation
is read: the grade, the looking, the confirmation", "How the spans are
counted", "How the image table is built", "The twenty-six things, and what
is not read", "The lord of the year and the distributor, ranked by scope",
"Row conventions of the fourteen indicators", "The cycle of the hour lords,
and the three answers to their names", "How the governor is tallied", "How
the Moon's connections are read", "The proxies, and what each depends on",
"The turning, the direction, and the twelve Lots", "How the distribution is
classified", "Five things the book leaves unsaid of this distribution", "The
third case: proportional semi-arcs", "The harmers, the points directed, and
the readings", "The ladder's steps, this app's definitions, and the
sources", "Abu 'Ali's ladder, where 1.20 is silent"); the section headings
listed block by block above; the bold leads of the visible qualifications
("The nodes last, in both sects.", "An approximation, by the author's own
grading.", "The first proxy needs the releaser.", "Two rows for a cusp in
another sign.", "The natal hour lord is approximate here."); the formula
line; one table fragment the script split at "Sect." ("13, "my idea") | Not
built |"); "Abu Ma'shar's rule, IX.1, 26-34." and "The Indian rule, reported
and not adopted." among them since the fix round.

*Placeholders and boilerplate* — 3: "Select a planet to read its effect,
grades, reading and witnesses"; "Abu Ma'shar's rule is in the notes under
the table." (the radio tooltip's pointer); "; if middling in strength:" (the
detail renderer's column labels between the row's cells).

*Composed tooltips (clauses of the old sentences)* — 5: the time-standard
line; "IX.9, 1-9 name eight testimonies and IX.9, 10 the rule; IX.2, 4 gives
a second, sign-level governor for the first month."; "VI.1, 4: … and on
past twelve." (truncated at its dash); "Every other planet is the third
case, whose method PN IV defers to a book it does not reproduce."
(truncated at its colon); "Applied rate: 12.175 days per degree -- the
author's parenthetical (IX.7, 25); the three figures that sentence holds
are compared in the notes." (the label the brief asked for, from "the
parenthetical's 12.175 d a degree is applied", the figure read from the
constant; the script prints it from "days per degree", after the f-string's
number).

*Reworded sentences listed in the forward run (ALL CAPS to bold, "this
app", cross-references, correction 9b)* — 35: each is the branch side of a
forward miss above ("The engine uses a true-Sun return; …", "Facts from this
app's own evaluators …", "Note the order: within a year …", "… (the notes
under the table).", "II.3, 5-6 … this app's own evaluators …", "Only the
turning is built …", "A planet on an axial degree …", "The house-master
directed here is selected by Nawbakht's rule …", "Two limits of the denial:
IX.8, 32 restricts the role …", "Not applied: … is applied below …", "A
reading: the "houses" …", "Some software divides the life by the lords of the
Ascendant's triplicity.", "IV.7, 24: the Head and Tail come last in both
sects, …", "The lesser, middle, greater and mighty years … the power unit
…", "Three figures stand in that sentence: … of a day …", "Applied: the
author's parenthetical, 12.175 d a degree.", "IX.1, 26-34: … backwards …",
"IX.1, 31 applies the test to each indicator's own sign, individually.",
"How often is keyed …", "At what age: …", "Two things in Dykes's fn 191 …
the sum …", "III.7, 35's "once" … if strong …", "), as facts -- … the
Alchabitius division … this app's convention …", "The tally runs over what
is available and names a governor alone …", "Which "twelve Lots" … this
app's Lots …", "III.1, 12 assigns … on the axial degree itself, …", "Here the
planet's degree is the significator …", "Positions from the Swiss Ephemeris
star catalogue this app ships …", "Facts, not judgment: 1.23, 4's verdict is
quoted in the notes …", "Al-Qabisi's choice is stated in that text, not
built here; Abu 'Ali's additions and subtractions are displayed, row by row,
…", "The Reference tables page carries every sign.", "The Egyptian bounds,
which the Reference tables page carries in full.", "The three faces, which
the Reference tables page carries beside the other dignities.", "The
Dignities and places page carries the full lordship table.", "The Dignities
and places page carries them for every planet.").

*A sentence of main's with a label before it* — 2: "The inner wheel: Dykes:
"Abu Ma'shar seems to prefer …" (the radio's name before the quotation, the
sentence verbatim); "PN IV keys the unit to the level of the chart (III.1,
6):" (the scope index's clause, closed with a colon, leading the unit list).

## What remains

- `ALLOWED_LONG` is empty and the guard holds every future help, glance and
  caption to its ceiling with no allowlist; the walker, the nothing-lost
  script and `_paragraphs` are the tooling later branches inherit.
- The engine's six note constants are unchanged; if a later branch wants
  the breaks in `engine.py` itself, the constants would have to become
  triple-quoted strings (a non-whitespace edit), which this branch did not
  make.
- "the app" stands in no page string of the four Prediction pages; the
  triplicity finding's title on Configurations (a fixture key and the
  export's heading) is the one page string that still says it, as B noted.
- The preview clone's launch entries (`almuten-readability`, port 8530, and
  `almuten-readability-2`, 8531), the worktree and `preview_data` are the
  plan's to remove after this branch merges.
