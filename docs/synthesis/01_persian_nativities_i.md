# Phase 1 — Māshā'allāh, *Book of Aristotle* (BA) and Abū 'Alī al-Khayyāt, *On the Judgments of Nativities* (JN) — *Persian Nativities* I

Source: `consolidated_texts_final/pn1/pn1_pdf_text.md`, 941,750 bytes, 19,455 lines, 407 page
markers for a 409-page PDF (see conventions). The PDF's own embedded OCR, filed 2026-09-15, "not
read against the page by a human" (its README); a marker re-OCR is queued to supersede it. Read
2026-09-15, whole, in order: Editor's Introduction (pdf pp. 13–46), Prologue and BA Books I–IV
(pdf pp. 47–271), JN Chs. 1–50 (pdf pp. 272–376), Appendices A–F (pdf pp. 377–393), Index. Nothing
in `app.py` cites this volume yet; this file precedes any citation.

**Companions.** `01_on_nativities.md` (Sahl), whose §§1, 5, 7 this file cross-checks;
`02_reconciliation.md` for the five classes; `docs/COURSE_COVERAGE_2026-09-14.md` and
`NOT_IMPLEMENTED_COVERAGE` in `app.py` for what is already declared unbuilt.

---

## Heading and citation conventions (the OCR caveat)

**Quote sparingly; every quotation below is "(OCR, unverified)."** The text layer is readable but
carries the classic defects: *Satum* for Saturn, *Mcrcury*, *I lugo* for Hugo, *bcncvolcnts*,
footnote numbers printed as `*NN`, `,l`, `'•` or as superscripts run into the first word of the
note, and running heads garbled beyond use. Figures are ASCII noise. No sentence numbers exist in
BA or JN (Dykes did not number these two texts); cite by **Book.chapter.section** as Dykes prints
them — BA `III.2.1`, and inside Book III and IV the bracketed topic/item numbers `[1.3]`, `[6.2]`
that Dykes added — and for JN by **chapter** (`JN Ch. 4`). Page markers are `*[PN I pdf p. N]*`,
the **PDF page index, not the printed folio**: printed page = pdf page − 45 for the whole body
(BA p. 1 = pdf p. 47; JN Ch. 1, printed 227 = pdf p. 272; Appendix A, printed 333 = pdf p. 377).

**Two pages are out of order.** Printed p. 24 (Figure 2, BA II.7 and the start of II.8) and printed
p. 233 (the end of JN Ch. 2 and the start of Ch. 3) are absent from their places (pdf p. 69 jumps
23→25; pdf p. 277 jumps 232→234) and sit at the **end of the file** under the markers
`*[PN I pdf p. 407]*` and `*[PN I pdf p. 408]*`. Read them there. Nothing else is missing.

**Book structure**, from the Table of Contents (pdf pp. 5–10), verified against the body:
Prologue; Book I, 6 chapters; Book II, 17 chapters; Book III organised by house topic —
III.1 (life, 10 chapters), III.2 (assets, 0–6), III.3 (siblings, 0–7), III.4 (parents, 1–9),
III.5 (children, 0–5), III.6 (illness, 0–8), III.7 (marriage, 0–13), III.8 (death, 0–1),
III.9 (travel, 1–2), III.10 (work, 1–8), III.11 (slaves, 1), III.12 (friends, 1–10); Book IV,
25 chapters. JN: 50 chapters; Heller's note before Ch. 46 marks Chs. 46–50 as from "another
copy". Footnotes restart per Book in BA and run continuously through JN (1–291).

Dykes's own scheme for Book III (Intro §2, pdf pp. 21–22): each topic's first chapter lists the
**questions** in brackets `[1]…[7]`; the next lists the **items** to examine per question
`[2.1]…[2.4]`; the remaining chapters delineate each item. Book IV he has tagged the same way to
his ten "cycle of the year" heads (`[1]`–`[10]`, Intro §7). These bracket numbers are Dykes's,
and they are the only fine-grained address the text has; use them.

---

## 0. What these two books are, and how Sahl uses them

**BA** is Hugo of Santalla's 1140/41 Latin of a lost Arabic natal compendium by Māshā'allāh
(c. 740–815), from the Rueda Jalón library; two manuscripts survive, both once John Dee's
(Digby 159, Savile 15; Intro §1, pdf pp. 13–17). Its sources (Intro §2, pdf pp. 17–21): a Pahlavi
Valens with Buzurjmihr's commentary; a fuller Pahlavi Dorotheus than 'Umar's; Rhetorius (used
line by line in Book III); Ptolemy; Paul; the *Zīj al-Shāh*; Zaradusht; and **al-Andarzaghar's
*Book of Nativities***, which supplies the whole of Book IV and much of Book III. Dykes translates
Burnett–Pingree's 1997 critical edition and corrects Hugo constantly from Sahl, al-Dāmaghānī
("Da.") and Rhetorius, in brackets.

