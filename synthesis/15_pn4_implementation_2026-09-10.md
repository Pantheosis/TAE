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

### 4f. VI.2, 1–26: the turning of the houses of the root — built 2026-09-10, second session

Technique 5 of the continuation brief, put to the owner with the four-point prompt. Chosen as
recommended: **the full turning table** — planets, whole-sign houses with a displaced quadrant cusp
turned both ways, and the Lots VI.2 names — over planets and houses alone. The direction half of
VI.2, 1 was not asked: it is the standing refusal, and the prompt said so instead.

**Re-checked in the corpus before writing:**

| Citation | What it had to support | Held? |
|---|---|---|
| **VI.2, 1** + fn 11 | turned "from its own position (a year for every sign)", directed "a year for every degree"; the fortune or infortune reached | yes |
| **VI.2, 2–17** + fn 12–31 | the topics; the Lot formulas are the editor's identifications | yes |
| **VI.2, 6, 8** + fn 16, 19 | "whichever one of the two had the shift" = the sect planet | yes, as an editor's reading |
| **VI.2, 18–20** + fn 32 | the generalisation to any indicator | yes — not built |
| **VI.2, 21–26** + fn 33, 34 | a displaced cusp turned "in two ways", directed "by the portions of the hours and the right circle" (semi-arcs, fn 33); Figures 90–91 are Dykes' | yes |

**Stated, not presupposed — for the turning.** The turning is whole-sign profection from each
point's own natal position, and the engine's `pn4_profect` already does it for the Ascendant. The
direction is III.1, 12's third case for planets and Lots and, for cusps, a name for semi-arcs with
no procedure (VI.2, 21); it stays refused and every row of the table says so, with houses 1, 10
and 4 pointing to the distributions the page applies.

**Read in and said on the page.** Which "twelve Lots" is not stated; the engine's Lots are paired
to fn 12–31 (`PN4_TURNING_LOTS`), and the two places the engine's Sahl rows do not reverse at
night where the footnote does — siblings (fn 15, Firmicus) and marriage (fn 26) — are named in
the row rather than silently repaired. All three of fn 31's enemy Lots appear. The parents'
indicators follow the sect.

**What was built.** `PN4_TURNING_HOUSES`, `PN4_TURNING_LOTS`, `pn4_turning_planet_topics`,
`pn4_turned_sign`, `pn4_turning_rows` (with `_pn4_natal_planets_in_sign` for VI.2, 1's fortune
or infortune reached); the bundle carries `turning_rows`; one section, one table and a caption.

**What pins it.** Six fixtures: each point turns from its own sign (Sun, house 3, the Lot of the
father, none from the sign of the year); the fortune reached is reported (Jupiter in Sagittarius
at the Sun's fifth year); a displaced fifth cusp in the sixth sign gives two rows turned from Leo
and from Virgo, VI.2, 22–24's own example, and an undisplaced house gives one; the direction
column refuses with the citation and points houses 1, 10 and 4 at the distributions; the parents'
indicators follow the sect; every footnote Lot is present, fn 31's three, and the two reversal
differences are stated in the row.

**Verification.** Doctrine fixtures 196 (were 190). `tables.json` **+6 / −0**. Full suite
**2509 passed**, six of them new; `test_base_tables.py` 121 / 0. Rendered in the browser.

**Left undone, on purpose.** The direction; VI.2, 4–5's triplicity lords; VI.2, 18–20's
generalisation; the delineations. The next prompt, per the brief, is indicators 5–19 of the
year (II.1, 10–24) — of which #5 is now built.

### 4g. II.1, 11–24: indicators 6–19, the fact each one reads — built 2026-09-10, second session

Technique 6 of the continuation brief, put to the owner with the four-point prompt. Chosen as
recommended: **the positional nine computed, the other four as honest rows** — over applying the
static connection test to the revolution for #7 and #15 without II.22's condition.

**Re-checked in the corpus before writing:**

| Citation | What it had to support | Held? |
|---|---|---|
| **II.1, 11–25** + fn 8–23 | the fourteen indicators, their chapters, the ranking | yes |
| **V.1, 1–3** | transits to rooted positions graded: the degree, the bound, the sign | yes |
| **VI.3, 1–5** | the revolution's Ascendant and lord; the terminal sign and the revolution's Ascendant as one natal house, with a revolution planet in it | yes |
| **VI.4, 1–3** | the year reaching a sign with a natal planet, "or that sign was the Ascendant of the revolution" | yes |
| **VI.5, 1–4** | the three places: natal Ascendant, terminal sign, revolution's Ascendant | yes |
| **VI.6, 1–2** + fn 128; **3–7** + fn 129 | the three lords "relative to its place" = relative to its own Ascendant; the lords' connections | yes |
| **VII.9, 1** | the Head and Tail against the same three places | yes |
| **VIII.1** | the planets in their own or another's house and bound | yes |
| **II.22, 1–4** | the Moon's connections "so long as she is in her own sign"; void → the lord of her house | yes |

**Stated, not presupposed.** Every row reads a fact the sentences name. What is NOT computed, and
each row says: #7 and #15 need a connection read in the revolution, and II.22's condition is that
it perfects before the Moon leaves her sign, which the engine's static natal-chart test does not
encode; #16 and #17 follow the year's transits, which the engine does not track. Nothing here
delineates: II.6–21, V, VI.3–6, VII.9 and VIII.1–15 are the judgments and are not built.

**What was built.** `_pn4_transit_grade` (V.1, 2–3), `_pn4_house_from`, `pn4_further_indicators`
— fourteen rows in II.1, 25's order with `#`, `Indicator`, `Reads`, `Source`; the bundle carries
`further_rows`; one section, one table and a caption under the indicators table.

**What pins it.** Five fixtures: fourteen rows numbered 6–19 with the four honest rows saying
what they omit; V.1's three grades (20.5, 23 and 27 Aries against natal 20 Aries) and a quiet
revolution reading "none, even by sign"; fn 128's own example (revolution Ascendant Scorpio, Mars
in Capricorn: house 3 from Scorpio); VI.3, 3's coincidence and VI.4's natal planets in the
terminal sign; VI.5's three-place counting for a planet and VII.9's for the Head and Tail, with
VIII's own-house/own-bound reading (Mars at 0 Aquarius: Saturn's house, Mercury's bound).

