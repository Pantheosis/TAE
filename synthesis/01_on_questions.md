# Phase 1 — Sahl, *On Questions* (complete)

Source: `sahl_on_questions.md`, Sahl Vol. I pp. 89–193, 18 chapters (~1,160 numbered sentences),
Figures 32–43. **New to code reconciliation**; zero citations in `app.py`.

Replaces the earlier combined filtered artifact (now removed), which covered only Ch. 1's
general principles. Chs. 2–18 are read here for the first time.

Citation: **Questions Ch. N, M**. Paragraph numbers restart per chapter.

---

## 1. Ch. 1 is a method chapter, and the rest of the book applies it

*On Questions* is far more systematic than its length suggests. **Ch. 1 states a general
procedure; Chs. 2–18 are that procedure applied to eighteen topics.** Almost every later chapter
opens with the same formula — "look at the lord of the Ascendant and the Moon (and they are the two
indicators of the one asking), and at the sign of the sought matter and its lord."

So the general doctrine is concentrated, and it is worth having in full.

### 1a. ★ The three approaches, with a stated fallback order

> "**26** And if there was not anything of what I mentioned, then look for a **transfer of light**…
> **27** And if you do not find a planet between them [which is] bearing the light of one of them to
> the other, then look for a **collection of light**… **28** So from these **three approaches** comes
> the judgment of all sought matters." — Questions Ch. 1, 26–28

> "**29** The **first**, the connection of the lord of the Ascendant, the Moon, and the lord of the
> sought thing; the **second**, if there is a planet transferring between them…; and the **third** is
> the collection of light… **30** So from these topics comes a judgment of the sought things."
> — Questions Ch. 1, 29–30

**A ranked fallback, not a menu**: connection first; transfer only if no connection; collection only
if no transfer. Each also carries an *agency* reading — connection = directly, transfer = "by the
hands of messengers," collection = "by the hand of a judge or a man he has confidence in."

### 1b. ★ A quantified testimony rule, with "safe" explicitly defined

This is the most concretely computable doctrine in the work.

> "The testimony of the stars in the accomplishment of the sought matters, is [in] **three
> testimonies** … and they are the **lord of the Ascendant, the lord of the sought matter, and the
> Moon**. **49** Now when the two indicators encountered [each other] … and **one of the two is safe,
> he will attain to one-third** of what he sought. **50** And if it was two testimonies … **two-thirds**.
> **51** And if all of the testimonies met together (that is, that the lord of the Ascendant, the lord
> of the sought matter, and the Moon were **safe from retrogradation, burning, the infortunes, and
> falling**), he will attain to **all** of what he sought. **52** And if along with their testimonies
> they were **received**, and the one receiving them was also received, then truly it will **add good
> on top of that**." — Questions Ch. 1, 48–52

Two things make this unusual in the corpus:

1. **A fractional outcome scale** — thirds, tied to a count of satisfied conditions. Most rules in
   the corpus are binary or unranked.
2. **"Safe" is defined by enumeration** — free of **retrogradation, burning, the infortunes, and
   falling**. Four named afflictions, no others. Compare the glossary's *Safe* (p. 791: "not being
   harmed, particularly by an assembly or square or opposition with the infortunes") and *Cleansed*
   (p. 774), neither of which includes retrogradation or falling. **Sahl's operative list here is
   wider than the glossary's.**

Reception is explicitly **additive on top**, not one of the three.

### 1c. Upright stakes — and a three-way disagreement about what "upright" excludes

> "the testimony of the signs … is if the Ascendant is a **fixed sign or one having two bodies**,
> and **the stakes are upright**: that is, if the Midheaven **is the tenth sign**, and the Midheaven
> is **not the ninth sign** nor the stake of the earth the **third** [sign]." — Questions Ch. 1, 47

**Figure 32 (p. 95), "Upright and falling Midheavens," illustrates it.**

