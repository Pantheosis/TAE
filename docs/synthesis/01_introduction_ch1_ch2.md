# Phase 1 — Sahl, *The Introduction*, Chapters 1–2

Source: `sahl_introduction_zodiac_chapters.md`, Sahl Vol. I pp. 41–51.
Ch. 1 = "Categories of the signs" (¶2–41). Ch. 2 = "The essences of the twelve houses" (¶2–60).
Figures: Sahl 3–8. Read without reference to `app.py`.

Citation convention in this file: **Intro Ch. 1, N** / **Intro Ch. 2, N** for this work;
**Nat. Ch. X.Y, N** for `on_nativities.md`. Paragraph numbers restart per chapter and collide
across works.

---

## 1. Sign gender alternates from Aries, and is tied to sect

> "Know that six of the twelve signs are masculine, and six feminine. **3** So Aries is a
> masculine sign, diurnal, and Taurus a feminine sign, nocturnal; and likewise the masculine
> follows the feminine, and the feminine the masculine, up to the end of the signs."
> — Intro Ch. 1, 2–3

Stated once, without qualification. Note that gender and sect are asserted as one property
here (masculine **=** diurnal, feminine **=** nocturnal), not two.

No figure. No contradiction found elsewhere in the corpus.

---

## 2. Crooked and straight signs — and the figure says something the prose does not

Prose:

> "Now the ones straight in rising are from Cancer to the end of Sagittarius: and it is that
> the breadth of each of these signs is greater than its length, and arises in more than two
> equal hours: so because of that they are called 'straight in rising.' **6** And those crooked
> in rising are from Capricorn to the end of Gemini … and arises in less than two equal hours"
> — Intro Ch. 1, 5–6

The prose states **only the northern case**, and states it flatly, with no mention of latitude.

**Figure 3 (p. 41) disagrees by adding a condition the prose lacks.** The wheel is halved on the
Capricorn/Cancer axis and each half carries *two* labels:

| Half | Signs | Figure 3 label |
|---|---|---|
| Cancer → Sagittarius | ♋ ♌ ♍ ♎ ♏ ♐ | **Straight (N. lat.)** / **Crooked (S. lat.)** |
| Capricorn → Gemini | ♑ ♒ ♓ ♈ ♉ ♊ | **Crooked (N. lat.)** / **Straight (S. lat.)** |

So the classification **inverts in the southern hemisphere**. This is Dykes's figure, not Sahl's
sentence — the prose supports only the N. lat. row. But the astronomy is not in doubt (ascensional
times are a function of the observer's latitude), and the figure is unambiguous.

**Status: figure supplements prose — and the glossary states it in words.** The latitude
inversion is *not* figure-only: `sahl_glossary.md` p. 776 (*Crooked/straight*) says it outright —
*"In the northern hemisphere, the signs from Capricorn to Gemini are crooked (but in the southern
one, straight); those from Cancer to Sagittarius are straight (but in the southern one, crooked)."*
So it is attested twice, in two independent places, though both are Dykes rather than Sahl.

An engine that hard-codes Cancer–Sagittarius as "straight" is right for northern births and wrong
for southern ones, and the corpus contains the correction — in the figure and the glossary, not in
Sahl's sentence. Do not cite Intro Ch. 1, 5–6 for the latitude-dependent rule; cite Figure 3 and the
glossary entry.

---

## 3. Quadruplicities, with reasons

> "four of them are 'convertible,' and they are Aries, Cancer, Libra, and Capricorn."
> — Intro Ch. 1, 7
> "four of them are 'fixed,' and they are Taurus, Leo, Scorpio, and Aquarius." — Ch. 1, 9
> "four of them have two bodies, and they are Gemini, Virgo, Sagittarius, and Pisces." — Ch. 1, 11

Standard, stated once, no figure, no disagreement. The reasons given are seasonal (¶8, 10, 12),
not structural.

---

## 4. Four-footed signs — **Sahl contradicts Sahl**

> "And of them are those having four feet: and they are Aries, Taurus, and the beginning of
> Capricorn, and the end of Sagittarius." — Intro Ch. 1, 13

