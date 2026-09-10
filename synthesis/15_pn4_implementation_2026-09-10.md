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
  question from #5; the Planetary years table still chooses no row.

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
  increment and they need no decision.
- **Appendix B, pp. 675–677** — the table of ascensional times — exists in PN IV three pages past
  the corpus boundary. It is not needed (Appendix A gives a latitude-exact method, and this engine
  computes ascensions directly), but `04_timing_open_questions.md`'s claim that the corpus cannot
  supply it should be read as "chose not to".
- A **corpus typo not in the findings file**: **IX.7, 79** reads "their Ascendants and *plants*"
  for "planets" (line 13215). Trivial, but it is a real defect and it is not on the list.