⚠ Three sources say three different things about what counts as upright:

| Source | Excludes |
|---|---|
| **Questions Ch. 1, 47** (Sahl's own text) | the MC in the **9th** sign (and IC in the 3rd). Says nothing about the 11th. |
| **Glossary p. 796** (*Upright*) | "rather than the **eleventh-fifth, or ninth-third**" — excludes **both** |
| **Dykes's fn. 25** | *"we could undoubtedly allow the Midheaven to be in the **eleventh** sign, for that sign is moving up towards being the tenth sign"* — **allows** the 11th |

So Sahl excludes only the 9th; the glossary excludes the 9th *and* the 11th; and Dykes's own
footnote argues the 11th should be allowed. **Prefer Sahl's sentence** — it is the narrower,
primary statement, and it is the only one of the three that is Sahl's.

This matters because `app.py` has no "upright" concept and the glossary entry is the version most
likely to be picked up.

### 1d. Advancing and retreating matched to the nature of the matter

> "if you were asked about a sought matter, and it was **in the nature of advancing** … look [at]
> the **advancement of the one accepting** … **20** But if the question was about **the nature of
> retreating, such as travel, moving, a detained person's exit from his prison, and being released
> from sorrows**, then look for these matters **from the place of retreat and withdrawal**."
> — Questions Ch. 1, 18–20

Retreat is not a defect when the matter sought is a departure. The named topics (travel, prison
release, release from sorrows) are the 9th, 12th and 3rd — the cadent, withdrawing places — so the
doctrine is internally coherent: matters *of* withdrawal are read *from* withdrawal.

### 1e. Tie-break between the two chief significators

> "look at the lord of the Ascendant and the Moon, **the stronger one of them (that is, the one in a
> stake) and the one looking at the Ascendant**: begin with it." — Questions Ch. 1, 22

Two criteria — angular, and aspecting the Ascendant — given together with no stated priority if
they conflict.

### 1f. Direction of application governs manner

> "if one of them connected with the lord of the sought thing, then the sought thing will be
> accomplished **by the seeking of the one asking**; and if you found the lord of the sought thing
> connecting with the lord of the Ascendant, that sought thing would be accomplished **in ease** …
> apart from seeking it and without beseeching." — Questions Ch. 1, 23

Restated at ¶34–36. The same principle organises Appendix B (see `01_appendices_a_and_b.md` §B1),
so it is attested in two works.

### 1g. Aspect quality

> "if the connection … was **from a trine or sextile, the attainment will be with ease**; and if the
> connection was **from a square or opposition**, then truly the attainment will be **after
> difficulty, beseeching, and delay**." — Questions Ch. 1, 33

Note this is a **two-grade** split (trine/sextile vs square/opposition), where *On Choices* Ch. 6, 41
and *Introduction* Ch. 2, 58 give a **three-grade** one with the square as "middling." Not a
contradiction — a coarser statement of the same scale — but an engine quoting one should not
present it as the other.

### 1h. Connecting *from* a fall, and the vetoes

> "the lord of the Ascendant and the Moon, if they connected with a planet **from its fall** (such as
> if the lord of the Ascendant is connecting with Mars **from Cancer** or with Jupiter from
> Capricorn), it indicates the **corruption** of the sought matters. **41** And likewise if they were
> connecting with a planet **from their own fall** … **42** … if the Moon is connecting with a planet
> from **3° of Scorpio (which is her fall)**." — Questions Ch. 1, 40–42

**Two distinct cases**, easy to conflate: applying *from the sign that is the other planet's fall*,
and applying *from one's own fall*. ⚠ fn. 22 adds a condition from *Introduction* Ch. 3, 61: the
second case "**also requires that the other planet not have any dignity in the connecting planet's
sign** — otherwise this would be a case of reception."

This is the glossary's *Not-reception* (p. 787) stated from the primary text, with the exception
attached.