**JN** is Abū 'Alī's short manual (Heller's 1549 Latin edition, from John of Seville). Dykes's
account of it (Intro §8, pdf pp. 35–43, and Appendix F, pdf p. 393): Chs. 1–7 derive from
Māshā'allāh's *Nativities*; Chs. 8–38 are a simplified, re-ordered digest of BA III (with 'Umar);
Chs. 39–45 are *On Sig. Planet.*; Chs. 47–50 are *Twelve Dom.*; Ch. 46 unknown. Chs. 46–50 are not
Abū 'Alī's own. No *muhtazz* by weighted points anywhere in either book: "BA and JN cannot be used
as sources for any clear notion of a weighted *mubtazz*" (Intro §8, pdf p. 39).

**Sahl's *On Nativities* is the third witness to al-Andarzaghar**, beside BA and Da. Dykes's Sahl
footnotes name BA well over a hundred times and JN a dozen; the map is §7 below. The pattern: Sahl
Chs. 1.15–1.32 (life) parallel BA III.1; Sahl 2.1–2.22 parallel BA III.2.0–6 (Dykes's own table at
Sahl 2, comment); Sahl 3–12 parallel BA III.3–III.12 chapter by chapter, with Sahl reordering,
adding Ptolemy, Māshā'allāh and 'Umar, and dropping some items. Sahl has **no** counterpart to BA
Books I–II (apparatus) except 1.22 (easternness ↔ BA II.1–2) and **no** counterpart to BA Book
IV (the cycle of the year, the *firdāriyyāt*), which is why PN IV was needed for timing. JN
supplies what BA lacks: religion (Ch. 29), animals (Ch. 23), boldness (Ch. 34), the lord of the
hour (Ch. 46), and twelve worked prosperity charts (Ch. 7).

---

## 1. Editor's Introduction (pdf pp. 13–46) — nine sections

| § | Topic | pdf pp. | Bears on |
|---|---|---|---|
| 1 | Hugo, Bishop Michael, the manuscripts | 13–17 | provenance |
| 2 | BA's sources; the bracket scheme | 17–22 | how to cite |
| 3 | "An alternative Rhetorius?" | 22–23 | spear-bearing Type 3 |
| 4 | Causes in BA (Providence, millstones) | 23–25 | — |
| 5 | Hugo's Latin vocabulary, nine terms | 25–29 | *cardo*, *hospitium*, "third from a pivot", "safe place", *perversus* |
| 6 | Sect and "at rest" (*quies*) | 29–33 | *hayyiz*, *halb*, *hazz* |
| 7 | Annual predictions: the ten heads of the cycle of the year | 33–35 | Book IV; PN IV |
| 8 | JN: relation to Māshā'allāh; no weighted *muhtazz*; why not Holden | 35–43 | JN citation |
| 9 | Arabic and Pahlavi vocabulary, 22 terms | 43–46 | *hīlāj*, *kadukhudhāh*, *jārbakhtār*, *jārzamān*, *jār kanār*, *intihā'*, *sālkhudhāy* |

Three things to carry from it:

- **§5 (6)–(7)**: "safe place" = the Ascendant and the places configured to it (the 3rd
  ambiguous); "turned awry" (*perversus*) = 6th, 12th, probably 8th, perhaps 2nd — the places in
  aversion — and, of planets, the malefics. **Not** "cadent": "third from a pivot" is Hugo's cadent.
  Hugo errs once, at IV.8, making "good place *and* own domicile" into "safe place, namely its own
  domicile".
- **§7**: BA's cycle of the year has **three Ascendants** — profected, directed, calculated — and
  **no separate revolution chart with cusps**: "according to al-Andarzaghar the cycle of the year
  was really a set of transits" (pdf p. 35). Abū Ma'shar's twelve-cusp revolution (PN IV I.6) is
  a century later; whether his invention or standard by then Dykes cannot say.
- **§8**: Holden's Equal-House cusps in JN's charts are unjustified; "Abū 'Alī never uses the word
  'cusp'"; the syzygy is "the conjunction", not Holden's "New Moon".

**§9 defines the words Sahl leaves untranslated**: *jārbakhtār* "distributor of time" = bound lord
of the directed *hīlāj*; *jārzamān* "hour of the time" = the cutting point; *jār kanār* "limit of
time" = the last-resort *hīlāj* of III.1.10; *intihā'* = the profection's terminal sign;
*sālkhudhāy* = lord of the year; *nawbah* "turn" — JN Ch. 1's "lord of the nawbah" is the
*mubtazz* taking its turn, the Latin gloss "the luminary of the sect" being the translator's
error; *tamrīn* = the Moon's quarters; *wabāl* = detriment.

---

## 2. Book I (pdf pp. 47–63) — Prologue and the disagreements of the astrologers

The Prologue (pdf pp. 47–53) is Hugo's dedication and Māshā'allāh's bibliography: 255 authors,
twelve books of "Aristotle", thirteen of Hermes, four of Ptolemy, thirteen of Dorotheus, Valens's
ten, the *Zīj al-Shahriyār*, an Indian *Bhrgusamhitā*-like book of "12,000 birthdays". Nothing
operative.

- **I.1** (pdf pp. 54–58): the seven and the twelve govern births and plantings; a diurnal-hour
  temperament scheme (airy dawn, fiery morning, earthy afternoon, watery evening — Dykes fn 3);
  the three questions the book answers; *myriogenesis* (24,000 minutes an hour, fn 12); the
  latitude disagreements (Egyptians vs Ptolemy, Mars 4°02′ S / 3°?′ N vs 8°36′, fn 17: the values
  are Saturn's, misplaced).
- **I.2** (pdf pp. 58–59): climes; Babylonia in the 2nd (Egyptians) or 4th (Ptolemy) clime;
  errors in ascensions corrupt "the arisings of nativities for life … under the degree of the
  cycle itself from sign to sign" (fn 27: profections too).
- **I.3** (pdf pp. 59–60): the *hīlāj* chapter of Dorotheus quoted on arisings: Saturn, Jupiter,
  Mars at 6°/5° from the Sun count as arising "and thus are strengthened in the *qismahs*"; Mars
  to 18°, Venus/Mercury 19°, Saturn/Jupiter 15°; Ptolemy's Venus 6°52′ in the fourth quadrant.
- **I.4** (pdf p. 61): the five degrees above the Ascendant count with it (Ptolemy, "Marius" =
  Porphyry); others give the whole sign to the east if the degree is at 29°. Dykes fn 41:
  Māshā'allāh "seems to approve of this 5° rule, though it is unclear to what end".
- **I.5** (pdf p. 61): rectification by the Sun–Moon distance and the Moon's 15-day course
  (Antiochus). **I.6** (pdf pp. 62–63): stations from the *Zīj*; the superiors retrograde "after
  four signs"; Saturn's first station at 3 signs 25°29′ (*Alm.* XII.8); Ptolemy's 1°/100 years
  precession "plainly omitted in the *Zīj*" (sidereal).

---

## 3. Book II (pdf pp. 64–89, with printed p. 24 at pdf p. 407) — the conditions

**II.1 — the seven-fold corruption** (pdf pp. 64–65), each footnoted to its chapter: (1) arising
and sinking, the greater years, the stations; (2) with the Head or Tail; (3) the fortunes or
lights squeezed between the infortunes; (4) in the 6th or 12th; (5) falling, "in the opposite of
their own domicile — namely the *wabāl*"; (6) the same degree as an infortune; (7) retrograde.
Then the **nine-day rule**, identical to Sahl 1.22, 1–8 (Dykes's Sahl fn 171 cites this chapter):
Saturn and Jupiter at 6° or 5° from the Sun are "pertaining-to-arising … stars of greater years",
because in nine days the Sun withdraws 9° and they stand at 15°; Mars only when the Sun leaves
him by 10° (fn 14: BP read "ten days"); setting at 22° (Saturn, Jupiter) and 18° (Mars); a planet
that enters the rays within seven days "is useless for the *kadukhudhāh* and for life".

- **II.2** (pdf pp. 66–67): the inferiors' stations from the mean Sun; Venus arising at 19° in the
  fourth quadrant, second station at 48°; Mercury "copies Venus" (fn 23: 28° missing); Dorotheus:
  Venus and Mercury arising at 12° at dawn, sinking at 15° in the west. Sahl 1.22, 7 has 19° for
  both (Dykes's Sahl comment, `:1096`).
- **II.3** (pdf p. 67): "the Node of the coming-together and the opposition" = the syzygies, not
  the lunar nodes (fn 25). **II.4** (pdf pp. 67–68): the *buht* = 12°, the Moon's daily course;
  al-Qabīsī's seasonal-hour version is different. **II.5** (pdf p. 68): "the terror of the Head and
  Tail is whenever the Sun and the Moon or any star is being separated from the Head or Tail by
  12°… the threats of an eclipse" — a **12° Node orb stated for any star**.
- **II.6 — enclosure** (pdf pp. 68–69, Figure 1; Figure 2 at pdf p. 407): two infortunes in the
  Moon's sign on either side of her; or by square/opposition rays "while the solar rays do not
  touch the 7° between the Moon and the infortunes" (fn 30: the 7° is both the besieging interval
  and the breaking interval); the Sun's ray from any aspect within 4°–5° of the Moon "shatters the
  siege". Worked: Moon 10 Aries, Saturn 17 Aries, Mars 3 Aries.
- **II.7** (pdf p. 407): bad houses 6th, 12th, then 8th, 2nd, 3rd ("still, the Moon rejoices in the
  third"); worst 6th and 12th. **II.8** (pdf pp. 407, 70): *wabāl* = regarding its own domicile
  from the opposite, listed per planet; "another kind of ruin" = regarded by the infortunes from
  the opposite (fn 39: the whole-sign angles of the malefics); the sixth corruption "the same
  degree with the malevolents, or at least regarded from a tetragon or opposition, under that many
  degrees"; **void of course**: the Moon "applies to neither the fortunate ones nor the malevolents
  with her own body, nor does she regard any from the trigon, tetragon, hexagon, or opposition" —
  **no "within 30°" clause** (fn 41: Rhet. 39 only; the fuller definition "makes a void in course
  Moon extraordinarily rare").
- **II.9** (pdf pp. 70–71): *tamrīn*, the quarters, 7½ days. **II.10** (pdf p. 71): corporal
  application at "3° and just short of that", or by aspect "by that whole number of degrees" — the
  Hellenistic 3° moiety (fn 45).
- **II.11** (pdf pp. 71–73): sect = "rest"; Sun, Saturn, Jupiter diurnal; Moon, Venus, Mars
  nocturnal; **"Mercury is made diurnal with diurnal stars and nocturnal with nocturnal ones"**
  (fn 50: a corruption of Paul's benefic/malefic rule — Māshā'allāh "had no textual guidance for
  Mercury's sect"); *halb* stated obscurely (fn 54); overcoming/decimation from "a certain Roman
  professor" (Porphyry/Rhetorius) with the tenth-from confusion (fn 59).
- **II.12 — *dustūriyyah*, spear-bearing** (pdf pp. 73–75). Dykes has re-cut Hugo's paragraph
  into Rhetorius's three types and **added the defining phrases in brackets**: Type 1, a planet in
  a pivot in its domicile/exaltation regarded from a pivot by another in its domicile/exaltation
  (or, outside a pivot, in mutual aspect); Type 3, a diurnal planet accompanying a sect-mate
  planet in the east or MC in a diurnal birth — the Sun's spear-bearers precede him, the Moon's
  follow her, within 7°, the Sun's harmless only at 15°; Type 2, the lights in the Ascendant or MC
  outside their dignities, regarded by planets "at rest" that aspect the degree rising before the
  Sun / after the Moon, trigonal best, hexagonal weakest. **Type 3 is Dykes's reconstruction**
  (fns 65–66: "I have totally replaced Māshā'allāh's/Hugo's sentence here"). Not a fourth
  definition for the app; the same three Antiochus types Sahl 2.5 and 4.15 reflect.
- **II.13** (pdf p. 75): the quarters — Asc→MC diurnal, male, eastern, "the beginnings of human
  life"; MC→7th diurnal, female, southern, "the middle of life"; 7th→IC nocturnal, male, western,
  "the last things of life"; IC→Asc [nocturnal], female, northern, the patrimony and fame after
  death. **II.14** (pdf pp. 75–76): twelfth-parts, "multiply … by 12", 30° per sign from the sign
  itself (fn 78: Moon 16 Aquarius → 192 → Virgo); Dorothean, not Paul's ×13.
- **II.15** (pdf p. 76): male Sun, Mars, Jupiter, Saturn; female Venus, Moon; Mercury by sign or
  company; a female star made male when arising within 15°, between the 4th and 7th, or from the
  MC to the Ascendant [or in male/northern signs]; the reverse for males.
- **II.16 — the Moon's application and recession** (pdf pp. 77–79, Figure 3): Rhetorius Ch. 110's
  chart (Feb/Mar 601, fn 85), Egyptian bounds; a separation is "shaken" when the Sun's opposition
  falls between; the Moon in the last degree applies to none, in the first separates from none
  (fn 90: **no out-of-sign aspects**); "if the stars are 3° from the Moon … they are effective".
- **II.17 — the regards** (pdf pp. 80–89, Figures 4–7): four kinds of aspect — equatorial, by
  ascensional times, zodiacal, whole-sign — and four worked directions to the MC, Ascendant, IC
  and Descendant in Babylon's System A ascensions for a hypothetical chart at 51° N. "A regard
  from sign to sign is pointless" for prediction. Dykes fn 102 and Appendix A: "a historical
  exercise" — ascensional aspects are a crude approximation of primary directions. **Do not
  build from it**; PN IV III.1, 12 and Appendix A there are the specification.

---

## 4. Book III.1 (pdf pp. 90–116) — life, the *hīlāj*, the *kadukhudhāh*, the *jārbakhtār*

**III.1.1** (pdf pp. 90–92): the checklist of twenty-five preliminaries `[a]`–`[y]`, each footnoted
to Book II (fn 1: "several topics are missing … Hugo might not have been working with a complete
text"); the ship-building simile; the six questions of the first house.

**III.1.2** (pdf pp. 92–94) = Sahl 1.25, 8–14 and 1.29 (Dykes's Sahl fns 258, 305–309): the
mother's safety (Saturn in the Ascendant in a female sign, "difficult births"; Mars there "easy
and unexpected birth, as often happens on the road or in a bath"); then the **upbringing
sequence** `[3.1]`–`[3.5]`: lords of the Ascendant's triplicity (first and second) in an optimal
place → the sect light's triplicity lord → the Lot of Fortune's triplicity lord → Jupiter, then
Venus "in the fifteenth degree beyond the east" and at the end of the rising sign "does not save
from death" → the Moon safe in the Ascendant/MC/11th with a planet of the sect.

**III.1.3** (pdf pp. 94–98) = Sahl 1.30–1.32: those to whom life is denied. Operative sentences:
the Moon in a pivot with an infortune in the degree of the Ascendant or aspecting it by
tetragon/opposition "from the bound and degree" is fatal, unless Jupiter holds the Ascendant
cleansed; the Moon in the 4th with a malefic opposite "afflicts the native and mother with death
on the day of birth" unless she is in her own triplicity, domicile or exaltation with a fortune's
regard; enclosed and decreasing, the infortunes "do not yet signify death … until they extinguish
the benefit of the light"; the syzygy, the *kadukhudhāh* [fn 56: read *hīlāj*], the sect light's
triplicity lord, the Lot of Fortune and the Lot of Spirit all corrupted "discharges one already
dead"; the weighing rule — infortunes with two or three witnesses against one fortune, and the
reverse. Also the twelfth-part "bestows a not-middling effect".

**III.1.4** (pdf p. 98): parents' hatred; Fortune and Spirit for the luckiness of life.

**III.1.5 — the *hīlāj*** (pdf pp. 98–99): **Sun by day, Moon by night, "if their places are
cleansed and safe"; failing them the Ascendant's degree; failing it the Lot of Fortune; failing
that the syzygy.** Best places: the Ascendant, MC, "the domicile of hope" (11th); the Sun in a
male sign, the Moon in a female; Dorotheus adds the 7th–8th for the Moon in a male sign; for the
Ascendant, Lot and syzygy the gender argument "is of second importance". Dykes fn 70: "Hugo's
list differs quite a bit from *Nativities* §2". **Order differs from Sahl 1.15** (day: Sun,
meeting; night: Moon, fullness, Lot; then the Ascendant): BA puts the Ascendant second and the
syzygy last. See §9 #5.

**III.1.6 — the *kadukhudhāh*** (pdf pp. 100–101): the lord of the *hīlāj*'s **bound** by day
(the Moon's by night), "especially if it would have the dominion of the eastern sign or of the
Lot of Fortune or of the sign of the coming-together"; it must **aspect** the *hīlāj* ("the
testimonies"); the **share-counting rule**: domicile + bound beats triplicity + exaltation; bound
+ triplicity beats domicile alone and exaltation alone; more than two testimonies preferred,
"especially while it regards the east with its bound" and rules the hour, Lot or syzygy; one
testimony chosen only if it is in its own domicile, exaltation, bound or triplicity. A
*kadukhudhāh* that "diverts its own aspect from the *hīlāj*" leaves the native "deprived of the
benefit of a *kadukhudhāh*" (fn 79: the candidate *hīlāj* is normally rejected instead). No
testimonies → direct the degrees "up to where the detriment of an infortune falls". = Sahl 1.15,
13 and 1.20, 2–5 (the two-share rule).

**III.1.7 — the quantity of life** (pdf pp. 101–105): the four heads — `[6.1]` the *tasyīr* of the
Sun, Moon, Ascendant [as *hīlājes*] "and of the *kadukhudhāh*" to the malefics' bodies and rays
(fn 82: "the *kadukhudhāh* is not supposed to be directed"); `[6.2]` when they reach "their own
tetragon or opposition" (fn 83: Ptolemy and Valens conflated — see Appendix B); `[6.3]` the
*jārzamān*; `[6.4]` the Lot of Fortune (Valens III.11). Those who "wholly perish": Sun, Moon,
Ascendant and Lot generally corrupted. A malefic met "in a sign turned awry and under the rays"
kills "from the trigon and the hexagon not otherwise than from the tetragon or the opposition";
the Sun in the 6th/12th aspected by an angular malefic "suffocates at length". The *hīlāj*'s
"greatest circuit, the middle or the lesser"; the arc in ascensions "means that same amount of
hours or days, even months or years". `[6.4]` Valens's proportional method garbled (fn 96: the
greater years reduced by the fraction of the diurnal/nocturnal arc already travelled). **No
*kadukhudhāh*** → the lesser years of the Lot of Fortune's lord plus "how many degrees are
arising in the clime"; a corrupted birth gives only days, weeks, months. For non-survivors direct
the strongest of the four; "the east destroys more severely; after that, the Moon" (= Sahl 1.32,
11–14, which the app quotes).

**III.1.8 — the years** (pdf pp. 105–106), the table as Dykes corrected it (fn 104: "BP have made
mistaken corrections … Hugo himself got some things wrong"):

| | Greater | Middle | Lesser |
|---|---|---|---|
| Sun | 120 | 69½ | 19 |
| Moon | 108 | 66½ | 25 |
| Saturn | 57 | 43½ | 30 |
| Jupiter | 79 | 45½ | 12 |
| Mars | 66 | 40½ | 15 |
| Venus | 82 | 45 | 8 |
| Mercury | 76 | 48 | 20 |

(OCR "69 '/s", "66 Vs", unverified; the same two values recur as "69 Va", "66 'A" in JN Ch. 4's
table, pdf p. 279, and are the ordinary means (120+19)/2, (108+25)/2.) **The luminaries' middle
years are the ordinary mean here, not the 39½/39½ of *Gr. Intr.* Fig. 146 that the app carries.**
See §9 #1. The *jārbakhtār* named "the leader of life"; trouble "practically equal to death" comes
from it, and from "the cycle of years", transits, and the *hīlāj* first entering a malefic's bound
(fn 109: Valens III.3 — a direction is active on entering the bound).

**III.1.9 — long life** (pdf pp. 106–109): the sect light in the Ascendant, MC or 11th ("that
Dorotheus added the ninth, eighth and seventh … I do not believe is trustworthy enough");
**the Sun in Aries or Leo, the Moon in Taurus or Cancer, is both *hīlāj* and *kadukhudhāh***
(= Sahl 1.16, 1–2; Dykes's Sahl fn 113 reads Sahl with this passage; JN Ch. 3); the strongest
*kadukhudhāh* — in a pivot or succedent, in its own domicile, bound or triplicity, aspecting the
sect light's triplicity lord, "removed from retrogradation and scorching by a space of seven
days" — gives the greater years; a *hīlāj* from the Ascendant, Lot or syzygy "will not lavish the
greater years to the full extent". A fortune's aspect "from its own bound" mitigates (fn 115).
The *hīlāj*'s application to a planet in the second from a pivot, scorched, or within 3° of the
Ascendant's degree (fn 118) "afflicts with the most serious adversity". **Hermes's rule: after a
conjunction take the *hīlāj* first from the Ascendant, then the Lot; after an opposition, first
the Lot** — JN Ch. 2 encodes exactly this. Ptolemy: direct the Moon even when she is not *hīlāj*
(= Sahl 1.16, 7); the Ascendant *hīlāj* meeting a Moon corrupted in the root kills, and the
converse (= Sahl 1.16, 8–9); the syzygy's degree applying to the Head or Tail kills (= Sahl 1.16,
11, whose "the Tail indicates [illegible]" Dykes's Sahl fn 117 fills from here). The *hīlāj*
entering the infortunes' bounds "either destroys completely or urges forward a virtually mortal
trouble"; the Sun's or Moon's freedom in the root "promises escape".

**III.1.10 — the *jārbakhtār*** (pdf pp. 110–116, Figure 8): "the Lord of its bound (through which
it walks)" is the *jārbakhtār*; **the rate: a year per degree of the arisings, a month for 5′,
six days for 1′, a day for 10″** — identical to Sahl 1.18, 21 (`01_on_nativities.md` §5a). The
*jārbakhtār* in a malefic's bound, "when it is going to reach a malevolent" or the infortunes
regard that bound by square/opposition with the fortunes turned away, "afflict … with death or
ruin"; in a malefic's bound "afflicts with disease and detriment, but in the end it will free".
Fn 128: in practice the *jārbakhtār* "might often have been treated as the bound Lord of the
directed Ascendant". The **jār kanār**: if the five *hīlājes* fail, the Sun in a male sign or the
Moon in a female, angular or succedent, with the lord of the Ascendant or MC aspecting it "from
the direction of the tenth", gives "the complete years" — a last-resort releaser Sahl does not
carry. Retrograde stars "are virtually unable to lavish their gift of prosperity". **Gestation**
`[2]`: 258 days with the Moon at the Descendant, adding [2½] days per twelfth counter-clockwise
to 288 at the Descendant from the other side; an eighth-month birth "would not show one capable
of life" (= Sahl 1.8–1.9). **The Dorotheus example** (Carmen III.2, Figure 8): the Ascendant
directed through Mars (1 year 2 months 12 days), Venus (4 y 9 m), Mercury (to 19 y 7 m — fn 154:
the arithmetic multiplies degrees by 1.03, "practically at the equator"), Jupiter, Saturn
(mother's death), into Sagittarius and death at Saturn's 6th degree, "29 years, [10] months"; the
*jārbakhtār* delineated "according to both its own nature and that of its bound Lord" (fn 152).
**This is Sahl 1.18's source and the only worked distribution in either book.**

---

## 5. Book III.2 (pdf pp. 117–135) — the seven-fold prosperity scheme

This is the passage Dykes's comment on Sahl Ch. 2 names ("Sahl's seven categories do not
exactly match the neat organization of BA", with his table). **III.2.0** lists the seven questions
and, under each, the items:

| # | Question (III.2.0) | Items | Delineated at |
|---|---|---|---|
| 1 | amount of prosperity | `[1.1]` fixed stars on Asc/MC/Sun/Moon; `[1.2]` first and second triplicity lords of the sect light, their place from the Moon and regard to her and the Lot; `[1.3]` the sect light and its lords "in the fifteenth degree of the first sign"; `[1.4]` the Lot of Fortune, its lord, in own triplicity/exaltation/bound; `[1.5]` lords of the Asc, MC, 11th; `[1.6]` the Moon's positions; `[1.7]` benefics/malefics in the **eleventh from the Lot**; `[1.8]` the Lot of Money and lord | III.2.1 |
| 2 | its disappearance | `[2.1]`–`[2.12]`: the sect light's triplicity lords corrupted; the Lot and lord corrupted; malefics on the 7th's degree; infortunes out of sect in the 2nd; in the 4th and MC without Jupiter; in the eleventh from the Lot; Saturn with the Moon in a pivot or Mars's aspect; the Lot regarding neither the Sun nor its lord; the syzygy's lord in the 6th/12th; the Moon's recession/application; enclosure; the *kadukhudhāh* awry | III.2.2 |
| 3 | a mediocre life | `[3.1]`–`[3.5]`: the Lot and who regards it; the "at rest" triplicity lords "namely the fifteen degrees from the beginning of the east"; fortunes regarding the Lot; lords of Asc/MC/11th; lords of the sect triplicities | III.2.3 |
| 4 | raised from low to high | `[4.1]` infortunes in pivots, fortunes succedent; `[4.2]` the Moon from malefics to benefics; `[4.3]` sect planets; `[4.4]` the sect triplicity lords' "distribution"; `[4.5]` Asc and Lot and lords; `[4.6]` "the Lot decrees the beginnings of life, and its Lord the last things"; `[4.7]` the Moon's speed; `[4.8]` MC and 7th | III.2.4 |
| 5 | chronic adversity | `[5.1]`–`[5.5]`: the Ascendant's [Sahl: sect light's] triplicity lord and the Lot; the Lot regarding neither the Moon nor Jupiter/Venus with malefics angular; lords of the pivots; the 2nd and its lord; the Lot of Money | III.2.5 |
| 6–7 | own hands; violence | `[6-7.1]` the bound the Lot falls in; `[6-7.2]` the Lot's triplicity lords; `[6-7.3]` the eleventh from the Lot | III.2.6 |

**III.2.1 `[1.1]` — the fixed stars** (pdf pp. 120–126): 27 stars in seven nature-groups with
Persian names and positions (Spica 0°06′ Libra "*Haarf*", Vega 24 Sagittarius, Fomalhaut 12°50′
Aquarius: Venus–Mercury; Alphecca 15°20′ Libra "*Sarben*", Zuben Eschamali 27°50′ Libra, Castor 27
Gemini: Jupiter–Mercury; Regulus 6°10′ Leo, Antares 16°20′ Scorpio, Sirius 21°20′ Gemini,
Menkalinan, Altair: Jupiter–Mars; Rigel, Rukbat, Algol, Capella, Alnilam: Jupiter–Saturn; Pollux:
Mars; Bellatrix, Procyon, Betelgeuse, Alpheratz: Mars–Mercury; Toliman, θ Eridani: Venus–Jupiter;
Alphard, Zosma, Denebola; Aldebaran/Antares), Appendix D tabulates them with J2000 positions.
This is Sahl 2.2's list (Dykes's Sahl fns 7, 9, 71–72 compare them: Sahl omits Alphecca as a
fifth Venus–Mercury star and puts it under Jupiter); the app already carries the 28 stars and
declares 2.2's delineation unbuilt.

**`[1.2]`–`[1.8]`** (pdf pp. 126–129): both sect triplicity lords cleansed and angular → "perpetual
luckiness for all the days of his life", firmer if received by the lord of the Lot or of the 2nd;
**`[1.3]` the triplicity lord "from the first degree of the sign up to the fifteenth, wholly with
the degrees of the arisings of the Sun, and it in a pivot"** → dignities, attendants, "nor will
he ever … be deprived of dominion"; in the last 15° "an underofficial or scribe or viceroy" (fn
70: Dykes reads ascensions from the axial degree, as at Sahl 2.3, 4 fn 82–83 — both texts
"misunderstood"); `[1.4]` the lord of the Lot eastern, free, regarding it, in the 5th/11th
promises luckiness; `[1.5]` fallback to the lords of Asc/MC/11th; `[1.6]` the Moon in the 2nd,
increasing, out of the rays [Sahl fn 94: "separating from the Node by at least 12°"], applying to
fortunes, in tetragon to the Sun, free of Mars; `[1.7]` **the eleventh from the Lot "strong like
the eleventh from the east"** (fn 89: Valens II.21); `[1.8]` **the Lot of Money: "from the Lord of
the house of money to the degree of that same lodging-place, with the degrees of the east being
added", day and night** — the app's `assets_lord2`.

**III.2.2–2.6** (pdf pp. 129–135): the sentence-level parallels Dykes's Sahl fns 227–268 record.
Notable "other" readings: `[2.9]` the syzygy's lord in the 6th/12th, or the Sun in the syzygy's
sign there; `[4.4]` the triplicity lords in each other's domiciles with the third in the 7th
"furnish the last parts of life" (the only use of the third lord); `[4.8]` malefics eastern
regarded by fortunes "from their own triplicity" (Sahl: "from opposition"); III.2.5 is read
throughout with Sahl (fns 121–127, six emendations); `[6-7.2]` the first triplicity lord in
aversion, the second regarding, "now profit, now detriment … to the extent that he would be in
total starvation"; **III.2.6's timing paragraph is lacunose** ("from the greater cycles of the
stars, the middle and the lesser, even from the *jārbakhtār*, from the *kadukhudhāh* […]", fn
137) — Sahl 2.22 is its fuller form.

---

## 6. Books III.3–III.12 (pdf pp. 136–229) and Book IV (pdf pp. 230–271)

### 6a. The topical books, in one line each

- **III.3 siblings** (pdf pp. 136–144): the two Lots — Saturn→Jupiter "by night and day"
  (Hermes) and Mercury→Jupiter (Valens), "each is certain and reliable" (= Sahl 3.11, 4; fn 12:
  **BA does not reverse the Saturn–Jupiter Lot at night**, unlike Carmen/Valens); Sun/Saturn
  older brothers, Jupiter/Mars middle, Mercury younger, Moon older sisters, Venus younger;
  counting from the MC to the Ascendant a sibling per sign; the Moon at 3 Scorpio "snatches the
  fetus away"; III.3.7 the death of siblings "in the cycle of the Mercurial year" (fn 59: Sahl's
  fuller instruction). JN Chs. 12–15 digest it.
- **III.4 parents** (pdf pp. 145–158): the planetary joys listed as "the *ateci*" (Mercury 1st,
  Moon 3rd, Venus 5th, Mars 6th, Sun 9th, Jupiter 11th, Saturn 12th; Intro §9: *ateci* = Valens's
  figure-description); Buzurjmihr's legitimacy rule from the Lot of Parents (III.4.2; Sahl 4.1
  fn 9: this Lot is the Lot of Fortune); the Sun's twelfth-part in the 12th; the Sun in the 12th
  = father's servitude; **first triplicity lord = first part of the father's life, second = second
  (III.4.3 fn 32: the third left out, following Valens)**; which parent dies first by the Lots
  directed "in the degrees of the arisings", the lords' direction, the syzygy ×12 (Valens II.31
  adapted, fn 98); Mars in the left tetragon of the Sun toward the IC, sudden death "before the
  son knew him". JN Chs. 16–19.
- **III.5 children** (pdf pp. 159–166): Lot Jupiter→Saturn (reversed, fn 22), Time of Children
  Mars→Jupiter (III.5.1 `[4.2]`, unreversed; fn 10: "Mars signifies parturition"), Male
  Moon→Jupiter, Female Moon→Venus (Paul's, fn 17); the Jovial triplicity lords count a child per
  sign to the Ascendant, two for bicorporeal; children in adolescence if the "leader of children"
  is in the Asc/MC/11th, middle years 2nd/7th/8th, old age 4th/5th; **the year of a child when
  transiting Jupiter reaches the Mars–Jupiter Lot or the profection reaches natal Jupiter/Venus
  (III.5.5 `[4.2]`)** = Sahl 5.3, 8; JN Ch. 21.
- **III.6 illness** (pdf pp. 167–178): the eye rules; **the eye-harming degrees `[1.5]`** — Leo
  16–18, Scorpio 8, 9, 10, 23, [Sagittarius 6–9], Taurus 6–10, Cancer 9–15, Aquarius 18–19,
  Capricorn 26–29 as Dykes prints them **from Sahl** (fns 36–43 give Hugo's own: Leo 18, 28, 29;
  Scorpio 17, 19; Taurus 6, 7, 8, 10; Aquarius 10, 18, 19; Sagittarius omitted); the sect light
  takes the right eye; oriental corrupted stars "spoil with decline", occidental "with pain
  alone"; Lot of Disease Saturn→Mars by day, reversed; **the second triplicity lord of the 4th =
  chronic illness, the first = death** (fn 54, Carmen IV.1.81–83); the melothesia; the Lot of
  Fortune and Spirit in Sagittarius–Pisces → gout; timing of illness by quadrant (III.6.8:
  Asc→MC youth, MC→7th middle age, 7th→IC last years; oriental stars adolescence, occidental old
  age). JN Ch. 24.
- **III.7 marriage** (pdf pp. 179–196): Lots — Men Saturn→Venus (reversed by night, fn 7), Women
  Venus→Saturn, Eros Fortune→Spirit, "Happiness and Wedding" Venus→the 7th's pivot (reversed,
  fn 87), the Sun→Moon Lot "the degrees of Venus being added" (fn 31: by day added to Venus, by
  night subtracted); number of wives = signs from the MC to Venus (women: to Mars); the Venus
  triplicity lords' condition; Jupiter's transit to the Lot or natal Venus without Saturn's
  aspect gives the year (III.7.10), and **the profection "made from the east" reaching the Lot of
  Marriage's sign, with Saturn's aspect denied** = Sahl 7.4; III.7.11 synastry (Dykes's summary of
  Carmen II.5.12–15 in fn 34); III.7.12 who dies first; III.7.13 sodomy. JN Chs. 25–26.
- **III.8 death** (pdf pp. 197–202): the fourteen heads; **`[4]` the Lot of Death "by night and
  day from the Moon to the degree of the eighth itself, and it is cast out from the degree of
  Saturn"** (Intro fn 65: "degree of the eighth" may be the first degree of the eighth sign; Sahl
  "the eighth place"); `[9]` the Lot of Killing — III.8.0 "under a nocturnal birth from the eastern
  Lord to the Moon … under a diurnal [birth the reverse]" (bracketed from Rhetorius for Hugo's
  "Lord of the domicile of the Sun") but **III.8.1 `[9]` "from the eastern Lord to the Moon, with
  the degrees of the east being added by day, by night the converse"** = Sahl 8.2, 17; `[13]` the
  Moon **40 days** after birth applying to infortunes "cut down in one blow"; `[14]` Mercury 29°
  (28°) and Venus 47° (48°) from the Sun, the maximum elongations; **most of III.8.1's items 2–8
  are Dykes's summaries in `[{n}]` brackets from Rhetorius 77 and Carmen — Hugo lacks them.**
- **III.9 travel** (pdf pp. 203–206): **`[1]` "the place of the Moon under the third day of the
  nativity"**; the Lot of Travel "from the Lord of the house of travel to the degree of the house
  itself, not without the degrees of the east", day and night, "with Antiochus attesting" (fn 29:
  not in surviving Antiochus; Sahl "the ninth place"); Mars regarding the Moon on the third day
  "establishes travel"; the sect triplicity lords in their own triplicity "speak against travel".
- **III.10 work** (pdf pp. 207–220): the nine heads; Mercury, Venus, Mars; the Moon's application
  after the syzygy; the Lot of Works Mercury→Mars by day, reversed; Rhetorius 82–96 line by line
  (III.10.6–8). = Sahl 10.1.1–10.1.5 (Dykes's Sahl fns 4–13, 29, 78, 93, 104, 110).
- **III.11 slaves** (pdf p. 221): two Lots — Mercury→Moon ("by day … by night the converse",
  ambiguous) and Mercury→Fortune (the Hermetic Necessity); "I consider the Lot from Mercury to the
  Moon to be more certain"; fn 3: al-Andarzaghar "expressly said these two Lots must be used
  together". = Sahl 6.10, 20; JN Ch. 22.
- **III.12 friends** (pdf pp. 222–229): Lot of Friends Moon→Mercury, reversed; the four Lots
  (Fortune, Spirit "the Absent", Eros "Pleasure or Appetite", Necessity); synastry by Moons, Lots
  of Fortune, lights in "obedient" signs (Appendix C: should be seeing/hearing); **III.12.6 the
  *jārbakhtār* and friendship**: "you will note the *jārbakhtār*, namely whenever the distributor
  of the year will be corrupted under even the root of the nativity itself … found in the east of
  the friend's birth under the cycle of the year, your benevolence will grow cold" (fn 33: BP take
  this as the *sālkhudhāy*); III.12.9 elections for friendship by the Moon in "the east of the
  annual cycle". = Sahl 11–12 (Dykes's Sahl fns 2, 9, 12–13, 61).

### 6b. Book IV — the cycle of the year (al-Andarzaghar via Da.)

- **IV.1** (pdf pp. 230–232): the return computed by adding "six hours and one-fifth of an hour"
  per year (fn 1: a sidereal year of 365.25833 days); the profection a sign per year from the
  Ascendant; then the ten heads `[1]`–`[10]`: the profected sign in root and revolution; the
  *sālkhudhāy* in root and revolution (`[3.1]`–`[3.7]`); "the eastern distribution under that
  year" `[4]` (the directed Ascendant's bound and its lord); "the east of that year" `[5]` (the
  calculated Ascendant); its lord `[6]`; the Moon `[7]`; the Lots `[8]`; the *jārbakhtār* `[9]` —
  "namely, is the direction going from a fortune to an infortune, or from a benevolent to a
  benevolent…"; the *firdāriyyāt* `[10]`. **The *sālkhudhāy* "is even the Lord of the Year", the
  *jārbakhtār* "both distributes the years and differs from the one receiving"; a Moon corrupted
  at the cycle "either kills or impairs" if the root testifies death.**
