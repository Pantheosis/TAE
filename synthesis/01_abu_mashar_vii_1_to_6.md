# Phase 1 — Abū Ma'shar, *Great Introduction* Book VII, Chapters VII.1–VII.6 (complete)

Source: `abu_mashar_book_vii.md`, lines 1–1809, **Abū Ma'shar's own** pagination pp. 407–484 (a
different printed volume from Sahl's Vol. I; `CORPUS_MANIFEST.md` says never to compare a bare
page number across the two files). Read end to end on 2026-09-08 in four slices, before any
`app.py` citation was opened. Figures 98–146. Companion: `01_abu_mashar_vii_7_to_9.md` covers
VII.7–9; this file closes the gap that was scoped out as "previously reconciled."

**This file has changed under its citations.** Per `DOCTRINAL_CAVEATS.md`: pp. 440, 442, 452, 453
and 477 were recovered from reshoots after earlier passes; a block mislabelled "p. 440" was moved
to its place between pp. 445 and 447; VII.5, 7 was recovered from a corrupted sentence number; a
garbled duplicate of VII.5, 9–10 was removed; Figure 146 was repaired; the Table of Contents and
fns. 1–2 were restored from a pre-merge snapshot. Every citation older than 2026-09-07 was written
against a different file. The audit of the citations is `11_abu_mashar_citation_audit.md`.

**Heading conventions (the heading trap).** Chapters are `### Chapter VII.N: …`; sub-headings are
bracketed italics or `### [Inferior planets]`. Sentence numbers are plain (`10 So as for…`) or bold
(`**10** So…`), and **restart per chapter**; VII.5 runs to ¶142. Footnotes run **continuously 1–329
across the whole book** (unlike *On Nativities*, where they restart per chapter), so "fn. 222" is
unambiguous here. Per-chapter maxima, derived from the file and checked against the reading:

| VII.1 | VII.2 | VII.3 | VII.4 | VII.5 | VII.6 | VII.7 | VII.8 | VII.9 |
|---|---|---|---|---|---|---|---|---|
| 39 | 75 | 11 | 109 | 142 | 74 | 22 | 8 | 37 |

Citation: **AM VII.N, P**.

---

## 1. VII.1 — the planets' conditions "in themselves"

Nine kinds of condition are announced (¶3–9) and worked (¶10–39):

| ¶ | Condition | Worked at |
|---|---|---|
| 3 | rising / falling in the apogee, or the middle zone | 10–13, Fig. 98 |
| 4 | increasing / decreasing in motion, light, size | 14–22 |
| 5 | adding / subtracting in number | 23–25 |
| 6 | increasing / decreasing in calculation | 26–28 |
| 7 | increasing / decreasing in travel | 29–33 |
| 8 | northern / southern, rising / falling, much / little / no latitude | 34–36 |
| 9 | in its domain or the contrary | 37–39 |

### 1a. Apogee and speed (10–13)

> "**10** … if the corrected planet is at the top of its apogee, or between it and [the apogee] are
> less than 90° to the right or left, then it is rising in the zone of the circle of its apogee
> [and] decreasing in motion … **12** But if it goes past the top of its apogee by 90° until it
> reaches exactly 270°, then it is falling from the middle of the circle of its apogee [and]
> increasing in motion (and the most it can be in motion is if it was in the opposition of its
> apogee)." — AM VII.1, 10–12 (`:79`)

### 1b. ★ "Increasing in light" has two senses, and Abū Ma'shar says which is agreed

> "**19** And if it was falling down from the middle zone of the circle of the apogee, it is
> increasing in light and size. … **22** And the three superior planets are also said to be
> increasing in light (and decreasing in it) in the manner that is said about the Moon: because when
> they go past the Sun until they oppose him, they are said to be increasing in light; but after
> that until their meeting with him, they are said to be decreasing in light (except that the first
> [way] which we stated previously is the one agreed upon [by all])." — AM VII.1, 19, 22 (`:89–91`)

So for the five planets the *agreed* sense is distance (apogee → perigee), and the synodic sense is
an admitted alternative; for the Moon it is her glow (VII.2, 62–71). `app.py:5288–5300` reads it
exactly this way.

### 1c. Number and calculation (23–28) — no astrological import

fn. 14: *"This has to do with how a planet's position in its system relates to the corrections or
equations which must be applied to it. It does not have direct astrological import."* ¶27–28 give
the "middle path" (no equation) and Venus's special case.

### 1d. ★ Rate of motion, with the inferiors excepted (29–33)

> "**29** As for increasing in its rate of movement (with respect to the five planets), it is that
> it travels more than its mean motion … **30** But as for Venus and Mercury, their mean motion in
> one day at a [particular] time is not like their mean travel for the day. **31** And indeed, the
> conditions of the motion for each of them is known by looking [at this]: if the motion of one of
> them on any of the days is more than the motion of the Sun on that day, then it is quick in
> motion, increasing in it; and if it was less than his motion, then it is slow in motion." — AM
> VII.1, 29–31 (`:113–127`)

**For Venus and Mercury the yardstick is the Sun's motion that day**, not their own mean. fn. 18
gives the interpretive gloss (fast = accomplished quickly). ¶32–33 are the *kardaja* tables.

### 1e. Latitude (34–36)

> "**34** … a northern planet, that is when it goes beyond the Head of its own Dragon until it
> reaches its own Tail … **35** And if it was exactly 90° from the Head or Tail of its own Dragon,
> then it is the greatest it can be in latitude in that direction." — AM VII.1, 34–35 (`:133`)

Each planet's **own** nodes ("its own Dragon") — which `app.py:4281` records as not computed.

### 1f. ★ Domain (37–39), with the Mars exception and the "male, not diurnal" problem

> "**37** As for 'domain,' it is that a male planet by day is above the earth (and by night below
> the earth), in a male sign; but if it was female, then by day it is below the earth (and by night
> above the earth), in a female sign—except for Mars alone, because he is contrary to what we said.
> **38** So if a planet was in this condition, it is in its domain, and it is strong in nature,
> indicative of balance and suitability. **39** But if any of what I said is taken away, it takes
> away from the nature of balance; and if it was contrary to all of this, it is in the contrary of
> its domain, and indicates corruption and the contrary of balance." — AM VII.1, 37–39
> (`:137–155`)

