# §4 answered from *Persian Nativities* IV

Written 2026-09-10 from a read of PN IV pinned at blob `295eb22ad58ebc5ad0c330ede60e5f4b0159aee9`
(md5 `06a9b805b29d890525018ecf17fef755`, HEAD `c85fff8`), unchanged from the first line read to
the last.

This answers the six items of `04_timing_open_questions.md` §4, and gives a per-question
status for all 34 of its numbered questions. Every answer carries a citation
in the form `PN IV III.1, **12**` (Book, chapter, sentence) plus a page marker where it helps, so
the builder can re-check any reading against the page without re-reading the book. **Where a
reading is uncertain or declined, that is stated in the answer itself, not in a footnote.**

**Read this first.** Two of the numbers below were verified against the photograph because the
corpus or the printed book is wrong about them. They are flagged inline as **[ERRATUM]** and are
listed in full in `PN4_READTHROUGH_FINDINGS_2026-09-10.md`. Do not implement from the corpus text
alone at those two points.

---

## Item 1 — The revolution chart itself (Q19–Q22)

### Q19. How the revolution is cast, and whether its houses are read topically

**ANSWERED.**

The revolution is the moment the Sun returns to his natal zodiacal position, cast **for the
birth location**.

> "If the Sun was in some place of the circle in the root of the nativity, and then moved along
> in all of the signs until he came back to his position in which he was at the root, then he
> will have traversed 360° in 365 days (and a fraction), and a solar year will have been
> concluded for the nativity." — **I.2, 1** (p. 148)

> "And at the revolution of every year, one ought to derive its Ascendant and calculate the
> twelve houses of the circle according to it, and understand the positions of the planets for
> that time." — **I.2, 4** (p. 149)

**Location.** PN IV never states the location explicitly. Dykes uses the birth location and says
he sees "no evidence that Abū Ma'shar or other authors of his time used anything else", noting
that the "excess of revolution" technique presupposes a fixed location (Intro §2, p. 12). For
monthly revolutions the birthplace *is* stated: "(And we will use the birthplace for the
location)" — Intro §9, p. 95. **Assumption for the builder: birth location.** This is Dykes'
inference plus the MR statement, not an Abū Ma'shar sentence.

**Year length.** Abū Ma'shar endorses the Hipparchan tropical year of 365;14,48 days
(365.24667) for revolutions — **I.4, 31** and **IX.7, 10** ("365 1/4 minus 1/300 of a day"). He
uses the *mean* Sun for the nativity and then applies the tropical year to the revolution
(I.4, **23–31**); Dykes says plainly that this does not make sense (Intro §1, p. 6). A modern
implementation should use a true-Sun return; PN IV's own astronomy is not worth reproducing.

**Houses: both systems, together.** The chart-construction chapter is explicit that the twelve
signs are entered one per house *and* that quadrant cusps are computed:

> "Then, know the Ascendant of the year by its degree and minute, and write it down in one of
> those houses, then after that write down the twelve signs in succession, a sign in every
> house, calculating the houses by their degrees and minutes, in the way that you calculate the
> houses by the portions of hours and the ascensions of the right circle." — **I.6, 2** (p. 159)

Dykes' fn 31 reads the last clause as right ascensions, i.e. the twelve quadrant-based cusps.
So the revolution chart carries whole signs *and* division cusps. Intro §6 (pp. 49–60) is a long
treatment of how Abū Ma'shar handles the mismatch; **VII.1, 1–4** gives his two rules for
transits (two cusps on one sign → interpret by cusps and divisions only; intercepted sign →
interpret by the division only).

**Read topically: yes.** **I.7, 2** directs you to ask, of the revolution's Ascendant, "which
house it is in the root (of the houses of the circle, which are the stakes and what follows
them)". **II.23, 4** assigns topics to the revolution's own houses. **IX.9, 16–23** works
examples of combining a planet's house meanings across the root, the profection and the
revolution.

**What actually goes in the chart — the single most useful passage for a builder.**
**I.6, 3–8** (pp. 159–161) enumerates it:

| From | What is drawn |
|---|---|
| Revolution | the seven planets with condition, retrogradation; their rays; their twelfth-parts; the twelfth-parts of the house degrees; the Lots; Head and Tail (**3**) |
| Root | the seven planets, rays, twelfth-parts, Lots, Head and Tail, in their natal positions (**4**) |
| Root | the natal Ascendant; the **terminal point** profected from it, from the natal Lot of Fortune, **and from the rest of the indicators** (**5**) |
| Time lords | the **endpoint of the distribution**, the **distributor**, the **partner**, the ***fardār* lord**, the ***fardār* sub-lord**, and the **lord of the orb** (**6**) |
| Fixed stars | any on the natal Ascendant degree, the MC stake degree, with a luminary, or with a planet in the stakes (**7**) |

**I.6, 8** and Figure 52 (p. 162) total this at 154 points: 14 planets + Head and Tail in two
places each + 98 rays + 38 twelfth-parts, plus Lots. The arithmetic is self-checking
(116 + 38 = 154) and it holds.

Abū Ma'shar puts the **revolution in the inner wheel** and the nativity outside it (Dykes' fn 33
to Figure 51, p. 160); Dykes reverses this everywhere else in the book and says so.

**The reading checklist** is **I.7, 1–26** — twenty-six numbered things to examine, ending with
the comparison principle in Abū Ma'shar's own words:

> "its indication will be according to its place and condition in the two times together — the
> root and the revolution." — **I.7, 26** (p. 165)

### Q20. The relation of the revolution's Ascendant to the natal stakes

**ANSWERED.** It is the first question asked of the chart: **I.7, 2** (above). The reason is
given at **II.23, 3** (p. 269):

> "the power of the planets of the root and revolution is known from their positions in the
> revolution relative to the Ascendant of the year and its stakes, and the rest of its houses."

So the revolution's angularity governs the strength of **natal** planets too, not only
revolutionary ones. Named conditions where the two charts coincide are worked at
**II.23, 14–17, 20–41** and throughout **VI.3–VI.4**; the general rule for a natal planet
activated by the SR Ascendant falling on it is **VI.4, 3–8**, and the elicitation rule (the
activated planet should see its own natal place in the SR) is **VI.4, 29–30**.

### Q21. What "the lord of the year" is

**ANSWERED: the lord of the sign of the year, i.e. the profection lord — not the revolution
Ascendant's lord, and not a victor.**

> "In the revolution of years you ought to look at the Ascendant of the root, and for every year
> the native has completed, cast out one sign from it: the sign which the intended year reaches
> is the 'sign of the terminal point,' and its lord is the 'lord of the year' (and in Persian it
> is called the *sālkhudhāh*)." — **II.3, 1** (p. 185)

