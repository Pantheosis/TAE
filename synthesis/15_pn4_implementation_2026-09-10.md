# Building the timing apparatus from *Persian Nativities* IV

Written 2026-09-10 by the implementing session, against
`PN4_IMPLEMENTER_BRIEF.md`. The reading it builds on is
`04_timing_answers_2026-09-10.md`; the corpus defects it works around are in
`process/PN4_READTHROUGH_FINDINGS_2026-09-10.md`.

**I did not read PN IV to fill any gap the reader declined.** Every citation below was opened in
the corpus and read in context before code was written against it.

---

## 1. What I re-checked, and what I took on trust

The brief's rule is that a citation can point at a real sentence and still mislead, so the ones
the code depends on were opened individually. I built a small extractor
(Book.chapter + sentence -> text, line, page) rather than grepping, because eight chapter
headings are bold-wrapped and `Chapter I.1` sits in pointed brackets — the reader's own O-01, and
it defeats a naive `^### Chapter` grep.

### Re-checked in the corpus, verbatim (33 sentences)

| Citation | What it had to support | Held? |
|---|---|---|
| **III.1, 3–6** | what is distributed; the unit keyed to chart level | yes |
| **III.1, 11** | distributor = bound lord "whether it looked at [the bound] or not" | yes |
| **III.1, 12** + fn 13, 15, 16 | the three-case ascension rule | yes, and fn 16 is *more* explicit than the answer claimed |
| **III.1, 13** + fn 17 | the rate ladder; the idealised 360-day year | yes — corpus reads 25″ (see §3) |
| **III.1, 14** | the *jār bakhtār* is the Ascendant's distributor and no other | yes |
| **III.1, 15–16** | partner = body or ray, holding until the next | yes |
| **III.1, 23–25** | the partner at birth, and the search's limit | yes |
| **III.1, 47** | every point directed from its own natal position | yes |
| **III.2, 2–3** | the distribution stronger for rooted matters, across years | yes |
| **III.2, 103–104** | body > opposition > square > trine > sextile | yes |
| **III.10, 1, 5** | the first ninth-part, with three worked examples | yes — all three reproduce |
| **I.2, 1, 4, 5** | the revolution; one sign per year | yes |
| **I.6, 2** | whole signs *and* quadrant cusps | yes |
| **I.7, 2** | the revolution's Ascendant read into the root | yes |
| **I.8, 9–26** | the Ages of Man and their derivation | yes — but see §2 |
| **I.8, 34–35** | ages not subdivided; the exaltation inconsistency | yes |
| **II.1, 5–9, 25** | the first four indicators, and their ranking | yes |
| **II.3, 1** | lord of the year = lord of the sign (*sālkhudhāh*) | yes |
| **IV.1, 2–6, 8, 11** | the *fardār*, its sub-periods, the Nodes' exclusion | yes |
| **IV.7, 24–26** | Nodes last in both sects; restart at the sect light | yes |
| **IX.1, 9–10, 26–32, 35–39** | the monthly indicators and their turning | yes — but see §2 |
| **IX.3, 2** | the monthly revolution, "like degree and minute" | yes |
| **IX.7, 29–31** | the SR Ascendant at 59′08″ a day | yes |
| **IX.7, 56** | equal hours, not planetary ones | yes |
| **IX.7, 79** | day and hour charts declined by the author | yes |

### Taken on trust, not re-checked

Stated so the next session knows where to look.

1. **IX.8 in full** — the cutters, the gate at III.2, 110–111, IX.8, 123's deferral. Nothing here
   is implemented, so nothing depends on the details; I read IX.8, 123 itself (it is the reason
   the longevity chain is refused) but not the forty configurations of IX.8, 79–118.
2. **Dykes' Introduction §§1–19 page references** (p. 12 on location, p. 90 on profection rules,
   p. 102 and fn 95 on rejecting the quadruplicity rule, p. 136–139 on the longevity frame). I
   checked the *Abū Ma'shar sentences* the answer pairs with them, not Dykes' pagination.
3. **VII.8 / Figure 146 in the *Great Introduction*** — the engine's existing `PLANETARY_YEARS`.
   I verified it agrees with PN IV's **IV.1, 2** cell for cell, which is a stronger check than
   re-reading the figure, but I did not re-open VII.8.
4. **The photographic readings of D-05 and D-07.** I did not re-photograph. D-07 I verified by
   arithmetic instead (§3), which is independent of the page. D-05 I did not need: **IV.1, 3–4's
   prose gives the whole sequence**, so the *fardār* is built from the prose and not from the
   defective figure at all.