Dykes's own fn. 5 to this sentence reads, in full: *"But see Nativities Ch. 1.38, 1."* That
cross-reference is a warning, and it pays out:

> "The signs having two feet and four: Gemini, Libra, and Aquarius have two feet; **Aries, Leo,
> Taurus have four feet**; and the ⟨first⟩ half of Sagittarius has two feet, and the other has
> four feet." — Nat. Ch. 1.38, 1

| | Intro Ch. 1, 13 | Nat. Ch. 1.38, 1 |
|---|---|---|
| Aries | four-footed | four-footed |
| Taurus | four-footed | four-footed |
| **Leo** | *not listed* | **four-footed** |
| **Capricorn** | **beginning four-footed** | *not listed* |
| Sagittarius | end four-footed | second half four-footed (agrees) |
| Two-footed | *no list given* | Gemini, Libra, Aquarius |

Leo and Capricorn are the disagreement. **Do not merge the two lists.** Neither text gives the
union, and the union is exactly the "completing a pattern the text leaves incomplete" failure the
brief warns against. If the engine needs four-footed signs it must pick a work and say which.

---

## 5. Dark signs and the burned place — the two works agree

> "And of them are signs which are said to be dark, and they are **Libra and Capricorn**."
> — Intro Ch. 1, 18
> "The signs of darkness are Libra, Capricorn." — Nat. Ch. 1.38, 8

> "And of them is a place called the 'burned place,' and it is **the end of Libra and the
> beginning of Scorpio**." — Intro Ch. 1, 19
> "And the burned place of the signs is the end of Libra and the beginning of Scorpio."
> — Nat. Ch. 1.38, 9

Stated twice, identically, in two separate works. These are the two most securely attested
sign-categories in this chapter. Note that **no degree bounds are given for the burned place** in
either statement — "the end of Libra and the beginning of Scorpio," nothing more. Dykes's fn. 7
only supplies the Latin name (*via combusta*).

**Degrees for it do exist in the corpus, but only in the glossary, and only as competing opinions
not attributed to Sahl** (`sahl_glossary.md` p. 774, *Burnt path*): *"Some astrologers identify it
as between **15° Libra and 15° Scorpio**; others between the exact degree of the fall of the Sun in
**19° Libra** and the exact degree of the fall of the Moon in **3° Scorpio**."* So a numeric span is
an **interpretive choice between two named alternatives**, and neither is Sahl's. See
`01_sahl_glossary.md` §1d.

---

## 6. Voice signs — **Sahl contradicts Sahl, and Nativities contradicts itself**

Intro:

> "And of them are signs which are said to have half a voice, and they are **Capricorn, Aquarius,
> and Virgo**. **21** And of them, signs having [full] voices, and they are **Aries, Taurus, Gemini,
> Leo, Libra, and Sagittarius**. **22** And of them, signs which do not have a voice, and they are
> **Cancer, Scorpio, and Pisces**." — Intro Ch. 1, 20–22

