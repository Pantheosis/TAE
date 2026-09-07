# Report — Tier 1, the worked question chart, and spear-bearing

**Nothing in this pass was implemented.** No code changed, no commits, no fixtures written. This is
a report of recommended changes plus a plan, per the instruction that overrode the brief's
"small commits, one item each."

Verified against the working tree on 2026-09-07. **Note the baseline:** the brief says branch off
`main` at `9b76b45`; the repo is actually on branch **`wheel-2026-09-07`** at **`980330b`**
("Chart: true node instead of mean node"), one commit ahead. Line numbers below are from `980330b`
and differ from the brief's throughout.

---

# Part A — Tier 1

## A1 ✅ Confirmed. `NOT_IMPLEMENTED_COVERAGE` states a falsehood

**Now at `app.py:4218–4219`** (brief said ~4150):

> `("Abu Ma'shar VII.7", "The casting of rays according to Ptolemy. The chapter begins on a page not photographed."),`

VII.7 is complete: `abu_mashar_book_vii.md:1812–1857`, 22 numbered sentences, pp. 485–487,
footnotes 247–253.

**Recommended change.** Replace the description. What is actually absent is not the chapter but the
**tables it presupposes** — hourly times (fn. 250: "special tables in the *Almagest*") and the
ascensions↔degrees inverse tables (fn. 251) — all computable. The entry should also carry VII.7, 22
(the opposition ray needs no tables) and the ¶18/¶21 anchor asymmetry.

## A2 ⚠ Confirmed, but the brief's diagnosis is wrong in a way that matters

The brief says the test "only fires when an absence claim names a *book*." That describes the
second stage. **The failure is at the first stage**, and fixing only the second would leave the bug
in place.

`tests/test_prose_counts.py:96`:

```python
ABSENCE_CLAIM = re.compile(r"not in (?:this|the) corpus|no table for them in this corpus", re.I)
```

The VII.7 entry says "*begins on a page not photographed*" — which matches **neither** alternative.
The `continue` at `test_prose_counts.py:112` fires and the entry is never examined at all.

There is a **second, independent** reason it could not catch this: `BOOK_CITE` is searched against
`desc`, not `passage`. The book reference "VII.7" lives in the *passage* field; the description
contains no book citation. So even with the gate widened, `cited` would be empty and the assertion
would pass vacuously.

**Recommended change — both halves, or the fix is cosmetic:**

1. Widen `ABSENCE_CLAIM` to cover the vocabulary actually used: *not photographed*, *not included*,
   *not in this photo set*, *no photo*, *not legible*, *page not*.
2. Search `passage + " " + desc`, not `desc` alone.
3. Better still, and what I would actually recommend: **assert against the corpus files rather than
   a hardcoded book list.** `CORPUS_BOOKS = ("VII",)` is a stale constant that will rot again. A
   test that greps `consolidated_texts/` for a chapter heading matching the cited passage would have
   caught A1 on the day VII.7 landed, and would catch the next one.

## A3 ✅ Confirmed — and it is the *root cause* of A1

`abu_mashar_book_vii.md:1790`:

> `*[Chapter VII.7, "On the casting of the planets' rays," begins on the following page, which is not included in this photo set.]*`

Twenty-two lines above `:1812`, where the chapter does begin. **`app.py`'s false claim is a faithful
transcription of a corpus marker that was never removed when VII.7 was added on 2026-09-07.**

That reframes A1: it is not a code defect that happened to be wrong, it is a **corpus defect that
propagated**. Fixing `app.py` without fixing the corpus leaves the source of truth contradicting
itself, and the next reader will re-import it.

**Recommended order: A3 before A1.** And the corpus file is under the OCR project's control, not
this repo's — coordinate before editing, as the brief says.

## A4 — C-02, the advancing comment

Unchanged from `03_changes.md` C-02, **strengthened** by the second-pass reading: Sahl does not
merely mention Māshā'allāh's hemisphere scheme in a timing chapter, he **uses** it in *On Choices*
Ch. 6, 16–17 and 6, 30. Comment-only; no computed value moves. Current location `app.py:4352–4400`.

## A5 ⚠ Confirmed, but the count is **six**, not four

`grep -in glossary app.py` returns six references, all to the *TNAC Course Glossary*:

| Line | Context |
|---|---|
| 811 | "the Course Glossary defines Domain" |
| 2421 | "Glossary makes the same equivalence under Cadent" |
| 4702 | "the course glossary — and takes this function's natal_houses argument" |
| 4774 | "The Course Glossary's own Cadent entry says so" |
| 4796 | "the course glossary defines advancement as…" |
| 4823 | "The Course Glossary's Eastern (2) is…" |

**Recommended change.** Four of the six have a direct counterpart in `sahl_glossary.md`, which is a
corpus document rather than external course material:

| Code claim | Sahl's glossary counterpart |
|---|---|
| advancement = dynamically angular/succedent (4702, 4796) | *Advancement* p. 771 — same definition verbatim |
| Cadent ≡ falling/withdrawing (2421, 4774) | *Cadent* p. 774, *Falling* p. 780, *Remote* p. 790 |
| Eastern (2) = outside the rays and visible (4823) | *Eastern and western* sense (2), p. 778 |
| Domain (811) | *Domain* p. 777 / *Hayyiz* p. 782 |

⚠ **Do not simply swap the citations.** The Domain case at 811 is the one to be careful with: the
course glossary and Sahl's glossary do **not** say the same thing — Sahl's separates *halb* (sect +
hemisphere) from *hayyiz/domain* (halb + own-gender sign), which is exactly the distinction the
`DOMAIN_RULE_OPTIONS` switch at `app.py:536` exists to expose. Adding Sahl's glossary there should
*add a second witness*, not replace the first.

---

# Part B — C-19, Sahl's worked question chart

**Ready to build; no blockers.** I re-read Figures 33 and 34 directly and confirm the brief's three
reproductions, plus six more judgments that also hold.

**Chart data** — Questions Ch. 1, 54, verbatim:

> "the Ascendant was **Gemini, 20°**; and the Midheaven **Pisces, the first degree**; and the Sun in
> **Cancer, 12°**; and the Moon in **Virgo, 17°**; and Mercury in **Gemini, 27°**; and Mars in
> **Taurus, 8°**; and Venus in **Leo, 3°**; and Jupiter in **Pisces, in 20°, stationing toward
> retrogradation**; and Saturn in **Gemini, in 6°**."

Figure 34's reconstruction: **5 July 824 AD (Julian), 3:18:10 AM LMT −02:57:40, Baghdad
44e25'/33n21, geocentric, "Sassanian" zodiac, whole signs.**

**The nine judgments to assert** (from `01_on_questions.md` §2b) — the brief's three plus six:

| ¶ | Judgment |
|---|---|
| 56 | Mercury, lord of the Ascendant, **in the Ascendant at the end of the sign** |
| 56 | Jupiter, lord of the sought matter, **in the Midheaven** |
| 56 | Lord of the Ascendant **separated from** the lord of the sought matter ✔ *brief* |
| 57 | Moon **in the stake of the earth** ✔ *brief* |
| 57 | Moon **connecting with Jupiter from an opposition**, 3° from exact ✔ *brief* |
| 61 | Jupiter **stationing toward retrogradation** |
| 63 | Mercury **shifting from his own house into the house of assets** |
| 63 | On leaving, Mercury **connects with Mars, who does not accept him** — fn. 27: from Cancer, **Mars's fall** |
| 65 | Jupiter **is with the Tail** |

⚠ **¶65 needs a decision the brief does not raise.** The node positions are **not among the nine
longitudes Sahl lists**. They come only from Figure 34's recomputation (☋ 25°♓46' with Jupiter
20°♓32'). Two consequences:

1. It is the strongest evidence that Dykes's date reconstruction is right — a claim in the text
   verified by data the text does not supply.
2. But asserting it in a fixture means **either** hardcoding a node longitude that is not in the
   prose, **or** recomputing from the date — which the brief rightly forbids.

**Recommendation: assert ¶65 as a same-sign check against a hardcoded ☋ 25°♓46' sourced explicitly
to Figure 34, with a comment saying it is figure-derived, not prose-derived.** Or omit it. Do not
recompute.

⚠ **A second, newer complication the brief could not have known:** HEAD `980330b` is "Chart: true
node instead of mean node." Figure 34's ☋ is whatever Dykes's software produced; if the fixture ever
*does* recompute, true-vs-mean now matters. Another reason to hardcode.

**Venus negative control** — keep it, exactly as the brief says. MS gives Venus ♌3°, the
recomputation ♌9°06'; Sahl draws **no** judgment from Venus. The control should assert that no
Venus-dependent assertion exists, so nobody adds one later.