---

## 2. Four places where the answer document is looser than the text

Both were found by re-checking, and both change what got built.

### IX.1, 31: monthly profections turn per **indicator**, not once for the year

The answer document tabulates the quadruplicity rule as *"Sign of the year -> direction of
monthly profection"*. That is right for indicator #1, whose sign **is** the sign of the year, and
wrong for #3, #4 and #5, which have signs of their own. **IX.1, 31** is explicit:

> "Now if some of these four indicators are of the fixed signs, and others of them of the
> convertible signs, and others of them of the signs having two bodies, then one turns **each one
> of them individually** in the manner we mentioned previously."

Implemented per indicator, keyed to the sign each one occupies, with a fixture
(`test_pn4_each_indicator_turns_by_its_OWN_sign`) that puts #1 in a convertible sign and #4 in a
fixed one and requires them to turn in **opposite** directions. A global reading would have
turned both the same way and passed every other test.

The boundary in a double-bodied sign is exactly **15°00′**: forward "up to 15 complete degrees"
(**28**), backward "from the beginning of the sixteenth degree" (**29**). Pinned at 14.99° and
15.00°.

### I.8, 25: the seventh age has no upper bound

The answer document's table gives Saturn "30 / ages 68–97", which is Figure 53. The prose
disagrees: the seventh age runs **"until the end of his lifespan"** (**I.8, 25**), and no number
appears in the sentence. 30 is Saturn's lesser years and is the figure's nominal span.
Implemented open-ended — a native of 120 is still in Saturn's age — and the ages do **not**
restart at the Moon (**I.8, 31–33** reports that view without endorsing it). Both halves pinned.

### IX.1, 12–16: monthly indicator #2 is not the shape the summary implies

This one was a **real bug in my first implementation**, and Abū Ma'shar's own worked months
caught it. The answer document lists indicator #2 as "ninth-part of the sign of the year", which
reads as: take the year's ninth-part sign, then profect *that* month by month. The text says
something else — what turns is the **sign of the terminal point**, and the indicator is the lord
of the first ninth-part of *whatever sign the turning reaches*:

> "And the lord of the first ninth-part belonging to the **second sign from the sign of the
> terminal point** … is the indicator of the condition of the second month of that year."
> — **IX.1, 12**, generalised at **13–14**

**IX.1, 15–16** works it: a year terminating at Cancer gives the Moon for month 1, then
**Leo → Mars, Virgo → Saturn, Libra → Venus**. My first version turned the ninth-part sign
instead and produced **the Sun** for month 2. All four months are now a fixture.

### IX.1, 17–21: #3 is profected a sign a year; #4 and #5 are not

Also a real bug. The four rooted indicators are not brought to their yearly positions the same
way, and the answer document's table does not distinguish them. **IX.1, 17–18** profects #3 in
its own right — "you see where the Lot of Fortune is in the root of the nativity, and **turn from
it a sign for every year**, up to the year which you want" — and only then turns it monthly (19).
I had been passing the **natal** Lot unprofected. **IX.1, 20–21**, by contrast, assigns the
revolution's Ascendant and its Lot of Fortune to the first month **as they stand**; they must not
be profected by the age. Both directions are now pinned, the second as a negative control.

**Seven worked examples in total** now bind the ninth-part: three from **III.10, 5**
(Taurus → Saturn, Gemini → Venus, Cancer → Moon) and four from **IX.1, 15–16**.

---

## 3. The two corpus defects, and how each was handled

The corpus is unrepaired: `pn4_complete/persian_nativities_iv.md` is still blob `295eb22`,
byte-identical to the reader's pin. I did not edit `consolidated_texts/` — a repair session owns
that tree.

**D-07, the rate ladder.** The corpus reads `every 25" one hour`; the page prints **25‴**. I did
not need the photograph: the ladder is internally over-determined. 1° = 1 year = 360 days,
5′ = 1 month, 1′ = 6 days and 10″ = 1 day are mutually consistent on a 360-day year, and they
force 1 hour = 10″/24 = **25‴** exactly. The corpus reading would make an hour 2½ days.
Implemented as 25‴, with a **negative control** asserting that 25″ yields 60 hours and not one.

