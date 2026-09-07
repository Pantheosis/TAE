# Phase 2 — reconciliation against `app.py`

Every doctrine from the Phase 1 artifacts, classified against what the code does and claims.
`app.py` at 7,260 lines; line numbers as of 2026-09-07 (HEAD `82b2758`).

Classes, per the brief:

1. **Newly available** — in the corpus now, not implemented, not previously known.
2. **Contradicts a current implementation** — the code does what the text does not support.
3. **Contradicts a current claim** — a comment, tooltip, coverage entry or test asserts something
   the text does not say. User-facing; the CODE-01 class.
4. **Confirms** — the code matches. Recorded so this ground is not audited a fifth time.
5. **Still genuinely absent.**

---

## Class 3 — Contradicts a current claim (highest priority; user-facing)

### 3.1 `NOT_IMPLEMENTED_COVERAGE` says Abū Ma'shar VII.7 was never photographed. It is now complete.

`app.py:4150`:

> `("Abu Ma'shar VII.7", "The casting of rays according to Ptolemy. The chapter begins on a page not photographed.")`

**False.** VII.7 is present in full at `abu_mashar_book_vii.md:1812–1857` — 22 numbered sentences,
pp. 485–487, footnotes 247–253, added 2026-09-07.

This is the **second** falsified coverage entry on this project (after the equal-ascension one), and
it is displayed to users as a statement about what the sources contain. The entry needs rewriting:
the chapter *is* in the corpus, and what is actually missing is the **tables** it depends on
(hourly times from the *Almagest*, and the ascensions↔degrees inverse tables — see
`01_abu_mashar_vii_7_to_9.md` §B7), all of which are computable.

**Fixture:** a test asserting that no `NOT_IMPLEMENTED_COVERAGE` entry claims a chapter is
unphotographed when a page-marker range for it exists in the corpus files. Positive: VII.7 now
fails such a test. Negative control: the VII.6, 13/36 entry ("no table for them in this corpus"),
which I checked and which **remains true** — the corpus has no masculine/feminine degree table.

### 3.2 The advancing coverage entry is now incomplete, not wrong

`app.py:4152–4156` records `ADVANCING_BY_QUADRANT_FIG90` as Abū Ma'shar's quadrant sense
(ASC→MC, DSC→IC), "distinct from Sahl 83, which is his own Ch.3, 4." Both halves of that are
**correct** and the glossary independently confirms both senses exist
(`01_sahl_glossary.md` §2c).

But *On Times* Ch. 1, 10–14 — a file never read against the code — adds a **third** position, and
attributes the first two:

- The quadrant scheme is "**according to the statement of the ancients**" (¶11).
- Māshā'allāh "**differs from them**" and divides by **hemisphere** — IC→ASC→MC quick, MC→DSC→IC
  slow (¶12–13).
- **Sahl endorses Māshā'allāh**: "that is the closest of the two statements" (¶14).

Figure 44 shows both wheels and agrees with the prose (verified by reading the image).

So the comment's framing — quadrants = Abū Ma'shar, stakes/succedents = Sahl — is **true but
partial**. Sahl knew the quadrant division, called it the ancients', and preferred a third one.
Caveat: *On Times* Ch. 1's subject is quickness of **timing**, not strength, so it is not certain
the same division governs advancing-as-strength. That caveat is exactly why this is a comment fix
and not a behaviour change.

**Fixture:** none needed — this is a documentation change. The negative control is that no computed
value moves.

### 3.3 The five-degree rule's provenance is fine; the "course glossary" citation now has a better source

`app.py:4728` and the note at `app.py:7026` justify reading advancement dynamically by citing
"the course glossary" (the *TNAC Course Glossary*, external to this corpus). **Sahl's own volume now
contains a glossary saying the same thing**, and it is a corpus document:

> "**Advancement, advancing** … Refers to being (1) **dynamically angular or succeedent, i.e.
> moving by primary motion toward an axial degree**." — `sahl_glossary.md` p. 771

Not a contradiction — a citation upgrade from an external course document to the primary volume's
own apparatus. Low effort, improves every tooltip that carries it.

---

## Class 2 — Contradicts a current implementation

### 2.1 ⚠ Advancement is scored as a flat good; Sahl matches it to the nature of the matter

`app.py:4722–4747` scores testimony (83) "Advancing" as a positive label, unconditionally, with the
five-degree carryover. That is right for *Introduction* Ch. 3, 4 read alone.

But *On Questions* Ch. 1, 18–20 qualifies it:

> "if you were asked about a sought matter, and it was **in the nature of advancing**, then look …
> [at] the **advancement of the one accepting** … **20** But if the question was about **the nature
> of retreating, such as travel, moving, a detained person's exit from his prison, and being
> released from sorrows**, then look for these matters **from the place of retreat and withdrawal**."

**Retreat is not a defect when the matter sought is itself a departure.**

**How far this reaches is a real question and I am not overstating it.** ¶18–20 is framed for
questions ("if you were asked"), and the engine is natal. The doctrine is *general in form* —
nothing in it depends on the chart being a question chart — but Sahl states it in a horary setting
and does not restate it natally. So this is **not** a demonstrated error in a natal score; it is a
demonstrated qualification of the underlying principle, from a text the code has never read.

**Recommended handling: a note, not a rescore.** Surface the qualification where advancement is
explained, and leave the score alone unless the user wants a topical modifier.

**Fixture if it were implemented:** positive — a planet withdrawing from the 9th (travel) should not
be penalised for a travel significator; negative control — the same planet withdrawing should still
be penalised where the topic is acquisition (2nd), since ¶18 names advancement for those.

### 2.2 ⚠ Benefic/malefic is absolute in the scoring; Sahl says it is chart-relative

The scoring treats the infortunes as harmful per se — e.g. `app.py:4877–4892`, "Connecting with the
infortunes from an assembly, opposition, square (94)".

*On Choices* Ch. 1, 12:

> "And perhaps you have seen the indicator being connected to an infortune from a square, assembly,
> or opposition, and **someone had gains**: **that infortune was good for him, because the infortunes
> are perhaps more fitting for him**, since [one] may be **the lord of the original Ascendant**…"

(fn. 8: "original" = natal.)

So a malefic ruling the native's own Ascendant is *fitting* for that native.

**But this is genuinely contested inside Sahl's own text.** Four sentences later, Ch. 1, 16–17 gives
the flat version: "the infortunes are **unjust in nature** … there is **no escape** from their
injustice." I recorded this as an internal disagreement in
`01_on_choices.md` §1a and I am not resolving it.

**Classification: interpretive choice, not a correction.** If implemented, it belongs behind a
switch with both readings named — which is how this project has handled comparable splits (the Moon
rays 12°/15° switch at `app.py:6433`, the domain rule at `app.py:536`).

### 2.3 Nothing else in Phase 1 contradicts an implementation

I looked specifically for contradictions and found none beyond the two above. Where the new texts
touch implemented machinery, they **agree** with it — see Class 4, which is unusually long, and
which is the more important result of this pass.

---

## Class 4 — Confirms (the code is already right)

These matter: several are places where I *expected* to find an error and did not.

### 4.1 ✅ Cazimi — the code already splits Abū Ma'shar's 16' from Sahl's one degree

The glossary attributes the strict reading to Sahl by name
(`sahl_glossary.md` p. 783, and `01_sahl_glossary.md` §1b). The code got there first, and cites
better sources than the glossary does:

- `app.py:634–640` — `CAZIMI_ORB = 16.0/60.0`, with the comment naming Abū Ma'shar's derivation from
  the Sun's 32' diameter (VII.2, 7–9), al-Bīrūnī's agreement, **and** Sahl's dissent
  ("*Sahl instead says 'with him in one degree' (The Introduction Ch.3, 87; Fifty Aphorisms #40,
  79), which is measured separately where Sahl's own testimony is scored*").
- `app.py:4787–4794` — testimony (87) measures Sahl's one-degree window independently rather than
  reusing the 16' flag.

The comment also correctly rejects the 17' Lilly-era value. **No change.**

One residual, minor: `app.py:4793` implements "in one degree" as `elongation ≤ 1.0°`. Sahl's phrase
"with him in one degree" could equally mean *within the same zodiacal degree* (⌊lon⌋ = ⌊sun⌋), which
is not the same set. The glossary's wording — "in the **same degree** as the Sun" — leans slightly
toward the latter. **Interpretive choice, low impact**; recorded, not recommended for change.

### 4.2 ✅ Solar phase uses Abū Ma'shar's per-planet values, not the glossary's generic band

`app.py:606–627`. `SOLAR_BURNED_ORB` and `SOLAR_RAYS_ORB` are per-planet dictionaries sourced to
VII.2, with the Moon's disputed 12°/15° exposed as a switch (`app.py:6433`) because Sahl's
*On Nativities* 1.19, 6 disagrees with Abū Ma'shar VII.2, 61.