**Verification.** Doctrine fixtures 201 (were 196). `tables.json` **+6 / −0**. Full suite
**2514 passed**, five of them new; `test_base_tables.py` 121 / 0. Rendered in the browser.

**Left undone, on purpose.** The connections of #7 and #15; the year's transits of #16 and #17;
all delineation. The next prompt, per the brief, is the governor (IX.9, 1–10; IX.2, 4–7), which
can only be partial because one of its eight indicators is the distributor from the longevity
releaser.

### 4h. IX.9, 1–10 and IX.2, 4–7: the governor — built 2026-09-10, second session, partial by nature

Technique 7 of the continuation brief, put to the owner with the four-point prompt. Chosen as
recommended: **both governors, admitted as partial** — IX.9's tally over the six available
testimonies and IX.2's five-condition sign test — over IX.2 alone.

**Re-checked in the corpus before writing:**

| Citation | What it had to support | Held? |
|---|---|---|
| **IX.9, 1–9** + fn 321–324 | the eight testimonies; "the first lord" of the revolution's Ascendant; fn 321: the same list as II.2, 10–18 | yes |
| **IX.9, 10** | all eight in one planet → governor alone; some → primary, the rest partner | yes |
| **IX.2, 4–7** + fn 35–39 | the five conditions; fn 36 the convertible sign's ninth-part; fn 37 governs the year too; fn 39 Dykes' worked case | yes |
| **IX.8, 123** | the releaser is not supplied — why #3 and half of #4 are unavailable | yes (already pinned) |

**Stated, not presupposed.** Both rules are the sentences'. What is partial, and each row says: #3
and the releaser's half of #4 need the longevity releaser; #7 needs the Moon's connection in the
revolution, with her house lord standing in only when she is void, which is not determined. The
tally therefore runs over six of eight, names the primary among them, and **never prints a planet
as governor alone**. "The first lord" is read as the domicile lord (fn 324). Judgments — IX.9,
11–13, IX.2, 8–11 — are not built.

**What was built.** `PN4_GOVERNOR_TESTIMONIES`, `pn4_governor` (rows + summary with tally,
primary, counted-of-eight, and a text that states the ALONE bar), `pn4_first_month_governor` (five
rows and a verdict, each condition with what it reads); the bundle carries `governor` and
`first_month_governor`; one section with two tables on the page.

**What pins it.** Four fixtures: six of eight counted even when all six agree, with the ALONE bar
in the text and the three unavailable rows carrying their reasons; a tie named as two primaries,
and a missing distributor making #2 and #4 unavailable with the reason; Dykes' fn 39 case (natal
Lot on the natal Ascendant, age 39 → Cancer, revolution Ascendant and Lot in Cancer, convertible,
the Moon) passing all five; and one condition failing at a time as negative controls.

**Verification.** Doctrine fixtures 205 (were 201). `tables.json` **+12 / −0** (two tables on six
charts). Full suite **2518 passed**, four of them new; `test_base_tables.py` 121 / 0. Rendered in the browser.

**Left undone, on purpose.** The two releaser testimonies; the Moon's connection; the judgments.
The next prompt, per the brief, is the Moon's connections dividing the year (II.22, 2–3), which
needs the same connection-in-the-revolution the engine does not compute — the prompt must say
whether it can be built at all.