**D-05, Figure 43's dropped glyphs.** Not used. **IV.1, 2** gives the years and **IV.1, 3–4**
gives the order in prose ("the Sun … Venus … Mercury, the Moon, and … Saturn, according to the
succession of their spheres"; "the Moon, then Saturn, Jupiter, [and] Mars"), which together
determine the table without the figure. Both sects are asserted to sum to 75 and the seven
planets to 70, which is **IV.1, 8**'s own checksum.

**P-01 and P-02 are not reproduced as errors**, and P-01 is actively defended: the monthly
revolution is asserted to hold the natal degree **and minute** in every sign, which is the rule
Intro §2 p. 7's "12° 23′" breaks.

---

## 4. What was built, and what was refused

### Built

| Rule | Citation |
|---|---|
| Solar and monthly revolutions, true-Sun return, birth location | I.2, 1–4; IX.3, 2 |
| The revolution's Ascendant read into the root | I.7, 2 |
| The first four indicators of the year, in Abū Ma'shar's order | II.1, 5–9, 25 |
| Lord of the year by annual profection (*sālkhudhāh*) | II.3, 1; I.2, 5 |
| The distribution **from the Ascendant** — the *jār bakhtār* | III.1, 11–16, 23–25 |
| Directed by oblique ascensions of the birth latitude | III.1, 12 |
| The rate ladder, with 25‴ | III.1, 13 |
| The unit keyed to the level of the chart | III.1, 6 |
| The *fardār*, its sub-periods, the Nodes last in both sects | IV.1, 2–8; IV.7, 24–26 |
| The seven monthly indicators, with the turn as a reading | IX.1, 9–10, 26–32, 35–39 |
| The first ninth-part (monthly indicator #2) | IX.1, 36; III.10, 5 |
| The Ages of Man | I.8, 9–26 |
| When a natal indication comes out, and at what ages | III.7, 32–42 |

### Refused, each with the reason carried into the UI

- **The releaser, the house-master, the granted years, the cutters.** PN IV lists five releasers
  (III.3, 1) and never says how to choose among them; **IX.8, 123** sends the reader to another
  book. Nothing on the page is built on a guessed releaser.
- **Directing anything but the Ascendant and the meridian.** III.1, 12's third case is deferred by
  Abū Ma'shar to a book he does not reproduce. Dykes' fn 16 names Ptolemy's proportional
  semi-arcs, but that is an editor's identification, not a stated method, and the reconstructions
  differ. Named on the page, marked "Applied: no".
- **Revolutions of the day and hour** — declined by the author at IX.7, 79.
- **The Indian lord of the year** (III.10) — reported by PN IV, not adopted; used only as monthly
  indicator #2, where IX.1, 36 puts it.
- **Corpus disagreements #2 and #5** stay open. PN IV is silent on #2 and answers a different
  question from #5; the Planetary years table still chooses no row, and neither does III.7's
  activation table (below).
- **Valens's sum and thirds** (Dykes' fn 191). See §4a.

### 4a. III.7, 32–42, and what had to be left out of it

Added 2026-09-10 on the owner's request. The chapter turned out to be narrower than the answer
document's Q32 summary, in a way that matters.

**What III.7 states.** How often a natal indication manifests, keyed to the quadruplicity of the
planet's *natal* sign — fixed "in [only] a single time" (**35**), convertible "in [only] one of
the times" (**39**), double-bodied "on an occasional basis" (**38**) — and at what ages: "the
number of ascensions of the sign in which it was in the root, or the amount of one of its own
years, or the rest of the times which one employs as models" (**42**). Abū Ma'shar's own
contribution is the confirmation: the effect is "strong, evident, notable" when such an age falls
where that same planet is the distributor or the manager. That last part is computed against the
*jār bakhtār* table, which is the one place the two techniques meet.

**What is left out, and why.**

1. **The sum, and ⅓, ½ and ⅔ of it.** The answer document lists these among the activation ages.
   They are **not Abū Ma'shar's**: Dykes' fn 191 introduces them with *"**If we follow Valens**"*,
   and no sentence of III.7 contains them. The reader did attribute the confirmation rule
   correctly, but the summary line reads as though the whole construction were PN IV's. Refused,
   on the same ground as III.1, 12's third case: an editor's identification is not a stated rule.
   Corpus disagreement #4 over Valens's tables is untouched.
2. **Which of the greater, middle and lesser years applies.** **III.7, 35** selects "in accordance
   with what its position in the rotation of the circle indicated in the root" and never states
   that rule — it is the placement question of disagreement #2, which PN IV does not adjudicate.
   All three grades are printed and none chosen, exactly as the planetary-years table does. This
   is what admitted the evaluator past the D-3 guard, and a fixture asserts no row says "grants",
   "selected" or "chosen".
3. **III.7, 36's promotion** to "whenever it distributes" needs the planet to be "strong in [its]
   indication for that thing". Strength is nowhere defined in the chapter; the looking half is
   computable, the strength half is not, so no row is promoted.

**Dykes' worked figure is not reproduced, and the ascension code is validated against a better
witness.** fn 191 gives Taurus at 45° N as 20.17 ascensional times; the exact computation gives
**20.09**. Checked further at the owner's request:

- 20.17 is the value for Taurus at **44.78° N**, not 45°.
- Obliquity does not explain it. It would need ε = 23.29°, and the historical obliquity was
  *larger* (≈23.7° in Abū Ma'shar's day, 23.85° in Ptolemy's tables), which moves the figure the
  **wrong way** — at 23.85° Taurus at 45° N is 19.86.
- His own thirds are inconsistent with his own 20.17 (he prints ⅔ of the sum as 26.75; 20.17
  gives 26.78).

So it is slop in an illustrative footnote. **The engine is instead checked against Abū Ma'shar's
own worked arithmetic**, which is a much stronger test and which the corpus turned out to contain:

> "And between the degree of the Ascendant and the Lot of courage, were 4° 20′ by [degrees] of
> equality: in the ascensions of the clime of Babylon (the fourth) that is **3° 02′**, so Venus
> distributes alone for **3 years, 12 days**." — **III.1, 26** (p. 291), the chart's latitude given
> as 36° at **III.1, 19**

At 36° N with **Ptolemy's obliquity 23;51 = 23.85°** the engine returns 3° 02′, matching to within
half an arcminute; the modern 23.44° gives 3° 04′, which is the size of error the wrong obliquity
produces. And the rate ladder closes it: 3° is 3 years and 2′ is 12 days at six days to the
minute, exactly the period printed. **Three numbers, printed in one sentence, all reproduce.**

*A departure recorded.* `04_timing_answers_2026-09-10.md` says of the III.1 worked example "do not
use it as a test fixture", following Dykes' verdict that it is "corrupted and ought to be ignored"
(Intro §7). That verdict is about its **doctrine** — the data in **19** and **22** are mutually
inconsistent, and it accumulates Lots against III.1, **47**. The fixture takes no doctrine from it:
one self-contained arithmetic step, all of whose inputs and outputs are printed in the same
sentence and check three ways. The reasoning is written into the test itself.

A second fixture pins the property that would catch a real error rather than a rounding one: a
sign and its opposite sum to the same value at every latitude — twice the equatorial span, not
60 — because the two ascensional differences cancel.

### 4b. III.1, 12: the meridian, by right ascension — built 2026-09-10, second session

Put to the owner first, per `PN4_CONTINUATION_BRIEF.md` §7, as one technique with the four things a
prompt owes (citation and whether stated; the releaser; a worked example; what the page must admit).
The owner's answer: **build it, the MC and IC degrees only, applied at every latitude.**

**Re-checked in the corpus before writing**, each opened and read in context:

| Citation | What it had to support | Held? |
|---|---|---|
| **III.1, 12** + fn 14, 15, 16 | "what is in the Midheaven or the fourth is directed by the ascensions of the right sphere"; fn 14 "or rather, the IC itself"; fn 15 the Descendant omitted | yes |
| **III.1, 7–11** | the bound-by-bound method is stated for "every bound you need, of the bounds of the Ascendant and the rest of the releasers, and the other planets and Lots" (10) | yes |
| **III.1, 13, 15–16, 23–25, 47** | ladder; partner by body or ray; partner at birth — **worded for the Ascendant**; every point from its own position | yes |
| **II.2, 4–16** | the year's indicators name the Ascendant's and the releaser's distributions (6–7, 12–13), not the meridian's | yes |
| **VI.2, 15** | "the tenth house of the root is turned and directed" for authority and rank — the *profected house*, not the MC degree; **not** used as the topic | yes |
| **Appendix A, p. 673** + fn 1 | Dykes' animation, 1° per 4 min (fn 1: 3 m 59.34 s), "the same thing with the degree of the Midheaven" | yes — an editor's procedure, used only as the cross-check |
| **fn 4** (al-Qabīsī IV.12) | the Midheaven "for the profession" — an editor's note | yes, cited as such |

**Stated, not presupposed.** III.1, 12 states the measure outright and III.1, 10 makes the method
general. What PN IV does *not* state, and the page says instead of filling in: the distribution's
topic (fn 4 and Dykes only); its place among the year's indicators (none, II.2); any worked example
(III.1, 19–45 directs the Ascendant only); and the partner-at-birth rule for a point other than the
Ascendant (carried by analogy). Planets *in* the Midheaven, which III.1, 12 also assigns to right
ascension, are not directed.

**What was built.** `_pn4_distribute` — III.1, 7–16 generalised over its measure, with
`pn4_distribution_from_ascendant` now a wrapper that keeps its D-23 refusal;
`pn4_distribution_from_meridian`, right ascension through `_ra_decl`, `point` one of
`PN4_MERIDIAN_POINTS` and a `ValueError` for anything else (fn 15); `_pn4_distribution_rows`, one
row-builder for all three tables. Every segment now carries `from_lon`, the degree it opened on.
The Timing page gains one section, two tables and a five-point caption of what the source does
not supply. The ascension-rule table's states are now `applied to the degree of the Ascendant` and
`applied to the degrees of the Midheaven and the fourth`: the Ascendant row's old bare `applied`
beside the label "and things in it" was imprecise, and the new row would have inherited the
imprecision.

**Domain: applied everywhere.** D-23 refuses where the *oblique* ascension has no inverse. Right
ascension has no latitude in it and the meridian crosses the ecliptic at every latitude, so the
arc is defined everywhere; the Ascendant's run refuses at 78° N and the meridian's does not, and a
fixture holds both halves. The refusing alternative was offered to the owner and declined.

**What pins it, there being no author's example.** Six fixtures in `test_doctrine_fixtures.py`:

- the measure — from 0 Aries the Sun's body at 0 Cancer (the solstice, RA exactly 90 at any
  obliquity) is met at **90.000** years, where the Ascendant's run from the same degree at 43.78° N
  meets it at 65.45; every segment's `from_lon` is the inverse of its arc;
- no refusal at 78° N, and the span tiled for both points;
- the fourth is the Midheaven's run **half a turn on** — opposite points are 180° apart in RA, so
  every boundary in the IC's first 180 years is one the MC's direction crosses 180 years later,
  on the same degree, with the same distributor;
- the Descendant refused;
- **Dykes' animation** — cast a chart, advance the clock by 3 m 59.34 s per year of age, and the
  Midheaven `swe.houses` reports for the later moment agrees with the directed degree to
  **0.004°** at ages 17.97, 42 and 100, and lies in the bound of the engine's distributor (Saturn,
  Mars, Saturn — three different periods, so the check has teeth). `swe.houses`' meridian is an
  independent path from the `cotrans` the engine directs with; the engine's RA of the MC equals
  swe's ARMC to 1e-14;
