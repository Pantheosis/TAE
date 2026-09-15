# Course → app coverage, 2026-09-14

The reverse of the citation check: every table in *TNAC Handy Tables from Part 1* (Lessons
5–20, in hand since 2026-09-13) and the *Reference Guide* (in hand since 2026-09-12), asked
whether the app carries it. A gap list, not a build list: the canon-only rule stands, and the
page-text rule (no course citations on pages) means anything built from these would be cited to
the corpus text behind it, or carried as a supplement row with the Handy Tables as sole witness
in the docs only. Method: keyword search of `app.py` per table, then reading the hits;
`NOT_IMPLEMENTED_COVERAGE` consulted for what is already declared unbuilt.

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

## Gaps with a corpus text behind them (buildable under the canon rule)

1. **Stars harming eyesight** — Sahl, On Nativities 6.2, 48-75 and Gr. Intr. VI.20 (both
   transcribed). Not built; no mention in `app.py`.
2. **The Lots of Jupiter and Saturn** (the Handy Tables' Victory and Nemesis) — Gr. Intr.
   VIII.3, 37-41 and VIII.6, 7-14 give all seven planetary Lots; the app carries Fortune,
   Spirit, Venus (Eros), Mercury (Necessity) and Mars (Courage), not Jupiter's or Saturn's.
3. **The Moon's twelve phases with their lords** (Handy Tables p. 26, "adapted from Anth.
   II.36 and Gr. Intr. VII.2") — the app reads VII.2's conditions for the solar phase but
   carries no phase-by-phase delineation. VII.2 supplies the phases; the lords and meanings
   are Valens's (not in hand) — a partial, Handy Tables sole witness for the meanings.
4. **Eminence from the fixed stars** (Sahl 2.2's own judgment) and **the advancing/withdrawing
   quadrants** (VII.3, 2 / VI.26, 3) — already declared in `NOT_IMPLEMENTED_COVERAGE`; listed
   here because the course teaches both (Lesson 6; Lesson 13).
5. **Ptolemy's planetary elemental powers** (hot/cold/wet/dry per planet, Handy Tables p. 8) —
   Gr. Intr. IV.1 ("according to what Ptolemy said") is transcribed. No planet-nature table in
   the app.

## Gaps whose only witness in hand is the Handy Tables

Source texts not in the corpus (Morin, Antiochus, Firmicus, Rhetorius, Ptolemy's
*Tetrabiblos*, al-Qabisi/ITA, Lehman). Building any of these means the course summary is the
whole authority, as it already is for the Reference Guide's Rhetorius/Firmicus columns.

6. **Antiochus's bonification and maltreatment** (five conditions each, p. 29). The switch
   matrix has "overcome"; the five-fold scheme is not there.
7. **Morin's rules for aspects into good and bad places** (Lesson 14).
8. **The fortune/infortune × place × sect guide** (Lesson 12's twelve-row table).
9. **Al-Andarzaghar's triplicity lords by place** (the 12 × 3 table, from al-Qabisi I.57-68)
   and the "typical significators and their triplicity lords" list. The app applies triplicity
   lords only where Sahl does (life, the lords of the triplicity over the life).
10. **Mercury's sect-and-phase phrases** (Mathesis III.7) and the per-planet of/contrary-to-sect
    delineations of Lesson 10 (Rhetorius, Abu Bakr).
11. **Ptolemy's stars of unusual sexuality** (Tet. IV.5), the fifteen first-magnitude stars of
    the Almagest with their categories, and the "stars harming eyes" rows that are Carmen's or
    Rhetorius's rather than Sahl's/Abu Ma'shar's.
12. **The eastern/western quadrants by gender and age** (Figure 1, Lesson 16) — the app has the
    masculine quadrants from Figure 90; the age reading is not there.
13. Keyword tables (elements and principles, planetary conditions and functional values,
    the special meanings of fall, dignity analogies, eastern/western, retrogradation,
    configuration vs aversion): teaching prose, not computable; nothing to build, and the
    page-text rule keeps them off the pages.

## Not gaps

The Reference Guide's "Planets in the Nth" and "lords of other places in the Nth" tables are
the app's two delineation tables (`tests/test_prose_tables.py`); `VICTOR_WEIGHTS` matches p. 33
verbatim (course README, 2026-09-13).
