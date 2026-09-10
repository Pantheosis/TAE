# Phase 1 — Abū Ma'shar, *On the Revolutions of the Years of Nativities* (*Persian Nativities* IV)

Source: `consolidated_texts/pn4/pn4_complete/persian_nativities_iv.md`, pinned at blob
`295eb22ad58ebc5ad0c330ede60e5f4b0159aee9` (md5 `06a9b805b29d890525018ecf17fef755`,
HEAD `c85fff8`), 13,964 lines. **Re-checked byte-identical at the end of the read.** Read
2026-09-10. PN IV's own pagination pp. i–xii and 1–674; `CORPUS_MANIFEST.md`'s rule holds —
**never compare a bare page or figure number across volumes.** PN IV Fig. 63, Sahl Fig. 63 and
*Gr. Intr.* Fig. 63 are three different figures.

**Companions.** The answers this read was commissioned for are in
`04_timing_answers_2026-09-10.md`. Text defects are in
`consolidated_texts/process/PN4_READTHROUGH_FINDINGS_2026-09-10.md`. **Seven corpus defects and
three printed errata were found; two of them change engine output.** Where a passage below sits
on one of those, it is marked **[see findings D-nn]**.

**Coverage.** Front matter, the Editor's Introduction, Books I–IV, Book IX and Appendix A were
read line by line, with the exceptions listed in §11 of the findings file. **Books V–VIII
(pp. 395–551) were deferred** per `PN4_READING_BRIEF.md` §2 and are summarised here only from
their chapter titles and from cross-references made elsewhere in the volume. Do not cite this
file for Books V–VIII.

---

## Heading and citation conventions (the heading trap, PN IV edition)

Chapters are `### Chapter N.M: …`. **Three traps**, each of which broke a naive grep of mine
before I corrected it:

1. `Chapter I.1` is written `### <Chapter I.1: Introduction>` — **pointed brackets**, Dykes'
   mark for a title supplied editorially because the manuscripts lack it.
2. **Eight** headings are bold-wrapped, `### **Chapter X.Y: …**` (findings O-01).
3. `# BOOK III` is **missing from the body altogether** (findings D-01); every other Book carries
   one. Book I's is `## BOOK I: <ON THE REVOLUTIONS OF YEARS>`, at H2 and in pointed brackets.

Sentence numbers are **bold** and **restart per chapter**. Footnotes **restart per Book**
(eleven runs: Introduction 1–135, I 1–90, II 1–377, III 1–265, IV 1–100, V 1–73, VI 1–139,
VII 1–114, VIII 1–65, IX 1–328, Appendix A 1–…), so "fn. 222" is **ambiguous** unless the Book
is named — the opposite of *Gr. Intr.* Book VII. Page markers are `*[PN IV p. N]*`.

**Citation form used here and in the answers file: `PN IV III.1, **12**`** — Book, chapter,
sentence. This is Dykes' own convention, stated at §19 (p. 144).

Per-chapter sentence maxima, derived from the pinned file:

| Book | maxima by chapter |
|---|---|
| I | 1=14 2=6 3=13 4=31 5=10 6=11 7=26 8=37 9=33 |
| II | 1=33 2=21 3=20 4=29 5=84 6=28 7=29 8=39 9=16 10=15 11=42 12=20 13=14 14=13 15=15 16=12 17=18 18=18 19=8 20=12 21=15 22=28 23=71 |
| III | 1=50 2=112 3=13 4=13 5=14 6=14 7=42 8=54 9=49 10=7 |
| IV | 1=37 2=25 3=15 4=30 5=19 6=18 7=28 |
| V | 1=52 2=16 3=13 4=21 5=23 6=15 7=18 8=35 |
| VI | 1=19 2=26 3=152 4=38 5=24 6=46 |
| VII | 1=28 2=38 3=20 4=18 5=12 6=12 7=12 8=12 9=29 |
| VIII | 1=8 2=8 3=8 4=11 5=9 6=7 7=8 8=5 9=5 10=5 11=5 12=5 13=8 14=9 15=31 |
| IX | 1=45 2=38 3=10 4=109 5=126 6=20 7=79 8=128 9=25 |

