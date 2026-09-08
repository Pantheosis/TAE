# Phase 1 — Abū Ma'shar, *Great Introduction* Book V excerpt: V.19–V.22, Figures 59–64

Source: `abu_mashar_book_vii.md:2181–2416`, pp. 303–310 of **Abū Ma'shar's own volume** (not
Sahl's *Volume I*; the two paginations collide by coincidence, see `CORPUS_MANIFEST.md`). Four
chapters, six figures, 218 lines. Read end to end on 2026-09-08 before `app.py` was opened.
Written on branch `book-v-excerpt-2026-09-08`, which sits on the wells fix
(`wells-fix-2026-09-08` @ `ea34231`): `WELLED_DEGREES` is already corrected and pinned there, and
every "Fig. 63" in `app.py` already names its volume. Neither is redone here.

**Heading conventions.** One `###` heading per chapter (`Chapter V.19` … `Chapter V.22`).
Sentence numbers restart per chapter. Where a sentence *is* a figure the file says so in
brackets (`[Sentence 2 is Figure 59 below.]`, `[Sentence 5 is Figure 62 below.]`) and the prose
skips that number; V.22's two tables are unbracketed but the captions give their sentence ranges
(1–3 and 4–5). The excerpt opens with the last sentence of **V.18** (`:2185`, ¶8, on the lords of
the bounds: *"the one which Hermes stated is more correct"*) and closes with **V.22, 6–8**, which
are the envoi of Book V, not part of the degree doctrine. Footnotes run **106–116** (Dykes's
continuous numbering for this volume, as in Book VII).

**Figure-number collisions.** All six numbers also exist in Sahl's *Volume I*: Sahl Fig. 59
(*Nativities*), Fig. 60 (Valens Fortune-years, `on_nativities.md:8349`), Fig. 61 ("Frequency of
illness"), Fig. 63 (Lots of action or work, `:12196`), Fig. 64 (the *Questions* Ch. 1 example
chart, used in `04_tier1_and_spearbearing_report.md`). Every reference to any of them must name
the volume. `synthesis/00_inventory.md` had called Abū Ma'shar's Fig. 61 "the aspect-conditions
table"; it is the degrees of brightness, and the inventory line is corrected in this pass.

---

## 1. V.19 — the male and female degrees (¶1–8; Figure 59, p. 304)

**Doctrine (¶1).** *"Within the twelve signs are male and female degrees: so if there was a
nativity or question about males, and the planets and degree of the Ascendant occurred in male
degrees, it would be stronger for them; and if there was a nativity or question about females,
and the stars occurred in the female degrees, it would be stronger for them."* — V.19, 1. The
use is topical (a question *about* males or females), not a general dignity.

**Three schemes, and no verdict.**

- *Scheme 1 — the table (¶2 = Figure 59).* fn. 109: *"Sentence 2 is a table constructed from the
  sentences in Gr. Intr. which for the most part simply list amounts of degrees and genders …
  The table is very similar to that of Firmicus Maternus in Mathesis IV.23."* Dykes built the
  ranges; the widths are Abū Ma'shar's.
- *Scheme 2 — halves and quarters (¶3–4).* *"some of the ancients … make [them] be male from
  their beginning up to twelve and a half degrees, and twelve and a half degrees female, then two
  and a half degrees male, and two and a half female"*; female signs mirror it.
- *Scheme 3 — twelfth-parts (¶5–6).* *"[some] people assigned the degrees of each sign … in
  accordance with the nature of the twelfth-parts of the signs"*: 2½° bands alternating from the
  sign's own gender. fn. 106: *"That is, Vettius Valens (Anth. I.11), probably from the
  Bizidaj."*
- *The combination rule (¶7–8).* *"So, in these three ways they stated the masculinization of the
  degrees of the signs, and their feminization. Whenever two or three of these indications
  coincide in masculinization or feminization for a single position, it is stronger for it."*
  fn. 108: *"Abū Ma'shar does not take a stance on which one is correct, so that one might use all
  three and play the odds."*

**Internal observation.** With three binary indicators, two of them *always* coincide, so ¶8 as
written is never undecided; read strictly it is a majority vote, and "stronger" can only
distinguish unanimity (all three) from a bare majority. Measured over the zodiac at half-degree
steps (`bookv_check.py`): the three schemes are **unanimous on 35.6%** of positions; the table
agrees with scheme 2 on 55.3%, with scheme 3 on 49.2%; schemes 2 and 3 agree with each other on
66.7%. The table's gender matches the **sign's** gender on only 174/360 = **48.3%** of degrees
(ten of twelve rows open masculine, including five female signs; only Gemini and Virgo open
feminine), so "male sign *or* male degrees" is a much wider net than "male sign".

**Figure 59 integrity** (rebuilt from photographs after marker corrupted every glyph; checked here
for the Figure 62/146 pattern — a dropped, duplicated or shifted row): **nothing found.** All
twelve rows parse; every printed width equals its range (end − start + 1); every row runs 0°–29°
without gap or overlap; genders alternate in every row; no two rows are identical; the row
totals are 21/22/15/19/18/15/18/16/15/22/16/15 masculine degrees (212/360 = 58.9% of the zodiac).
Not checked against the photograph itself — nothing in the engine reads it, and that check is
the OCR project's.

**In the engine:** nothing. `app.py:4285` lists the male/female DEGREES as a coverage gap, and the
VII.6 docstring at `:5202` repeats it (both updated in the wells pass to say the table now
exists). VII.6, 13 and 36 are the consumers: *"in their domains (I mean, that a male one is in a
male sign **or male degrees**, by day above the earth …)"* (13, fn. 223 → VII.1, 37–39) and
*"the male ones are in a female sign, **or in the female degrees** by day, under the earth …"*
(36, fn. 229). The engine evaluates both with signs only (`:885–909`), so today's condition 13 is
the *narrower* reading and 36 the narrower too.