> "if you found the lord of the Ascendant or the Moon **in the place of the sought thing** … it will
> be accomplished, **unless the Ascendant was the fall of the lord of the sought thing, or it was
> burned up in it**." — Questions Ch. 1, 24

### 1i. The acceptor of the management must itself be sound

> "look at the **one accepting the management** … for if it was **free of the infortunes, in the
> stakes and what follows them, and it is not retrograde, burned, nor falling** … that sought matter
> will be accomplished. **32** And if it was made unfortunate, the sought matter will be **corrupted
> after he has attained it**; and if the one accepting was **retrograde**, it will be **terminated
> after he believed he has already attained it**." — Questions Ch. 1, 31–32

The failure *modes* are distinguished by cause — affliction spoils it after attainment,
retrogradation reverses it after apparent attainment. That is a finer distinction than a single
"corrupted" flag.

---

## 2. ★ Figures 33 and 34 — the corpus's only dated, located, fully worked chart

`00_inventory.md` flagged these as "a directly testable fixture." They are, and they are better
than expected: the corpus gives **the manuscript's own figures, a modern recomputation, and the
judgment Sahl drew** — so the judgment can be tested against both.

### 2a. The data

> "the Ascendant was **Gemini, 20°**; and the Midheaven **Pisces, the first degree**; and the Sun in
> **Cancer, 12°**; and the Moon in **Virgo, 17°**; and Mercury in **Gemini, 27°**; and Mars in
> **Taurus, 8°**; and Venus in **Leo, 3°**; and Jupiter in **Pisces, in 20°, stationing toward
> retrogradation**; and Saturn in **Gemini, in 6°**." — Questions Ch. 1, 54

**Figure 34** supplies the reconstruction: **5 July 824 AD (Julian), 3:18:10 AM LMT −02:57:40,
Baghdad, 44e25'00 33n21'00, geocentric, "Sassanian" zodiac, whole signs.** Both figures read
directly from the images.

| Body | MS (Fig. 33 / ¶54) | Modern (Fig. 34) | Δ |
|---|---|---|---|
| ASC | ♊ 20° | ♊ 20°11' | ~0 |
| MC | ♓ 0–1° | ♓ 01°10' | ~0 |
| ☉ | ♋ 12° | ♋ 12°44' | ~0 |
| ☽ | ♍ 17° | ♍ 15°46' | **1°14'** |
| ☿ | ♊ 27° | ♊ 29°31' | **2°31'** |
| ♀ | ♌ 3° | ♌ 09°06' | **6°06'** |
| ♂ | ♉ 8° | ♉ 07°23' | 0°37' |
| ♃ | ♓ 20° | ♓ 20°32' | ~0 |
| ♄ | ♊ 6° | ♊ 07°06' | 1°06' |

The angles and Jupiter are near-exact; **Venus is 6° out** and Mercury 2½°.

### 2b. Every judgment Sahl draws survives the discrepancy — which is what makes it a good fixture

| ¶ | Sahl's judgment | MS | Modern |
|---|---|---|---|
| 56 | Mercury (lord of ASC) **in the Ascendant, at the end of the sign** | ♊27 ✓ | ♊29°31' ✓ |
| 56 | Jupiter (lord of the sought matter) **in the Midheaven** | ♓20 ✓ | ♓20°32' ✓ |
| 56 | **Lord of Asc separated from** lord of the sought matter | ✓ (♊27 past the ♓20 square) | ✓ |
| 57 | Moon **in the stake of the earth** | ♍ = 4th from ♊ ✓ | ✓ |
| 57 | Moon **connecting with Jupiter from an opposition** | ♍17 → ♍20, applying ✓ | ♍15°46' → ♍20°32', applying ✓ |
| 61 | Jupiter **stationing toward retrogradation** | stated ✓ | Fig. 34 marks Rx ✓ |
| 63 | Mercury **shifting from his house into the house of assets** | leaving ♊ for ♋ ✓ | ✓ |
| 63 | On leaving, Mercury **connects with Mars, who does not accept him** | fn. 27: Mercury applies to Mars **from Cancer, Mars's fall** ✓ | ✓ |
| 65 | Jupiter **is with the Tail** | ⚠ **not in ¶54's data at all** | ☋ ♓25°46', with ♃ ♓20°32' ✓ |