**96 chapters in nine Books** — matching the Table of Contents and Abū Ma'shar's own count at
**I.1, 3**: *"there are nine Books and ninety-six chapters."*

---

## 0. What this book is, and why it is not what the checklist expected

`04_timing_open_questions.md` was written on the premise that PN IV would settle the corpus's
longevity disputes. **It does not, and the reason is structural rather than accidental.**

PN IV is a book about **revolutions** — the annual chart and everything recalculated with it. It
treats the releaser and house-master as *already identified* and spends its effort on what
happens afterwards: distributing the releaser, reading the year, timing the month and the day.
Abū Ma'shar says so himself, and unusually plainly:

> "there is great difficulty and much confusion in deriving the years of the indicator of the
> lifespan which is like the root … but a statement of the truth of that, and its correctness, is
> found in the book which we worked on concerning **nativities**." — **IX.8, 123** (p. 665)

So the book answers the *frame* questions completely and the *selection* questions not at all.
That maps almost exactly onto §4's six items: items 1, 3, 4, 5 and 6 come back full; item 2 comes
back as a well-specified procedure with an unspecified first step.

The second surprise is how much of the apparatus is **integrated**. **I.6, 6** puts the
distributor, the partner, the *fardār* lord, the *fardār* sub-lord and the lord of the orb into
the revolution chart itself. The revolution is not one technique among several; it is the surface
on which all of them are read together. Anything the engine builds should reflect that.

---

## 1. The Editor's Introduction (pp. 1–144) — nineteen sections

Dykes' Introduction is not front matter. It is 144 pages, roughly a fifth of the volume, and its
§§5–17 are the practitioner's account of every technique in the book. **It is also the only place
some things are stated** — the vocabulary lists at §7 (p. 64) and §8 (p. 77) and §16 (p. 139) are
the definitions the rest of the corpus lacks.

| § | Topic | pp. | Load-bearing for |
|---|---|---|---|
| 1 | Abū Ma'shar; sources; his astronomy | 1–7 | dating, *zīj* mixing |
| 2 | Definitions: root, distribution, profection, revolution, time lord, indicator | 7–13 | the whole vocabulary |
| 3 | Theory of prediction; why the revolution is solar | 14–25 | Q19 |
| 4 | Interpreting a planet | 25–37 | "advancing" = quadrant |
| 5 | **Profections** | 37–49 | item 4 |
| 6 | Whole signs, quadrant cusps, intercepted signs | 49–60 | house handling |
| 7 | **Distributions** | 61–75 | item 3 |
| 8 | **Solar revolutions** | 75–88 | item 1 |
| 9 | **Monthly revolutions and monthly profections** | 88–106 | items 1, 4 |
| 10 | The Moon | 106–08 | |
| 11 | Transits | 108–15 | Q23–25 |
| 12 | ***Fardārs*** | 115–21 | item 5 |
| 13 | The lord of the orb | 121–29 | |
| 14 | Ninth-parts | 129–32 | |
| 15 | **Summary statements about timing** | 132–35 | item 6 |
| 16 | **Longevity** | 135–40 | item 2 |
| 17 | Lots | 140–42 | |
| 18 | Fixed stars, eclipses, comets | 142–43 | |
| 19 | Manuscripts and editorial remarks | 143–44 | conventions |

**Manuscripts** (§19): **B** = Oxford Bodleian Digby Or. 5 (primary, with marginalia the others
lack); **P** = Paris BNF Ar. 2588 (close to B); **E** = Escurial Ar. 917 (often divergent,
sometimes better); **T** = Tehran Majlis 6433 (incomplete: III.2, **31** to IX.7, **61**).
Variant readings are footnoted constantly and by siglum, which is one reason fabrication would be
conspicuous here.

**§19 contains no statement of the unprinted-sentence-number convention** that Dykes gives at
*Gr. Intr.* §9 and Sahl §8 — confirming independently what `PN4_AUDIT_2026-09-09.md` observed.
The convention operates in PN IV anyway (p. 462 s. 26). **Do not look for it again.**