- `from_lon` agrees with `_pn4_seg_degree`'s oblique-ascension inverse on every Ascendant segment,
  so the two routes to the degree a period opened on cannot drift apart.

**One thing observed on the page rather than designed.** On the default chart at age 42 the
Midheaven's and the fourth's current periods both end at 44.47 years: a body the Midheaven's
direction meets is met by the fourth's direction as its *opposition ray* at the same arc, because
opposite points are 180° apart in right ascension. It follows from the sentence and it is what the
half-a-turn fixture pins.

**Verification.** Doctrine fixtures 176 (were 170). `tables.json` **+12 / −0**: the two new tables
on six charts, no existing table moved. Full suite **2489 passed**, six of them new; `test_base_tables.py` 121 / 0.
Rendered in the browser on the default chart at target date 1282-06-01 (age 42): both "now" lines,
both tables, the caption, and the ascension table's new states.

**Left undone, on purpose.** Planets in the Midheaven. III.7's "Confirmed by the distribution"
column still checks the *jār bakhtār* alone. The meridian enters neither the year's indicators nor
any governor. The next technique, per the continuation brief, is "the small days" (IX.7, 29–31),
and it is to be put to the owner before it is built.

### 4c. IX.7, 29–31: "the small days" — built 2026-09-10, second session