---

## 2. V.20 — bright, dusky, empty and dark degrees (¶1–4; Figures 60–61, pp. 305–306)

**Doctrine.** *"In this scheme the degrees of the signs are in four classes: the first of them are
[1] the bright degrees, the second [2] the dusky degrees (and they are also said to be those
having a shadow, and smoky), the third are said to be [3] vacant (I mean, an empty void), and the
fourth are said to be [4] dark."* — V.20, 1. Effects: bright — *"more powerful for them in the
indication of the good, and they indicate brilliance, brightness, and good fortune"* (2); dark —
*"difficulty, what is detestable, and a gloomy, bad matter"* (3); dusky or vacant — *"a small
detestable thing"* (4). fn. 111: *"the [1] bright are the best, the [2] dusky and [3] vacant in the
middle, and the [4] the worst."*

**Figure 60** is the key (B/K/E/D ↔ Bright/Dusky/Empty/Dark with the Arabic terms), not a degree
table. fn. 110: *"See Figure 60 for their abbreviations and typical Arabic words."* **Figure 61**
is the sign-by-sign table, each cell a width plus a letter ("3K") with Dykes's cardinal range
beneath.

**Integrity:** nothing found. Figure 60's key parses to exactly four letters; in Figure 61 every
width equals its range, every row runs 0°–29° contiguously, no two adjacent bands share a
category. Zodiac coverage: Bright 183 (50.8%), Dusky 94 (26.1%), Dark 46 (12.8%), Empty 37
(10.3%). (Figure 61 was verified cell by cell against the p. 306 photograph in the OCR pass, per
`DOCTRINAL_CAVEATS.md`.)

**In the engine — matches.** `BRIGHTNESS_DEGREES` (`app.py:4410`) re-parsed from Figure 61 through
Figure 60's key is **identical in all twelve rows** (77 bands). Its comment *"Great Introduction
V.20, Figs. 60-61"* resolves: Fig. 60 supplies the category names the table uses, Fig. 61 the
bands, both now at Abū Ma'shar pp. 305–306 in `abu_mashar_book_vii.md` (Figure 60 moved out of
`sahl_introduction_ch3.md` on 2026-09-08; `01_sahl_introduction_ch3.md` §14 records it). Pinned
as `BRIGHTNESS_FIG61` in `tests/test_base_tables.py`. Consumers: condition 11 *"in the bright
degrees"* (`:5328`) and 35 *"in the dark degrees"* (`:5544`); the dusky/empty middle is
deliberately not voted (comment at `:5539–5542`), which follows VII.6's own silence about them —
V.20, 4's "small detestable thing" is Book V's, not VII.6's. Measured over 2,842 sampled
placements: Bright 50.5%, Dusky 26.1%, Dark 13.0%, Empty 10.5% — the same as the zodiac shares,
as expected for a static table.

---

## 3. V.21 — the wells (¶1–6; Figure 62, p. 308)

**Doctrine.** *"In the signs there are degrees called 'wells,' such that if one of the planets
occurred in those very degrees of the signs, without being powerful, the disappearance of its
brilliance will not be delayed, and its indication being very weak."* — V.21, 1. Fortunes there
*"like what we stated about weakness"*; infortunes *"their indication will be weakened (and
sometimes they will indicate incidental good fortune due to their inability to [create]
misfortune, and sometimes the nature of their misfortune will be strengthened)"* (2) — a hedge
both ways, recorded as such. ¶4 admits disagreement about the degrees and gives *"what the
generality of the old scholars of the people of Persia and Egypt agree on"*; fn. 114 sends the
delineations to *PN4* VIII.15 (not in the corpus). fn. 115: the table is Abū Ma'shar's ordinal
list with Dykes's cardinal column added.

