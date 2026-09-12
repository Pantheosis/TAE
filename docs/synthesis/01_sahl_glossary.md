# Phase 1 — the Glossary (Dykes, in *The Astrology of Sahl b. Bishr, Vol. I*)

Source: `sahl_glossary.md`, Sahl Vol. I pp. 771–797, ~220 entries, no figures.
**New to code reconciliation** — `app.py`'s four "Glossary" references are all to the *TNAC Course
Glossary*, a different document.

---

## ⚠ 0. Read this before using anything below

The glossary's own opening sentence defines its scope, and it is **not** "Sahl's doctrine":

> "This Glossary contains terms from **all branches of traditional astrology, from all of my
> translations**. Most entries also provide the Greek, Latin, and Arabic source words." — p. 771

So this is **Dykes's cross-author reference apparatus**, spanning every text he has translated. It
is not a witness to Sahl. Three consequences:

1. **A glossary entry never overrides Sahl's or Abū Ma'shar's own sentence.** Where they conflict,
   the primary text wins and the glossary records that the wider tradition varies.
2. **Where the glossary names an author, that is a real attribution** and carries weight — e.g.
   "according to Sahl b. Bishr and Rhetorius" under *In the heart*.
3. **Where the glossary offers two definitions, that is evidence the tradition is genuinely split**,
   which is exactly the content this project values.

Its real value is as a **disambiguation index**: many entries exist precisely to say "this word has
two or three distinct senses." Those entries are the ones recorded below.

---

## 1. Direct numeric conflicts with the primary texts

### 1a. ✅ Assembly: NOT a conflict — the glossary is reporting Abū Ma'shar, and Sahl's 12° is derived

> "**Assembly** … When two or more planets are in the same sign, and **more intensely if within
> 15°**." — Glossary p. 772

I initially read this as conflicting with Sahl's "12° … is the limit of the assembly"
(*Introduction* Ch. 2, 51). **Checking the primary texts dissolves the conflict**, and the result is
worth recording because it is the reverse of what the numbers suggest.

**Abū Ma'shar VII.4, 3 says exactly what the glossary says, structure included:**

> "And a planet is said to be **assembling** with something of what we state, **if they were both in
> a single sign**; and it is **stronger for the indication** of their assembly if there were **15°
> and less** between one of them and the other, [whether] in front of it or behind it."
> — AM VII.4, 3

Same-sign is the assembly; 15° is an *intensity* threshold, not a limit. So the glossary entry is a
faithful précis of Abū Ma'shar and makes no claim about Sahl at all.

**And Sahl's 12° is not a flat orb either — it is derived from his own per-planet body table:**

> "**13** Know that the body of the Sun is 30°, so one-half of them are in front of him and one-half
> behind him… **14** And the light of the **Moon is 12°**, in front of her and behind her. **15** And
> the light of **Saturn and Jupiter** (each one) is **9°**… **16** And **Mars is 8°**… **17** And
> **Venus and Mercury** (each one of them) is **7°**… **18** So **by the extent of these lights, they
> are connected** one to the other." — *Introduction* Ch. 3, 12–18

Dykes's fn. 45 to Ch. 2, 51 makes the derivation explicit: 12° is the Moon's body, and since she has
the second-largest body after the Sun, 12° is the greatest distance at which two planets' bodies
*both* touch. **Ch. 2, 51's "12°" is a summary of the Ch. 3 table, not an independent rule.**

The two authors also agree on the body sizes themselves: AM VII.4, 7 has Saturn inside the Moon's
body at 12° while the Moon enters Saturn's only at "a little under 9°" — matching Sahl Ch. 3, 15's
9° for Saturn.

**Conclusion:** implementing Sahl by per-planet bodies (not a flat 12°) is the faithful reading, and
Abū Ma'shar by same-sign with a 15° intensity band. `app.py` already does exactly this — see
`02_reconciliation.md`. **No change needed; recorded so this is not re-litigated.**

### 1b. ⚠ In the heart (cazimi): the glossary attributes the strict reading to Sahl by name

> "**In the heart.** … A planet is in the heart of the Sun when it is **either in the same degree as
> the Sun (according to Sahl b. Bishr and Rhetorius), or within 16' of longitude** from him."
> — p. 783