---

# Part C — Spear-bearing

## C.0 Headline: the brief's framing is wrong on two points, and the second one blocks its deliverable

### ⚠ C.0.1 "The doctrine is distributed, not chaptered" — it *is* chaptered

`on_nativities.md:3597` is not a stray mention. It is a **chapter title**:

> **Chapter [2.5]: On the right-sidedness of the planets
> (& it is what is called the "spear-bearing" of the planets):
> what it indicates of good fortune & assets**

Chapter 2.5 runs ¶1–9 and gives a complete, computable, two-grade definition with a sect
preference, per-planet significations, and an intensifier. The brief's line reference points at the
chapter's own title without recognising it as one.

### ⚠ C.0.2 There are **three** definitions in this one work, and two of them are incompatible

This is the finding that matters, and it is why the brief's deliverable #3 cannot be built as
specified.

| # | Location | Criterion | Provenance |
|---|---|---|---|
| **I** | **Ch. 2.5, 2–3** | **square or sextile**, both in exaltation/house/share, **each casting rays on the other**; lesser grade = same sect | fn. 121: "a version of the **first definition of Antiochus**" |
| **II** | **Ch. 10.2.1, 10–15** | planets **eastern from the Sun and western from the Moon** | fn. 139: cf. ***Tet.* IV.3** — Ptolemy |
| **III** | **Ch. 10.2.7, 1–26** | the seven worked examples | fn. 121: "must derive from a **Persian source**" |

**Definition I requires an aspect. Definition III explicitly excludes one.** Example #1:

> "these two planets come to be in a position of paying honor from the Sun, **without a connection
> from him to them**, and without their position being at sunrise except that they are **eastern
> from him**." — Ch. 10.2.7, 3

And Example #4 states II in so many words:

> "Jupiter in his **easternization from the Sun**, and Saturn and Mercury in their **westernization
> from the Moon**." — Ch. 10.2.7, 14

**All seven examples test definition II/III. None tests definition I.** So "commit the seven charts
as fixtures" silently commits to the Ptolemaic/Persian reading and leaves the dedicated chapter's
definition untested — the opposite of what the brief intends by "the examples confirm the reading."

### ✅ C.0.3 Good news: fn. 213's uncertainty is probably resolvable, from inside the same work

The brief flags fn. 213 at `:6091` as the editor's open doubt about the Sun/Moon asymmetry:

> "I believe this means different things for the Sun and Moon. For the Sun and Mars, it probably
> means that Mars is in an earlier degree than the Sun ('behind' him zodiacally)… For the Moon and
> Saturn, it probably means that Saturn is in a later degree than the Moon…"

Ch. 10.2.1, 10 states that asymmetry **flatly, in the same direction, in the same work**:

> "the planets formed an honor-guard for them (**and that is if the planets were eastern from the
> Sun and western from the Moon**)"

Dykes does not make this cross-reference himself. I am **not** calling it settled — fn. 213 comments
on a different passage (a chapter on parents) and its uncertainty is about what "behind" means
*there*. But it is a strong lead, and the reread artifact should record it as such rather than
inheriting the brief's "preserve the uncertainty; do not resolve it silently" as if nothing bore
on it.

## C.1 ⚠ Only three of the seven charts are usable as fixtures

The brief says "Figures 64-70 give positions; each is an example of the configuration, so each is a
positive case." I read all seven passages and two of the figures directly. That is not so.

| Ex | Data | Verdict |
|---|---|---|
| **#1** | ASC ♍6, ☽♍6, ♀♍21, ☿♎4. **Sun's degree missing in prose *and* in Figure 64** — I checked the image; the ☉ glyph is drawn with no number. fn. 190: "we do not even know the position of the Sun, the chart is impossible to date" | ⚠ **Moon/Venus leg only** |
| **#2** | ASC ♈19. **Sun "in Aries", degree not given.** Mars degree disputed (fn. 195: M reads 27 or 29) | ⚠ **Partial** |
| **#3** | ♄♍19, ☉♏26. **ASC inferred by Dykes** (fn. 199 "it does mean that Libra is rising"; fn. 198 narrows to the last 7° of Libra). Lot position also inferred | ⚠ **Sun/Saturn leg only** |
| **#4** | ☉♒25, ♃♒0–1, ASC ♉9, ☽♓9, ☿♓12, ♄♈13 | ⚠ **fn. 203: astronomically impossible at any latitude.** Figure 67 faithfully reproduces the impossibility |
| **#5** | ☉♍14, ♀♌26, ASC ♉3 | ✅ complete — but fn. 206 "a connection with whom?" and "the Sun is not angular by sign, nor… by dynamic division" |
| **#6** | ASC ♈3, ☉♒16 (M: 18), ☿♒5 | ✅ complete — but see C.2 |
| **#7** | ASC ♐9, ☉♈8, ☽♐2, ♃♑14, ♀♈2 | ✅ **best of the seven.** fn. 209 notes only Venus can truly be easternizing |