**In the engine — matches after the wells pass.** `WELLED_DEGREES` (`app.py:4339`) equals Figure
62 in all 64 cells; the p. 308 photograph was checked cell by cell (`ea34231`). Consumers:
"Welled Degree" in Special Degrees (`:4385`), and Favor & Recompense (VII.5, 126–128, whose
fn. 203 is *"For the wells, see Ch. V.21"*). Coverage 64/360 = 17.8% of the zodiac; **17.4% of
sampled placements**.

**Integrity:** nothing further; the `DOCTRINAL_CAVEATS.md` correction (first rebuild wrong in two
cells, caught by the wells pass) is already recorded there.

---

## 4. V.22 — degrees increasing in good fortune (¶1–3, Figure 63) and of elevation and power (¶4–5, Figure 64), p. 309

**Doctrine A (Figure 63).** *"The ancients claimed that within the circle are degrees increasing in
good fortune, and they said that when planets indicate the native's good fortune by means of
their positions, and the Moon or the Lot of Fortune is in these degrees, or [these degrees] are
exactly on the Ascendant, then they will increase in the native's good fortune. And if they
indicate downfall, then these will instigate some motion towards high rank and power."* — V.22,
1–2. Applies to three points only (Moon, Lot of Fortune, Ascendant); an amplifier of a good
fortune already shown, and a consolation in the contrary case. Seven degrees: Taurus 15, 27, 30;
Leo 3, 5; Scorpio 7; Aquarius 20 — **7/360 = 1.9% of the zodiac.**

**Doctrine B (Figure 64).** *"if the Ascendant was one of these degrees which we will state
[below], or the Sun by day or the Moon by night was in one of them, and they were in an excellent
position of the circle, and the planets of the root of the nativity indicated good fortune, then
they will make him attain nobility and the houses of kings, and he will conquer lands and
cities, and possess many assets"* — V.22, 4. Applies to the Ascendant and the sect luminary,
under two further conditions the table cannot carry (an excellent place; a fortunate root).
Thirty-one degrees across all twelve signs (Cancer 1–3, 14–15; Capricorn 12–14, 20; …) — **31/360
= 8.6% of the zodiac.**

**Internal repetition and contradiction.** Leo 5 and Aquarius 20 are in **both** tables. Aquarius
17 is a degree of elevation (Fig. 64) *and* a well (Fig. 62) — the same degree weakens a planet
in V.21 and raises a luminary in V.22. Six of Fig. 63's seven degrees are Bright in Fig. 61
(Taurus 30 is Dusky); Fig. 64's are Bright 16, Dusky 8, Dark 5, Empty 2, i.e. the Fig. 61
distribution, no correlation. The text does not reconcile any of this; it presents four schemes
as the ancients' claims, and only V.21 speaks in Abū Ma'shar's own voice (*"we will state …"*).

**Integrity:** nothing found. Every ordinal matches its cardinal range in both tables, including
the three ranged entries (Cancer 1st–3rd, 14th–15th; Capricorn 12th–14th; Aquarius 16th–17th).

**In the engine:** nothing, and **no other text in the corpus cites either table** — Book VII's 74
conditions draw on V.19, V.20 and V.21 but never on V.22, and Sahl has nothing corresponding.
`03_changes.md` has no item for them.

