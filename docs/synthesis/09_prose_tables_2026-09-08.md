# Prose tables: unsourced cells removed, bled cells restored, both tables pinned by content — 2026-09-08

Branch `prose-tables-2026-09-08` off `main` @ `ba567ce` (975 passed / 2 xfailed, re-run before any
change). Authority throughout: *TNAC Reference Guide for the Planets and Places* (Dykes 2023),
read as page images (pp. 16–40), not `pdftotext`, whose two-column rendering interleaves rows.

## 1. Unsourced cells → explicit uncertainty — `d639683`

| Cell | Said | Guide | Now |
|---|---|---|---|
| `PLANETS_IN_HOUSES[6]['Moon']` | *"Health and bodily stability."* / *"Fluctuating health, bodily weakness."* | p. 28: `?` / `?`, PN4 blank | `[UNCERTAIN -- the TNAC Reference Guide (p. 28) prints ? … do not rely on this cell]` in both |
| `PLANETS_IN_HOUSES[8]['Moon']` | *"Sudden inheritance, finding money."* / *"Passive and sick."* | p. 32: `?` / `?`, PN4 blank; the text is **Mercury's** Bad cell, *"(Evening by night): sudden inheritance, finding money, fortunate; passive and sick"*, split at the semicolon | same marker, p. 32 |

No substitute delineation supplied. Pinned by `test_moon_cells_the_guide_leaves_blank_stay_marked_uncertain[6,8]`
and the control `test_no_other_cell_is_marked_uncertain`.

## 2. The four bled cells named in `08` §2a — `a8050f2`