fn. 24: *"Instead of 'male' and 'female,' Abū Ma'shar should probably be saying 'diurnal' and
'nocturnal.' Either way, Mars will stand out because he is a male, nocturnal planet: so either he
must be in a different hemisphere (diurnal/nocturnal) or in differently-gendered sign
(male-female)."* Three grades: in domain / partly / contrary. VII.6, 13 restates the rule **without
the Mars clause** and adds "male degrees" (§6a). Compare Māshā'allāh's version, *Nativities* 1.23,
17, where the *sign's* gender follows the hemisphere (`01_on_nativities.md` §4).

---

## 2. ★ VII.2 — the planets relative to the Sun (the solar-phase chapter)

### 2a. Right and left (2–4) — the Moon is the reverse of the planets

> "**2** Now as for Saturn, Jupiter, and Mars, from the time of their separation from the Sun until
> they oppose him to the minute, they are 'on the right side' of him; and from the time of their
> opposition until they conjoin with him, they are 'on the left side' of him. **3** But as for Venus
> and Mercury, from [the time] of their separation from the Sun and they are retrograde in the region
> of the east until they go direct, become quick, overtake the Sun, and conjoin with him, they are
> 'on the right side' of him … **4** And as for the Moon, from the time of her separation from him
> until she opposes him, she is 'on the left side' of him, and when she passes beyond his opposition
> until she conjoins with him, she is 'on the right side' of him." — AM VII.2, 2–4 (`:163–187`,
> Figs. 99–101)

fn. 32 ties "right side" to spear-bearing and good luck: *"All three meanings are connected here:
being on the right side, bringing luck, and spear-bearing for the Sun."*

### 2b. ★ The superiors' seventeen conditions (6–34) — the degree table