**Two places where Dykes' Introduction and Abū Ma'shar's text disagree**, both recorded in the
answers file:

- Intro §3 p. 21 point 3 says distributions outrank profections. **II.1, 25** says the reverse.
  Dykes cites no sentence; his own fn 321 concedes the ordering. **Follow II.1, 25.**
- Intro §2 p. 7's monthly-revolution example uses 12° 23′ where the rule requires 12° 22′.
  A printed erratum, four witnesses against it **[findings P-01]**.

---

## 2. Book I (pp. 145–178) — the revolution chart itself

Nine chapters. This is the Book the checklist's item 1 needed, and it delivers.

- **I.1** — preface; the nine Books and ninety-six chapters enumerated (**4–12**). **14**: Abū
  Ma'shar wrote a companion book of worked chart examples, now lost.
- **I.2** — the definition. **1**: the Sun's return to his rooted position, 360° in "365 days (and
  a fraction)". **4**: derive the Ascendant and the twelve houses, and the planets' positions.
  **5**: the profection, a sign per year from the Ascendant. **6**: the terminal sign, the
  revolution's Ascendant and the planets' positions all differ each year, "for that [reason] the
  conditions of people's years will differ."
- **I.3** — why solar and not lunar. **3–7**: the four seasons return "the time to a likeness of
  the original condition"; the Moon cannot do this. **7**: "the months of nativities come to be
  from the transit of the Sun in the signs, **a month for every sign**." **9–13**: the *symbolic*
  solar units — 30° is a "month of the Sun", 1° a "day", 2′30″ an "hour" — with **13** noting they
  diverge from clock time. These are a different thing from the real-time MR charts, and IX.7,
  **78** uses them again; do not conflate.
- **I.4** — the four objections and the replies. **23–31** is the passage on mixing *zījes*;
  **29** names the *Sindhind*, the *Almagest* and the *Zīj al-Shāh*; **31** endorses the Hipparchan
  tropical year for revolutions while using the mean Sun for the nativity. Dykes says this does
  not cohere (Intro §1 p. 6), and he is right.
- **I.5** — the benefit of revolutions.
- **I.6** — **the chart-construction chapter**, and the most operationally useful eleven sentences
  in the book. Covered in full in the answers file, item 1. Two things to carry forward: the
  revolution chart is a **bi-wheel** with the natal positions drawn into it (**4**), Abū Ma'shar
  placing the revolution **inside**; and **6** loads the distributor, partner, *fardār* lord,
  *fardār* sub-lord and lord of the orb into the same figure. Figure 52 totals 154 points and the
  arithmetic checks.
- **I.7** — the twenty-six-point reading checklist. **2** asks first which natal house the
  revolution's Ascendant occupies. **26** states the comparison principle: "its indication will be
  according to its place and condition in the two times together."
- **I.8** — **the Ages of Man**: Ptolemy's seven, ordered by sphere, Figure 53. Moon 4 / Mercury
  10 / Venus 8 / Sun 19 / Mars 15 / Jupiter 12 / Saturn 30. **34–37** explicitly refuses to
  subdivide them into sevenths as the *fardārs* are subdivided. **35** misdescribes the *fardār*
  order as following the exaltations — an internal inconsistency, recorded in the answers file.
  **12** gives the Moon's middle years as **39½**, an independent witness for the luminary
  construction settled in `project_contested_table_readings`.
- **I.9** — four things the astrologer must know before judging: the native's age, class, physical
  possibility, and actual circumstances. **33** and Figure 54: a native's revolutions keep
  indicating for **living** parents and children even after the native's own death — the PN IV
  counterpart to *Nat.* 4.1, **3**'s "fathers do not have a revolution."

---

## 3. Book II (pp. 179–285) — the lord of the year

Twenty-three chapters, of which **II.1, II.2, II.3 and II.23 are apparatus** and II.4–II.22 are
delineation on a fixed template (each planet: suitable condition / bad condition / in the houses).

**II.1, 5–24 — the nineteen indicators of the year, ranked**, with **25**: *"each one in turn is
stronger in indication than the one which is after it."* This is the ranking the engine should
use, and it is the single most quotable sentence in the book for item 4:

1 sign of the terminal point + its lord · 2 the distribution and distributor · 3 the partner ·
4 the *fardār* lord + sub-lord · 5 the lord of the orb · 6 the SR Ascendant + its lord ·
7 the Moon and what she connects with · 8 transits over rooted positions · 9 the lord of the year
in the twelve revolutionary houses · 10 planets relative to their own houses · 11 the profection
of planets and houses · 12–13 the terminal point or SR Ascendant coinciding with a rooted house
or a rooted planet · 14 a planet changing house between charts · 15 connections of house lords ·
16 shifting through houses and bounds · 17 connections through the year · 18 a planet in its own
or another's house or bound · 19 Head and Tail.

Each item is footnoted to the Book or chapter that treats it — a table of contents for the
apparatus, and the fastest way into the book.

**II.1, 29–33** is Abū Ma'shar's complaint that his predecessors applied the *annual* indicators
to months and days unchanged, and his statement that each month needs its own Ascendant, planets,
rays, twelfth-parts and Lots combined with the year's and the root's. That is the programme of
Book IX.

**II.2** splits the indicators into **five for the body** and **eight for the soul**. The body
list is where the **two simultaneous distributions** first appear explicitly: "the bound which the
distribution has reached, **from the Ascendant**" (**6**) and "the bound which the distribution has
reached, **from the [longevity] releaser**" (**7**). The soul list is the same eight that IX.9,
**1–9** calls the special indicators of the year.

**II.3, 1** defines the terminal point and the lord of the year (Pers. *sālkhudhāh*). **2–4** give
the natal and revolutionary analysis of the sign; **5–8** the four-way root/revolution comparison
(Figure 55, reprinted from Figure 8); **9–19** place and reception. **17** names the four places
in aversion to the Ascendant: second, sixth, eighth, twelfth.

**II.13, 1**, **II.14, 1** and **II.22, 1–5** carry the **luminary proxy** rules — the four (five,
with the void-Moon fallback) alternatives when a luminary is lord of the year. Figure 16 (p. 44)
tabulates them.

**II.22, 2–3** is a genuine timing rule that nothing in the corpus hinted at: **if the Moon
connects with two planets while still in her sign, the year divides into halves; with three, into
thirds; with more, by their number** — each portion judged by its planet.

**II.23** treats the SR Ascendant and its lord. **1**: "After the sign of the terminal point, the
power of the indication belongs to the distributor" — confirming II.1's ranking. **3**: the
revolution's stakes measure the power of **rooted** planets too. **14–71** is a long series of
named configurations, many with figures (56–64), several cross-referenced from IX.8 as
death-indications. **[findings D-06 sits at p. 282 inside this run.]**

---

## 4. Book III (pp. 286–363) — directions and distributions

Ten chapters. **The highest-consequence Book for the engine**, and the one `PN4_READING_BRIEF.md`
§6 was right to front-load.

**III.1 is the specification.** In eighteen sentences it gives: the five releasers and what each
is directed for (**3–4**); everything else that is directed (**5**); **the unit key by chart
level** (**6**); the computation (**7–9**); the definition of the position of the distribution and
the distributor, with the note that the distributor need not aspect its own bound (**10–11**);
**the three-case ascension rule** (**12**); **the rate ladder** (**13**) **[findings D-07]**; the
restriction of the name *jār bakhtār* to the Ascendant's distributor (**14**); the partner and the
shifting of management (**15–16**); the twelfth-parts and Lots (**17**).

**III.1, 19–45 is the worked chart example, and it is unusable.** Dykes' verdict (Intro §7,
pp. 73–75) is that it should be ignored: the data at **19** and **22** are mutually inconsistent
(Saturn at 28°26′ Aquarius in one and 9°24′ in the other), and the example accumulates Lots as
though each becomes a releaser when met, contradicting **III.1, 47** and the principle that every
point is directed from its own natal position from birth. **Do not build a test fixture on it.**
Use Appendix A's Figures 140–141 instead.

**III.2 is the interpretive core**, 112 sentences:

- **1–3** the scope reconciliation between the distribution and the lord of the year — see the
  answers file, Q17. This is the passage that resolves corpus disagreement #1.
- **4–9** a nine-point checklist for any distribution.
- **10–54** seven "static" distributor/partner types (Figure 66).
- **55–86** the twenty-four transitions (Figures 68–73), built from six factors: the two bounds,
  their two lords, and the two partners.
- **87–101** twelve interpretations covering those twenty-four.
- **103** ranking: lord of the distribution > manager by **body** > lord of the **ray**.
- **104** ray strength: **opposition > square > trine > sextile**. Hard aspects outrank soft ones
  *as partners*; this is easy to implement backwards.
- **105–06** the twelve managements are about **rooted** bodies and rays; revolutionary planets in
  the bound are handled separately at **43, 46–47, 54**.
- **107–09** directing to the thirty fixed stars of good fortune, and to stars of toil or killing.
- **110–11** **the longevity gate** — no death without the house-master's years. Quoted in full in
  the answers file.

**III.3–III.7** are the per-planet distributor delineations (Saturn, Jupiter, Mars, Venus,
Mercury), each pairing the distributor with each possible partner. **III.3, 1** carries the
five-releaser list in Abū Ma'shar's own words; **III.3, 2** ranks the longevity releaser's
distribution above the other four.

**III.8** partners the lord of the year, the distributor and the Ascendant. **9–14** fixed stars,
comets and eclipses on the four sensitive positions (natal Ascendant, terminal point, SR
Ascendant, sign of the distribution). **15–16** the natal planet that displaces the lord of the
year. **48–50** divides the **year** into quarters by the quadrants from the SR Ascendant.
**51–54** directs the rooted Lots to the fortunes and infortunes.

**III.9–III.10 — ninth-parts** (*nahbahar*), attributed to India. Each sign divided into nine
portions of 3° 20′ **[findings P-02 sits on III.9, 4]**, ruled by the lords of the signs in order
from the convertible sign of the triplicity. **III.9, 14–16** subdivides each ninth-part into
thirds ruled in *darījān* order (lord of the ninth-part, lord of the 5th sign from it, lord of the
9th). **III.9, 16 and 22–38** contain the rule Dykes finds hard to believe and which is genuinely
unusual: **a direction entering a ninth-part must complete *all three* subdivisions, wrapping
around, before moving on** (fn 247). **III.10** gives the Indian lord of the year — the lord of the
first ninth-part of the sign of the year — which restricts the lord of the year to **four planets
only** (Mars, Venus, Saturn, the Moon).

Abū Ma'shar's own attitude: use both systems, "each by itself, so that the investigation into
knowing the condition of the years will be strengthened" (**III.9, 3**). Dykes ignores the
ninth-parts throughout and says so. **Recommend the engine follow Dykes: record, do not
implement.**

---

## 5. Book IV (pp. 364–394) — the *fardārs*

Seven chapters, one per planet, and the shortest Book. Its apparatus is entirely in **IV.1, 1–10**
and **IV.7, 24–28**; everything between is delineation drawn from al-Andarzaghar via
al-Dāmaghānī, footnoted "Da. n" throughout.

The complete system is set out in the answers file, item 5. The essentials:

- **IV.1, 2** — the nine periods and the 75-year total.
- **IV.1, 3–4** — descending Chaldean order from the sect light; diurnal starts at the Sun,
  nocturnal at the Moon.
- **IV.1, 5–7** — seven equal sub-periods, in the same descending order from the lord itself.
- **IV.1, 8** — **the Nodes take no sub-periods and partner with nothing, "because they do not
  have houses."**
- **IV.7, 24** — **the Nodes always come last, in both sects**, entering at year 71. This is the
  point the later tradition got wrong, and Abū Ma'shar is unambiguous.
- **IV.7, 25** — after 75 the cycle returns to "the luminary which he began from at his birth".
- **IV.7, 26** — a short lifespan ends "in the *fardār* of the planet which did reach".
- **IV.7, 27–28** — the delineations are the planets' *natural* indications; natal condition and
  condition at handover alter them.