Three qualifications, all in the text:

1. **A planet *in* the sign of the year can displace the lord.** If the SR Ascendant falls on a
   sign holding a natal infortune (or fortune) **and** the year profects to that same sign,
   "then you should make that infortune be like the lord of the Ascendant or like the lord of
   the year, because it will be more powerful than them both" — **III.8, 15–16** (p. 340).
   Dykes thinks this overstates it (fn 205); recorded as stated.
2. **Luminary proxies.** When the Sun or Moon is lord of the year, Abū Ma'shar redirects most of
   the judgment onto other planets — **II.13, 1**; **II.14, 1**; **II.22, 1–5**:
   the distributor / the lord of the sign in which the distribution **from the longevity
   releaser** falls; the planet in Leo (resp. Cancer) in root or revolution; the planet the
   luminary hands over to while still in its sign; and the luminary's own place as a witness.
   If the Moon is void, use the lord of her house (**II.22, 4**).
3. **The Indian alternative**, which PN IV reports but does not adopt: the lord of the year is
   the lord of the **first ninth-part** of the sign of the terminal point, which restricts the
   lord of the year to four planets only — Mars, Venus, Saturn, the Moon (the lords of the
   convertible signs). **III.10, 1, 4–5** (pp. 361–362).

**"Governor" (Ar. mustawlī) is a separate term** and is the thing closest to a victor: the sign
(and lord) on which all or most of the year's indicators coincide — **IX.9, 10**; **IX.2, 4–7**.
The eight indicators that must coincide are listed at **IX.9, 1–9** (identical to the eight
"soul" indicators of **II.2, 10–18**):

lord of the year · distributor from the Ascendant · distributor from the longevity releaser ·
their partner by body and ray · *fardār* lord · lord of the orb · the planet receiving the
Moon's connection (or the lord of her house) · lord of the SR Ascendant.

### Q22. Whether revolutions of the month and day exist

**ANSWERED: months yes, and they are the subject of most of Book IX. Days and hours exist in
principle and Abū Ma'shar explicitly declines to use them.**

> "as for the second month, and the rest of the months which follow it, see when the Sun reaches
> the second sign from his rooted place, and, within it, comes to be in the like degree and
> minute which he was in at the root of the nativity: then derive the Ascendant for that time,
> and it is the Ascendant of the second month." — **IX.3, 2** (p. 575)

Same rule at **IX.1, 23–24** and Intro §9 p. 95. Cast for the birthplace. The SR itself *is* the
first month (**IX.1, 10**; **IX.2, 1–2**), which is why Book IX needs a separate rule for
distinguishing what belongs to the year from what belongs to month 1 (**IX.2, 3**).

> **[ERRATUM — do not follow the corpus here]** Intro §2 (p. 7) illustrates this with a natal Sun
> at 12° 22′ Gemini and then puts the monthly revolutions at 12° **23′** Cancer and 12° **23′**
> Leo. The page genuinely prints that (photo-verified); it is an error in Dykes' own book. It
> contradicts the rule stated in the same sentence, the worked example at Intro §9 p. 95
> (15° 29′ Scorpio → 15° 29′ Sagittarius → 15° 29′ Capricorn), and **IX.1, 23** and **IX.3, 2**,
> which both say "the like degree **and minute**". **Use the natal degree and minute unchanged in
> every sign.**

**Days and hours.** Abū Ma'shar defines them symbolically from the Sun's motion — 1° of the Sun's
travel is a "day of the Sun", 2′30″ is an "hour" (**I.3, 10–13**, repeated at **IX.7, 78**) — but
having laid out nine methods for managing days and hours he says a day-chart is unnecessary:

> "if we wanted the revolution of the days and hours, and we do derive their Ascendants and
> planets, we would work with them both in the way we described … but there is no need for us
> [to do] that, because these nine indicators … are complete for everything needed."
> — **IX.7, 79** (p. 644)

**Recommendation: implement SR and MR; do not implement day or hour charts.** They are declined
by the author.

---

## Item 2 — The single releaser/house-master procedure PN IV uses (Q1–Q9)

This is the item where PN IV gives the **most** on the frame and the **least** on the details, and
the split matters. Read the two halves separately.

### What PN IV does supply

**Q1. Which releaser, chosen how — ANSWERED as to the list; DECLINED as to the choice.**

The list is given twice, identically, in Abū Ma'shar's own words:

> "If you directed one of the releasers (I mean, **the Sun, Moon, Ascendant, Lot of Fortune, or
> the degree of the meeting or degree of the opposition**), then understand the distributing
> planet…" — **III.3, 1** (p. 316)

> "each of the five releasers is directed individually" — **III.1, 3** (p. 286)