| # | Name | Boundary (♄♃ / ♂) | ¶ |
|---|---|---|---|
| 1 | in the heart | ±16′ (Sun's disc ≈32′, "the most … close to 34′") | 7–9 |
| 2 | burned in the east | to 6° / 10° | 10–11 |
| 3 | under the rays; "advancement towards easternization … suitable for granting their greater years as well as spear-bearing" | to 15° / 18° | 12–13 |
| — | "day-limit" (Persian *kinārrūziyah*) covers conditions 1–3 | | 15 |
| 4 | proper, strong easternization, "most powerful … in easternization, spear-bearing, and being on the right side" | to 60° | 17–18 |
| 5 | weak in easternization | to 90° | 19–20 |
| 6 | after easternization | to first station | 22 |
| 7 | first station | | 23 |
| 8 | retrograde | to opposition | 24 |
| 9 | opposition ("night-limit of the opposition") | | 25 |
| 10 | retrograde | | 26 |
| 11 | second station | | 27 |
| 12 | direct | to 90° | 28 |
| 13 | inclining towards westernization | to 60° | 29 |
| 14 | westernizing | to **22° / 18°** | 30 |
| 15 | in the degrees of setting | to 15° / 15° | 31 |
| 16 | under the rays, "not suitable for granting their greater years"; "night-limit of westernization" | to 6° / 10° | 32–33 |
| 17 | burned under the rays | to the heart | 34 |

Two sentences worth having verbatim because the engine leans on them:

> "**12** When these three planets come to the completion of these degrees, then they have already
> gone past burning and shift over to the third condition, and they are said to be simply 'under the
> rays,' and from there they begin in [their] advancement towards easternization, and they are
> suitable for granting their greater years as well as spear-bearing." — AM VII.2, 12 (`:201`)

> "**16** And even though we have called these planets 'easternizing' at this time, we don't mean by
> it that they are [actually] seen in the east … but we do mean by their easternization that they
> have separated from the power of the Sun's body." — AM VII.2, 16 (`:201–213`)

**Easternization here is a degree band, not visibility** — the opposite emphasis from Sahl's 1.22,
which is a fitness/visibility discussion. ⚠ **Mars westernizes at 18° and sets to 15°** (¶30–31);
his western "under the rays" band is 15→10, so 15° west is Abū Ma'shar's figure and 18° is Sahl's
(`01_on_nativities.md` §3).

### 2c. The inferiors' sixteen conditions (35–57)

| # | Name | Boundary | ¶ |
|---|---|---|---|
| 1 | in the heart | ±16′ | 36 |
| 2 | burned (east) | to 7° ("up to", *dūn* = just under) | 37 |
| 3 | under the rays; advancement to easternization; "fit to grant the greater years and spear-bearing" | to 12° | 40 |
| 4 | strong easternization | to station | 41 |
| 5 | station | | 42 |
| 6 | direct in the east | | 43 |
| 7 | under the rays | 12° → **6°** ⚠ | 44 |
| 8 | burned under the rays | to the heart | 45 |
| 9 | in the heart | | 46 |
| 10 | burned (west) | to 7° | 47 |
| 11 | under the rays | to 15° | 48 |
| 12 | direct in the west | | 49 |
| 13 | station | | 50 |
| 14 | retrograde | to 15° | 51 |
| 15 | under the rays | to 7° | 52 |
| 16 | burned | to the heart | 53 |

⚠ ¶44 says **6°**; fn. 43: *"To me it seems this should be 7° as in 40, but this is what the text
says."* `app.py:703–706` records this. ¶38–39: **Venus at great latitude (up to 8°56′) is
"appearing," not "burned," even within 1°** of the Sun. ¶54–57 give the Persian day-/night-limits.

### 2d. The Moon's sixteen conditions (58–74)

Burned to **6°** (¶60, with the visibility reason: *"the closest she can be to the Sun when she is
seen on the equator in the signs of longest ascension"*); under the rays to **12°** (¶61, ¶72–73);
quarters by glow at 45°, 90°, 135° (¶62–64, ¶69–71); the 12° bands either side of the opposition
(¶65–66, ¶68). fn. 51 warns the 6° may be latitude-specific (*"the Persians"*). VII.6, 65–66 reuse
the 12° bands as corruptions.

---

## 3. VII.3 — quadrants and the bodies of the planets

> "**2** The first is if one is in the advancing and withdrawing quadrants of the circle. **3** The
> second is if it is in one of the houses of the circle which are the stakes. **4** The third is if
> it is in a house which follows a stake. **5** The fourth is if it is in the withdrawing houses."
> — AM VII.3, 2–5 (`:418–424`); fn. 52: *"See VI.26, 3"*; fn. 53: *"See VI.26, 5."*

The quadrant condition (¶2) and the house conditions (¶3–5) are **separate conditions** — the
basis of `ADVANCING_BY_QUADRANT_FIG90` being kept apart from Sahl's 83. The quadrants themselves are
defined at VI.26, 3 (Figure 90, a standalone capture at `:2213`), outside VII.

**Figure 105 (¶6–11):** Sun 15°, Moon 12°, Saturn and Jupiter 9°, Mars 8°, Venus and Mercury 7°,
*"in front of him, and the same behind him"* — `PLANETARY_ORBS`.

---

## 4. VII.4 — assembly, and the philosophy of mixture

### 4a. ★ Assembly is same-sign; power begins at 15°; bodies are asymmetric (2–14)

> "**3** And a planet is said to be assembling with something of what we state, if they were both in
> a single sign; and it is stronger for the indication of their assembly if there were 15° and less
> between one of them and the other, [whether] in front of it or behind it." — AM VII.4, 3 (`:454`)

> "**7** And that is like Saturn and the Moon: if they were in a single sign, and the distance
> between them both was within 12° in front of them or behind, Saturn would be in the power of the
> body of the Moon, while the Moon would not be in the power of the body of Saturn, until there is a
> little under 9° between them. **8** But if each of them was in the power of the body of its
> associate, the indication of their assembly would become strong—and if in addition they were in
> a single bound, it is more powerful in indication." — AM VII.4, 7–8 (`:458–472`, Fig. 106)

> "**13** And when the two planets are in two different signs, and each one of them is in the power
> of the body of the other by the amount of degrees, then they are *not* said to be 'united,'
> because of the difference of their signs; but rather it is said that one of them is 'in the power'
> of the other's body. **14** But due to the merging of the power of their bodies they will have an
> indication over a small matter, as compared with what they would indicate in a [proper]
> assembly." — AM VII.4, 13–14 (`:486`)

fn. 55, 139: **no out-of-sign conjunctions, no out-of-sign aspects** — repeated at VII.5, 14 and
fn. 145. ¶12: going-towards beats departing at equal distance. ¶15–16: fixed stars, nebulae, Nodes,
Lots and twelfth-parts have no body of their own; they fall in the planet's.

### 4b. Conjunctions are only apparent; qualities mix, natures do not (17–32, 93–109)

¶17–20 (Fig. 107): "uniting" is one planet being *set over against* the other. ¶21–29: the
water-and-wine objection answered — *"in their own bodies and natures they would [still] be in
their own [respective] condition, though indeed their qualities would be combined"* (¶28). ¶97–109
(Fig. 110, p. 440 recovered): the four kinds of bodily mixture (fastening, heterogeneous mixture,
aggregation, blending) and why planets do none of them: *"one of them would mix with its associate
in the quality which is contrary to the quality of the other planet"* (¶107). Not engine material;
recorded because ¶108–109 is the argument that **Saturn–Mars in two qualities "come to be of the
character of fortunes"** (fn. 127: *"they are not actually fortunes"*).

### 4c. ★ The criteria for mixing and for power (33–43)

> "**34** Now as for [1] mixing their qualities … that is known by five things. **35** The first of
> them is [1a] by the special property of their natures. **36** The second is [1b] by their rising or
> falling in the circle of the apogee. **37** The third is [1c] by their place in relation to the
> nature of their sign. **38** The fourth is [1d] by their condition relative to the Sun. **39** The
> fifth is [1e] by their condition in the quadrants of the circle." — AM VII.4, 34–39 (`:564–580`)

> "**41** … [2a] the closer of the two to the apex of the circle of its apogee is stronger in
> influence over the one farther from [its own] apex, and [2b] the northern rising one with much
> latitude is stronger than the northern rising one with less latitude than it, and [2c] the
> northern rising one is stronger than the northern falling one, and [2d] the northern one is
> stronger than the southern one, and [2e] the southern rising one is stronger than the southern
> falling one, and [2f] the southern one with less latitude is stronger than the southern one with
> more latitude." — AM VII.4, 41 (`:582`)

**Relative power in a conjunction is decided by apogee and latitude alone** — none of the
dignities. ¶43: against fixed stars, Lots, etc., only the planet's own condition counts.

### 4d. Mars–Saturn (44–64), and the synodic cycle of qualities (53–56, Fig. 108)

> "**53** … from the time of the Sun's departing from them until their first station, the nature of
> them both is changed to wetness … **54** And from their first station to their opposition to the
> Sun the nature of them both is changed to heat … **55** And after their opposition up to the second
> station the nature of them both is changed to the dry … **56** And after the second station up to
> their meeting with him, the nature of them both is changed to the cold." — AM VII.4, 53–56
> (`:626–632`)

Fig. 109 (¶59–64): mixing in two qualities (one or both wet) = moderation, *"the character of
fortunes"*; in one quality (both dry) = harshness. ¶64: even then, *"with toil, exertion, and
trouble."* fn. 88 flags the counter-intuition (Saturn–Mars in Cancer should be *more* moderated).

### 4e. ★ Conjunctions with the Sun — the harm of burning ranked (65–85)

> "**67** The most intense harm for the planets by burning is that of the Moon and Venus, because
> they are both cooling and moistening … **68** But as for Saturn and Jupiter, burning is less
> harmful to them because they both harmonize with the Sun in one of their characteristics … **69**
> And the harm for Mars and Mercury, when they are direct while being burned, is the least harmful of
> all of them, because they are both of the essence of the Sun." — AM VII.4, 67–69 (`:675–691`)

¶71–72: the malefics make the Sun *somewhat* unfortunate under his rays, Mars more than Saturn.
¶80–82: Mercury least harmed **when direct**, more when retrograde; he passes on to the Sun whatever
fortune or misfortune he carries. ¶85: *"if they were with the Sun 'in the heart' … in many matters
it indicates good fortune."* None of this ranking is in the engine's solar-phase scoring.

### 4f. The Moon with the malefics by half-month (86–89)

> "**87** But if it was in the first half of the [lunar] month her nature is heating: so should she
> mix with the cold of Saturn with her heating nature, her misfortune from Saturn will be less; and
> she [should] not mix with the heat of Mars, for her misfortune from him would be harsher. **88** And
> if it was in the last half of the [lunar] month, cold will predominate in her and her cold will mix
> with the heat of Mars so that her misfortune from him will be less." — AM VII.4, 87–88 (`:743`)

Waxing Moon: Mars worse; waning Moon: Saturn worse. ¶86: in general *"her misfortune from Saturn is
said to be harsher than that from Mars."* ¶90–92: in any union, the stronger's nature shows.

---

## 5. ★ VII.5 — the twenty-one conditions

The table at ¶1 (`:859–866`): [1] Looking, [2] Connection, [3] Separation, [4] Emptiness of course,
[5] Wildness, [6] Transfer, [7] Collection, [8] Reflection, [9] Blocking, [10] Handing over nature,
[11] Handing over power, [12] Handing over two natures, [13] Handing over management, [14]
Returning, [15] Revoking, [16] Resistance, [17] Escape, [18] Cutting the light, [19] Favor, [20]
Recompense, [21] Reception. Each is defined below with its own sentence.

### 5a. Looking (2–8, Fig. 111)

> "**2** … the LOOKING of every planet is to the given signs, and there are seven signs: the third
> sign from it, and the fourth, fifth, seventh, ninth, tenth, and eleventh. **3** And it looks at
> every degree of the sign as well as everything which is in it (of planets, Lots, and other things).
> **4** And the strongest thing there is in its looking at every one of the degrees of these signs,
> is the degree which is related most closely by number to the degree of its own sign (such as 60°,
> 90°, 120°, and 180°), in degrees of equality; and if the aspect was far from these degrees, its
> aspect will be weaker." — AM VII.5, 2–4 (`:887–893`)

fn. 130: *"This is fundamentally by whole signs."* ¶6: right = 9th/10th/11th, left = 3rd/4th/5th.
¶8: the four averse signs sum to 120°. **No orb for aspects is given here** — a continuum from the
exact degree (¶4).

### 5b. ★ Connection and separation (9–37)

> "**9** … the light one connects with one which is slower than it, and this is in eight ways: one
> of them is the connection by assembly, and seven are a connection by looking. **10** So as for the
> connection by assembly, it is that two planets are direct in motion, in a single sign, and the one
> of them light in motion is in fewer degrees than the slow one. … **12** And the beginning of the
> power of the connection by assembly, and mixing the nature of the connecting one with the
> connected one, is when there are 15° between them … **13** And this is when they are in a single
> sign. **14** But if they were in two different signs, and there were few degrees between them, that
> is not counted as a 'connection by assembly,' but they are both 'mixing their natures' in a weak
> way." — AM VII.5, 9–14 (`:917–954`)

> "**16** And if the light one passed by the slow one by one minute or by less than that, then it
> has already SEPARATED from it. **17** And if one planet separated from another by assembly, and it
> is not connecting with <another> planet, then one of them will be 'in the nature' of its partner so
> long as it is in the sign in which they united. **18** And the strongest that the mixture of their
> natures could be, is if they were both in one bound, and not distant from each other by the amount
> of one-half of the body of the one in fewer degrees." — AM VII.5, 16–18 (`:958–968`, Fig. 114)

> "**24** And sometimes at the assembly both of the two planets will be retrograde, or one of them
> will be retrograde and the other direct: the connection of one of them with the other, and its
> separation from it, will be by retrogradation." — AM VII.5, 24 (`:990`)

> "**27** And the beginning of the power of the connection by aspect is when there are 12° between
> the two planets: and the more that one of them comes near its associate by [an exact] aspect, it is
> stronger for it." — AM VII.5, 27 (`:1010`, Fig. 118)

fn. 146 (on ¶28): *"aspect rays are not given specific 'orbs,' because they are not bodies with a
glow of power around them (unlike planets). The distance of 12° may be analogous to the Moon's own
body, as the 15° distance for an assembly may be analogous to the Sun's body."* The 15/12 pair is
not a conflict — `01_abu_mashar_vii_7_to_9.md` §E settled that.

¶23 (Fig. 115–116): a union at the end of a sign carries the bodies' power into the next sign, but
*"this way of mixing their natures is weak."* ¶28: a connection can fail to complete before both
change sign (→ Escape). **¶29–31 (Figs. 119–120): priority among simultaneous connections goes to
the planet with more claims in the handing-over sign, the bound lord breaking ties** — recorded
as not implemented at `app.py:4261`. ¶32–33 (Fig. 121): a planet at the end of a sign, in aversion
to a ray at the start of the next, mixes only weakly until it changes sign. ¶34–37 (p. 452
recovered): separation at 1′; the nature persists until the next body or ray in that sign; *"the
condition of the connection by assembly is different from the condition of the connection by
looking."*

### 5c. Connection by latitude (38–52, pp. 452–454 recovered, Figs. 122–123)

Three kinds: (¶39) assembly at equal latitude, *"one of them eclipses the other"*; (¶40) opposition
with equal latitude, one rising and one descending on the same side; (¶41) the six aspects with one
rising north and the other descending south or vice versa. ¶42–45: the one with less latitude
connects when it reaches the other's latitude; separates when it exceeds it. ¶46–49: a fourth way,
with a longitude "fudge" (fn. 153). ¶50–51: Dorotheus's runaway slave — Moon to Mars in one
dimension and Jupiter in the other (fn. 154: neither 'Umar nor Hephaistion agrees with this
reading). ¶52: **the firmest connection is with one of the planet's own five lords, and firmer
still in longitude and latitude at once.** Not implemented (`app.py:4264`).

### 5d. ★ Natural connections (53–77) — equal ascensions and equal daylight

> "**53** And another type of connection and separation [even] without the planets' looking at each
> other is said to be a 'natural connection and separation,' and indeed the scholars among the
> astrologers used them … **55** But the ancients among the people of Persia, Babylon, and the
> Egyptians certainly mentioned it in their famous books known as the *Bizidajāt* … it is of two
> types: **56** One of them is from the nature of the degrees of the signs corresponding in
> ascensions, such as Aries and Pisces, Taurus and Aquarius, Gemini and Capricorn, Cancer and
> Sagittarius, Leo and Scorpio, and Virgo and Libra." — AM VII.5, 53–56 (`:1126–1128`)

The mirror rule: a planet at *x*° of one sign is in the nature of a planet at (30 − *x*)° of its
partner (¶57–66, worked for every pair). ¶67–75: the second type by *"the hours of the day"*
(antiscia; fn. 162), likewise worked. ¶76–77 (fns. 163–164): "natural opposition" pairs Gemini–
Capricorn, Sagittarius–Cancer, Aries–Virgo, Libra–Pisces; "natural sextile" pairs Gemini–Cancer,
Virgo–Libra, Sagittarius–Capricorn, Pisces–Aries — and **Dykes notes he omits Aries–Scorpio,
Taurus–Libra (¶76) and Aquarius–Capricorn (¶77)** relative to VI.6. `app.py` builds the pairs he
lists and declines to add the three (`:4268–4274`).

### 5e. Emptiness of course (78) and wildness (79–82)

> "**78** EMPTINESS OF COURSE is that a planet separates from the connection of a planet (by
> assembly or looking), and will not connect with a planet so long as it is in its [current]
> sign." — AM VII.5, 78 (`:1186`, Fig. 124)

> "**79** WILDNESS is if a planet is in a sign such that absolutely no planet looks at it: so if it
> was like that, it is called 'wild.' **80** And that happens mostly to the Moon, even though her
> connection is made with the lords of the bounds in which she is: so for as long as she is in the
> bound of a planet, she is counted as being connected with the lord of that bound." — AM VII.5,
> 79–80 (`:1194`, Fig. 125)

⚠ ¶80–82 give the Moon a **bound-lord connection** even when wild or void — a doctrine the engine
does not carry and Sahl does not have.

### 5f. Transfer (83–85), collection (86), reflection (87–89)

> "**84** One of them is that the light planet separates from the slow one, and then connects with
> another so that it transfers the nature of the one it is separating from, to the one it connects
> with. **85** And the second is that a light planet connects with a planet slower than itself, and
> that slow one connects with [yet] another planet, so that the slow planet shifts the nature of the
> light planet over to the [third] planet which it connects with." — AM VII.5, 84–85 (`:1216–1218`,
> Fig. 126)

