# Phase 1 — Sahl, Appendix A (*The Sixty-Six Sections*) and Appendix B (*Connections of the Lord of the Ascendant*)

Sources: `sahl_appendix_a_sixty_six_sections.md` (Sahl Vol. I pp. 750–758) and
`sahl_appendix_b_lord_of_ascendant.md` (pp. 759–765). Both **new to code reconciliation**; zero
citations in `app.py`. No figures in either. Read without reference to the code.

---

# PART I — Appendix A, *The Sections on Ascendants & the Judgments of Nativities*

## A0. Provenance — weaker than the rest of the corpus, and Dykes says so

> "This short set of 66 statements appears in two manuscripts mentioned by Sezgin (p. 127, #5). The
> following is based on **Nuruosmaniye 2785/3, 13a-15a**; the other manuscript (**not yet seen by
> me**) is Cairo, Tal'at 139/4, 62a-65a." — Dykes's comment, p. 750

So Appendix A rests on **a single consulted manuscript**. That is a lower evidentiary base than
*On Nativities* or the *Introduction*, and it should temper how strongly anything here is asserted.

> "It so happens that **every one of these is reflected in the famous *Propositions of al-Mansūr***,
> one of several centiloquies popularized in the Latin Middle Ages. In some cases, the Latin helps
> clarify some readings in N. I have prefaced each of the sections with a 'Sahl number' [S] and an
> 'al-Mansūr number' [M] so that they may be compared." — *ibid.*

Two consequences. First, the Latin *al-Mansūr* is used as a **corrective witness** throughout the
footnotes, so a number of readings here are Latin-influenced rather than purely Arabic. Second, the
[S]/[M] tags mean every section has two numbers, neither of which is the paragraph number.

## ⚠ A0b. Citation hazard: 67 paragraphs, 66 sections

The file carries **67 numbered paragraphs** but the work has **66 sections**, because ¶56 is tagged
`[S56/M132, 134]` and contains *two* numbered sentences (56 and 57) under one section. From ¶58
onward the paragraph number runs **one ahead** of the section number:

| Paragraph | Section |
|---|---|
| ¶1 … ¶56 | S1 … S56 (¶56 contains sentences 56 *and* 57) |
| ¶58 | S57 |
| … | … |
| ¶67 | **S66** (the last) |

Anything citing this work must say which numbering it uses. Below I give both as `¶N [SN]`.

## A1. Scope — this is not a natal text

Dykes: *"They cover all areas of traditional astrology: questions, inceptions, nativities, and
mundane."* That is accurate. Roughly a third of the sections are mundane (world-year ingresses,
conjunctions, climes) or electional (bloodletting, circumcision, buying, travel), and they are not
natal doctrine at all. I have sorted them below rather than treating the set as homogeneous.

## A2. Natal sections with concrete, computable conditions

Quoted in full where short.

