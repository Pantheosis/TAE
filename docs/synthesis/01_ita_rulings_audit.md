# ITA against the rulings and the app's declared readings (2026-09-15)

An audit, not a book read. Every ruling in `process/astra_2026-09-11/*_ruling.md` and `*_order.md`, the
owner's rulings logged in `docs/ASTRA_BUILD_2026-09-11.md`, and every reading `app.py` declares as its own,
set against what Dykes prints in *Introductions to Traditional Astrology* (2010): Abū Ma'shar's
*Abbreviation* (Abbr.), al-Qabīsī's *Introduction*, the *Gr. Intr.* excerpts (John of Spain's Latin, so
they can differ from the 2020 Arabic-based volume the app cites), the other texts he quotes (BA, BW,
Carmen, Sahl's *Judgments*), his footnotes and his comments.

Source: `ita/introductions_to_traditional_astrology_PROVISIONAL.md` — unread marker OCR, cited by section
and printed page. Every quotation below is **(OCR, unverified)** and kept to a clause; the page is the
authority, and the 32 photographed pages (`ita_photographed.md`: 71-76, 112-123, 206-208, 213-216,
224-229, 395) are the second witness where they overlap. Read whole: the TOC, the Introduction, Books
I-IV. Read for the rulings: V.9-14, VI.1-2, VII.1-4, VII.7-10, VIII.1-4, the Glossary, Appendices E-F.

Verdicts: CONFIRMS / CONTRADICTS / QUALIFIES / SILENT. "Owner's call" marks what is a ruling, not a
correction.

## A. The rulings, one entry each

### 1.15 readings (`1.15_readings_ruling.md`)

**1. The sect-specific candidate order; 1.15, 15 a collective fallback, not a universal all-five procedure**
(ruling Q1; `app.py` Releaser tab caption (7)).
ITA VIII.1.3, al-Qabīsī IV.4, pp. 353-354: by day "you will begin from the Sun" and, the Sun failing, "Then
you will look at the Moon"; by night "we begin from the Moon" and, she failing, "you will look after this
to the Sun"; then the conjunction or prevention degree, then Fortune, then the Ascendant (OCR, unverified).
Verdict: QUALIFIES. Al-Qabīsī's procedure consults BOTH luminaries in either sect before the syzygy — the
"other sect's candidate" the ruling declined to read into Sahl. A different author, not Sahl's text; the
ruling stands for Sahl. Change: none required; the caption's "read as a procedure it would consult the
other sect's candidates" now has a named ancient procedure that does exactly that. Owner's call whether to
name it.

**2. "In good places" (1.15, 16) = the seven praised places {1,4,5,7,9,10,11}, an interpretation**
(ruling Q2; `SAHL_GOOD_PLACES`, `app.py` 9265).
ITA III.4 comment, p. 121: Sahl "explicitly uses the seven-place arrangement of Timaeus and Dorotheus in
his Introduct. §4", where the seven "are more 'praiseworthy' and 'stronger'" (OCR, unverified);
Introduction §6, p. 18: Dorotheus calls the seven-place version "good" and "strong" (Carmen I.5). Also
Judgments 41 quoted at I.8, p. 49: "in a good place from the Ascendant, or in the Midheaven or in the
eleventh".
Verdict: CONFIRMS. Dykes himself ties "good" to the seven-place scheme. Change: the page can cite ITA
pp. 18 and 121 beside fn 372 instead of calling the identification the app's alone.

### 1.7 governor (`1.7_governor_independent_ruling.md`, `1.7_governor_ruling.md`)

**3. The Sun's solar side is not applicable; he is neither preferred nor set aside by 1.7, 3.**
ITA II.8-II.10 (pp. 93-108): right/left and eastern/western are defined for the five planets and the Moon
relative to the Sun; nothing is said of the Sun's own side.
Verdict: SILENT (confirms by omission). No change.

**4. The Moon's side by the rising-before-the-Sun rule (waning = eastern), declared.**
ITA II.8, Abbr. II.16 / Gr. Intr. VII.2.151-54, p. 94: the Moon from conjunction to opposition is "left",
after the opposition "right"; II.10.1, al-Qabīsī III.8a, p. 98: the superiors from the rays to the
opposition "are called 'eastern' and 'right'" (OCR, unverified).
Verdict: QUALIFIES (supports). The bridge the row said no text gives — right = eastern — al-Qabīsī states
for the superiors; the Moon's "right" half (opposition to conjunction) is the waning, rising-before half
the app calls eastern. Change: cite al-Qabīsī III.8a on the row's Moon note. Not a ruling.

**5. 1.7, 7 scored as a comparison without a scale; 4's "stronger in its own place" and 5-6 unmodelled;
1.20's ranking not imported.**
ITA VIII.1.3, al-Qabīsī IV.5, p. 356, on the kadukhudhāh: equal claimants that all aspect — "the one which
was stronger in [its own] place will be more worthy"; equal there — "the one which was closer to the degree
of the releaser" (OCR, unverified). IV.6: "changed more quickly from its own being to one which was better"
(cf. Sahl 1.7, 6).
Verdict: QUALIFIES. Al-Qabīsī's kadukhudhāh tie-breaks run in Sahl's 1.7 order (own-place strength, then
speed of bettering) and add one the app lacks: nearest the degree. A different technique of a different
author. Owner's call whether the governor row may borrow the nearest-degree tie-break as a declared
parallel; otherwise name it in `SAHL_1_7_UNMODELLED`'s note.

**6. The stakes for 1.7, 7 by the division (canon), with the notation that the text's word is the counted
sign** (`1.7_governor_ruling.md`, "The stakes").
ITA I.12 fn 149, p. 68: Greek and Arabic writers "called the signs and the regions measured from the axial
degrees by the same name" without always clarifying; III.4 fn 32, p. 122: "The texts here are ambiguous as
to whether angles by whole sign or quadrant-based divisions are meant" (OCR, unverified).
Verdict: CONFIRMS the notation (the ambiguity is Dykes's own statement). Change: cite fn 149 / fn 32 on
the row.

**7. The moment: every condition read in the natal chart, extending Dykes's comment.**
Verdict: SILENT. ITA's al-Qabīsī IV.3 (the namūdār, p. 352) reads the syzygy's victor "at that same hour
of the conjunction or the prevention" and then "calculate[s] that planet for the hour of the nativity" — a
different technique; no bearing on 1.7. No change.

### DEC-D-3 (`DEC-D-3_ruling.md`)

**8. The natal grant from 1.20, 7-34; On Times 4 a question-chart rule.**
Verdict: SILENT. ITA VIII.1.3 al-Qabīsī IV.5 selects the kadukhudhāh and gives no years; On Times is not
in ITA. No change.

**9. The planetary years table (`PLANETARY_YEARS`, `app.py` 8530): the luminaries' middle years 39½.**
ITA VII.2, Gr. Intr. VII.8.1365-80, Figure 108, p. 332 (the Latin): Sun "19 | 69½ | 120 | 1,461", Moon "25
| 66½ | 108 | 520" (OCR, unverified; figures that are tables are the least trustworthy OCR).
Verdict: CONTRADICTS the two cells (a fourth witness against 39½, after the memory's "contested a third
time"). The app's comment says the halved-great construction "must not be corrected"; ITA's Latin figure
is the ordinary mean. Change: a note on the Reference page's years table naming the Latin Gr. Intr.'s
69½/66½ beside the 2020 volume's 39½ — after the page is read against the scan. Owner's call.

### DEC-D-11 (`DEC-D-11_ruling.md`)

**10. The Lot of death from the Moon to the eighth, cast from Saturn; the eighth "by equation" = the
quadrant cusp** (`LOT_DEFINITIONS` death row, `app.py` 5263).
ITA VI.2.27, pp. 308-309: Abbr. VI.36 "from the Moon up to the eighth sign from the horoscope", Saturn's
degrees added, counted "from the first degree of the sign in which Saturn was"; Gr. Intr. VIII.4.1098-1106
(Latin) "to the degree of the eighth house by equal degrees ... projected from the beginning of that same
sign" (Saturn's); al-Qabīsī V.11a "to the degree and minute of the eighth house ... from the beginning of
Saturn's sign" (OCR, unverified).
Verdict: CONFIRMS Saturn (three more witnesses; none reads the Ascendant). QUALIFIES the cusp: the Latin
has "by equal degrees" where the Arabic-based volume has "by equation"; Adelard has "the eighth sign";
al-Qabīsī's "degree and minute" is a computed cusp (he uses quadrant houses, VIII.1.3 fn 17). Change: add
the three witnesses to the row's standing, with the Latin/Arabic difference named. Not a ruling.

### DIS-12 (`DIS-12_ruling.md`)

**11. 2.13, 48-51 as the sect light's first triplicity lord by ascensional band; the every-planet display
is the app's generalisation** (`app.py` 14718).
ITA Introduction §6, pp. 17-19: Dykes reads Carmen I.7.7-8's 15° as the Antiochus/Porphyry rule that a
planet in the second sign within 15° of the Ascendant is "co-busy" — a general chart-support consideration
for any planet, which the Arabic Dorotheus "links ... to a specific topic: life" and, past 15°, to "no
upbringing" — "what the text should (and probably did) read is that such a planet cannot be considered
'jointly busy'" (OCR, unverified). He measures "up to 15° from the axes" (p. 17) and says nothing of
ascensions.
Verdict: QUALIFIES. Dykes's own reading of the source rule is that it applied to any planet as a busyness
upgrade — support for the display's generalisation, against the topical restriction the ruling preserved;
silent on the ascensional unit (fn 57 to Aphorism 45 stands alone for that). Change: the display could cite
ITA pp. 17-19 as the warrant for showing every planet. Owner's call.

### REL-1 (`REL-1_ruling.md`)

**12. Selection by 1.15, ranking by 1.20, direction of the house-master under 1.23 — a declared join.**
ITA VIII.1.3, al-Qabīsī IV.4-5, pp. 353-356: the releaser first, then its kadukhudhāh from "the Lord of the
domicile of the releaser, or ... its exaltation or ... bound or ... triplicity or ... face", the one
"stronger and more authoritative in the place of the releaser, and aspected the releaser"; VIII.2.2f, p.
366: the points directed are the Ascendant, Sun, Moon, Fortune, Midheaven; fn 50, p. 366: Māshā'allāh
"prefer[s] the releaser for longevity"; Glossary p. 385: kadukhudhāh "preferably the bound Lord".
Verdict: QUALIFIES. The releaser-then-house-master sequence is al-Qabīsī's own procedure (support for the
join as standard), but he directs the releaser, not the house-master. No change; the Releaser tab may cite
IV.4-5 as a second author's shape of the technique.

**13. PN IV IX.8, 32 read as a role restriction, not a prohibition.**
Verdict: SILENT.

**14. 1.20, 2's ranking bound, house, exaltation, triplicity, face** (`SAHL_DIGNITY_RANK`, `app.py` 9256).
ITA VIII.1.3, al-Qabīsī IV.5, p. 356: some began from the domicile lord in order to the face; "Dorotheus
used to put the Lord of the bound before the Lord of the domicile"; fn 21: Carmen III.2.5-6, "the preferred
and older approach" (OCR, unverified).
Verdict: CONFIRMS Sahl's bound-first order as Dorothean, and names the domicile-first order and
al-Qabīsī's own "more authoritative" (weighted) order as the alternatives. Change: cite fn 21 on the row.

### REL-2-1 (`REL-2-1_ruling.md`, `REL-2-1_phase2_ruling.md`; decision-sheet row 3)

**15. 1.15's places classified by whole sign; the Lot of Fortune candidate by whole-sign place; the
meeting/fullness degrees by division, declared open.**
ITA VIII.1.3, al-Qabīsī IV.4, p. 355: "you will look for the releaser in the angles and in their followers
according to how the twelve houses of the circle are calculated through the degrees of the hours of the
Ascendant" — fn 17: "Al-Qabīsī is telling us to use quadrant-style houses (such as Porphyry or Alchabitius
Semi-Arc) for this longevity method" — and the conjunction, prevention and Fortune "fit ... only ... in
these eight places" so calculated (OCR, unverified).
Verdict: QUALIFIES. A second author's releaser procedure puts every candidate, the Lot included, in
quadrant houses; the ruling's whole-sign base for Sahl is unaffected but no longer the only ancient
practice in hand. Change: name al-Qabīsī IV.4 on the Releaser tab as the quadrant witness (the tab now
rests the division on the course). Owner's call whether the Lot-by-whole-sign change of row 3 is revisited.

**16. Sahl's day places for the Sun (1, 10, 11, 7, 8)** (`SAHL_RELEASER_DAY_PLACES`).
ITA VIII.1.3, al-Qabīsī IV.4, p. 353: the Sun fit by day within 5° before the Ascendant, in the tenth or
eleventh "whether that sign were masculine or feminine", and "in the seventh or in the eighth or in the
ninth in a masculine sign" — eleven places in all with the night list (p. 355); the Moon likewise with
sign-gender conditions; "if the Moon were under the rays of the Sun in these places, she will not be fit".
Verdict: QUALIFIES. Al-Qabīsī admits the ninth (masculine) and gates by sign gender and the Moon's rays,
none of which Sahl 1.15 has. A variant, not a defect. Change: none; a coverage note.

### The canon (`OWNER_RULING_PLACES_VS_DYNAMICS_2026-09-11.md` as applied in the build log)

**17. The five-degree carry-over at the four axial degrees only; 1.18, 19's "likewise in all of the houses"
read as the four stakes (the course's reading, Lesson 3)** (`get_effective_house`, `app.py` 4524-4560;
Releaser tab note restored a9c8314).
ITA VIII.1.3, al-Qabīsī IV.4, p. 355: "every planet which was before the degree of the Ascendant or any
house by five equal degrees and less, its strength will be valid in the house which follows it" (OCR,
unverified). Introduction §6, p. 12: "planets within 5° prior to a house cusp will be considered to have
topical significance for that house" — Ptolemy's recommendation, adopted by "many traditional
astrologers"; the quadrant figure p. 14 applies it to the first cusp. I.12, BA I.4 quoted p. 70: some
attribute "the 5° [above] its arising" to the Ascendant.
Verdict: CONTRADICTS the axial-only reading as a general doctrine: al-Qabīsī states the rule for "any
house", in the releaser procedure, as Sahl 1.18, 19 does; Dykes attributes the all-cusps form to Ptolemy.
For Sahl's three sentences the ruling is still a reading; it now has a contrary witness in hand. Change:
the retired `five_degree_all_cusps` form returns as a declared alternative at least where the releaser is
sought, or the note says al-Qabīsī IV.4 reads "all of the houses" literally. Owner's call.

**18. The five degrees measured in ecliptic longitude "by choice" (Dykes's Aphorism 44 note says diurnal
motion)** (`get_effective_house` docstring).
ITA VIII.1.3, al-Qabīsī IV.4, p. 355: "by five equal degrees and less" — equal (zodiacal) degrees, the
term Gr. Intr. uses for ecliptic measure (VI.1.1 fn 2, p. 281: "zodiacal or ecliptical degrees").
Verdict: CONFIRMS the longitude measure as a text's own unit (al-Qabīsī's, not Sahl's). Change: the
docstring's "proxy named as one" can cite al-Qabīsī's "equal degrees".

**19. Strength language → the Alcabitius division with the axial 5°; topic language → the whole sign; the
Alcabitius and the axial five degrees "the course's"** (Releaser tab; `app.py` 14985 "this app's
convention for strength language").
ITA Introduction §6, pp. 15-20: the four ambiguous concepts (stake, busy/advancing, strong, topic); Dykes's
"possible solution": "(1) adopt whole signs for topics; ... (3) apply Nechepso's eight-place scheme to
quadrant-based dynamical divisions, to assess planets' overall activeness and engagement" (OCR,
unverified); p. 16: "al-Qabīsī definitely uses quadrant houses"; I.12 fn 154, p. 70: al-Qabīsī "obviously
favors a quadrant-house division"; VIII.1.3 fn 17: "such as Porphyry or Alchabitius Semi-Arc".
Verdict: CONFIRMS the dispatch as Dykes's own published proposal; QUALIFIES the system: no text in ITA
names Alchabitius as required, and Dykes's own reconstruction offers Carmen's 15° regions as the
alternative measure (p. 18). Change: cite ITA Introduction §6 for the dispatch where the pages now say
"this app's convention" or cite the course; keep Alchabitius as the app's choice among quadrant systems.

**20. GAP-31: IX.9, 13's "in a stake or what follows a stake" by the divisions, an adopted
dynamic-fitness reading** (build log, 47cc309).
ITA IV.2, pp. 219-220: power is being "in a firm sign or one next to it" (Abbr. IV.4-7, Adelard) / "in an
angle or in one following an angle" (Gr. Intr. VII.6.1182-91; al-Qabīsī III.27); III.3 fn 18, p. 118: "The
Ar. does not specify these as signs, but simply as the 'stakes' and 'what comes after them'" (OCR,
unverified).
Verdict: QUALIFIES. The same phrase in Abū Ma'shar's own power condition is sign-language in the Latin and
unit-less in the Arabic; Dykes leaves it open (fn 32). The "qualified" confidence is right. No change.