> "**86** COLLECTION is if two planets (or more than that) connect with a single planet, so that it
> collects their light, and takes up their natures." — AM VII.5, 86 (`:1228`, Fig. 127)

Reflection ¶88 = collection for two planets in aversion, the collector then *"reflects the light of
the two to that place which it looks at"*; ¶89 = transfer for two in aversion (Figs. 128–129, fns.
170–171). Type II transfer is Abū Ma'shar's, not Sahl's (`app.py:1642`).

### 5g. ★ Blocking (90–94), with Dykes's corrections to the example

> "**91** The first of them is by assembly, and it is that three planets are in a single sign, in
> different degrees, and the heavy one has more degrees than [the other] two, so that the middle one
> blocks the one with the fewest degrees from connecting with the [first] heavy one, until it passes
> by it." — AM VII.5, 91 (`:1272`)

fn. 172: = Sahl's Blocking #1 ("Intervention", *Introduction* Ch. 3, 35–37). ⚠ fn. 173: **Abū
Ma'shar's own example (¶92) inverts Mercury and Venus**; Figure 130 uses Sahl's example instead.

> "**93** And the second type of blocking is from the manner of looking: and it is that two planets
> are in a single sign, and the light one is connecting with the heavy one, and another, [third]
> planet connects with that heavy one by looking, <but by degree it is less than the light one which
> is uniting>: thus the one with it in its sign blocks the one looking, and spoils its connection
> when the degrees of them both are the same. **94** But as for when the degrees of the one looking
> are closer to the connection [of the heavy one] than the degrees of the one joining [by body], the
> connection belongs to the one looking, because it connects with it before the one joining with it
> [by body]." — AM VII.5, 93–94 (`:1284–1290`, Fig. 131)

