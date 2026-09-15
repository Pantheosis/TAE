# Phase 1 — Abū Ma'shar, *On the Revolutions of the Years of Nativities*, from the Latin (*Persian Nativities* III)

Source: `consolidated_texts_final/pn3/pn3_pdf_text.md` (md5 `13efb7a48408e2a853586fe81dc70ccc`),
8,164 lines, 532,271 bytes, filed 2026-09-15 from the owner's PDF (the Kindle edition's own text
layer, rendered from HTML; no OCR). Read whole, in order, 2026-09-15. 174 page markers
`*[PN III pdf p. N]*`, pdf pp. 2–184. **The text layer carries no printed folio** — the README says
the running heads do, but no running head survives in the layer — so every citation below is by
**chapter and pdf page**. `CORPUS_MANIFEST.md`'s rule holds: never compare a bare page or figure
number across volumes. PN III Figure 3 (Abū Ma'shar's nativity) and PN IV Figure 65 are the same
chart; PN III Figure 1 (the *firdārīyyāt* arc) and PN IV Figure 43 are not the same table.

**Companion.** PN IV is read in `01_persian_nativities_iv.md`; its PN IV sentence citations are
reused here unchanged. PN IV quotations below are from
`consolidated_texts_final/pn4/pn4_complete/persian_nativities_iv.md` (13,932 lines, md5
`8fd5f30d439bf56fe36e37f73f5cfcee`) — **not** the blob the earlier synthesis pinned; the sentences
quoted were checked in this copy.

**Coverage.** Everything: Dykes' Introduction §§1–16, Books I–V, the IX.7 summary, Appendices
A–E, the bibliography, and all 713 footnotes. Nothing was skimmed by title alone. The book is a
third the length of PN IV because two thirds of Abū Ma'shar never reached Latin (§0).

---

## Heading and citation conventions (the heading trap, PN III edition)

- **No sentence numbers.** The Latin edition predates Dykes' numbering convention. Cite as
  `PN III II.22 (pdf p. 83)`; within a long chapter add the paragraph's opening words.
- Chapter headings are plain text, indented one space, `Chapter N.M: …`, and **wrap onto two
  lines** for twenty-five of them (`grep -c '^ *Chapter'` under-counts). Book headings are
  `BOOK II: [PROFECTIONS]` — printed twice each, on a divider page and again at the top of the
  text (pdf pp. 49–50, 90–91, 115–16, 129–30, 142–43).
- **Four chapters are Dykes', not the manuscript's**, and are bracketed: `[Chapter II.24]`,
  `[Chapter IV.8]`, `[Chapter V.9]`, `[Chapter V.10]`. Bracketed sub-headings inside chapters
  (`[General template for examining the Lord of the Year]`, pdf p. 55; `[Six places or planets in
  the distribution]`, p. 97; `[Superior squares over the Lord of the Year]`, p. 83) are his too.
- **Footnotes are numbered continuously 1–713 for the whole volume** (Introduction 1–276, text
  277–698, appendices 699–713) and sit together at pdf pp. 166–184. "fn 371" is unambiguous — the
  opposite of PN IV, where "fn 222" needs a Book.
- Figures 1–5 are captions only; the images did not survive into the text layer. **Appendix B
  (the Egyptian bounds table, pdf p. 147) is a heading with no body** for the same reason.
- Book abbreviations (pdf p. 7): *BA* = Māshā'allāh, *Book of Aristotle*; *TBN* = 'Umar; *JN* =
  al-Khayyāt; *Gr. Intr.*; *On Rev. Nat.* = this book. Dykes cites *TBN* and *BA* constantly; both
  are in the corpus as PN II and PN I.

Chapters present, by Book: I 9 · II 23 (+ II.24) · III 10 · IV 7 (+ IV.8) · V 8 (+ V.9, V.10) ·
IX 1 (IX.7 only, and that a summary). **57 chapters of Abū Ma'shar's 96.**

---

## 0. What this book is: the same work as PN IV, from the other side of the transmission

PN III (2010) and PN IV (2019) are two translations of one book. PN III is **Latin → English**;
the Latin is the c. 1262 version of a **partial Greek** translation made in the late tenth century
from the Arabic, and Dykes reads it against Pingree's 1968 edition of the Greek and Robert
Schmidt's unpublished/1999 English of the Greek. PN IV is **Arabic → English** from four
manuscripts. Dykes says so at the start:

> "these complete and epitomized Arabic versions have never been translated: instead, in the late
> 10th Century it was partially translated into Greek, and that work was the basis of a Latin
> version in about 1262 AD. Persian Nativities III is based on this Latin version, with references
> to Pingree's Greek." — Introduction §1 (pdf p. 9)

What the Latin lacks is stated as a table of contents at §1 (pdf p. 10): **all of Books VI, VII,
VIII, and IX.1–6 and IX.8–9.** The only Book IX chapter present, IX.7, "is my own summary of the
nine types of indicators from the surviving Greek text of Book IX, based on Robert Schmidt's
translation. The indicator titles are my own" (pdf p. 143). **So PN III has no cutters (IX.8), no
monthly revolutions (IX.1–5), no lord of the orb chapter (VI.1), no "turning" chapter (VI.2), no
wells (VIII.15).** Every one of the app's citations to those Books has no Latin witness.

Two consequences for the corpus:

1. **Where the two overlap (Books I–V), the Latin is an independent witness** two removes from
   the Arabic. Where it agrees with PN IV against the printed PN IV, it settles a reading (§9,
   items 9, 15, 16). Where it disagrees, the Arabic is the better text and Dykes' 2019 footnotes
   say so; the Latin's variants are recorded, not adopted.
2. **Dykes' 2010 Introduction is not superseded by the 2019 one.** It is shorter (29 pages
   against 144) but organised differently — by *principle* (§3: priority of the nativity,
   reinforcement by repetition, activation by key places) rather than by technique — and it has
   three things the 2019 Introduction does not: the transit checklist with its Hellenistic
   sources marked (§12), the treatment of overcoming/decimation in Book II (§15), and the
   *firdārīyyāt* number-theory (§11, Figure 1).

The chapter numbering **differs by one in Book I** (the Latin lacks Abū Ma'shar's preface, PN IV
I.1) and **coincides thereafter** until Dykes' editorial chapters; the full map is §8.

---

## 1. Dykes' Introduction (pdf pp. 9–37) — sixteen sections