### 4i. II.22, 1–4: the Moon's connections in her sign, and the portions of the year — built 2026-09-10, second session

Technique 8 of the continuation brief, put to the owner with the four-point prompt. Chosen as
recommended: **computed every year, filling indicator #7 and the governor's testimony #7**, over
showing the division only in the Moon's years.

**Re-checked in the corpus before writing:**

| Citation | What it had to support | Held? |
|---|---|---|
| **II.22, 1** + fn 307–309 | "the planet which the Moon connects with, so long as she is in her [current] sign", inside "If the Moon was the lord of the year" | yes |
| **II.22, 2–3** | two → halves, three → thirds, more → by their number; each portion judged by its owner | yes |
| **II.22, 4, 17** + fn 310 | empty in course → the lord of her house, "whether it looked at her or not" | yes |
| **II.1, 12**; **IX.9, 8** + fn 323 | the connection as indicator #7 of every year and testimony #7 of the governor | yes |
| **VII.5, 14** (via `_perfection_day`) | no out-of-sign connection — the configuration re-checked at perfection | already pinned |
| Intro p. 106–107 | Dykes on the void Moon and Sahl's exception — the editor's, not built | read |

**Stated, not presupposed — with four readings named on the page.** "Connects with" is a
perfection by degree of the body or a Ptolemaic ray before her sign exit, found by the engine's
forward simulation; the portions go to the planets in the order of connection (not stated); the
division is stated for the Moon's year and is computed every year with this year's lord named;
"empty in course" is no such perfection before she leaves the sign. II.22, 11's rays, Lots and
twelfth-parts are not counted; II.22, 5–24's judgments are not built. No worked example exists.

**What was built.** `PN4_MOON_ASPECTS`, `pn4_moon_connections` (simulation from the revolution,
`_perfection_day` before her sign exit, day order), `pn4_moon_portions`, `pn4_moon_testimony`;
`pn4_further_indicators` takes the result for row #7 and `pn4_governor` takes the testimony and
counts it, so the governor's tally now runs over **seven** of eight; the bundle carries the
year's length to the next revolution and the portions; one section with two tables (none when
she is void, and the markdown says so). The two captions that said the connection was not
computed now say where it is read.

**What pins it.** Five fixtures: the portion arithmetic; every connection the simulator reports
on four real revolutions perfects before the exit day, inside her starting sign, and exact to the
ephemeris at that moment (checked with a fresh `swe.calc_ut`, not the simulator); a void case
built by searching the ephemeris for a Moon within a third of a degree of her sign's end with no
aspect degree ahead of her, which must read empty in course and fall to her house lord; the
governor counting seven when handed the testimony and six when not; the bundle's row #7 no
longer reading "NOT computed" and its portions closing at the year's length.

**Verification.** Doctrine fixtures 210 (were 205). `tables.json` **+8 / −0**: the two tables on the four fixture charts whose Moon is not void. Full suite
**2523 passed**, five of them new; `test_base_tables.py` 121 / 0. Rendered in the browser.