fn. 174: = Sahl's Blocking #3 ("Nullification", Ch. 3, 38–48); the bracketed clause is **added from
Sahl's ¶38**. fn. 176: Sahl adds that body outweighs aspect.

### 5h. The four handings-over (95–103)

- **Nature** (¶95, Fig. 132): connecting with one of one's own five lords hands that lord *its own*
  nature — fn. 178: *"an example of reception (129), but with a focus on what is being handed over."*
- **Power** (¶96, Fig. 133): a planet in its own dignity connecting hands over its own power.
- **Two natures** (¶97–100, Fig. 134): both planets have a claim in the sign (Venus→Jupiter from
  Pisces); or **same-sect planets in the place of their sect** (¶100, fn. 182: the opposite of
  "counteraction"). Not in Sahl; not modelled (`app.py:2199`, `:4275`).
- **Management** (¶101–103, Fig. 135): any connection hands over management; *"from a sextile or
  trine, and there was reception between them, that handing over is from harmony; and from the
  assembly, if there was a blending between them, it is also harmony."*

### 5i. ★ Returning (104–116) — the full tree

> "**105** One of them is if a planet connects with a planet under the rays of the Sun, so that it is
> not able to hold onto what it accepts from it, and throws it back onto it. **106** And the second
> one is if a planet connects with a retrograde planet, so that due to its retrogradation it returns
> to it what it accepted from it." — AM VII.5, 105–106 (`:1379–1381`)

With suitability (¶108–112), three ways: the acceptor receives the hander-over; the hander-over is
direct and the burned/retrograde acceptor is in a stake or succedent (both); the acceptor is
falling and the hander-over angular/succedent — *"it will improve the sought matter after the
corruption."* With corruption (¶113–116), two ways: the hander-over is falling/retrograde/burned and
the acceptor angular — *"corrupted after [its] moving forward"*; both falling or burned — *"neither
a beginning nor end"* (fn. 193: Abū Ma'shar is reading Sahl Ch. 3, 65, or its source). Only Sahl's
two manners are implemented (`app.py:4277`).

### 5j. Revoking, resistance, escape (117–119)

> "**117** REVOKING is if a planet is connecting with a planet, but before it reaches it, it
> retrogrades away from it, and its connection is nullified." — AM VII.5, 117 (`:1393`, Fig. 137)

> "**118** RESISTANCE is if there was a light planet in many degrees, and another planet heavier
> than it in fewer degrees, and a third planet lighter than that light one wanting a connection with
> the heavy one, so that the light one in more degrees goes retrograde and connects with the heavy
> one through its retrogradation—and then goes past it and there is a connection of that third one
> … with this retrograde one …, not with the heavy one." — AM VII.5, 118 (`:1423–1429`, Fig. 138)

> "**119** ESCAPE is if a planet is going towards the connection of a planet, but before it reaches
> it, the one it is connecting with shifts over to the next sign, and when the one handing over
> changes [to that next sign] there is one of the planets closer to it than [the first one], so its
> connection is with the other planet, and its connection with the first one is nullified." — AM
> VII.5, 119 (`:1435`, Fig. 139)