**Frequency** (400 random charts, seed 20260908, plus the six fixtures; the doctrine's own points):

| Table | Test applied | Charts with any hit | Per point |
|---|---|---|---|
| Fig. 63 | Moon, Lot of Fortune or Ascendant in a listed degree | **7.6%** | Moon 2.5%, Fortune 2.2%, Asc 3.0% |
| Fig. 64 | Ascendant, or Sun by day / Moon by night, in a listed degree | **18.5%** | Asc 8.4%, Sun 6.2%, Moon 4.7% |

Fixture charts: Fig. 63 hits **none** on its three points (Mars sits at Taurus 30 on 1240-05-25,
but Mars is not one of them). Fig. 64 hits **one**: 1240-09-18, diurnal, Sun at Libra 3 (the
Moon at Cancer 14 on 1240-05-25 and Jupiter at Pisces 20 on 1240-01-04 are in listed degrees but
are not the sect luminary / Ascendant). A display-only flag would therefore add one row to one
fixture's Special Degrees table and change no `tables.json` structure.

---

## 5. The five items

| # | Chapter / figure | In the engine | Verdict |
|---|---|---|---|
| 1 | V.19 male & female degrees, Fig. 59 | absent | **⟨CHOICE⟩ N-1** — see §6 |
| 2 | V.20 brightness, Figs. 60–61 | `BRIGHTNESS_DEGREES` | **matches**: 12/12 rows identical to Fig. 61 via Fig. 60's key; citation resolves; pinned |
| 3 | V.21 wells, Fig. 62 | `WELLED_DEGREES` | **matches** after `wells-fix-2026-09-08`; pinned; photo-checked |
| 4 | V.22, 1–3 increasing in good fortune, Fig. 63 | absent | **⟨CHOICE⟩ N-2** — see §6 |
| 5 | V.22, 4–5 elevation and power, Fig. 64 | absent | **⟨CHOICE⟩ N-3** — see §6 |

No `BRIGHTNESS_DEGREES` error was found, so nothing here needs the bounds treatment.

---

## 6. New ⟨CHOICE⟩ items — three, none implemented

**N-1. Read the male/female degrees (Fig. 59) into VII.6 conditions 13 and 36?**
*Passage:* 13 *"a male one is in a male sign or male degrees"*; 36 *"in a female sign, or in the
female degrees"*; V.19, 8 on combining schemes; fn. 108 *"does not take a stance"*.
*Cost:* one table (12 rows, the shape of `BRIGHTNESS_DEGREES`) and an `or` in the two gender
tests at `:885` and `:900`; a sub-choice of scheme (the table alone, or ¶8's majority of three).
*What moves:* condition 13 (a Good Fortune vote) and the contrary-domain half of 36 fire on
the degree as well as the sign; since the table disagrees with the sign's gender on 51.7% of
degrees, "sign or degree" makes 13 satisfiable on far more placements than today. Māshā'allāh's
rule (*Nativities* 1.23, 17, the sidebar alternative) uses signs only and is untouched.
*Recommendation:* **no, leave as a coverage gap** (medium confidence). V.19 itself is topical
("a question about males/females"), VII.6 borrows it as an "or" without saying which scheme, and
Abū Ma'shar declines to choose; adding a table the author would not commit to widens a vote on
the engine's own initiative. If built, use the table only and label it Fig. 59.

**N-2. Flag the seven "degrees increasing in good fortune" (Fig. 63)?**
*Passage:* V.22, 1–2 above. *Cost:* one 4-row table and three membership tests (Moon, Fortune,
Ascendant) in `evaluate_special_degrees` or the Lots page; display only. *What moves:* a flag on
7.6% of charts; no fixture. *Recommendation:* **display-only flag, supplement-labelled, no
scoring** (low–medium confidence). It is cheap, it is Abū Ma'shar's own volume, and the
condition is self-contained; but no Sahl text and no VII.6 condition uses it, so under the
course-first policy it cannot enter any verdict. Deciding N-2 and N-3 together is natural.

**N-3. Flag the thirty-one "degrees of elevation and power" (Fig. 64)?**
*Passage:* V.22, 4 above. *Cost:* one 12-row table and two membership tests (Ascendant, sect
luminary); display only. *What moves:* a flag on 18.5% of charts (one fixture, 1240-09-18, Sun
at Libra 3); the two textual preconditions ("an excellent position", "the root … indicated good
fortune") cannot be tabulated and would have to be shown as caveats. Aquarius 17 would carry
both "Welled Degree" and "elevation" on the same row. *Recommendation:* **same as N-2, or
neither** (low–medium confidence). Weaker than N-2 because the promise is conditional on two
judgements the engine does not make, and because of the well collision.

**Count for the decision document: 3 new items.** None affects the suite; none is on
`03_changes.md`. The wells question (`13_open_decisions.md` D-10, "shoot GI V.21") is closed by
this capture and can be struck.

---

## 7. What this pass did not do

- No `app.py` change, no test change (`1024 passed, 2 xfailed` on `main`; `1038 passed, 2 xfailed`
  on the wells branch this sits on).
- Figures 59, 63, 64 were checked internally and against each other, not against the
  photographs.
- Firmicus *Mathesis* IV.23 and Valens *Anth.* I.11, both named by the footnotes, are not in the
  corpus; the "very similar" claim of fn. 109 is unverified.
- *PN4* VIII.15 (fn. 114, well delineations) belongs to the Persian Nativities IV OCR
  sub-project.

Method: `scratchpad/bookv_check.py` parses all six figures from the corpus file, runs the
integrity checks, compares Figure 61 to the engine namespace, and samples the charts;
`bookv_fix.py` re-runs the six fixtures under the harness convention (Florence, 14:30 LMT).
