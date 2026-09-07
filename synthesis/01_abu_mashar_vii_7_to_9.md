# Phase 1 — Abū Ma'shar, *Great Introduction* Book VII, Chapters VII.7–VII.9

Source: `abu_mashar_book_vii.md`, **Abū Ma'shar's own** *Great Introduction* pagination
pp. 485–498 (a different printed volume from Sahl's Vol. I — see `00_inventory.md`).
Added to the corpus 2026-09-07; footnotes 247–329 transcribed from photographs, not OCR.

**Scope of this artifact.** VII.1–VII.6 were reconciled in the 2026-09-06 audit and are not
re-read here (Option 2 ordering). This covers only the three chapters that are new. Where VII.7–9
bears on VII.1–6, it is noted.

Citation convention: **AM VII.7, N** etc. Paragraph numbers restart per chapter.

---

## A. The headline fact

The corpus now contains all nine chapters. Two of the three new chapters carry doctrine that is
**not** a restatement of anything else in the corpus:

- **VII.7** — a complete, step-by-step algorithm for casting rays by ascensions. Nothing else in
  the corpus contains this procedure.
- **VII.9** — Abū Ma'shar's planetary natures and significations, with explicit humoral and
  qualitative assignments per planet.
- **VII.8** — *fardārs* and the four grades of planetary years. **Timing; deferred** (see §D).

---

## B. VII.7 — Casting the rays, "according to the work of Ptolemy"

### B1. What the chapter announces about its own authority

> "All of the masters of the stars have mentioned the casting of the planets' rays, although many
> of them have **differed** from the others. **2** And we will state their disagreement about it in
> another book besides this one, but as for this book of ours we will state what Ptolemy (the
> author of the *Book of Judgments*) said." — AM VII.7, 1–2

This matters. Abū Ma'shar explicitly says (a) the tradition disagrees about ray-casting, (b) he is
**not** adjudicating here, and (c) he is reporting **Ptolemy's** method specifically. So VII.7 is
not "Abū Ma'shar's rule"; it is one named method, presented as one among several, with the
disagreement deferred to a book this corpus does not contain.

Dykes's fn. 248 adds that the source is *Tet.* III.10 (Robbins pp. 291–95) **"but the method here
is explained somewhat differently."**

### B2. Step 1 — hours of distance from the stake, by quadrant

The planet's quadrant selects the formula. Writing *RA(x)* for "the right circle of *x*" (fn. 249:
*"Or rather, the right ascension"*) and *H(x)* for "the portions of the hours" of *x* (fn. 250:
the *hōriaioi chronoi* of *Tet.* III.10, from tables in the *Almagest*):

| Planet lies between | Procedure (verbatim source) | Yields distance from |
|---|---|---|
| **MC → ASC** | "subtract the right circle of the degree of the Midheaven from the right circle of the degree of the planet, and divide what remains by the portions of the hours of the degree of the planet" (¶4–5) | Midheaven |
| **ASC → IC** | "subtract the right circle of the Midheaven from the right circle of the planet… **7** take the portions of hours of the degree of the planet, multiply them by 6, and subtract them from what was preserved. **8** Divide what remains by the portions of the hours of **the degree of the opposition of the planet**" (¶6–8) | Ascendant |
| **IC → DSC** | "subtract the right circle of the stake of the earth from the right circle of the degree of the planet. **10** Divide what remains by the portions of the hours of the degree of the opposition of the planet" (¶9–10) | Stake of the earth |
| **DSC → MC** | "subtract the right circle of the stake of the earth from the right circle of the degree of the planet… **12** take the portions of the hours of the degree of the opposition of the planet, and multiply them by 6, and subtract them… **13** Divide what remains by the portions of the hours of the degree of the planet" (¶11–13) | Stake of the setting |

Two structural features worth recording, because they are what make the procedure coherent:

- The **6×** term is a quadrant expressed in hours (a quadrant is six seasonal hours), subtracted to
  re-base the measurement from the far stake to the near one.
- The alternation between *H(planet's degree)* and *H(the opposition of the planet's degree)*
  is the diurnal/nocturnal switch: the hourly times of the opposite degree are the nocturnal hourly
  times of the degree itself.

Neither of those explanations is in the text. They are mine, and they are inferences from the
structure — flagged as such, not as source claims.

### B3. Step 2 — the two lookups

