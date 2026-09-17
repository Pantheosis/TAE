# UI changes 2026-09-17 — the P2 blocks outside Prediction (branch B)

Branch `readability-b-2026-09-17` off `main` at `dfdf6a9` (the merge of PR #75,
branch A). Branch B of `UI_READABILITY_PLAN_2026-09-17_rev2.md` §2, built to
`B_BRIEF_2026-09-17.md`. Nine commits: one per page in the brief's order
(Findings, Dignities and places, Lots, Configurations, Reference tables,
Chart), the active-readings line, the Chart page's last long block, this
note, and the fix round after the two gates (`B_ADVERSARIAL_REPORT_2026-09-17.md`,
`B_BLIND_TEXT_REPORT_2026-09-17.md`; the paragraphs below read as the
branch stands after it). `engine.py` is byte-identical to `main` (`git diff main -- engine.py`
is empty); `tests/fixtures/tables.json` is byte-identical to `main`
(regenerated once with `UPDATE_TABLE_FIXTURE=1`, 85 passed, no diff: no
heading and no column changed). Streamlit 1.62.0.

## What was asked

The P2 blocks outside the four Prediction pages, migrated onto branch A's
contract (`summary=`, `qualifications=`, `detail=` + `detail_key=`,
`note_sections=`, `notes_title=`; `key=` and `note_sections=` on
`_tick_grid`; `_prose()`, `_notes_expander`, `_detail_selector`), one
commit per page: every sentence shown already on the page; comparison tables
built only from the page's own sentences and listed here per table; headed
notes with descriptive headings ending in a period; ALL CAPS outside
quotations to bold; "the app" to "this app" in every block touched;
quotations as blockquotes under their locator lines; inline lists as
Markdown lists; `ALLOWED_LONG` entries deleted per block; nothing added; no
locator or quotation outside `app.py`; detail selectboxes in the displayed
table's order with `index=None` and a placeholder; the readings note's
count-and-list form in its one slot; the two Dignities cross-references
in the Planetary Condition block; `analysis_markdown` unchanged; both
nothing-lost runs classified.

## What was done, per block

Common to every block: the tooltip is a sentence of the old glance (whole
where it fits, truncated at a colon or semicolon where it does not, in
three places composed of the sentence's own clauses -- said so below);
the old glance's long sentence is the visible summary; the qualifications
are sentences the block already had; every other sentence stands verbatim
under a heading; quotations of a sentence or more are `> ` blockquotes with
the locator line above keeping its colon or dash, and a fragment that
followed a closing mark on `main` stays in the same string constant after
it; the block's `ALLOWED_LONG` entries are deleted in the same commit.

### 2.1 Findings (commit 1, `21d472f`)

- **The fetus's stay (Sahl).** Tooltip: the glance's opening truncated at
  its colon, and "Display only; nothing scores it." Summary: the glance's
  first sentence whole. Qualifications: *Not computed.* (the glance's second
  sentence) and *This app's reading of the year.* (the notes' calendar-
  anniversary sentence, copied; it also stands where it stood after fn 45,
  since on `main` it opens with the closing mark of fn 45's quotation in the
  same constant). Sections, in chapter order: *The meeting before the birth
  and its Ascendant (1.8, 5-6).* · *The three divisions of 1.8, not
  computed.* · *The seven-month native and the four-footed nativities (1.8,
  1).* · *The three Moons of 1.9, 1, and the year.* · *The aspects of 1.9,
  2-10.* · *The conception and the stay by the day and hour, not computed
  (1.9, 11-14).* The conception-unavailable and unspecified-chart limits
  stand in the last two and the second.
- **The Moon on the third day (Sahl).** Tooltip: the glance truncated at
  its colon. Summary: the sentence whole. Qualification: *The third day, this
  app's reading of Firmicus.* -- the notes' "This app takes it two days after
  the birth ..." sentence, copied (it stays in the day-count section, whose
  "his worked chart" needs Firmicus named before it). Sections: *The
  sentences: 1.29, 11-13 and 1.26, 7.* · *The day count.* · *The corruption
  tests.* · *The four-footed signs.* · *Clauses not evaluated: 1.29, 11 and
  12.* The run-in leads "The third day.", "Corrupted." and "Four feet." are
  the headings (each under 25 characters, silent in the nothing-lost run).
- **Places harming the eyesight.** Tooltip: the glance's opening phrase
  and its last sentence. Summary: the first sentence whole. Qualifications:
  *This app's addition, and what is not tested.* (the glance's second
  sentence) and *Method.* -- "Neither table is precessed here: each is
  applied as printed." (copied from the Abu Ma'shar section, where it also
  stands after his 10) and the "Readings, this app's:" sentence on ordinal
  and measured degrees (moved from the notes). Sections, one per source:
  *Sahl, On Nativities 6.2, 48-75: four lists.* · *Abu Ma'shar, Gr. Intr.
  VI.20: the measured places.* · *Two spans read from a phrase, and one bare
  number.* · *Abu Bakr, On Nativities II.7.3: his list, beside the others.*
  Blockquotes: 6.2, 48; 56-57; VI.20, 1-3; VI.20, 10; II.7.3.
- **Mars in his own domicile, by sect (Abu Bakr)** (a subheader, not a
  `_finding`). Tooltip: its first clause and "Display only". The two
  sentences at reading width above the table; the caption unchanged; the
  notes in three sections: *The paragraph whole.* (a blockquote) · *Dykes's
  note on "unsound".* (a blockquote) · *This app's reading.*
- **The Moon's phase, Valens's eleven.** Tooltip: the first sentence
  truncated at its second comma. Summary: the sentence whole. Qualification:
  *Phase boundaries used by this app.* (the glance's second sentence).
  Sections: *Phase boundaries used by this app.* (before the source list,
  as the handoff asks) · *Source phase list.* (a blockquote) · *Phase
  indications.* (Riley's passage as one blockquote, a paragraph per phase) ·
  *Rulers actually named.*
- **Affliction and fortification after Rhetorius.** Tooltip: the first
  sentence truncated after "(Ch. 42's list)". Summary: the glance's two
  sentences. Qualification: *How this app reads each condition.* (the notes'
  paragraph of that name, moved up: degree where a chapter gives one, whole
  sign where it does not, malefics Saturn and Mars). Sections: *The
  conditions tested, each with its reading.* (the existing list, first) ·
  *Rhetorius's chapters, as Holden has them.* (the six chapters as
  blockquotes under bold locator lines, Ch. 27's included; "Holden's notes name them ..." after
  Ch. 28, glued as on `main`) · *The besiegers of an afflicted planet.*
- **Morin's rules for aspects into good and bad houses.** Tooltip: the
  sentence truncated before "read by the kind of ray". Summary: whole.
  Qualification: *The unfortunate houses, this app's reading.* (the notes'
  sentence, copied; the notes' section opens with it because "The equation
  with Morin's phrase" refers back to it). Sections: *The four governing
  sentences, whole.* (the four as blockquotes after the paragraph that
  introduces them) · *The unfortunate houses, this app's reading.* (Dykes's
  fn 43 as a blockquote; "the app's" → "this app's") · *Quoted but not tested,
  and what is not read.*

No comparison table on this page.

### 2.2 Dignities and places (commit 2, `3d91816`)

