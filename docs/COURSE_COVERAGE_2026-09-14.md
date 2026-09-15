# Course → app coverage, 2026-09-14 (restated 2026-09-15)

The reverse of the citation check: every table in *TNAC Handy Tables from Part 1* (Lessons
5–20, in hand since 2026-09-13) and the *Reference Guide* (in hand since 2026-09-12), asked
whether the app carries it. A gap list, not a build list: the canon-only rule stands, and the
page-text rule (no course citations on pages) means anything built from these is cited to the
corpus text behind it, or carried as a supplement row with the Handy Tables as sole witness in
the docs only. Method: keyword search of `app.py` per table, then reading the hits;
`NOT_IMPLEMENTED_COVERAGE` consulted for what is already declared unbuilt.

**Restated 2026-09-15** against what merged on 2026-09-14/15 (PRs #15–#22) and what the four
syntheses found (`docs/synthesis/02_reconciliation_pn_ita.md`, reconciliation 3.4 / decision 20).
The 2026-09-14 version's header said the texts behind gaps 6–12 were "not in the corpus"; ITA
(al-Qabīsī and the Abbreviation, 32 photographed pages and a provisional OCR), Firmicus
*Mathesis* III.7, Morin *Astrologia Gallica* 21.II.X, Rhetorius and the four nativity treatises of
*Persian Nativities* I–II are in the corpus now, and seven of the gaps below are built (1, 2, 3,
5, 6, 7, 8); the numbering is new, the Mars row of the old gap 10 moved up on its witness.

## Carried (no action)

Dignities (domicile, exaltation with the standard degrees, Dorothean triplicities, Egyptian
bounds, faces); planetary periods (lesser/middle/greater/mighty) and average daily speeds; the
28 fixed stars with Rhetorius Ch. 58's natures and the cutting stars of IX.8, 32-50; sect and
its per-planet conditions; advancing/withdrawing (Sahl 83, dynamic); aversion, the lord in
aversion to its sign; solar phase (eastern/western, under the rays, in the heart, the stations);
retrogradation; Sahl's strengths and weaknesses (Intr. Ch. 3, 77-112, the switch matrix); the
ten defects of the Moon; the configurations (assembly, looking, connection, transfer,
collection, reflection, returning, reception) and the prevented connections; orbs; the four
medieval categories; the Lots of Fortune, Spirit, Eros (as `desire`), Necessity, Courage,
father (both forms), mother, children, marriage (Hermes, both), friends, action; triplicity
lords of the sect light and the Ascendant where Sahl uses them; the joys; the weighted victors
(both methods), ibn Ezra's two, Hermann's/Masha'allah's; lords of the day and hour; the
Reference Guide's per-place delineation tables; the wells and Book V's degree tables.

Hermes's exaltation degrees (Handy Tables p. 1): the "Hermes" column is Gr. Intr. Figure 39
read as cardinal degrees; the app's note on Figure 38/39 already says how the two differ.
Nothing to add.

## Gaps with a corpus text behind them

1. **Stars harming eyesight** — Sahl, On Nativities 6.2, 48-75 and Gr. Intr. VI.20. **Built
   2026-09-14 (PR #20)**: `EYESIGHT_PLACES`, `evaluate_eyesight_places()`, a display-only finding
   at the supplement depth; the four lists and Abū Ma'shar's carried apart, never reconciled.
   Still open behind it: a second eye-degree list, Abū Bakr II.7.3 (= Māshā'allāh's, BA III.6.2)
   and Hugo's own variants — decision 14 of the reconciliation, a second column after the marker
   OCR, two lists never merged.
2. **The Lots of Jupiter and Saturn** (the Handy Tables' Victory and Nemesis) — Gr. Intr.
   VIII.3, 37-41 and VIII.6, 13-14. **Built 2026-09-14 (PR #15)**: `jupiter_prosperity` and
   `saturn_burdensome` in `LOT_DEFINITIONS`, supplement rows; the names Victory and Nemesis are
   ITA VI.1.7–8's section headings, cited on the rows since 2026-09-15.
3. **The Moon's phases with their lords** (Handy Tables p. 26, "adapted from Anth. II.36 and
   Gr. Intr. VII.2"). **Built 2026-09-14 (PR #17)** as Valens's eleven phases, `VALENS_MOON_PHASES`,
   display only, Riley's text for the meanings; the 12° boundaries Valens does not give are Abū
   Ma'shar's markers of the Moon's phases (Abbr. II.27–31, ITA II.10.5), said so since 2026-09-15.
   The Handy Tables' twelve-phase version is not what was built; Valens is.
4. **Eminence from the fixed stars** (Sahl 2.2's own judgment) and **the advancing/withdrawing
   quadrants** (VII.3, 2 / VI.26, 3) — declared in `NOT_IMPLEMENTED_COVERAGE`; listed here
   because the course teaches both (Lesson 6; Lesson 13). Not built.
5. **Ptolemy's planetary elemental powers** (hot/cold/wet/dry per planet, Handy Tables p. 8) —
   Gr. Intr. IV.1. **Built 2026-09-14 (PR #19)**: `PLANET_NATURES_IV1`, a supplement table on the
   Reference page; nothing computes with it.
6. **Morin's rules for aspects into good and bad places** (Lesson 14) — Morin, *Astrologia
   Gallica* 21.II.X, OCR'd 2026-09-14. **Built 2026-09-14 (PR #18)**: `MORIN_ASPECT_RULES`,
   display only. The unfortunate houses Morin never lists; 6, 8 and 12 are the app's equation
   with his phrase, the three being the tradition's difficult averse places (ITA IV.4.1 fn 43,
   p. 224, photographed), cited since 2026-09-15.
7. **Al-Andarzaghar's triplicity lords by place** (the 12 × 3 table, al-Qabīsī I.57b-68 in ITA
   I.13, pp. 71-76, photographed). **Built 2026-09-15 (PR #21)**: `ANDARZAGHAR_TRIPLICITY_LORDS`,
   display only, under the supplement depth on the Timing page. The sect order of
   first/second/third is al-Qabīsī's own (I.16, ITA I.7; Gr. Intr. V.14, 6; Sahl 10.2.7, 16),
   said so since 2026-09-15. The "typical significators and their triplicity lords" list is not
   built.
8. **Mercury's sect-and-phase phrases** (Mathesis III.7) — **built 2026-09-14 (PR #16, `8f96202`;
   `MERCURY_PHASE_SECT_READING`, display only, Dykes's fn 186/194 phrases)**. The sect a morning
   star takes is Abū Ma'shar's rule too (Gr. Intr. IV.9 in ITA V.11), cited since 2026-09-15.
9. **The per-planet of/contrary-to-sect delineations of Lesson 10 (Rhetorius, Abū Bakr)** — one
   row has a corpus witness: Abū Bakr II.1.0 (PN II, PDF p. 168; OCR, unverified) gives the Mars
   row with the condition *in his domicile, by sect of chart* — by night "a good soldier", by day
   "lazy in those things in which he ought to make money" — not "contrary to sect" at large.
   Decision 13: a supplement row after the marker OCR of PN II. The other rows stay in the
   section below.
10. **Antiochus's bonification and maltreatment** (five conditions each, p. 29). The switch
    matrix has "overcome"; the five-fold scheme is not there. Rhetorius is in the corpus now;
    Antiochus's own text is not, and ITA III.28's bodyguarding (pp. 206-216, photographed) is the
    nearest corpus witness — a different doctrine. Not built.
11. **Ptolemy's stars of unusual sexuality** (Tet. IV.5), the fifteen first-magnitude stars of
    the Almagest with their categories, and the "stars harming eyes" rows that are Carmen's or
    Rhetorius's rather than Sahl's/Abū Ma'shar's. The Almagest is in the corpus; the Tetrabiblos
    is not. Not built.

## Gaps whose only witness in hand is the Handy Tables

12. **The eastern/western quadrants by gender and age** (Figure 1, Lesson 16) — the app has the
    masculine quadrants from Figure 90; the age reading is not there, and no corpus text states
    it.
13. **Lesson 10's rows other than Mars** (Rhetorius's and Abū Bakr's of/contrary-to-sect
    delineations) — Rhetorius's text is in the corpus but the per-planet rows are the course's
    digest; Abū Bakr II.1.0 witnesses only the Mars row (gap 9). Building the rest would make the
    course summary the whole authority.
14. Keyword tables (elements and principles, planetary conditions and functional values,
    the special meanings of fall, dignity analogies, eastern/western, retrogradation,
    configuration vs aversion): teaching prose, not computable; nothing to build, and the
    page-text rule keeps them off the pages.

## What the syntheses added to the list (not course tables; recorded, not gaps of the course)

From `02_reconciliation_pn_ita.md` Class 1, the items with a text in hand that the course does
not teach, each waiting on the canon rule or on a build decision: al-Qabīsī's proportional
semi-arcs (decision 5, a build order; the relabel is done), his whole releaser procedure (in
`NOT_IMPLEMENTED_COVERAGE` and `16_open_features.md` F-6 since 2026-09-15), 'Umar's 30° profection
(`16_open_features.md` F-5), the JN/TBN years ladder for the "1.20 silent" cells (decision 9), the
prosperity classifier (decision 11), the Moon on the third day and gestation (decision 18).

## Not gaps

The Reference Guide's "Planets in the Nth" and "lords of other places in the Nth" tables are
the app's two delineation tables (`tests/test_prose_tables.py`); `VICTOR_WEIGHTS` matches p. 33
verbatim (course README, 2026-09-13) — its "older" label kept as printed with a note citing
Abū Bakr II.5.14 and al-Qabīsī I.22 (PR #23, owner's ruling 2026-09-15).