> "if you wanted the casting of the rays of the sextile of a planet (or its square, or trine)
> **towards the left**, then *add* 60° to the right circle of the degree of the planet for the left
> sextile (and 90° for its square, and 120° for its trine), and enter what it amounts to into the
> [table of the] ascensions of the right circle, and take what is opposite it (of the degrees of
> equality of the sign in which it occurs), and preserve it." — AM VII.7, 14

> "**15** Then, take the ascensions of the degree of the planet, and also add to them 60° for its
> left sextile (and 90° for its square, and 120° for its trine), and enter what it amounts to into
> the arguments of the ascensions of **that city which you want**, and see what is opposite whichever
> portion occurs in the signs." — AM VII.7, 15

So two candidate ray-positions are produced: one from **right ascension** (¶14) and one from
**oblique ascension for the latitude** (¶15, and fn. 252: *"This refers to oblique ascensions"*).

### B4. Step 3 — reconciling the two lookups

> "**16** For if the ascensions of the right circle and the ascensions of the city both occur
> opposite to one [and the same] portion and minute, then the rays of the planet are in that degree
> and minute. **17** But if they differ, then understand which of them is increased over the other,
> and take the excess which is between them, **divide it by 6**, and multiply what comes out as its
> 1/6 by **the hours of the planet's distance from the stakes**. **18** Add the result to that one of
> the two positions which is **nearest** the planet by degrees of equality… **19** And whatever it
> comes to is the rays of the planet." — AM VII.7, 16–19

The division by 6 is the same quadrant-in-hours constant as step 1: the interpolation is linear in
the planet's hour-distance across a six-hour quadrant.

### B5. Step 4 — right (dexter) aspects, and an asymmetry worth flagging

> "**20** Now as for the right sextile, square, and trine, ***subtract*** from the ascensions of the
> right circle of the degree of the planet, and from the ascensions of its degree in the city …
> the same degrees which we stated, and work with that and the hours of distance just as we said.
> **21** And whatever comes out, add it to the more ***distant*** of the two places from the planet
> by degrees of equality" — AM VII.7, 20–21

**⚠ The anchor flips between the left case and the right case:** ¶18 says add to the *nearest* of
the two positions, ¶21 says add to the *more distant*. The text states both flatly and gives no
reason. This may be geometrically correct (the sign of the interpolation reverses when you subtract
rather than add) or it may be a copying artefact. **The corpus does not say which, and I am not
resolving it.** Any implementation must treat this as a decision point and test both.

### B6. The opposition is exempt

> "But as for the opposition, [a planet] casts its ray into the opposition of its sign, in the same
> degree and minute." — AM VII.7, 22

Flat, unconditional, one sentence. The opposition ray needs no ascensional machinery at all — it is
exactly 180° in zodiacal longitude. This is a clean, cheap, testable rule and it is the only part of
VII.7 that requires no tables.

### B7. What VII.7 depends on that the corpus does not supply

The procedure is written against tables Abū Ma'shar assumes the reader has:

| Needed | Source named | In this corpus? |
|---|---|---|
| Right ascensions of zodiacal degrees | "the [table of the] ascensions of the right circle" | No table; computable |
| Oblique ascensions for a given city | "the arguments of the ascensions of that city which you want" | No table; computable. *TNAC* `Ascensions-table-2014.pdf` exists but is course material, not this corpus |
| "Portions of the hours" (*hōriaioi chronoi*) | fn. 250: *"This refers to special tables in the Almagest."* | **Not in this corpus.** Computable |
| Degrees ↔ ascensions inverse lookup | fn. 251: *"old tables in which the ascensions and zodiacal degrees are converted into their opposites"* | **Not in this corpus** |

All four are computable from spherical astronomy; none is *given*. So VII.7 is a **complete
algorithm with absent tables**, not an incomplete algorithm.

### B8. ⚠ Scope question this chapter forces — flagged, not decided

Dykes's fn. 247, on the phrase "casting of the planets' rays" in ¶1:

> "This is normally called **'primary directions'** in English-language astrology."

And fn. 248 identifies the source as *Tet.* III.10 — which in Robbins is the **length-of-life**
chapter, i.e. the prorogation apparatus.

The project's deferral covers "releaser, house-master, distribution by ascensions, firdaria, solar
revolutions." VII.7 is none of those *by name*, and what it computes is a **static chart quantity** —
where a planet's sextile/square/trine ray falls, corrected for the birth latitude. That is aspect
geometry, not prediction. But its machinery (RA, OA, hourly times, interpolation across a quadrant)
is precisely the machinery the deferred techniques need, and Dykes labels it with the deferred
technique's English name.

**Two defensible readings:**