This is a named attribution, so it is usable. **Sahl's own criterion is "the same degree," not
16'.** The 16' figure belongs to other authorities. An engine implementing Sahl should use
same-degree; if it uses 16', it is implementing someone else and should say so.

Note that Appendix A depends on this in three sections — ¶59 [S58] "in the heart with the Sun,
**degree by degree**", ¶60 [S59], ¶61 [S60] "in one degree" — and ¶59's phrasing independently
supports the same-degree reading.

### 1c. ⚠ Sun's rays: the generic 7.5°/15° scheme is labelled *later*, and Abū Ma'shar disagrees

> "**Sun's rays** … In **earlier astrology**, equivalent to a regularized distance of **15°** away
> from the Sun, so that a planet under the rays is not visible at dawn or dusk. But a **later
> distinction** was made between being **burned up (about 1° – 7.5°)** and merely being under the
> rays (**about 7.5° – 15°**)." — p. 793
>
> "**Burned up** … Normally, when a planet is between about **1° and 7.5°** away from the Sun."
> — p. 773

Abū Ma'shar VII.2 (already in the reconciled range) gives **per-planet** values instead, and they do
not match: Saturn and Jupiter burned within 6°, Mars within 10°; under the rays until 15° for
Saturn/Jupiter and 18° for Mars (VII.2, 11–13); 7°/12° for another group (VII.2, 40, 44); 12° for
the Moon (VII.2, 61).

So the corpus contains **a per-planet table from a primary source** and **a generic simplification
from a cross-author glossary that flags itself as the later development**. Prefer Abū Ma'shar's
table. This is the same source-fidelity call as 1a.

### 1d. Burnt path — the degrees *are* in the corpus, but only here, and doubly

`01_introduction_ch1_ch2.md` §5 said no degree span for the burnt path exists in the corpus. **That
was wrong; it exists here** — with two competing definitions, neither attributed to Sahl:

> "**Burnt path** (Lat. *via combusta*). A span of degrees in Libra and Scorpio … **Some
> astrologers identify it as between 15° Libra and 15° Scorpio; others between the exact degree of
> the fall of the Sun in 19° Libra and the exact degree of the fall of the Moon in 3° Scorpio**."
> — p. 774

Sahl's own two statements (*Introduction* Ch. 1, 19; *Nativities* Ch. 1.38, 9) give **no degrees at
all** — "the end of Libra and the beginning of Scorpio." So: the span is genuinely undetermined for
Sahl, and the glossary shows the tradition split two ways. **Any implementation is an interpretive
choice with two named alternatives.** (Correction applied to §5 of that artifact.)

---

## 2. Questions from earlier artifacts that the glossary answers

### 2a. ✅ Crooked/straight is latitude-dependent — now stated in prose, not just in a figure

`01_introduction_ch1_ch2.md` §2 flagged that Figure 3 adds a southern-hemisphere inversion that
Sahl's prose omits, and noted the figure was Dykes's. The glossary states it in words:

> "**Crooked/straight.** … **In the northern hemisphere, the signs from Capricorn to Gemini are
> crooked (but in the southern one, straight); those from Cancer to Sagittarius are straight (but
> in the southern one, crooked).**" — p. 776

Now attested twice (Figure 3 + this entry). Still Dykes rather than Sahl, but no longer resting on
a single diagram. **Treat the latitude inversion as settled.**

### 2b. ✅ The 7-place and 8-place systems are answering different questions — and the glossary says so explicitly

`01_introduction_ch1_ch2.md` §12 item 7 flagged that the 8th house is "good" in one scheme and
"most bad" in the other, and that an engine keeping one house-strength number silently picks a side.
The glossary resolves the *why*:

> "**Advantageous places.** One of two schemes of **houses** … The **seven-place scheme** according
> to **Timaeus** and reported in ***Carmen*** includes only certain signs which **look at** the
> Ascendant by whole-sign, and suggests that these places are advantageous **for the *native***
> … The **eight-place scheme** according to **Nechepso** lists all of the angular and succeedent
> places, suggesting places which are stimulating and advantageous **for a planet *in itself***."
> — p. 771