- **The Moon in the houses — PN IV VII.8, by her transit.** Tooltip
  composed of two of the sentence's clauses: "A natal analogy: VII.8 reads
  the Moon's transit through the houses, and the natal Moon's own whole-sign
  house is marked." Visible at reading width: the tooltip's first sentence
  whole (the natal analogy and "it supplies no condition split" explicit),
  then *The text's own reservation.* and *The translator's readings.* (its
  second and third). The twelve-row table with its natal marker column is
  unchanged; under it a "Read details for" selectbox
  (`the_moon_in_the_houses_pn_iv_vii_8_by_her_transit_detail`, options
  "1st house" … "12th house" in the table's order, the natal Moon's house
  marked "(the natal Moon's)", placeholder "Select a house to read the
  Moon's transit through it in full") prints "**The Moon in the Nth house.**
  reading" and "locator. Natal Moon here: Yes/No." No notes expander: the
  three sentences are all the tooltip had.
- **Topical House Lords (Masha'allah).** Tooltip: the old tooltip's first
  sentence whole (under the ceiling). Visible: "Every cell's wording is this
  app's paraphrase of Sahl's own sentence for that pairing, from his twelve
  lords-of-places passages in On Nativities." (a truncation; the whole
  sentence with the twelve passage references is in the notes), then
  *Masha'allah's condition.* (the caption's opening clause, truncated before
  its quotation) and *This app's implementation.* (the caption's second and
  third sentences whole: the whole-sign test, and "It is met on about one row
  in ten; the readings are shown regardless, with the column saying whether
  he would apply them."). The caption is gone. The structural table is as it
  was; under it a selectbox (`topical_house_lords_masha_allah_detail`,
  options "Lord of the 1st: Saturn, in the 4th place" … in the table's
  order, placeholder "Select a topical house to read its lord's placement and
  Masha'allah's sentence") prints the lord's placement with "Masha'allah's
  condition: met / not met: why" and "Averse to its place: Yes/No" on one
  line, then *Masha'allah's signification.* with his sentence whole. The
  "Masha'allah readings for lord placements" `st.table` stays as the full
  comparison. Notes: *The twelve passages, and the arrangement.* (the
  tooltip's second, third and fourth sentences whole) · *Masha'allah's
  condition, where he states it.* (the caption's first sentence whole, the
  quotation as a blockquote, the eight locators on the line below).
- **Planetary Dignity Evaluation** (inside its expander; no nested
  expander). *This app's ranking convenience.* (the caption's first two
  sentences) before the score table; after it, "**Solar phase** follows Abu
  Ma'shar's walk … (Sahl states no burn boundary, and his Mars westernizes
  at 18°, not 15°):" then the thresholds table at the expander's width with
  the caption "The figures shown are those in force under the current
  readings." (so the in-force figures and the lead's parenthetical do not
  read against each other under the Moon-15 or Mars-18-west reading), then
  "In the heart: within 16' (VII.2, 7-9, from the Sun's own apparent
  diameter). Sahl elsewhere says one whole degree for the heart, …" and the
  **Domain/hayz** paragraph as it was (`DOMAIN_RULE` interpolated, both
  branches verbatim).

**Table "Solar phase thresholds" (Planet / Burned within / Under the rays
within)**, six rows, built from data, not typed: each row is
`SOLAR_BURNED_ORB[planet]` and `solar_rays_orb(planet)` (the engine's own
function, which applies the Moon-15 and Mars-18-west readings, so the table
prints 15° for the Moon and 18° for Mars west when those readings are in
force -- the old caption printed the Moon's figure through `MOON_RAYS_ORB`
and typed the rest); the "In the heart" figure is `round(CAZIMI_ORB * 60)`.
The sentence it replaces, verbatim from `main`: "**Solar phase** follows Abu
Ma'shar's walk through the synodic cycle (VII.2); Sahl's *On Nativities*
1.22 and al-Biruni give the under-the-rays figures independently (Sahl
states no burn boundary, and his Mars westernizes at 18°, not 15°): burned
to 6° for Saturn and Jupiter, 10° for Mars, 7° for Venus and Mercury, 6°
for the Moon; under the rays to 15°, 18° east / 15° west, 12° east / 15°
west, and {MOON_RAYS_ORB:.0f}° for the Moon; in the heart within 16'
(VII.2, 7-9, from the Sun's own apparent diameter)." Its opening clause
stands verbatim before the table and "in the heart within 16' (VII.2, 7-9,
from the Sun's own apparent diameter)" after it, as "In the heart: within
16' (…)". The sentence itself does not survive (it is the table); the
nothing-lost script prints it as two fragments around the interpolation.

### 2.3 Lots (commit 3, `632457e`)

- **Classical Lots.** The notes expander is "Where the four classical Lots
  are stated" (book icon): the key at the expander's width, then *The four,
  in the sources' words.* holding the old paragraph whole (so the key's
  source sentences stand beneath it and the nothing-lost run is silent).