1. **In scope.** VII.7 refines *aspects*, which the engine already computes. Implementing it adds a
   latitude-correct ray position alongside the zodiacal one. It also supplies the ascensional
   apparatus that *Fifty Aphorisms* 45 (editor's ascensional correction, already a decided project
   policy) and *Nativities* Ch. 2.13, 48–51 (the three 15° ascensional bands) both require and
   currently lack.
2. **Out of scope.** fn. 247 says this *is* primary directions; building the ascensional engine is
   the bulk of the deferred work, and doing it under an "aspects" label smuggles the deferral open.

**My reading: (1), narrowly** — implement the ascensional apparatus and the ray positions, and do
not build anything that *directs* them through time. But this is a user decision, not mine, and it
should be recorded as an explicit choice either way rather than settled silently.

---

## C. VII.9 — Natures of the seven planets

### C1. The chapter's own warning against mechanical use

Before any signification, Abū Ma'shar states a caveat that an engine emitting keyword lists should
carry:

> "And **not everything we state in this chapter** (of the indication of each planet) **will be
> gathered together within a single man**, but sometimes many things of them will be gathered
> together in him, **according to the condition of the planet in itself and its condition in the
> houses of the circle**." — AM VII.9, 2

Two claims: the lists are disjunctive, not conjunctive; and which items apply is governed by the
planet's *condition* — which is what VII.1–VII.6 spent ninety pages defining. VII.9 is explicitly
the payload that the rest of Book VII selects from.

### C2. The natures, verbatim

| Planet | Nature as stated | ¶ |
|---|---|---|
| **Saturn** | "his nature is cooling, drying, black bile, dark, harsh in coarseness; **but sometimes it is cooling [and] wet**, heavy, stinking air" | 3 |
| **Jupiter** | "his nature is heating, wet, airy, temperate" | 6 |
| **Mars** | "his nature is heating, drying, fiery, yellow bile, and his taste bitter" | 11 |
| **Sun** | "his nature is heating [and] drying" | 14 |
| **Venus** | "her nature is cooling, wet, phlegmatic, temperate, **a fortune**" | 19 |
| **Mercury** | "his nature **inclines to the natures of the planets and signs he mixes with**, [although] an equal balance of **dryness and coldness** is in him" | 23 |
| **Moon** | "her nature is cooling, wet, phlegmatic (**and in her is incidental heat, because her glow is from the Sun**), and she is light" | 33 |

Four things here are more than a qualities table:

1. **Saturn carries an internal alternative** — "but sometimes it is cooling [and] wet." Dykes's
   fn. 254 hedges the reading further: *"Or perhaps, 'of heavy, stinking air.'"* Saturn is the only
   planet given two temperaments in a single sentence.
2. **Mercury has both a convertible nature and a fixed one.** He "inclines to" what he mixes with,
   *and* is cold-dry in himself. These are stated in one breath and are not ranked.
3. **The Moon's heat is explicitly derivative** — "incidental… because her glow is from the Sun."
   A causal claim, not just a quality.
4. **Venus's "a fortune" is stated as part of her nature**, not as a separate classification. The
   Sun is given no humor and no fortune/infortune label at all.

**Humors are assigned to planets here.** Note that Sahl assigns humors to **triplicities** instead
(*Introduction* Ch. 1, 34–41: fire→yellow bile, earth→black bile, air→blood, water→phlegm). The two
schemes are not in conflict — different carriers — but they are different schemes and an engine
that shows "humor" must say which it means. Note also that **no planet in VII.9 is assigned blood**;
the sanguine humor has no planetary owner in this chapter.

### C3. Significations — structure, not a full transcription

The lists are long and I am not reproducing them; they are ¶4–5 (Saturn), 7–10 (Jupiter), 12–13
(Mars), 15–18 (Sun), 20–22 (Venus), 24–32 (Mercury), 34–36 (Moon). Structural observations:

- **Family members are assigned across planets and they collide.** Saturn: "the ancestors, the dead,
  … grandfathers, fathers, older brothers" (¶5). Sun: "fathers, middle brothers" (¶18). Mars:
  "middle brothers" (¶13). Venus: "the mother, younger sisters" (¶20). Mercury: "younger brothers"
  (¶24). Moon: "mothers, maternal aunts, wet-nurses, and older sisters" (¶35).
  **Fathers are both Saturnian and Solar; middle brothers are both Martial and Solar.** Stated
  without reconciliation.