*On Nativities*, which Dykes cross-references at fn. 8 and again at Nat. fn. 520 ("Cf. Introduction
Ch. 1, 20-22"):

> "indeed, the voiced signs with a powerful voice are **Gemini, Virgo, and Libra**. **26** And those
> with a balanced voice are those having half a voice: they are **Aries, Taurus, Leo, and
> Sagittarius**. **27** And those weak of voice are **Capricorn and Aquarius**. **28** And those which
> do not have a voice are **Cancer and its triplicity**." — Nat. Ch. 1.38, 25–28

These are not the same scheme:

| Sign | Intro Ch. 1, 20–22 | Nat. Ch. 1.38, 25–28 |
|---|---|---|
| Gemini, Libra | full voice | powerful voice |
| **Virgo** | **half voice** | **powerful voice** |
| Aries, Taurus, Leo, Sagittarius | full voice | balanced / half voice |
| Capricorn, Aquarius | half voice | weak voice |
| Cancer, Scorpio, Pisces | no voice | no voice (= "Cancer and its triplicity") |

Three classes in the *Introduction*, four in *On Nativities*. **Virgo moves from the bottom class
to the top class.** Aries, Taurus, Leo and Sagittarius are demoted from full to half. Only the
mute signs are stable.

And *On Nativities* then contradicts itself within the same chapter, which Dykes flags at fn. 519:

> "The signs indicating yelling and lying … are Gemini, Virgo, Libra, Scorpio, Sagittarius, and
> **Pisces**" — Nat. Ch. 1.38, 21
> fn. 519: *"But see 28, as Pisces is a sign lacking a voice."*

**Do not implement a voice-sign classification without naming which of the two schemes it is.**

---

## 7. Barren and fertile signs — agreement on fertile, disagreement on barren

> "And of them are signs of barrenness, few in children: and they are **Aries, Leo, and Virgo**.
> **24** And of them are signs of many children, and they are **Cancer, Scorpio, and Pisces**."
> — Intro Ch. 1, 23–24

> "**14** … Cancer, Scorpio, and Pisces are of many children. **15** A middling amount of children:
> Taurus, Gemini, Libra, Capricorn, Aquarius. **16** The barren ones: **Leo, Virgo, and
> Sagittarius**. **17** Some scholars said that Capricorn and Aquarius are barren, not having
> children." — Nat. Ch. 1.38, 14–17

- **Fertile:** Cancer, Scorpio, Pisces in both. Securely attested twice.
- **Barren:** Leo and Virgo in both. **Aries** is barren in the *Introduction* only; **Sagittarius**
  is barren in *On Nativities* only. Aries is not classified at all in the *Nativities* list.
- *On Nativities* ¶17 contradicts its own ¶15 (Capricorn/Aquarius: middling, or barren?) and
  reports it as a competing scholarly opinion rather than resolving it.

There is a further layer Dykes marks as **not Arabic at all**:

> fn. 10: *"The Latin adds an extra sentence, making Libra, Sagittarius, and Capricorn be sterile
> as well, and that Taurus, Gemini, and Aquarius are middling."*

That sentence is a Latin-tradition accretion, absent from the Arabic. It should not be quoted as
Sahl.

---

## 8. Triplicities: lords, humors, and directions — Figure 4

Prose ¶34–41 and Figure 4 (p. 44) give the same thing; the figure is a table, and it matches the
prose cell for cell.

| Triplicity | Day | Night | Partner | Quality | Humor | Direction |
|---|---|---|---|---|---|---|
| ♈ ♌ ♐ | ☉ | ♃ | ♄ | hot, dry | yellow bile | east |
| ♉ ♍ ♑ | ♀ | ☽ | ♂ | cold, dry | black bile | **south** |
| ♊ ♎ ♒ | ♄ | ☿ | ♃ | hot, moist | blood | **west** |
| ♋ ♏ ♓ | ♀ | ♂ | ☽ | cold, moist | phlegm | **north** |

> "The lords of this first triplicity are by day the Sun, by night Jupiter, and their partner by
> night and by day is Saturn." — Intro Ch. 1, 35

The lords are the standard Dorothean set. The **directions** are worth noting because they are not
the modern element→direction mapping: earth is south and air is west here, and fire is east.
Stated once each, no cross-reference, no figure beyond the lord table.

Note also the triplicity *significations* at ¶14–17 and ¶29–33 (fire → fire and jewels; earth →
vegetation and cultivation; air → "people and winds"; water → moisture), which are the semantic
basis for the mundane/topical lists rather than a dignity rule.

---

## 9. Houses: two ranking systems, and the second one is partly Dykes's reconstruction

Sahl gives **two distinct schemes** and does not merge them.

### 9a. The 8-place system — presence and power (Intro Ch. 1 [sic Ch. 2], 30–36)

> "Four of them are called the 'stakes,' and they are the sign of the Ascendant, the fourth, the
> seventh, and the tenth. **32** And these stakes indicate what is already present of matters …
> **33** And four of them are said to be what follows the stakes (that is, rising up to them), and
> they are the second from the Ascendant, the fifth, the eighth, and the eleventh. **34** And they
> indicate what is coming to be of matters. **35** And four of them are said to be falling from the
> stakes … the third sign from the Ascendant, the sixth, the ninth, and the twelfth. **36** And they
> indicate what has already elapsed and passed away" — Intro Ch. 2, 31–36

**Figure 5 (p. 48) agrees exactly.** I read the shading directly: grey = 1, 2, 4, 5, 7, 8, 10, 11
— stakes plus succedents. The eighth *is* included here, despite being called a place of "intense
misfortune" twenty lines later (¶46). That is the point of having two systems: this one grades
**presence/power**, not goodness. Temporal significations (present / coming / elapsed) attach to
angular / succedent / cadent respectively.

### 9b. The 7-place system — goodness (Intro Ch. 2, 37–45)

> "And the strongest of the places of the circle is the Ascendant … **38** Then the Midheaven
> follows that in power (and it is the tenth). **39** Then the stake of the west follows that …
> **40** Then the stake of the earth … **41** Then the eleventh sign from the Ascendant follows
> that in power. **42** Then the ninth sign follows that, because it is the house of the joy of the
> Sun. **43** Then the fifth sign from the Ascendant follows that. **44** And these seven places are
> praised, powerful; and the first one [mentioned] is better than the second one, and the second one
> better than the third one." — Intro Ch. 2, 37–44

Order: **1 > 10 > 7 > 4 > 11 > 9 > 5.**

**Figure 6 (p. 48) agrees**: I read the shading as grey = 1, 4, 5, 7, 9, 10, 11 — the same seven.
Figure 7 (p. 49) tabulates it against *Carmen*:

| | Good | | | | | | | Middle | | Bad | | |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| Sahl | 1 | 10 | 7 | 4 | 11 | 9 | 5 | 3 | 2 | 8 | 6 | 12 |
| *Carmen* I.5 | 1 | 10 | 11 | 5 | 7 | 4 | 9 | 3 | 2 | 8 | 6 | 12 |

Then the middle pair:

> "the third sign from the Ascendant is preferred because it is the place of the Moon's joy; then
> the second place from the Ascendant, because it rises up toward the Ascendant."
> — Intro Ch. 2, 45

And the bad three:

> "as for the eighth sign … intense misfortune is in it, because it is the sign of death, and does
> not look at the Ascendant. **47** And as for the remaining two signs … (and they are the sixth and
> the twelfth …), they are the most bad of the places and the most evil of them, and **every planet
> in these two places has no benefit**." — Intro Ch. 2, 46–47

Full Sahl ranking: **1, 10, 7, 4, 11, 9, 5, 3, 2, 8, 6, 12.**

### ⚠ 9c. ¶42–43 is an editorial construction, not a manuscript reading

This must be marked. Dykes's fn. 42:

> "**42-43** is a construction from **H** and **L** (which read alike), and **B**, and follows on the
> discussion of the relative superiority of the places earlier in the chapter. **B** has the fifth
> followed by the ninth, with the explanatory note about the Sun's joy (which no other manuscript
> has). **H** and **L** have the ninth, followed by the fifth."