**¶65 is the interesting one.** Sahl asserts Jupiter is with the Tail, but the node positions are
**not among the figures he lists**. The modern recomputation supplies them and confirms it. That is
an independent check that Dykes's date and time reconstruction is right — a claim in the text is
verified by data the text does not give.

### 2c. What this fixture can and cannot prove

**Can**: whole-sign house assignment from a 20° Gemini Ascendant; separation vs application by
degree; opposition across Virgo–Pisces; applying-from-the-other's-fall (Mercury→Mars from Cancer);
lord-of-house lookup; the three-testimony count of §1b.

**Cannot**: anything depending on Venus, whose manuscript position is 6° from the recomputation —
and note Sahl draws **no judgment from Venus at all** in this worked example.

⚠ **The zodiac is "Sassanian," not tropical.** Figure 34 says so explicitly. Any fixture built from
the date/time must either use that frame or use the **positions** rather than recomputing them. The
safer fixture uses ¶54's stated longitudes directly as inputs.

---

## 3. ★ A general dignity ranking, never cited in the code — and it disagrees with *On Nativities*

> "if it was **in its own house** and it is in a stake, then it is from the people of a house of
> well-known people, and he is also from that house, and he has rank. **7** And **the triplicity is
> below the house, and likewise the bound below the triplicity, and the face below the bound**."
> — Questions Ch. 13, 6–7

**house > triplicity > bound > face.** ⚠ Exaltation is **absent from the chain** — it appears
separately at ¶4 ("a fortune or in its own exaltation") but is not placed in the ordering.

This is a **third** ordering in the corpus:

| Source | Order | Context |
|---|---|---|
| **Questions Ch. 13, 7** | house > triplicity > bound > face *(exaltation unplaced)* | a planet's rank/standing |
| **Nativities Ch. 1.20, 2** | **bound** > house > exaltation > triplicity > image | choosing the **house-master** among the releaser's lords |
| **Glossary p. 777** | domicile > exaltation > triplicity > bound > face *("often listed in the following order")* | general listing |

Verbatim, for the middle row:

> "if you found all of the five indicators looking at the releaser, then the stronger of them is
> **the lord of the bound, then the lord of the house, then the lord of the exaltation, then the
> lord of the triplicity, then the lord of the image**." — Nativities Ch. 1.20, 2

**The bound is first in one and third in another.** The contexts differ — Nativities 1.20 is
specifically house-master selection, where the bound lord's priority is a known idiosyncrasy (the
glossary's *House-master* entry says "preferably the **bound lord**") — so this is **not
necessarily a flat contradiction**. But Questions Ch. 13, 7 is a general strength claim, and it is
the one the code has never seen.

**Do not merge these into one ranking.** Record which context each belongs to.

---

## 4. ★ The angles are reassigned per topic — a systematic doctrine

Sahl repeatedly overrides the standard house significations for the topic at hand. This is not
occasional; it has **eight figures devoted to it** (Figs. 35, 36, 37, 39, 40, 41, 42, 43, each
captioned "Angles for…" or "Houses for…").

The clearest statement, for illness:

> "the **Ascendant indicates the doctor**, the **Midheaven indicates the sick person**, the
> **seventh sign indicates the illness**, and the **fourth sign indicates the medicine**."
> — Questions Ch. 6, 2 *(Figure 37)*

For a landed estate:

> "erect the Ascendant … and make it an indicator for **the leasing and the farmers**. **6** And the
> **fourth sign indicates the condition of the land**, and the **seventh** … **vegetation shorter
> than trees**, and from the **Midheaven** … **trees**." — Questions Ch. 9, 5–6 *(Figure 35)*