- **Sun and Moon share a "universal" quality**, and Dykes flags it twice as deliberate:
  fn. 326 on the Moon's "a king with kings, a slave with slaves, and with every man he is like his
  nature" — *"Note the similarity between this and the Sun in 18, which suggests a kind of universal
  quality which can take many other things on"* — and fn. 293 makes the same cross-reference from
  the Sun's side.
- **Saturn and Mercury are explicitly distinguished on handwork**, by footnote, and the distinction
  is doctrinal rather than lexical. Saturn ¶4 "those working with their hands," fn. 255:
  *"This includes skilled laborers, but is not the same as doing fine and delicate work with the
  hands, which is a Mercurial signification (see 30 below)."* Mercury ¶30, fn. 318:
  *"This connotes fine, delicate work…, not so much that of the laborer or craftsman, which is a
  Saturnian signification."* The two footnotes point at each other; the distinction is secure.
- **The Sun's proximity doctrine is stated as signification, not as a condition** (¶17): "treats
  badly those who meet with him and get close to him with extreme insult, and the people most on
  the brink of that are those closest to him by place, while the most fortunate of them are those
  far from him." This is combustion described in the language of *people around a king*. The
  quantitative version is VII.2, already reconciled.
- **Mercury contradicts himself within his own list**: ¶27 "a scarcity of joy and the corruption of
  assets" then ¶28 "He indicates assets, distribution, markets, businesses…". Dykes's fn. 315 says
  the two-sidedness is the point (*"to show Mercury's two-sided nature"*), so this is a reported
  feature, not a defect — but it is not a list an engine can score monotonically.

### C4. Textual instability inside VII.9

These are readings Dykes chose between manuscripts. They affect meaning and should not be quoted as
settled:

| ¶ | Word | Situation |
|---|---|---|
| 7 | "making judgments" | fn. 268 — Dykes reads القضاء with Lemay for **BY**'s "judges" (القضاة) |
| 9 | "comfort" | fn. 271 — reads الرخاء with BY for الرجاء, "hope" |
| 9 | "an inclination **towards** them" | fn. 273 — reads إليهم with BY for Lemay's عليهم, which would mean **hostile to** them. Opposite sense. |
| 17 | "he will be put aright and corrupted…" | fn. 291 — **Lemay and C** make this the person near the Sun; **BY and other MSS** make it the Sun itself. Changes who is affected. |
| 18 | "the multitude" | fn. 292 — Dykes reads بُهْتَة as an **unattested** variation; BY read يُبُوسَة, "dryness". Dykes offers a third possibility (Persian بَاشَا, a governor). |
| 18 | "pure clarity" | fn. 293 — Dykes emends; BY read "empty zero". Dykes: *"Nevertheless I feel something is wrong here."* |
| 21 | "wishing good health" | fn. 305 — *"I do not find this in Lane's lexicon… Grammatically it looks like the unattested Form 2"* |
| 32 | "proficiency with riding animals" | fn. 319 — reads الجَلَب for Lemay's الجَرَب, "mange in" |

¶18 ("the multitude" / "pure clarity") is the weakest passage in the chapter; Dykes says so himself.

---

## D. VII.8 — *fardārs* and planetary years (TIMING — DEFERRED)

Recorded for completeness. **Not synthesized into rules**, per the project's standing deferral.

### D1. The table, and it now checks out arithmetically

Figure 146 (p. 487) was structurally corrupt and was repaired 2026-09-07. I verified the repair by
checking the table against the prose, which states the same numbers a second time in ¶3–8:

| | *Fardār* | Lesser | Middle | Greater | Mighty |
|---|---|---|---|---|---|
| ♄ | 11 | 30 | 43½ | 57 | 265 |
| ♃ | 12 | 12 | 45½ | 79 | 427 |
| ♂ | 7 | 15 | 40½ | 66 | 284 |
| ☉ | 10 | 19 | 39½ | 120 | 1461 |
| ♀ | 8 | 8 | 45 | 82 | 1151 |
| ☿ | 13 | 20 | 48 | 76 | 480 |
| ☽ | 9 | 25 | 39½ | 108 | 520 |
| Head | 3 | | | | |
| Tail | 2 | | | | |

**Every cell in all five columns matches the prose at ¶3, 5, 6, 7, 8.** And the *fardār* column
carries its own checksum, which the text states:

> "the *fardār* of the Sun is 10 years, the *fardār* of Venus 8 years, Mercury has 13 years, the
> Moon 9 years, Saturn 11 years, Jupiter 12 years, Mars 7 years, the Head 3 years, and the Tail 2
> years: **that is 75 years**." — AM VII.8, 3