**The sentence about "the light one in more degrees" going retrograde is ¶118 (Resistance), not
¶120** — `app.py` cited it as 120 twice; corrected (`11_…` §5).

### 5k. Cutting of light (120–125)

Three types: (¶121–122, Fig. 140) a planet in the next sign retrogrades in and conjoins the heavy
one first — fn. 199: *"essentially resistance (118) or obstruction from the next sign"*; (¶123–124,
Fig. 141) the middle planet connects with the heavy one and passes on, leaving the light one a
different connection — *"when he is on the verge of achieving it, it will escape him"*; (¶125,
Fig. 142) transfer of light to a planet *"apart from the lord of the sought matter"* — fn. 202:
*"possible that Cutting #3 is not really a distinct category but a variation on blocking."* fn. 198
reads ¶121's verb as conjoining **by degree**.

### 5l. Favor and recompense (126–128)

> "**126** FAVOR AND RECOMPENSE is if there was a planet in its own well or fall, and a planet
> connects with it (or it connects with a planet) which is friendly towards it, or one of the lords
> of its triplicities, or [one of] the claimants in its sign, or the one handing over or the one
> accepting has testimony in its own sign: for it will pluck it out and pull it out from its well or
> fall. **127** And [the first planet] will not cease to have favor for it until the planet which had
> bestowed the favor on it falls into its own well or fall, and the other [planet] connects with it
> (or it connects with [the other]), and pulls it out of its well or fall … **128** And sometimes the
> lord of the exaltation of the sign of the planet is called the 'lord of its favor.'" — AM VII.5,
> 126–128 (`:1486–1510`, Fig. 143)

fn. 203: the wells are **Ch. V.21** — outside the corpus (`WELLED_DEGREES`, deferred). ⚠ fn. 205:
the Figure's scenarios *"are also what Sahl would call 'non-reception' (Introduction Ch. 3,
58–62)."* The helper set is wider than "dispositor": *"friendly towards it"* is included.

### 5m. ★ Reception (129–142), in two classifications

> "**129** RECEPTION is if a planet connects with a planet from the house of the one it connects with
> (or from its exaltation, bound, triplicity, or face), so that [its lord] receives it. **130** Or, a
> planet connects with a planet, and the one accepting the connection is in the house of the one
> handing over (or in the rest of its shares which we mentioned before). **131** And the strongest of
> them is the lord of the house or exaltation. **132** But if the connection is with the lord of the
> bound, the lord of the triplicity, or the lord of the face alone, it is weak unless it brings
> together the bound and triplicity, or the bound and face, or the triplicity and face: for that will
> be a complete reception. **133** And these claimants also receive by looking (without a
> connection), except that reception by connection is more powerful." — AM VII.5, 129–133
> (`:1541`, Fig. 144)

fn. 206: the reverse form (¶130) exists because *"Saturn could never be received because he is too
slow to connect with anyone (unless by retrogradation)."* fn. 207: the lesser-dignity rule (¶132)
is Māshā'allāh's per Sahl Ch. 3, 54–55.

> "**134** And if one of the two planets was in the trine of the other (or in its sextile), or in two
> signs of equal ascensions, or in two signs whose length of the day is one [and the same], or in two
> signs belonging to one [and the same] planet, then one of the two will 'receive' its associate …
> **135** And the fortunes receive each other due to the moderation of their natures, while Mars and
> Saturn each receive the other from the assembly, sextile, and trine." — AM VII.5, 134–135
> (`:1555`, p. 477 recovered)

> "**137** … strong reception, the majority of that belongs to the Moon relative to the Sun, because
> he receives her from all signs, since her glow is from him—except that his reception of her from
> the opposition is detestable. **138** But if her connection with him is from a sign in which he
> has a claim, that is two receptions … **139** And if Mercury received a planet from out of Virgo,
> that is also a strong reception. **140** And a [2] middling reception is the planets' reception of
> each other from the house, exaltation, bound, triplicity, or face. **141** (But if two met
> [together] from this, or each one of them received its associate, it is a strong reception.)
> **142** But as for the rest of what we mentioned, it is [3] below that." — AM VII.5, 137–142
> (`:1557–1579`)

⚠ **131 vs 140**: house/exaltation is "the strongest" locally and "middling" globally — fn. 216:
*"It takes two dignities or a mutual reception to be both complete and strong. (But this might be
Abū Ma'shar quibbling over details.)"* `app.py:7182` presents both, correctly, as two questions.

---

## 6. ★ VII.6 — good fortune, strength, weakness, misfortune, the Moon

### 6a. Good fortune (1–20)

Fourteen items, ¶2–14, verbatim at `:1584–1614`: aspected by the fortunes *"from the sextile,
square, or trine, or are assembled with them"* (2); infortunes in aversion (3); separating from a
fortune and connecting with a fortune (4); enclosed between two fortunes (5); in the heart (6);
Sun's trine or sextile (7); aspected by a fortunate Moon (8); *"quick in motion, increasing in
light and number"* (9); in their *halb* (10 — ⚠ fn. 222: here a synonym for dignity, *"but in
al-Qabīsī this is a sect-related rejoicing condition"*); in the bright degrees (11); received (12);
**in their domains, restated with "male degrees" and no Mars clause** (13); luminaries in the
fortunes' shares and vice versa (14).

> "**15** And these good fortunes are of three types: [1] doubled good fortune, [2] being [merely]
> fortunate, and [3] [what is] less than that. **16** … Mercury if he was in Virgo … the good fortune
> of the house, and the good fortune of exaltation. … **19** … a planet was in that house of its own
> in which its nature is moderated and agrees with it: such as Saturn in Aquarius, Jupiter in
> Sagittarius, Mars in Scorpio, Venus in Taurus, and the Sun and Moon in their own houses. **20** And
> what is [3] below that … Saturn in Capricorn, Jupiter in Pisces, Mars in Aries, Venus in Libra, and
> Mercury in Gemini." — AM VII.6, 15–20 (`:1616–1620`)

fn. 224: the moderated domiciles are the sect-matching ones (= joys by sign). This is the table at
`app.py:4419` (which cited it to VII.3; corrected).

### 6b. Strength (21–29) and weakness (30–46)