- **Topical Lots.** The tooltip's MORE THAN ONCE is bold.
- **Provenance and standing per Lot.** A selectbox
  (`provenance_and_standing_per_lot_detail`, the forty Lot names in the
  comparison table's order, placeholder "Select a Lot to read its standing,
  source and editor's note") prints "**Topic: Lot.**" then *Standing.*,
  *Source.* and *Editor's note.* as labelled paragraphs from the same
  `provenance_rows`; the "Provenance and standing per Lot" expander with its
  `st.table` stays as the full comparison.
- **The standings note** is "How the standings are recorded": *The Standing
  column.* (its sentence, STANDING bold, and "Every formula is taken from the
  running prose or a footnote, never from one of the summary tables.") ·
  *Four kinds of case.* (a Markdown list, one item per case with its
  existing example: **Sahl himself rules**, **Dykes names his choice**,
  **Dykes marks one standard**, **Dykes only tabulates**) · *The Lot of
  death: a stated rule with a manuscript variant.* (kept separate, STATED
  bold).

**Table "Where the four classical Lots are stated" (Lot / Formula / Stated
where)**, four rows: the Lot and Formula cells are the Classical Lots
table's own (`_classical_lot_rows`, from `LOT_DEFINITIONS`); the Stated
where cells are keyed by Lot name from the paragraph: "Fortune and
Exaltation are stated in Sahl." → "Stated in Sahl" twice; "Spirit -- the
Lot of the Invisible, which Sahl names -- is stated at Gr. Intr. VIII.3,
28-29: by day from the Moon to the Sun, by night the reverse, from the
Ascendant." → "Gr. Intr. VIII.3, 28-29 -- the Lot of the Invisible, which
Sahl names"; "Basis is stated at Gr. Intr. VIII.4, 22-24 as "the Lot of
firmness and survival, the Lot of the Ascendant's support" (fn 67: the Greek
Basis): by day from Fortune to the Invisible, by night the contrary, from
the Ascendant -- the same construction as Sahl's Lot of passion (7.1, 141)
and Abu Ma'shar's Lot of Venus, with which VIII.4, 24 says it coincides." →
"Gr. Intr. VIII.4, 22-24, "the Lot of firmness and survival, the Lot of the
Ascendant's support" (fn 67: the Greek Basis)". The constructions are the
Formula column's; all three sentences stand verbatim beneath the table.
The named-source / unsupported-definition distinction is the table's own
Standing column ("stated (…); named in Sahl", "not in Sahl under this
name"), untouched.

### 2.4 Configurations (commit 4, `d432d39`)

- **Aspects, aversions and connections.** Tooltip: the glance's first
  sentence. Summary: its second (LOOKING bold). Notes: *The columns, and
  what each one measures.* (the key below) · *Motion, orb and bodies.* ·
  *Connection, and where the rules differ.* · *Strength: two measures.* ·
  *Light and heavy: the standing classes.* · *The connecting planet, and
  retrogradation.* -- the old paragraph's sentences whole under those
  headings, MOTION, EXACT ORB DIST, BODIES, CONNECTION, RULES DIFFER,
  STRENGTH, LIGHT, HEAVY and CONNECTING PLANET to bold; the retrogradation
  evidence stays as its three attributed quotations with their locators
  (VII.5, 24; VII.5, 118; the note on VII.5, 130), the capitals inside them
  standing; the "about 4% of configured pairs" measurement stays in the notes.
- **Enclosure.** Tooltip: the one sentence truncated before "-- graded";
  the sentence whole as the summary.
- **Reception.** Tooltip: the first sentence. Summary: both sentences
  (the second's "those" needs the first).
  Qualifications: *Under Sahl's rule.* (the glance's Kind II / Kind IV
  sentence) and *An empty table.* ("An empty table is **not** non-reception
  -- that is a separate set of hostile configurations, in the table below.",
  the notes' last sentence, above the table where its state is read; when
  the finding has no rows it joins the "Not present in this chart" line as
  before, and the Non-reception finding's own glance says it is a distinct
  finding). The notes are a sibling disclosure "Sahl and Abu Ma'shar on
  reception", drawn only when the finding has rows, opening with the
  comparison table at the page's width and then, at reading width: *Sahl's
  reception (Ch. 3, 49-55).* · *Abu Ma'shar's reception (VII.5, 129-133).*
  (REVERSE bold) · *Dignity quality: the local basis.* · *Overall class:
  136-142.* (the one paragraph split at its sentence boundary, SECOND,
  DIGNITY QUALITY, OVERALL CLASS and AND to bold; "both are true, and they
  are different questions" closes the second) · *Sahl's reception at one
  remove (56).* · *Sahl's reception after the sign change (57).* (56 and 57
  as blockquotes; JUST LIKE RECEPTION, OTHER and IT UNDERMINES HER inside
  57's quotation stand).
- **Non-reception.** Tooltip: the first sentence truncated at its
  semicolon. Summary: the sentence whole. Qualification: *Under Sahl's
  rule.* (the glance's second sentence). Notes: *Sahl's A -> B model.* ·
  *The five kinds.* (a Markdown list; OWN bold).
- **Strength of the Planets** and **Weakness of the Planets** (`_tick_grid`,
  `note_sections`): *Testimonies 78 and 83: two measurements.* (LOOK,
  DYNAMIC bold) · *Sahl's five-degree rule.* (FIVE-DEGREE RULE bold, Aphorism
  #44's sentence as a blockquote; the course citation "the course's reading,
  Lesson 3 §4-5, adopted here" exactly as it was) · *Distinct from Planetary
  Condition.*; *The ten, in words.*
- **The sect light's first triplicity lord by ascensional band -- and the
  app's generalisation.** Tooltip: the glance's "Stated for one planet …"
  sentence (ONE bold). Summary: the 2.13, 48-51 sentence, that sentence,
  and the chart's own clause after it, as before. Notes: *This app's
  generalisation, an ordinal preference and no score.* · *Aphorism 45 as
  printed, and the editor's correction.* (its quotation as a blockquote) ·
  *Conventions, this app's.* -- each body opening with the old capitalised
  run-in as bold ("This app's angular-proximity grade, generalised from
  Sahl, On Nativities 2.13, 48-51:", "Aphorism 45 as printed:",
  "Conventions, this app's:"; FOLLOWS bold). The title keeps "the app's": it
  is a fixture key and the export's heading, and the brief prefers no key
  change (listed under "What remains").
- **Right-sidedness** and **The honor-guard.** Tooltips: the one-sentence
  glances truncated at their first semicolon. Summaries: whole. Notes:
  *Readings, this app's.* ("Readings, the app's:" → "Readings, this app's:")
  and, for right-sidedness, *A second definition, and the witnesses.*
- **Natural connections.** Tooltip: the glance's second sentence. Summary:
  both. Notes: *Equal ascensions (56), and equal daylight (67-75).* ·
  *Degrees, and the motion read from both speeds.* · *Affinity (76-77).* ·
  *The same pairs in the Reception table.* (EQUAL ASCENSIONS, EQUAL
  DAYLIGHT, DEGREES, MOTION, AFFINITY bold).
- **Book V degrees.** Tooltip: the first sentence truncated at its colon
  and the second sentence. Summary: the first whole and the second.
  Qualification: *Sahl's own table of the second rule.* (the third
  sentence). Notes: *V.22, 1-2 and 4, the sentences.* (both as blockquotes)
  · *Ordinal degrees, and the degrees in both tables.*
- **Forward-Looking Conditions.** Notes as four sections: *An ordered
  sequence, against the ephemeris.* · *Revoking (117).* · *Resistance
  (118).* · *Escape (119).* (ORDERED SEQUENCE, REVOKING, RESISTANCE, BY
  RETROGRADATION, ESCAPE, SAME bold; BEFORE IT REACHES IT inside 117's
  quotation stands; the horizon still interpolated from the simulation).
- **Banished** (CONNECTIONS bold) and **Rays cast by ascensions** (NEAREST,
  DISTANT bold): the notes otherwise as they were.
- **The fitting infortune.** The checkbox tooltip is its first sentence and
  "Full text on the Sources page." (the app's form for a reading control);
  its second sentence, "When on, that malefic drops out of every 'afflicted
  by an infortune' test in these tables (Sahl's enclosure, strength and
  weakness 94-95; Abu Ma'shar's 3, 47-50 and enclosure; the Moon's 67-68 and
  106).", rides on the in-force line under the checkbox when the reading is
  on and a malefic rules the Ascendant -- where the reading shows, beside
  the tables it changes -- inside the same fixed `st.empty()` slot, and
  stands as well, a copy, as the second paragraph of the reading's entry
  under Configurable readings on the Sources page, where a reader deciding
  whether to switch it on can read it with the reading off.
- **Planetary Condition** (A's block): "the Dignities page" → "the
  Dignities and places page" in the qualification ("They are kept beside
  the Dignities and places page, which prints …") and in the notes ("Topical
  Planets in Houses on the Dignities and places page prints …").

**Table "The columns, and what each one measures" (Column / Meaning)**,
seven rows, two columns at reading width, built from: "MOTION and EXACT
ORB DIST are the degree-to-degree approach." · "BODIES is whether each
planet falls inside the other's sphere of power, which is asymmetric
because the spheres differ in size: Abu Ma'shar VII.4, 7 notes that Saturn
sits inside the Moon's body from 12 degrees while she only enters his at a
little under 9." · "CONNECTION is the active author's verdict, named as his
own text names the state -- switch the Connection rule at the top of this
page to see where they disagree; RULES DIFFER marks the pairs where the two
tests disagree." · "STRENGTH is two different measures. For an assembly it
is the source's own: whose body reaches whose (VII.4, 5-8) and whether they
share a bound. For an aspect it is marked "(app scale)", because VII.5, 4
grades looking as a continuum with no cutoffs anywhere -- … The thirds are
this app's own scanning aid; the measurement itself is the Exact Orb Dist
column." · "LIGHT and HEAVY are the standing classes both authors name as
nouns (Saturn heaviest through the Moon lightest), not a reading of
momentary speed: they are fixed, and a planet slowing toward its station
does not thereby become heavy." · "CONNECTING PLANET is the separate,
directed fact: which one is actually closing the aspect." All stand whole
(bold for the capitals) in the sections beneath the key.

**Table "Sahl and Abu Ma'shar on reception" (Question / Sahl (Ch. 3,
49-55) / Abu Ma'shar (VII.5, 129-133))**, three rows -- Direction,
Dignities that count, Connection required -- at the page's width, built
from: "SAHL (Ch. 3, 49-55) runs one way only -- the connecting planet
stands in a dignity of the planet it connects with, and so is received by
it (52: the Moon in Aries connecting with Mars, "he receives her because
Aries is his house")." · "House or exaltation is perfect reception;
triplicity alone is expressly ranked below it (50); bound counts only
paired with triplicity, which Sahl credits to Masha'allah (54-55)." · "Face
never appears, and a connection is always required." · "ABU MA'SHAR (VII.5,
129-133) is wider on every axis: all five dignities count (129), reception
also runs in REVERSE where the accepting planet sits in the connector's
dignity (130, which exists because Saturn is otherwise too slow to ever be
received), house/exaltation is strongest (131), a lone minor dignity is weak
unless two of bound/triplicity/face combine into a complete reception (132),
and reception can hold by looking with no connection at all (133)." All
four stand whole in the two sections beneath the table.

### 2.5 Reference tables (commit 5, `465d8a7`)

- **Dignities by sign.** The caption is its first sentence (the sources
  and the exaltation scheme); *The triplicity lords.* and *The faces.* hold
  the other two in a notes expander. The tooltip's "the app" is "this app",
  as is the Egyptian bounds tooltip's.
- **Orders of the dignities, and the good places.** `SEVEN_PLACE_RANKING_NOTE`,
  the engine's constant, moves whole and unedited from a caption into a
  notes expander under *The seven praised places' printed order.*
- **Planetary years.** Above the table at reading width: *The middle years,
  this app's convention.* -- "This app keeps 39 1/2, the Arabic Great
  Introduction's, the table it reads for the rest of the row." (the
  caption's sentence, moved). The caption is the source line alone ("Gr.
  Intr. VII.8, Figure 146; the fardar periods PN IV IV.1, 2."). A sibling
  disclosure "Why the middle years differ": *Two constructions of the middle
  years.* (the constructions' sentence, Valens VII.5 as a blockquote, the
  Moon's sentence) · *The witnesses, kept apart.* (the table below, at the
  page's width) · *Four witnesses, and three against.* (the sentence the
  table was built from, whole) · *A variant not adopted.* (Valens's Venus,
  under the source that reports it).
- **Degrees of nobility and rank.** Above the table: *This app's
  ordinal-degree convention.* (the caption's first sentence). Notes: *The
  ordinal span, and the editor's endpoint reading.* (one sentence on `main`,
  which binds the span "18° to 19° for the nineteenth" to Dykes's endpoint,
  so the brief's "ordinal span" and "editor's endpoint reading" share one
  section rather than being split) · *The distinct source lists.*
  (al-Qabisi's third list, then the depth-dependent sentence on Abu Ma'shar's
  column, both branches as they were). The exact boundary convention stands
  verbatim; the caption is gone.

**Table "The witnesses, kept apart" (Construction / The luminaries' middle
years / Witnesses)**, two rows, built from: "The middle years use two
constructions, the ordinary mean for the planets and (least + great/2)/2
for the luminaries, which Valens VII.5 states outright: …" (the two
Construction cells) · "So the luminaries' 39 1/2 has four witnesses in hand
-- Valens VII.5; Gr. Intr. VII.8, 3-8 with Figure 146; Abu Bakr, On
Nativities I.16, the same construction in prose (half the greater years
added to the lesser, the sum halved); PN IV I.8, 12, the Moon's 4 as a tenth
of her middle years -- and three against it that take the ordinary mean,
the Sun 69 1/2 and the Moon 66 1/2: Masha'allah, Book of Aristotle III.1.8;
Abu 'Ali al-Khayyat, Judgments of Nativities Ch. 4; and the Latin Great
Introduction's table of the years as Dykes prints it (ITA VII.2, Figure
108)." (the value and witness cells of both rows, each witness under its own
construction and no consensus drawn). Both sentences stand whole beside the
table.

### 2.6 Chart (commits 6 and 8, `913809e`, `bbe7bb0`)

- **The introduction.** The four About sentences render as `st.markdown`
  inside one `_prose()` container (680 px, body size) instead of four
  captions, open for the first two launches and inside "About this app"
  after that as before; the text is unchanged. Main's direct children before
  the wheel fragment are what they were; after it the four caption slots are
  one container, so Calculation is main's sixth child (was ninth).
- **The circumpolar hour notice.** One caption under the ceiling: "⚠️ **The
  Lord of the Hour here is not a temporal hour.** What is shown is an
  explicitly modern approximation: the civil day divided into 24 equal
  hours, continuing the same Chaldean cycle. The Lord of the Day is still
  exact." Its reason -- "No sunrise or sunset exists for this date at this
  location (circumpolar day or night), and the temporal hour is *defined* by
  the interval between them — so it has no value at all, and no source in
  hand contemplates the case." -- stands whole in a notes expander "Why the
  hour lord is approximate here" under *No temporal hour exists for this
  date at this location.*, drawn only on such a chart, directly under the
  caption.
- **Mars under the rays to 18° west.** The checkbox tooltip (422
  characters) is composed of its own clauses and a pointer: "Dykes's table
  for Sahl has Mars under the rays at 18 west; Gr. Intr. VII.2, 31 puts him
  under the rays at 15 on the western side. Both give 18 east. Full text on
  the Sources page, and in the notes under this table." Its sentences stand
  whole in a notes expander after the Planetary Positions table, *Mars under
  the rays to 18° west.*, beside *The Moon under the rays to 15°.* (the
  Moon's tooltip text less its pointer; that tooltip is unchanged).
- **Special Degrees & Conditions.** Tooltip: the one-sentence glance with
  its three parentheticals dropped. Summary: the sentence whole. Notes:
  *Entering a sign.* · *Leaving a sign.* (ENTERING, LEAVING bold; each
  aphorism as a blockquote; IS inside Aphorism #15's quotation stands).
- The Calculation and Quadrant divisions tooltips read "this app".

### 2.7 The active-readings line (commit 7, `7cb7ab7`)

`_readings_note()` keeps its one `st.empty()` slot and its single-sentence
form for one reading off default. With two or more it fills the slot with
one container holding two captions: "{count} readings differ from defaults.
They are remembered between runs; see Sources and readings to reset them."
and a Markdown list "- Label = value" in the registry's order (the form the
one-reading sentence uses). One element in the slot either way, so the tab
bars keep their place; Sources shown stays excluded; nothing the semicolon
paragraph carried is dropped.

## Consolidated duplicates

None reduced. Four sentences are copied rather than moved -- the fetus's
year sentence, the third day's Firmicus sentence and Morin's "unfortunate
houses" sentence, each visible as a qualification and standing in its notes
paragraph where a later sentence refers back to it, and the eyesight
block's method line ("Neither table is precessed here: each is applied as
printed.") -- and a fifth after the gates: the fitting infortune's "When on,
that malefic drops out of every 'afflicted by an infortune' test in these
tables (…)" stands on the Configurations in-force line and on the Sources
page's entry for the reading. The Mars tooltip's sentences stand once, in the
notes; the Moon's tooltip stands unchanged and its text once more in the
notes beside them (a copy, so that the two readings' full texts are read
together).

## Fixed in passing

`tests/test_prose_counts.py::test_a_locator_names_its_volume_never_the_author_alone`
requires every Abu Ma'shar locator to carry "Gr. Intr." or "PN IV". Two in
the aspects notes on `main` -- "Abu Ma'shar VII.4, 7 notes that Saturn sits
inside the Moon's body …" and "… leaving it to be inferred -- Abu Ma'shar
VII.5, 24 (…)" -- did not, and the test never saw them because the notes
were a single-quoted literal in which the apostrophe was written `\'`, which
the test's regex does not match. Migrating the sentences into double-quoted
constants exposed them. They read "Abu Ma'shar, Gr. Intr. VII.4, 7" and
"Abu Ma'shar, Gr. Intr. VII.5, 24" now, the page's own citation form and
nothing else changed; the two sentences are listed under their own heading
in the nothing-lost list.

## Re-pinned tests (same intent, new strings or places)

- `tests/test_prose_tables.py::test_the_help_and_caption_state_what_the_table_is`:
  the Moon block's "natal analogy" and "supplies no condition split" are
  read from the visible summary; the tooltip is checked for its opening.
- `tests/test_prose_counts.py::test_dignity_caption_restates_the_solar_orbs`
  is `test_dignity_thresholds_table_is_built_from_the_solar_orb_constants`:
  the rendered table's rows equal `SOLAR_BURNED_ORB` and `solar_rays_orb()`
  per planet, the source builds the rows from them and `round(CAZIMI_ORB *
  60)`, and types no figure ("burned to 6° for Saturn and Jupiter" is gone);
  `currently {DOMAIN_RULE}` and the `DOMAIN_RULE_OPTIONS[0]` comparison
  still pinned.
- `tests/test_decisions_2026_09_08.py::test_d11_lot_of_death_...`: "STATED
  by Abu Ma'shar" is "**stated** by Abu Ma'shar".
- `tests/test_chart_layout_2026_09_15.py`: the four-caption tests read the
  introduction's container (main's fifth child, four Markdown children, 680
  px) and Calculation at `kids[5]`; the circumpolar test reads the caption,
  the notes expander (label, icon, two markdowns) and the container at
  `kids[4:7]`.
- `tests/test_fragments_2026_09_15.py::test_the_page_around_the_chart_fragment_is_untouched`:
  the container at `kids[4]`, Calculation at `kids[5]`.
- `tests/test_clickable_wheel_2026_09_15.py`: the two introduction tests read
  markdown, not captions.
- `tests/test_readability_a_2026_09_17.py::test_the_tabs_keep_their_place_whatever_the_readings_say`:
  its changed run has three readings off default, so it reads "3 readings
  differ from defaults" and accepts a `flex_container` in the slot.
- `tests/test_text_lengths_2026_09_17.py`: `ALLOWED_LONG` from 78 entries to
  53, twenty-five deleted, one per migrated string: Findings 7 (the fetus,
  third-day, eyesight, Valens, Rhetorius and Morin glances; the Mars help),
  Dignities 4 (the Moon help, the lords' help and caption, the evaluation
  caption), Configurations 8 (the fitting help; the Reception, Non-reception,
  triplicity-lord, right-sidedness, honor-guard, natural-connections and
  Book V glances), Reference 3 (the three captions), Chart 3 (the
  circumpolar caption, the Mars help, the special-degrees glance). `python
  tests/test_text_lengths_2026_09_17.py` prints 53 offenders: 32 help, 1
  glance, 20 captions, none on the six pages of this branch but the
  sidebar's LMT help (line 803, 345 characters, no page's block) -- the rest
  are the Prediction pages' and The releaser's opening caption, C's.

New tests: `tests/test_readability_b_2026_09_17.py` (33): per block, the
tooltip, the layers in order and the section headings; the locator-and-
blockquote pairs and the glued fragments on Findings; the three Dignities
selectors' options against their tables and the chosen row's cells; the
thresholds table's order and rows against the constants under the default,
Moon-15 and Mars-18-west readings; the Lots key against the table, the
provenance selector at both depths, the four cases and the Lot of death
apart, none of the seven capitalised phrases in `page_lots`; the aspects
key's rows and sections, the fitting line on and off, Reception's layers,
table rows, sections and absence, Non-reception's list, the grids' sections,
the display-only and supplement findings' tooltips and sections, the two
cross-references and no capitalised phrase left in `page_configurations`'
strings; the Reference headings, captions, sections, the engine constant
whole, the witnesses table and the nobility block at both depths; the Mars
tooltip and the positions notes, the circumpolar notes' presence and
absence, Special Degrees on 1240-09-18; the readings note's one-reading
sentence, its count and list in the slot on five pages with main's child
count unchanged, and the Configurations tabs' index with three readings off
default.

## The preview

On the clone (`almuten-readability-2`, port 8531, the owner's chart, the
Sources shown reading switched to the supplement for the supplement blocks
and put back), at 1400 × 900 dark and 1920 × 1080 light, measured by
script since the pane was not displayed in this session: no page scrolls
sideways; the introduction's paragraphs are 680 px at 16 px; the Column /
Meaning key sits at 680 px and the reception comparison at 864 px inside
its bordered tab, the Lot key and the witnesses table at the page's width
(896 px at 1400, 1416 at 1920), the thresholds table at 383 px; blockquotes
render with their left rule in both themes (text rgb(250,250,250) on
rgb(14,17,23); rgb(49,51,63) on white); every migrated block's headings,
tables and selectboxes are present on Findings (all nine findings on the
owner's chart under the supplement, the eyesight block included),
Dignities, Lots, Configurations (all four tabs, the supplement's blocks
merged; "Not present in this chart: Book V degrees" for the absent
finding), Reference and Chart. The selectboxes' keyboard path could not be
driven in this session: the pane was hidden, and BaseWeb's virtualised
listbox renders no options while the tab is not displayed (the click
opened it, the arrow keys reached an empty list); it is the same
`st.selectbox(index=None)` A verified by keyboard on the clone, and
`test_readability_b` drives every selector's `select()`. The clone's
`preferences.json` differs from before only in `_launches`;
`saved_charts.json` is unchanged; the viewport was reset and the preview
stopped. The circumpolar chart was not on the clone; the caption and
notes are pinned by `test_chart_layout` at 78.2 N.

`analysis_markdown` for 1240-05-23 and 1240-09-18, in Age and Date mode,
is byte-identical to `main`'s but for the export timestamp (a detached
worktree at `main`, since removed).

## Nothing-lost, forward

`python tests/tools/prose_preserved.py main --summary`: 1,329 base sentences, 114 base locators, **55 misses, 0 locator misses, 0 locator count drops**, exit 1. Every miss under its heading; the text of each stands on a page verbatim but for what the heading names.

*ALL CAPS to bold (capitals inside quotation marks stand, as on main; `test_prose_counts.py` pins none of these phrases, so it is unchanged; `test_decisions_2026_09_08.py`'s d11 test re-pins "STATED by Abu Ma'shar" as "**stated**")* — 42 (one of them, "THE APP'S ANGULAR-PROXIMITY GRADE …", is also "the app's" → "this app's"):
- ENTERING: "every planet which is at the beginning of a sign is weak until it is firmly established in it and comes to be 5 degrees within it" (Fifty Aphorisms #44, 87), repeated in On Nativities Ch.
- LEAVING: "if a planet came to be in the last degree of the sign, then its strength has already gone away from that sign, and its strength is in the next sign ... like a man putting his foot on the threshold of his door.
- He gives several of them MORE THAN ONCE, with formulas that genuinely conflict, and Dykes's apparatus does not silently reconcile them -- so neither does this table.
- The STANDING column records his editorial position in his own words where he states one.
- SAHL HIMSELF RULES: of the two sibling Lots, "both of the Lots are correct, so work with them both together" (3.11, 4) -- neither is subordinate.
- DYKES NAMES HIS CHOICE: of the three witnesses to the Lot of enemies, "I have used M here"; on the night reversal of the Saturn-Moon work Lot, "Paul instructs us to reverse it by night, but Abu Ma'shar says not to.
- DYKES MARKS ONE STANDARD: on children, "the usual calculation ... is that of Hermes."
- DYKES ONLY TABULATES: three Lots for work, after noting that "Sahl quietly switches to Masha'allah's treatise on Lots ... without telling us that the formula is different."
- The Lot of death is projected from Saturn: STATED by Abu Ma'shar (Gr.
- LOOKING is the whole-sign configuration (Union/Sextile/Square/Trine/Opposition, or Aversion if none applies) -- sign to sign.
- MOTION and EXACT ORB DIST are the degree-to-degree approach.
- CONNECTION is the active author's verdict, named as his own text names the state -- switch the Connection rule at the top of this page to see where they disagree; RULES DIFFER marks the pairs where the two tests disagree.
- STRENGTH is two different measures.
- LIGHT and HEAVY are the standing classes both authors name as nouns (Saturn heaviest through the Moon lightest), not a reading of momentary speed: they are fixed, and a planet slowing toward its station does not thereby become heavy.
- CONNECTING PLANET is the separate, directed fact: which one is actually closing the aspect.
- EQUAL ASCENSIONS (56): "Aries and Pisces, Taurus and Aquarius, Gemini and Capricorn, Cancer and Sagittarius, Leo and Scorpio, and Virgo and Libra."
- EQUAL DAYLIGHT (67-75), the antiscia: Gemini-Cancer, Taurus-Leo, Aries-Virgo, Libra-Pisces, Sagittarius-Capricorn, exactly as he lists them -- Aquarius-Scorpio completes the standard scheme but is not enumerated here and is not added (see the coverage note on the Sources page).
- DEGREES: "when a planet is in the first degree of Aries, then it is in the nature of a planet which is at the last degree of Pisces" (57); "the planet which is in 12° of Gemini is in the nature of the degree of the planet which is in 18° of Capricorn: so when it passes beyond 12° of Gemini, then it has separated from it" (62).
- So the counterpart degree runs backwards as the planet runs forwards, and MOTION is read from both speeds together.
- AFFINITY: 76-77 single out four pairs of each family as bridging an ordinary aversion -- Gemini-Capricorn, Sagittarius-Cancer, Aries-Virgo, Libra-Pisces "is called a natural connection by opposition" (76); Gemini-Cancer, Virgo-Libra, Sagittarius-Capricorn, Pisces-Aries "the natural connection by sextile" (77).
- 16-19: when they differ, a sixth of the excess for every hour of distance is added to the candidate NEAREST the planet (left rays); 20-21: for right rays the same, to the more DISTANT candidate.
- ABU MA'SHAR (VII.5, 129-133) is wider on every axis: all five dignities count (129), reception also runs in REVERSE where the accepting planet sits in the connector's dignity (130, which exists because Saturn is otherwise too slow to ever be received), house/exaltation is strongest (131), a lone minor dignity is weak unless two of bound/triplicity/face combine into a complete reception (132), and reception can hold by looking with no connection at all (133).
- He then classes reception a SECOND way, and under his rule the table shows both.
- DIGNITY QUALITY is 129-133, the local basis.
- OVERALL CLASS is 136-142: "a [2] middling reception is the planets' reception of each other from the house, exaltation, bound, triplicity, or face" (140) -- house and exaltation included -- while "if two met [together] from this, or each one of them received its associate, it is a strong reception" (141); the natural acceptances of 134-135 are "[3] below that" (142); the Moon received by the Sun (137) and a planet received by Mercury from Virgo (139) are his named strong forms, and the Sun receiving the Moon from the opposition keeps his own word, "detestable" (137).
- A lone domicile reception is therefore the strongest basis AND globally middling: both are true, and they are different questions.
- 56, RECEPTION AT ONE REMOVE: "if the Moon was connecting with a planet and that planet was connecting with the lord of the house of the Moon or its exaltation, then the Moon is received" -- the note there calls it "like a transfer of light which indirectly allows for reception."
- 57, AFTER THE SIGN CHANGE: "if the Moon was empty in course, and then she passed over into the next sign and connected with the lord of her first sign, it is JUST LIKE RECEPTION; and if she connected with a planet OTHER than [that], IT UNDERMINES HER."
- An empty table is NOT non-reception -- that is a separate set of hostile configurations, in the table below.
- Kind III (61): A is in its OWN fall and B has no house or exaltation there to rescue it -- "as though the one asking is offering defeat."
- Sahl's definition is about CONNECTIONS (6-21), not signs: a planet can be in trine by sign with everyone and still be banished if no planet is inside a live connection with it, and it can hold an out-of-sign body connection (20-21) and not be banished at all.
- THE APP'S ANGULAR-PROXIMITY GRADE, GENERALISED FROM SAHL, ON NATIVITIES 2.13, 48-51: the per-planet column applies 2.13's distances to every planet, which no text does -- an ordinal preference, no score; Aphorism #45 with fn 57 is credited for the universal-band analogy and Carmen I.28 for "the more that it is closer to the degree of the stake, the more elevated".
- APHORISM 45 AS PRINTED: "every planet which is [distant] from the stake in what follows it, by 15 degrees, is in the situation of one who is in the stake; and if it increases [beyond that], then it does not have strength" (90-92; the example 10 to 25 Aries).
- CONVENTIONS, this app's: the stake a planet FOLLOWS (zodiacally behind it: 2.13 "what follows it", Introduction 2, 33 "rising up to them"); oblique ascension at the horizon (the setting degree by the oblique descension) and right ascension at the meridian, a split Carmen's single rising instruction does not state; the ecliptic degree, latitude ignored; bands end-inclusive at 15, 30 and 45, truncated by the next actual stake; the five-degree allowance (Aphorism #44) lies on the other side of the stake and is not inherited.
- Each chapter prescribes an ORDERED SEQUENCE of events, and a row appears only when every step in that sequence actually occurs against the ephemeris -- the day columns show when.
- REVOKING (117): "a planet is connecting with a planet, but BEFORE IT REACHES IT, it retrogrades away from it."
- RESISTANCE (118): a light planet ahead of a heavier one by degree stations retrograde, reaches that heavier one BY RETROGRADATION, goes past it, and a third planet lighter still -- one that wanted the heavy planet -- meets the retrograde one instead.
- ESCAPE (119): the planet being applied to leaves its sign first; the applicant then follows across the SAME boundary on its own next crossing, and is captured by a body it meets in the new sign.
- 78 is whole-sign, narrowed to the six places that LOOK at the Ascendant.
- 83, advancing, is DYNAMIC -- read against the Alchabitius quadrant cusps, since the note on 83 says the word means "dynamically angular or succeedent, i.e. by primary motion with respect to the angular axes, and not by whole sign."
- 83 also carries Sahl's FIVE-DEGREE RULE: "the planet will not be falling from the stake unless it was 5 degrees distant from its rear -- I mean, if the stake was 10 degrees of Aries, then every planet which has less than 5 degrees between it and the stake is truly counted as being in the stake" (Fifty Aphorisms #44, 88), which he states again in On Nativities Ch.
- Stated for ONE planet, the sect light's first triplicity lord (fn 190), and applied to it in the last column

*"the app" → "this app" (brief 2(e))* — 7:
- The intermediate quantities of the chart calculation -- universal time, the Julian day, sidereal time, the RAMC, the obliquity -- so a hand calculation can be checked against the app line by line.
- Domicile, exaltation, the three triplicity lords (day, night, participating) and the three faces of each sign, as the app holds them.
- The same table the app directs by; pinned against four independent witnesses.
- The twelve quadrant house cusps computed by the Alchabitius (semi-arc) system -- the app's other unit beside the whole-sign places: whole signs where the texts speak of a topic, these divisions where they speak of a planet's strength (the five-degree allowance at the four axial degrees).
- The equation with Morin's phrase is the app's; the three are the tradition's difficult averse places, as Dykes's note on al-Qabisi III.28's "cadent from the Ascendant" has it (ITA IV.4.1 fn 43): "That is, being in aversion to it; in a sign which does not aspect the rising sign, particularly the twelfth, eighth, and sixth; the second sign is also cadent from the Ascendant but is not considered as difficult."
- Readings, the app's: "casting rays upon its companion" = the pair is Connected under the Configurations page's connection rule; "one of its shares" = a triplicity, bound or face held by the partner of a planet in its house or exaltation; "of the sect of the day or ... night" = both planets of one sect, Mercury not counted.
- Readings, the app's: "eastern from the Sun" = rising before him (the solar phase's side); "western from the Moon" = rising after her, by the shorter arc; "in the stakes" = the whole-sign places 1, 4, 7, 10 (rank is a topic, so the sign-places); "look at" = the whole-sign aspect.

*Cross-reference reworded (N's rule: a page named as the bar names it)* — 2, both in the Planetary Condition block, "the Dignities page" → "the Dignities and places page":
- They are kept beside the Dignities page, which prints both the good and the bad Rhetorius/PN IV reading for each placement and chooses neither, showing this Net as a lean; a Net of −1, 0 or +1 is Indeterminate on both pages.
- They are kept because Topical Planets in Houses on the Dignities page prints both the good and the bad reading for every placement and chooses neither: this Net is shown there as a lean, and a Net of −1, 0 or +1 is Indeterminate in both places.

*Rebuilt into the table "Solar phase thresholds" from the sentence* — 2: the two fragments the script prints of the one caption sentence, split at the old `MOON_RAYS_ORB` interpolation (the table's source sentence is listed under the table in §2.2):
- Solar phase follows Abu Ma'shar's walk through the synodic cycle (VII.2); Sahl's *On Nativities* 1.22 and al-Biruni give the under-the-rays figures independently (Sahl states no burn boundary, and his Mars westernizes at 18°, not 15°): burned to 6° for Saturn and Jupiter, 10° for Mars, 7° for Venus and Mercury, 6° for the Moon; under the rays to 15°, 18° east / 15° west, 12° east / 15° west, and
- ° for the Moon; in the heart within 16' (VII.2, 7-9, from the Sun's own apparent diameter).

*Locator brought to the citation convention* — 2, a seventh heading, explained under "Fixed in passing": "Abu Ma'shar VII.4, 7" → "Abu Ma'shar, Gr. Intr. VII.4, 7" and "Abu Ma'shar VII.5, 24" → "Abu Ma'shar, Gr. Intr. VII.5, 24", each sentence otherwise verbatim (the BODIES sentence, which carries the first, is an ALL CAPS sentence and is counted above):
- BODIES is whether each planet falls inside the other's sphere of power, which is asymmetric because the spheres differ in size: Abu Ma'shar VII.4, 7 notes that Saturn sits inside the Moon's body from 12 degrees while she only enters his at a little under 9.
- Retrogradation reverses it, and both authors say so rather than leaving it to be inferred -- Abu Ma'shar VII.5, 24 ("the connection of one of them with the other ... will be BY RETROGRADATION"), VII.5, 118 ("the light one IN MORE DEGREES goes retrograde and connects with the heavy one"), and the note on VII.5, 130 (Saturn "could never be received because he is too slow to connect with anyone, UNLESS BY RETROGRADATION").

## Nothing-lost, reverse

`python tests/tools/prose_preserved.py readability-b-2026-09-17 --tree <a detached worktree at main>` from this tree: **148 branch sentences not on main**, plus `LOCATOR-COUNT` lines, which in this direction (base = the branch, tree = main) say the branch holds more copies of a token than main: Ch. 3, 49-55 and VII.5, 129-133 (the reception table's headers and section headings beside the paragraphs), Ch. 3, 58-62 (Non-reception's tooltip and summary), VII.4, 5-8 (the aspects key and its section), Nativities 1.19, VII.2, 31 and VII.2, 61 and 72-73 (the Chart notes beside the tooltips), VII.8, VII.8, 3-8, VII.8, 3 and VII.2 (the witnesses table beside its sentence), Nativities 2.13 (the triplicity block's headings) -- copies made by headings, table headers and a tooltip's sentence standing as the summary too, no copy lost on either side (the forward run reports 0 count drops). Every branch-only sentence classified:

*Table rows (the comparison tables' and the keys' rows, and the script's fragments of them)* — 11:
- VIII.3, 28-29 -- the Lot of the Invisible, which Sahl names
- VIII.4, 22-24, "the Lot of firmness and survival, the Lot of the Ascendant's support" (fn 67: the Greek Basis)
- \| Lot \| Formula \| Stated where \| \|---\|---\|---\|
- \| Construction \| The luminaries' middle years \| Witnesses \| \|---\|---\|---\| \| (least + great/2)/2 \| 39 1/2 for both \| Valens VII.5; Gr.
- VII.8, 3-8 with Figure 146; Abu Bakr, On Nativities I.16, the same construction in prose (half the greater years added to the lesser, the sum halved); PN IV I.8, 12, the Moon's 4 as a tenth of her middle years \| \| The ordinary mean \| the Sun 69 1/2 and the Moon 66 1/2 \| Masha'allah, Book of Aristotle III.1.8; Abu 'Ali al-Khayyat, Judgments of Nativities Ch.
- 4; the Latin Great Introduction's table of the years as Dykes prints it (ITA VII.2, Figure 108) \|
- \| Planet \| Burned within \| Under the rays within \| \|---\|---\|---\|
- - Sahl himself rules: of the two sibling Lots, "both of the Lots are correct, so work with them both together" (3.11, 4) -- neither is subordinate. - Dykes names his choice: of the three witnesses to the Lot of enemies, "I have used M here"; on the night reversal of the Saturn-Moon work Lot, "Paul instructs us to reverse it by night, but Abu Ma'shar says not to.
- \| Column \| Meaning \| \|---\|---\| \| Motion, Exact Orb Dist \| The degree-to-degree approach \| \| Bodies \| Whether each planet falls inside the other's sphere of power, which is asymmetric because the spheres differ in size \| \| Connection \| The active author's verdict, named as his own text names the state \| \| Rules differ \| The pairs where the two tests disagree \| \| Strength \| Two different measures: for an assembly the source's own, whose body reaches whose (VII.4, 5-8) and whether they share a bound; for an aspect "(app scale)", this app's own scanning aid \| \| Light, Heavy \| The standing classes both authors name as nouns (Saturn heaviest through the Moon lightest), not a reading of momentary speed \| \| Connecting planet \| The separate, directed fact: which one is actually closing the aspect \|
- 3, 49-55) \| Abu Ma'shar (VII.5, 129-133) \| \|---\|---\|---\| \| Direction \| One way only: the connecting planet stands in a dignity of the planet it connects with, and so is received by it \| Also in reverse, where the accepting planet sits in the connector's dignity (130) \| \| Dignities that count \| House or exaltation is perfect reception; triplicity alone ranked below it (50); bound only paired with triplicity (54-55); face never appears \| All five dignities count (129); house/exaltation strongest (131); a lone minor dignity weak unless two of bound/triplicity/face combine (132) \| \| Connection required \| Always \| Reception can hold by looking with no connection at all (133) \|
- - Kind I (58): B holds no essential dignity at all at A's position -- B is alien in A's sign, so A is not recognised. - Kind II (59-60): A stands in B's own sign of fall, "like one who comes to it from the house of its enemies." - Kind III (61): A is in its own fall and B has no house or exaltation there to rescue it -- "as though the one asking is offering defeat." - Kind IV (62): B is in its own fall, which brings the connection down whatever A's condition. - Kind V (62): B sits in A's own sign of fall.

*Section headings, disclosure titles and bold leads* — 68:
- How the standings are recorded
- Why the hour lord is approximate here
- The text's own reservation.
- The translator's readings.
- This app's implementation.
- Where the four classical Lots are stated
- The middle years, this app's convention.
- Why the middle years differ
- This app's ordinal-degree convention.
- The Moon under the rays to 15°.
- Mars under the rays to 18° west.
- This app's reading of the year.
- The third day, this app's reading of Firmicus.
- Masha'allah's signification.
- The twelve passages, and the arrangement.
- Masha'allah's condition, where he states it.
- This app's ranking convenience.
- The Lot of death: a stated rule with a manuscript variant.
- The seven praised places' printed order.
- Two constructions of the middle years.
- The witnesses, kept apart.
- The ordinal span, and the editor's endpoint reading.
- The distinct source lists.
- No temporal hour exists for this date at this location.
- The meeting before the birth and its Ascendant (1.8, 5-6).
- The three divisions of 1.8, not computed.
- The seven-month native and the four-footed nativities (1.8, 1).
- The three Moons of 1.9, 1, and the year.
- The aspects of 1.9, 2-10.
- The conception and the stay by the day and hour, not computed (1.9, 11-14).
- The sentences: 1.29, 11-13 and 1.26, 7.
- Clauses not evaluated: 1.29, 11 and 12.
- This app's addition, and what is not tested.
- Dykes's note on "unsound".
- Phase boundaries used by this app.
- The unfortunate houses, this app's reading.
- Sahl's own table of the second rule.
- The four, in the sources' words.
- Four witnesses, and three against.
- Sahl, On Nativities 6.2, 48-75: four lists.
- VI.20: the measured places.
- Two spans read from a phrase, and one bare number.
- Abu Bakr, On Nativities II.7.3: his list, beside the others.
- The conditions tested, each with its reading.
- Rhetorius's chapters, as Holden has them.
- The besiegers of an afflicted planet.
- The four governing sentences, whole.
- Quoted but not tested, and what is not read.
- The columns, and what each one measures.
- Connection, and where the rules differ.
- Light and heavy: the standing classes.
- The connecting planet, and retrogradation.
- Sahl and Abu Ma'shar on reception
- Equal ascensions (56), and equal daylight (67-75).
- Degrees, and the motion read from both speeds.
- The same pairs in the Reception table.
- V.22, 1-2 and 4, the sentences.
- Ordinal degrees, and the degrees in both tables.
- An ordered sequence, against the ephemeris.
- This app's generalisation, an ordinal preference and no score.
- Aphorism 45 as printed, and the editor's correction.
- A second definition, and the witnesses.
- Abu Ma'shar's reception (VII.5, 129-133).
- Dignity quality: the local basis.
- Sahl's reception at one remove (56).
- Sahl's reception after the sign change (57).
- Testimonies 78 and 83: two measurements.
- Distinct from Planetary Condition.

*Placeholders and boilerplate (the three selectbox placeholders, the count caption's constant part, the Mars tooltip's pointer, the thresholds table's caption)* — 6:
- Select a house to read the Moon's transit through it in full
- Select a topical house to read its lord's placement and Masha'allah's sentence
- Select a Lot to read its standing, source and editor's note
- The figures shown are those in force under the current readings.
- Full text on the Sources page, and in the notes under this table.
- readings differ from defaults.

*Reworded per the forward list: ALL CAPS to bold (each matches main case-insensitively; two are the four cases' and the five kinds' list bodies as the script joins them)* — 35:
- He gives several of them more than once, with formulas that genuinely conflict, and Dykes's apparatus does not silently reconcile them -- so neither does this table.
- Looking is the whole-sign configuration (Union/Sextile/Square/Trine/Opposition, or Aversion if none applies) -- sign to sign.
- 16-19: when they differ, a sixth of the excess for every hour of distance is added to the candidate nearest the planet (left rays); 20-21: for right rays the same, to the more distant candidate.
- The Standing column records his editorial position in his own words where he states one.
- We should follow Paul." - Dykes marks one standard: on children, "the usual calculation ... is that of Hermes." - Dykes only tabulates: three Lots for work, after noting that "Sahl quietly switches to Masha'allah's treatise on Lots ... without telling us that the formula is different."
- The Lot of death is projected from Saturn: stated by Abu Ma'shar (Gr.
- Sahl's definition is about connections (6-21), not signs: a planet can be in trine by sign with everyone and still be banished if no planet is inside a live connection with it, and it can hold an out-of-sign body connection (20-21) and not be banished at all.
- Motion and Exact Orb Dist are the degree-to-degree approach.
- Connection is the active author's verdict, named as his own text names the state -- switch the Connection rule at the top of this page to see where they disagree; Rules differ marks the pairs where the two tests disagree.
- Strength is two different measures.
- Light and heavy are the standing classes both authors name as nouns (Saturn heaviest through the Moon lightest), not a reading of momentary speed: they are fixed, and a planet slowing toward its station does not thereby become heavy.
- Connecting planet is the separate, directed fact: which one is actually closing the aspect.
- An empty table is not non-reception -- that is a separate set of hostile configurations, in the table below.
- Equal ascensions (56): "Aries and Pisces, Taurus and Aquarius, Gemini and Capricorn, Cancer and Sagittarius, Leo and Scorpio, and Virgo and Libra."
- Equal daylight (67-75), the antiscia: Gemini-Cancer, Taurus-Leo, Aries-Virgo, Libra-Pisces, Sagittarius-Capricorn, exactly as he lists them -- Aquarius-Scorpio completes the standard scheme but is not enumerated here and is not added (see the coverage note on the Sources page).
- Degrees: "when a planet is in the first degree of Aries, then it is in the nature of a planet which is at the last degree of Pisces" (57); "the planet which is in 12° of Gemini is in the nature of the degree of the planet which is in 18° of Capricorn: so when it passes beyond 12° of Gemini, then it has separated from it" (62).
- So the counterpart degree runs backwards as the planet runs forwards, and motion is read from both speeds together.
- Affinity: 76-77 single out four pairs of each family as bridging an ordinary aversion -- Gemini-Capricorn, Sagittarius-Cancer, Aries-Virgo, Libra-Pisces "is called a natural connection by opposition" (76); Gemini-Cancer, Virgo-Libra, Sagittarius-Capricorn, Pisces-Aries "the natural connection by sextile" (77).
- Revoking (117): "a planet is connecting with a planet, but BEFORE IT REACHES IT, it retrogrades away from it."
- Resistance (118): a light planet ahead of a heavier one by degree stations retrograde, reaches that heavier one by retrogradation, goes past it, and a third planet lighter still -- one that wanted the heavy planet -- meets the retrograde one instead.
- Escape (119): the planet being applied to leaves its sign first; the applicant then follows across the same boundary on its own next crossing, and is captured by a body it meets in the new sign.
- Stated for one planet, the sect light's first triplicity lord (fn 190), and applied to it in the last column
- This app's angular-proximity grade, generalised from Sahl, On Nativities 2.13, 48-51: the per-planet column applies 2.13's distances to every planet, which no text does -- an ordinal preference, no score; Aphorism #45 with fn 57 is credited for the universal-band analogy and Carmen I.28 for "the more that it is closer to the degree of the stake, the more elevated".
- Conventions, this app's: the stake a planet follows (zodiacally behind it: 2.13 "what follows it", Introduction 2, 33 "rising up to them"); oblique ascension at the horizon (the setting degree by the oblique descension) and right ascension at the meridian, a split Carmen's single rising instruction does not state; the ecliptic degree, latitude ignored; bands end-inclusive at 15, 30 and 45, truncated by the next actual stake; the five-degree allowance (Aphorism #44) lies on the other side of the stake and is not inherited.
- Each chapter prescribes an ordered sequence of events, and a row appears only when every step in that sequence actually occurs against the ephemeris -- the day columns show when.
- Abu Ma'shar (VII.5, 129-133) is wider on every axis: all five dignities count (129), reception also runs in reverse where the accepting planet sits in the connector's dignity (130, which exists because Saturn is otherwise too slow to ever be received), house/exaltation is strongest (131), a lone minor dignity is weak unless two of bound/triplicity/face combine into a complete reception (132), and reception can hold by looking with no connection at all (133).
- He then classes reception a second way, and under his rule the table shows both.
- Dignity quality is 129-133, the local basis.
- Overall class is 136-142: "a [2] middling reception is the planets' reception of each other from the house, exaltation, bound, triplicity, or face" (140) -- house and exaltation included -- while "if two met [together] from this, or each one of them received its associate, it is a strong reception" (141); the natural acceptances of 134-135 are "[3] below that" (142); the Moon received by the Sun (137) and a planet received by Mercury from Virgo (139) are his named strong forms, and the Sun receiving the Moon from the opposition keeps his own word, "detestable" (137).
- A lone domicile reception is therefore the strongest basis and globally middling: both are true, and they are different questions.
- 56, reception at one remove:
- 57, after the sign change:
- 78 is whole-sign, narrowed to the six places that look at the Ascendant.
- 83, advancing, is dynamic -- read against the Alchabitius quadrant cusps, since the note on 83 says the word means "dynamically angular or succeedent, i.e. by primary motion with respect to the angular axes, and not by whole sign."
- 83 also carries Sahl's five-degree rule:

*Reworded per the forward list: "this app", the Dignities and places cross-references, the two locators (otherwise verbatim)* — 11:
- The intermediate quantities of the chart calculation -- universal time, the Julian day, sidereal time, the RAMC, the obliquity -- so a hand calculation can be checked against this app line by line.
- Domicile, exaltation, the three triplicity lords (day, night, participating) and the three faces of each sign, as this app holds them.
- The same table this app directs by; pinned against four independent witnesses.
- The twelve quadrant house cusps computed by the Alchabitius (semi-arc) system -- this app's other unit beside the whole-sign places: whole signs where the texts speak of a topic, these divisions where they speak of a planet's strength (the five-degree allowance at the four axial degrees).
- They are kept beside the Dignities and places page, which prints both the good and the bad Rhetorius/PN IV reading for each placement and chooses neither, showing this Net as a lean; a Net of −1, 0 or +1 is Indeterminate on both pages.
- They are kept because Topical Planets in Houses on the Dignities and places page prints both the good and the bad reading for every placement and chooses neither: this Net is shown there as a lean, and a Net of −1, 0 or +1 is Indeterminate in both places.
- The equation with Morin's phrase is this app's; the three are the tradition's difficult averse places, as Dykes's note on al-Qabisi III.28's "cadent from the Ascendant" has it (ITA IV.4.1 fn 43):
- Bodies is whether each planet falls inside the other's sphere of power, which is asymmetric because the spheres differ in size: Abu Ma'shar, Gr.
- Retrogradation reverses it, and both authors say so rather than leaving it to be inferred -- Abu Ma'shar, Gr.
- Readings, this app's: "casting rays upon its companion" = the pair is Connected under the Configurations page's connection rule; "one of its shares" = a triplicity, bound or face held by the partner of a planet in its house or exaltation; "of the sect of the day or ... night" = both planets of one sect, Mercury not counted.
- Readings, this app's: "eastern from the Sun" = rising before him (the solar phase's side); "western from the Moon" = rising after her, by the shorter arc; "in the stakes" = the whole-sign places 1, 4, 7, 10 (rank is a topic, so the sign-places); "look at" = the whole-sign aspect.

*Truncations and compositions of main's own clauses (tooltips and visible leads; every clause is on main and the whole sentence stands elsewhere on the branch)* — 17:
- Flags planets in Sahl's dark signs (Libra, Capricorn), in the two signs of his burned place, in a welled degree of their sign, or in one of Sahl's two sign-boundary conditions.
- What 1.8 and 1.9 let this app state of the fetus's stay in the belly.
- The Moon on the third day -- two days after the birth, the birth day counted as the first.
- A natal analogy: VII.8 reads the Moon's transit through the houses, and the natal Moon's own whole-sign house is marked.
- Every cell's wording is this app's paraphrase of Sahl's own sentence for that pairing, from his twelve lords-of-places passages in On Nativities.
- Masha'allah's condition is his own, stated at the end of eight of the twelve lord-of-the-Nth sections.
- Dykes's table for Sahl has Mars under the rays at 18 west; Gr.
- The "degrees of chronic illness in the signs".
- Abu Bakr, On Nativities II.1.0: Mars in his own domicile (Aries, Scorpio) by night, or by day.
- Valens's eleven phases of the Moon, the chart's Moon placed in one by its angle ahead of the Sun.
- Each trine, sextile, square or opposition that a Fortune (Jupiter, Venus) or an Infortune (Saturn, Mars) casts to another planet.
- Two degree tables from Book V that no condition in VII.6 reads.
- A planet separating from one of the two infortunes (or, per Abu Ma'shar's extension, fortunes) and connecting with the other, with neither leg intercepted by a third planet's rays.
- 3, 58-62), a distinct finding from simply lacking reception.
- Stated for one planet, the sect light's first triplicity lord (fn 190), and applied to it in the last column.
- 2.5, 2: a pair in square or sextile, both in their exaltations or houses (or one in each, or one of them in one of its shares), each casting rays upon the other -- "a strong right-sidedness".
- 10: the planets "formed an honor-guard for [the luminaries] (and that is if the planets were eastern from the Sun and western from the Moon)".

## What remains for C

- `ALLOWED_LONG` holds 53 entries: the Prediction pages' 51 and The
  releaser's opening caption are C's; the sidebar's LMT help (line 803, 345
  characters) belongs to no page block and no branch's brief -- C or a
  later pass.
- "the app" stands in six page strings: the triplicity finding's title on
  Configurations (a fixture key and the export's heading, kept) and five on
  the Prediction pages (C's); three docstrings say it too, which are not
  page text.
- The renderer contract is unchanged; the reception block shows how to
  place a three-column table at the page's width inside a notes disclosure
  (a hand-built `st.expander(…, icon=NOTES_ICON)` with the table before
  `_note_sections`), and the Planetary years block does the same as a
  sibling.
- A `_finding` that returns early (absent) draws no sibling disclosure:
  guard the sibling with the data, as Reception does.
- The nothing-lost script's paragraph rule: a `\n\n` in a base constant
  ends a sentence, so only a fragment glued to a closing mark in the same
  paragraph (`" -- the meeting …`, `") -- not computed …`, `" So the …`)
  must stay in one constant after the mark; a sentence that opened a new
  paragraph after a quotation is free to stand under its own heading.
- The preview clone's pane was hidden for this agent; the keyboard path
  on a selectbox needs a displayed pane.
- The Chart page's wheel pick panel (`_pick_panel`, main's strings) says
  "The Dignities page carries …" twice and "The Reference page carries …"
  three times; the bar names them "Dignities and places" and "Reference
  tables" -- for C or a later pass, not this branch's.