- **IV.2–IV.7** (pdf pp. 232–241): the lord of the year per planet, in three registers — good
  condition, bad condition, and the Lots that fall with it (`[8]`), with the class of native
  ("if the native would be considered lofty in the root … mediocre … lower", IV.3) and the
  sign-kind (own, friend's, enemy's, peregrine, human, bestial) naming the source of the good or
  harm. Saturn (Da. 130–138), Mars (143–153), Jupiter (139–142), Venus (154–159), Mercury
  (160–165), Sun and Moon (one paragraph). Dykes reads Hugo with Da. in some 30 footnotes.
- **IV.8 — the *jārbakhtār*** (pdf pp. 242–244): "the Lord of the bound of the *hīlāj* itself is
  the *jārbakhtār*, and it is called the 'distributor of the year'"; example, the Sun at 1
  Aquarius → Mercury's first 7° → so many years (fn 81: by oblique ascensions). Then the
  **four-way rule**: a benefic's distribution with the *jārbakhtār*, *sālkhudhāy*, Moon and
  annual east all well placed and aspected by benefics → "the highest dignity"; the same with those
  four corrupted → good and bad equally; a malefic's distribution under benefics' regard → mixed;
  a malefic's distribution, itself pressed by malefics in the root, regarding the *hīlāj*'s bound
  in root and revolution, with the four corrupted → "the year will truly be fatal"; a malefic
  distributor well placed in the root → success; **a lucky *jārbakhtār* with a corrupted
  *sālkhudhāy* (or the converse): "the stronger and luckier place of whichever one under the natal
  root" decides** (fn 86, Da. 178). Then "conveying" and "receiving" between distributors (fn 87:
  unclear whether bound-handover or the transiting distributor's applications).