| Cell | Said | Guide row (page) | Now |
|---|---|---|---|
| 3rd Sun Good | *"Good for marriage/religion; travel with good status"* (= Venus's row) | p. 21 Sun Good: *"Bad death for father; serious in counsel, responsible for management of public things, religious honors and duties"* / *"Travel due to Sultan; good reputation due to religion, good from relatives and brothers"* | that |
| 3rd Mars Bad | *"Bad death for father, evil reports, difficult travels"* (Sun's line bled in) | p. 21 Mars Bad: *"Worse than by night?"* / *"Evil reports about him; difficult travels; illness from heat, misfortune from wild animals"* | that |
| 8th Sun Bad | *"Wealthy, benefit from death of women; negligence"* (= Venus Good) | p. 32 Sun Bad: *"See above"* / *"Leisure but without benefit, poor way of life, negligence or laziness"* | that |
| 8th Venus Good | *"Marry late; benefit from underclass/commerce"* (Venus Bad + Mercury) | p. 32 Venus Good: *"Wealthy, benefit from death of women, easy death"* / *"Benefit from underclass or base work; much spending"* | that |

## 3. Siblings — all 84 cells re-read by content — `49e9bba`

**Re-read: 84 of 84 `PLANETS_IN_HOUSES` cells against pp. 17–40 (plus p. 22 for the 3rd's Moon
row).** The overlap heuristic had cleared nine houses; the content read found **ten more defective
cells in seven of them**, all with the same fingerprint the owner identified — a sentence or half
sentence in a cell of the right shape but the wrong row, usually the Guide's *Good/of sect* line
placed in the code's *Bad* cell of the same planet (or the reverse), which no overlap test can see:

| Cell | Defect | Guide (page) |
|---|---|---|
| 2nd Mercury Good | *"good at learning"* is the Bad cell's *"Evening star by day: good at learning; poor"* | p. 19 |
| **3rd Moon Good** | was *"Good religious activities (with Jupiter)"* — a fragment of the **Bad** cell; the Guide's Good line, *"With Saturn: slow, unsuccessful, sacrilegious"* (fn. 76, Firmicus), was absent | p. 22 |
| 4th Sun Bad | *"Annoyances"* is the Good line *"Annoyances and interruptions in life; better in old age"*; the Bad line is *"Destroys native, parents, and livelihood"* | p. 24 |
| 6th Mars Bad | *"Harms children, uneven life, illness"* is the **Good** cell (fn. 78, "reading with Firmicus") | p. 28 |
| 6th Sun Good | *"good fortune from parents"* is inside the Bad cell's condition (*"…but with one, good fortune from parents and resources"*) | p. 28 |
| 6th Venus Bad | the low-quality-women line is the **Good** cell; Bad is *"See above"* / *"Leisure time and illness"* | p. 28 |
| 7th Sun Bad | *"conflict"* is Venus's PN4 Bad | p. 30 |
| 7th Mercury Good | *"Managing affairs of women"* is the **Bad** cell's nocturnal line; Good is the diurnal *"Bad with Venus or Mars: lewd, brothel-keepers, fugitives"* | p. 30 |
| 8th Venus Bad | *"loss"* is Mercury's PN4 Bad | p. 32 |
| 12th Mars Bad / Sun Bad | *"exile"* is the Sun's PN4 Bad, restored to the Sun; Mars's PN4 Bad line added | p. 40 |

Clean on content read: houses 1, 5, 9 (see below), 10, 11 in full; every other cell of 2, 3, 4, 6,
7, 8, 12 not listed above.

**Reported, not changed:** 9th Mercury (p. 34). The Guide prints its PN4 cells against its own
column headings — *Good/of sect*: *"Bad reports and journeys; defamed in religion, bad assets and
commerce"*; *Bad/contrary*: *"Good journeys, true visions, good religious reputation, good reason
and management"*. The code has them the sensible way round. Which to follow is a decision about the
Guide, so the pin holds the code as it is and the docstring says so.

## 4. `MASHAALLAH_LORDS[8][5]` — `91229f4`

Was `[UNCERTAIN -- the source reads '[illegible] they will survive and will be miscarried' …]`
(Sol, 2026-09-05). Guide p. 31, "The lords of other places in the 8th", row **5th**: *"Children
premature or miscarried."* Now that string; the table's comment records that the OCR of Sahl 8.5 is
still illegible and the resolution is the course document's. Pinned by
`test_lord_of_the_fifth_in_the_eighth_is_resolved_from_the_guide`, which also asserts no
`[UNCERTAIN` remains anywhere in the lords table.

All 144 lords cells were also re-checked by anchor against their Guide rows (every cell shares at
least two content words with its own row; none fits another row better).

## 5. The content pins — `tests/test_prose_tables.py`, 40 tests

Two pins per cell, both transcribed from the Guide rather than from the code's self-description:

1. **Literal** — every cell of both tables as it stands after the re-read, keyed to the Guide page.
   Any edit fails on the cell and must be reconciled against that page.
2. **Anchors** — for each cell, words its paraphrase shares with the Guide's *own row* for that cell,
   extracted mechanically from the Guide text (2–3 per cell; every one of the 84 + 144 cells has at
   least two). A cell moved to another planet or house keeps its literal but loses its anchors.
   Where the Guide prints `?`, the anchor is `None` and the marker is asserted instead.

**What the pins would have caught, shown against `main` @ `ba567ce`:** the literal pin fails on all
16 corrected `PLANETS_IN_HOUSES` cells and the one lords cell; the anchor/uncertainty pin, which
does not depend on the wording chosen here, fails on **12 of the 16** — both fabricated Moon cells,
every cell whose text came from another planet's row (3rd Sun, 8th Sun, 8th Venus), and seven
others. The four it cannot see (2nd Mercury, 3rd Moon, 4th Sun, 6th Venus) are Good/Bad swaps
within one planet, where the row's words are all still present; the literal pin holds those.

## What moves for users

Displayed delineation strings on the Dignities page ("Topical Planets in Houses" and the
Rhetorius/PN4 expander; the Masha'allah lords table). No number, score, fixture or chart changes.

## Not verified / out of scope

- The Guide's own transcription of Rhetorius, Firmicus and PN4 is taken as authority; PN4 is not in
  the corpus.
- 9th Mercury (above) awaits an owner decision.
- `WELLED_DEGREES` untouched, per the brief.