| Scheme | Source | Criterion | Advantageous *for* |
|---|---|---|---|
| 7-place (1,10,7,4,11,9,5) | Timaeus, via *Carmen* | aspects the Ascendant by whole sign | **the native** |
| 8-place (1,2,4,5,7,8,10,11) | Nechepso | angular + succeedent | **the planet itself** |

This is not a contradiction and the two must not be merged into one score. It also explains why the
8th is included in one and condemned in the other: the 8th is a strong place *for a planet*, and in
aversion to the Ascendant *for the native*. Note the criterion given for the 7-place scheme —
"look at the Ascendant by whole-sign" — is exactly Sahl's own justification at *Introduction*
Ch. 2, 7/15/28/46, which is a nice independent corroboration.

Related: **Excellent place** (p. 780) narrows further —
> "Includes several of the advantageous places, among which the **Ascendant, Midheaven, and
> eleventh** are consistently mentioned. (These may be the only excellent places.)"

A third, tighter grade. Note the parenthetical hedge is Dykes's own.

### 2c. ✅ "Advancing" has three senses, and the glossary enumerates them

The project already records that advancing carries two senses
(`project_advancing_two_senses`, and `NOT_IMPLEMENTED_COVERAGE`'s
`ADVANCING_BY_QUADRANT_FIG90`). The glossary independently gives them, and adds a third:

> "**Advancement, advancing** (اقبال \ مقبل; Lat. *accedens*). Refers to being **(1) dynamically
> angular or succeedent, i.e. moving by primary motion toward an axial degree**. (But occasionally
> might refer to **angular or succeedent whole signs**.) Its two antonyms are **retreat/retreating**,
> and **withdrawal/withdrawing**. It can also refer to **(2) the eastern quadrants**." — p. 771

So: (i) dynamic — moving by primary motion toward an axis; (ii) whole-sign angular/succedent;
(iii) the eastern quadrants. The mirror entries agree —

> "**Retreat, retreating** … dynamically **cadent**, i.e. moving by primary motion **away from** an
> axial degree… It may also refer to … the **western** quadrants." — p. 790
> "**Withdrawal, withdrawing** (زوال \ زائل …) … [same definition] … the **western** quadrants."
> — p. 796

**This corroborates the existing project reading rather than disturbing it**, and it names the
third sense the project recorded from the Figure 90 margin (eastern quadrants) as a standard
meaning of the word, not a one-off. It also confirms *retreat* and *withdrawal* are near-synonyms
with the same two senses — see also *Remote* (p. 790), which reports al-Ṭabarī distinguishing
cadent (ساقط) from remote (زائل), i.e. **falling** from **withdrawing**.

### 2d. ✅ Overcoming / right / left — a worked example that confirms *Introduction* Ch. 2, 59

> "**Right/left.** Right (or "dexter") degrees and configurations or aspects are those **earlier in
> the zodiac** relative to a planet or sign, up to the opposition; left (or "sinister") … those
> **later in the zodiac**. For example, **if a planet is in Capricorn, its right aspects will be
> towards Scorpio, Libra, and Virgo; its left aspects will be towards Pisces, Aries, and Taurus**."
> — p. 791

Checking this against *Introduction* Ch. 2, 52–56 and the *Overcoming* entry:

- From Capricorn, **Scorpio, Libra, Virgo** are the 11th, 10th and 9th signs.
- *Overcoming* (p. 787): a planet in the **11th, 10th or 9th** from another **overcomes** it.
- Therefore: **a planet you cast a *right* aspect to is the planet that overcomes you**; the
  overcomer casts the *left* aspect. Left = sinister = "second" aspect = superiority.
- *Introduction* Ch. 2, 59: "the **second** sextile is **stronger** than the first … and this aspect
  is called 'superiority'." ✓

Everything coheres — the glossary, the *Overcoming* entry, and *Introduction* Ch. 2, 52–59 give one
consistent relation stated three times. **Treat as settled.** And *Decimation* (p. 776) sharpens the
middle case:

> "**Decimation.** A form of **overcoming**, specifically from the **superior square** (i.e., the
> tenth sign from something else)."
> "**Look down upon** (Ar. أَشْرَف). A synonym for **overcoming**, and in particular **decimation**."
> — p. 785