| ¶ [S] | Rule |
|---|---|
| ¶1 [S1] | "He will not save up on provisions except one whose **lord of the Ascendant and lord of the fourth are a single planet**, just as one will not take on rank and assets and a pension except one whose **lord of the Ascendant and lord of the tenth are a single planet**." |
| ¶5 [S5] | "If the heavy planets were **westernizing** from the Sun, they grant the native good fortune **at the end of his lifespan**." |
| ¶8 [S8] | "If the Moon is made unfortunate in the root of the nativity, and the **first lord of the triplicity of the Ascendant is falling**, and the stakes harmed, then judge for the native the **shortness of his survival**." |
| ¶9 [S9] | "If **all of the lords of the triplicities** were falling, and in one of the stakes was [one of the] **fixed stars which are of the first and second magnitude, of the complexion of the lords of the triplicities**, the upbringing will be completed and the years will be passed by." |
| ¶14 [S14] | "The testimonies of the **connection of the Moon** with a planet are **stronger in the Ascendant or the Midheaven**." |
| ¶17 [S17] | "One whose Moon in the root of his nativity is found in the **minute of [her] exaltation**, and the **Sun in Leo on the horizon of the east**, will reach a powerful rank." |
| ¶20 [S20] | "One whose **lord of the Ascendant is connected to the lord of his tenth**, will be received by his employer; and one whose lord of his tenth is **separated** from the lord of his Ascendant, will in no way be received." |
| ¶21 [S21] | "If the **Moon and Ascendant were in signs of the fortunes**, and the two fortunes were also like that, and **one of the two looked at the other**, the native will have strong exaltedness and ability." |
| ¶27 [S27] | "The **misfortune of Mercury by Saturn** necessitates a **knot in the native's tongue**; and **harsher for that is the assembly**." |
| ¶29 [S29] | "One whose nativity has **each one of the luminaries in the degree of its exaltation, safe from the infortunes**, [that] native will rule the world…" |
| ¶32 [S32] | "If the **lord of the fourth is made unfortunate by the lord of the Ascendant**, it is feared for the **parents**; and if the **lord of the Ascendant is made unfortunate by the lord of the fourth**, it is feared for the **native**." |
| ¶38 [S38] | "If the **lord of the Ascendant was in the bound of the fortunes** in nativities, and a praiseworthy place, and the **lord of the bound in a good condition, attached to it**, then it grants benefit and leadership and goodness of conduct." |
| ¶39 [S39] | "The reasons for good fortune are the alighting of the **lord of the house of the Sun, and the lord of the house of the Moon, and the lord of the Ascendant, in their own domain, in the stakes, looking at each other from a trine or sextile**." |
| ¶40 [S40] | "The most powerful status which one's **Sun can have is in the Midheaven, in a fiery sign**, and the **Moon looking at him from a trine or sextile, she being on the left of him**." |
| ¶41 [S41] | "The most powerful king is one whose **lord of the second is in its exaltation, house, or its *halb*, connecting with the lord of the Ascendant**, and especially if it was Jupiter." |
| ¶49 [S49] | "One whose **lord of the Ascendant is right-siding the Sun and has spear-bearing, and is superior to [the Sun], and its easternization is accomplished**, is of those who associates with kings…" |
| ¶50 [S50] | "One who has the **two infortunes in the fourth sign, in one bound**, the native will certainly be contemptible, disreputable." |
| ¶52 [S52] | "One who has the **stakes of his Ascendant as convertible [signs], and the two infortunes in the stakes**, will fall down low within his lifespan." |
| ¶59 [S58] | "If **Venus and Mars were [in the] heart with the Sun, degree by degree, in the places of Venus and her shares**, the speech of the native will be received by all the people…" |
| ¶60 [S59] | "The worshipper who is close to prophethood is one whose **Jupiter and Venus are [in the] heart** in his nativity." |
| ¶61 [S60] | "Those who are celebrated in leadership … are those whose **Jupiter and Moon are in one degree, rising up to the cycles of their spheres**." (fn. 47: *"probably … rising up toward the apogee of their deferent circles"*) |
| ¶62 [S61] | "One harsh in power and mighty in force is one who has the **Sun in the Midheaven with Saturn, in a male sign, easternizing**." |
| ¶67 [S66] | "The **harm of the Nodes to the inferior planets is more powerful** than their harm to the superior planets." |

### Remarks on individual sections

- **¶38's "attached to it"** carries a hidden orb claim. fn. 30: *"مرتبط به. This unusual word
  suggests that Sahl is drawing from an older author who was translating the Greek *kollēsis*, **a
  conjunction within 3°**. Normally, Arabic authors use اتّصال, 'connection.'"* This is the only
  place in this appendix where a **degree** value is implied, and it is implied by a translator's
  etymological argument, not stated. **Do not treat 3° as a sourced orb.**
- **¶40's "on the left of him"** is directional and Dykes reads a consequence out of it —
  fn. 32: *"In this case she would be waxing in light as well."* Left/sinister = later in zodiacal
  order = separating from the Sun = waxing. Consistent with *Introduction* Ch. 2, 52–56.