Put to the owner as technique 2 of the continuation brief with the four-point prompt. Two
decisions were the owner's and both were taken as recommended: **the stated rate, 59′08″ a day in
degrees of the zodiac**, over the author's own "exact" form (the Sun's real daily motion, IX.7, 32)
and over Dykes' fn 178 (by ascensions); and **the opening partner looked for behind the degree
within its bound**, the shape of III.1, 23–25 narrowed to the window IX.7, 30 names.

**Re-checked in the corpus before writing:**

| Citation | What it had to support | Held? |
|---|---|---|
| **IX.7, 29** | "a day for every 59′ 08″, until it returns to the degree of the Ascendant at the end of the year" | yes — the corpus carries it as `$59'\ 08''$` |
| **IX.7, 30** + fn 179 | a body or ray "in the bounds of the degree" manages until another meets it; else the bound lords "in the way we have stated" (→ 24) | yes |
| **IX.7, 31** | the name, and the extension to "everything of the planets, Lots, and houses" | yes |
| **IX.7, 32** + fn 178, 180 | the author's grading: an approximation, the exact form is the Sun's daily direction, "no harm in the work"; Dykes' preference for ascensions is his own | yes |
| **IX.7, 23–24** + fn 176 | the mighty days' identical management rule, which 30 refers back to | yes |
| **IX.7, 1** + fn 161 | a "day" is not defined by the author; Dykes raises it | yes |
| **IX.7, 10** + fn 167 | the year of the revolution, 365¼ − 1/300 | yes |
| Findings file, appendix item | the Janus note's "59° 08′" is the appendix's error against IX.7, 29 | yes, already recorded |