**Figure 43 (p. 116) is the table of the whole system, and the corpus has gutted it**
**[findings D-05]**. The photo-verified reading is in the answers file. The prose at **IV.1, 2–4**
recovers it independently, and both check to 75 against *Gr. Intr.* VII.8, **3**.

**IV.4, 4–11** is worth reading for its own sake: Abū Ma'shar explains that his predecessors wrote
one delineation per planet-pair aimed at an adult client, which fails because the same pair falls
at very different ages in the two sects — a nocturnal native has the Moon *fardār* at ages 0–9, a
diurnal one at 31–40. So he keeps al-Andarzaghar for one sect and writes his own for the other.
This is the clearest instance in the volume of Abū Ma'shar reasoning about a source rather than
copying it.

---

## 6. Books V–VIII (pp. 395–551) — DEFERRED, not read

Recorded from the Table of Contents and from cross-references made elsewhere in the volume. **No
claim here rests on reading these pages.**

- **Book V — transits** (pp. 395–425). V.1 is the general treatment: the "completeness" of a
  transit or planetary return graded by same bound / within half orb / same sign applying / same
  sign separating (**V.1, 1–7**); three approaches to interpretation (**V.1, 11–23**), of which the
  third, **derived domiciles**, Dykes urges the reader to ignore as "bogus" (Intro §11, pp. 113–15)
  — he has underlined in the translation every phrase he believes was generated that way.
  Figure 83 (p. 397) is a table of **Persian planetary orbs**. V.2–V.8 are per-planet.
- **Book VI — planets in the signs** (pp. 426–475). **VI.1** is the lord of the orb. **VI.2** is
  "the turning of the houses of the root, & the direction of degrees" — cited from Intro §5 as the
  authority for *what* may be profected (**VI.2, 1–20**), so it is apparatus and arguably should
  not have been deferred. **VI.3, 4–149** is the big delineation list for the SR Ascendant or
  profection coming to a sign with an SR planet in it. **VI.4, 3–8 and 29–30** carry the
  activation and elicitation rules cited throughout Books I–III. **VI.6** treats connections
  between house lords.
- **Book VII — transits through the twelve houses** (pp. 476–522). Dykes recommends *against*
  using this list (Intro §4, p. 27): "shot through with odd and unlikely interpretations, with too
  much repetition to be of value." **VII.1, 1–4** is the exception and is apparatus — the two rules
  for transits through signs carrying two cusps, and through intercepted signs.
- **Book VIII — planets in signs, bounds and wells** (pp. 523–551). VIII.1–7 signs, VIII.8–14
  bounds, **VIII.15 the wells**, with Figure 98 (p. 547) reproducing *Gr. Intr.* V.21.

> **The wells table again.** PN IV's Figure 98 differs from Abū Ma'shar's own *Gr. Intr.* Figure 62
> in three cells (PN IV omits Aries' 29th and Pisces' 28th, and prints Gemini's 13th for the
> 12th). Both readings are photo-verified and the corpus transcribes PN IV **as printed**, without
> reconciliation. This is already settled as `project_pn4_wells_conflict`: `app.py` follows
> *Gr. Intr.* Fig. 62, PN IV Fig. 98 is a variant. **Nothing in this read changes that**, and the
> deferral of Book VIII does not put it back in question — the table itself was verified in the
> earlier pass.

---

## 7. Book IX (pp. 552–670) — months, days, hours, and the cutters

Nine chapters and the longest Book. Three distinct subjects.

### 7a. Monthly revolutions (IX.1–IX.5)

**IX.1** lists the **seven monthly indicators** (Figures 34 and 100) and the rules for profecting
them; **IX.1, 26–34** is the **quadruplicity direction rule** (fixed forward, convertible
backwards, double-bodied by half), which Dykes rejects and Abū Ma'shar states plainly. **IX.1,
40–45** rejects three rival methods — Dorotheus's monthly Lot, Ptolemy's 28-day count, and the
30½-day solar month — with the reasons.