- **¶41's *halb*** is a tentative reading. fn. 33: *"Tentatively reading for جلبه or حلبه. If my
  reading is correct, this is a sect-related condition… (The Latin al-Mansūr omits.)"* So the term
  is (a) conjectural and (b) unsupported by the Latin witness. Weak.
- **¶49 stacks four conditions** — right-siding, spear-bearing, superiority, completed
  easternization — all of which are defined in Abū Ma'shar Book VII (VII.2 for easternization and
  spear-bearing, VII.5 for superiority). This section is a **cross-work composite** and is a good
  candidate test case precisely because every term in it is defined elsewhere in the corpus.
- **¶46 [S46] reads counter-intuitively and I am not smoothing it over:**
  > "What is most powerful for [what a sign] is responsible for, is a sign in which there alights a
  > planet **whose fall is that sign**, or it is **retrograde** in it, or one in a **bad condition
  > relative to the Sun**."

  As printed, debility of the visiting planet *increases* the sign's power for its own topic. No
  footnote explains it. This may be sound (the sign's own nature is unopposed), or it may be a
  corrupted negation. **Flagged, unresolved.**

## A3. ⚠ Sections that are editorial reconstructions — do not implement as Sahl

### ¶35 [S35] — the "detested connection" pairs are Dykes's arrangement

Printed text:

> "The connection of the Moon with Mars is detested from the houses of Venus, [nor with Jupiter from
> the houses of Mercury, nor with the Sun from the houses of Saturn]." — ¶35, brackets in the source

fn. 28, in full:

> "I have read this in an **astrologically more appropriate way**: namely, that we don't want the
> Moon to connect with a planet from the signs which are opposite that planet's signs: Mars-Venus,
> Jupiter-Mercury, and Sun-Saturn. **The Arabic and Latin versions each make some unusual pairs
> which can be explained by accidentally skipping and mismatching some clauses.** For example, the
> Latin is close to mine but pairs Jupiter with both Saturn and Mercury, while the **Arabic pairs
> Jupiter with Saturn and the Sun**."

Three different pairings exist:

| Witness | Pairs |
|---|---|
| **Arabic (N)** | Jupiter–Saturn, Jupiter–Sun (as reported) |
| **Latin al-Mansūr** | Jupiter–Saturn *and* Jupiter–Mercury |
| **Dykes's printed text** | Mars–Venus, Jupiter–Mercury, Sun–Saturn (the tidy opposite-domicile scheme) |

Dykes's version is the *regular* one — each planet paired with the ruler of the signs opposite its
own. **That regularity is the reason to distrust it.** This is precisely the "completing a pattern
the text leaves incomplete" failure the brief names: the manuscripts give an irregular set and the
edition prints a symmetrical one, on the editor's own admission that he found his version "more
appropriate." Classify as **interpretive choice**, and if it is ever implemented, implement it
behind a switch with the Arabic reading as the alternative.

### ¶29 [S29] — the second half is supplied from the Latin

> "[his seed will inherit his lands, and will occupy] them for a long time" — fn. 21: *"Reading
> with the Latin al-Mansūr for an uncertain and partly undotted phrase."*

The protasis (both luminaries in their exaltation degree, safe from infortunes) is Arabic; the
apodosis about inheritance is Latin-restored.

### ¶12 [S12] and ¶13 [S13] — clauses added from the Latin

¶12 "⟨In journeys⟩" (fn. 11) and ¶13 "⟨toward him⟩" (fn. 12) are both *"Adding with the Latin
al-Mansūr."*

### ¶53 [S53] — excluded by standing policy

> "especially if she had ⟨missing⟩ in her claims"

`DOCTRINAL_CAVEATS.md` already excludes this: fn. 44's "in her dignities" is an **editorial guess,
not a restored reading**. No change; recording that I hit it and honoured the exclusion.

## A4. Internal disagreement: ¶37 [S37] vs *On Nativities* Ch. 4.1

> "The strongest of the indications **for the father** is the **first child** born to him, and what
> follows after that becomes a partner." — ¶37 [S37]

Dykes's fn. 29 flatly contradicts it from the main work:

> "But see *Nativities* Ch. 4.1, 1-2, which says that the **following children** will be more
> indicative in the father's nativity."

Two Sahl texts, opposite answers, on which child a father's nativity primarily describes. Recorded,
not resolved. (I have not read *Nativities* Ch. 4.1 in this pass; that is a later artifact. The
disagreement is Dykes's own report of it.)

## A5. ⚠ ¶64 [S64] — a non-aspect configuration that may be antiscia, parallel, or neither

This is the most consequential unclear section in the appendix, and it touches a family the project
has already been burned on.

> "If there was **no connection [by] aspect** between the indicator and one of the planets **but they
> were both in one [and the same] of the circles parallel to the meridian of the day or in a
> corresponding path**, then it is **the most preferable aspect**." — ¶64 [S64]

fn. 48, in full:

> "This sounds like being in the **same declination**, but I would expect a different word for that;
> **perhaps** it means that they are each **equidistant from the meridian in right ascension**?"

So the source asserts something strong — a *non-aspectual* configuration that outranks aspects
("the most preferable aspect") — and the translator does not know what configuration it is. Three
readings are live:

1. **Same declination** (parallel / contraparallel) — Dykes's first guess, which he immediately
   doubts on lexical grounds.
2. **Equidistant from the meridian in right ascension** — Dykes's alternative. This is the
   *antiscia* relation expressed mundanely.
3. Something else. "Circles parallel to the meridian" are hour circles, which suggests (2) more
   than (1) — but that is my inference, not the text's.

**This must not be implemented, and it must not be folded into the antiscia family.** The corpus
already enumerates five antiscia pairs and stops (Abū Ma'shar VII.5, 67–75); adding a sixth from
this section would be exactly the reconstruction the brief forbids, and would rest on a footnote
whose author says "perhaps." Record it as **genuinely present but undetermined**, and name what
would settle it: a passage elsewhere in Sahl using the same Arabic phrase in a context that fixes
its referent.

## A6. Sections that are mundane or electional — out of natal scope

Listed so a later pass does not re-derive the sort. Mundane: ¶10 [S10], ¶24 [S24], ¶25 [S25],
¶26 [S26], ¶30 [S30], ¶31 [S31], ¶33 [S33], ¶34 [S34], ¶55 [S55], ¶56–57 [S56], ¶58 [S57],
¶66 [S65]. Electional / horary: ¶2 [S2], ¶3 [S3], ¶6 [S6], ¶7 [S7], ¶11 [S11], ¶12 [S12],
¶28 [S28], ¶36 [S36], ¶43 [S43], ¶44 [S44], ¶45 [S45], ¶48 [S48], ¶63 [S62], ¶65 [S64].
General/theoretical, applicable anywhere: ¶15 [S15], ¶16 [S16], ¶18 [S18], ¶47 [S47], ¶51 [S51],
¶54 [S54].

Two of the "general" ones are worth keeping in view:

- ¶16 [S16] / ¶54 [S54] are a **matched pair** (fn. 14 and fn. 45 cross-reference each other):
  "Every thing which occurs quickly and corrupts quickly, that is from the indication of Mars; and
  if it happened slowly and is slow in corruption, that is from the indication of Saturn" (¶16);
  "There will not be speed except from Mars, just as there is no steadiness except from Saturn"
  (¶54). Stated twice in one work — unusually well attested for this appendix.
- ¶13 [S13] states a plain astronomical fact as doctrine: "Every planet, when it parts from the Sun,
  speeds up its course; and if it goes ⟨toward him⟩, it slows its course down."

## A7. Timing sections — DEFERRED, recorded only

¶19 [S19] ("when the **management and the distribution** passes over to it"), ¶22 [S22] (solar
revolution resembling the root), ¶23 [S23] ("the **direction of the lord of the sign the year
terminates at, to the bounds**"), ¶31 [S31] ("the **distributor and the ray**, and the **lord of
the year**"), ¶34 [S34] (mundane profection, "a year for every sign"), ¶42 [S42].

¶42's footnote makes the deferral explicit — fn. 35: *"This most likely refers to longevity
techniques, in which one **directs an indicator of life by primary directions**."* Note that ¶42
itself is a substantive doctrinal claim that would matter if the deferral lifts:

> "If the **fortunes were the lords of the destructive places**, they will **sever** [matters] just
> as the infortunes sever when they connect with the indicator or it connects with them." — ¶42

---

# PART II — Appendix B, *The Connections of the Lord of the Ascendant*

## B0. What it is, and a note on attribution

Dykes's comment, in full:

> "This short piece gives **easy, cook-book style interpretations** for connections between the lord
> of the Ascendant and the lords of other houses. **The author** focuses on the following principles
> of interpretation:
> 1. Whether the lord of the Ascendant **hands the management over** to the other lord, or *vice
>    versa*.
> 2. **Out of which house** the management is handed over (i.e., where the applying planet is).
> 3. Whether the planet being handed over to (or applied to) is a **fortune or infortune**."

Note "**the author**," not "Sahl." Dykes does not assert Sahl's authorship in this comment. The
file is filed under Sahl's name and sits in his volume; I record the wording without drawing a
conclusion from it.

**This file has no source photographs anywhere in the project** (per `CORPUS_MANIFEST.md` /
`DOCTRINAL_CAVEATS.md`), and it carries five `⟨missing⟩` / `[uncertain]` / `[illegible]` marks
(¶12, 20, 43, 45, 48) plus further "meaning unclear" footnotes at ¶67 and ¶71. It is the least
secure text in the corpus.

## B1. The doctrinal skeleton — three axes, and they are real rules

Although the *content* is interpretive prose, the *structure* is a computable three-key lookup, and
that structure is stated repeatedly rather than once:

- **Axis 1 — direction.** Every section splits on "If the lord of the Ascendant **handed over** its
  management to the lord of the Nth" vs "if it **accepted** the management from" it. See ¶15/¶16,
  ¶20/¶21, ¶26/¶27, ¶30/¶32, ¶43/¶47, ¶50/¶51, ¶55/¶57, ¶63/¶66.
- **Axis 2 — the house the management comes from.** "The place of the affliction is known from **the
  place of the light**" (¶52) is the general statement; ¶23, ¶35–40, ¶44–46, ¶52 and ¶70 are the
  worked expansions.
- **Axis 3 — benefic or malefic receiver.** "if the planet was a fortune… and if it was an
  infortune…" (¶20, ¶16, ¶26, ¶37, ¶38, ¶55, ¶56).

¶19 states the method for the whole appendix:

> "So look into **the aspect of one of them to the other** when the management is handed over, and
> **their aspect to the Ascendant**, and **their positions relative to the Ascendant**." — ¶19

## B2. Rules that are general, not topical

Most of the file is topic-specific interpretation (which does not generalise and which an engine
would be reproducing rather than computing). These few are stated as principles:

| ¶ | Statement |
|---|---|
| 17 | "if it connected **from a sextile or trine, it will be what he longs for** and he will see what he loves; and **the square is middling** except that the square of the third indicates that between him and his siblings and friends there will be words and reprimands." |
| 19 | The three things to look at (quoted above). |
| 52 | "**The place of the affliction is known from the place of the light.**" |
| 59–61 | On the 1st/10th pair: "know the **positions of the stakes and their power**, and the aspect of the planets in nativities… **60** if the **fortunes looked at them**, that is an increase in affection… **61** And likewise [it indicates] **enmity** and restraint … if the **infortunes looked [at] them or squared them**." |
| 63–65 | A three-grade strength scale by place: "from a **powerful** position, their owners will be powerful, well known. **64** And if the position was **middling**, they will be well known [but] will not have that strength. **65** And if the position is **falling**, they will be worthless, not known." |
| 71 | "investigate the **falling [place] and the stake**: for a falling [place] is indicative of his condition, and [as for] **the withdrawing place, it is better**." — fn. 25: *"Meaning unclear."* |

¶63–65's three grades (powerful / middling / falling) map onto the angular / succedent / cadent
division of *Introduction* Ch. 2, 31–36, but the appendix does not say so and does not name the
places. **Do not assert the mapping.**

¶17 is the one place in this appendix that grades aspects, and it grades only three
(sextile/trine good, square middling). Opposition is not mentioned.

## B3. Sect, sign gender and sign-type used as switches

Two sections use sign categories as live conditions, which ties this appendix to
*Introduction* Ch. 1:

> "if the sign was **of the images of people**, then in relation to illness and slaves; and if it
> had **four feet**, then from the yields of animals and their profit." — ¶7

> "if the sign was **female**, then in relation to women and because of them; and if it was
> **male**, then in relation to contention, hardship, and hostility." — ¶8

> "if the sign was one **having four feet**, he will buy beasts; and if it was **of the images of
> people** he will buy slaves; and if it was **neither of these two types** it will be what I
> mentioned of heaviness." — ¶33

**This is a direct consumer of the four-footed-sign list**, which §4 of
`01_introduction_ch1_ch2.md` shows is *contradicted between Sahl's own two works* (Leo vs
Capricorn). So the disagreement is not academic: this appendix's ¶7 and ¶33 give different answers
depending on which list is used. Worth recording as the first concrete downstream cost of that
contradiction.

## B4. Is this natal or horary? The text is mixed and does not resolve it

- "in **nativities**" — ¶59
- "if it was **in the root**" — ¶31, ¶33 (i.e. as against a derived chart)
- "if it was **in the revolution of the year**, it indicates his death" — ¶51 (**timing; deferred**)
- "if the **owner of the question** did not have a woman" — ¶48
- "The second half sounds like it is part of instructions for a **question chart**" — fn. 8 on ¶24

So the same short text addresses nativities, solar revolutions, and questions without partitioning
them. Any engine use must decide which chart type each section applies to, and **the text will not
supply that decision.**

## B5. The one hard timing claim, recorded and deferred

> "And if [the lord of the Ascendant] handed over the management to it, and it was **in the
> revolution of the year**, it indicates his death: **he will die in that management**." — ¶51

Followed by ¶52's placement rules for *where* death occurs. This is solar-revolution doctrine and
falls squarely inside the deferral. Recorded so it is not rediscovered as "new."

---

# PART III — Summary

## What these two appendices make newly available

| Category | Appendix A | Appendix B |
|---|---|---|
| Computable natal conditions | ~23 sections (§A2) | The 3-axis handing-over lookup (§B1) and 6 general principles (§B2) |
| Confirms machinery defined elsewhere | spear-bearing, easternization, superiority, domain, *halb* (¶49, ¶39, ¶41) | aspect quality grading (¶17); place-strength grades (¶63–65) |
| Genuinely undetermined | **¶64 [S64]** — the meridian/declination configuration (§A5) | ¶71 (fn.: "meaning unclear") |
| Editorial reconstruction — do not ship as Sahl | **¶35 [S35]** detested-connection pairs (§A3); ¶29 apodosis; ¶12, ¶13 | — |
| Internal disagreement | ¶37 [S37] vs *Nativities* Ch. 4.1 (§A4) | ¶7/¶33 depend on the contradicted four-footed list (§B3) |
| Timing — deferred | ¶19, ¶22, ¶23, ¶31, ¶34, ¶42 | ¶51 |
| Excluded by standing policy | ¶53 [S53] `⟨missing⟩` | ¶12, 20, 43, 45, 48 marks |

## Confidence note

Both appendices are **weaker evidence than the rest of the corpus**: Appendix A rests on one
consulted manuscript with a Latin centiloquy used to patch it; Appendix B has no source photographs
in the project at all and six passages its own translator marks as unclear. Where either appendix
agrees with *On Nativities* or the *Introduction*, it is corroboration. Where either stands alone,
it should not by itself justify changing engine behaviour — and where either disagrees with the
main works (¶37), the main work should win, per the project's standing source-fidelity preference
for the narrower, better-attested statement.