and again at Intro §17 p. 140 fn 131 ("the other four are the Ascendant, the luminaries, and the
pre-natal lunation").

**This is decisive for the corpus disagreement.** PN IV's list is *Times* 4, **2–3**'s list —
Ascendant, the luminaries, Fortune, the prenatal syzygy — **without the lords**. It is **not**
Nawbakht's place-based day/night list of *Nat.* 1.15. So if the engine must pick one, PN IV
selects the five-candidate victor-style list, not the release-by-place list.

**But PN IV never says how to choose among the five.** It says only that all five are directed,
that one of them is the one "we rely on for information about the native's lifespan"
(**III.1, 4**), and that the distribution taken from *that* one is the strongest
(**III.3, 2**). The selection rule is presupposed, not stated. See "What PN IV declines" below.

**Q2. Is the eighth place in PN IV's list? — DECLINED, and the question does not arise.**
PN IV's releaser list is a list of *points*, not of *places*. No place-list of any kind appears.
Nothing in PN IV bears on Nawbakht's eighth place.

**Q3. The Ascendant fallback — DECLINED.** No fallback chain appears. PN IV assumes the releaser
is already identified.

**Q4. What "in a stake or what follows a stake" means for the Moon — DECLINED for the releaser
context.** PN IV does not use that phrase to qualify a releaser. It does use the
stake/succedent/cadent distinction constantly for planetary strength, and it is explicit that
this is the **dynamic quadrant** sense, not whole sign: Intro §4 p. 29 defines "advancing"
(Ar.) as angular or succedent *by quadrant division*, and **II.23, 3** makes the revolution's
stakes the measure. That is evidence about PN IV's general usage, not about *Nat.* 1.15's rule.

**Q9. The "mighty years" — DECLINED.** PN IV never grants a planet's mighty/greatest years to a
nativity. Its only use of the greater/middle/lesser years in a longevity context is
**IX.8, 13**, where the native's *age* matching the house-master's greater, middle or lesser
years — or one-third, one-half or two-thirds of one of them — marks a candidate cutting year.
That is a *timing* use, not a grant.

### The procedure PN IV does give — and it is a clean one

The whole method is a special case of distributions. Dykes states this (Intro §16, p. 136) and
Abū Ma'shar's own text bears it out. Figure 50 (p. 138) is Dykes' equivalence table:

| Longevity term | Distribution term |
|---|---|
| Releasing | Distributing |
| Releaser | the point distributed |
| House-master ("indicator of the lifespan", Ar. *dalīl al-ʿumr*) | distributor of the releaser's **natal** position |
| Increaser / decreaser | planets connecting with the distributor |
| Cutter / killer | the **partner** |

**The house-master is normally the bound lord of the releaser** — which is exactly the
distributor of the releaser's natal position (Intro §16, p. 136). Abū Ma'shar's own procedure:

> "the operative foundation in that is that you look at the indicator of the lifespan in the root
> of the nativity, [to see] how many years it grants. **5** So if it has increasers and decreasers
> there, you will make an increase to it due to the increasers, and make a decrease from it due
> to the decreasers; and you make what happens to the indicator of the lifespan after that (in
> terms of years, months, days, and hours), be like **the foundation of the man's lifespan**."
> — **IX.8, 4–5** (p. 646)

Then the test (**IX.8, 8–9**, p. 647): direct the releasers in the root **a year for each
degree**, *and* turn them in the signs **a year for each sign**, *and* read the revolutions. If a
releaser reaches a cutter by direction or by profection at a time matching the foundation years,
or if the infortunes govern that revolution, it is a cutting year.

**The gate — the single most important rule for the builder.** A bad distribution far from the
foundation years is *not* death:

> "everything we have mentioned … about the death of the owner of the revolution … is [only] if
> those years matched the years of the lifespan which his [longevity] indicator in the root [had
> already] pointed out (or if they were close to them) … So if the year was in a condition
> indicating destruction, and that was not the time in which the years of the planets judged
> [it] … then he will have a disaster in it which can be gotten over."
> — **III.2, 110–111** (p. 316); restated **IX.8, 120–122** (p. 665)

**A rule that surprised me and matters for implementation:**

> "the indicator of the lifespan alone is turned in the signs, sign-by-sign, and is **not**
> directed degree-by-degree." — **IX.8, 32** (p. 651)

So the **house-master is profected, not directed**. (Dykes independently doubts the practice of
distributing the house-master, Intro §16 fn 129; Abū Ma'shar's sentence settles it.)

**Modulation by the strength of the house-master (IX.8, 10–13):** if the house-master and its
increasers are strong, the cutting disaster falls at or after the foundation years; if weak, it
falls *before* them, unless the intervening years are clean.

**The cutters — a complete, implementable enumeration.** **IX.8, 14–18** gives four ways of
cutting, and the chapter then works each:

1. **The stars — nineteen cutters** (**IX.8, 19–55**, Figure 137 p. 652). Five fast-moving:
   Saturn and Mars cut *by nature*; the Sun and Moon *by contingency*; Mercury *by mixture*.
   Then seven fixed stars and seven nebulae/clusters.
   - Saturn and Mars cut from **body, opposition, square, trine or sextile**, right or left
     (**21**) — i.e. every aspect.
   - The Sun cuts from **body, opposition or square** (**22**); from trine/sextile only a
     powerful disaster, and only when he is himself afflicted by Mars or Saturn.
   - The Moon cuts from **body, opposition or square** (**23**); if she is well-fortified natally
     she may not kill. **If the Ascendant is the releaser the Moon cuts with her body regardless
     of her condition** (**25**).
   - The luminaries cut *themselves* from the square (**26**).
   - Mercury kills only when besieged by the infortunes with no fortune looking (**27–28**).
   - Reached **by profection** rather than direction, only body/opposition/square kill; trine and
     sextile are "a weak testimony" (**30–31**).
   - **Star positions are for AD 820** ("the year 1150 of Alexander") and precess at **1° per
     100 years** (**IX.8, 51**). Latitude matters: a star kills when the releaser meets it *and*
     they agree in inclination/latitude; if one is north and the other south, disaster but not
     death (**54–55**).
2. **Ten positions** (**IX.8, 56–70**): the Head; the Tail; the degree of the prenatal
   conjunction; the degree of the prenatal opposition; the degree of the Descendant — these five
   kill on direction, and by profection indicate a cutting-like disaster that kills with
   corroboration (**62–63**). Then: the natal Ascendant (especially with the Moon as releaser,
   **64–66**); **the direction running out at the end of a sign and crossing into the next**
   (**67**); the two places where Sun and Moon were in square before birth (**68**); a shift from
   a fortune's bound to an infortune's (**69**); and from an infortune's bound to an
   infortune's (**70**).
3. **Five distribution transitions** (**IX.8, 71–78**), keyed one-to-one to III.2's transition
   list, plus: "if the direction of one of the releasers reached the beginning of the bound in
   which Mars is: for that kills" (**78**).
4. **Corruption of the year** (**IX.8, 79–118**) — some forty named revolution configurations,
   each cross-referenced to its home passage in II.3, II.23, III.2, III.8, IV, V and VI.

**IX.8, 112–113** grades them: the *cutters* are "clear [and] not in doubt", but the
"fear of death" configurations are individually weak — **two or more must occur together**, and
"the lord of the *fardār* is powerful in indication in this topic."

### What PN IV declines — state this to the builder plainly

**Q5, Q6, Q7, Q8 — NOT DETERMINABLE FROM PN IV.**

PN IV does not give the house-master's candidate ranking, does not say where each grade of years
is granted, does not quantify the increasers and decreasers, and does not adjudicate a planet
that passes one test and fails another. It presupposes all of it. Abū Ma'shar says so himself:

> "there is great difficulty and much confusion in deriving the years of the indicator of the
> lifespan which is like the root: and generally for those who are called to this knowledge,
> those who look into it are wandering around in the dark; but a statement of the truth of that,
> and its correctness, is found in **the book which we worked on concerning nativities**."
> — **IX.8, 123** (p. 665)

Dykes' own reading table for Longevity (Intro §16, p. 139) points the reader to *Sahl,
Nativities* 1.15–1.16 for the releaser, **1.20 for the house-master and its years**, and 1.21 for
increasers and decreasers. That is an editor's cross-reference, not PN IV doctrine.

**Consequence for the engine: PN IV cannot adjudicate *Nat.* 1.20, 10–13 against *Times* 4, 7
(disagreement #2). It is silent, and its silence is the answer.** The book that was supposed to
settle where the greater years are granted does not address the question. Disagreement #2 should
stay open, and the checklist's instruction not to resolve it stands.

---

## Item 3 — The distributor's rules (Q10–Q14)

### Q10. Which ascensions — **ANSWERED, and this is the sharpest result in the whole read.**

> "the Ascendant and the things in it are directed by degrees of ascensions of the **country in
> which the native was born**, while what is in the **Midheaven or the fourth** is directed by
> the ascensions of the **right sphere**, and what is not in these three positions is directed
> according to what we stated in our book [on that topic]."
> — **III.1, 12** (p. 288)

Dykes' fn 16 identifies the third case as Ptolemy's method: **proportional semi-arcs**. So:

| Point directed | Measure |
|---|---|
| Ascendant (and things in it) | **oblique ascensions of the birth latitude** |
| Midheaven / IC | **right ascensions** |
| everything else | **proportional semi-arcs** |

The checklist's Q10 asked whether it was oblique throughout *or* right ascension near the
meridian. The answer is **both, selected by position, with semi-arcs for the remainder** — a
three-case rule, not a two-case one.

**The simple proportional shortcut Abū Ma'shar actually works with** is at **III.1, 7–9**: take
the zodiacal degrees remaining of the bound, multiply by the ascension of the sign, divide by 30.
That is the older sign-ascension method; **III.1, 12** is his correction of it, and fn 13 says so.

**The rates** — **III.1, 13** (p. 288):

| Arc | Time |
|---|---|
| 1° | 1 year |
| 5′ | 1 month |
| 1′ | 6 days |
| 10″ | 1 day |
| **25‴** | **1 hour** |

These match *Nat.* 1.18, **21** exactly and extend it by one place. The year is idealised at
360 days = twelve 30-day months (fn 17).

> **[ERRATUM — the corpus is wrong here, the printed book is right]** The corpus reads
> `every 25" one hour` — 25 **seconds**. The page prints **25‴**, twenty-five **thirds**
> (photo-verified, p. 288). The arithmetic settles it independently: 10″ = 1 day = 24 hours, so
> 1 hour = 10″/24 = 0.4167″ = 25‴ exactly. The corpus reading makes an "hour" two and a half
> days long. **Implement 25‴ = 1/60 of a second of arc.** No triple-prime survives anywhere in
> the corpus; elsewhere the volume writes thirds as a doubled double-prime (`7' 25" 33""`,
> IX.7, **62**).

**Zodiacal 1°/year is named by Abū Ma'shar himself as an inferior approximation**, which bears
directly on the engine's current labelled shortcut:

> "there is an approximation in it, but the correct [approach] is that this way of directing is
> like the direction of the Sun every day … except that directing in this work is complicated,
> and between this sense which is by approximation and the exact one, the second one is easy,
> [with] no harm in the work." — **IX.7, 32** (p. 636)

Dykes' fn 180: not really true, because ascensions and zodiacal degrees diverge sharply as birth
latitude increases. **The engine's existing label — ascensional named as the real method,
zodiacal implemented as a shortcut — is exactly right and is now backed by a citation.**

### Q11. What counts as "reaching" — **ANSWERED.**

The **partner** is "the most recent planet which the releaser has encountered **by body or ray**"
(Intro §7 p. 65 vocabulary), and Abū Ma'shar's own statement:

> "when the direction reaches one of those, the direction of the distribution will be in the
> 'management' of what is there, from that position until it encounters another planet by its
> body or rays, so that the management will shift from the body or rays of the first planet, to
> the body or rays of the other planet." — **III.1, 15–16** (p. 288)

So: **body and rays both, with no orb — the ray is a point.** The partner persists until the next
body or ray is met, so there is always exactly one partner. This settles Q11 in favour of the
*no-orb* reading (VII.5 fn 146 in the *Gr. Intr.*), and against any orb-based partner rule.

**Ranking of aspects as partners** — **III.2, 104** (p. 315):

> "the strongest of the rays is the **opposition**, and after that the **square**, then the
> **trine**, and the weakest of them is the **sextile**."

with the body ahead of all of them (**III.2, 103**: "the strongest of the three indicators is the
lord of the distribution, and the one below it in power is the one managing for it **by body**;
but as for the lord of the **ray**, it is lower than both of them"). Note the order is
**body > opposition > square > trine > sextile** — *hard aspects rank above soft ones as
partners*, which is the reverse of the usual benefic/malefic intuition and is easy to get wrong.

**At birth**, when the releaser is not exactly on a body or ray, use the most recent partner
going backwards in the same sign; if there is none between the start of the sign and the
Ascendant's degree, the distributor acts alone (**III.1, 23–25**).

**The distributor needs no aspect:** "the lord of that bound is the 'distributor,' **whether it
looked at [the bound] or not**" — **III.1, 11**.

### Q12. "An infortune corrupts four signs" — **DECLINED. Not in PN IV.**

PN IV contains no rule of that shape. The nearest things are **III.2, 55–101** (the 24
bound-to-bound and partner-to-partner transitions) and **IX.8, 69–70**, neither of which counts
signs. *Nat.* 1.23, **37** is unaddressed by PN IV; leave it open.

### Q13. Which points are distributed — **ANSWERED, and the answer is "many, simultaneously."**

> "Now, each of the five releasers is directed individually. **4** As for the one which we rely on
> for information about the native's lifespan, we direct [it] for the conditions of survival,
> illness, and death; but as for the rest of the releasers, we direct [them] for the knowledge of
> health and emaciation, and disasters, and the rest of the different conditions which each of
> them indicates. **5** And all of the planets and Lots are [also] directed, as well as the
> twelfth-parts and the twelve houses, in the root of the nativity, the revolutions of years, and
> the revolutions of months." — **III.1, 3–5** (pp. 286–287)

Three consequences the builder must not miss:

1. **Two distributions run in parallel at minimum.** **II.2, 6–7** lists as separate body
   indicators "the bound which the distribution has reached, **from the Ascendant**" and "the
   bound which the distribution has reached, **from the [longevity] releaser**"; **II.2, 12–13**
   and **IX.9, 3–4** list their two distributors separately. These are different points moving at
   different rates.
2. **Every point is directed from its own natal position, starting at birth** — Intro §7 p. 73,
   principle (3), and **III.1, 47**: "as for the Lots and the twelfth-parts … they are directed
   from their positions which they are in, until the end of the lifespan." Dykes uses this to
   show that the book's own worked example (III.1, **19–45**) violates the method and should be
   ignored; see Item 3 note below.
3. **The SR Ascendant is separately distributed around the SR chart for exactly one year** —
   **IX.7, 29–33** and **III.1, 3–6**, at **59′08″ per day** (the Sun's mean daily motion). This
   is a *second, independent* distribution operating inside the year.

### Q14. How the distributor's own condition modifies the period — **ANSWERED.**

- Root beats revolution: "its condition's indication for good or evil in the root is more
  powerful than its condition's indication in the revolution" — **III.2, 22**, repeated **29**.
- Revolutionary planets transiting in, or casting rays into, the bound of the distribution modify
  it *incidentally* — **III.2, 38, 43, 46–47, 54**; fortunes with the distributor or partner in
  the SR alleviate — **III.8, 7**.
- A full nine-point checklist for analysing any distribution is **III.2, 4–9**.
- Seven "static" distributor/partner types: **III.2, 10–54** (Figure 66).
- Twenty-four transitions with twelve interpretations: **III.2, 55–101** (Figures 68–73).

**Note on the book's worked example.** **III.1, 19–45** is a chart example that Dykes judges
"corrupted and ought to be ignored" (Intro §7, pp. 73–75): the data in **19** and **22** are
mutually inconsistent, and the example accumulates Lots as though each becomes a releaser from
the moment it is met, contradicting **III.1, 47** and principle (3). **Do not use it as a test
fixture.** Use Appendix A's two worked distributions instead (Figures 140–141, pp. 672–673),
which are Dykes' own and internally consistent.

**Ascension tables.** The checklist noted these are not in the corpus. **They exist in PN IV, at
pp. 675–677 — "APPENDIX B: TABLE OF ASCENSIONAL TIMES" — which is inside the volume but outside
the OCR'd range** (coverage stops at p. 674 by decision). They are computable anyway; Appendix A
pp. 671–674 gives a method that needs no table at all:

> the sphere rotates 1° per 4 minutes of clock time, and 1° of the equator is 1 year — so
> **age = (minutes of elapsed clock time) / 4**, and conversely **clock offset = age × 4
> minutes**. Animate the chart to that time and read the bound and the partner.

That is exact, latitude-correct, and trivially implementable from any ephemeris; it is
recommended over transcribing Appendix B.

---

## Item 4 — Profection scope and the lord of the year (Q15–Q18)

### Q15. What is profected — **ANSWERED: everything.**

> "Everything may be profected. **2.** All profections are sign-by-sign. **3.** Months are
> measured from the date of the SR and the MRs, not by calendar months. **4.** The sign of the
> profection in an annual chart (the nativity or the SR) is also the first month."
> — Dykes' summary of the rules, Intro §9 p. 90, from **IX.1**

In Abū Ma'shar's own words the profected points that matter are the **seven monthly indicators**,
**IX.1, 9–25** and **35–39** (Figures 34 and 100):

| | Indicator | Rooted? |
|---|---|---|
| #1 | profected natal Ascendant | rooted |
| #2 | ninth-part of the sign of the year | rooted |
| #3 | profected natal Lot of Fortune | rooted |
| #4 | SR Ascendant | rooted |
| #5 | SR Lot of Fortune | rooted |
| #6 | Ascendants of the monthly revolutions | not rooted |
| #7 | Lots of Fortune of the monthly revolutions | not rooted |

"Rooted" is defined at **IX.1, 37**: their position depends on a chart cast from the natal Sun.
They decrease in universality in that order (**IX.1, 39**).

**Profected houses exist too**: each house profects from the sign of the year, so there is a
profected second, third and so on, each with its own lord (Intro §5 pp. 38–39, from
**VI.2, 1–20**). Dykes says he mostly ignores them and I would too, but they are Abū Ma'shar's.

Also profected: **I.6, 5** puts into the revolution chart the terminal point taken from the natal
Ascendant, from the natal Lot of Fortune, "and from the rest of the indicators".

### Q16. Monthly profections — **ANSWERED, including a rule the corpus had no hint of.**

The sign of the year **is** month 1; month 2 is the next sign, and so on, measured from the SR/MR
dates rather than the calendar (Intro §9 p. 90; **IX.1, 9–10**).

**But Abū Ma'shar has a quadruplicity rule that reverses the direction of monthly profection**
— **IX.1, 26–34** (pp. 558–560, Figure 103):

| Sign of the year | Direction of monthly profection |
|---|---|
| fixed | forward |
| convertible | **backwards** |
| double-bodied, 0°–15° | forward |
| double-bodied, 15°–30° | **backwards** |

with the reason at **IX.1, 30**: the first half of a common sign is of the nature of the preceding
fixed sign, the second half of the following convertible sign. It applies to indicators #1, #3,
#4 and #5 — **not** to #2, the ninth-part, which always runs forward (**IX.1, 32**). It applies to
the "quick methods" 2 and 3 as well (**IX.5, 124**).

**Flag for the builder.** Dykes rejects this rule as "complicated, probably wrong, and an
over-zealous application of quadruplicities" and does not use it (Intro §9 p. 102 and fn 95). It
is nonetheless Abū Ma'shar's, and it is alluded to by Māshā'allāh in *Nat.* 1.23, **36** in the
context of converse directions. **This is a decision the owner should take, not the implementer:**
either implement PN IV as written, or follow Dykes. Recorded, not resolved.

**Three rejected alternatives** — **IX.1, 40–45**: (a) a Lot-of-Fortune-style monthly lot
measured from the monthly Sun to the natal Moon and projected from the natal Ascendant (this is
Dorotheus, *Carmen* IV.1, **46–55**); (b) Ptolemy's 28-days-per-sign method; (c) a 30½-day solar
month. Abū Ma'shar rejects all three. **He also explicitly rejects Ptolemy's Moon-based monthly
profections** (Intro §3 p. 24, citing **IX.1, 42, 44**).

### Q17. How the lord of the year is judged, and its precedence over the distributor

**ANSWERED — and this resolves corpus disagreement #1.**

*Judged by both charts.* **II.3, 5–8** (Figure 55, p. 188) gives the four-way comparison —
good/good, good/bad, bad/good, bad/bad in root and revolution — and **II.3, 9–19** adds place and
reception. This is the same table Dykes reproduces as Figure 8 at p. 18.

*Precedence.* Abū Ma'shar ranks the **nineteen indicators of the year** at **II.1, 5–24** and then
says:

> "So these are the indicators of the revolution of the years of nativities, and **each one in
> turn is stronger in indication than the one which is after it**: so one ought to compose their
> indications in this order, treatise after treatise." — **II.1, 25** (p. 181)

The first four are: **(1) the sign of the terminal point and its lord; (2) the distribution and
the distributor; (3) the partner; (4) the *fardār* lord and its sub-lord.** So *within a given
year*, the profection outranks the distribution. Restated at **II.23, 1**: "After the sign of the
terminal point, the power of the indication belongs to the distributor."

But **III.2, 2–3** compares them on a different axis:

> "They [the distributors and partners] are **stronger in the indication of rooted matters** than
> the lord of the terminal point is, because the indication of the lord of the terminal point is
> only over the condition of **that year**: but as for the lord of the distribution, sometimes its
> indication for good or evil is for **several years** … **3** But in addition to that, in every
> year one must call upon the sign of the terminal point and the lord of the year, and the
> Ascendant of the revolution of the year and its lord, and the Moon … **as witnesses** to that
> condition."

**The two statements are not in conflict; they are indexed to different scopes.** The lord of the
year ranks first *among the indicators of a single year*. The distribution is stronger *for
activating rooted matters across several years*, and the year's indicators are read as witnesses
to it. **PN IV does not contradict itself here.**

This is precisely the shape of *Nat.* 1.23, **33** (distributor stronger) versus 1.24, **2**
(turning stronger), which fn 245 guessed should read "stronger when combined with the
distributor". PN IV supplies the real reconciliation: **scope, not combination.**

> **Correction to a secondary source.** Dykes' Introduction §3 (p. 21, point 3) states the
> opposite — "even among time lord systems, distributions tend to be more powerful than
> profections" — and cites no Abū Ma'shar sentence for it; it is his own editorial judgement, and
> his fn 321 concedes Abū Ma'shar's ordering. **The builder must use II.1, 25, not Intro §3.**

*General hierarchy*, for what it is worth: Intro §3 p. 21 gives natal > time lords > revolutions,
and Abū Ma'shar's own **III.2, 22** and **29** confirm root over revolution. **VI.3, 1–5** says an
SR "resembles" a profection but the profection is "more powerful".

### Q18. "The Ascendant of the year" — **ANSWERED. PN IV's vocabulary is unambiguous.**

From the vocabulary list at Intro §8, p. 77:

- **"Ascendant of the year"** (Ar. *ṭāliʿ al-sana*) = **the Ascendant of a solar revolution.**
- **"Sign of the year" / "sign of the terminal point"** = **the profected sign.**
- **"Lord of the year"** = lord of the *sign* of the year, i.e. the profection lord.

The two are named separately and used separately throughout — e.g. **II.23** is titled "On the
indication of the Ascendant of the revolution & its lord, & their partnership with the terminal
point & the lord of the year", and **III.8, 15** distinguishes the case where the SR Ascendant and
the sign of the year fall on the *same* sign as a special reinforcing condition.

**So for PN IV, disagreement #11 does not arise: the terms are distinct and consistently used.**
This does not resolve the disagreement *in Sahl*, where the same English phrase renders both;
it means PN IV cannot be cited on either side, and the engine should keep the two concepts under
separate names internally, as PN IV does.

---

## Item 5 — The *fardār* sequence (Q27–Q29)

**FULLY ANSWERED.** This is the item where the corpus had nothing at all, and PN IV supplies a
complete, checksummed system.

### Q27. Order by sect, and the Nodes

> "The *fardār* of the Sun is 10 years, the *fardār* of Venus 8 years, the *fardār* of Mercury 13
> years, the *fardār* of the Moon 9 years, the *fardār* of Saturn 11 years, the *fardār* of
> Jupiter 12 years, the *fardār* of Mars 7 years, the *fardār* of the Head 3 years, and the
> *fardār* of the Tail 2 years: the amount of all of that is 75 years."
> — **IV.1, 2** (p. 364)

> "as for nativities of the day, from when the native is first born one begins the distribution
> of the years of their *fardār* from the Sun … then after that are the years of Venus, then the
> years of Mercury, the Moon, and the years of Saturn, **according to the succession of their
> spheres**. **4** But as for nativities of the night, one begins … with the Moon, then Saturn,
> Jupiter, [and] Mars, according to the first arrangement." — **IV.1, 3–4**

The order is **descending Chaldean**, starting from the sect light and wrapping:

| | Diurnal | | Nocturnal | |
|---|---|---|---|---|
| 1 | Sun | 10 | Moon | 9 |
| 2 | Venus | 8 | Saturn | 11 |
| 3 | Mercury | 13 | Jupiter | 12 |
| 4 | Moon | 9 | Mars | 7 |
| 5 | Saturn | 11 | Sun | 10 |
| 6 | Jupiter | 12 | Venus | 8 |
| 7 | Mars | 7 | Mercury | 13 |
| 8 | Head | 3 | Head | 3 |
| 9 | Tail | 2 | Tail | 2 |
| | **75** | | **75** | |

Both columns check to 75, matching *Gr. Intr.* VII.8, **3** and Figure 146 cell for cell.

> **[ERRATUM — the corpus is wrong here]** This is PN IV's **Figure 43** (p. 116), and the corpus
> has **dropped 15 of its 18 planet glyphs**, retaining only diurnal Sun, diurnal Venus and
> nocturnal Sun. The years column is intact and correct. The table above is the **photo-verified
> printed reading** (PN4_p0116.jpg). Do not build from the corpus cell contents.

**The Nodes always come last, in both sects** — this is the point the medieval tradition got
wrong, and Abū Ma'shar is explicit:

> "the Head and Tail distribute for diurnal nativities after the years of Mars, and for nocturnal
> nativities after the years of Mercury: and it is when the native enters year 71 — and he will
> begin in the distribution of the *fardārs* with the Head, then the Tail, **whether the native
> was diurnal or nocturnal**." — **IV.7, 24** (p. 393)

Dykes traces the contrary medieval view (Head/Tail always after Mars, hence Ages 39–43 in a
nocturnal chart) to al-Qabīsī IV.21 being unclear, and notes that the *Gr. Intr.* lists only the
diurnal years (Intro §12, pp. 116–117).

**After 75 years the cycle restarts at the sect light**, not always at the Sun:

> "once 75 years are completed for the native, the distribution of the *fardār* returns to **the
> luminary which he began from at his birth**, in the original order." — **IV.7, 25**

(**IV.1, 2**'s "then it returns to the Sun" is the diurnal case of that rule.) And **IV.7, 26**:
if the lifespan falls short of 75, "his death will be in the *fardār* of the planet which did
reach" — the same form as **I.8, 30** for the Ages of Man.

> **A contradiction inside PN IV, recorded and not resolved.** **I.8, 35** says the *fardār* years
> and order follow "the succession of their **exaltations** in the signs". They do not — the
> sequence in Book IV is descending Chaldean, and the exaltation order (Sun-Aries, Moon-Taurus,
> Jupiter-Cancer, Mercury-Virgo, Saturn-Libra, Venus-Pisces) does not reproduce it. Dykes' fn 70
> says this may hold for Abū Ma'shar's *mundane fardārs* but not the natal ones. **Build from
> Book IV; note I.8, 35 as an internal inconsistency.**

### Q28. Sub-periods

> "when any of them manages the years of its *fardār*, it stands alone in [its] indication at
> first, for an amount of **one-seventh** of its years, then after that the rest of the planets
> partner in the indication … also in the amount of one-seventh of it. **6** And so the beginning
> [of those sub-periods] will be from the planet which has the *fardār*, and the one which
> partners with it the first time is **the planet which is below it in the celestial circle**,
> and the one which partners with it the second time is the planet which is below that, in
> succession." — **IV.1, 5–6** (p. 364)

So each period divides into **seven equal parts**, running in the same descending-Chaldean order
from the *fardār* lord itself. The Sun's ten years run Sun-Sun, Sun-Venus, Sun-Mercury, Sun-Moon,
Sun-Saturn, Sun-Jupiter, Sun-Mars (worked out sentence by sentence at **IV.1, 11–36**).

**The Nodes have no sub-periods:**

> "as for the Head and the Tail, they stand alone in the management of their years … and they do
> **not** partner with the planets (nor do [the planets] partner with them), **because they do not
> have houses**." — **IV.1, 8**

Sub-period length is simply *years ÷ 7* (Sun: 10/7 = 1.42857 y = "1 year, 5 months, 4 days, and
approximately 6 hours", **IV.1, 11**). **Caution:** Abū Ma'shar's months are idealised 30-day
months, so converting his stated day-counts to real dates needs care (Intro §12, p. 119). A full
sub-period table is at the end of **IV.1**.

### Q29. Judged from the nativity or from each revolution — **BOTH.**

> "the natal meanings of the time lords are activated according to their condition, place, and
> rulerships. These natal indications are then compared with their real-time conditions at the
> time **when they take over the management**." — Intro §12, p. 120

Abū Ma'shar's own version: **IV.7, 27–28** — the stated indications are the planets' *natural*
indications, but "the suitability of each one's condition (or its badness) **in the root and at
the time of the management**, alters much of what we have stated". For a major *fardār* lord the
handover falls at an SR; for sub-lords it falls at arbitrary times that must be computed.
When a *fardār* lord is **also** the lord of the year by profection, the indication intensifies
(**IV.2, 24–25**; **IV.7, 27–28**).

---

## Item 6 — The time-unit keys (Q33, disagreements #5–6)

### Q33 and the unit key — **ANSWERED, and the answer is none of the three rival triggers.**

PN IV keys the unit of directed motion to **the level of the chart**, not to sign type, planetary
strength, or quadruplicity:

> "And you make the degrees of direction **in the root of the nativity be years**, but **in the
> revolutions of years months and days**, and **in the revolutions of months days and hours**."
> — **III.1, 6** (p. 287)

That is a clean, implementable rule, and it is orthogonal to corpus disagreement #5 (*Times* 2,
2–4 by sign type; *Times* 11, 24 by strength; *Times* 11, 16 by quadruplicity; 2.7, 7 by sign
gender; Aph. #13 by planetary speed). **PN IV does not adjudicate disagreement #5 — it answers a
different question, and it answers it unambiguously.** Disagreement #5 stays open; PN IV should
not be cited on any side of it.

Likewise **disagreement #6** (unit by planet — *Times* 7, 6; *Nat.* 4.3, 16–17): PN IV has no
per-planet unit rule. **DECLINED.**

**The complete PN IV rate ladder**, from **III.1, 13** with the erratum applied:

```
1°   = 1 year        (of ascensions, per III.1, 12)
5′   = 1 month
1′   = 6 days
10″  = 1 day
25‴  = 1 hour
```

with an idealised 360-day year of twelve 30-day months.

**Other timing keys PN IV supplies, all citable:**

| Key | Rate | Citation |
|---|---|---|
| profection, annual | 1 sign per year | **II.3, 1**; **I.2, 5** |
| profection, monthly | 1 sign per month from the sign of the year | **IX.1, 9–10** |
| SR Ascendant distributed round the SR | **59′08″ per day**, one full circuit per year | **IX.7, 29–31** ("the small days") |
| profected 30° increment treated as a year | 12 d 4 h 10 m 30 s per degree | **IX.7, 23–28** ("the mighty days") |
| Ages of Man | fixed planetary spans, see below | **I.8, 10–26** |
| *fardār* | see Item 5 | **IV.1, 2** |
| Moon's connections dividing the year | see below | **II.22, 2–3** |
| planetary "weeks" and days | nine methods | **IX.7, 1–72** |

Two of these are worth calling out because nothing in the corpus hinted at them:

- **II.22, 2–3**: if the Moon connects with two planets while still in her sign, **the year
  divides into halves**; with three, into thirds; with more, by their number — each portion
  judged by the condition of the planet owning it.
- **IX.7, 56**: every hour-level management in the book is in **equal** hours, not unequal
  planetary hours. (The *planetary* hours are used only for the lord of the orb, **VI.1**.)

### Q30 — Ages of life — **ANSWERED (asked in §2H, answered here because it is a unit key).**

PN IV uses **Ptolemy's seven ages**, ordered by planetary sphere from lowest to highest, not the
quadrant scheme of *Nat.* 3.9, **32–36**. **I.8, 10–26**, Figure 53 (p. 169):

| Planet | Years | Ages |
|---|---|---|
| Moon | 4 | 0–3 |
| Mercury | 10 | 4–13 |
| Venus | 8 | 14–21 |
| Sun | 19 | 22–40 |
| Mars | 15 | 41–55 |
| Jupiter | 12 | 56–67 |
| Saturn | 30 | 68–97 |

Derivation (**I.8, 9**): each span is a planet's lesser years, or one-half or one-tenth of its
lesser or middle years. Moon 4 = one-tenth of her middle years (**I.8, 12**) and matches the four
elements; Mercury 10 = half his lesser years (20); Venus 8, Sun 19, Mars 15, Jupiter 12,
Saturn 30 are lesser years outright. All seven check.

**Abū Ma'shar explicitly refuses to subdivide the Ages into sevenths the way the *fardārs* are
subdivided** — **I.8, 34–37**: "his years are not divided among the seven planets, but he will be
in the nature of the planet itself, for the amount of those years." Some hold that after Saturn's
thirty the cycle restarts at the Moon (**I.8, 31–33**), reported without endorsement.

> **A witness for a settled question, noted in passing.** **I.8, 12** gives the **Moon's middle
> years as 39½**, with Dykes' fn 54 noting "others sometimes say 66½". 39.5 = (25 + 108/2)/2, the
> luminary construction; 66.5 = (25 + 108)/2, the ordinary mean. This is an independent
> confirming witness for the reading already settled in `project_contested_table_readings`.

### Q31, Q32, Q34 — **DECLINED.**

- **Q31 (Valens's Fortune-years, 1.37 vs 6.5):** PN IV uses neither table and does not mention
  the method. Disagreement #4 is untouched.
- **Q32 (ascensions and periods, *Nat.* 2.22 [4]):** the closest thing in PN IV is
  **III.7, 32–42** with Figure 75 (p. 336), where a planet is activated at ages equal to its
  planetary years, or the ascensional times of its sign, or their sum, or ⅓/½/⅔ of that sum —
  and Abū Ma'shar's contribution is that the effect is more certain if the planet is *also* a
  time lord then. The same age-matching idea reappears at **IX.8, 13**. That is a *relative* of
  the Valens method, not the method itself; I would not call Q32 answered.
- **Q34 (meeting/opposition nativities, 8.7):** absent from PN IV. The prenatal syzygy appears
  only as a **releaser** (**III.3, 1**) and as a **cutting position** (**IX.8, 59–60**), never as
  a death-timing rule of the *Nat.* 8.7 kind.

---

## Two further items the checklist did not ask for, which the builder needs

**A. Egyptian bounds, Aquarius.** Figure 23 (p. 65) prints the Egyptian bounds table, and
**Aquarius is Mercury-first** (☿ 0°–6°59′, ♀ 7°–12°59′, ♃ 13°–19°59′, ♂ 20°–24°59′,
♄ 25°–29°59′). This is a further independent witness for the reading settled in
`project_contested_table_readings`, and it agrees with `EGYPTIAN_TERMS` in `app.py`.

**B. Aspects are used by degree, with the ray as a point.** Rays are cast "from the seven
directions" (**I.7, 12**, and Dykes' fn 42: "by degree-based aspects or connections"), and the
partner is whatever body or ray the direction meets. There is no orb on a ray in the distribution
machinery. Orbs *are* used elsewhere — Figure 83 (p. 397) is a table of "Persian planetary orbs
(on each side)" for judging the intensity of transits, and **V.1, 1–7** grades the "completeness"
of a planetary return by whether the returning planet is in the same bound, within half its orb,
in the same sign applying, or in the same sign separating. **Do not carry transit orbs into
distributions.**

---

## Summary table — all 35 questions

| Q | Status | Where answered |
|---|---|---|
| 1 | **Answered** (list); declined (choice) | III.3, **1**; III.1, **3–4** |
| 2 | Declined — question does not arise | — |
| 3 | Declined | — |
| 4 | Declined for the releaser; general usage evidenced | Intro §4 p. 29; II.23, **3** |
| 5 | **Not determinable from PN IV** | IX.8, **123** |
| 6 | **Not determinable from PN IV** | IX.8, **123** |
| 7 | **Not determinable from PN IV** | IX.8, **4–5** names them only |
| 8 | **Not determinable from PN IV** | — |
| 9 | Declined; related timing rule found | IX.8, **13** |
| 10 | **Answered** — three-case rule | III.1, **12** |
| 11 | **Answered** — body or ray, no orb | III.1, **15–16**; III.2, **103–04** |
| 12 | Declined — absent from PN IV | — |
| 13 | **Answered** — five releasers + all planets, Lots, twelfth-parts, houses | III.1, **3–5** |
| 14 | **Answered** | III.2, **4–9, 22, 38–54**; III.8, **7** |
| 15 | **Answered** — everything; seven indicators | IX.1, **9–25, 35–39** |
| 16 | **Answered**, incl. the quadruplicity direction rule | IX.1, **26–34** |
| 17 | **Answered** — resolves disagreement #1 by scope | II.1, **25**; III.2, **2–3** |
| 18 | **Answered** — terms distinct in PN IV | Intro §8 p. 77 vocabulary |
| 19 | **Answered** | I.2, **1–4**; I.6, **1–11** |
| 20 | **Answered** | I.7, **2**; II.23, **3** |
| 21 | **Answered** | II.3, **1**; III.8, **15–16**; IX.9, **1–10** |
| 22 | **Answered** — months yes, days declined by the author | IX.3, **2**; IX.7, **79** |
| 23 | Partly — transit/direction combination is pervasive but no single-window rule | V.8, **21–35**; IX.8, **8–9** |
| 24 | **Answered** — by degree, with "completeness" grading | V.1, **1–7** |
| 25 | **Answered** — corroboration required | IX.8, **112–13**; III.7, **32–42** |
| 26 | Declined — no per-planet unit switch in PN IV | — |
| 27 | **Answered** — full sequence, Nodes last | IV.1, **2–4**; IV.7, **24–25** |
| 28 | **Answered** — sevenths, Nodes excluded | IV.1, **5–8** |
| 29 | **Answered** — both | IV.7, **27–28** |
| 30 | **Answered** — Ptolemy's seven ages | I.8, **10–26** |
| 31 | Declined — absent | — |
| 32 | Partly — a relative, not the method | III.7, **32–42**; IX.8, **13** |
| 33 | **Answered** — unit keyed to chart level | III.1, **6** |
| 34 | Declined — absent | — |

**Answered: 20. Partly: 2. Declined or not determinable: 12. Total 34.**

> **Note on the count.** `04_timing_open_questions.md` §2 describes itself as "the 35 numbered
> questions in §2A–2H", and `PN4_READING_BRIEF.md` §4 repeats that. **There are 34**, numbered
> 1–34 with no gaps and no duplicates (verified by extracting the numbers from §2). The "35" is
> an off-by-one in the checklist's own prose, not a missing question.

---

## What the corpus disagreements now look like

| # | Item | Effect of PN IV |
|---|---|---|
| 1 | Distributor vs lord of the year | **RESOLVED BY SCOPE.** II.1, **25** + III.2, **2–3** |
| 2 | Where the greater years are granted | **PN IV IS SILENT.** IX.8, **123** defers to another book. Stays open |
| 3 | Two longevity procedures | PN IV uses the releaser/house-master/cutter procedure; Māshā'allāh's alternative is absent |
| 4 | Valens's Fortune-years | Untouched |
| 5 | Time unit by sign type | **PN IV answers a different question** (III.1, **6**). Stays open |
| 6 | Unit by planet | Untouched |
| 7 | Directing "by the bounds" | PN IV distributes *through* the bounds throughout; 4.12, **5**'s "not distributed" has no PN IV parallel |
| 8 | Fig. 47 vs prose | Untouched (a *Times* problem) |
| 9 | Ascending quick/slow | Untouched |
| 10 | Primary malefic for the father's Lot | Untouched |
| 11 | "The Ascendant of the year" | **PN IV keeps the two senses under different names.** Cannot be cited either way for Sahl |
| 12 | Aphorism #45 | Untouched; policy stands |

**One disagreement resolved, two clarified as out of scope, nine untouched.** The checklist's
"do not resolve" instruction remains correct for all of them except #1.