And for war, a **full twelve-house** reassignment (Ch. 7.7, 91–101, Figure 41): 2nd = whether the
fighting happens; 3rd = the weapons; 4th = the terrain; 5th = the soldiers' eagerness; 6th = their
animals; 7th = the enemy and siege engines; 8th = the wounded and prisoners; 9th = spies and
stratagems; 10th = the commander; 11th = mobilization and battle lines; 12th = the besieged city.

Then the general instruction:

> "So look at these **twelve places, and the positions of their lords**, and who (of the infortunes
> and the fortunes) **is looking at them** … **103** Then, speak based on what you see … for if a
> fortune is looking, it indicates good fortune and the good **for that sign**."
> — Questions Ch. 7.7, 102–103

**This is doctrinally important and easy to miss**: the *machinery* (lord, aspect, fortune/
infortune) is constant; the *topic assignment* of each house is variable. An engine that hard-codes
house significations is implementing one topic's assignment as if it were universal. Note the
tension with *Introduction* Ch. 2, 4–29, which gives the houses fixed meanings — the two are
reconciled by taking Ch. 2's list as the default and Sahl's per-topic tables as overrides, but
**neither text says that.**

---

## 5. ⚠ Ch. 9, 79 contradicts *On Choices* Ch. 2, 5 on the convertible signs

This is the passage Dykes cross-references from *On Choices* fn. 11, and reading it does not settle
what he suggests it settles.

> "if she was in a **convertible** sign, it indicates **liberation with quickness**, **except for
> Cancer (indeed it is slow, because it is her house; and Aries and Libra are slower for liberation
> than Capricorn)**." — Questions Ch. 9, 79

So the ordering here is **Capricorn quickest → Aries and Libra slower → Cancer slowest**.

*On Choices* Ch. 2, 5 gives the reverse at both ends:

> "the **quickest of the convertible** [ones] are **Aries and Cancer** … and **Libra and Capricorn
> are the more powerful and balanced** of them."

| | Quickest | Slowest |
|---|---|---|
| *Choices* Ch. 2, 5 | **Aries, Cancer** | (Libra, Capricorn "more balanced") |
| *Questions* Ch. 9, 79 | **Capricorn** | **Cancer** |

**Cancer is the fastest in one and the slowest in the other.**

⚠ Two mitigations, both real: the topics differ (general sign nature vs liberation from prison), and
*Questions* gives a **reason** — Cancer is slow "because it is **her house**," i.e. the Moon settles
in her own domicile. Dykes's fn. 11 uses exactly this to argue the rankings track *the ruling
planet's* quickness rather than ascensional times.

But that reconciliation, applied here, **cuts against *On Choices***: if the lord's quickness
governs, the Moon's own house should be quick, not slow. **Recorded as an unresolved disagreement.**
Do not implement either ranking.

---

## 6. Other general rules worth carrying

| Rule | Source |
|---|---|
| An infortune as lord of the sought thing, applied to **by square or opposition**, "will not accept them"; **from a trine or sextile it will refrain from this** | Ch. 1, 43–44 |
| Lord of Asc and lord of the sought matter being **the same planet**: accomplished if received and free of infortunes | Ch. 1, 45 |
| Applying to a planet **that has dignity in the place of the sought thing** also accomplishes it | Ch. 1, 25 |
| **Reflection of light** used as a named configuration alongside transfer and collection | Ch. 5, 2; Ch. 9, 5 |
| Quadruplicity of Asc-lord and Moon governs **durability** of a partnership: convertible → will not last; fixed → durable; double-bodied → profitable and loyal | Ch. 7.6, 2 |
| **Reception plus aspect** determines reconciliation in war, and the **initiator is the one handing over (the lighter)** | Ch. 7.7, 4–6 |
| Ordering of **multiple options** by the lord of the Ascendant's condition (in stakes + free + received → the first named wins) | Ch. 16, 4–6 |
| Saturn in a stake **without testimony** prolongs a war; **worse if retrograde** | Ch. 7.7, 31 |
| Retrogradation read as **return**: "if the lord of the Ascendant was retrograde, then he will return to his authority" | Ch. 10, 143 |