**21. GAP-37 (e): planets not on an axis "Requires proportional semi-arcs; calculation unavailable"; (f)
authorised as an OUTSIDE-CORPUS import, "Ptolemy's method as Dykes identifies it ... the formula is stated
in no text in hand"** (`PN4_SEMIARCS_UNAVAILABLE`, `PN4_ASCENSION_RULE`; build log c71be46 and the "Left
for the next order" paragraph).
ITA VIII.2.2b-e, al-Qabīsī IV.11c-12c, pp. 362-364: the significator's "hours of the distance from the
angle" (meridian distance divided by the hour-parts of its degree), the "significator of the right circle"
(RA difference), the "significator of the region" (OA difference), "one-sixth of [the difference] ...
multiply it by the hours of the distance from the angle: ... the 'equation'", added or subtracted; VIII.2.2e
directions across quarters; Appendix E, pp. 402-407: "PromMD − [(SigMD/SigSA) × PromSA] = Arc", worked
with and without latitude, "Al-Qabīsī's method is essentially the same as this" (OCR, unverified).
Verdict: CONTRADICTS the label. The proportional semi-arc method is stated, in full, by a primary author
now in hand (al-Qabīsī) and restated by Dykes with a worked example; (f) is no longer an outside-corpus
import. Change: `PN4_ASCENSION_RULE`'s third string ("the formula stated in no text in hand") → "stated by
al-Qabīsī (ITA VIII.2.2) and worked by Dykes (Appendix E)"; when (f) is built, the readings it must declare
(body vs ecliptic, i.e. with or without latitude) are the two cases Appendix E works. Building (f) stays
the owner's call; the label is a correction.