10+8+13+9+11+12+7+3+2 = **75.** ✓

So Figure 146 is now doubly verified — against its own prose restatement, and against a total the
source itself supplies. **This figure is safe.**

### D2. Why it is still deferred

The lesser/middle/greater/mighty years are the quantities the **house-master (alcocoden)** grants
for lifespan, and the *fardārs* are **firdaria** — both named in the deferral. VII.8 gives the
numbers but not the technique; ¶2 explicitly sends the reasons elsewhere:

> "But as for the reasons for them, we have stated them in the book in which it is necessary to
> mention them." — AM VII.8, 2

One consequence worth stating plainly: **the numbers are no longer the blocker.** If the deferral
is ever lifted, the planetary-years table is present, complete, and verified.

⚠ **Correction (added after the omitted chapters were read).** I originally wrote that "what remains
missing is the *procedure*." That was too strong. *On Times* Ch. 4, 7 gives a granting rule —
**angular → greater years, succedent → middle, cadent → lesser** — together with the releaser
candidate set (Ch. 4, 2–3) and directing "a year for every degree by the ascensions of the signs in
that city" (Ch. 4, 4). See `01_on_times.md` §4.

What is still missing is narrower: that rule is stated for a **question** chart's lifespan, and the
natal apparatus — which releaser wins under which sect conditions, the house-master's own
qualification tests (*On Nativities* Ch. 1.20–1.23), and the revolution techniques that modify the
result — remains absent. *On the Revolutions of the Years of Nativities* is still what would supply
it.

Note also that VII.2 (already reconciled) repeatedly conditions "granting their greater years" on
solar phase — e.g. "they are suitable for granting their greater years as well as spear-bearing"
(VII.2, 12), "not suitable for granting their greater years" (VII.2, 32). Those hooks already exist
in the reconciled part of the corpus; VII.8 now supplies what is being granted.

---

## E. ✅ Resolved: the 12°/15° assembly question is not a conflict

Dykes's fn. 146 (VII.5, p. 450) says aspect rays get no orbs, and speculates that "the **15°
distance for an assembly** may be analogous to the Sun's body," while his fn. 45 to Sahl's
*Introduction* Ch. 2, 51 derives Sahl's **12°** from the **Moon's** body. I flagged this as a
possible cross-author tension pending a reading of VII.4.

**I read VII.4. There is no tension.** Abū Ma'shar states his own rule directly:

> "And a planet is said to be **assembling** … **if they were both in a single sign**; and it is
> **stronger for the indication** of their assembly if there were **15° and less** between one of
> them and the other, [whether] in front of it or behind it." — AM VII.4, 3

So 15° is Abū Ma'shar's own number, from his own text — an *intensity* band over a same-sign
assembly, not a limit. Sahl's 12° is a different thing again: a summary of his per-planet body table
(*Introduction* Ch. 3, 12–18), where the Moon's 12° body is the largest that can be reciprocated.

The two authors then **agree** on the underlying bodies. AM VII.4, 7:

> "if they were in a single sign, and the distance between them both was within **12°** in front of
> them or behind, **Saturn would be in the power of the body of the Moon, while the Moon would not
> be in the power of the body of Saturn, until there is a little under 9°** between them."

— matching Sahl Ch. 3, 15 ("the light of Saturn and Jupiter (each one) is 9°"). Same body sizes,
same asymmetry.

Recorded so this is not re-opened. See `01_sahl_glossary.md` §1a.

## F. Summary of what VII.7–VII.9 make newly available

| Item | Chapter | Character |
|---|---|---|
| Quadrant-based hour-distance from the stakes | VII.7, 4–13 | Complete algorithm, tables absent |
| Left/right ray positions by RA + OA interpolation | VII.7, 14–21 | Complete algorithm; **anchor asymmetry ¶18 vs ¶21 unresolved** |
| Opposition ray is exact in longitude | VII.7, 22 | One sentence, unconditional, needs no tables |
| Explicit "the tradition disagrees; this is Ptolemy's" framing | VII.7, 1–2 | Provenance, limits how the rule may be labelled |
| Per-planet temperaments and humors | VII.9, 3–33 | Table above; Saturn dual, Mercury dual, Moon derivative |
| Per-planet significations | VII.9, 4–36 | Long lists; disjunctive by ¶2; family roles collide |
| The anti-mechanical caveat | VII.9, 2 | Should govern how any of §C3 is displayed |
| *Fardārs*, four grades of years | VII.8, 3–8 + Fig. 146 | **Deferred.** Verified, complete, unused |