---

## 3. Worked examples — free test fixtures

Three entries carry a concrete instance that an implementation can be checked against directly.

| Doctrine | Worked example, verbatim | Verified |
|---|---|---|
| **Antiscia** | "a degree mirrored across an axis drawn from 0° Capricorn to 0° Cancer. For example, **10° Cancer has 20° Gemini as its antiscion**." (p. 772) | ✓ 10° past 0♋ mirrors to 10° before 0♋ = 20°♊ |
| **Twelfth-part** | "Signs of the zodiac defined by **2.5° divisions** of other signs. For example, the twelfth-part corresponding to **4° Gemini is Cancer**." (p. 795) | ✓ 4°/2.5° → 2nd division; 2nd from Gemini = Cancer |
| **Right/left** | the Capricorn example above (p. 791) | ✓ §2d |

### ⚠ A caution on the antiscia entry

This gives the **degree-wise formula** for antiscia. It does **not** license completing the
five-pair *natural connections* list of Abū Ma'shar VII.5, 67–75. Those are two different objects:
the glossary defines a continuous degree mirror; VII.5 enumerates specific **sign pairs** and stops
at five. `NOT_IMPLEMENTED_COVERAGE` already records that Aquarius–Scorpio is absent from VII.5, and
that entry stays correct. **Having the formula is not permission to add the sixth pair** — the
formula belongs to the glossary's cross-author vocabulary, the pair list belongs to Abū Ma'shar's
text, and only the latter is a claim about what Abū Ma'shar says.

Also note *Proper face* (p. 789) supplies a fourth worked example, for a doctrine not otherwise in
this synthesis: "Leo (ruled by the Sun) is two signs to the right of Libra (ruled by Venus): so
whenever Venus is western and two signs away from the Sun, she will be in the proper face of the
Sun."

---

## 4. Terms with more than one meaning — the disambiguation index

These are the entries whose whole purpose is to warn that a word is ambiguous. Any of them appearing
in a tooltip or a variable name without a chosen sense is a latent bug.