**22. PN4R-4n-5: the revolution wheel keeps Dykes's whole signs (fn 33) though I.6, 2 asks for houses by
degree** (build log 2026-09-13, "No change to the drawing (owner)").
ITA VIII.2.1, al-Qabīsī IV.8 + fn 30, p. 358: profection "in such a degree as it was in the Ascendant of
the nativity" — "al-Qabīsī uses 30° increments in his profections instead of whole-signs"; the 12 1/6 days
per degree rule (pp. 359-360) (OCR, unverified).
Verdict: QUALIFIES (a variant witness for degree-based profection with a timing rule the app lacks).
Owner's call already made for the drawing; the timing rule is a coverage item (§C).

### DELIN-TABLES (`DELIN-TABLES_order.md`)

**23. The Masha'allah "lords of places in places" table to be re-derived from Sahl's chapters; the
Rhetorius column not in hand.**
ITA I.15, al-Qabīsī I.73-76, pp. 77-79: the lords of the four angles in each of the four angles — sixteen
cells ("The presence of the Lord of the Ascendant in the Ascendant signifies his fortune ... through
himself"; the lord of the tenth in the seventh, "victory in contentions and from the purposes of wives";
etc.) — "we have only introduced the Lords of the angles because they are an example for the rest"; I.14,
al-Qabīsī I.71-72: house meanings by angularity (OCR, unverified).
Verdict: QUALIFIES. A text in hand for 16 of the 144 cells and for the angular/succedent/cadent
delineation the Guide's "Planets in the Nth" column compresses. Change: the order's step 1 may cite
al-Qabīsī I.73-76 where its cells coincide with Sahl's. Owner's call.