| § | Topic | pdf pp. | Note |
|---|---|---|---|
| 1 | Abū Ma'shar; the transmission; what is missing | 9–10 | the missing-chapters table |
| 2 | The Persian annual system: nine stages; cross-reference table to *BA*, *TBN*, Abū Bakr, al-Qabīsī | 10–13 | five "technical points" |
| 3 | Three delineation principles | 13–16 | the reconstructed argument against 'Umar |
| 4 | Benefic–malefic combinations | 17–18 | III.2's seven types generalised |
| 5 | Four points on timing | 18 | quadrants of the year (III.8) |
| 6 | Profections; **alternative Lords of the Year** | 18–23 | the luminary-proxy table, fn 117–130 |
| 7 | The Ascendant of the year and its Lord | 23–24 | |
| 8 | Distributors and partners; **his own worked example** | 24–27 | fn 155: "Abū Ma'shar's own example in III.1 uses Lots in an unusual way, so I will construct my own" |
| 9 | The Moon | 27–28 | twelve passages, half of them from V.10 |
| 10 | Lots | 28 | |
| 11 | *Firdārīyyāt*; Figure 1 | 28–31 | the Nodes' placement |
| 12 | **Transits**: a checklist with sources | 31–34 | Figure 2, the "transit template" |
| 13 | Ninth-parts | 34 | three doubts |
| 14 | Monthly, weekly, daily rulers; Hephaistio II.28 | 34–35 | 2½-day profections |
| 15 | **Superior squares, overcoming, decimation** | 35–36 | Book II read for the rule |
| 16 | Vocabulary: "necessities", "steering", signs that "hate" | 36–37 | |

Points to carry forward:

- **§2 (pdf p. 12), five technical points.** (1) Abū Ma'shar erects a separate revolution chart
  with quadrant cusps, where *BA* did not; "in I.5 Abū Ma'shar practically suggests that natal
  positions should be marked around the edges of the revolutionary chart" — PN IV I.6, **4** and
  Figure 51. (2) He profects the Lot of Fortune and other points, "and, like 'Umar al-Tabarī but
  unlike Māshā'allāh, Abū Ma'shar explicitly profects in 30º increments" (fn 11: IX.7). (3) III.7
  mentions ascensional times with planetary years — PN IV III.7, **34–35, 42**. (4) A dead
  native's chart keeps speaking of his living children and father (I.9) — PN IV I.9, **33**.
  (5) Public vs private expression: angular = public, cadent = private, aversion = clandestine.
- **§3 (pdf pp. 13–16).** The threefold body/soul/action grouping of II.2, of which Dykes is
  "skeptical … because the delineations given later … often deal indiscriminately with effects
  on the body, soul, actions". Then the three principles, each with numbered examples footnoted
  to the chapters. Principle 1's "the signification of the nativity does not become inactive on
  account of a revolution" is I.3 (pdf p. 40) — PN IV I.4.
- **§6 (pdf pp. 22–23), alternative Lords of the Year.** Dykes' table for the Sun and Moon
  (fn 117–128) mixes Abū Ma'shar's alternatives with *BA* IV.7's. His verdict on the substitute
  natal-planet rule of II.24/III.8: "I have my doubts about the value of this rule: surely it
  would mean that we would have substitute Lords … about half the time." On the Moon's division
  of the year: "**This does not make sense to me.**" — the Latin reads differently from the
  Arabic here (§9, item 1).
- **§8 (pdf p. 25), the partner across bounds** — stated here more plainly than anywhere in PN IV:
  "the distributor's term of governing is restricted to the period of the bound itself, while
  partners work across bounds; and the Persians stated that a partner may become active upon a
  releaser entering the bound and not only when it reaches the partner by degree."
- **§11 (pdf p. 30), the Nodes.** "Abū Ma'shar's text is absolutely clear on where the Nodes
  fall: at the end of the sequence of the seven planets, no matter the sect of the chart."
  The next sentence has a slip — "in a diurnal chart they will come after the Mars period, and in
  a diurnal chart after the Mercury period" — the second "diurnal" should be "nocturnal"; the
  text at IV.8 (pdf p. 125) has it right.
- **§12 (pdf pp. 32–33).** Three lists — whose transits, which places, what intensifies — with
  each item marked as shared with the Hellenistic sources, Hellenistic only, or Abū Ma'shar's
  addition. Then the "transit template" of V.1 (Figure 2): take each planet's domiciles as
  Ascendants and read the other's domiciles as derived houses; "it should be viewed with caution
  if not skepticism" (pdf p. 34). This is the "derived domiciles" method PN IV's Intro §11 calls
  bogus and underlines throughout Book V.
- **§13, §14.** "if the rules are correct as presented, then there can only ever be four Lords
  of the Year: Mars, the Moon, Venus, and Saturn" — the III.10 consequence. §14 adds
  Hephaistio's 2½-days-per-sign sub-profection, which Abū Ma'shar's IX.7 method 8 also has.
- **§15 (pdf pp. 35–36).** Overcoming = tenth sign; the Greek edition says "decimate", the Latin
  "elevated" (fn 274). Four principles extracted from Book II: the overcoming planet "will
  determine the source or cause of the good or bad". Worked on Saturn–Moon, Jupiter–Mars,
  Venus–Moon from II.5, II.8, II.17.

---

## 2. Book I (pdf pp. 39–47) — nine chapters, one short

- **I.1** (pdf p. 39) — the definition: "being restored in that same place [after] 365 days and
  a portion, it becomes one year for the native"; a place per year from the natal horoscope. =
  PN IV **I.2**. The Latin has **no preface**; PN IV I.1's "nine Books and ninety-six chapters"
  is absent.
- **I.2** (pp. 39–40) — why the Sun and not the Moon: the four seasons; 30° a solar month,
  2′30″ an hour, 1° a day. = PN IV **I.3**, whose symbolic units the exemplar warns not to
  conflate with real-time charts; the Latin closes with the same caveat, "certain ones of the
  hours and days and months are changed … on account of the diversity of the Sun's motions".
- **I.3** (pp. 40–41) — the objections and replies; the *zīj* passage; "the accurate horoscope
  of the year is the one taken from the annual motion of the Sun observed by a philosopher,
  through instruments about which [Ptolemy] makes mention in the Almagest … 365 ¼ days (less
  one-hundredth of a day)". = PN IV **I.4**, whose **29** names three *zījes*; the Latin names
  none (fn 285 supplies "Ptolemy" from the Greek).
- **I.4** (pp. 41–42) — the ancients' use of revolutions. = PN IV **I.5**.
- **I.5** (p. 42) — **the chart-construction chapter** = PN IV **I.6**, sentence for sentence:
  "14 planets and two ascending [Nodes] … and a sending of rays both of the nativity and of the
  revolution in 98 places, and the particular twelfth-parts … in 38 places" (fn 294 reads xcviii
  for the Latin's xcvi). Its fixed-star clause is shorter than the Arabic's — §9, item 13.