**IX.2** handles **the first month**, which is the awkward case because the SR chart stands for
both the year and month 1. The rule (**IX.2, 3**) is that a topic manifests in the first month
when the **lord** of its indicator sits **in one of the signs of the five rooted indicators**,
especially the SR Ascendant, and is fast and angular. Figures 104, 107 and 108 tabulate the
topic/native comparison, which is Abū Ma'shar's real innovation in this Book: he judges not only
whether a topic is well or badly indicated but **how it bears on the native**, by the mixture
between the topic's indicators and the native's.

**IX.3** is the MR chart: **2** gives the casting rule ("the like degree and minute"), **4–8** what
to draw, and **10** the point count — 21 planets, 147 rays, 57 twelfth-parts across three wheels.
All three check.

**IX.4** is the combinatorics of house significations across the three (four, with the MR)
Ascendant schemes, running to 32 combinations per planet and, multiplied out by months, 3,300 per
year. Dykes calls it an exercise of little practical value and I agree. **Skim.**

**IX.5** covers months 2–12 and ends with **three "quick" methods** (**107–26**, Figures 132–134)
which are the practical residue of the whole Book: (1) the lord of the MR Ascendant, judged in the
MR and compared to SR and root; (2) monthly profections from the natal Ascendant and natal Lot;
(3) monthly profections from the SR Ascendant and SR Lot. **IX.5, 99–102** assigns subject matter:
the Ascendants and their signs to body and to the native's action, the Lots to assets and
fortune, the lords to soul and to thought.

### 7b. Days and hours (IX.7)

**Nine methods**, all in **equal** hours (**56**), not unequal planetary hours. Two of them matter
for the engine because they are directions rather than counting schemes:

- **Method 6, "the mighty days"** (**23–28**): treat the profected 30° increment as the year and
  direct through it at ~12d 4h per degree, with bound lords and partners as in a distribution.
- **Method 7, "the small days"** (**29–33**): **direct the SR Ascendant around the SR chart at
  59′08″ per day**, one circuit per year, with bound lords and partners. **32** concedes that doing
  this zodiacally rather than ascensionally is "an approximation".

**79** declines to cast day or hour charts as unnecessary.

### 7c. Longevity and the cutters (IX.8)

128 sentences, and the chapter the checklist's item 2 needed. Its opening is unlike anything else
in the corpus: Abū Ma'shar is answering a student who has asked how to find his own death, and
he spends three sentences telling him he should not want to know before giving him sixty pages of
method (**1–3**).

Structure: the house-master procedure and the corroboration requirement (**4–7**); the test by
direction, profection and revolution (**8–9**); modulation by the strength of the house-master
(**10–13**); **the four ways of cutting** (**14–18**), then each worked —

1. **nineteen cutters** among the stars (**19–55**), Figure 137;
2. **ten positions** (**56–70**);
3. **five distribution transitions** (**71–78**);
4. **corruption of the year** (**79–118**), some forty configurations, each cross-referenced to
   its home passage elsewhere in the volume.

Then the grading rule (**112–13**), Abū Ma'shar's restatement (**119–22**), the admission that the
house-master's years are derived elsewhere (**123**), the same method applied to relatives
(**124–26**), and the Indian ninth-part version (**127–28**).

All of this is set out with citations in the answers file, item 2.

### 7d. IX.9 — the eight special indicators

**1–9** lists them; **10** defines the **governor**: if all eight fall on one planet, "then it
alone would be the governor of the indication for the condition of the year." **16–23** works two
examples of combining a planet's house meanings across root, profection and revolution
(Figures 138–139). **[findings D-08 sits at p. 670, at the very end of this chapter.]**

The book closes: *"The book is ended."*

---

## 8. Appendix A (pp. 671–674) — calculating distributions

Dykes' own, not Abū Ma'shar's, and the most immediately implementable four pages in the volume.

The identity it rests on: **the sphere turns 1° in 4 minutes of clock time, and 1° of the equator
is 1 year.** Therefore:

- to find the age at a given distribution: animate the chart until the Ascendant reaches that
  degree, and **divide the elapsed minutes by 4**;
- to find the distribution at a given age: **multiply the age by 4**, add that many minutes to
  the birth time, and read the bound and the most recent body or ray.