### LOT-BASIS (`LOT-BASIS_order.md`)

**24. Basis = Fortune → Spirit by day, reversed by night, from the Ascendant; coincides with the Lot of
Venus/passion** (`LOT_DEFINITIONS` basis row, `app.py` 5130).
ITA VI.1.4 "The Lot of Basis", pp. 285-286: Abbr. VI.7; Gr. Intr. VIII.3.560-78 "taken in the day from the
Lot of Fortune to the Lot of the Absent, and conversely in the night ... And this Lot matches the Lot of
Venus"; al-Qabīsī V.4f "is just like the Lot of esteem and concord" (OCR, unverified).
Verdict: CONFIRMS, and Dykes's section heading is the name the row lacks a source for. Change: cite ITA
VI.1.4 for the name "Basis" (the row cites fn 67's gloss).

### Rulings logged in `docs/ASTRA_BUILD_2026-09-11.md`

**25. The victor weights' "Older (al-Tabari/Masha'allah)" label kept; "the bound-3 order has no witness
here"** (5b01442; `VICTOR_WEIGHTS` comment and the Victors page note).
ITA I.18, al-Qabīsī I.22, p. 81: "the Lord of a domicile has five strengths, and the Lord of the exaltation
four, and the Lord of the triplicity three, and the Lord of the bound two, and the Lord of the face one.
And certain people put the bound before the triplicity"; fn 207 → VII.4; VII.4, al-Qabīsī I.19b, p. 334:
"certain people put the triplicities before the bounds, because the Lords of the triplicities are stronger
in nourishment, and the Lords of the bounds are stronger in directions" (OCR, unverified).
Verdict: CONTRADICTS the note's "no witness". Al-Qabīsī attests the bound-before-triplicity order
(unnamed "certain people", with the reason), though not its attribution to 'Umar or Māshā'allāh. Change:
the page note and the comment → "attested by al-Qabīsī (I.22) for unnamed 'certain people'; the
attribution to al-Tabari/Masha'allah has no witness here; Abu Bakr II.5.14 gives 'Umar the other order".
A factual correction; the label stays the owner's ruling.

**26. Ibn Ezra's victor and the almuten "techniques from outside these texts"** (d683f4e; Victors page).
ITA I.18, al-Qabīsī I.22 and I.77, pp. 81-82: the 5-4-3-2-1 weights and the victor of a topic (the house's
cusp degree — "the second house ... was the fifth degree of the sign of Aries" — plus the natural
significator and the Lot of the topic; fn 210: "only the primary triplicity Lord receives points");
VIII.1.4, al-Qabīsī IV.7, p. 357: the victor over the native from the Ascendant, the luminaries, Fortune and
the syzygy, "in charge of two or three or four places or more, by the multitude of its power in them";
fn 211, p. 82: Dykes's judgment that with Dorothean triplicities, Egyptian bounds and one triplicity lord
"the victor will always be either the domicile or exalted Lord of the place" but for "a few degrees of
Pisces" (Mars) and "of Cancer" (Venus) (OCR, unverified).
Verdict: QUALIFIES. The weighted almuten and the five-place victor are in a text in hand (the app's
`evaluate_victors` scores exactly those five points and only the sect's triplicity lord, as fn 210 says);
ibn Ezra's worksheet rows (Day, Hour, Places) are not. Change: relabel "from outside these texts" → "the
weights and the five places al-Qabīsī's (I.22, IV.7); the worksheet ibn Ezra's"; quote fn 211 as the
standing critique. Owner's call on the relabel.

**27. GOV-1.7's build: the unweighted count of claims in 3's "at least as many claims" stands as built**
(owner, after the fourth check).
Verdict: SILENT. ITA's al-Qabīsī IV.5 weighs authority ("more authoritative in the place"), which is the
weighted alternative the note flagged; not a statement about 1.7.

**28. F-4: the lords of the triplicity over the life keyed to the sect light; the Ascendant rows a
labelled comparison, off by default** (2026-09-13).
ITA I.13, al-Qabīsī I.57b, pp. 71-72: al-Andarzaghar's first, second and third lords "of the triplicity of
the Ascendant" signify the beginning, middle and end of life; Introduction §7 fn 31, p. 20: the eight-place
scheme "is already used by traditional astrologers in assessing conventional happiness and prosperity, when
judging the triplicity Lords of the sect light" (OCR, unverified).
Verdict: QUALIFIES. Both keys are ancient: al-Andarzaghar keys the life to the Ascendant's triplicity
lords, Dykes's own summary keys prosperity to the sect light's. The comparison rows the owner allowed have
a named source. Change: the Ascendant rows' label may cite al-Qabīsī I.57b (the app's supplement table
already quotes it). Not a ruling.

**29. The Andarzaghar triplicity-lords table: "first/second/third" = the chart's sect order, "the app's
reading"** (61d9df5; build log 2026-09-15).
ITA I.7, Abbr. I.86, pp. 46-47: "the diurnal judge of these is the Sun and [then] Jupiter, but the nocturnal
one Jupiter and [then] the Sun; sharing with them by day and night [is] Saturn"; al-Qabīsī I.16b-e the same
(OCR, unverified).
Verdict: CONFIRMS: the order of the first two lords flips with sect in Abū Ma'shar's and al-Qabīsī's own
tables, and al-Qabīsī is the author of the Andarzaghar report. Change: cite I.7 on the row and drop "the
app's reading".

**30. Besieging limited to the malefics (ITA IV.4.2); enclosure by the fortunes its own row; "a third body
or ray between the two breaks either"** (9c6c7e3; `RHETORIUS_AFFLICTION_CONDITIONS`).
ITA IV.4.2, Gr. Intr. VII.6.1244-60, p. 225: the loosening is "if the Sun or a certain one of the fortunes
aspected the besieged planet by an aspect of friendship, and there were less than 7° between"; al-Qabīsī
III.28b "a fortune or the Sun ... from a trine or sextile aspect"; Dykes's comment p. 228: "a benefic planet
will break or prevent a malefic enclosure by degree, and a malefic planet will break or prevent a benefic
enclosure by degree" (OCR; pp. 224-228 are also among the photographed pages, where both sentences read
the same). IV.1, al-Qabīsī III.25b-26, p. 218: "a planet would have a fortune or its rays in front of it,
and another fortune or its rays after it. And certain people called this 'being surrounded'" (OCR,
unverified).
Verdict: CONFIRMS the malefic limit and the fortunes' row (al-Qabīsī III.25b-26 is the cleaner citation for
the latter); QUALIFIES the breaker: the ITA texts loosen a malefic siege only by a fortune or the Sun, by
friendly aspect, within 7°; Dykes generalises to "a planet of opposite quality"; "any third body or ray" is
Rhetorius Ch. 41's construction, not ITA's. Change: the row says whose breaker it applies. Owner's call
whether the breaker follows Rhetorius (any) or ITA (opposite quality / fortune or Sun).