**Stated, not presupposed.** The rate, the point, the circuit and the management are all in the
sentences. Read into them and said on the page: the bodies and rays are the **revolution's**; the
days count from the **moment of the revolution**; the opening window is the bound, looking back;
only the revolution's Ascendant is directed. No worked example exists — IX.7's only one (57–69)
is the ninth-part method.

**What was built.** `_pn4_distribute` gains `opening_window` ('sign' for III.1, 23–25, 'bound'
for IX.7, 30) and `epoch` (the row text now says "at the revolution" rather than "at birth");
`PN4_SMALL_DAYS_RATE`, `pn4_small_days_arc_to_days`, `pn4_small_days` (measure = the zodiac,
span = the full circuit, segments returned in days); `_pn4_distribution_rows` gains a `unit`. The
bundle computes the day of the year as target − revolution in Julian days. The page gains one
section, one table and a caption carrying the author's grading and the four readings.

**The arithmetic the sentence itself supplies.** 360 ÷ 59′08″ = **365.28 days**: the promised
return "at the end of the year" holds to within an hour of the tropical year, which is what makes
a zodiacal rate defensible here where III.1, 12 would otherwise want oblique ascensions. The page
says the two distributions of the Ascendant on it run in different measures, and why.

**What pins it.** Six fixtures: the rate (59′08″ = 1 day; the circuit 365.28, within an hour of
the year, tiled); zodiacal and latitude-free (a body 30° ahead met at 30.44 days, where the natal
Ascendant's oblique run meets it elsewhere); the opening partner within the bound (Sun 21 Aries,
degree 22 Aries in Mars's bound: partner from day 0); **the window is the bound, not the sign**
(Sun 19 Aries in Mercury's bound: the natal distribution takes it, the small days do not, and cite
IX.7, 30); a body ahead in the bound manages on arrival, 2.03 days, not from day 0 — the owner's
reading pinned as a negative control; and the bundle starts from the revolution's Ascendant, not
the natal one, with the day of the year in range.

**Verification.** Doctrine fixtures 182 (were 176). `tables.json` **+6 / −0**: one new table on six
charts. Full suite **2495 passed**, six of them new; `test_base_tables.py` 121 / 0. Rendered in the browser.

**Left undone, on purpose.** IX.7, 31's extension to the planets, Lots and houses; the exact form
of IX.7, 32; the mighty days (IX.7, 23–28), which is the next prompt.

### 4d. IX.7, 23–28: "the mighty days" — built 2026-09-10, second session

Technique 3 of the continuation brief, put to the owner with the four-point prompt. Chosen as
recommended: **the printed rate, zodiacal, with the same three readings as the small days**, over
fn 177's corrected rate and over stopping at the end of the sign.

**Re-checked in the corpus before writing:**

| Citation | What it had to support | Held? |
|---|---|---|
| **IX.7, 23** + fn 175, 176 | the terminal point, "in the revolution of the year"; a body or ray "in the bounds of that degree" manages | yes |
| **IX.7, 24** | else the lord of the bound, "then to the lord of the bound which follows it" — the direction runs on past the sign | yes |
| **IX.7, 25** + fn 177 | "12 days, <4 hours>, 10 minutes, and 30 seconds" a degree, "from the first day of the revolution"; the `<4 hours>` is Dykes' insertion; fn 177's correction | yes |
| **IX.7, 27** | the extension to the Lots of the parents and every house and Lot | yes — not built |
| **IX.7, 28** | thirty of them are "365 1/4 days, approximately"; the name | yes |
| **II.3, 1**; `pn4_sign_of_the_year` | the terminal point is the natal Ascendant's degree carried into the sign of the year | yes |

**Stated, not presupposed.** The point, the management, the rate and the span are all in the
sentences. The rate's inexactness is the book's: thirty of 12 d 4 h 10 m 30 s is 365 d 5 h 15 m,
short of 365¼ by 45 minutes, which "approximately" covers and fn 177 corrects. The printed number
is applied and a fixture holds the 45-minute gap, so repairing the rate silently to fn 177's would
fail a test. The three readings shared with the small days are made and said on the page.

**What was built.** `PN4_MIGHTY_DAYS_PER_DEGREE`, `PN4_MIGHTY_DAYS_SPAN_DEGREES` (30),
`pn4_mighty_days_arc_to_days`, `pn4_mighty_days` — `_pn4_distribute` over the zodiac with the
bound window, cut at thirty degrees, in days. The bound-window citation in the row text is now
"IX.7, 24 and 30", the two sentences that state it identically. One section, one table and a
caption on the page. **The direction crosses the sign boundary**: from the terminal degree it runs
thirty degrees, so its last part lies in the next sign's bounds, which is what IX.7, 24 describes.

**What pins it.** Four fixtures: the printed rate and its 365.22-day year, with the 45-minute gap
from 365¼ held; zodiacal and crossing the boundary (from 25 Aries, Venus's bound of Taurus opens
at five printed days and a body ten degrees on is met at ten); the opening window is the bound
(Sun 21 Aries taken, Sun 19 Aries refused with the citation); and the bundle directs the terminal
point — the natal Ascendant's degree, six signs on at age 42 — not the revolution's Ascendant.

**Verification.** Doctrine fixtures 186 (were 182). `tables.json` **+6 / −0**. Full suite
**2499 passed**, four of them new; `test_base_tables.py` 121 / 0. Rendered in the browser.

**Left undone, on purpose.** IX.7, 27's extension; fn 177's rate. The next prompt, per the brief,
is the lord of the orb (VI.1), which uses planetary hours where the rest of the book uses equal
ones (IX.7, 56).

### 4e. VI.1: the lord of the orb — built 2026-09-10, second session

Technique 4 of the continuation brief, put to the owner with the four-point prompt. Chosen as
recommended: **the continuous loop of VI.1, 8, with the six named lords of VI.1, 18–19 read by
VI.1, 10's naming**, over VI.1, 4–8 alone and over Dykes' single-cycle alternative.

**Re-checked in the corpus before writing:**

| Citation | What it had to support | Held? |
|---|---|---|
| **VI.1, 4–8** | the natal hour lord to the Ascendant and year 1; each next hour lord to the next house and year; "the lord of the thirteenth hour from it belongs to the Ascendant of the root and the thirteenth year" | yes |
| **VI.1, 10–11** | each named by the house its number matches; all called the lord of the orb | yes |
| **VI.1, 12** | judged "just as you judge by means of the lord of the year", root and revolution | yes |
| **VI.1, 18–19** + fn 9, 10 | the six named positions | yes |
| **II.1, 10** + fn 8 | "The fifth is the lord of the orb" → VI.1 | yes |
| **IX.7, 3–5** | "the planet which is below it in the circle" — the hour lords run down the spheres | yes |
| **Intro §13**, Figures 45–48 + fn 4 to VI.1 | the hour system; the editor's worked example; the single-cycle alternative and the "reset" are his | yes — Figure 89 in the chapter is the editor's tabulation of VI.1, 8, identical to Intro Figure 47 |

**Stated, not presupposed — except the hours.** VI.1 assumes the planetary hours and never defines
them; the day-lord-at-sunrise sequence is Dykes' Figure 45. The engine's `calculate_chronocrats`
already follows it with real sunrise and sunset, a flagged equal-hour approximation where the Sun
is circumpolar, and one continuous cycle of seven across day and night, which matches Figure 45
(Sunday night-hour 1 is Jupiter in both). That is what the lord of the orb starts from, and the
page says the system is the editor's.

**What was built.** `pn4_hour_lord_from_natal`, `pn4_lord_of_the_orb` (age steps down
`PN4_DESCENDING_SPHERES`, no reset), `pn4_hour_lord_of_house` (VI.1, 10: hour k for house k),
`pn4_named_lords_of_the_orb` (the six of VI.1, 18–19). `PN4_YEAR_INDICATOR_ORDER` gains its
fifth; the bundle takes `chronocrats` and emits row 5 of the indicators table, saying which hour
of seven, which cycle of the profection, and whether the hour was approximate — or "natal hour
lord unavailable". One new section, one table and a caption on the page.

**What pins it.** Four fixtures. Dykes' worked example (Venus natal: Mercury at 1, Moon and Saturn
at 9 and 10, Mars at 12, Sun at 13, Mars at 82), every value following from VI.1, 8; the loop
does not reset (for all seven natal lords, ages 12·n for n = 1…6 differ from the natal lord and
84 returns to it — Dykes' Figure 48 is the negative control); the named lords by VI.1, 10 (at age
14 the sign of the year's lord is the third hour lord, not the natal one, which Dykes' reset would
give); and the bundle's row 5, with and without a natal hour lord.