- **I.6** (p. 43) — the reading checklist = PN IV **I.7**. Adds one gloss PN IV lacks: *hayyiz*
  is transliterated (fn 299 defines it from *Gr. Intr.* VII.6 and al-Qabīsī's *halb*).
- **I.7 + I.8** (pp. 43–46) — the Ages of Man, split across two Latin chapters = PN IV **I.8**.
  Moon 4 ("her middle years are 39 ½, one-tenth of them is taken"), Mercury 10 ("one-half the
  years of his lesser period"), Venus 8, Sun 19, Mars 15, Jupiter 12, Saturn "until the last day
  of life"; then "certain people said that Saturn would steer the seventh age through 30 years"
  (p. 45) = PN IV I.8, **31**. I.8 also carries the *firdārīyyāt*-by-exaltations claim (fn 314:
  "This is not true … But Pingree (1968 pp. 60ff) claims it was so") = PN IV I.8, **35**.
- **I.9** (pp. 46–47) — the four things to know = PN IV **I.9**; the four ranks of men; the
  eunuch; "the outcome of children may be known from the revolution of a dead man" = I.9, **33**.

---

## 3. Book II (pdf pp. 50–88) — twenty-three chapters and Dykes' twenty-fourth

**II.1** (pp. 50–51) — the nineteen significators, same order as PN IV II.1, **6–24**. Three
wording differences carry weight and are §9, items 4–6: the seventh lacks the void-Moon fallback;
the eleventh is "the period or orb of the stars and of the twelve houses" (Dykes with Schmidt for
the Latin's *annorum*, fn 331) where the Arabic has "the turning"; and the ranking sentence is
"the first is stronger than the second, and the second [stronger than] the third", not "each one
in turn". Then the complaint against those who "make a [primary] direction of all of these, and
they resolve [them] into days, months, and hours" — fn 338: "Possibly a critical reference to
'Umar al-Tabari in TBN II" — = PN IV II.1, **29–33**.

**II.2** (pp. 51–52) — five for the body, eight for the soul, **identical lists** to PN IV II.2,
**4–18** ("the bound in which the direction of the apheta (which the Persians call the hīlāj) has
arrived"; "Sixth, the Lord of the period" = the lord of the orb).

**II.3** (pp. 53–55) — "compute one sign for every year, and where it applied, that one will be
the sign of the profection, whose Lord will be the Lord of the Year (which in Persian is called
the slkƒudy)" — the transliteration is garbled in the text layer; = PN IV II.3, **1**
*sālkhudhāh*. The natal and revolutionary analyses (**2–4**), the four-way comparison (**5–8**),
and then Dykes' bracketed *[General template]* = **9–19** — but with **"configured to
benevolents" where the Arabic has "received"** (§9, item 3). The four aversion places "(namely in
the 2nd, 6th, 8th or 12th)" = **17**.

**II.4–II.21** (pp. 55–83) — the delineations, on the PN IV template (suitable / bad / places),
read through. Three apparatus passages inside them:

- **II.5**, pdf p. 60, *[General comments on delineating the Lord of the Year]* — **fn 371:
  "I have rewritten parts of this paragraph because I believe both the Greek and Latin texts have
  mixed up some of the conditions."** Dykes' 2010 rewrite is what the Arabic says at PN IV II.5,
  **59–62** (§9, item 24). The same page's aspect ranking — "the square aspect has greater power
  for harming than the trine does" — is **not** what the Arabic says (item 25). The
  root-vs-revolution rule "if the signification of the nativity is stronger, it will surmount
  one-half of the judgment" = PN IV II.5, **70–73**. The eight "ways" = **76–83**.
- **II.13** (pp. 74–75) and **II.14** (p. 76) — the Sun as lord of the year: "we do not take him
  principally … but we look at the sign in which the direction of the hīlājes has arrived
  (whether the Sun is the hīlāj or another), taking as the [primary] significator (with [the Sun])
  a planet of the nativity or a planet of the revolution, and the ones which are configured with
  the Sun" — garbled against the Arabic (§9, item 2). II.13's close, "if the planets were in the
  heart of the Sun and of a good condition, good things will be signified" (fn 420: "against
  *Gr. Intr.* VII.630-35").
- **II.22** (p. 83) — the Moon as lady of the year: "we take the partner and [also] a planet
  which was in Cancer … even a planet to which the Moon is being conjoined in the sign where she
  is. By means of the two planets, we divide the year into two. But if there were three, [we
  divide the year] into three" — **the division reads as among the proxies, not by the Moon's
  connections** (§9, item 1). "the sign in which the Moon was at the time of the revolution, for
  it has an equal role to the horoscope of the year" (fn 449, *partem* for *planetam*) = PN IV
  II.22, **14** "close to the power". Then *[Superior squares over the Lord of the Year]* —
  fn 275 flags it as "contrary to his presentation of the delineations in the other chapters".

**II.23** (pp. 84–85) = PN IV II.23, **1–22**. "After the Lord of the Year, the distributor has
its own signification" = **1**. The angles/succedents/cadents topics = **4**.

**[II.24]** (pp. 85–88) = PN IV II.23, **23–71**, the named configurations (PN IV Figures 56–64).
Dykes' fn 459: "may well be based on actual charts". Fn 464 on the Sagittarius/Leo chart: "so
precise they sound as though they are from a real chart, but I have not been able to find a
corresponding date." The substitute-lord rule at p. 86 — "take that malevolent as the Lord of the
Year, especially if the Lord of the sign of the profection or the Lord of the Ascendant of the
revolution did not aspect its own Lord" with **fn 468 "I believe this should probably read
'sign'"** — is confirmed by PN IV II.23, **41** "falling away from an aspect to its own house"
(§9, item 26). It closes with "Let this be a rule for you in the revolutions of years" (p. 88) =
**65–71**.

---

## 4. Book III (pdf pp. 91–113) — directions

**III.1** (pp. 91–93) is the specification and matches PN IV III.1 point for point:

- five *hīlājes*; "the first hīlāj indicates the years of life, illness, even the quality of
  death; but the remaining hīlājes signify soundness or illness or dangers" = **3–4**.
- **the unit key**: "take the degrees in the Ascendant of the nativity for years, but in the
  figure of the revolution for months or days, and indeed in the figure of the months for days or
  hours" = **6** (item 7).
- distributor "whether it aspects [the bound] or not" = **11**.
- **the three-case rule**: "the direction of the Ascendant and of those which are in it comes to
  be through the ascensions of the city in which someone was born; but a direction of the
  Midheaven [and] even of the fourth and of those which are in them, comes to be through the
  ascensions of the right sphere. But for the other places the direction comes to be just as we
  have shown before in our treatises" = **12** (item 8).
- **the rate ladder**: "each degree into one year, but 5' into a month, and 1' into six days, and
  10" into a day, and twenty-five sixtieths [of a second] into an hour" (fn 485: "Reading with
  Schmidt for *tertia*") = **13** (item 9).
- the *jārbakhtār* named for the Ascendant's distributor = **14** (fn 486: 'Umar uses it
  widely, Māshā'allāh restricts it).
- the partner rule = **15–16**.
- the worked example, **Figure 3, "Abū Ma'shar's nativity"** (fn 488: "approximately 10:00 p.m.
  on August 10, 787 AD, near Balkh"). Its data differ from PN IV's in five places (item 10) and
  Dykes already in 2010 corrects the Lots and the "sextile" of Saturn ("This should be a square",
  fn 492, 494, 495). **Unusable in both volumes.**

**III.2** (pp. 93–99) = PN IV III.2 in the same order: the scope statement ("the Lord of the Year
signifies accidents for a [single] time, but the distributor [signifies] the passions which are
signified in diverse times" = **2**); the checklist; **the seven kinds** (1 benefic alone …
7 both benefic); *[Six places]* and **the twenty-four ways** (fn 513: "I have changed some of the
wording slightly to match the Greek, as there are ordering mix-ups in a few items in the Latin");
*[Four pairs and eight double pairs]* = **87–101**. Then p. 99, word for word with PN IV:

> "of these three, the distributor has the stronger power, the one which partners with it by
> body [has] the second-[strongest power], but partnership by rays is the last. Also, of the
> aspects, the opposite is stronger, after that the square, then the trine, but the sextile is
> most weak. But it is not necessary to take these things which we have stated about the one
> partnering according to the revolution, but [only] according to the nativity." (= **103–106**)

and **the longevity gate**:

> "whatever we have said before … that signifies death … they then come to be when those years
> will agree with the number of the years of life (or near it) which the hīlāj of the nativity
> signified. … But if the revolution of the year signified death and destruction, but the full
> amount of years did not happen then … death will not touch [him], but [rather] a great and
> dangerous impediment." (= **110–111**)

**III.3–III.7** (pp. 99–105) — per-planet distributors. III.3 opens with the releaser list —
"the Sun or Moon or the Ascendant or the Lot of Fortune or the degree of the conjunction or the
degree of the prevention" = PN IV III.3, **1**. **III.7's tail** (pp. 104–105), *[Further
instructions]*, has the quadruplicity and "once" rules = PN IV III.7, **27–42**: "if the
distributor were in a firm sign in the nativity, and it did not aspect the place of the
distribution, the operation of the planet comes to be once, namely when the distribution agrees
with the ascension of the sign in which it is according to the nativity, or [according to] the
number of the greater or middle or least years" = **35**.

**III.8** (pp. 105–108) = PN IV III.8. Fixed stars, comets, eclipses (p. 106) = **9–14**, with a
shorter list of places (item 12); the substitute-lord rule again (p. 106) = **15–16**; **the
quarters of the year** (p. 108) = **48–50**, cleaner in the Latin (item 14):

> "From the Ascendant up to the Midheaven is the eastern quarter, and it signifies one-fourth of
> the year; from the Midheaven up to the seventh place is the southern quarter … from the west up
> to the angle of the earth is the western quarter … from the angle of the earth to the Ascendant
> is the northern [quarter] … If there were malevolents in the Ascendant or in the eleventh or in
> the Midheaven of the revolution, but benevolents under the earth, they signify severity at the
> beginning of the year, but good things in the last [part], especially if the sign of the year
> were movable."

**III.9–III.10** (pp. 109–113) — ninth-parts. "it [has a size] of 200', namely 3 1/3 degrees
exactly" (p. 109) — item 15. Figure 4 and Figure 5 (captions only). The subdivision into thirds
by the lords of the sign, the fifth and the ninth; **the wrap-around rule** stated as plainly as
in PN IV, and doubted as early: fn 574, "the instructions here make it seem as though the
direction begins in the relevant sub-ninth, but then cycles through the other two sub-ninths no
matter where it begins". The example's latitude is 36° (fn 573: Schmidt for the Latin's 26).
III.10: "the Indians take the Lord of the Year to be the Lord of the first ninth-part, whether the
revolution applied to the beginning of the sign or in the end"; the 20° Taurus / Saturn example;
the casting-out by 108 — all = PN IV III.10, **1–6**.

---

## 5. Book IV (pdf pp. 116–126) — the *firdārīyyāt*

**IV.1** (p. 116) carries the whole apparatus in one paragraph = PN IV IV.1, **1–10**: the nine
periods summing to 75; diurnal "the Sun … then Venus, then Mercury, then the Moon, then Saturn,
then the others according to the order of their circles"; nocturnal "the Moon … then Saturn, then
Jupiter, then Mars"; sevenths from the lord itself; "the Head and Tail alone dispose according to
their own disposition (not uniting to any planets), namely after the full amount of years, for
the reason that they do not have domiciles". Fn 588: "Abū Ma'shar clearly puts the Nodes at the
very end, and not in between the firdārīyyāt of two other planets."

**IV.2–IV.7** (pp. 118–125) — delineations by sub-period with running totals; the Latin gives
every sub-period's length ("1 year, 5 months, 4 days, 6 hours") as the Arabic does. Two Latin
misprints Dykes corrects from the Greek: Mercury's seventh (fn 606, *decem* for *sex*) and the
Moon's (fn 616, *tres* for *decem*).

**[IV.8]** (p. 125) is assembled by Dykes: the Node paragraphs he **moved here from the end of
the transit material** (fn 629), replacing the Latin's own Node text, which he prints as
**Appendix A** (p. 146). Both the moved text and PN IV IV.7, **20–23** have the Head in the
Ascendant / second / third and the Tail's contraries. Then, from the Latin edition proper: "in
diurnal nativities the aforesaid Nodes dispose after Mars, but in a nocturnal one after Mercury.
But once the 75 years are completed, the distribution of the firdārīyyāt is restored to the planet
from which the firdārīyyah at the beginning of the nativity began … his death will be in the
firdārīyyah of that planet which it touches" = PN IV IV.7, **24–26** (items 16–17).

---

## 6. Book V (pdf pp. 130–139) — ingresses (transits)

**V.1** (pp. 130–131) = PN IV V.1. The completeness grade — "oftentimes a planet in a revolution
of the year reaches its degree according to the nativity and oftentimes to the sign but not to
the degree. But if … it reached the degree … or to the bound in which it was, then its
signification will be perfected" — **three rungs only** (degree, bound, sign); the Arabic's
half-body rungs at **4–6** are absent (item 19). The threefold interpretation and the derived-
domiciles example (Venus to Jupiter's place: Taurus sixth from Sagittarius, illness; Libra
eleventh, friends; Taurus third from Pisces, travel; Libra eighth, inheritance) = **11–20**. The
**duration** rule uses "orb" for what the Arabic calls the period: "if a malevolent reached its
own proper place, double its orb … if the sign were in a movable sign, you would take the lesser
orb of this [planet]; if in a double-bodied one, the middle; if in a fixed one, the greater"
(fn 639: "Converting its lesser, middle or greater years into units such as days"; fn 645:
Venus 8 + Jupiter 12 "considered as days, makes 20 days") = **27–35** (item 20).

**V.2–V.8** (pp. 132–137) — per-planet ingresses, same order as PN IV. V.8's tail on the Moon —
"if the Moon were impeded, and she reached [the square of] her own place according to the
nativity, or to its opposite, he will have danger on that day" = PN IV V.8, **21**.

**[V.9]** (p. 138) = PN IV V.8, **26–35**: transits to the degree of the distribution, the two
Ascendants, rays, Lots, twelfth-parts; the twelfth-part example (fourth house's twelfth-part in
the second sign); "if the planets are configured according to the nativity, it signifies the
outcome is from a preceding cause; but if … according to the revolution [alone] … from a
supervening cause … not configured to any … from an unexpected cause" = **32–35**.

**[V.10]** (pp. 138–139) — **fn 680: "This chapter is not reflected in Pingree."** It has no
counterpart in PN IV either (item 21): the Moon and her lord for bearing, health and prosperity;
"you should look at the twelfth-part of the Moon, and it will be worse if it is being aspected by
malevolents"; "if the Moon is not being aspected by any [planet], nor does she aspect the
Ascendant, he will strive to acquire something in that year but he will not acquire it" (fn 189:
"a maxim from horary transferred to revolutions"); "the Sun burning up the planets is worse than
a malevolent"; Mercury and the timing of good and bad rumours; the Moon reaching the natal
Ascendant "elevates thoughts" (fn 686: or "cares"), the Midheaven, the fourth, and — added from
the parallel Dorotheus in Schmidt 1995 — the seventh.

---

## 7. IX.7 and the appendices (pdf pp. 143–165)

**IX.7** (pp. 143–145) is Dykes' summary of the Greek's nine methods, with his own titles. It
maps to PN IV IX.7 method by method; the two directions-as-timing methods differ in their unit
(items 22–23):

- **6. "The 'greater condition' or 'greatest days'"**: "Convert the following 30º into
  ascensions, and treat them as equaling 1 year: thus every degree will on average equal 12 1/6
  days of the revolution" — PN IV IX.7, **25** multiplies zodiacal degrees by 12d 4h 10m 30s
  and never mentions ascensions. Fn 691: Schmidt took it for a distributor-partner direction;
  Dykes takes it for 'Umar's "greater condition" of *TBN* II "converted into ascensions".
- **7. "The 'lesser condition' or 'small days'"**: "Direct the degree of the Ascendant of the
  revolution around the entire circle for the year of the revolution, at a rate of 59' 08" per
  degree" — a slip for *per day*; PN IV IX.7, **29** "a day for every 59′ 08″".
- **8** has the four chief indicators "left unnamed" (fn 694), 30° a month, 2½ days, 5 hours =
  PN IV IX.7, **34–38**. **9** has the same puzzle as PN IV's worked example — the year "begins
  with the Lord of the first ninth-part in every case" (fn 698 on 20° Taurus and Saturn) — and
  the same 1 1/9-day sub-periods.

**Appendix A** (p. 146) — the displaced Latin Node text (§5). **Appendix B** (p. 147) — heading
only. **Appendix C** (pp. 148–150) — aphorisms on revolutions from pseudo-Ptolemy (24, 77, 87, 88
with al-Ridwān's commentary and Dykes' own reading of *Tet.* II.6's eclipse timing), Hermes 87,
al-Mansūr 63, 64, 65, 81. Two of these are apparatus: **ps-Ptolemy 77 / al-Mansūr 63**, the
per-releaser topics (Ascendant body, Fortune substance, Moon body-with-soul, Sun princes, MC
works, "a year to every degree"), with al-Ridwān's three-case ascension rule — "in the Midheaven,
… the right circle; if it were in the Ascendant, by the ascensions of your region. But if it
were not in one of these, by the ascensions of these two" (fn 700: proportional semi-arcs);
and **ps-Ptolemy 88**, the Lot of Fortune "in some revolution of years … from the place of the
Sun in the nativity to the place of the Moon, and we will project out from the degree of the
Ascendant of the revolution" (fn 705: "an important variation"). **Appendix D** (pp. 151–159) —
the study guide, twenty-three topic tables cross-referencing PN I–III by chapter; table 23,
"Annual Methods", repeats §2's table. **Appendix E** — the series plan. Bibliography pp. 164–165.

---

## 8. Concordance PN III ↔ PN IV

PN IV sentence ranges are from the PN IV synthesis' maxima table. "=" means the same text, apart
from the wording variants listed in §9.

| PN III | PN IV | Note |
|---|---|---|
| — | I.1 (**1–14**) | preface, 96 chapters, lost companion book: **absent from the Latin** |
| I.1 | I.2 | = definition |
| I.2 | I.3 | = why solar; symbolic units |
| I.3 | I.4 | = objections; the Latin names no *zīj* |
| I.4 | I.5 | = |
| I.5 | I.6 | = chart construction; 14 / 98 / 38; fixed-star clause shorter (item 13) |
| I.6 | I.7 | = the checklist |
| I.7 + I.8 | I.8 | = Ages of Man, split in two |
| I.9 | I.9 | = |
| II.1 | II.1 | = nineteen; #7, #11, and **25** differ (items 4–6) |
| II.2 | II.2 | = five + eight |
| II.3 | II.3 | = ; "configured to benevolents" for "received" (item 3) |
| II.4–II.12 | II.4–II.12 | = Saturn, Jupiter, Mars; II.5's general comments garbled (items 24–25) |
| II.13–II.15 | II.13–II.15 | = the Sun; II.13's proxies garbled (item 2) |
| II.16–II.21 | II.16–II.21 | = Venus, Mercury |
| II.22 | II.22 | = the Moon; the division of the year read differently (item 1) |
| II.23 | II.23, **1–22** | = |
| [II.24] | II.23, **23–71** | Dykes' split; = the named configurations (Figures 56–64) |
| III.1 | III.1 | = specification (items 7–9); chart example variant (item 10) |
| III.2 | III.2 | = seven types, 24 ways, 12 pairs, ranking, gate (item 11); "thirty" fixed stars unnumbered in the Latin |
| III.3–III.7 | III.3–III.7 | = ; III.7's tail = **27–42** |
| III.8 | III.8 | = ; fixed-star places shorter (item 12); quarters cleaner (item 14) |
| III.9 | III.9 | = ; 3⅓° (item 15); the wrap-around rule in both |
| III.10 | III.10 | = |
| IV.1 | IV.1 | = |
| IV.2–IV.7 | IV.2–IV.7, **1–19** | = |
| [IV.8] + App. A | IV.7, **20–28** | assembled by Dykes; Nodes last (items 16–17) |
| V.1 | V.1 | = ; no half-body rungs (item 19); "orb" = period (item 20) |
| V.2–V.8 | V.2–V.8, **1–25** | = |
| [V.9] | V.8, **26–35** | = |
| [V.10] | — | **Latin only** (fn 680); item 21 |
| — | VI.1–VI.6 | lord of the orb, turning, signs: **absent** |
| — | VII.1–VII.9 | transits through houses: **absent** |
| — | VIII.1–VIII.15 | signs, bounds, wells: **absent** |
| — | IX.1–IX.6 | monthly revolutions: **absent** |
| IX.7 (summary) | IX.7 | nine methods; units differ in 6 and 7 (items 22–23) |
| — | IX.8–IX.9 | **cutters and the governor: absent** |
| App. C | — | aphorisms: Dykes' addition, no PN IV counterpart |
| — | PN IV App. A | Dykes' distribution method (Janus/Morinus): PN III has only fn 153's software note |

---

## 9. Differences that matter

Class is given **against the app as it stands, with PN IV as the canon**: 4 = the Latin confirms
what the app does; 5 = absent from the app in both texts; 1 = in the Latin, not in PN IV, not
built. Where the Latin would change a reading if it were preferred, that is said; it should not be
preferred (§0). The app's readings are from `app.py` on branch `synthesis-pn-2026-09-15`.

1. **The Moon's division of the year.** PN III II.22 (pdf p. 83): "we take the partner and
   [also] a planet which was in Cancer … even a planet to which the Moon is being conjoined in
   the sign where she is. By means of the two planets, we divide the year into two. But if there
   were three, [we divide the year] into three." PN IV II.22, **2** (p. 265): "if in that sign
   she connected with not just one, then see how many there are: for if it was two planets, the
   year is divided into two halves; and if her connection in that sign of hers was with three
   planets, then that year is divided into equal thirds." The Latin's "two planets" are the
   proxies just listed (the partner, the Cancer planet); the Arabic's are the Moon's connections.
   Dykes 2010, §6 p. 23: "we take the various planets we have identified, and divide the year
   equally among them. This does not make sense to me." **The app builds the Arabic**
   (`pn4_moon_portions`, "the year divided by the number of planets she connects with"). **Class
   4**; the Latin reading is the one the translator himself could not use.
2. **The Sun's proxies.** PN III II.13 (pdf pp. 74–75): "taking as the [primary] significator
   (with [the Sun]) a planet of the nativity or a planet of the revolution, and the ones which
   are configured with the Sun, wherever the Sun was in that sign". PN IV II.13, **1** (p. 241):
   "[2] the planet which is in Leo in the root of the nativity or in the revolution, and [3] the
   planet to which the Sun hands over the management (so long as it is in its sign)". The Latin
   has lost "Leo" and turned the hand-over into "configured with"; Dykes' 2010 table (fn 119)
   accordingly lists "A planet configured with the Sun" and notes "he does not specify whether
   to use the nativity or the revolution". **The app builds the Arabic** (Leo in root and
   revolution; the hand-over as the Sun's own applying connections per fn 239). **Class 4.**
3. **Reception in II.3.** PN III II.3 (pdf p. 55): "If however it were well disposed in each
   figure, but was not configured to benevolents, it signifies that he will indeed obtain goods,
   but they will be made smaller and reduced gradually." PN IV II.3, **11** (p. 188): "in an
   excellent condition and position in the root, and in the revolution it was like that as well
   except that it is *not* received, then it indicates that he will come to the brink of gain
   … but then it will decrease". The Latin substitutes benefic aspect for reception throughout
   **9–18**. **The app reads II.3, 9–12 by reception** ("under the Configurations page's
   reception rule"). **Class 4.**
4. **Indicator #7, the void Moon.** PN III II.1 (pdf p. 50): "Seventh, the Moon and the planets
   which are being conjoined with her, [when] appearing in the sign in which she is." PN IV II.1,
   **12** (p. 180) adds "and if she were empty in course, then [use] the lord of her house."
   Fn 326: "The Greek text also says that if she is void in course, one should examine her
   dispositor" — so the Latin alone dropped it. The app's row 7 has the fallback. **Class 4.**
5. **Indicator #11.** PN III II.1 (p. 50): "Eleventh, the period or orb of the stars and of the
   twelve houses" (fn 331: "Reading with Schmidt for *annorum* ('years')"). PN IV II.1, **16**
   (p. 180): "The eleventh is the turning of the planets and the twelve houses", footnoted to
   VI.2. The app reads #11 as the turning (VI.2) with its refusal row. **Class 4**; the Latin's
   "period" would send it to the lord of the orb instead, which is already #5.
6. **The ranking sentence.** PN III II.1 (p. 51): "indeed the first is stronger than the second,
   and the second [stronger than] the third. For it was good to arrange their accounting in
   order, but … sometimes the last things are put first, and the first ones put last." PN IV
   II.1, **25** (p. 181): "each one in turn is stronger in indication than the one which is after
   it". The app ranks all nineteen on **25** (nine citations). The Latin is a weaker witness for
   the full ranking, not a contrary one. **Class 4.**
7. **The unit key.** PN III III.1 (p. 91): "take the degrees in the Ascendant of the nativity for
   years, but in the figure of the revolution for months or days, and indeed in the figure of the
   months for days or hours." PN IV III.1, **6** (p. 287): "in the root of the nativity be years,
   but in the revolutions of years months and days, and in the revolutions of months … days and
   hours" (fn 8: B adds "weeks"). Same rule, "or" for "and". The app keys the unit by chart
   level. **Class 4.**
8. **The three-case ascension rule.** PN III III.1 (p. 91), quoted in §4; PN IV III.1, **12**
   (p. 288): "the Ascendant and the things in it are directed by degrees of ascensions of the
   country … while what is in the Midheaven or the fourth is directed by the ascensions of the
   right sphere, and what is not in these three positions is directed according to what we
   stated in our book". **Both defer the third case to another book**; "semi-arcs" is Dykes'
   gloss in both (2010 fn 484 "See for instance al-Qabīsī IV.11-12, and Gansten"; 2019 fn 16).
   The app cites III.1, 12 thirty times and says it "sends the reader to" another book. **Class
   4**, and the app's phrasing is exactly right.
9. **The rate ladder's bottom rung.** PN III III.1 (p. 91): "twenty-five sixtieths [of a second]
   into an hour" — fn 485, "Reading with Schmidt for *tertia*", i.e. the Latin says *thirds*.
   PN IV III.1, **13** printed `25"` and the corpus finding **D-07** restored `25‴` by
   arithmetic and photograph. **The Latin is an independent witness for D-07.** The app's
   `III.1, 13` ladder (twelve citations) has the thirds. **Class 4.**
10. **The chart example.** PN III III.1 (p. 92): "Taurus was ascending with 2º 54', and the Moon
    in it by 12º 43', Mars in Leo by 10º 29', The Sun in Leo [by] 25º 57', Mercury retrograde in
    Leo [by] 22º 7', Venus in Libra [by] 2º 14', Jupiter retrograde in Capricorn [by] 20º 26',
    Saturn retrograde in Aquarius [by] 23º 26', the Head of the Dragon in Virgo [by] 21º 24."
    PN IV III.1, **19** (p. 289): Moon 12° 48′, Sun 15° 59′, Mercury 22° 04′, Venus 2° 54′,
    Saturn 28° 26′, "the Tail" 21° 14′ — with fn 27 recording a manuscript at **23° 26′** and
    fn 28 "This should be the Head". The Latin sides with the minority manuscripts on Saturn and
    the Node and with Dykes' 2010 emendation on the Sun (fn 490, "25" for "15"). The periods that
    follow agree to the day in most steps and differ in three (Saturn's ray 1y 10m 17d vs
    1y 11m 19d; the Lot of Success at 6y 12d vs 6y 6m 22d; the Moon 11m 16d vs 11m 6d). The app
    does not build on the example (`III.1, 23-25` is cited for the *method* of the first bound).
    **Class 4**; still not a fixture.
11. **III.2's ranking and gate.** Identical (§4). PN IV III.2, **104** (p. 315): "the strongest
    of the rays is the opposition, and after that the square, than the trine, and the weakest of
    them is the sextile"; **110** (p. 316): "[only] if those years matched the years of the
    lifespan which his [longevity] indicator in the root [had already] pointed out". The Latin
    says "hīlāj of the nativity" — the *releaser's* years, in both texts, not the house-master's;
    the exemplar's "house-master's years" is a paraphrase. The app cites III.2, 110–111 seven
    times and 103–104 for partner strength. **Class 4.**
12. **Fixed-star places in the revolution.** PN III III.8 (p. 106): "in the Ascendant of the
    revolution or in the Midheaven, or in the degree of the sign of the distribution, or with the
    same degrees, or with one of the luminaries". PN IV III.8, **9** (p. 338): "in the Ascendant
    of the year, or in the degree of the tenth from it, or in the degree of the terminal point, or
    in the degree of the distribution, or with their lords, or with one of the luminaries". The
    Latin lacks the terminal point and the lords. The app's star table uses the Arabic's six
    places. **Class 4.**
13. **Fixed-star places in the root.** PN III I.5 (p. 42): "if there were a fixed star in the
    degree of the Midheaven or with one of the luminaries or the planets appearing in the
    angles". PN IV I.6, **7** (p. 161): "in the very degree of the Ascendant, or in the very
    degree of the stake of the Midheaven, or with one of the luminaries, or with one of the seven
    planets which are in the stakes". The Latin lacks the Ascendant. The app uses the Arabic's
    four. **Class 4.**
14. **The quarters of the year.** PN III III.8 (p. 108), quoted in §4: four quadrants, four
    quarters, no further condition. PN IV III.8, **48** (p. 345): "when the lord of the Ascendant
    is [located] from the Ascendant up to the degree of the Midheaven [it is] eastern, and it is
    the first quarter of the year (if its Ascendant was a convertible sign)" — a subject and a
    condition the Latin does not have at 48 and both texts have at 50 ("especially if the sign
    of the year were movable"). The Latin is the cleaner statement of a rule PN IV's Intro §5
    also reports without the condition. The app does not build the quarters. **Class 5.**
15. **The ninth-part's size.** PN III III.9 (p. 109): "200', namely 3 1/3 degrees exactly".
    PN IV III.9, **4** prints "2 1/3" — corpus finding **P-02**, photo-confirmed as printed and
    left as printed. **The Latin is an independent witness against the print.** The app's
    ninth-parts are 3° 20′. **Class 4.**
16. **The Nodes' delineation, Head before Tail.** PN III IV.8 (p. 125): "if the Head were in the
    third place, he will rule over his own brothers; but if it were the Tail, he will be the
    least of his brothers." PN IV IV.7, **23** prints "Tail" twice — finding **P-03**. Confirmed
    from the Latin. **Class 4** (delineation, not built).
17. **The Nodes' place in the sequence.** PN III IV.8 (p. 125): "in diurnal nativities the
    aforesaid Nodes dispose after Mars, but in a nocturnal one after Mercury." PN IV IV.7, **24**
    (p. 393): "the Head and Tail distribute for diurnal nativities after the years of Mars, and
    for nocturnal nativities after the years of Mercury: and it is when the native enters year
    71". Identical; and PN III IV.1 (p. 116) has the Nodes "not uniting to any planets … for the
    reason that they do not have domiciles" = IV.1, **8**. The app's `pn4_fardar_sequence` puts
    them last in both sects with no sub-periods. **Class 4** — the point "the later tradition
    got wrong" is now witnessed from both transmissions.
18. **The diurnal sequence.** PN III IV.1 (p. 116): "the Sun … then Venus, then Mercury, then
    the Moon, then Saturn, then the others according to the order of their circles" = PN IV IV.1,
    **3**. Fn 586 records Schmidt's "wherever" for the Sun's position and dismisses it: "his
    ability to be a time lord in the firdārīyyāt is unaffected by his natal position." **Class 4.**
19. **The transit grade.** PN III V.1 (p. 130), quoted in §6: degree, bound, sign. PN IV V.1,
    **4** (p. 395) adds "if the planet in the revolution was not in that bound, but between it and
    that rooted degree there was less than one-half its body … it will make a subtraction",
    and **5–6** the applying/separating rungs, with Dykes' Figure 83 of orbs. The app's
    `_pn4_transit_grade` has the Latin's three rungs and not the moieties. **Class 4** for what
    is built; the moiety rungs remain **Class 5**, and Figure 83's orbs are Dykes' table, not the
    text's.
20. **"Orb" in V.1 is the planetary period.** PN III V.1 (p. 131): "if a malevolent reached its
    own proper place, double its orb … if the sign were in a movable sign, you would take the
    lesser orb of this [planet]; if in a double-bodied one, the middle; if in a fixed one, the
    greater." PN IV V.1, **34** (p. 403): "if it was in a convertible sign, it works by its
    lesser period; and if it was in a sign having two bodies, it works by its middle period; and
    if it was in a fixed sign, it works by its greater period." Same rule; the Latin's *orbis*
    renders Greek *periodos* (fn 639), so it must not be read as an aspect orb. Not built.
    **Class 5.**
21. **V.10, Latin only.** PN III [V.10] (pp. 138–139): "you should look at the twelfth-part of
    the Moon, and it will be worse if it is being aspected by malevolents. And if the Moon is not
    being aspected by any [planet], nor does she aspect the Ascendant, he will strive to acquire
    something in that year but he will not acquire it. And know that the Sun burning up the
    planets is worse than a malevolent". No PN IV sentence corresponds (fn 680: "not reflected in
    Pingree"; a search of PN IV for the Moon's twelfth-part, the striving maxim and the combustion
    maxim finds nothing). Dykes' 2010 Intro §9 builds half its Moon rules on it. **Class 1** —
    but with no Arabic witness and outside Dykes' course; record, do not build.
22. **The mighty days' unit.** PN III IX.7 method 6 (p. 144): "Convert the following 30º into
    ascensions, and treat them as equaling 1 year: thus every degree will on average equal
    12 1/6 days". PN IV IX.7, **25** (p. 635): "multiply by 12 days, <4 hours>, 10 minutes, and 30
    seconds … and what it comes to is where the management terminates"; **28**: "this is the
    number which, if you multiply it by 30°, comes to 365 ¼ days". The Arabic's arithmetic only
    works on zodiacal degrees; the Greek (as Schmidt and Dykes 2010 read it) converts to
    ascensions, which is what PN IV's fn 176 says Steven Birchfield "points out … would make more
    sense". **The app builds the Arabic**: `PN4_MIGHTY_DAYS_PER_DEGREE = 12 + 1/6 + 1/120` on
    zodiacal degrees. **Class 4**; the ascensional variant is recorded here for
    `13_open_decisions.md`, since it is the one place the older transmission is arguably the
    better astronomy.
23. **The small days' unit.** PN III IX.7 method 7 (p. 144): "at a rate of 59' 08" per degree" —
    a slip; PN IV IX.7, **29** (p. 636): "a day for every 59′ 08″". The app's
    `PN4_SMALL_DAYS_RATE` is per day. **Class 4.**
24. **II.5's mixed-up conditions.** Fn 371 (p. 175) prints the Greek's four conditions and says
    "It does not make sense to me that (2) squares and oppositions from a planet in a bad
    condition should be better than (3) trines and sextiles"; Dykes rewrote the paragraph. PN IV
    II.5, **59–62** (p. 207) has it coherently: an impeded planet's trine or sextile "introduces
    confusion and distresses and toil", its square or opposition "diminishment and harm"; a
    fortunate planet's trine or sextile improves "greatly", its square or opposition "below
    that". The 2010 rewrite matches the Arabic. Delineation; not built. **Class 5.**
25. **Aspect strength for harm.** PN III II.5 (p. 60): "the square aspect has greater power for
    harming than the trine does, since the trine is weaker for enmities than the square is."
    PN IV II.5, **64** (p. 207): "the opposition is more powerful than the aspect of the square in
    the occurrence of something detestable, and is weaker [than the square] in the acquisition
    of good fortune". Different sentence, same direction; the Latin's is trivially true. Not
    built. **Class 5.**
26. **The substitute lord's condition.** PN III [II.24] (p. 86): "especially if the Lord of the
    sign of the profection or the Lord of the Ascendant of the revolution did not aspect its own
    Lord" — fn 468 "should probably read 'sign'". PN IV II.23, **41** (p. 278): "especially if
    the lord of the terminal point or the lord of the Ascendant was falling away from an aspect
    to its own house". The conjecture is confirmed. The rule (II.23, 41; III.8, 15) is not built
    in the app, and Dykes doubts its value in both volumes. **Class 5.**
27. **The Moon's sign and the Ascendant of the year.** PN III II.22 (p. 83): "it has an equal
    role to the horoscope of the year". PN IV II.22, **14** (p. 266): "its power is close to the
    power of the Ascendant of the year". Weaker in the Arabic. Not built. **Class 5.**

**Twenty-seven items; seventeen Class 4, eight Class 5, one Class 1, one (10) Class 4 with a
warning.** Nothing here is Class 2 or 3: no reading the app makes from PN IV is contradicted by
the Latin, and no claim on a page cites PN III.

---

## 10. What this book adds to the corpus that nothing else had

1. **A second transmission for Books I–V.** For every apparatus sentence the app rests on in
   those Books — the nineteen indicators, the unit key, the three-case rule, the rate ladder,
   the partner rule, the seven types and twenty-four ways, the partner ranking, the gate, the
   *fardār* sequence with the Nodes last, the transit grade — the Latin agrees with the Arabic.
   Three printed defects in PN IV (D-07, P-02, P-03) are now witnessed from the other side.
2. **Dykes' 2010 Introduction §12**, the transit checklist marked by source, and **§15**, the
   only sustained reading of overcoming in Abū Ma'shar's revolutions anywhere in the corpus.
3. **The "partners work across bounds" statement** (§8, pdf p. 25) in plain words.
4. **V.10**, a Latin-only chapter of Moon and combustion maxims.
5. **Appendix C**: ps-Ptolemy 77 with al-Ridwān's three-case rule and ps-Ptolemy 88's
   revolution Lot of Fortune projected from the revolution's Ascendant.
6. **The dating of the III.1 chart** to Abū Ma'shar's own nativity (fn 488, from Pingree), which
   PN IV's Introduction discusses without the Latin's manuscript readings.

## 11. What it does not add

- **Nothing on the cutters, IX.8, or the releaser choice** (IX.8, **123**): Book IX is absent
  except for IX.7, and IX.7 is a summary, not a translation. The app's thirteen citations of
  IX.8, 123 and its whole longevity apparatus have no Latin witness and needed none.
- **Nothing on the lord of the orb's derivation (VI.1), the turning (VI.2), the monthly
  revolutions (IX.1–5), the wells (VIII.15), or the quadruplicity direction rule (IX.1, 26–34).**
- **No sentence numbers**, so nothing in it can be cited to the app's convention without a
  page-and-paragraph locator; and **no printed folio** in the text layer, so even that is by
  PDF page.
- **No table of ascensions, no bounds table** (Appendix B is a heading), no figures.
- **No new technique.** Dykes says so at §16: "For the most part, there is no new technical
  vocabulary in On Rev. Nat."

---

## 12. Reading notes worth keeping

- **Dykes' 2010 footnotes are the emendation record.** Every "Reading with Pingree/Schmidt for
  …" (there are more than a hundred) marks a place where the Latin was corrected from the Greek;
  where the Arabic later agreed with the correction (items 2, 9, 24, 26), the 2019 volume does
  not always say so. Read the two volumes' notes together at any disputed sentence.
- **The Latin is the worse text and the 2010 Introduction knows it**: "at any rate, the Latin
  version seems a little more mixed up than the Greek" (fn 371). Where PN III and PN IV differ,
  assume the Arabic unless the Arabic's own footnote reports a manuscript split (item 10).
- **Dykes' doubts are the same in 2010 and 2019** — the ninth-parts' wrap-around, the derived
  domiciles, the substitute lord, the III.1 example — and were formed on the Latin first. His
  2019 rejection of the quadruplicity profection rule has no 2010 counterpart because IX.1 is not
  in the Latin.
- **"Orb" and "period" are one word here.** Fn 324 (II.1 #5), fn 331 (#11), fn 639 (V.1): Greek
  *periodos*, Latin *orbis*, English "orb" or "period" as Dykes chose. Never read a PN III "orb"
  as degrees of aspect.
- **Watch the editorial chapters.** II.24, IV.8, V.9, V.10 are Dykes' divisions and one of them
  (IV.8) is spliced from two places in the Latin; cite the PN IV sentence, not the PN III
  chapter, for anything in them.
- **The text layer is clean but not perfect**: the Persian at II.3 is mangled, two footnotes
  lost their italics markup (fn 635, 679), and the study guide's tables are column-scrambled.
  Nothing doctrinal sits on any of these.