**31. Kollēsis by degree, "a sign boundary between them notwithstanding (Ch. 34 names degrees, not the
sign)"** (fb4f86f).
ITA III.7 comment, p. 136: "the Arabic, unlike the Greek, does not distinguish connections within the same
sign (kollēsis) from those in different signs (sunaphē)"; the section head lists "Cf. Greek: Attachment,
adherence (kollēsis)" beside "Joining (sunaphē)"; BA II.10 quoted p. 134: application "by 3° and just short
of that" (OCR, unverified).
Verdict: QUALIFIES (against). Dykes defines kollēsis as the same-sign connection; the app's reading that Ch.
34's three degrees run across a sign boundary has his definition against it (Rhetorius's Greek is what
Holden translates). Owner's call: revert to same-sign with the 3°, or keep the across-boundary reading with
Dykes's definition named on the row.

**32. The Moon's phase boundaries after Valens II.36: the 12° boundaries "this app's"** (2f1ab71;
`app.py` 14444).
ITA II.10.5, Abbr. II.27-31, p. 108: the Moon's eight properties from the Sun — the conjunction; "if she
receded from him by 12°"; 90°; "distant from the opposite of the Sun by 12°"; the opposition; "if she would
add 12° on top of the opposite"; 90° pursuing; "distant from the Sun by 12°" (OCR, unverified); fn 41 →
IV.5, where 12° from the Sun and from the opposition are the Moon's corruptions.
Verdict: QUALIFIES (supports). Three of the four boundaries the page calls the app's own — 12° after the
conjunction, 12° after the opposition, 12° before the conjunction — are Abū Ma'shar's phase markers; his
fourth (12° before the opposition) the app does not use. Change: the note says the 12° boundaries are Abū
Ma'shar's (Abbr. II.27-31) applied to Valens's phases, and names the one marker not used.

**33. Mercury's phase against the sect (Mathesis III.7, fnn 186, 194): a morning star diurnal** (8f96202);
and the hayz code's Mercury derivation (`app.py` 1726).
ITA V.11, Gr. Intr. IV.9.1312-38, pp. 276-277: "if [Mercury] is arising [before the Sun] he becomes
diurnal, but when he sets [after the Sun] he will be nocturnal"; fn 188: Paul Ch. 6 and Tet. I.7; fn 171,
pp. 269-270: the Rhetorius/BA doctrine that Mercury takes sect from the planets aspecting him is an error
Dykes traces to Paul's benefic/malefic rule (OCR, unverified).
Verdict: CONFIRMS, with a corpus-author witness (Abū Ma'shar) for the sect half, which the page sources
only to Firmicus's translator. Change: cite Gr. Intr. IV.9 in ITA V.11 on the finding and in the hayz
comment.

**34. Morin's unfortunate houses as 6, 8, 12, "this app's reading"** (8101fdf; `app.py` 6099).
ITA IV.4.1, al-Qabīsī III.28c + fn 43, p. 224: "cadent from the Ascendant. That is, being in aversion to
it: in a sign which does not aspect the rising sign, particularly the twelfth, eighth, and sixth; the second
sign is also cadent from the Ascendant but is not considered as difficult" (OCR; p. 224 is photographed and
reads the same); Judgments 24 fn 178, p. 271, the same.
Verdict: QUALIFIES (supports). Dykes names 12, 8, 6 as the difficult averse places; not Morin's phrase, but
a witness that the triad is the tradition's, not the app's invention. Change: the note may cite fn 43 as
the parallel and keep "the app's" for the equation with Morin's houses.

**35. Places harming the eyesight: "the Ascendant degree itself (this app's addition)"** (2707e07).
ITA VII.10, al-Qabīsī I.52, p. 350: the degrees of chronic illness by sign; Figure 120: BA's fixed-star
degrees (Pleiades, Praesepe, the sting of Scorpio, the pitcher of Aquarius ...) fn 42: from Carmen
IV.1.108-11 and Rhetorius Ch. 61.
Verdict: SILENT on the Ascendant degree; the tables are a coverage item (§C). No change.