**Verification.** Doctrine fixtures 190 (were 186). `tables.json` **+6 / −0**. Full suite
**2503 passed**, four of them new; `test_base_tables.py` 121 / 0. Rendered in the browser.

**Left undone, on purpose.** VI.1, 12–17's delineations; the seven days of IX.7, 7–8; Dykes'
reset. The next prompt, per the brief, is the profected houses (VI.2, 1–20).

### Refused at the poles

`pn4_distribution_from_ascendant` returns `None` where |latitude| + obliquity ≥ 90°, on the
domain already decided for every ascensional method here (**D-23**). Above the polar circle some
degrees never rise, the oblique ascension has no unique inverse, and an arc of direction from the
Ascendant is not defined. The page says so instead of drawing a table.

---

## 5. Where I departed from the brief, and why

**The brief said to stop.** §5 item 2: *"If the reader declined it, **stop** — items 3 and 6 depend
on it."* The reader did decline the releaser **choice**. I checked the dependency claim before
acting on it, and **it does not hold**: III.1, 11/12/13/15–16 and III.1, 6 are stated without
reference to which point is released, and **II.2, 6–7** lists the distribution *from the Ascendant*
as an indicator separate from the one *from the longevity releaser*. Only the latter needs the
choice.

Put to the owner on 2026-09-10 with that finding; the decision was to **build what does not need
the releaser and refuse the longevity chain outright**, which is also what the brief's own §7
definition of done contemplates ("implemented, or explicitly not implemented with the reader's
reason carried through to the UI").

**The owner also decided IX.1, 26–34** (the quadruplicity turn), which the reader escalated
rather than resolving: **implemented, defaulting OFF**, with Dykes' plain forward count as the
shipped default and Abū Ma'shar's rule available as a reading.

---

## 6. Verification

- **Suite green before and after.** Baseline **2392 passed** in 428 s; after, see the commit
  message. `test_base_tables.py` 121 passed / 0 skipped in both.
- **67 new doctrine fixtures**, each rule with a positive case from PN IV and a negative control.
  Several negatives are the specific wrong readings the tradition or this corpus actually
  produced: 25″ for 25‴; the Nodes after Mars in a nocturnal chart (al-Qabīsī IV.21); a
  degree-sensitive ninth-part; the ages restarting at the Moon; a global rather than per-indicator
  monthly turn; the revolution's own Ascendant profected by the native's age.
  **Two of these fixtures failed against my first implementation** and are the reason §2's last
  two items exist.
- **`tables.json` regenerated**: **+54 lines, −0**. Nine new tables on the Timing page across six
  charts; no existing table's heading or columns moved.
- **Numerically checked outside the tests**: the solar and monthly revolutions land the Sun on
  target to < 0.0001″; the arc-of-direction round-trip through the oblique-ascension inverse is
  exact to 5.7e-14°over all 29 segments of the default chart; every bound-boundary segment's
  distributor agrees with the degree it names; the refusal fires at 78° N.
- **Rendered in the browser**, not asserted: see the commit message.

## 7. For whoever comes next

- The **releaser** is the one thing still missing, and it is missing because the source does not
  supply it. It needs a source outside this corpus, not more work on PN IV.
- **IX.7, 23–33** gives two further rate keys ("the mighty days", 12 d 4 h 10 m 30 s per degree,
  and "the small days", 59′08″ a day) and **II.22, 2–3** divides the year by the Moon's
  connections. All three are cited on the page but none is computed; they are the obvious next
  increment and they need no decision. (III.7, 32–42, which used to head this list, is now built —
  see §4a.)
- **IX.8, 13** applies the same age-matching to the *house-master's* years. It stays unbuilt for
  the same reason the rest of the longevity chain does: there is no house-master to take them from.
- **Appendix B, pp. 675–677** — the table of ascensional times — exists in PN IV three pages past
  the corpus boundary. It is not needed (Appendix A gives a latitude-exact method, and this engine
  computes ascensions directly), but `04_timing_open_questions.md`'s claim that the corpus cannot
  supply it should be read as "chose not to".
- A **corpus typo not in the findings file**: **IX.7, 79** reads "their Ascendants and *plants*"
  for "planets" (line 13215). Trivial, but it is a real defect and it is not on the list.