Strength, ¶22–29 (`:1636–1650`): rising in the north or northern; rising in the apogee; second
station; *"going out of the rays"*; in a stake or succedent; superiors eastern (*"and if they look
at him from the sextile it is stronger for them"*, fn. 227 → VII.2, 17); superiors in the two male
quadrants, the Sun likewise unless in Libra (fn. 228 → IV.8, 16, outside the corpus); inferiors
western or in the feminine quadrants.

Weakness, ¶31–46 (`:1656–1698`): slow; first station; retrograde (worse for the inferiors, worst
when also burned); under the rays; dark degrees; **males in a female sign or female degrees by day
under the earth and by night above** (36 — ⚠ fn. 229: this mirrors 13, so it belongs under
misfortune, not weakness); in fall; southern (fn. 230: apogee-falling missing as the parallel of
23); *"falling from the stake or [from] what follows it"* (39 — fn. 231: dynamic cadence, though
the word suggests a cadent sign); **the burned path "Libra and Scorpio," harsher 19° Libra to 3°
Scorpio "because those are the fall of the luminaries"** (40); in detriment (41); connecting with a
retrograde, corrupted, fallen or cadent planet (42); not received (43); peregrine, worse if void
with no fortune looking (44); superiors western or in the feminine quadrants, the Sun likewise
*"unless he is in the ninth: for it is his joy"* (45); inferiors *"at the beginning of their
easternization, or … in the two masculine quadrants"* (46).

### 6c. Misfortune (47–55) and enclosure (56–62)

> "**48** They are in the assembly of the infortunes, or in their opposition, square, trine, or
> sextile, and there are less than the bound of [a single] planet between them and the infortunes.
> **49** Or they are in the bounds of the infortunes, or in their houses. **50** Or one of the
> infortunes is elevated above them from the tenth or eleventh from their place (and it is bad for
> that in all of this if the infortunes were not receptive of them). **51** Or it is assembling with
> the Sun, or squaring or opposing him. **52** Or they are with the Heads of their own Dragons, or
> with their Tails, or they are with the Head or Tail [of the Moon's Dragon], and between them are 12°
> or less than that." — AM VII.6, 48–52 (`:1718–1726`)

¶53: the Sun's node orb **4°**, the Moon's 12°. ¶54–55: Head increases, Tail decreases — *"the Head
is a fortune with the fortunes, but an infortune with the infortunes; and the Tail is a fortune with
the infortunes … but an infortune with the fortunes."* fn. 234: ¶50 is "overcoming."

> "**56** And another misfortune is called 'enclosure,' and it is of two types. **57** One of them is
> if a planet is in a sign, and with it in its sign is an infortune or its rays in front of it, and an
> infortune or its rays behind it—or, the planet is separating from an infortune by assembly or
> aspect, and connecting with the other infortune, in that [same] situation. **58** And the second
> type of enclosure is if a planet is in a sign, and an infortune is in the second sign from it (by
> its body or rays), and the other infortune or its rays is in the twelfth sign from it. **59** Now if
> it was not a planet in [the sign] but the situation of the Ascendant (or the rest of the signs) was
> like that, then the Ascendant or that sign will be enclosed. **60** And in both types, if the Sun or
> one of the fortunes looked at the enclosed planet, and there was less than 7° between the planet
> and those rays, then it indicates the dissolving of that misfortune. **61** And if the enclosed
> thing was itself a sign, and the fortunes or Sun looked at it, they will dissolve that misfortune.
> **62** But if the planet or sign was enclosed by the fortunes, then that is of superior good
> fortune." — AM VII.6, 56–62 (`:1738–1750`, Fig. 145)

fn. 238: the enclosing rays or bodies are normally within 7°. ⚠ fn. 239: ¶60's *"in both types"*
*"actually … only refers to the degree-based type."*

### 6d. ★ The corruption of the Moon — eleven ways (63–74)

> "**63** And the CORRUPTION OF THE MOON is in 11 ways: **64** One of them is if she is eclipsed, and
> harsher than that is if she is being eclipsed in the sign which she was in at the root of the
> nativity of a man, or in its trine or square. **65** The second is if she was under the rays of
> the Sun, and there are 12° between her and his body in the front or in the rear. **66** The third
> is if these same degrees were between her and the minute of his opposition … **67** The fourth is
> if she was with the infortunes or they were looking at her. **68** The fifth is if she was in the
> twelfth-part of Saturn or Mars. **69** The sixth is if she was with the Head or Tail, and there are
> 12° between her and one of them. **70** The seventh is if she was southern or going down in the
> south. **71** The eighth is if she was in the burned path, and that is Libra and Scorpio. **72**
> The ninth is if she was at the end of the signs, because at that time she will be in the bounds of
> the infortunes. **73** The tenth is if she was slow in motion, and it is when she goes at less than
> her mean motion. **74** And the eleventh is if she was in the ninth house from the Ascendant."
> — AM VII.6, 63–74 (`:1766–1788`)

fn. 241: *Carmen* V.6, 3 has no square. fn. 246 on ¶74: *"offhand I'm not aware of this being a
standardly-recognized concept."* The list overlaps Sahl's ten (Ch. 3, 103–112) only partly, as
`app.py:5858` says.

**VII.6 never totals, weights or tie-breaks its conditions.** Confirmed on the full read; the
engine's "Net" is its own, as `app.py:5786` and the UI say.

---

## 7. Figures 98–146 — what each one settles

All read from the OCR (captions, tables, and the footnotes that describe them). **No diagram image
was opened**; where a figure's content exists only in the image, the row says so.

| Fig. | Illustrates | What it settles / where its content lives |
|---|---|---|
| 98 | VII.1, 10–13 speed vs apogee | image only |
| 99–101 | VII.2, 2–4 right/left of the Sun | image only; the text is complete without them |
| 102–104 | the three synodic cycles | image only; the degree tables in §2 are from the text |
| 105 | VII.3, 6–11 bodies | **in the OCR as a table** (`:428–434`): 15/12/9/8/7 |
| 106 | VII.4, 5–8 asymmetric bodies | image; fn.-free; the text carries the Saturn–Moon example |
| 107 | VII.4, 17–20 apparent union | image; fn. 61 describes it |
| 108 | VII.4, 53–56 cycle of simple principles | image; the text gives the four arcs |
| 109 | VII.4, 59–64 Mars–Saturn | **in the OCR as a table** (`:644–650`) |
| 110 | VII.4, 97–109 kinds of mixture | **in the OCR as a table with three bullet conclusions** (`:787–797`) |
| 111 | VII.5, 2–7 Saturn looking | fn. 134 names the averse signs from Aquarius |
| 112 | VII.5, 10–13 assembly | image |
| 113 | VII.5, 14, 23, 32 mixing across signs | image |
| 114 | VII.5, 18 | fn. 141: Moon still in Saturn's nature within 9° and the same bound |
| 115–116 | VII.5, 23 | fn. 143–144: union at 29° Sagittarius; bodies extend to 8°/11° Capricorn; Moon at 9° Capricorn is beyond Saturn's body |
| 117–118 | VII.5, 25–27 | fn. 145: **no out-of-sign aspects** (27° Aquarius / 1° Taurus example) |
| 119–120 | VII.5, 29–30 priority | fns. 147–148: the dignities counted (Saturn: exaltation, face, triplicity vs Mercury: bound, triplicity); *"an example of reception"* |
| 121 | VII.5, 32–33 | fn. 149; the degrees `app.py:4298` quotes (29°59′ Aquarius, 1° Pisces) are **in the image only** |
| 122–123 | VII.5, 39–41 latitude | **image absent; bracketed text placeholders** (`:1072`, `:1088`) give the positions |
| 124 | VII.5, 78 | fn. 165 |
| 125 | VII.5, 79 | fn. 166: *"in aversion to all other planets"* |
| 126 | VII.5, 83–85 | fns. 167–168: both transfer types in one chart |
| 127–129 | VII.5, 86–89 | fns. 169–171 |
| 130 | VII.5, 91–92 | ⚠ fn. 173: **Sahl's example, because Abū Ma'shar's inverts Mercury and Venus** |
| 131 | VII.5, 93–94 | fn. 176: Sahl's example; body outweighs aspect |
| 132–135 | VII.5, 95–103 handings-over | fns. 178–179, 185 |
| 136 | VII.5, 104–114 returning | fns. 187–188: both branches in one chart |
| 137–139 | VII.5, 117–119 | fns. 196–197 |
| 140–142 | VII.5, 121–125 | fns. 199, 201–202 |
| 143 | VII.5, 126–128 | fn. 205: **= Sahl's non-reception** |
| 144 | VII.5, 129–130 | fn. 206: both directions of reception in one chart |
| 145 | VII.6, 56–57 | fn. 238: 7° |
| 146 | VII.8 planetary years | in the 7–9 artifact; repaired 2026-09-07 |
| 61, 90 | supplementary captures at `:2181`, `:2213` | Fig. 61 is **Abū Ma'shar's p. 306**, not Sahl's |

Figures decided nothing here that the prose left open, with one exception already known:
**Fig. 142 (fn. 202) shows a degree-connection cutting a bare sign-aspect**, and fn. 202 itself
doubts Cutting #3 is distinct from Blocking #2.

---

## 8. Internal disagreements, collected

| # | Item | Statements |
|---|---|---|
| 1 | Inferiors' inner "under the rays" limit | VII.2, 40 = 7°; VII.2, 44 = 6°; fn. 43 suspects 44 |
| 2 | "Increasing in light" | VII.1, 19 (apogee, "agreed upon") vs VII.1, 22 (synodic, allowed) |
| 3 | Domain: male/female vs diurnal/nocturnal | VII.1, 37 "male" with the Mars exception; fn. 24; VII.6, 13 restates with no Mars clause and adds "degrees" |
| 4 | *halb* | VII.6, 10 = a dignity synonym; fn. 222: al-Qabīsī's sect-and-hemisphere condition |
| 5 | Category of VII.6, 36 | listed as weakness; fn. 229: it mirrors 13 and should be misfortune |
| 6 | Category of VII.6, 38 / 39 | fn. 230 (apogee parallel missing), fn. 231 (dynamic vs sign cadence) |
| 7 | Reception grades | 131 "strongest" (house/exaltation) vs 140 "middling"; fn. 216 |
| 8 | Handing over nature vs reception | fns. 178, 206: the same thing described twice |
| 9 | Favor/recompense vs Sahl's non-reception | fn. 205 |
| 10 | Blocking #1 example | ¶92 inverts the planets; fn. 173; Fig. 130 uses Sahl's |
| 11 | Cutting #3 vs Blocking #2 | fn. 202 |
| 12 | Enclosure dissolution scope | ¶60 "in both types"; fn. 239: degree type only |
| 13 | Moon's node orb | VII.6, 52 (12° for all), 53 (Sun 4°, Moon 12°); Sahl *Nativities* 1.21, 12 (Tail 12°) |
| 14 | The Moon's 6° | VII.2, 60 with a latitude-specific reason (fn. 51); Sahl 1.19, 6 has 15° for her fitness |
| 15 | Mars's western orb | VII.2, 30–31 = 18→15; Sahl 1.22 table westernizes at 18 |
| 16 | Dorotheus's runaway | VII.5, 51 vs 'Umar vs Hephaistion (fn. 154) |
| 17 | Eclipse corruption | VII.6, 64 adds the square that *Carmen* lacks (fn. 241) |
| 18 | Ninth-house corruption | VII.6, 74; fn. 246 knows no parallel |
| 19 | Assembly 15° vs aspect 12° | VII.4, 3 / VII.5, 12 vs VII.5, 27 — not a conflict (fn. 146; 7–9 artifact §E) |
| 20 | Natural-connection pairs | VII.5, 76–77 omit three pairs that VI.6 has (fns. 163–164) |

---

## 9. Where the engine stands (pointer)

`11_abu_mashar_citation_audit.md` audits all 200 citing lines. Five citation defects were found and
corrected (two "VII.5, 120" for 118; "VII.3, 19–20" for VII.6; a wrong al-Qabīsī note locator; a
wrong recovery page). No value changed. Doctrine in VII.1–6 the engine does not carry, already in
`NOT_IMPLEMENTED_COVERAGE`: priority (29–31), latitude (38–52), the omitted natural pairs, two
natures (97–100), the returning tree (104–116), the degrees (VII.6, 13/36), own nodes (52). Not in
that list and not in the engine: the burning-harm ranking (VII.4, 65–85), the Moon's half-month
rule with the malefics (VII.4, 86–89), the apogee/latitude power ranking (VII.4, 41), and the wild
Moon's bound-lord connection (VII.5, 80–82).

## 10. Not synthesized

VII.4's mixture philosophy (¶17–32, 93–109) beyond what is needed to read the Mars–Saturn doctrine;
the *kardaja* tables (VII.1, 32–33); the Persian day-/night-limit terminology beyond the table.
VII.7–9 are in `01_abu_mashar_vii_7_to_9.md`.