**36. Sahl's degrees of nobility (Figure 57) read as ordinals, "the app's (Figure 64's manner)"**
(PR #13; 0f1c310).
ITA VII.9.2-3, Figures 116-118, pp. 347-349: the degrees of eminence printed as ordinals ("19th", "3rd,
15th, 27th"); I.3 fn 23, p. 29: "widespread inconsistency between cardinal and ordinal numbers ... My sense
is that the authors probably meant 'at the end of the nineteenth degree, namely at 19°'" (OCR, unverified);
VII.9.3 fn 38: the degrees "were probably the locations of eminent fixed stars".
Verdict: QUALIFIES. Dykes prints ordinals but resolves them to the cardinal point at the end of the Nth
degree (19th → 19°), not to the span N-1..N the app tests. And al-Qabīsī I.53 (Figure 118) is a THIRD table:
Taurus "3rd, 15th, 27th" — agreeing with Sahl's Taurus 3 against Abū Ma'shar's 8th. Change: the pages' "the
ordinal reading is the app's" could add Dykes's resolution; the Figure 57/64 comparison may add al-Qabīsī's
table. Owner's call on the unit.

**37. The Lots of Jupiter and Saturn as supplement rows, named "prosperity, aid, victory" and "the
burdensome"; whether they belong at course-text depth "a ruling"** (4c96bf0).
ITA VI.1.7-8, pp. 288-289: "§VI.1.7: The Lot of Victory or Jupiter" — Abbr. VI.10 "by day from the Lot of
Spirit to Jupiter, conversely by night"; "§VI.1.8: The Lot of Nemesis or Saturn" — Abbr. VI.11 "by day from
Saturn to the Lot of Fortune, conversely by night"; al-Qabīsī V.5c, V.11d the same (OCR, unverified).
Verdict: CONFIRMS the formulas (al-Qabīsī a further witness) and sources the course's names Victory and
Nemesis to Dykes's own headings. Change: the rows may carry "Victory / Nemesis (ITA VI.1.7-8)". The depth
stays the owner's call.

**38. The father Lot's second form: Saturn under the rays → Sun to Jupiter (Hermes preferred), Sahl's Mars
to Jupiter the "some people" form** (PR #13; `father_burnt_abu`).
ITA VI.2.7, pp. 294-295: Gr. Intr. VIII.4.703-26 "If however Saturn were under the rays, it is taken in the
day from the Sun to Jupiter"; "certain people said ... from Mars to Jupiter"; "what Hermes said is more
true"; al-Qabīsī V.6b-7a the Sun-to-Jupiter form only (OCR, unverified).
Verdict: CONFIRMS; al-Qabīsī is a second primary witness for the Hermes form. Change: cite him on the row.

**39. The eyesight/nobility/Moon-phase/Morin/natures/Andarzaghar findings placed at "Course text and
supplement" depth, display only** (2026-09-14/15).
Verdict: SILENT. ITA has no bearing on depth.

## B. The app's own declared readings (strings in `app.py`)

**40. "This app's convention for strength language" — the division at the axial degrees** (14985).
See 19. Verdict: CONFIRMS as Dykes's proposal (Introduction §6). Cite him.

**41. Sect/hayz: all three conditions (sect, hemisphere, sign gender); Mars nocturnal** (1723-1740).
ITA III.2, Abbr. III.3, p. 113: a masculine planet above the earth by day, in a masculine sign, "with Mars
alone being excepted"; al-Qabīsī I.78, pp. 113-114: halb (sect and hemisphere) and, "if in addition" the
sign's gender, the domain (OCR, unverified).
Verdict: CONFIRMS; the halb/hayyiz distinction is stated (the app scores only the full hayz). Cite.

**42. Whole-sign aspects; no out-of-sign aspects** (the aspect table).
ITA III.6, Gr. Intr. VII.5.722-41, p. 127, and fn 40: the paragraph "underscores that out-of-sign aspects
are not used"; fn 47, p. 128: al-Qabīsī "defines aspects solely in terms of whole-sign configurations"
(OCR, unverified). Verdict: CONFIRMS.

**43. Per-planet orbs (Sun 15, Moon 12, Saturn/Jupiter 9, Mars 8, Venus/Mercury 7), no moiety; Saturn in
the Moon's body at 12° but she not in his until 9°** (`PLANETARY_ORBS`, 1919; 2005-2015).
ITA II.6, Abbr. II.11-12 and Gr. Intr. VII.4.354-89, pp. 90-91: the same values and the same Saturn-Moon
example ("until there are less than 9° between them") (OCR, unverified); III.7, p. 134: al-Qabīsī's "6° or
less" and BA's 3° as the other two ranges; Dykes p. 136: "each planet gets a standardized orb of 6°" in
al-Qabīsī.
Verdict: CONFIRMS the Abū Ma'shar rule; QUALIFIES it as one of three witnesses in hand (12°/6°/3°). No
change; the Configurations help may name the three.

**44. Cazimi 16'; superiors under the rays 15/15/18 east, inferiors 7 (6 direct east), the Moon 12
(option 15)** (`CAZIMI_ORB`, `solar_phase`, 1573-1600; CONV-SOLAR_BURNED_ORB).
ITA II.9, al-Qabīsī III.7, p. 95: "united" when "16° or less" between them (the OCR's degree sign for the
minute; the Glossary p. 384 reads "within 16' of longitude"); II.10.1, Abbr. II.17-21, p. 97: Saturn and
Jupiter 15°, Mars 18°; II.10.2, Abbr. II.22-26, p. 101: the inferiors 7°; II.10.5, p. 108: the Moon 12°;
Judgments 39, p. 96: "less than 12° between them and the Sun" for under the rays; Glossary p. 379/391: burned
1°-7.5°, under rays 7.5°-15° (the later convention) (OCR, unverified).
Verdict: CONFIRMS (the 16' with the OCR caveat). The inferiors' direct-eastern 6° is Gr. Intr. VII.2's; ITA's
Abbr. has 7° throughout — QUALIFIES that one order. No change.

**45. The burned place: all Libra and Scorpio for Sahl's 110; 19° Libra-3° Scorpio Abū Ma'shar's harsher
band; 15° Libra-15° Scorpio "often defined (Dykes, Carmen p. 258 fn 104; Course Glossary)"**
(`BURNED_PLACE_SIGNS`, 5630-5640; DEC-D-5).
ITA IV.3, Gr. Intr. VII.6.1192-1218, p. 221: "in the burnt path (that is, in Libra and Scorpio), and more
difficult than that if they were from the nineteenth degree of Libra to the third degree of Scorpio";
al-Qabīsī III.29, p. 222: "the burnt path (which is the last half of Libra and the first half of Scorpio)";
fn 21 and Glossary p. 379 state both (OCR, unverified).
Verdict: CONFIRMS Abū Ma'shar's two bands; QUALIFIES the 15°-15° attribution: al-Qabīsī III.29 is a
primary text in hand for it. Change: cite al-Qabīsī III.29 (ITA IV.3) in place of the Course Glossary.

**46. Testimony 83 (advancing) dynamic, against the Alchabitius cusps** (14712).
ITA I.12, al-Qabīsī I.56e-f, p. 68; III.3-4 and Dykes's comment pp. 120-123 (Nechepso's eight places, "the
type of advancement and retreat used by Abū Ma'shar and al-Qabīsī"); fn 32 "ambiguous"; Introduction §6 (3).
Verdict: QUALIFIES (as 19-20): the quadrant reading is Dykes's proposal and al-Qabīsī's practice, not a
statement of the definitions. Cite ITA pp. 16, 20, 122.

**47. The prenatal fullness's degree = the luminary above the earth; both or neither above, the Moon —
"no text says"** (Releaser tab caption (5), 15726-15728).
ITA VIII.1.2, al-Qabīsī IV.3, p. 352: Ptolemy — "the degree of the luminary which was above the earth";
"certain ones of the sages" — if one is on the eastern degree and the other on the western, "the degree of
the east is the degree of the prevention"; Valens — "the degree in which the fullness is — wanting the
degree of the Moon"; al-Qabīsī follows Ptolemy (OCR, unverified).
Verdict: QUALIFIES. A text names a tie rule (the eastern luminary) and the Moon default the app uses is
Valens's. Change: replace "no text says" with the three opinions; owner's call whether the "certain sages"
tie rule is adopted.

**48. The four-sign self-house-master exception (1.16, 1-2)** (`SAHL_BOTH_AT_ONCE`).
ITA VIII.1.3, al-Qabīsī IV.6, p. 356: the Sun in Aries or Leo, the Moon in Taurus or Cancer, "the releaser
and the kadukhudhāh together" (OCR, unverified). Verdict: CONFIRMS. Cite.

**49. "Looking" = the whole-sign aspect for the house-master's testimony** (caption (2)).
ITA VIII.1.3 fn 18, p. 355: the lord "does not need to be connected to the releaser itself ... suggesting
that only a whole-sign aspect to the releaser's sign is needed" (OCR, unverified). Verdict: CONFIRMS. Cite.

**50. The meeting's lord-looking test supplied from 1.15, 15's general wording (a reading)** (caption).
ITA VIII.1.3, al-Qabīsī IV.4, p. 355: "every place ... will be fit to be the releaser, if the Lord of the
domicile or of the exaltation or of the rest of the dignities aspected it" — stated for all candidates, the
conjunction degree included (OCR, unverified). Verdict: CONFIRMS the reading as another author's explicit
rule. Cite.

**51. The Ascendant as last resort, under 1.15, 16's conditions.**
ITA VIII.1.3, al-Qabīsī IV.4, p. 354: "After this, you will look at the degree of the Ascendant, and
establish it as the releaser" (OCR, unverified) — no benefic-aspect or lord condition stated for it.
Verdict: QUALIFIES (a variant). No change.

**52. The Lot of friends Moon → Mercury, reversed at night, "settled"** (5335).
ITA VI.2.45, p. 320: Abbr. VI.53 and Gr. Intr. VIII.4.1464-69 "in the day and night from the Moon to
Mercury" (unreversed); al-Qabīsī V.14a "And al-Andarzaghar said it is taken conversely in the night"; fn
104: "This should be reversed at night" (OCR, unverified).
Verdict: QUALIFIES. Abū Ma'shar's form is unreversed; the reversal is al-Andarzaghar's and Dykes's
preference. Change: confidence "settled" → "reversed after al-Andarzaghar (al-Qabīsī V.14a) and Dykes; Abū
Ma'shar unreversed". Owner's call.

**53. Men's and women's marriage Lots (Saturn ↔ Venus) unreversed, "settled"** (5238-5245).
ITA VI.2.21 and VI.2.23, pp. 305-307: Hermes "in the day and night", "certain people" reverse, "what Hermes
said is more fitting"; al-Qabīsī V.10e, V.10b unreversed; fnn 58 and 62: "this Lot is really supposed to be
reversed at night: Carmen II.2.2" (OCR, unverified).
Verdict: CONFIRMS the texts' unreversed form (three witnesses); QUALIFIES with Dykes's dissent. Change: a
note on the rows. Not a ruling.

**54. The Lot of work (expedition) Saturn → Moon unreversed, Paul's reversal a second row** (5300-5322).
ITA VI.2.40, pp. 317-318: Abbr. VI.49-50, Gr. Intr. VIII.4.1331-46 and al-Qabīsī V.13a all "in the day and
night from Saturn to the Moon" (OCR, unverified). Verdict: CONFIRMS (al-Qabīsī a third witness).

**55. The Lots of children (Jupiter → Saturn: Theophilus unreversed, Hermes reversed) and of the timing of
children (Mars → Jupiter, unreversed)** (5215-5237).
ITA VI.2.13-14, pp. 299-300: Gr. Intr. "Theophilus thought that the Lot of children is taken in the day and
night from Jupiter to Saturn, but the first ... which Hermes and all the ancients described is more true";
al-Qabīsī V.8a reversed; the time of children "in the day and night from Mars to Jupiter" (OCR,
unverified). Verdict: CONFIRMS all three rows.

**56. The Lots of siblings (Saturn → Jupiter, Hermes; Mercury → Jupiter, Valens), both unreversed** (5190).
ITA VI.2.5, p. 293: "Hermes and all the ancient sages ... in the day and night from Saturn to Jupiter";
al-Andarzaghar "relating this to Valens" Mercury to Jupiter; fn 28: "a misattribution which was current
among the Arabs and Persians" (OCR, unverified). Verdict: CONFIRMS; the Valens attribution QUALIFIED by
Dykes. Note fn 28 on the row.

**57. The Lot of Spirit (Moon → Sun by day, reversed) and of the mother (Venus → Moon, reversed)**.
ITA VI.1.2, pp. 284-285; VI.2.41, p. 318: identical in Abbr., Gr. Intr. and al-Qabīsī. Verdict: CONFIRMS.

**58. Abū Ma'shar's eleven corruptions of the Moon (VII.6, 63-74) as their own table** (7880-7890).
ITA IV.5, Abbr. IV.26-31 and Gr. Intr. VII.6.1261-77, pp. 230-231: the same eleven. Verdict: CONFIRMS.

**59. Rhetorius Ch. 26's dominance (the other in the 9th, 10th, 11th from the planet), reported neutrally**.
ITA IV.4.1, p. 223: a malefic "elevated over them from the tenth or eleventh [sign] from their place";
Glossary p. 386 "Overcoming": eleventh, tenth or ninth, "the tenth ... more dominant" (OCR, unverified).
Verdict: CONFIRMS (Abū Ma'shar names the tenth and eleventh only). Cite.

**60. The wells (`WELLED_DEGREES`, from the 2020 Gr. Intr.'s photographs)**.
ITA VII.9.1, Figures 114-115, pp. 346: the Latin Gr. Intr. and al-Qabīsī tables differ from the app's in
several cells (Aries "24th" for 23; Gemini "13th ... 22nd" for 12, 26; Cancer "22nd ... 28th"; Sagittarius
"23rd"; Capricorn without 7) and from each other (OCR, unverified — tables are the OCR's weakest ground).
Verdict: QUALIFIES (edition differences, Latin vs Arabic). Change: none until the page is read; then a
note that the Latin figure and al-Qabīsī's differ.

**61. The victor weights: only the sect's triplicity lord scores (`evaluate_victors`)**.
ITA I.18 fn 210, p. 81: "Note that only the primary triplicity Lord receives points." Verdict: CONFIRMS.

**62. Twelfth-parts (PN IV; Sahl's further uses unbuilt, `NOT_IMPLEMENTED_COVERAGE`)**.
ITA IV.6, al-Qabīsī IV.15, pp. 231-232: of the planets "or the degree of the house which you wanted" — fn
59: "Obviously using quadrant houses" (OCR, unverified). Verdict: CONFIRMS the computation; the houses'
twelfth-parts are a coverage item (§C).

**63. `NOT_IMPLEMENTED_COVERAGE`: Gr. Intr. VII.5 connection by latitude; the masculine/feminine degrees;
the advancing/withdrawing quadrants**.
ITA III.7.2, pp. 135: connection by latitude in Abbr. III.15-19 and al-Qabīsī III.11b (three kinds); VII.8,
pp. 342-344: the three schemes of masculine/feminine degrees, "we have followed this teaching as a most
potent one"; I.11, Abbr. I.98-102, p. 66: the four quarters "eastern, masculine, advancing" etc., fn 143:
"the same as for advancing and retreating planets in III.3-III.4" (OCR, unverified).
Verdict: CONFIRMS the list's descriptions; ITA adds al-Qabīsī's latitude definition and Abū Ma'shar's
"most potent" preference among the degree schemes. No change to the list.

## C. What the app declares as its own that Dykes states (cite him instead)

- The dispatch — whole signs for topics, quadrant divisions for power/activeness — is Dykes's proposed
  solution, ITA Introduction §6, pp. 19-20 (entries 19, 40, 46). The pages say "this app's convention".
- The seven "good places" = Timaeus/Dorotheus's seven busy places, which Sahl calls praiseworthy and
  Dorotheus good and strong: ITA pp. 18, 121 (entry 2).
- The Moon's 12° phase boundaries: Abbr. II.27-31, p. 108 (entry 32). The page says "this app's".
- The triplicity lords' sect order: Abbr. I.86-89, al-Qabīsī I.16 (entry 29). The build log says "the
  app's reading of first/second/third".
- The five degrees in ecliptic longitude: al-Qabīsī IV.4's "five equal degrees" (entry 18). The docstring
  says "by choice".
- Mercury diurnal as a morning star: Gr. Intr. IV.9 in ITA V.11 (entry 33). The page cites only Firmicus.
- The difficult averse places 12, 8, 6: fn 43, p. 224 (entry 34). The page says "this app's reading".
- The 15° Libra-15° Scorpio burnt path: al-Qabīsī III.29 (entry 45). The page cites the Course Glossary.
- The fullness's degree when both or neither luminary is above the earth: Valens's Moon and the "certain
  sages'" eastern degree, al-Qabīsī IV.3 (entry 47). The page says "no text says".
- The name "Basis": ITA VI.1.4 (entry 24); the names Victory and Nemesis: VI.1.7-8 (entry 37).
- The weighted almuten (5-4-3-2-1, one triplicity lord) and the five-place victor: al-Qabīsī I.22, I.77,
  IV.7 (entries 26, 61). The page says "from outside these texts".
- The proportional semi-arc formula: al-Qabīsī IV.11-12 (ITA VIII.2.2) and Appendix E (entry 21). The
  page says "stated in no text in hand".
- The bound-before-triplicity weighting: al-Qabīsī I.22 (entry 25). The page says "no witness here".
- The Moon's right/eastern bridge: al-Qabīsī III.8a (entry 4). The row says the texts name only right and
  left.

## D. ITA doctrines the coverage list does not know

Computable, with an ITA text behind them (al-Qabīsī and Abū Ma'shar are corpus authors; the canon-only
rule still asks whether the course teaches them):

1. Al-Qabīsī's releaser and kadukhudhāh procedure whole (VIII.1.3, pp. 353-356): eleven places for each
   luminary with sign-gender gates, the Moon's rays, quadrant houses with 5° at every cusp, three
   orderings of the lords, the tie-breaks (own place, nearest degree, the Sun's relations), the four-sign
   exception. A second longevity procedure beside Sahl's, from a text in hand.
2. Al-Qabīsī's primary directions (VIII.2.2, pp. 360-367) with the "hours of distance", the two
   significators and the equation; directions across quarters; distributions by the same arithmetic; the
   revolution's Ascendant directed "one day for every 59' 08"" (IV.13b, p. 367); the mundane directions
   (VIII.3.3). Appendix E's worked example is the test fixture.
3. The victor of a topic (I.18, al-Qabīsī I.77): the house's cusp degree plus the natural significator plus
   the Lot of the topic; Dykes's fn 211 critique.
4. The lords of the angles in the angles (I.15, sixteen delineations) and house meanings by angularity
   (I.14).
5. Bodyguarding (III.28, pp. 206-216): al-Qabīsī's (domain, angle, a luminary in its square), BA's three
   medieval types (with the Moon's 7° and the Sun's 15°), Ptolemy's ranked eminence. The app has none
   (`docs/synthesis/04_tier1_and_spearbearing_report.md` is the only trace).
6. Enclosure by sign (IV.4.2, the second kind): malefics or their rays in the 2nd and 12th signs from the
   planet or sign, benefics in aversion; Dykes's minimal/maximal forms (p. 227).
7. Facing (II.11, al-Qabīsī III.5): a western planet as many signs from the Sun as its domicile from Leo;
   eastern of the Moon likewise from Cancer.
8. Al-Qabīsī's synodic stages (II.10.1-2, III.9-10): "eastern, increased in strength" to 30°, "eastern,
   strong" to 60°, "going toward weakness", the retrograde and western stages; Abū Ma'shar's easternness
   ending at 90° (fn 27, p. 97) against the app's hemisphere option.
9. The Moon's and the superiors' elemental quarters (II.12, al-Qabīsī II.41a-42).
10. Profection by 30° from the natal degree with 12 1/6 days per degree (VIII.2.1); the Lord of the turn —
    the lord of the hour of birth and its successors year by year over the houses (VIII.2.3); transits
    defined by apogee and latitude, "the northern one of them goes over the southern" (VIII.2.4).
11. The namūdār (VIII.1.2): the syzygy's victor carried to the nativity to fix the Ascendant or Midheaven
    degree — a rectification the app does not offer.
12. The bright/dark/smoky/empty degrees (VII.7, two tables that disagree — the app tests "bright degree
    (11)" from one), the three schemes of masculine/feminine degrees (VII.8, already declared unbuilt), the
    degrees of chronic illness (VII.10) with BA's fixed-star degrees (Figure 120), al-Qabīsī's
    increasing-fortune degrees (I.53, Figure 118) as a third witness beside Sahl's Figure 57 and Gr. Intr.'s
    Figure 64.
13. Times or changes (IV.7): a planet's five turning points (stations, the rays, a benefic leaving a
    malefic, the degree of fall or exaltation, the last degree of a sign).
14. The planetary Lots and house Lots the app lacks: the releaser (VI.2.2, from the syzygy to the Moon —
    fn 22 "probably wrong" against Valens), origins and condition (from Mercury's sign), real estate,
    cultivation, the end of matters, male and female children, the time of marriage (Sun → Moon), the
    suspected year, the oppressive place, navigation, intellect, wisdom, rumors, religion, nobility, the
    three kingdom Lots, Valens's Sun → MC job Lot, the cause of a kingdom (from Jupiter), hope, knowledge,
    heroism; Appendix D's concordance.
15. Al-Qabīsī's pains of the planets in the signs (I.4) and the colours of the places (I.17); planetary
    friendship and enmity (III.27); the bust (VIII.4); the opening of the portals (VIII.3.4).

## Counts

CONFIRMS 31 · CONTRADICTS 4 (entries 9, 17, 21, 25) · QUALIFIES 21 · SILENT 7 — over 63 entries (verdicts
counted once per entry by the leading verdict; a CONFIRMS-and-QUALIFIES entry is counted as CONFIRMS).

## The five for the owner

1. **Entry 21** — the proportional semi-arc method is stated by al-Qabīsī (ITA VIII.2.2, pp. 362-364) and
   worked by Dykes (Appendix E): `PN4_ASCENSION_RULE`'s "the formula stated in no text in hand" is false and
   (f) is not an outside-corpus import.
2. **Entry 25** — al-Qabīsī I.22 (p. 81): "certain people put the bound before the triplicity" — the
   Victors page's "the bound-3 order has no witness here" is false; the attribution to 'Umar/Masha'allah
   remains unwitnessed.
3. **Entry 17** — al-Qabīsī IV.4 (p. 355) gives the five degrees "before the degree of the Ascendant or any
   house"; Dykes gives the all-cusps form to Ptolemy (p. 12): the axial-only canon has a primary-text
   witness against it, in the releaser procedure itself.
4. **Entry 9** — ITA's Latin Gr. Intr. table (Figure 108, p. 332) gives the luminaries' middle years as 69½
   and 66½ against the app's 39½ (OCR; read the page).
5. **Entry 31** — Dykes defines kollēsis as the same-sign connection (p. 136); the app's across-the-boundary
   reading of Rhetorius Ch. 34, declared 2026-09-15, has his definition against it.