**Left undone, on purpose.** The judgments; #15's house-lord connections, which the same
simulator could read but which no prompt has yet asked for. The next items in the brief are the
interpretation bodies (III.2's analysis and the rest), which are delineation prose.

### 4j. III.2: the distribution analysed — built 2026-09-10, second session

Technique 9 of the continuation brief, the first of its interpretation items, put to the owner
with the four-point prompt. Chosen as recommended: **the checklist as facts, the static type by
nature, and this year's transitions with the twelve indications quoted verbatim**, over a
classification with nothing quoted.

**Re-checked in the corpus before writing:**

| Citation | What it had to support | Held? |
|---|---|---|
| **III.2, 1–3** | the distributor's power across years; the year's witnesses | yes |
| **III.2, 4–9** + fn 41–43 | the checklist: bound and lord, its condition, the places from the three signs, the sign's rulers, who is in it, who casts rays to it | yes |
| **III.2, 10–17** + fn 44–50, Figure 66 | the seven types, and the sentences delineating each (18–54) | yes; fn 48 calls type 5 "an ambiguous mixture" |
| **III.2, 33** + fn 56, Figure 67 | Dykes' diagram: Mars distributing in Leo with Venus's sextile — type 3 | yes, an editor's example |
| **III.2, 55–86** + fn 69–72, Figures 68–73 | the six factors and the twenty-four ways (58–62 the bound alone, 63–67 the management alone, 68–76 the bound qualified, 77–85 the management qualified) | yes; 72 and 95 run across page breaks and were read whole |
| **III.2, 87–101** + fn 73–82 | the twelve indications, four paired and eight doubled; 93 and 101 for all four alike | yes — quoted |
| **III.2, 102–104** | the ranking of the three indicators | already built |
| **III.2, 105–106** + fn 83 | the twelve concern the rooted manager; a revolutionary planet in the bound is another matter (43, 46–47, 54) | yes |
| **III.2, 110–111** | every death statement gated on the longevity indicator's years | yes — the gate is printed |

**Stated, not presupposed — and what is not judged.** The checklist is answered as facts; the
conditions the delineation turns on ("in a suitable condition in the root and in the revolution")
are not judged and III.2, 18–54 is not built. The Sun, Moon and Mercury are neither fortune nor
infortune and the types and transitions speak only of those two, so a distribution under one of
them reads "no type by nature" and a shift involving one "not among the twenty-four"; type 5,
which turns on a corrupting infortune and a weak fortune, is never assigned. The transitions are
read from the natal distribution, as 105 requires. Each quoted indication that mentions death —
90, 91, 98, 99, 100, and 101 — carries 110–111's gate, which is the refused releaser.

**What was built.** `pn4_nature`, `PN4_III2_TYPES`, `pn4_static_type`, `PN4_III2_TRANSITIONS`
(the twenty-four as (kind, from, to, context)), `PN4_III2_PAIRED` and `PN4_III2_DOUBLED` (the
twelve, quoted, with the death flag), `pn4_transition_numbers`, `pn4_classify_shift` (one
boundary → zero, one or two shifts, numbered, with 93/101 when all four are alike),
`pn4_year_transitions` ([age, age+1) in years of arc), `pn4_distribution_checklist` (the seven
fact rows for the current bound, with the revolution's rays into it listed as a fact under
105–106); the bundle carries `iii2_type`, `iii2_checklist`, `iii2_transitions`; one section on
the page after the Ascendant's distribution.

**What pins it.** Five fixtures: the seven types by nature with Figure 67's Mars–Venus as type 3
and the neutrals as none, type 5 never; the twenty-four mapping onto the twelve — every number
answers to exactly one indication, the isolated eight to the paired four and the qualified sixteen
to the doubled eight, and the five death-gated sentences named; shift classification quoting the
sentence (#2/#11 → 97 with 90 cited; #7/#22 → 96; the gate on 98; 101 when all four are
infortunes and 93 when all four are fortunes; a neutral manager leaving only the isolated number;
a neutral distributor not among the twenty-four); the year window; and the checklist on a
constructed pair of charts (Mars's bound of Aries, the places 1 / 9 / 10, the sign's rulers, the
planets in it, the Sun's square and Saturn's body in the bound).

**Verification.** Doctrine fixtures 215 (were 210). `tables.json` **unchanged**: the six fixture charts are past the 120-year table, so the section renders its "no current distribution" line and no table there; the live state was checked in the browser at age 42. Full suite
**2528 passed**, five of them new; `test_base_tables.py` 121 / 0. Rendered in the browser.

**Left undone, on purpose.** III.2, 18–54's delineation and its conditions; the revolutionary
planet in the bound as a rule (item 12). The next prompt, per the brief, is the luminary proxies
for the lord of the year (II.13, 1; II.14, 1; II.22, 1–5).

### 4k. II.13, 1; II.14, 1; II.22, 1–5: the luminary proxies — built 2026-09-10, second session, partial by nature

Technique 10 of the continuation brief, put to the owner with the four-point prompt. Chosen:
**the proxies table, its first row admitting the releaser**, over leaving it unbuilt.

**Re-checked in the corpus before writing:**

| Citation | What it had to support | Held? |
|---|---|---|
| **II.13, 1** + fn 237–241 | the Sun's four: the releaser's distribution sign and lord; the planet in Leo, root or revolution; the planet the Sun hands over to in his sign; where the Sun is | yes; fn 239 reads the hand-over as the Sun's and notes root/revolution unstated; fn 241 reads "where the Sun is" as his sign's lord |
| **II.14, 1** + fn 249–250 | the distributor added, "probably" the releaser's | yes |
| **II.22, 1–5** + fn 308–310 | the Moon's six | yes (1–4 already pinned under 4i) |
| **II.22, 6–10** + fn 311 | her conditions: latitude, "calculation", glow | yes — shown as facts, not judged |

**Stated, but the first proxy is the releaser.** In every version the leading proxy is the sign the
longevity releaser's distribution stands in and its lord (II.14 adds that distributor itself),
which PN IV does not supply and the engine refuses: those rows read unavailable with the reason.
The rest is built: the occupants of Leo or Cancer in root and revolution; the Sun's hand-over as
his own connections before he leaves his sign in the revolution, "hands over" read as the Sun
being the applying body at the perfection (a speed comparison at that moment, so the Moon, always
faster, never receives it); the Moon's rows from 4i; her conditions as facts.

**What was built.** `_pn4_luminary_connections` (the Moon's computation generalised over the
body, with an `applying_only` gate), `pn4_moon_connections` as its wrapper, `pn4_sun_handover`
(horizon 40 days, daily steps), `PN4_PROXY_RELEASER`, `pn4_luminary_proxies`; the bundle runs
the Sun's simulation only in a Sun year and carries `proxies`; one section, one table, shown
only when the Sun or the Moon is lord of the year, otherwise a line saying so.

**What pins it.** Three fixtures: every hand-over the simulator reports on two real revolutions
perfects before the Sun's exit, in his sign, exact to a fresh ephemeris call, with the Sun the
faster body and never the Moon; the rows for a Sun year and a Moon year on constructed charts
(the releaser rows, Leo's and Cancer's occupants from both charts, the hand-over, the Moon's
rows, her conditions), and `None` for a Mars year; the bundle computing the Sun's hand-over in a
Sun year only.

**Verification.** Doctrine fixtures 218 (were 215). `tables.json` **+1 / −0**: one fixture chart has a luminary year, the others render the one-line notice. Full suite
**2531 passed**, three of them new; `test_base_tables.py` 121 / 0. The non-luminary notice was seen in the browser on the default chart; the luminary table's render is covered by the fixture chart whose year a luminary rules (the Browser pane was hidden when the live check was attempted, so no screenshot of that state).

**Left undone, on purpose.** The releaser rows; the delineations of II.13, 2 – II.21 and II.22,
5–24. The next prompt, per the brief, is the four-way root/revolution comparison for the lord of
the year (II.3, 5–19, Figure 55).

### 4l. II.3, 2–19: the sign of the terminal point and its lord, examined — built 2026-09-10, second session

Technique 11 of the continuation brief, put to the owner with the four-point prompt. Chosen as
recommended: **facts for both charts, Figure 55's four sentences quoted, the cell unchosen**, over
a verdict by II.3, 6's list.

**Re-checked in the corpus before writing:**

| Citation | What it had to support | Held? |
|---|---|---|
| **II.3, 1** | the terminal point and the lord of the year | already pinned |
| **II.3, 2** + fn 35–42 | the root checklist: house class, rulers, occupants (planets, Lots, twelfth-parts), who looks and from where, to what bound, face and degree, devoid | yes; fn 37–41's classes of sign and degree are not read |
| **II.3, 3–4** + fn 43–44 | the revolution checklist; conditions "in the way we stated it in Chapter I.7" | yes |
| **II.3, 5–8** + fn 45–49, Figure 55 | the four cases and the factors of suitable and contrary; "domain" as sect; "westernization" as going under the rays for the superiors | yes — quoted, cell unchosen |
| **II.3, 9–18** + fn 50–51 | reception; a stake of the revolution's Ascendant under a non-receiving infortune's square or opposition; aversion to the Ascendant from 2, 6, 8, 12 | yes |
| **II.3, 19–20** | the Lots and twelfth-parts; the eighteen chapters that follow | yes — not built |

**Stated, not presupposed — and no verdict.** The book names the factors and gives no rule for
weighing them, so every factor is shown per chart from the engine's own evaluators (essential and
accidental dignity, solar phase, reception under the Configurations page's rule, all run on the
revolution's data as on the root's) and Figure 55's cell is left to the reader. Aspects to the
sign and to the lord are by whole sign. Not read: twelfth-parts; fn 37–41's classes. II.4–II.21
are not built.