- **IV.9–IV.13** (pdf pp. 244–250): the distribution of Saturn, Jupiter, Mars, Venus, Mercury, each
  by the planets "regarding that bound" (fn 89: "the partners or participators with the
  *jārbakhtār*") — the ancestor of PN IV III.3–7. E.g. Saturn's bound regarded by Venus → marriage
  and birth; by Saturn or Mars, with no benefic "from a strong place" → death "by some windiness
  or an enemy hand"; Mars regarding Saturn "snatches away full brothers"; the Sun's regard "frees
  the native from death, but kills the father".
- **IV.14 `[5]`** (pdf pp. 250–253): the annual east's natal house; a malefic in the SR Ascendant
  "and the same in the same place in the root, it is wholly dangerous"; the lights at the cycle in
  the 7th or 4th applying to infortunes "destroy the parents in that year"; a malefic at the cycle
  on the natal Moon; the year reaching the 6th "will attack with a serious illness"; the
  *sālkhudhāy* returning to the natal Ascendant under malefics "wholly fatal" if the root agrees;
  the kinship of the planet with the *sālkhudhāy* and *jārbakhtār* names the source (Venus women,
  Jupiter kings, lights parents, Mars violence, Mercury controversies); `[8]` the Lots with the
  year lord (Da. 166–169 summarised by Dykes).
- **IV.15 the *intihā'*** (pdf pp. 254–255, Figure 9): natal Ascendant Cancer, the year to the
  9th (Pisces, Jupiter's), the SR Ascendant Scorpio so that Cancer is the SR's 9th; the Moon with
  Saturn in Sagittarius — "the reinforcement of testimonies" (fn 153: the example is incomplete).
- **IV.16 monthly, daily and hourly rulers** (pdf p. 256): rebuilt by Dykes from Da. 189 (Hugo
  lacunose): count days from birth in seven-day cycles, the lord of the Ascendant ruling the
  first week, then the planet below it, back to Saturn after the Moon; the planet ruling the week
  in which the cycle falls also rules the first day of the year and its first seventh. Hugo's own
  remnant assigns the sevens to the **signs** from the east, not to the planets (fn 154).
- **IV.17–IV.25 the *firdāriyyāt*** (pdf pp. 257–271): diurnal Sun 10, Venus 8, Mercury 13, Moon 9,
  Saturn 11, Jupiter 12, Mars 7, Head 3, Tail 2; nocturnal from the Moon 9, Saturn 11, Jupiter
  12 "until the continuous repetition comes to be through the rest of the stars"; each divided
  by seven, the lord first — sub-periods stated: Sun 1 y 5 m 4 d; Venus 1 y 1 m 21 d (Da. 79 for
  Hugo's 26); Mercury 1 y 10 m 8 d; Moon 1 y 3 m 13 d; Saturn 1 y 6 m 25 d 18 h; Jupiter 1 y 8 m
  16 d; Mars 1 y. **Hugo omits the Nodes-last rule** (fn 228: Da. and Abū Ma'shar put the Nodes
  after all seven, "as the native enters his 71st year"); the Saturn–Mercury sub-period is
  supplied from Abū Ma'shar (fn 208, "no Saturn–Mercury period in Da. or Hugo"). The
  delineations are Da. 72–127 with Abū Ma'shar's variants footnoted. IV.25 ends with the Head
  in the Ascendant/2nd/3rd (royal life; innumerable resources; charge of the brothers) and the
  Tail the reverse — the seed of JN Ch. 48.

---

## 7. Where Sahl's *Nativities* draws on BA/JN

From Dykes's footnotes in `on_nativities.md` (line numbers there) and the chapter parallels.
"MORE/OTHER" = what the source has that Sahl does not, or has differently.

| Sahl | BA / JN | Sahl line | Source says MORE or OTHER |
|---|---|---|---|
| 1.8–1.9 gestation | BA III.1.10 `[2]` | — | BA: 258 days at the Descendant, +2½/twelfth to 288; eighth-month non-viable |
| 1.15 releaser (Nawbakht) | BA III.1.5; JN Ch. 2 | `:778` | **OTHER order**: BA Sun/Moon → Asc → Lot → syzygy; JN sect light → other light → Asc or Lot by conjunctional/preventional → syzygy, each needing an aspecting lord of the five dignities |
| 1.16, 1–2 both at once | BA III.1.9; JN Ch. 3 | `:778` fn 113 | JN adds: the Lot as *hīlāj* takes only the domicile, exaltation or bound lord; Asc/Lot/syzygy exempt from the gender test |
| 1.16, 4–11 | BA III.1.9 (Ptolemy on the Moon; Asc/Moon cross rule; syzygy to the Head) | `:778`, `:804` fn 117 | BA: "the Tail" too; Sahl's illegible clause |
| 1.18, 21–22 rates | BA III.1.10 | — | identical; BA adds the Carmen III.2 worked example |
| 1.20, 2–5 two-share rule | BA III.1.6 | — | BA counts shares: domicile+bound > triplicity+exaltation; bound+triplicity > any single |
| 1.20, 7–34 years | BA III.1.9; JN Ch. 3 | — | **JN MORE**: a demotion ladder (angle/succedent/cadent; not oriental −1; occidental+peregrine −1; +retrograde+burned → days) |
| 1.21 aspects to the house-master | JN Ch. 4; BA III.1.7 `[6.4]` | `:1021` fn 160, `:1084` fn 170 | **JN OTHER**: fortunes' squares/oppositions add nothing (Sahl 8 as emended: they add); Mercury adds/subtracts by company; Mars the worst impeder; Nodes ±¼ graded by closeness, no 12° orb |
| 1.22 easternness | BA II.1–II.2 | `:1069`, `:1100` fn 171 | BA II.2: Venus/Mercury 19° (Carmen 12°/15°); Mars "10°" (BP: ten days) |
| 1.23 Māshā'allāh on the lifespan | BA III.1.7 `[6.1]`–`[6.2]`; Appendix B (5) | `:2189` fn 383 | Dykes: "direct the *kadukhudhāh*" is a conflation with the *jārbakhtār* — "apparently an error" |
| 1.25, 8–14 mother's safety | BA III.1.2 `[1]`–`[2]` | `:1565` fn 258 | Rhetorius 55 / Carmen I.3 |
| 1.29 upbringing | BA III.1.2 `[3]`; JN Ch. 1 | `:1783`–`:1909` fns 302–326 | JN MORE: life = degrees between the *mubtazz* and the malefics, as days/months/years; profection to an angular malefic; Ascendant directed a month per degree in year one; the Moon's 3rd and 7th day |
| 1.30–1.32 short lives | BA III.1.3, III.1.7 `[6.3]`–`[6.4]`, "III.1, 21–24" | `:1981`, `:2303` fn 406 | BA: the *jār kanār*; Valens's Lot-of-Fortune years; "the east destroys more severely; after that, the Moon" |
| 2.1–2.21 the seven classes | BA III.2.0–III.2.6 | `:2953` table | BA keeps 7 questions cleanly; Sahl doubles "high to low" and merges "own hands" with "violence" |
| 2.2 fixed stars | BA III.2.1 `[1.1]`; App. D | `:3027`–`:3382` fns 7, 9, 71–72 | Alphecca placed differently; BA never has "three" Venus–Mercury stars only |
| 2.3 | BA III.2.1 `[1.2]`–`[1.8]`; JN Ch. 7, 9, 50 | `:3420`, `:3440`, `:3470`, `:3502` fns 84, 86, 94, 103 | BA `[1.7]` the eleventh **from the Lot**; JN Ch. 7's twelve worked charts |
| 2.15 Lot of assets | BA III.2.1 `[1.8]`; JN Ch. 11 | `:3829` fn 167 | JN: lord of the 2nd in the twelve houses; lord of 2nd/lord of Asc application direction |
| 2.16 middling | BA III.2.3 | `:4135` fn 227 | — |
| 2.17–2.18 falling | BA III.2.2 | `:4159`–`:4207` fns 228–242 | BA `[2.9]` the Sun in the syzygy's sign in the 6th/12th; BA `[2.12]` the *kadukhudhāh* awry |
| 2.19 rising | BA III.2.4 | `:4237`–`:4261` fns 248–252 | BA `[4.7]` at the pre-natal lunation |
| 2.20 always miserable | BA III.2.5 | (BA fns 121–127 read Hugo with Sahl) | — |
| 2.21 own hands / injustice | BA III.2.6 | `:4303`, `:4325` fns 264, 268 | BA: "dependent on others" |
| 2.22 timing of fortune | BA III.2.6 end | — | BA lacunose; JN Ch. 8 the clean version |
| 3.1–3.12 siblings | BA III.3.0–III.3.7; JN 12–15 | `:4369`–`:5059` | BA: the Saturn–Jupiter Lot unreversed |
| 4.1 paternity | BA III.4.2 | `:5133`–`:5135` fns 8–9 | Buzurjmihr; "Lot of Parents" = Lot of Fortune |
| 4.2–4.7 | BA III.4.1, III.4.3 | `:6085` fn 214 | BA III.4.3: the Sun's twelfth-part in the 12th |
| 4.12 al-Khayyāt on directions | JN Chs. 17–19 | `:5887` | JN MORE: the parents' *hīlāj* chains and the years comparison |
| 4.19–4.20 which dies first; lifespans | BA III.4.6, III.4.7, III.4.9 | `:6218`–`:6384` fns 241–277 | BA "sudden" for Sahl's illegible word |
| 5.1–5.6 children | BA III.5.1–III.5.5; JN 20–21 | `:6547`–`:7132` | BA: Paul's male/female Lots; JN 21: profection triggers |
| 6.1–6.8 illness | BA III.6.0–III.6.8; JN 24 | `:7247`–`:8434` | BA lists nine items (Sahl 2–8); Hugo's variant eye degrees |
| 7.1–7.13 marriage | BA III.7.0–III.7.13; JN 25–26 | `:8694`–`:10199` | BA III.7.3 has Mars/Mercury/Venus as Lot lords (Sahl omits); JN 26: SR Ascendant in the 7th → betrothal |
| 8.1–8.6 death | BA III.8.0–III.8.1; JN 37 | `:10303` fn 5, `:10753` fn 94 | BA: 14 heads; the Lot of Death cast from Saturn; the 40th-day Moon |
| 9.1–9.4 travel | BA III.9.1–III.9.2; JN 27–28 | `:10781`–`:10933` fns 3, 18, 34–38 | BA: the Moon's third day as item `[1]` |
| 9.5 religion | JN Ch. 29 | `:11141` fn 71 | not in BA |
| 10.1 work | BA III.10.1–III.10.8; JN 30–33 | `:11433`–`:11904` | BA III.10.6 (Ptolemy's triads) which Sahl omits |
| 10.x boldness | JN Ch. 34 | `:12477` fn 213 | — |
| 11 friends | BA III.12.1–III.12.6 | `:12571`–`:12895` fns 2, 9, 12–13, 61 | BA III.12.6 the *jārbakhtār* and friendship; III.12.9 elections |
| 12 enemies | JN Ch. 36 ('Umar); BA III.11.1 (slaves) | — | BA: the two slave Lots used together |
| 6.10, 20 Lot of slaves | BA III.11.1; JN Ch. 22 | — | reversal disputed (JN fn 130) |

---

## 8. Doctrines that bear on the app

Numbered; each with the passage, what `app.py` does, and a Class 1–5 tag (`02_reconciliation.md`
scheme). **Canon-only** applies to everything here: BA/JN are corpus, not course text; a
Class-1 item is a candidate supplement row, not a build order.

1. **The luminaries' middle years.** BA III.1.8 (pdf p. 105) and JN Ch. 4 (pdf p. 279) both
   print Sun 69½, Moon 66½ — the ordinary mean. `PLANETARY_YEARS` carries 39½/39½ from *Gr.
   Intr.* Fig. 146 with a comment forbidding "correction", citing Valens VII.5's halved-great
   construction; `sahl_house_master_years` uses it. Two more witnesses, independent of each
   other, against the value in use. **Class 2** — a corpus disagreement now three-against-one
   (Fig. 146; PN IV I.8, 12 read the Moon as 39½). Decision for the owner; the OCR is unverified
   but the arithmetic is exact in both places.
2. **JN Ch. 3's years ladder** (pdf pp. 408, 278): angle → greater, succedent → middle, cadent →
   lesser, each with "own domicile/exaltation/triplicity, oriental, free from the bad ones,
   retrogradation and burning"; not oriental → one grade down; occidental and peregrine → middle
   to lesser; occidental, peregrine, retrograde, burned → "the lesser years and months … to days".
   The app grades by Sahl 1.20's thirty-four sentences and reports "1.20 silent" where none
   reaches the case. **Class 1** — a complete fallback ladder for the silent cases, as a
   labelled supplement.
3. **The Nodes' quarter** (JN Ch. 3): the Head "before or after" adds ¼ "and by how much more it
   were closer to it in degrees, it will be better"; the Tail subtracts ¼, "especially if the Sun
   or the Moon were the *kadukhudhāh* (but the Moon takes more detriment)". The app applies ±¼
   with a 12° orb to both (Sahl 1.21, 11–12 gives 12° for the Tail only; `01_on_nativities.md`
   §1c). **Class 4** for the ±¼; JN gives no orb and grades by closeness — and BA II.5's 12° "for
   any star" is a second witness for the orb the Head lacked.
4. **The 1.21 additions ↔ JN Ch. 4** (pdf p. 279): a fortune conjunct or by trine/sextile adds its
   own lesser years ("middling in strength, so many months; more unsound, days or hours"); a
   malefic conjunct or by square/opposition subtracts its lesser years; **"the square or opposite
   rays of the fortunes add or subtract nothing … just as the sextiles and trigons of the
   infortunes make no addition nor diminution"**; Mercury with fortunes adds, with malefics
   subtracts; "of all of those which impede the *kadukhudhāh* more, it is Mars". The app declares
   "the 1.21 additions" not applied. **Class 5**, with the note that JN's rule contradicts Sahl
   1.21, 8 as Dykes emends it ("<not> withhold … but will even add") — if built, the two disagree.
5. **Releaser order.** BA III.1.5 and JN Ch. 2 order the candidates differently from Sahl 1.15
   (§7, row 2); JN's conjunctional/preventional switch is Hermes's rule at BA III.1.9. The app
   follows Sahl. **Class 4** (the code matches its text); record the disagreement on the
   Releaser tab if any note is added.
6. **Both *hīlāj* and *kadukhudhāh*** (BA III.1.9; JN Ch. 3; Sahl 1.16, 1–2): Sun in Aries/Leo,
   Moon in Taurus/Cancer. `both_at_once` in `sahl_releaser`. **Class 4.** JN adds the Lot's
   restriction to domicile/exaltation/bound lords and the Asc/Lot/syzygy gender exemption —
   **Class 1**, minor.
7. **The distribution rate** BA III.1.10 = Sahl 1.18, 21: 1° = 1 year, 5′ = 1 month, 1′ = 6 days,
   10″ = 1 day, by ascensions. **Class 4.**
8. **Directing the house-master** (Sahl 1.23, 2; BA III.1.7 `[6.1]`–`[6.2]`): Dykes, Appendix B
   (5), pdf p. 387: "instructions to direct the *kadukhudhāh* itself. This is apparently an error
   … the *jārbakhtār* is thus being conflated with the *kadukhudhāh*." `sahl_house_master_direction`
   implements 1.23, 2 as Sahl states it and quotes him. **Class 4** for fidelity; the caption
   could carry Dykes's caveat. Not a build change.
9. **Lot of Death** BA III.8.0 `[4]`: Moon → degree of the 8th, cast from Saturn. The app's
   `death` is Saturn-projected, with a whole-sign-eighth variant that Intro fn 65 (pdf p. 40)
   independently motivates. **Class 4**, strengthened.
10. **Lot of the Killer** BA III.8.1 `[9]` (day: lord of the Asc → Moon; night reversed) = Sahl
    8.2, 17 = the app's `killer`. III.8.0 `[9]` prints the sects reversed (partly Dykes's
    bracket). **Class 4**; the BA-internal inconsistency recorded.
11. **Lot of Travel** BA III.9.1 `[9]` (lord of the 9th → degree of the 9th, day and night) = the
    app's `travel` (`lord9`→`cusp9`, unreversed). **Class 4.** Intro fn 65's "first degree of the
    sign" reading applies here too (Sahl "the ninth place"); the app has no whole-sign variant for
    this one.
12. **Lot of Money** BA III.2.1 `[1.8]` (lord of the 2nd → degree of the 2nd, day and night) =
    `assets_lord2`. **Class 4.**
13. **Sibling Lots** BA III.3.2: Saturn→Jupiter "by night and day" (unreversed, BA fn 12) and
    Mercury→Jupiter; = `siblings_hermes`, `siblings_valens`, both unreversed. **Class 4.**
14. **Children's Lots** BA III.5.1: Jupiter→Saturn reversed (`children_hermes`), Mars→Jupiter for
    the time (`children_timing`, unreversed — BA agrees), Moon→Jupiter male, Moon→Venus female
    (Paul's; not carried; `NOT_IMPLEMENTED_COVERAGE` lists "male/female (3.13, 20)"). **Class 4**
    for the three; **Class 5** for Paul's pair, now with a stated formula in the corpus.
15. **Lot of Disease** BA III.6.3 `[2.3]` Saturn→Mars by day, reversed = `chronic_illness`.
    **Class 4.** **Lot of Works** BA III.10.1 `[6]` Mercury→Mars by day, reversed = `work_action`.
    **Class 4.** **Lot of Friends** BA III.12.1 Moon→Mercury reversed = `friends`; Eros
    Fortune→Spirit = `desire`; Necessity Spirit→Fortune = `necessity`. **Class 4.**
16. **Marriage Lots** BA III.7.1: men Saturn→Venus reversed by night (BA fn 7), women
    Venus→Saturn (= `marriage_men`, `marriage_women`); Venus→the 7th's pivot **reversed by night**
    (fn 87); Sun→Moon "added to Venus by day and subtracted from Venus by night" (fn 31). The last
    two are in `NOT_IMPLEMENTED_COVERAGE`; BA supplies their night rules. **Class 5**, better
    specified.
17. **Lot of Slaves** BA III.11.1 Mercury→Moon (= `slaves`, reversed; BA's reversal clause is
    ambiguous, JN fn 130 records the dispute), paired with Mercury→Fortune (= `enemies_necessity`)
    "must be used together" (al-Andarzaghar via al-Qabīsī). **Class 4**; the pairing instruction
    **Class 1**, minor.
18. **Lot of Exaltation** JN Ch. 30 fn 166 (sect light → its exaltation degree, from the Asc) =
    `exaltation` (Sahl 4.1, 6). **Class 4.** Dykes takes JN's "Lot of the Kingdom" as this Lot, not
    Abū Ma'shar's Mars→Moon.
19. **Lot of Boldness / of the Military** JN Ch. 34: no formula; Dykes offers Saturn→Moon (Abū
    Ma'shar) or Mars→Fortune (Hermetic). The app's `courage` is the Hermetic one. **Class 5** —
    JN cannot decide it.
20. **The eleventh from the Lot of Fortune** BA III.2.0 `[1.7]`, `[2.6]`, `[6-7.3]`; III.2.1
    `[1.7]` "strong like the eleventh from the east"; JN Ch. 7 (a malefic "in the eleventh sign
    from the Ascendant, or with the Lot of Fortune"), Ch. 11 (fortunes/malefics "in the eleventh
    sign from the Lot"). No "eleventh from the Lot" anywhere in `app.py`. **Class 1** — a
    whole-sign count, computable, three witnesses (Valens II.21 behind them).
21. **The first-15° rule for the sect light's triplicity lord** BA III.2.1 `[1.3]`; JN Ch. 7 ("in
    the first 15° of the sign … the other degrees of the angle after the aforesaid 15 … as if in a
    succedent"); Sahl 2.3, 4 (fn 83: should be 15° of ascension from the axial degree). No "first
    15" in the app. **Class 1** — but the three texts disagree on what the 15° is measured from;
    Dykes's Sahl fn 82–83 and the app's existing "three 15° ascensional bands" (2.13, 48–51) are
    the reading to follow if built.
22. **The seven-fold prosperity scheme** BA III.2.0–III.2.6 (§5), with JN Ch. 7's clean rules and
    twelve worked charts (Figures 10–21, pdf pp. 287–298, = *Nativities* charts 1–12, Carmen
    I.24). The app has no prosperity classifier (Sahl 2.1–2.21 uncited beyond 2.2/2.3's stars).
    **Class 1** — the computable core: both sect triplicity lords angular / succedent / cadent;
    the Lot and its lord free and regarding the Ascendant; the eleventh from the Lot; the Moon's
    separation and application; the lords of Asc/MC/11th as fallback. Each rule is stated in
    Sahl too; BA/JN give the frame Sahl scrambled.
23. **JN Ch. 8, the time of fortune** (pdf pp. 300–301): oriental and above the earth → the
    beginning of life, occidental below → the end; the places — 1st and 2nd "the beginning of
    life and adolescence", 10th and 11th youth, 7th and 8th old age, 4th and 5th "a decrepit age
    and the end"; the Lot → the beginning, its lord → the end; **direct the Lot of Fortune to the
    bodies and rays of the fortunes and infortunes** (= BA III.2.4 end). Nothing of it in the app.
    **Class 1**, timing-deferred like the rest.
24. **The Moon on the third day** BA III.9.1 `[1]`, III.9.2 `[1]`; JN Ch. 1 end ("the third day
    and the seventh"), Ch. 27; Sahl 1.29, 11–13, 1.30, 28 (`:1773`–`:1787`). Absent from the app.
    **Class 1** — computable (the Moon 72 h after birth; JN Ch. 27: "commingled to Mars or in his
    domicile or bound … signifies foreign travels").
25. **Gestation** BA III.1.10 `[2]` (258 → 288 days by the Moon's distance from the Descendant);
    Sahl 1.8–1.9. Absent. **Class 1**, computable; canon says Sahl 1.8 is the citation.
26. **The nine-day rule and easternness** BA II.1 = Sahl 1.22 (Dykes fn 171). The app's phase
    logic reads Sahl 1.22 and *Gr. Intr.* VII.2. **Class 4**; BA II.2's 19° for Venus/Mercury
    matches Sahl 1.22, 7 against Carmen.
27. **Void of course** BA II.8: no application by body or aspect, no 30° limit (fn 41). The app's
    `void` (`_pn4_luminary_connections`, "empty in course") tests connections to sign exit.
    **Class 4** in substance (BA's rule is the sign-bounded one); record BA as a witness.
28. **Enclosure** BA II.6: bodies in the same sign either side of the Moon, or rays by
    square/opposition within 7°, broken by the Sun's ray within 4°–5°. The app's besieging follows
    *Gr. Intr.*/Sahl. **Class 4**, a third witness; the 7° interval is BA's own.
29. **The 12° Node orb for any planet** BA II.5. `app.py:7020` applies 12° to either node citing
    Intr. 3, 107 and VII.6, 52. **Class 4**, another witness.
30. **Mercury's sect** BA II.11: "diurnal with diurnal stars and nocturnal with nocturnal" — Dykes
    fn 50 shows it is a corruption of Paul's benefic/malefic rule. The app's Mercury-phase-vs-sect
    row is Firmicus's, display only. **Class 5**; do not import BA's rule.
31. **Spear-bearing** BA II.12: Rhetorius's three types with Dykes's bracketed reconstruction
    (fns 64–68); JN Ch. 6 and Ch. 16 use *dustūriyyah* for kings and for fathers ("the diurnal
    planets from the Sun, the nocturnal from Saturn"). The app displays two definitions and scores
    none (DEC-D-18). **Class 5**; BA is the third text and no cleaner than Sahl 2.5.
32. **Twelfth-parts** BA II.14 (×12, 30° per sign from the sign itself) = `_twelfth_part_sign`.
    **Class 4.** BA III.4.3 (the Sun's twelfth-part in the 12th) and III.10.8 (Mars's, Venus's,
    the Moon's) are the "beyond the Moon's" uses already declared unbuilt — **Class 5**.
33. **The 5° above the Ascendant** BA I.4 (Ptolemy; fn 41 "unclear to what end"). The app's
    five-degree rule is Sahl's/Abū Ma'shar's (`01_on_nativities.md` §2). **Class 4**, a weak
    extra witness.
34. ***Firdāriyyāt*** BA IV.17–25: years, the diurnal/nocturnal starts, sevenths in descending
    order from the lord — all as `pn4_fardar_sequence`/`pn4_fardar_subperiods`; the Nodes-last
    rule is absent from Hugo (fn 228) and present in Da./Abū Ma'shar. **Class 4.**
35. **The lord of the year per planet** BA IV.2–IV.7 (al-Andarzaghar) — a delineation set the app
    does not carry (its year-lord material is PN IV II.4–22 by house). Sahl has none. **Class 5**
    under canon-only; note that PN IV IV.4, 4–11 says Abū Ma'shar kept al-Andarzaghar for one sect
    and rewrote the other, so BA IV.2–7 is the older layer of the same delineation.
36. **The *jārbakhtār* four-way rule** BA IV.8 and the "stronger natal place decides" tiebreak
    between *jārbakhtār* and *sālkhudhāy* (Da. 178). PN IV II.1, 25 ranks the distributor above
    the lord of the year and `pn4_governor` follows it; BA's tiebreak is by natal strength, not
    by rank. **Class 1** as a recorded alternative — do not implement over PN IV.
37. **The weekly/daily/hourly rulers** BA IV.16 (Da. 189; Carmen IV.1.57): 7-day cycles from the
    lord of the Ascendant in descending order. The app's lords of the day and hour are the
    planetary-week system. **Class 1** — a different, computable scheme; canon-only says it stays
    a note (no Sahl witness).
38. **The SR interval** BA IV.1 `[1]`: 6⅕ hours per year (sidereal). The app computes true solar
    returns; PN IV I.4, 31 endorses the tropical year. **Class 4** (no change); the difference is
    about 20 minutes a year of Ascendant drift by age 60.
39. **The *jār kanār*** BA III.1.10: a sixth, last-resort releaser (Sun in a male sign / Moon in
    a female, angular or succedent). Not in Sahl, not in the app. **Class 1** in the corpus;
    canon-only keeps it a note.
40. **The Lot of the *Hīlāj*** (Valens III.7; BA III.1.9 fn 120 suggests BA's "Lot of Fortune or
    the syzygy" as *hīlāj* may be it; Appendix E lists it, uncertain). No formula stated in either
    text. **Class 5.**
41. **JN Ch. 50's weighting caution**: one testimony "routine", two stronger, three complete;
    cadent/movable weak, succedent/common stronger, angles/fixed strongest; equal contraries
    "both should be thrown out". The app has no general weighting rule of this kind (its "three
    testimonies" is Sahl 1.18, 10's). **Class 1**, a two-line rule; JN Ch. 38 is its method.
42. **Profection triggers by topic** — JN Ch. 21 (the year to natal Jupiter/Venus → children;
    Jupiter/Venus transiting the Lot of Children or its square/opposition), Ch. 26 (**the profection
    to the 7th, or the SR Ascendant being the 7th sign → betrothal; movable sign many wives, common
    two, fixed one**), Ch. 33 (the profection to the MC with a mastery planet there → renewed
    mastery); BA III.7.10, III.5.5 `[4.2]`, III.12.6. Sahl carries the marriage and children cases
    (`01_on_nativities.md` §5g); the app's profection is PN IV's general one. **Class 1** for the
    SR-Ascendant-in-the-7th trigger, which Sahl lacks; **Class 5** for the rest.
43. **JN Ch. 1's first-year timing**: the profection reaching "an angle in which there were some
    one of the malefics"; then "direct the degree of the Ascendant to the conjunction, square or
    opposition of the malicious stars, by giving a month to each degree", years if beyond one
    year (fn 11: *Nativities* says direct outright). Sahl 1.30–1.32 have the directions without
    the month-per-degree first year. **Class 1**, minor.
44. **The parents' *hīlāj*** JN Ch. 19: father by day Sun → Saturn → Lot of the Father → the
    degree of the 4th (night: Saturn first); mother by day Venus → Moon → Lot of the Mother →
    the MC's degree (night: Moon first); the aspecting lord of the five dignities is the
    *kadukhudhāh*; failing all, direct the Moon's degree. Chs. 17–18 ("Ptolemy said"): direct the
    Sun if it aspects the Ascendant, else Saturn, else the IC's degree, a year per degree of
    ascension, and compare with the years of the most dignified planet in the Sun's place. The app
    directs the Lot of the father, the Sun or Saturn (Sahl 4.20, 31–32). **Class 1** for the
    fallback chains and the years comparison (Sahl 4.12 is JN's abbreviation).
45. **JN Ch. 10's triplicity lords of the Ascendant** as thirds of life, "make the Lord of the
    Ascendant testify to the first Lord of the triplicity, and the Lord of the Midheaven to the
    second one, and the Lord of the seventh place to the third one" (fn 72 against Holden). The
    app uses the Ascendant's triplicity lords only for upbringing (Sahl 1.29). **Class 1**, minor.
46. **The eye-harming degrees** BA III.6.2 `[1.5]` — `COURSE_COVERAGE` gap #1 (Sahl 6.2, 48–75).
    **Class 5**, now with Hugo's variant numbers on record (§6a) so that a build from Sahl is not
    "corrected" from BA.

**Count: Class 1, 17 items (#2, 6b, 17b, 20–25, 36, 37, 39, 41–45); Class 2, 1 item (#1);
Class 3, none — 18 in Classes 1–3.** Class 4, 22 (#3, 5–15, 17, 18, 26–29, 32–34, 38); Class 5, 11
(#4, 14b, 16, 19, 30, 31, 32b, 35, 40, 42b, 46).

---

## 9. What these books add to the corpus that nothing else had

1. **The seven-fold prosperity frame in its original order**, with the item lists Sahl
   scrambled (BA III.2.0), and **twelve worked prosperity charts** (JN Ch. 7).
2. **A complete, mechanical years ladder for the *kadukhudhāh*** (JN Ch. 3) and a clean
   statement of the additions and subtractions (JN Ch. 4) — the only version without Sahl 1.21's
   emendations.
3. **The rate of distribution restated** (BA III.1.10) with the corpus's only worked
   *jārbakhtār* example (Carmen III.2 via Māshā'allāh, Figure 8).
4. **The share-counting rule for the *kadukhudhāh*** (BA III.1.6) — the basis of Sahl 1.20, 2–5.
5. **The cycle of the year before Abū Ma'shar**: no separate chart, three Ascendants, ten heads
   (BA IV.1; Intro §7) — the historical reason PN IV's II.1 list is what it is.
6. **The *jār kanār***, the **weekly rulers** (IV.16), the ***sālkhudhāy* delineations per
   planet** (IV.2–7), the **Lot of Money's formula**, the **Lot of Death cast from Saturn** stated
   flatly, the **third-day Moon**, the **eleventh from the Lot**.
7. **Vocabulary settled** (Intro §9): *jārbakhtār*, *jārzamān*, *jār kanār*, *intihā'*,
   *nawbah* (= the *mubtazz*'s turn, not the sect light), *ateci* (the joys / figure-description),
   *hayyiz*/*halb*/*hazz*.
8. **The statement that no weighted *mubtazz* exists in Māshā'allāh or Abū 'Alī** (Intro §8).

## 10. What they do not add

- **No new longevity selection rule beyond Sahl's**: the same five candidates; the order differs
  and JN's conjunctional/preventional switch is Hermes's from BA III.1.9.
- **No years-granting table other than the one Sahl has**, except the luminary middle years
  (#1).
- **No revolution chart, no cusps, no lord of the orb, no ninth-parts, no monthly revolutions**
  — PN IV's apparatus is absent; BA IV is transits plus profection plus direction plus
  *firdāriyyāt*.
- **No stated Nodes-last rule** for the *firdāriyyāt* (Hugo omits it).
- **No formula for the Lots of Faith, Boldness, Enemies, Parents** — named, not calculated.
- **Nothing on the proportional semi-arc**; BA II.17's directions are ascensional-time
  approximations Dykes tells the reader to ignore.
- **Nothing to change in the twelfth-parts, the void Moon, enclosure, the Node orb** — witnesses,
  all agreeing.

---

## 11. Reading notes, including OCR defects

- **Where the OCR is worst**: pdf pp. 88–89 (BA II.17's arithmetic; every number should be checked
  against Appendix A's restatement, pdf pp. 377–383, which is clean); pdf pp. 104–105 (III.1.7
  `[6.4]`, the Valens fraction paragraph); pdf p. 135 (III.2.6's lacunose timing paragraph —
  the bracketed lacunae are Hugo's, not the OCR's); pdf pp. 390–392 (Appendices D–E, the star
  table and Lot table are column-scrambled: read Appendix D's positions from the body at III.2.1
  and Appendix E from the chapters, not from the tables). Every figure is noise. JN Ch. 7's
  chart figures (pdf pp. 287–298) survive only as their captions and the prose positions.
- **Two pages relocated to the file's end** (printed 24 and 233, at pdf pp. 407–408) — see
  conventions. A reader who stops at "BIBLIOGRAPHY" misses BA II.7–II.8's opening and JN Ch. 3's
  opening, which carries the *kadukhudhāh* selection rule and the Sun-in-Aries/Leo sentence.
- **Dykes's brackets are load-bearing.** Book III.8.1's items `[{2}]`–`[{8}]`, II.12's Type 3,
  IV.16's whole method, IV.21's Saturn–Mercury sub-period and much of III.5–III.7 are Dykes's
  supplements from Rhetorius, Da., Sahl, Dorotheus and Abū Ma'shar, marked as such in
  footnotes. Cite the footnote, not "BA", for any of them.
- **Hugo's numbers are ordinal where BP read cardinal** (II.16 fn 86; III.6.2 fn 35; Figure 8
  fn 147): "the seventeenth degree" = 16°–17°. The same trap as Sahl's Figure 57.
- **"Cadent" in Dykes's JN is Latin *cadens*; in BA it is "third from a pivot"; "turned awry" is
  aversion.** Do not equate them when reading a rule across the two books.
- **Sect vocabulary**: "at rest" = of the sect; "not at rest or placed" = contrary to the sect
  and/or badly placed (Intro §6 lists all sixteen uses). Sahl's "in the sect" (1.21, 5 fn 162
  "share") is the same word-family.
- **JN Ch. 7's twelve charts are *Nativities* charts 1–12 and Carmen I.24's** (fns 46–61); the
  positions and delineations disagree in charts 5, 6, 7, 9, 11, 12 (Dykes's notes). Not test
  fixtures.
- **Dykes disagrees with the text openly**: BA I.4's 5° rule ("unclear to what end"), II.11's
  Mercury sect, II.17 entirely, III.1.7's *kadukhudhāh* direction, III.7.8's first paragraph
  ("totally departs from Sahl"), IV.8's "safe place" error, IV.16 as Hugo left it. As with PN
  IV, an editorial verdict is not doctrine — but Appendix B (5) is the one that touches a live
  page of the app (#8).