So the manuscripts split on **9th vs 5th**:

| Witness | Order |
|---|---|
| **B** | … 11, **5, 9** … (and carries the Sun's-joy note) |
| **H**, **L** | … 11, **9, 5** … (no Sun's-joy note) |
| **BL** | omits the ninth entirely — Dykes sets it aside |
| **Dykes's printed text** | … 11, **9, 5** … *plus* B's Sun's-joy note |

Dykes's text is a **conflation**: H/L's order with B's explanatory note, justified by a symmetry
argument (ninth-over-fifth mirrors third-over-second, each a cadent place promoted by a luminary's
joy). It is a good argument. It is still not what any single manuscript says.

**Classification: interpretive choice, not a correction.** The alternative is B's `1, 10, 7, 4, 11,
5, 9`. Figure 6's shading cannot arbitrate — it shades all seven places and does not rank them, and
it is Dykes's own figure besides.

### 9d. The joys, and one of them is supplied from the Latin

Four joys are used, and each is used *as the reason* for a place's rank:

| Place | Joy | Attestation |
|---|---|---|
| 9th | Sun | Intro Ch. 2, 42 — but **only in manuscript B** (fn. 42) |
| 3rd | Moon | Intro Ch. 2, 45 — in the Arabic |
| 6th | Mars | Intro Ch. 2, 48 — **inside `⟨ ⟩`; supplied from the Latin** |
| 12th | Saturn | Intro Ch. 2, 49 — in the Arabic |

> "and it falls away from the Ascendant, not looking at it, ⟨and it is the joy of Mars⟩."
> — Intro Ch. 2, 48, with fn. 43: *"Adding with the Latin version, and in parallel with 49."*

Mercury's joy in the 1st and Venus's in the 5th are **not in this chapter at all**. The corpus here
gives four joys, two of them securely, one manuscript-restricted, one Latin-supplied. Do not
present a complete seven-joy scheme as resting on this passage.

---

## 10. House significations

Given tersely, one or two sentences each (Intro Ch. 2, 4–29). Dykes warns at fn. 15 that these
lists are short in Arabic and long in Latin, and that he believes **the Latin translator padded
them**:

> "After the Ascendant, the Arabic lists of house significations are extremely short, but the Latin
> ones are much longer. I believe that instead of having a separate, more detailed manuscript, the
> Latin translator used his knowledge of many of the topics Sahl handles later, to add to the
> Arabic lists here. He probably also added significations from other sources." — fn. 15

So the *short* list is the authentic one. Condensed:

| H | Sahl's own words (Intro Ch. 2) |
|---|---|
| 1 | "life and death"; "the body and what comes from the contingent, or every apparent thing and event, and what is set into motion, and speech, and the beginning of a matter" (5–6) |
| 2 | "assets, assistants, profiting, and labor" (8) |
| 3 | "brothers and sisters, close companions, travel, and relatives" (10) |
| 4 | "the outcome, fathers, buildings, lands, and everything which is hidden under the earth" (12) |
| 5 | "children and all of what is hoped for with that" (14) |
| 6 | "illness and slaves" (16) |
| 7 | "women, wars, lawsuits, and every transaction between two people, and the seeker and the one sought" (18) |
| 8 | "death, inheritances, and everything that has already perished, general evil, grieving, destruction, and something demanded back, and the allies of one who is sought" (21) |
| 9 | "travel, religion, the knowledge of God and the matter of the hereafter, invisible things, piety, and what has already transpired of matters, and withdrawing, and what is distant" (23) |
| 10 | "the Sultan, and the property which was already stolen and disappeared, magistrates and those in charge, and works and professions" (25) |
| 11 | "friends, hope, good fortune, the assets of the Sultan and his land tax, and his assistants" (27) |
| 12 | "enemies, downfalls, travel, the wicked, prison, and riding animals" (29) |

Two structural remarks Sahl makes that are *rules*, not significations:

- **The 7th is the Ascendant's enemy by position**: "this sign (and every planet which is in it) is
  the enemy of the Ascendant, for it is contrary to the Ascendant." (Ch. 2, 19)
- **Aversion is given as the reason a place is bad**, repeatedly: the 2nd "does not look at the
  Ascendant" (7); the 6th "falls away from the Ascendant, not looking at it" (15, 48); the 8th
  "does not look at the Ascendant" (46); the 12th "falls away from the Ascendant, not looking at it"
  (28, 49). The house ranking is derived from aspect geometry, not asserted independently.

Note "travel" appears in the 3rd, 9th **and** 12th; the corpus does not disambiguate.

---

## 11. Aspects

### 11a. The five configurations

> "'Looking': and that is the union, sextile, square, trine, and opposition." — Intro Ch. 2, 50

### 11b. Assembly has a 12° limit, and a direction

> "As for the union (and it is the assembly), indeed that comes to be if two planets were in one
> sign, **the heavy one in front of the light one**, and between the two of them in terms of degrees
> are **12° and what is less than that**: for that is the limit of the assembly." — Intro Ch. 2, 51

Two separate claims in one sentence, and they should not be collapsed:

1. **12° is the outer limit of assembly.** Dykes's fn. 45 derives it rather than dogmatising it:
   "in Ch. 3, 14 he points out that the Moon's body … is 12° on either side. Since she has the
   second-largest body besides the Sun (15°), the largest distance between two planets whose bodies
   *both* touch each other is indeed 12°."
2. **"the heavy one in front of the light one"** — a *directional* condition on the pair. Sahl does
   not restate it, and does not say what a same-sign pair inside 12° in the opposite arrangement is.
   Flagging, not resolving.

Also: assembly is **within one sign**. The 12° figure is a maximum inside that constraint, not an
orb that reaches across a sign boundary.

### 11c. First and second aspects (dexter / sinister)

> "the aspect of the sextile … it is if a planet looks at a planet from the third sign in front of
> it (and it is called the aspect of the **first sextile**), and it looks at it from behind it, from
> the eleventh sign (and it is called the aspect of the **second sextile**)." — Intro Ch. 2, 52

Same construction for square (4th / 10th, ¶53) and trine (5th / 9th, ¶54). Opposition is the 7th
and has no first/second (¶55). Summarised by Sahl himself at ¶56.

fn. 46 gives the equivalence and immediately undercuts its own reliability:

> "A 'first' aspect is a right or 'dexter' aspect cast backwards in the order of signs … a 'second'
> aspect is a left, 'sinister' aspect cast forwards in the order of signs … **But the texts are not
> always consistent.** For example, in Sahl's mundane example in *Scito* Ch. 95 …, Mercury is in
> Aries, and Sahl says he casts his 'second' trine backwards to Sagittarius; according to the
> definition here, that should be Mercury's 'first' trine."

**The counterexample is from a work outside this corpus** (*Scito*, in AW1), so it cannot be
checked here. Record the definition as ¶52–56 gives it, and record that Dykes says Sahl himself
violates it elsewhere.

### 11d. Strength of aspects — two independent axes

Axis 1, by configuration:

> "And the strongest of these aspects is the assembly and the opposition—and [the opposition] is the
> more intense by place, and the more extreme, and this aspect indicates enemies and fighters, and
> contrariety and contention. **58** And the aspect of the square is the middle of the aspect [of the
> opposition], not openly proclaiming hostility." — Intro Ch. 2, 57–58

Axis 2, by direction:

> "And the aspect of the **second** sextile is **stronger** than the first, and the second square is
> stronger than the first square, and the second trine is stronger than the first trine (and this
> aspect is called 'superiority')." — Intro Ch. 2, 59

These are orthogonal and both are stated flatly. ¶57–58 rank *which* aspect; ¶59 ranks *which side*
the same aspect is cast from.

**This checks out against Sahl's own glossary**, which is the referent of fn. 49 ("See Overcoming in
the Glossary"):

> "**Overcoming.** When a planet is in the eleventh, tenth, or ninth sign from another planet (i.e.,
> in a superior **sextile, square, or trine**); being in the tenth sign is considered **decimation**,
> a more domineering or even harmful position." — `sahl_glossary.md`, p. 787

The 11th/10th/9th of the glossary are exactly the "second" positions of ¶52–54. So *superiority*
(الاستعلاء) in ¶59 and *overcoming* in the glossary are the same relation, stated twice, in two
places, consistently. The glossary adds one thing ¶59 does not: **decimation**, the 10th-sign case
singled out as "more domineering or even harmful."

L's marginal note at fn. 48 adds a benefic/malefic gloss that is **not Sahl's text**:
"The trine and sextile indicate the easiness of the matter and the pleasantness of the mind. The
square and opposition indicate difficulty and hindering."

### 11e. Aversion

> "And as for the signs which do not look at each other, and if a planet was in them it does not
> look at [another] planet, they are the second sign, the sixth sign, the eighth sign, and the
> twelfth sign, and what is equivalent to these four: for they are adversarial."
> — Intro Ch. 2, 60

fn. 50: *"aversion occurs between any signs which have the relationship of being in the second,
sixth, eighth, and twelfth from each other: see Ch. 3, 26."* — i.e. the relation is symmetric, and
"what is equivalent" means the 12th/8th/6th/2nd counted the other way.

**Figure 8 (p. 50) is a clean worked test case and it agrees with the prose exactly.** Jupiter in
Sagittarius; I read the wheel directly:

| Relation | Signs marked in Figure 8 | Expected from ¶52–56, 60 |
|---|---|---|
| Sextile ✳ | Libra, Aquarius | 3rd and 11th from ♐ ✓ |
| Square □ | Virgo, Pisces | 4th and 10th ✓ |
| Trine △ | Leo, Aries | 5th and 9th ✓ |
| Opposition ☍ | Gemini | 7th ✓ |
| **Aversion (grey)** | **Capricorn, Taurus, Cancer, Scorpio** | 2nd, 6th, 8th, 12th ✓ |

One caption/figure mismatch, minor: the caption names only Jupiter, but the Sagittarius wedge
**also contains Mars** (verified by crop). The figure does not say why; presumably co-presence.
Nothing in the aspect pattern depends on it.

---

## 12. Internal disagreements, collected

Recorded rather than resolved, per the brief.

| # | Doctrine | The disagreement |
|---|---|---|
| 1 | Four-footed signs | Intro Ch. 1, 13 has Capricorn (beginning) and omits Leo; Nat. Ch. 1.38, 1 has Leo and omits Capricorn. Dykes's fn. 5 points at it without resolving. |
| 2 | Voice signs | Intro Ch. 1, 20–22 (3 classes) vs Nat. Ch. 1.38, 25–28 (4 classes). **Virgo is half-voiced in one and powerful-voiced in the other.** |
| 3 | Voice signs, again | Nat. Ch. 1.38, 21 lists Pisces among yelling signs; ¶28 makes Pisces mute. Dykes's fn. 519 flags it. |
| 4 | Barren signs | Aries barren in Intro Ch. 1, 23 only; Sagittarius barren in Nat. Ch. 1.38, 16 only. |
| 5 | Fertility of Cap/Aqu | Nat. Ch. 1.38, 15 (middling) vs ¶17 ("some scholars said… barren"). Reported unresolved in the source. |
| 6 | 9th vs 5th in the ranking | Manuscripts H/L vs B. Dykes prints a conflation (§9c above). **Interpretive choice.** |
| 7 | 8-place vs 7-place | The 8th house is a *good/powerful* place in the 8-place system (¶33, Fig. 5) and a place of "intense misfortune" in the 7-place system (¶46). Not a contradiction — two different questions — but an engine that keeps only one "house strength" number silently picks one. |
| 8 | First/second aspects | ¶52–56 define them; fn. 46 says Sahl uses them the other way round in *Scito* Ch. 95. Cannot be checked in this corpus. |

## 13. Editorial supplements — present in the printed text, absent from the Arabic

Anything below is **not Sahl's Arabic** and must not be cited as though it were.

| Passage | What was added | Source of the addition |
|---|---|---|
| Intro Ch. 1, 12 | "[and *vice versa*]" | Dykes, from the Latin (fn. 4) |
| Intro Ch. 1, 23–24 area | Libra/Sagittarius/Capricorn sterile; Taurus/Gemini/Aquarius middling | **Latin only**, fn. 10 — Dykes reports it, does not adopt it |
| Intro Ch. 2, 38 | "(and it is the tenth)" | manuscript **B** only (fn. 41) |
| Intro Ch. 2, 42–43 | the 9th-before-5th order + the Sun's-joy note | **Dykes's conflation** of H/L with B (fn. 42) |
| Intro Ch. 2, 48 | "⟨and it is the joy of Mars⟩" | Latin (fn. 43) |
| Intro Ch. 2, 58 | the trine/sextile vs square/opposition gloss | **L's marginal note** (fn. 48) |
| Intro Ch. 2, 9 and 22 | "falls from the stakes" | Dykes reading *for* "Ascendant" (fns. 23, 28) |
| Intro Ch. 2, 4 | "a report" | Dykes reading الخبر *for* الخير, "the good" — flagged tentative (fn. 17) |

## 14. What this chapter pair does *not* contain

- No bound/term table, no face/decan table, no exaltation degrees. Only the **triplicity** lords
  (Fig. 4) appear here.
- No degree span for the burned place.
- No orb ("body") values except the 12° assembly limit and the parenthetical Moon 12° / Sun 15°
  in fn. 45 — and those are Dykes's reasoning, referring forward to Ch. 3, 14.
- No joys for Mercury or Venus.
- **No aspect orbs at all.** ¶50–60 are entirely whole-sign: every aspect is defined by counting
  signs, never by degrees. The only degree quantity in the entire aspect section is the 12° of
  assembly.