**What was built.** `PN4_II3_FIGURE_55` (the four sentences), `_pn4_house_class`, `_pn4_tag`,
`_pn4_looks_at_sign` (whole-sign aspects to a sign with the ray's degree in it),
`_pn4_lots_in_sign`, `pn4_ii3_examination` (root rows, revolution rows, the lord's six factors
per chart, the refinements, Figure 55); the bundle carries `ii3`; one section with five tables.

**What pins it.** Four fixtures on constructed charts: the root checklist (house 4 a stake; house
of the Moon, exaltation of Jupiter, triplicity of Venus by day; the Sun and Mercury in it; the
Moon's square from 20 Libra with the ray at 20 Cancer in Jupiter's bound and the Moon's face);
the revolution checklist (Saturn in it; Mars's trine and Jupiter's opposition with their degrees;
house 1 → 4; the labels; a devoid case); the lord's factors (direct → retrograde, burned in the
revolution, peregrine at 0 Aquarius) and Figure 55's four citations with no verdict key; the
refinements (a stake of the revolution's Ascendant opposed by Saturn; looking at the Ascendant
from a stake; house 6 not looking).

**Verification.** Doctrine fixtures 222 (were 218). `tables.json` **+30 / −0**: the five tables on six charts. Full suite
**2535 passed**, four of them new; `test_base_tables.py` 121 / 0. The section's five tables render on every fixture chart.

**Left undone, on purpose.** Twelfth-parts; the classes of sign and degree; the verdict; II.4–21.
The next prompt, per the brief, is transits into the bound of the distribution (III.2, 38, 43,
46–47, 54; III.8, 7).

### 4m. III.2, 38, 43, 46–47, 54; III.8, 7: transits into the bound — built 2026-09-10, second session

Technique 12 of the continuation brief, put to the owner with the four-point prompt and built as
recommended: **each revolutionary body or ray in the current bound keyed by the static type to
the one sentence that speaks of it, quoted, with III.8, 7's condition on the two lords as facts.**

**Re-checked in the corpus before writing:**

| Citation | What it had to support | Held? |
|---|---|---|
| **III.2, 38–39** + fn 61–63 | type 1 with an infortune's body or rays in the bound in the revolution: good fortune and "incidental adversity and harm"; 39's aggravators | yes |
| **III.2, 40–43** + fn 64–65 | in the type-5 discussion, a fortune's body or rays in the bound: "will not have the power to repel death, but his death will be with reverence" — read whole across p. 303 | yes |
| **III.2, 46–48** | type 6 with a fortune's ray: revered in illness; an infortune's ray: a bad death; 48 at home | yes — rays, not bodies |
| **III.2, 54** + fn 67–68 | type 7 with an infortune's body or rays: "good fortune but he will be unhappy with it" | yes |
| **III.2, 105–106** + fn 83 | these are "not in the manner we have described" for the twenty-four | yes |
| **III.8, 7** | both lords infortunes, "both not in their own shares, but a fortune was with each": "a little good" | yes |
| **III.2, 110–111** | the death gate | already printed |

**Stated, and keyed by type.** Each sentence names its type and its entrant, so the pairing is the
sentence's own. Said in the row: the Sun, Moon and Mercury are addressed by none; 46–47 speak of
rays, so a body in a type-6 bound is not paired; 43 is shown under 40–42's conditions, which are
not judged; III.8, 7 is a condition on the lord of the year and the distributor and is shown as
facts (in its own share or not; a fortune with it or not) with the sentence quoted when both are
infortunes.

**What was built.** `_pn4_bound_span` (shared with the checklist), `PN4_BOUND_TRANSIT_SENTENCES`
(the five, quoted, with the death flag), `pn4_bound_transit_sentence`, `pn4_bound_transits`; the
bundle carries `bound_transits`; one table under the III.2 section, and that section's caption now
says the pairing is built rather than that it is not.

**What pins it.** Two fixtures: the keying (each type and entrant to its sentence, the neutrals to
none, a type-6 body to "rays", 43's condition note, the three death-gated sentences); and the rows
on constructed charts (a neutral entrant, Saturn's body under a fortune alone quoting 38 without
the gate, III.8, 7 refusing for a fortune lord and reading the facts for two infortunes, a fortune's
trine into a type-6 bound quoting 46 with the gate, a fortune's body there reading "rays", and no
rows without a current distribution).

**Verification.** Doctrine fixtures 224 (were 222). `tables.json` **unchanged**: the fixture charts are past the 120-year table, so the table does not render there; the rows were checked on a real chart at age 42 by the bundle. Full suite
**2537 passed**, two of them new; `test_base_tables.py` 121 / 0.

**Left undone, on purpose.** 39's aggravators, 40–42's and III.8, 7's conditions as judgments; 48.
The next prompt, per the brief, is the revolution chart's full contents (I.6, 3–8, Figure 52).

### 4n. I.6, 3–8: the image of the revolution of the year, as an inventory — built 2026-09-10, second session

Technique 13 of the continuation brief, put to the owner with the four-point prompt. Chosen as
recommended: **the 154-point inventory with the twelfth-parts under the existing provenance
note**, over leaving the twelfth-parts out.

**Re-checked in the corpus before writing:**

| Citation | What it had to support | Held? |
|---|---|---|
| **I.6, 1–2** + fn 31 | the wheel, the houses by "the portions of hours and the ascensions of the right circle" = the quadrant cusps | yes |
| **I.6, 3** + fn 32 | the revolution's planets, conditions, rays, twelfth-parts, and the twelfth-parts of the house degrees | yes |
| **I.6, 4** | the root's planets, rays, twelfth-parts, "the twelfth-parts of the signs, and the Lots and Head and Tail" | yes |
| **I.6, 5** + fn 33 | the natal Ascendant and the terminal point; Dykes' whole-sign drawing | yes |
| **I.6, 6** + fn 34 | the endpoint of the distribution, distributor, partner, fardār lord and divider, lord of the orb, "in their signs and bounds" | yes |
| **I.6, 7** + fn 35 | a fixed star on the Ascendant, Midheaven, a luminary or an angular planet | yes — not computed |
| **I.6, 8–11** + Figure 52, fn 36 | the count: 14, 98, 2+2, 24+14 = 154, the Lots apart; by degree within a house | yes — the count is a fixture |

**Stated as a drawing, built as a table.** Every point of I.6, 3–6 is listed by whole-sign house
from the revolution's Ascendant, ordered by degree within the house, with its bound (I.6, 6's
"in their signs and bounds"). The twelfth-part construction is stated in no text in hand; the
engine's `_twelfth_part_sign` already supplies it from convention for the Moon's fifth corruption
and says so, and `pn4_twelfth_part` carries the same convention through to the degree and is
pinned to agree with it on the sign. The fixed stars are not computed and the page says so. The
Lots are the engine's, outside the count as I.6, 8 leaves them.

**What was built.** `pn4_twelfth_part`, `pn4_revolution_image` (rows and counts); the bundle
carries `image`; one section after the revolution table, with the count line checked against 154.

**What pins it.** Two fixtures: the twelfth-part degree (1 Aries → 12 Aries, 5 Aries → 0 Gemini,
29 Pisces → 18 Aquarius) agreeing with the engine's sign construction across the zodiac; and the
count on a real chart — 14, 98, 4, 24, 14 = 154 with the Lots outside — with I.6, 5's two points,
I.6, 6's time lords, twelve houses, and degree order within each house.

**Verification.** Doctrine fixtures 226 (were 224). `tables.json` **+6 / −0**: the inventory on six charts. Full suite
**2539 passed**, two of them new; `test_base_tables.py` 121 / 0.

**Left undone, on purpose.** The wheel itself; the fixed stars; I.6, 3's "conditions in rising and
falling" beyond direct/retrograde (fn 32 is unsure what it means). The next prompt, per the brief,
is the reading checklist (I.7, 1–26).

### 4o. I.7, 1–26: the reading checklist — built 2026-09-10, second session

Technique 14 of the continuation brief, put to the owner with the four-point prompt. Chosen as
recommended: **the facts, with the six things the page does not read named**, over 2–6 alone.

**Re-checked in the corpus before writing:**

| Citation | What it had to support | Held? |
|---|---|---|
| **I.7, 1–6** + fn 37–38 | the revolution's Ascendant: its house in the root (fn 37 adds "dynamic angularity"), who is in it and looks at it, who has a claim (fn 38) and where they stand, in a share or in exile; the lord's one house or two | yes |
| **I.7, 7–24** + fn 39–45 | the per-planet list; fn 41 whole sign, fn 42 by degree, fn 44 the return, fn 45 the Lots | yes |
| **I.7, 25–26** + fn 46 | the two-times principle | yes — already applied under II.3 |
| **I.6, 3** + fn 32 | "rising and falling", which fn 32 could not settle | yes — named as unread |

**Facts, and six things not read.** 2–7, 10–14, 17–19 and 22–24 are read from the engine's
evaluators on each chart: the pairwise configurations and the connection rule the Configurations
page uses (12–13), reception under its rule (14), the accidental dignities' domain (17), the
twelfth-part (18, the convention already declared), V.1, 2–3's grades for a return (19), the
stakes (23), the solar phase (24). Not read, and the caption says so: 8 strong or weak, 15
supporting or corrupting, 16 hostile or friendly — judgments; 9 rising and falling — fn 32; 20–21
— the year's transits, untracked. 22, the Lots of the year, are the image's rows.

**What was built.** `PN4_I7_NOT_READ`, `_pn4_share_or_exile` (I.7, 5's "share or exile"),
`pn4_i7_ascendant` (2–6), `pn4_i7_planets` (fourteen rows, seven a chart); the bundle carries
both; one section before the indicators table.

**What pins it.** Three fixtures on constructed charts: 2–6 for a Cancer revolution Ascendant
under an Aries root (house 4 a stake; the contents of both charts with the twelfth-parts falling
in it; the claimants with their shares; the Moon's one house and Mercury's two, one seen by
trine and one in aversion); share or exile (Mars in Aries, Libra, Gemini; Venus in her Aquarius
bound); and the per-planet rows (fourteen; retrograde; a return by degree and a return on the
Sun's bound; assembly and square by whole sign; the stake; the Sun's own row; the Moon's
twelfth-part at 0 Gemini; every row's domain and reception filled).

**Verification.** Doctrine fixtures 229 (were 226). `tables.json` **+12 / −0**: the two tables on six charts. Full suite
**2542 passed**, three of them new; `test_base_tables.py` 121 / 0.

**Left undone, on purpose.** 8, 9, 15, 16, 20, 21. The next prompt, per the brief, is the last
item, the nine methods for days and hours (IX.7, 1–72).

### 4p. IX.7, 1–72: the nine methods for the days and hours — built 2026-09-10, second session

Technique 15 of the continuation brief, its last item, put to the owner with the four-point
prompt. Chosen as recommended: **all seven remaining methods, method 9 pinned to IX.7, 57–69**,
over methods 3 and 9 alone.

**Re-checked in the corpus before writing:**

| Citation | What it had to support | Held? |
|---|---|---|
| **IX.7, 1** + fn 160–161 | nine indicators; fn 161: a "day" is not defined by the author | yes |
| **IX.7, 2–6** + fn 162–164 | method 1: the days since birth in weeks from the lord of the natal Ascendant, "the one below it in the circle"; the remainder; days and hours, 3 3/7 apiece | yes; fn 163's Scorpio case is a fixture |
| **IX.7, 7–9** + fn 165–166 | method 2: the lord of the orb "grants 7 days" from the first day of the revolution | yes |
| **IX.7, 10–13** + fn 167–169 | method 3: "365 1/4 minus 1/300 of a day" in greater sevenths of 52 d 4 h and a quarter, lesser sevenths of 7 d 10 h and about 6/7 | yes; fn 168's 52 d 4 h 16 m is a fixture |
| **IX.7, 14–17** + fn 170–173 | method 4: the weeks to the signs, "not the lord of the sign"; 14 hours a sign | yes |
| **IX.7, 18–20** | method 5: the days by twelves from the natal Ascendant; two hours a sign | yes |
| **IX.7, 21–22** + fn 174 | the judgment of the weeks and days | yes — not built |
| **IX.7, 34–39** + fn 181–182 | method 8: the four rooted monthly indicators and the month's Ascendant, Lot and Moon; a day per degree, or a day per 12°, 2½ days and five hours to a sign, sixty hours for the twelve | yes |
| **IX.7, 40–42** | the judgment; "sign after sign, whether ... convertible or something else" | yes — not built |
| **IX.7, 43–55** + fn 183–190 | method 9: three starts; a sign a month; the ninth-parts, thirds, ninths, thirds; 3 d 9 h 1/6; 30 d 10 h 1/2; 365¼ | yes — the durations are fixtures |
| **IX.7, 56** + fn 191 | equal hours throughout | yes |
| **IX.7, 57–69** + fn 192–198 | the worked example: 20 Taurus, Saturn; Saturn, Venus, Mercury; Saturn, Saturn, Jupiter; Saturn, Venus, Mercury; two printed fractions wrong (fn 195, 197) | yes — every lord and duration is a fixture; the errata shown as printed |
| **IX.7, 70–72** + fn 199–201 | the revolution's Ascendant start; the Moon "from that ninth-part and from that degree she is in" | yes |
| **IX.7, 79** | day and hour charts declined; these nine kept | already pinned |

**Stated, with four readings said on the page.** A "day" is a whole 24-hour period from the birth
moment, and "now" is the target date at noon; method 8's four rooted indicators are the monthly
profections already on the page (fn 181); method 9's partners are the domicile lords of the fifth
and ninth signs from the ninth-part's, as the example does; the example's two wrong fractions
are computed exactly and printed as printed. IX.7, 21–22 and 40–42 are not built.

**What was built.** `PN4_IX7_YEAR_DAYS`, `PN4_IX7_GREATER_SEVENTH`, `PN4_IX7_LESSER_SEVENTH`,
`PN4_IX7_MONTH_DAYS`, `PN4_IX7_NINTH_PART_DAYS`, `PN4_IX7_EXAMPLE_ERRATA`, `_pn4_sign_step`,
`_pn4_hours_of_seven`, `pn4_ix7_weeks_from_birth` (1), `pn4_ix7_weeks_from_orb` (2),
`pn4_ix7_sevenths` (3; its result keys are `greater_seventh` and `lesser_seventh`, since the D-3 control's regex reads `['greater']` as a planetary-years grant and method 3's sevenths are nothing of the kind), `pn4_ix7_weeks_to_signs` (4), `pn4_ix7_days_to_signs` (5),
`pn4_ix7_month_days` (8), `pn4_ix7_ninth_parts` and `pn4_ix7_moon_start` (9), `pn4_day_methods`
(the page's three tables); the bundle carries `day_methods`; one section after the mighty days.

**What pins it.** Five fixtures: the worked example of IX.7, 57–69 in full — Capricorn and
Saturn for a year at 20 Taurus, the four durations to fn 196's and 198's fractions, the thirds to
Venus and Mercury, the ninths to Saturn (Aquarius) and Jupiter (Pisces), the thirds of the ninth
to Venus and Mercury, the second ninth-part Aquarius, the second month Gemini, twelve months to
365¼, and the exact 7′24″ against the printed 7′25″; the Moon's start from her own ninth-part
and degree; methods 1–5 against fn 163's Scorpio case, fn 168's greater seventh, and the hour
fractions; method 8's two ways; and the bundle's three tables.

**Verification.** Doctrine fixtures 234 (were 229). `tables.json` **+18 / −0**: the three tables on six charts. Full suite
**2547 passed**, five of them new; `test_base_tables.py` 121 / 0.

**Left undone, on purpose.** The judgments; a dawn-based day. This closes §7 of the continuation
brief: every item is built or refused with its reason on the page.

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