The glossary's generic scheme — burned 1°–7.5°, under the rays 7.5°–15° (p. 793) — is explicitly
labelled by Dykes as the **later** simplification. The code prefers the primary per-planet table.
That is the right call under this project's source-fidelity policy. **No change.**

### 4.3 ✅ Assembly by bodies, not by a flat 12° — and the 12°/15° "conflict" is not one

I flagged this as a possible conflict and it dissolved on reading the primary texts
(`01_sahl_glossary.md` §1a, `01_abu_mashar_vii_7_to_9.md` §E):

- **Abū Ma'shar VII.4, 3** himself gives 15° as an *intensity* band over a same-sign assembly — so
  the glossary's "more intensely if within 15°" is a faithful précis of him, not a claim about Sahl.
- **Sahl's 12°** (*Introduction* Ch. 2, 51) is a **derived summary** of his own per-planet body table
  at Ch. 3, 12–18 (Sun 15°, Moon 12°, Saturn/Jupiter 9°, Mars 8°, Venus/Mercury 7° each side).
- The two authors **agree** on body sizes: AM VII.4, 7's "a little under 9°" for Saturn matches Sahl
  Ch. 3, 15's 9°.

The code implements Sahl by asymmetric body overlap and Abū Ma'shar by the flat 15°/12° distances,
and says so in the UI note at `app.py:7192–7198`. **This is more faithful than a flat 12° would
have been.** No change.

### 4.4 ✅ Aversion