**Recommended: commit #5, #6, #7 as positives, and #1's Moon/Venus leg. Do not commit #2, #3, #4.**
Record why in the test file so nobody "fixes" the omission later — especially #4, where the
temptation to correct the impossible chart is exactly the failure mode this project has been
guarding against.

## C.2 ⚠ A checkable discrepancy in Example #6

> "look at Mercury, how he is in the honor guard of the Sun and his right side, **in his own bound**,
> eastern" — Ch. 10.2.7, 22

Mercury is at **Aquarius 5°**. I queried the engine: `get_essential_rulers(305.0)` returns
`term: Venus`. So under the app's bound table Aquarius 5° is **Venus's** bound, not Mercury's.

Three possible explanations and I cannot choose between them from the corpus:
1. Sahl's source uses a different bound system than the engine's;
2. the degree is corrupt (M already disputes the Sun's degree in this example);
3. "his own bound" means something looser than the term lord.

**Must be resolved before #6 is committed as a fixture**, or the bound clause must be excluded from
what the fixture asserts.

## C.3 What Chapter 2.5 actually says — the definition the brief never saw

> "**1** You should not neglect the knowledge of the right-sidedness of one of the planets toward
> another, for it is **the summit of their good fortune** in their indication, and especially if the
> **diurnal planets were right-siding by day, and the nocturnal ones by night**."

> "**2** If you found one of the two planets **in square or sextile** to its companion, and they were
> both **in their exaltations or their houses**, or one of them was in its exaltation and the other
> in its house, or one of its shares, **and each one of the two was casting rays upon its
> companion**, then that is a **strong** right-sidedness. **3** And if they were not in their houses
> nor exaltations, but they were **both of the sect of the day or the sect of the night**, then that
> is **also called right-sidedness (though it is below** [the first version])."

Per-planet significations at ¶4–8 (Mars, Venus, Mercury, Jupiter, Saturn — **no Sun or Moon entry**,
since they are the ones being right-sided). Intensifier at ¶9:

> "if with that the **glowing ones were in the stakes**, and the **fortunes were in their
> right-sidedness**, then that is **more powerful and preferable**… and if that was reversed, it
> indicates **the middle** of what I have mentioned."

Two features worth flagging for any implementation:

- **Square or sextile only.** Not trine, not conjunction, not opposition. Unusual and specific.
- **The sect condition appears twice and differently**: ¶1 as a *preference* ("especially if"), ¶3 as
  the *defining criterion* of the lesser grade. Those are not the same claim.

## C.4 Ptolemy's version — a four-grade eminence ladder the brief does not mention

Ch. 10.2.1, 10–15 (cf. *Tet.* IV.3) grades outcomes, not just presence:

| Condition | Outcome |
|---|---|
| Luminaries in male signs, in stakes, in own domain + honour-guard (eastern from ☉ / western from ☽); the eastern planets also in stakes | "an **elevated king**" → "a **mighty king**" (¶10) |
| ☉ male sign, ☽ female sign, one in a stake | "a **commander** or one of the chiefs" (¶12) |
| No honour-guard and no aspect | "a **noble man having rank**" (¶13) |
| Luminaries *not* in stakes but the honour-guard *is*, not looking | "**revered, known in the cities**" (¶14) |
| Neither in stakes, not looking | "**below that**… not known, weak with toil" (¶15) |

⚠ fn. 141 corrects the text against Ptolemy: *"Actually, in this example Ptolemy does allow the
spear-bearing planets to be either in a stake **or configured to it**."* An implementation that
follows the printed sentence will be stricter than Ptolemy.

## C.5 Further locations the brief's list omits

Beyond its four, I found: `:12005` (fn. 129 identifying "honour-guard" as spear-bearing and
cross-referencing the Glossary and Ch. 10.2.7), `:12027` (the **"[Spear-bearing according to
Ptolemy]"** heading), `:12047` (fn. 141), and `:12232` (fn. 168: "This **seems to be a version of**
spear-bearing" — a fifth, hedged instance). The doctrine touches **at least eight** places.

---

# Recommendation on implementing spear-bearing

**I agree with the brief's instruction not to implement, and the evidence is stronger against it
than the brief anticipated.** Not a default — a conclusion:

1. **Three definitions, two demonstrably incompatible.** Choosing among them is a doctrinal decision
   with no textual tiebreak. Ch. 2.5 is the dedicated chapter; Ch. 10.2.1 is Ptolemy by name; the
   seven examples follow neither *exactly* but sit with Ptolemy. Sahl transmits all three without
   harmonising them.
2. **The examples cannot arbitrate**, because they only ever exercise one of the three.
3. **Four of the seven charts are defective as evidence** — a missing Sun (×2), an inferred
   Ascendant, and one astronomically impossible chart.
4. The brief's own reasons stand: the course material has not been reached, and the implementation
   should be able to answer the course's worked problems.

**What I would do differently from the brief:** its deliverable #3 — "the seven spear-bearing charts
as fixtures" — is not achievable as written. I recommend **three complete fixtures plus one partial
leg**, with the four exclusions documented in the test file.

---

# Plan

Sequenced so each step is independently committable and the suite stays green. Estimated sizes are
for a session that implements them, not this one.

## Stage 1 — Tier 1 (small, no doctrine)

| # | Step | Files | Risk |
|---|---|---|---|
| 1.1 | **A3 first**: remove the stale marker at `abu_mashar_book_vii.md:1790`. Coordinate with the OCR project — the file is not this repo's | corpus | Low, but cross-repo |
| 1.2 | **A1**: rewrite the VII.7 coverage entry at `app.py:4218` | `app.py` | Low |
| 1.3 | **A2**: widen `ABSENCE_CLAIM`, search `passage + desc`, and replace `CORPUS_BOOKS` with a check against `consolidated_texts/`. Land this **with** 1.2 so the test would have failed before the fix | `tests/test_prose_counts.py` | Medium — a corpus-grepping test needs the corpus path resolvable in CI |
| 1.4 | **A4/C-02**: extend the advancing comment at `app.py:4352–4400` | `app.py` | None — comment only |
| 1.5 | **A5**: add `sahl_glossary.md` citations at the six sites; **add**, do not replace, at line 811 | `app.py` | Low |

⚠ **1.3 has a dependency the brief does not flag.** A test that greps the corpus needs
`consolidated_texts/` present. It sits on the Desktop, outside the repo, and CI runs without it
(`3d741ab` "Run the suite in CI"). Either vendor a manifest of chapter headings into the repo, or
skip the test when the corpus is absent — and if you skip, the test will not protect CI, which is
where the regression would recur.

## Stage 2 — Part B, the worked question fixture

| # | Step |
|---|---|
| 2.1 | Add `SAHL_AUTHORITY` positions from Ch. 1, 54 as literals, with the ¶54 quote in a comment |
| 2.2 | Assert the seven prose-derived judgments |
| 2.3 | Decide ¶65 (Jupiter with the Tail): hardcode ☋ 25°♓46' sourced to Figure 34, or omit. **Do not recompute** |
| 2.4 | Add the Venus negative control asserting no Venus-dependent assertion exists |
| 2.5 | Comment: the frame is Sassanian; positions are inputs, never recomputed from the date |

## Stage 3 — Part C, the reread (the real job)

| # | Step | Note |
|---|---|---|
| 3.1 | `synthesis/01_on_nativities.md` — the Phase 1 artifact, ~135 subchapters | Largest single piece |
| 3.2 | Spear-bearing section: **three definitions side by side**, not one; C.0.2's incompatibility stated; C.0.3's lead recorded as a lead |
| 3.3 | `synthesis/05_on_nativities_citation_audit.md` — see the method below |
| 3.4 | Fixtures for examples **#5, #6, #7** + #1's Moon/Venus leg; near-miss controls; the four exclusions documented |
| 3.5 | Resolve C.2 (Mercury's bound in #6) before 3.4, or drop that clause |
| 3.6 | Implementation proposal — **not** an implementation |

### The citation-audit method — and a warning about automating it

I attempted the audit mechanically to test the approach. **It does not automate cleanly**, and the
plan should budget for hand work.

What I measured: **85 lines** in `app.py` mention *On Nativities*; **79** carry a chapter-level
citation across **30 distinct chapters** (most-cited: 1.22 ×19, 1.23 ×6, 1.18 ×6, 7.1 ×5).

Three traps, all of which produced false alarms on my first pass:

1. **Three degree encodings.** The corpus renders degrees as `5°`, as LaTeX `$5^\circ$`, and as
   `$\frac{1}{2}$` for fractions. `app.py` writes "5 degrees". Normalisation must handle all of them
   — this alone produced four spurious "misses."
2. **`app.py` mixes four kinds of quoted string** in the same syntax: verbatim source quotations,
   close paraphrase, the app's own editorial prose, and UI captions. A regex cannot tell them apart;
   of 158 candidate spans, most "misses" were the app's own writing.
3. **Emphasis and ellipsis.** Quotations carry ALL-CAPS emphasis and `...` elisions that must be
   stripped and split before matching.

**Result of the sample I did run — and this is the honest headline: I found no falsified
*On Nativities* citation.** Roughly a dozen hand-checks, chosen as the highest-risk-looking:

| Checked | Verdict |
|---|---|
| `app.py:3463` — 1.18, 19, five-degree rule "and likewise in all of the houses" | ✅ **verbatim**, incl. the clause |
| `app.py:4286` / `5461` — Aphorism #44, ¶87–88 | ✅ verbatim (my checker broke on `5°`) |
| `app.py:4826` / `4839` — 1.22, 1, six degrees / nine-day allowance | ✅ verbatim |
| `app.py:4829` — "Mars at 15 degrees (1.22, 3 **and its note**)" | ✅ **correct, and better than my reading.** The text says Mars 18°; fn. 174 concludes "he is **considered eastern at 15°** and then actually emerges at 18°." The code's own comment says "Mars's 15 is **Dykes' inference at 1.22 fn. 174, not text**" |
| `app.py:3893` — Lot formula, 1.37 | ✅ both halves verbatim |
| `app.py:4402` — advancement, Introduction Ch. 3, 4 | ✅ verbatim (in `sahl_introduction_ch3.md`, correctly cited) |

The `4829` case is worth dwelling on: I suspected a defect, and the code was **more careful than I
was** — it had already separated Sahl's text from Dykes's inference and labelled which was which.

**This is a sample of roughly 15% of the citation surface and it should not be read as a clean bill
of health.** But it does change the prior: the brief expects the audit to find CODE-01 defects, and
the sample suggests the *On Nativities* citations are in better shape than that. Budget for the
audit as verification, not as excavation.

---

# What I could not verify

- **The suite.** The brief says 713 tests, ~110 s, green. **I did not run it** — this pass changed
  nothing, so there was nothing to regress, and running it proves nothing about a report. Any
  implementation session must establish the green baseline first, and on `980330b`, not `9b76b45`.
- **`app.py:2421`'s glossary reference.** "Glossary makes the same equivalence under Cadent" does not
  say *which* glossary. I classified it as the course glossary by context; it needs a human look.
- **Example #6's bound claim** (C.2) — unresolved between three explanations.
- **Whether Ch. 2.5's definition has any worked example anywhere in the corpus.** I found none, but I
  searched `on_nativities.md` for spear-bearing vocabulary, not for unlabelled instances of the
  square/sextile-plus-dignity configuration. An exhaustive check is part of Stage 3.
- **The other 85% of the citation surface.**
- **Course material.** The brief notes the course spends more than one lesson on spear-bearing and
  that material has not been reached. It is in `/home/apothic/Documents/TNAC/`; I did not open it
  this pass, and it may well arbitrate between the three definitions — which is a further reason to
  defer implementation.

# Where the current text does *not* say what a comment claims

**Nothing found.** This is the brief's stated most-valuable outcome, and the honest answer from this
pass is that the sample turned up no such case. The one candidate (`app.py:4829`, Mars 15° vs the
text's 18°) resolved in the code's favour on reading footnote 174.

The falsehood that *does* exist — A1 — is not a misreading of *On Nativities* at all. It is a
faithful transcription of a **stale marker still sitting in the corpus file** (A3). That is a
different failure mode from CODE-01, and it argues for a different guard: not closer reading, but a
test that compares coverage claims against the corpus (Stage 1.3).