This is exact and latitude-correct, needs no ascension table, and works for the MC as well
(directed separately, because the two move at different rates). Two worked examples with figures:
Mars–Mercury at age 17.97 (Figure 140) and Saturn–Jupiter at age 42 (Figure 141).

Also given: the Janus settings (Egyptian bounds, zero latitude; "Deg for a year" for natal, and
59′08″ per day for SR distributions **[findings O-05 on the printed notation]**) and the Morinus
settings (Placidus semi-arc, Egyptian terms, whole-sign houses, static/Ptolemy keys). These
identify **which** primary-direction convention Dykes takes PN IV to require:
**Placidian semi-arc, Ptolemaic key, zodiacal-latitude-zero promittors** — consistent with
**III.1, 12**'s three-case rule.

**Appendix B, the table of ascensional times, is at pp. 675–677 — inside the volume, outside the
OCR'd range.** See the findings file §10.

---

## 9. What this Book adds to the corpus that nothing else had

Ordered by how much it unblocks.

1. **The *fardār* system, complete** — sequence by sect, the years, the sub-periods, the Nodes'
   placement and their exclusion from sub-periods. The corpus previously had nine numbers and a
   pointer (*Gr. Intr.* VII.8, **2**: "we have stated them in the book in which it is necessary to
   mention them"). **This is that book.**
2. **The three-case ascension rule** (**III.1, 12**) — oblique for the Ascendant, right for the
   meridian, semi-arcs for everything else. The corpus had "by the ascensions of the signs in that
   city" and nothing about the other cases.
3. **The unit key by chart level** (**III.1, 6**) — root years, revolution months, month days.
4. **The revolution chart's contents** (**I.6, 1–11**) — the corpus had no account of this at all.
5. **The nineteen ranked indicators** (**II.1, 5–25**) — and with them the resolution of
   disagreement #1.
6. **The cutters**, in an enumerated and implementable form (**IX.8, 14–118**), including the
   nineteen stars with positions and a precession rate, and the **gate** at **III.2, 110–11**.
7. **The seven monthly indicators** and the machinery of monthly revolutions — a whole technique
   the corpus knew only as "a month per sign".
8. **Vocabulary.** *Jār bakhtār*, *sālkhudhāh*, *hīlāj*, *kadukhudāh*, "foundation of the
   lifespan", increaser and decreaser, cutter, governor, owner of the revolution, terminal point.
   Several of these appear in Sahl untranslated or under-defined.

## 10. What it does not add

- **No releaser-selection rule.** Five candidates, no method of choosing (**IX.8, 123**).
- **No house-master ranking, no years-granting table, no quantified increasers.** Deferred by the
  author to his own book on nativities.
- **Nothing on Valens's Fortune-years**, the ascensions-and-periods method, or the
  meeting/opposition death rule of *Nat.* 8.7.
- **No "four signs" rule** for a corrupting infortune.
- **No per-planet or per-sign-type time unit** — so corpus disagreements #5 and #6 stand
  untouched.

---

## 11. Reading notes worth keeping

- **The book is heavily self-cross-referenced, and the references are reliable.** IX.8's forty
  year-corruption cases each footnote their home passage in II.3, II.23, III.2, III.8, IV, V or
  VI, and every one I followed was correct. This is the fastest way to navigate the volume and a
  strong indirect argument against fabrication.
- **Dykes disagrees with Abū Ma'shar openly and often** — the ninth-parts, the derived domiciles,
  the quadruplicity profection rule, Book VII's delineations, the III.1 chart example. His
  disagreements are always signposted. **Do not mistake an editorial recommendation for
  doctrine**, which is the trap Intro §3 sets for item 4.
- **"Advancing" is dynamic, not whole-sign.** Intro §4 p. 29 defines it as angular or succedent
  **by quadrant division**, and **II.23, 3** makes the revolution's stakes the measure of power for
  natal planets too. This bears on `project_advancing_two_senses`: PN IV uses the Abū Ma'shar
  quadrant sense throughout, as expected.
- **Four of the five layout defects sit beside a figure.** If anyone reads Books V–VIII later,
  read the figure pages first.