`app.py:878` — `AVERSION_SIGN_COUNTS = {1, 5}`, applied to `min(raw, 12-raw)`, i.e. the 2nd/12th and
6th/8th. Matches *Introduction* Ch. 2, 60 exactly ("the second sign, the sixth sign, the eighth
sign, and the twelfth sign, and what is equivalent to these four"), the glossary's *Aversion* entry
(p. 773), and **Figure 8**, which I read directly: Jupiter in Sagittarius, grey = Capricorn, Taurus,
Cancer, Scorpio = the 2nd, 6th, 8th, 12th. Three sources plus a worked figure. **No change.**

### 4.5 ✅ The antiscia pair list is still correctly *not* completed

`app.py:4133–4140`'s coverage entry says the five enumerated pairs stand and Aquarius–Scorpio is not
added, "*Adding them would be inference from the family, not from the text in hand.*"

The glossary now supplies the **degree-wise antiscia formula** ("10° Cancer has 20° Gemini as its
antiscion", p. 772) — and `_counterpart_degree` at `app.py:1771` implements exactly that mirror
(`30.0 - (lon % 30.0)`). **Having the formula is not permission to add the sixth sign pair**: the
formula is the glossary's cross-author vocabulary; the pair list is a claim about what Abū Ma'shar
enumerates. The coverage entry stays correct as written. **No change** — and this is worth stating
plainly, because the glossary entry is exactly the kind of thing that invites the completion the
brief warns against.

### 4.6 ✅ Overcoming/superiority is coherent across three sources (though unimplemented — see 1.4)

*Introduction* Ch. 2, 59 ("the second sextile is stronger than the first … called 'superiority'"),
the glossary's *Overcoming* (11th/10th/9th sign, p. 787) and *Right/left* with its worked Capricorn
example (p. 791) all describe one relation consistently. Dykes's fn. 46 warns Sahl violates his own
first/second terminology in *Scito* Ch. 95 — a work outside this corpus, so uncheckable.

### 4.7 ✅ Lesser years are now doubly attested

Sahl's Figure 47 (p. 238) and Abū Ma'shar's Figure 146 (p. 487) give **identical** lesser years for
all seven planets: ♄30 ♃12 ♂15 ☉19 ♀8 ☿20 ☽25. Two authors, two volumes, two separate photo batches.
Deferred in use, but the values are beyond doubt.

### 4.8 ✅ Figure 146 verified by its own checksum

AM VII.8, 3 states the *fardār* total: "that is **75 years**." 10+8+13+9+11+12+7+3+2 = 75. ✓ And all
five columns match the prose at ¶3, 5, 6, 7, 8. The repaired Figure 146 is sound.

---

## Class 1 — Newly available

Not implemented, not previously known, present in the corpus now.

### 1.1 Sahl's sign categories — an entire family, zero code presence

`grep -ci` over `app.py`: **crooked** 0, **four-foot** 0, **voice** 0, **barren/fertile** 0,
**via combusta / burnt** 0. None of *Introduction* Ch. 1's categories are implemented.

| Category | Source | Status |
|---|---|---|
| Crooked / straight, **latitude-dependent** | Intro Ch. 1, 5–6 + Figure 3 + glossary p. 776 | Attested twice for the latitude inversion. Clean to implement. |
| Four-footed | Intro Ch. 1, 13 **vs** Nat. 1.38, 1 | ⚠ **Sahl contradicts Sahl** (Leo vs Capricorn). Must pick a work and say which. |
| Voice signs | Intro Ch. 1, 20–22 **vs** Nat. 1.38, 25–28 | ⚠ **Two incompatible schemes**; Virgo moves from bottom class to top. |
| Barren / fertile | Intro Ch. 1, 23–24 **vs** Nat. 1.38, 14–17 | Fertile agrees; barren disagrees (Aries vs Sagittarius). |
| Dark signs (Libra, Capricorn) | Intro Ch. 1, 18 **and** Nat. 1.38, 8 | ✅ Agrees in both. Safe. |
| Burned place (end Libra – beginning Scorpio) | Intro Ch. 1, 19 **and** Nat. 1.38, 9 | ✅ Agrees in both — but **no degrees** in Sahl; the glossary gives two competing spans (p. 774). |
| Triplicity humors and directions | Intro Ch. 1, 34–41 + Fig. 4 | Lords already implemented; **humors and directions are not**. |

**The two that agree in both works (dark signs, burned place) are the safe ones.** The three that
disagree are the interesting ones and none should be implemented as a merged list.

Note this is **not idle**: Appendix B ¶7 and ¶33 both branch on the four-footed list
(`01_appendices_a_and_b.md` §B3), so the contradiction has a downstream consumer inside the corpus.

### 1.2 Sahl gives at least three good-place schemes; the code implements one

This is the most substantive structural finding of the pass.

| Scheme | Places | Source | In code? |
|---|---|---|---|
| **8-place** (power/presence) | 1, 2, 4, 5, 7, 8, 10, 11 | Intro Ch. 2, 31–36 + **Figure 5** | ✗ |
| **7-place, ranked** (goodness) | **1 > 10 > 7 > 4 > 11 > 9 > 5**, then 3, 2 | Intro Ch. 2, 37–45 + **Figures 6, 7** | ✗ |
| **Six "excellent places"** | 1, 4, 5, 7, 10, 11 | Intro Ch. 3, 78 | ✅ `EXCELLENT_PLACES`, `app.py:4618` |
| (glossary hedge) | possibly only 1, 10, 11 | Glossary p. 780, *Excellent place* | ✗ |

`app.py:4611–4618`'s comment derives the six correctly — stakes and succedents **intersected with**
the places that look at the Ascendant, which drops the 2nd and 8th. **That derivation is right.**

What is new is that Ch. 2 gives two *further* schemes, one of them **ranked**, and they are not the
same set: the 7-place system **includes the 9th** (justified by the Sun's joy) which Ch. 3, 78's six
excludes, and it **excludes** the 5th's peer the 2nd which Ch. 2's own 8-place includes.

And the glossary explains *why* the 7- and 8-place schemes differ without either being wrong:

> "The **seven-place** scheme … suggests that these places are advantageous **for the *native***…
> The **eight-place** scheme … suggesting places which are stimulating and advantageous **for a
> planet *in itself***." — Glossary p. 771

Different questions, not competing answers. **An engine holding one house-strength number is
silently answering one of them.** Figures 5 and 6 confirm both sets by shading; I read both.

⚠ **And the 7-place ranking is partly Dykes's reconstruction.** fn. 42: ¶42–43's order is
"a construction from **H** and **L** … and **B**"; **B** has 5 then 9, **H/L** have 9 then 5, and
Dykes prints H/L's order plus B's Sun's-joy note. **Interpretive choice**, alternatives named.

### 1.3 The joys — four are in the corpus, two of them weakly

`grep -c "joy"` in `app.py`: **0**. Yet the joys are the stated *reason* for the 7-place ranking:
9th/Sun (Ch. 2, 42), 3rd/Moon (¶45), 6th/Mars (¶48), 12th/Saturn (¶49).

⚠ **Two of the four are textually weak**: the 9th/Sun joy exists **only in manuscript B** (fn. 42),
and the 6th/Mars joy is **supplied from the Latin**, printed inside `⟨ ⟩` (fn. 43). Mercury's and
Venus's joys are **not in this chapter at all**. So the corpus supports a **four**-joy scheme, two
securely — never a complete seven. Do not present one.

### 1.4 Overcoming, superiority and decimation

Not implemented (`grep -ci overcom|superiority|decimat` = 0), though the aspect machinery to compute
it exists. Well attested (§4.6). Adds: dexter/sinister distinction on every aspect, the "second is
stronger" grading, and **decimation** as the singled-out 10th-sign case.

### 1.5 Abū Ma'shar VII.7 — the ray-casting algorithm

Complete, with absent-but-computable tables. Full analysis at `01_abu_mashar_vii_7_to_9.md` §B.

Cheapest usable piece by far: **VII.7, 22** — "as for the opposition, [a planet] casts its ray into
the opposition of its sign, **in the same degree and minute**." One sentence, unconditional, needs
no tables.

⚠ Two things must travel with any implementation: the **¶18/¶21 anchor asymmetry** (nearest vs more
distant, unexplained in the source), and the **scope question** — fn. 247 calls this "primary
directions," which is deferred territory (§B8).

### 1.6 Abū Ma'shar VII.9 — planetary natures and significations

Per-planet temperaments (`01_abu_mashar_vii_7_to_9.md` §C2), with three features a plain qualities
table would lose: **Saturn's dual temperament** ("but sometimes it is cooling [and] wet"),
**Mercury's dual nature** (convertible *and* cold-dry in himself), and the **Moon's heat as
derivative** ("incidental… because her glow is from the Sun").

And VII.9, 2 is a caveat that should govern how any of it is displayed:

> "**not everything we state in this chapter** … will be gathered together within a single man …
> according to **the condition of the planet in itself and its condition in the houses of the
> circle**."

### 1.7 Appendix A — ~23 computable natal conditions, zero citations in the code

`01_appendices_a_and_b.md` §A2. Best candidates are the ones whose every term is already computed
elsewhere in the corpus — e.g. ¶49 [S49] (right-siding, spear-bearing, superiority, easternization),
¶39 [S39] (domain + stakes + trine/sextile), ¶14 [S14] (Moon's connection stronger in the 1st or
10th), ¶67 [S66] (Nodes harm the inferiors more than the superiors — a one-line rule).

⚠ **Weaker evidence than the rest of the corpus**: one consulted manuscript, patched from a Latin
centiloquy. And two items must not ship as Sahl: **¶35's detested-connection pairs** are Dykes's
tidier reconstruction over irregular manuscript readings (§A3), and **¶64's meridian/declination
configuration** is undetermined even by its translator (§A5) — that one especially must not be
folded into the antiscia family.

### 1.8 Appendix B — the handing-over matrix

A three-axis lookup (direction of handing over × house the management comes from × benefic/malefic
receiver) plus six general principles (§B2). ⚠ The least secure text in the corpus: **no source
photographs exist anywhere in the project**, five `⟨missing⟩`/`[uncertain]` marks, two "meaning
unclear" footnotes. And it does not partition natal from horary from solar-revolution material.

### 1.9 Smaller newly-available items

- **Tie-break between the lord of the Ascendant and the Moon**: prefer the one in a stake *and*
  looking at the Ascendant (*Questions* Ch. 1, 22). Computable, one line.
- **Intra-quadruplicity gradations** (*Choices* Ch. 2, 5, 8) — ⚠ ¶5 calls Cancer "crooked" against
  the corpus's own rule; Dykes proposes an unsourced fix (fn. 11).
- **Solar-phase period cycle** (*Times* Ch. 1, 17–21 + Fig. 45) — six intervals.
- **Sign-type → time unit** (*Times* Ch. 2 + Fig. 46) — timing; deferred.

---

## Class 5 — Still genuinely absent

| Missing | What would be needed | Where it would live |
|---|---|---|
| **Abū Ma'shar's *On the Revolutions of the Years of Nativities* (PN4)** | A clean OCR. The PDF exists in `~/Downloads`; the one Marker run produced a **0-byte** file. | Unblocks releaser, house-master, distribution, firdaria, solar revolutions |
| **Masculine/feminine degrees** (VII.6, 13, 36) | A degree table. **I checked — the corpus has none.** The coverage entry stays TRUE. | `app.py:4148` |
| **The thirty fixed stars** (Nat. Ch. 2.2) | Positions for Sahl's epoch + precession | `app.py:4171` |
| **Hourly times (*hōriaioi chronoi*)** and the ascensions↔degrees inverse tables | Named by VII.7 as *Almagest* tables; not in the corpus. **Computable from spherical astronomy** | VII.7 |
| **Degree span for the burned place** | Sahl gives none; the glossary gives two competing spans, neither his | Interpretive choice, not a gap to fill |
| **The sixth antiscia pair (Aquarius–Scorpio)** | Abū Ma'shar stops at five. The glossary's formula does **not** supply the pair | Stays absent, deliberately |
| **Mercury's and Venus's joys** | Not in *Introduction* Ch. 2 | Four joys only, two securely |
| **Sahl's *Scito* Ch. 95** | The counterexample Dykes cites against his own first/second aspect definition (fn. 46) | Would settle §4.6's residual |
| **Appendix C, Bibliography, Sahl p. 40** | Decided exclusions, not gaps | `CORPUS_MANIFEST.md` |

---

## Summary counts

| Class | Count | Notes |
|---|---|---|
| 3 — contradicts a claim | **3** | One outright false coverage entry (VII.7); one now-partial comment; one citation upgrade |
| 2 — contradicts an implementation | **2** | Both are **interpretive choices**, not corrections; neither is a demonstrated natal error |
| 4 — confirms | **8** | Including three I expected to be errors and which were not |
| 1 — newly available | **9 groups** | Largest: the sign categories (1.1) and the three house schemes (1.2) |
| 5 — genuinely absent | **9** | PN4 remains the one that changes the plan |

**The headline result of this pass is Class 4, not Class 2.** The corpus roughly doubled and the
code's existing behaviour survived it almost intact — the two Class-2 items are both genuinely
ambiguous doctrine rather than mistakes, and several places where a naive reading of the new
material would suggest a bug (assembly 12° vs 15°, cazimi 16', generic solar-ray bands, the antiscia
sixth pair) turn out to be places where the code already made the more faithful choice.

---
---

# ADDENDUM — the previously-omitted chapters (added after Phase 1 was extended)

The horary/electional bulk of *On Times* (Chs. 4–11), *On Choices* (Chs. 3–13) and *On Questions*
(Chs. 2–18) — ~60,000 words originally out of scope — has now been read. Artifacts:
`01_on_times.md`, `01_on_choices.md`, `01_on_questions.md`, which supersede the earlier combined
filtered file.

**Summary: eight new Class-1 items, two new Class-3 items, one earlier claim of mine corrected, and
no new Class-2 contradictions.** The pattern from the first pass holds — the code's behaviour
survives the new material.

## A3.1 (Class 3) ⚠ My own claim was wrong: the years-granting *procedure* is in the corpus

`01_abu_mashar_vii_7_to_9.md` §D2 said the planetary-years **values** were present but the
**procedure** for granting them was missing and awaited PN4. *On Times* Ch. 4 contains a procedure:

> "**7** Now if the victor was received, or if the releaser was [itself] ruling, then **if the ruler
> was in a stake, eastern, it grants its greater years; or if it was in what follows the stakes, it
> grants its middle years; and if it was falling, it grants its lesser years**." — Times Ch. 4, 7

Angular → greater · succedent → middle · cadent → lesser. Plus the releaser candidate set (¶2–3:
Ascendant, its lord, the luminaries, Lot of Fortune and its lord, the prenatal syzygy, chosen by
victor) and directing "**a year for every degree by the ascensions of the signs in that city**"
(¶4).

**This does not lift the deferral**, and the correction is narrower than it sounds: what is now in
the corpus is the *grant rule* and the *candidate set*, stated for a **question** chart's lifespan.
The natal apparatus — which releaser wins under which sect conditions, the house-master's own
qualification tests, and the revolution techniques that modify the result — is still absent, and
*On Nativities* Ch. 1.20–1.23 remains the `NOT_IMPLEMENTED_COVERAGE` entry it always was.

**Fix:** the artifact statement, and `app.py:4160`'s coverage entry, should say what is missing more
precisely than "the releaser and house-master … and the years granted."

## A3.2 (Class 3) The advancing comment now has a third and fourth attestation

C-02 already records *On Times* Ch. 1, 10–14 (the ancients' quadrants vs Māshā'allāh's hemispheres,
Sahl preferring Māshā'allāh). Reading *On Choices* adds that Sahl **uses** the hemisphere division
operationally, in a second work:

> "treat every pain from the head to the navel when the Moon is in what is between the stake of the
> earth, so **rising up to the Midheaven** … the **highest region of the circle**. **17** … from the
> navel to the bottom of the foot … between the **tenth, declining towards the stake of the earth**
> … the **lowest part of the circle**." — Choices Ch. 6, 16–17

And again at Choices Ch. 6, 30 ("let the lord of the Ascendant be declining from the Midheaven
toward the stake of the earth"). So the rising/descending hemisphere division is not a one-off
remark in a timing chapter. **Strengthens C-02; still comment-only**, since none of these passages
applies the division to *strength*.

## A1.1 (Class 1) ★ A quantified testimony rule with "safe" defined by enumeration

> "**three testimonies** … the lord of the Ascendant, the lord of the sought matter, and the Moon.
> **49** … one of the two is safe, he will attain to **one-third** … **50** … two testimonies …
> **two-thirds**. **51** And if all … were **safe from retrogradation, burning, the infortunes, and
> falling** … **all** of what he sought. **52** And if … they were **received** … it will **add good
> on top of that**." — Questions Ch. 1, 48–52

**Code now:** `grep -ci "one-third|two-thirds"` → **0**.

Two things here the engine does not have: a **fractional outcome scale**, and an **enumerated
definition of "safe"** that is wider than the glossary's (which names only the infortunes —
p. 791 *Safe*, p. 774 *Cleansed*). Sahl's four: retrogradation, burning, the infortunes, falling.

## A1.2 (Class 1) ★ A general dignity ranking that has never been cited

> "And the **triplicity is below the house**, and likewise the **bound below the triplicity**, and
> the **face below the bound**." — Questions Ch. 13, 7

**Code now:** no dignity-strength ordering constant exists (`grep` for `DIGNITY_RANK` etc. → 0).

⚠ This is a **third** ordering, and it conflicts with the one `app.py:4160` already quotes from
*Nativities* Ch. 1.20, 2 — "the lord of the **bound**, then the lord of the house, then the lord of
the exaltation, then the lord of the triplicity, then the lord of the image." **The bound is first
there and third here.** Contexts differ (house-master selection vs a planet's rank), and exaltation
is unplaced in the Questions chain. **Do not merge.**

## A1.3 (Class 1) The three approaches are a ranked fallback, not a menu

> "**26** And **if there was not anything of what I mentioned**, then look for a transfer of light…
> **27** And **if you do not find** a planet … then look for a collection of light… **28** So from
> these **three approaches** comes the judgment of all sought matters." — Questions Ch. 1, 26–30

**Code now:** `evaluate_transfers_of_light` (`app.py:1512`) and `evaluate_collections_of_light`
(`app.py:1585`) are computed and reported **independently and unconditionally**.

**Not a contradiction** — reporting everything is right for a study tool, and the code's docstrings
are well sourced. What is missing is the **precedence**: Sahl consults transfer only when there is
no connection, and collection only when there is no transfer. That is display doctrine, not a
computation change.

## A1.4 (Class 1) ★ "Upright" stakes — and a three-way disagreement about it

> "the stakes are **upright**: that is, if the Midheaven **is the tenth sign**, and the Midheaven is
> **not the ninth sign** nor the stake of the earth the third." — Questions Ch. 1, 47 *(Figure 32)*

**Code now:** no "upright" concept (the single `grep` hit at `app.py:452` is an unrelated
delineation string).

⚠ Three sources disagree on what upright excludes: **Sahl** excludes only the 9th; the **glossary**
(p. 796) excludes the 9th *and* the 11th; **Dykes's fn. 25** argues the 11th should be *allowed*.
Prefer Sahl's sentence — it is the narrowest and the only primary one.

## A1.5 (Class 1) The angles are reassigned per topic — eight figures' worth

Ch. 6, 2 (illness: Asc = doctor, MC = patient, 7th = illness, 4th = medicine); Ch. 9, 5–6 (land);
Ch. 7.7, 91–101 (a full twelve-house war scheme), with the general instruction at ¶102–103. Figures
35, 36, 37, 39, 40, 41, 42, 43 are all per-topic house tables.

⚠ This sits in tension with *Introduction* Ch. 2, 4–29's **fixed** house significations. The natural
reconciliation — Ch. 2 as default, per-topic tables as overrides — **is not stated in either text**.
Relevant to the engine only as a caution: hard-coded house meanings implement one topic's
assignment as if universal.

## A1.6 (Class 1) A fourth good-places scheme, corroborating the glossary's hedge

> "let the Sun be in **an excellent place, in the Ascendant, eleventh, or tenth**. **13** And if he
> was **falling**, you will not get good … but if he was in the **ninth, third, or fifth**, it
> indicates hardship … and likewise the **stake of the west and the fourth** indicate a scarcity of
> benefit." — Choices Ch. 9, 12–13

Excellent = **1, 10, 11** — matching the glossary's parenthetical *"(These may be the only excellent
places.)"* (p. 780), which now has a text behind it. ⚠ And it **demotes the 7th and 4th, both
stakes**, which no other scheme in the corpus does. This is a datum against "angular = strong" as
uniform. Extends C-09 from three schemes to four.

## A1.7 (Class 1) Venus's joy is presupposed but never located

> "let Venus always be in her **exaltation, house, triplicity, or joy**" — Choices Ch. 7, 11

**Refines C-10.** The corpus **locates** four joys (9th/Sun, 3rd/Moon, 6th/Mars, 12th/Saturn — two
of them weakly attested) and **presupposes at least a fifth without locating it**. Still not licence
to supply the familiar 5th-house answer; the fixture in C-10 needs adjusting so it asserts "four
located," not "exactly four exist."

## A1.8 (Class 1) Smaller items

- **The Moon is more sensitive than the Ascendant**: "the infortunes' looking at the Ascendant is
  **easier than their looking at the Moon**" (Choices Ch. 9, 8).
- **Two explicit 2×2 condition matrices** crossing rising/declining with eastern/western
  (Choices Ch. 4, 22–25) and with direct/retrograde (Choices Ch. 12, 4–5) — corroboration that the
  axes are treated as independent, which is what a summed score assumes.
- **The lesser years granted as years when strong and received, months when weak** (Times Ch. 11,
  24–45), planet by planet. Deferred, but it is the bridge between the year tables and their use.
- **A retrospective use of separation** — measuring elapsed time backwards from a separating aspect
  (Times Ch. 10, 7). The engine's separation logic is forward-looking only.

## A4 (Class 4) New confirmations

- ✅ **Figure 47's Mars cell is wrong and the prose is right.** fn. 29 says the figure's "18" should
  be 15 "as found in Ch. 11, 39." I read Ch. 11, 39: it says **15 months**. Cross-reference checks
  out.
- ✅ **Crooked/straight and the burned path have downstream consumers in the corpus** — Choices
  Ch. 3, 18 and Ch. 7, 22 use "signs straight in rising"; Ch. 3, 6 and 3, 9 use the burned path.
  Strengthens C-04 and C-06 from "present in the corpus" to "used by the corpus."
- ✅ **The three-grade aspect scale** (trine/sextile · square middling · opposition) is now attested
  in **three works** — *Introduction* Ch. 2, 58; Appendix B ¶17; *Choices* Ch. 6, 41.
- ✅ **Not-reception** is stated from the primary text with its exception attached (Questions Ch. 1,
  40–42 and fn. 22), matching the glossary entry the code already follows.

## A5 (Class 5) One absence sharpened, one new

- **PN4 is still needed** — but for less than I said. See A3.1.
- ⚠ **A victor doctrine for questions is a Latin accretion, not Sahl.** Dykes, after Questions Ch. 1:
  the 1493 Latin version's paragraph "On the corruption of the Ascendant," attributed to Māshā'allāh
  and describing "some kind of victor in questions," **"evidently did not appear in the Arabic
  manuscripts of Sahl."** Worth recording given the engine's name: whatever victor doctrine it
  implements cannot be sourced to *On Questions*.

## A6 New internal disagreements

| # | Item | Note |
|---|---|---|
| 1 | Dignity ranking | Questions Ch. 13, 7 vs Nativities Ch. 1.20, 2 vs glossary p. 777 — **bound first or third** |
| 2 | Convertible-sign speed | Questions Ch. 9, 79 (Capricorn quickest, **Cancer slowest**) vs Choices Ch. 2, 5 (**Aries and Cancer quickest**). Cancer inverts. Dykes's proposed fix (fn. 11, quickness of the lord) **cuts against Choices** when applied here. |
| 3 | "Upright" | Sahl vs glossary vs Dykes's own footnote — see A1.4 |
| 4 | "Safe" | Questions Ch. 1, 51's four afflictions vs the glossary's one |
| 5 | Aspect grading | Two-grade (Questions Ch. 1, 33) vs three-grade (three other passages) |
| 6 | House significations | Fixed (*Introduction* Ch. 2) vs reassigned per topic (Questions, 8 figures) |
| 7 | Longevity method | Times Ch. 4, 2–7 vs Times Ch. 4, 8–10 (**Māshā'allāh's**), unadjudicated in the same chapter |
| 8 | Burned path degrees | Choices Ch. 9, 41's "beyond 10° [of Libra]" matches **neither** glossary span |