---

## 7. ⚠ Provenance: a Latin interpolation that is not in the Arabic

Dykes's comment after Ch. 1:

> "At this point the **1493 Latin version** (Bonatus Locatellus, Venice) has a short paragraph '**On
> the corruption of the Ascendant**,' which is attributed to **Māshā'allāh** and describes the use of
> **some kind of victor in questions**. But it **evidently did not appear in the Arabic manuscripts
> of Sahl**. Bonatti seems to have used a MS which was part of this 1493 lineage, because he inserts
> his own version into *The Book of Astronomy* Tr. 6, Part 2, Ch. 5."

**A victor-in-questions doctrine circulating under Sahl's name is a Latin accretion.** Given that
this project's engine is named for the victor (*almuten* / *mubtazz*), this is worth recording
explicitly: whatever victor doctrine the engine implements, **it cannot be sourced to Sahl's
*On Questions***.

Dykes also notes the absence of first-house questions here, pointing to *On Times* Ch. 4 instead —
which is where the longevity/releaser material turned out to be (see `01_on_times.md` §4).

---

## 8. Internal disagreements, collected

| # | Item | Note |
|---|---|---|
| 1 | Dignity ranking | Ch. 13, 7 (house > triplicity > bound > face) vs **Nativities 1.20, 2** (bound first) vs glossary p. 777. Contexts differ; three orderings. |
| 2 | Convertible-sign speed | Ch. 9, 79 (Capricorn quickest, Cancer slowest) vs ***Choices* Ch. 2, 5** (Aries and Cancer quickest). **Cancer inverts.** |
| 3 | "Upright" stakes | Sahl Ch. 1, 47 excludes only the 9th; glossary p. 796 excludes the 9th **and** 11th; Dykes's fn. 25 **allows** the 11th. |
| 4 | Aspect grading | Ch. 1, 33 is two-grade (trine/sextile vs square/opposition); *Choices* Ch. 6, 41 and *Introduction* Ch. 2, 58 are three-grade with the square middling. |
| 5 | "Safe" | Ch. 1, 51 enumerates retrogradation, burning, infortunes, falling. The glossary's *Safe* (p. 791) and *Cleansed* (p. 774) name only the infortunes. |
| 6 | House significations | Fixed in *Introduction* Ch. 2, 4–29; **reassigned per topic** here (Figs. 35–43). Neither text reconciles them. |
| 7 | Victor in questions | A Latin interpolation, **not in the Arabic** (Dykes's comment after Ch. 1). |
| 8 | Ch. 1, 57 fn. 26 | *"The Moon cannot be applied to — Sahl is simply trying to employ the rule mentioned in 22-23."* Dykes flags Sahl's own worked example as loosely reasoned. |

---

## 9. What is *not* synthesized

The topical bulk of Chs. 2–18 — the actual judgments for assets, siblings, land, children, illness,
marriage, lawsuits, buying and selling, runaways, theft, partnerships, war, death, travel,
authority, hopes, prison, books and messengers, reports, retaliation, hunting and meals. Roughly
40,000 words. These are horary delineations; the engine is natal, and reproducing them would be
transcription rather than synthesis. **The general machinery they all share is §1 above**, and that
is what an engine could use.

Figures 36, 38, 39, 40, 42, 43 (angles for leasing, critical days, theft, partnerships, travel,
meals) are per-topic house tables of the same kind as §4 and are not individually transcribed.
Figure 38 ("Critical days") is the one exception worth a later look if illness timing is ever in
scope — it is a lunar-phase table, not a house table.