| Term | Senses (glossary's own) | p. |
|---|---|---|
| **Eastern / western** | **four**: (1) rises before / sets after the Sun by degree; (2) outside the rays / under them; (3) eastern *quadrant of the chart* (ASC→MC, DSC→IC); (4) eastern *quadrant relative to the Sun* (the 90° preceding him) | 778 |
| **Easternize / westernize** | (1) coming out of / going under the rays, "**normally around 15°**", distances differing by planet; (2) close enough that "**within 7 or 9 days**" it will emerge or submerge | 778 |
| **Emptiness in course** | **Medieval**: no connection completed *for as long as it is in its current sign*. **Hellenistic**: no connection completed *within the next 30°* | 779 |
| **Angles / succeedents / cadents** | the region depends on (1) whole-sign angles, (2) the axial degrees themselves, or (3) quadrant houses | 771 |
| **Cadent / falling / declining / withdrawing / retreating / remote** | whole-sign vs dynamic-quadrant, with *falling* vs *withdrawing* distinguished by al-Ṭabarī | 774, 780, 790, 796 |
| **Testimony** | **four**: (1) planets having dignity in a place; (2) the *number* of dignities; (3) an assembly or aspect to a place; (4) "generally *any* way in which planets may make themselves relevant" | 794 |
| **Victor** (= *mubtazz* = *almuten*) | victor "**over**" several places at once, vs victor "**among**" several candidates on a ranked list | 796, 771 |
| **Halb / hayyiz / domain / share / glow / shift** | a cluster of sect-adjacent terms that are *not* synonyms — see §5 | 782, 781, 777, 792 |
| **Lord of the year** | profection lord of the terminal sign, **or** a mundane victor for the year (the entry is printed **twice**, p. 785, with slightly different wording) | 785 |
| **House** | the twelve-fold spatial division, **or** *domicile* ("Aries is the house of Mars") | 782 |
| **Conjunction** | assembly / connection by body, **or** the mundane *mean* Saturn–Jupiter conjunction | 775 |
| **Union** | any bodily conjunction, **or** a mean conjunction, **or** the New Moon | 796 |

**Testimony** deserves particular attention: the project already treats Moon defects as "one vote
per numbered testimony." The glossary's sense (4) — "generally *any* way in which planets may make
themselves relevant" — confirms the word is deliberately loose in the sources, so a counting rule
over it is necessarily a project convention rather than a doctrine. That is worth stating in the UI
rather than implying the count is Sahl's.

---

## 5. The sect cluster, disentangled

These five are routinely conflated and the glossary separates them. This matters because
Appendix A ¶39 ("in their own **domain**") and ¶41 ("its ***halb***") both depend on the distinction.

| Term | Definition, verbatim |
|---|---|
| **Sect** | "A division of charts, planets, and signs into 'diurnal/day' and 'nocturnal/night.'" (p. 792) |
| **Halb** (حلب) | "Probably Pahlavi for sect, but normally describes a special sect-related rejoicing condition. **For diurnal planets, when they are in the same hemisphere as the Sun** (upper or lower); **for nocturnal planets, when they are in the hemisphere opposite the Sun**." (p. 782) |
| **Hayyiz / Domain** (حيز) | "Arabic for **domain**, technically equivalent to **halb**, **except that the planet is also in a sign of its own gender**. But sometimes this term simply means sect." (p. 782) — and *Domain* (p. 777): "in a sign of its own gender **and** also in its preferred hemisphere relative to the Sun" |
| **Share** (حظ) | "Often equivalent to **dignity**, but sometimes used to mean **sect** (where it is synonymous with and perhaps confused with **domain**)." (p. 792) |
| **Glow** (ضوء) | "**three** primary meanings: (1) a planet in 'its own glow' is of the sect of the chart, or in some sect-related rejoicing condition; (2) the Moon increases and decreases in her light… by waxing and waning; (3) a planet can be 'in its own glow' when it is out of the Sun's rays so as to be visible." (pp. 781–782) |
| **Shift** (نوبة) | "(1) Equivalent to **sect** … not only the alternation between day and night, but also the period of night or day itself. The Sun is the lord of the diurnal shift…" (p. 792) |

So the ladder is: **sect** ⊂ **halb** (sect + hemisphere) ⊂ **hayyiz/domain** (halb + own-gender
sign). *Halb* and *domain* are **not** synonyms, and the glossary says so in as many words.

This has a direct consequence for Appendix A: ¶41's *halb* is a **tentative reading** (fn. 33) of an
unpointed word, and if it were instead *hayyiz* the condition would be strictly stronger. Recorded,
not resolved.

---

## 6. Definitions of aspect-doctrine machinery

These are the terms the engine's connection logic must answer to. Recorded because most have never
been checked against the code.

| Term | Definition |
|---|---|
| **Configured** | "To be in an aspect by **whole-sign** (though not necessarily connecting by degree)." (p. 775) |
| **Connection** | "When a planet **applies** to another (by body in the same sign, or by **ray** in **configured** signs), **within a particular number of degrees** up to exactness." (p. 775) — note it does *not* fix the number |
| **Applying** | "When a planet is in a state of connection, moving so as to make the connection exact. Planets assembled together or looked at **by sign**, but not yet connecting by the relevant degrees, are only **'wanting' to be connected**." (p. 772) |
| **Ray** | "An imaginary line which represents an exact aspect cast from a planet to the corresponding degree in another sign, such as if a planet is in 15° Gemini and casts a square ray to 15° Virgo." (p. 790) |
| **Orbs/bodies** | "A space of power or influence **on each side** of a planet's body or position" (p. 787); **Body**: "in aspect theory, also equivalent to an **orb**" (p. 773) |
| **Handing over / Pushing / Render / Confer / Convey** | "When a planet applies by connection to another, it hands over its **management**." (p. 782) — all four are the same relation |
| **Management** | "how a planet 'manages' a topic by signifying it. Typically, planets hand over and 'accept' management to and from each other, **simply by applying to one another**." (p. 785) |
| **Reception** | "What one planet does when another hands over or applies to it, and **especially when they are related by dignity, or by a trine or sextile from an agreeing sign**" (p. 790) |
| **Not-reception** | "When an applying planet is **in the fall of** the planet being applied to, **or applies from a place in which the other planet has no dignity**." (p. 787) |
| **Returning** | "What a **burned or retrograde** planet does when another planet hands over to it." (p. 791) |
| **Blocking / Prohibition / Barring** | "When a planet blocks another from completing a connection, either through its own body or **ray**… **see Sahl's *Introduction* Ch. 3, 31-48**." (p. 773) |
| **Cutting of light** | "Any of several ways in which a connection is prevented, such as by blocking." (p. 775) |
| **Escape** | "When a planet wants to connect with a second one, but **the second one moves into the next sign** before it is completed, and the first makes a connection with a different, unrelated one instead." (p. 780) |
| **Revoking / Refrenation** | "When a planet making an applying connection **stations and turns retrograde**, not completing the connection." (p. 791) |
| **Resistance / Obstruction** | "When one planet is moving towards a second …, but **a third one in a later degree goes retrograde**, connects with the second one, and then with the first one." (p. 790) |
| **Collection** | "When two planets **aspecting each other but not in an applying connection**, each apply to a third planet." (p. 774) |
| **Transfer / Translation** | "When one planet **separates** from one planet, and **connects** to another." (p. 794) |
| **Reflection** | "When two planets are **in aversion** to each other, but a third either **collects or transfers** their light. **If it collects, it reflects the light elsewhere.**" (p. 790) |
| **Separation / Disregard / Flow away** | "When planets have completed a connection by assembly or aspect, and move away from one another." (p. 792) |
| **Crossing over** | "When a planet **begins** to separate from an exact connection." (p. 776) |
| **Wildness / Feral** | "When a planet is **not looked at by any other planet**." (p. 796) |
| **Enclosure / Besieging** | "When a planet has the rays or bodies of the **infortunes (or alternatively, the fortunes)** on either side of it, **by degree or sign**." (p. 779) |
| **Cleansed** | "Ideally, when a planet is in **aversion** to the infortunes (but certainly not in an assembly, square, or opposition to them)." (p. 774) |
| **Safe** | "When a planet is not being harmed, particularly by an assembly or square or opposition with the infortunes." (p. 791) |
| **Largesse and recompense** | "A **reciprocal** relation in which one planet is rescued from being in its own **fall or a well**, and then returns the favor when the other is in its fall or well." (p. 785) |

Three of these are worth singling out:

- **Reflection** is defined with an internal conditional ("If it collects, it reflects the light
  elsewhere") that makes it a *consequence* of collection or transfer between planets in aversion,
  not a fourth independent configuration.
- **Wildness** ("not looked at by any other planet") is the glossary's single definition. The project
  has already separated Sahl's *banishment* from Abū Ma'shar's *wildness* (commit `fcdc977`); this
  entry is consistent with that separation and does not re-merge them.
- **Enclosure** explicitly admits a **benefic** version ("or alternatively, the fortunes") and both a
  degree and a sign version. Four combinations, one term.

---

## 7. Dignity and rulership vocabulary

| Term | Point worth recording |
|---|---|
| **Dignity** | "typically **five**… often listed in the following order: **domicile, exaltation, triplicity, bound, face/decan**." Also assignable "sometimes, to a **Node**." (p. 777) |
| **Alien / Peregrine / Foreign / Exile** | "When a planet is **not in one of its five dignities**." *Exile* is Arabic for peregrine but in **later Latin** means **detriment** — a false friend. (pp. 771, 780) |
| **Detriment / Unhealthiness** | "The sign **opposite a planet's domicile**." (pp. 776, 796) |
| **Fall / Descension / Slavery** | "The sign **opposite a planet's exaltation**." (p. 780) — ⚠ **this entry misprints the Greek as *hupsōma*, which is *exaltation*; the Greek for fall is *tapeinōma*.** A slip in the glossary. |
| **Triplicity lords** | "One planet is primary by day, another by night, and **the third lord always acts as their partner**… Saturn is **always the last, partnering lord**" for the fire triplicity. (p. 795) — matches *Introduction* Ch. 1, 34–41 and Figure 4 exactly |
| **Overlord** | "a **victor** over a place, but often used to designate the **primary triplicity lord**." (p. 787) |
| **Victor** | see §4 — "over" vs "among" |
| **Bound** | "**Unequal** divisions… each ruled by one of the **five non-luminaries**." (p. 773) |
| **Face / Decan** | "36 faces of 10° each, **starting with the beginning of Aries**." *Darījān* is "an alternative face system attributed to the Indians." (pp. 780, 776) |
| **Bright, smoky, empty, dark degrees** | "Certain degrees … said to affect how **conspicuous or obscure** the significations of planets or the Ascendant are." (p. 773) — the table for these is Abū Ma'shar's Figure 61 |
| **Well / Welled / Pitted degrees** | "A degree in which a planet is said to be **more obscure in its operation**." (p. 796) |
| **Chronic illness / Azamene** | "degrees … especially said to indicate chronic illness, due to their association with certain **fixed stars**." (pp. 773, 774) |

---

## 8. Structural terms the engine names but may not define the same way

| Term | Definition |
|---|---|
| **Place** | "Equivalent to a **house**, and **more often (and more anciently) a whole-sign house**, namely a sign." (p. 788) |
| **Whole signs** | "The **oldest** system… aspects are considered **first of all according to signs**: planets in Aries look at planets in Gemini, **even if aspects which connect by degree are more intense**." (p. 796) |
| **Counting vs Division/Equation** | *Counting* (عدد) = whole-sign houses; *Division* / *Equation* = any quadrant system. (pp. 775, 777, 779) |
| **Stake / Angle / Pivot / Cardine / Post / Firm** | all equivalent (pp. 793, 788, 781) |
| **Upright** | "Describes the axis of the **MC-IC**, when it falls into the **tenth and fourth signs**, rather than the eleventh-fifth, or ninth-third." (p. 796) — this is the referent of Appendix B ¶59 fn. 21 |
| **Axial degree** | "The degree of the zodiac which the horizon or meridian: the Ascendant, Midheaven, Descendant, and Imum Caeli/IC." (p. 773) — sentence is garbled in the source (a verb is missing) |
| **Degrees of equality** | "Degrees of the **zodiac**, as opposed to degrees of **ascensions** or measured on the celestial equator." (p. 776) — this is the term used throughout Abū Ma'shar VII.7 |
| **Ascensions** | "Degrees on the celestial equator, measured in terms of how many degrees pass the meridian as an entire sign or **bound** … passes across the horizon. **Often used in the predictive technique of ascensional times, sometimes as an approximation of primary directions.**" (p. 772) |
| **Lot** | "A place (**often treated as equivalent to an entire sign**) expressing a ratio derived from the position of three other parts of a chart." (p. 785) |
| **Twelfth-part** | see §3 |
| **Ninth-parts** | "Divisions of each sign into 9 equal parts of **3° 20'** apiece, each ruled by a planet. Used predictively … as part of the suite of **revolution techniques**." (p. 786) — **timing; deferred** |
| **Spear-bearing / Doryphory / Dustoria / Honor guard / Right-siding** | "A special configuration … showing eminence and prosperity, **of which there were several types and definitions**. Spear-bearing requires that there be a **royal planet (usually, a luminary)**, which is **accompanied by a spear-bearing planet**." (p. 793) |

### ⚠ 8a. "Right-siding" and "spear-bearing" are given as synonyms, which makes Appendix A ¶49 read oddly

> "**Right-siding, being on the right, right-sidedness** (تيامن / ميمنة). **A synonym for
> Spear-bearing.**" — p. 791

But Appendix A ¶49 [S49] uses both in one clause:

> "One whose lord of the Ascendant is **right-siding the Sun** *and* **has spear-bearing**, and is
> superior to [the Sun]…"

If the two are synonyms, the sentence is redundant. Either they are not strictly synonymous in
Sahl's usage, or ¶49 is doubling for emphasis, or one term is a copyist's gloss that entered the
text. **Unresolved; flagged.** Note the glossary itself hedges spear-bearing as having "several
types and definitions."

---

## 9. Timing vocabulary — recorded, deferred

The glossary is the most complete map of the deferred territory anywhere in the corpus, and it is
worth having as a map even while the territory stays closed.

**Releaser** (هيلاج / *hilāj* / hyleg, p. 790): "The point which is the focus of a **direction**,
often one of a standard set of five (**the luminaries, Ascendant, Lot of Fortune, and the prenatal
lunation**). In determining longevity, it is the **victor among** a set of possible points."
— note that is only four items named for a set of five; the Ascendant, Sun, Moon, Lot of Fortune and
prenatal lunation makes five, so the parenthesis is loosely written.

**House-master** (*kadkhudhāh* / alcochoden, p. 783): "One of the **lords of the longevity
releaser, preferably the bound lord**. But the Greek word is also used in a general way to mean
simply any lord, or even a victor."

**Directions** (p. 777): significator held stationary, promittors sent by primary motion, "The
degrees between the significator and promittor are converted into years of life. **This is the
method used in distributions. An astronomically less accurate version is done by ascensions.**"

**Distribution** (p. 777): "The primary **direction of a releaser** (often the degree of the
Ascendant) **through the bounds**. The bound lord of the distribution is the **distributor**, and any
body or ray which the releaser encounters is the **partner**."

Related: **Distributor** / *jārbakhtār* / *qāsim* (pp. 777, 784, 789); **Partner** (p. 788);
**Profection** / *Turning* (p. 789); **Lord of the year** / *sālkhudāh* (pp. 785, 791);
**Fardār / firdāriyyah** (p. 781); **Revolution** (p. 791) — "understood to involve an entire suite
of predictive techniques, including **distribution, profections, and fardārs**"; **Ages of Man**
(p. 771); **Turn / Lord of the orb** (pp. 787, 794); **Hundreds** and **Thousands** (pp. 783, 794);
**Planetary years** (p. 788); **Ninth-parts** (p. 786); **Tasyir** (p. 793); **Namūdār** (p. 786).

Two notes:

- **Distribution ≠ the ascensional approximation.** The glossary distinguishes true primary
  directions from the "astronomically less accurate" ascensional version. `NOT_IMPLEMENTED_COVERAGE`
  already records Sahl's ascensional distribution (Ch. 1.18, 20–22). These are two different
  techniques and should not be conflated if the deferral lifts.
- **Namūdār** is defined here ("a special way of determining the moment of conception or the
  nativity, if they are known only approximately") — and `DOCTRINAL_CAVEATS.md` already forbids
  encoding its arithmetic, because Dykes says he does not understand the operation in *Nativities*
  Ch. 1.11. Having a glossary definition does **not** lift that; the definition says what it is for,
  not how to do it.

---

## 10. Summary — what the glossary changes

| Kind | Item |
|---|---|
| **Dissolved on checking** | Assembly 12° vs 15° is *not* a conflict: the glossary reports Abū Ma'shar VII.4, 3, and Sahl's 12° is derived from his own body table (Ch. 3, 12–18) — §1a |
| **New numeric conflict** | Sun's rays: per-planet (Abū Ma'shar VII.2) vs generic 7.5°/15° "later" scheme — §1c |
| **Named attribution to Sahl** | Cazimi = **same degree**, not 16' — §1b |
| **Corrects an earlier artifact** | Burnt-path degrees *are* in the corpus, with two competing spans — §1d |
| **Strengthens an earlier finding** | Crooked/straight latitude inversion now attested in prose, not only Figure 3 — §2a |
| **Resolves an earlier open question** | 7-place vs 8-place = for the native vs for the planet itself — §2b |
| **Corroborates a project decision** | "Advancing" has the senses the project already records, plus eastern-quadrants named as standard — §2c |
| **Confirms** | Overcoming = second/left/sinister aspect, three sources agreeing — §2d |
| **Free fixtures** | antiscia 10°♋→20°♊; twelfth-part 4°♊→♋; right/left from ♑; proper face ♀/☉ — §3 |
| **Ambiguity warnings** | eastern/western (4 senses), emptiness in course (2), testimony (4), victor (2), the sect cluster (6 terms) — §4, §5 |
| **New oddity** | right-siding and spear-bearing given as synonyms, making Appendix A ¶49 redundant — §8a |
| **Glossary defect** | *Fall* entry misprints the Greek as *hupsōma* (= exaltation) — §7 |
| **Does not license** | completing the antiscia pair list; encoding *namūdār* — §3, §9 |
