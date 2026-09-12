# Phase 1 — Sahl, *On Nativities* (complete)

Source: `on_nativities.md`, Sahl Vol. I pp. 255–749 (495/495 page markers per `CORPUS_MANIFEST.md`),
13,090 lines, Figures 48–71. Read in full on 2026-09-08 in twenty-two 600-line slices; every
sentence quoted below was read in that pass and is cited by chapter and sentence number with
the OCR line in backticks where it helps (`:NNNN`).

Structure, counted from the headings in the file (extractor in
`tests/test_nativities_citations.py`): **12 chapters and 161 sub-headings** (173 headings in all;
Ch. 6.3 has ten sub-subchapters, Ch. 10 has 10.1.1–10.1.6, 10.2.1–10.2.7). The brief's "17 books,
135 subchapters" is a different count of a different thing and is not reconciled here.

Citation: **Nativities Ch. N.M, P** (chapter, subchapter, sentence). Sentence numbers restart per
subchapter. Where a chapter has a preamble before its first subchapter (Chs. 3, 5, 6, 7, 9, 10, 11,
12), the preamble is cited **Ch. N, P**, not Ch. N.1, P — four `app.py` citations had that wrong
(see `10_on_nativities_citation_audit.md`).

This is the Phase 1 artifact that Phase 0 scoped out as "previously reconciled." The 85-odd
`app.py` citations are audited separately in `10_…`; this file records what the text says.

---

## 0. What the book is, and why its authorship matters for citing it

Sahl is a compiler. Dykes's apparatus attributes nearly every passage to a source, and the sources
disagree with each other inside the same chapter. The named layers, in rough order of bulk:

- **al-Andarzaghar** (the *Book of Aristotle*, "BA"), the spine of Chs. 2–12 — item lists at the
  head of each chapter, then the items worked;
- **Māshā'allāh** — the "lord of the Nth in the houses" and "Lot of X in the houses" sections
  (his *Treatise on Lots*, cited by Dykes to Tehran MSS), plus Ch. 1.23 on the releaser;
- **Dorotheus** (*Carmen*), often at one remove through BA, and sometimes in a *different*
  translation from 'Umar's (7.1, 35 fn. 29: *"an example of Sahl having a totally different
  translation of Dorotheus than Carmen"*);
- **Ptolemy**, **Rhetorius**, **Theophilus**, **Valens**, **Hermes**, **Nawbakht**, **al-Khayyāt**,
  the **Bizidaj**, **Abū Sinīna**, **Muhammad b. Bishr al-Khurāsānī** (4.4, 5: *"An astrologer
  currently unknown"*).

Two consequences for any citation:

1. **"Sahl says" usually means "Sahl transmits."** When `app.py` attributes 1.23, 17 to Māshā'allāh
   it is right to; when it attributes the Lot of authority to Māshā'allāh (10.2.5, 4–14) it is
   right to — and Dykes's fn. 166 there is explicit that *"Sahl quietly switches to Māshā'allāh's
   treatise on Lots … substituting another one without telling us that the formula is different."*
2. **The same doctrine is stated two or three times by different sources, and the statements
   differ.** §12 collects these. They are recorded, not resolved.

---

## 1. ★ The releaser and the house-master (Chs. 1.15–1.23)

### 1a. Nawbakht's releaser rules — the operative list

> "**6** Then look in nativities of the day at the Sun and the meeting: because if you found the
> Sun in the Ascendant, the Midheaven, the house of hope, or in the stake of the west, or in the
> eighth, then he will have a releaser from which is taken the indication of life. **7** But if you
> do not find the Sun in any of these places, or he was in one of them but the lord of his bound
> was not looking at him, nor that of his house, exaltation, triplicity, or face, then the Sun will
> not be the releaser. **8** And with that you must look at the meeting, where it is: for if the
> meeting was in any of these five places, then the meeting is the releaser. **9** But if the meeting
> and the Sun were both falling, then the releaser at that time will be the Ascendant."
> — Nativities Ch. 1.15, 6–9 (`:738`)

> "**10** And in nativities of the night, begin by looking at the Moon, the fullness, and the Lot of
> Fortune. **11** Now if you found the Moon in a stake or what follows a stake, with the lord of the
> bound, house, exaltation, triplicity, or image looking at her, then the Moon is the releaser.
> **12** But if the Moon was falling or none of these indicators is looking at her, then you must turn
> to the fullness … **13** (And that one—of any of these indicators—which is looking at the
> releaser, is the house-master.) **14** Now if the fullness was also falling … then the Lot of
> Fortune is the [releaser]." — Nativities Ch. 1.15, 10–14 (`:740`)

Five places by day: **1, 10, 11, 7, 8** — *the eighth is in the list*. Fitness requires one of the
five lords to aspect. The Ascendant is the day fallback; by night the chain is Moon → fullness →
Fortune. ¶5 records that Sahl *tested and rejected* Dorotheus's rule that a releaser in the
seventh in a feminine sign is "feminized twice."

### 1b. ★ The ranking of the five lords, and the two-share rule

> "**2** Now if you found all of the five indicators looking at the releaser, then the stronger of
> them is the lord of the bound, then the lord of the house, then the lord of the exaltation, then
> the lord of the triplicity, then the lord of the image. **3** And if you found one of them having
> two shares, then the one having two shares is stronger than the lord of [only] a single one.
> **4** And if you found the releaser in the bound of a planet, and that planet was in the Ascendant
> with the releaser, it is stronger than the others. **5** But if the house-master was under the
> rays, then it is deceptive, subtractive, corrupting." — Nativities Ch. 1.20, 2–5 (`:969`)

**bound > house > exaltation > triplicity > image**, with two overrides (two shares beat one; the
bound lord bodily in the Ascendant beats all). ¶1 prefers an eastern lord, and by sect (*"a male
planet [by day], and by night the female planets"*). This is the ranking `app.py:4290` carries, and
it is the one that conflicts with *Questions* Ch. 13, 7 (house > triplicity > bound > face) — see
`01_on_questions.md` §3.

### 1c. Years of the house-master (1.20, 7–13) and its aspects (1.21)

The greater years are granted when the house-master is *"in the Ascendant or in the Midheaven, or in
the sign of the west, or the eleventh, enhanced"* (1.20, 10), or under the earth eastern in its own
share (¶11, *"and by night in the fourth and fifth"*), or in the eleventh diurnal in its own place
(¶12). ¶13 is partly illegible in the OCR (*"[illegible] greater [illegible] it grants the lesser
ones"*).

> "**11** And if you found the Head with the house-master, and the house-master is a fortune, then it
> adds one-fourth of the years which the house-master indicates. **12** And if it was with the
> Tail, being distant from it by 12°, …" — Nativities Ch. 1.21, 11–12 (`:1046`)

fn. 169: *"it will subtract one-fourth, if it is at or closer than 12°."* ⚠ **The 12° is stated for
the Tail only**; the Head in ¶11 has no orb. `app.py:5111` applies 12° to both, citing this
sentence and *Introduction* Ch. 3, 107 — the second citation is where the Head's orb would have to
come from.

### 1d. The Moon under the rays: 15°, not 12°

> "**6** And if the Moon was under the rays, she will not be fit to take up [the role of the]
> manager (and that is if there was 15° between her and the Sun, in front of him and behind
> him)." — Nativities Ch. 1.19, 6 (`:953`, Dorotheus)

Abū Ma'shar VII.2, 61 and 72–73 give 12. `app.py` keeps 12 (`MOON_RAYS_ORB`) with a sidebar switch
to 15; both witnesses are quoted there. Note the context: *fitness as releaser/manager*, not a
general "under the rays" definition.

---

## 2. ★ The five-degree rule — three statements, one wider than the others

> "**19** And know that if there were 5° between a planet and the degree of the Ascendant from
> behind it (that is, if it was before the Ascendant by 5°), its strength will be in the
> Ascendant, and it will be fit for releasing; **and likewise in all of the houses**."
> — Nativities Ch. 1.18, 19 (`:899`); fn. 139: *"This is Ptolemy's 5° rule in Tet. III.10."*

> "**9** And the planets will not fall from the stakes except after 5°, and the planets do not
> become powerful in the sign [they are in] until they travel 5° in it." — Nativities Ch. 1.22, 9
> (`:1157`); fn. 176: *"This sentence represents Sahl's Aphorism #44."*

So: **1.18, 19 = all twelve cusps** (with Ptolemy named as the source); **1.22, 9 = the stakes** (and
the sign-entry half); *Aphorisms* #44 = the stakes. Not a contradiction — the all-houses statement
contains the stakes statement — but they are not the same rule, and `app.py`'s
`FIVE_DEGREE_ALL_CUSPS` switch is the right shape for it.

---

## 3. ★ Easternness and westernness (Ch. 1.22, 1–8) — what Sahl actually gives

Dykes's table (`:1113–1115`, "relied on al-Bīrūnī for the diagrams"):

| | Westernizes at | Considered western | Considered eastern | Easternizes at |
|---|---|---|---|---|
| ♄ | 15° | 22° | 6° | 15° |
| ♃ | 15° | 22° | 6° | 15° |
| ♂ | **18°** | 22° | **15°** | 18° |

The sentences:

> "**1** And know that if there were 6° between Saturn and Jupiter and the Sun, then they are
> considered to be eastern, and they are powerful in the distributing of the lifespan and in every
> work, because in up to nine days the Sun will have passed them by 15°; but if they were less than
> that, they will not be fit. **2** And [Jupiter and Saturn] are not considered western until there
> are 22° between them and the Sun: at that time they are fit to be considered western. **3** And
> as for Mars, he does not easternize until there are 18° between him and the Sun. **4** Now if
> they were not like that [in the west], these stars will <not> enter under the rays on the seventh
> day, so they will not be fit at that time to be the house-master, nor for the distribution of
> life." — Nativities Ch. 1.22, 1–4 (`:1117–1123`)

> "**6** And the power of easternization [for] Saturn and Jupiter is when 15° have passed them, and
> Mars 18°. **7** And Venus and Mercury are eastern [when] direct in course before rising, or in
> front of the Sun ([he being] in the west), and there are 12° between them and the Sun. **8** Now
> as for [being] in the west, if there were 15° between them and the Sun, they will have gone out of
> the rays and become western [risers]." — Nativities Ch. 1.22, 6–8 (`:1137–1139`)

Four things the code's earlier comment got wrong or over-stated, now corrected at `app.py:684–700`:

1. **Sahl gives no "burned" boundary.** The 6° of ¶1 is the *nine-day "considered eastern" floor*,
   a fitness allowance, not a burn orb. (`app.py:4930` had this right all along; `:690` did not.)
2. **Mars westernizes at 18° in Sahl's table**, not 15°. The engine's 15° west for Mars is Abū
   Ma'shar VII.2, 31 and is now attributed only to him.
3. **Mars's "considered eastern at 15°" is Dykes's inference**, fn. 174: *"I think it is safe to say
   that he is considered eastern at 15° and then actually emerges or easternizes at 18°."* The text
   gives only 18. (`app.py:4933` already says so.)
4. The inferiors' 12° east / 15° west (¶7–8) *do* match the engine and Abū Ma'shar. fn. (Dykes's
   comment): *"Carmen III.1 and BA II.2 differ in their intervals for Mercury and Venus (7): in BA,
   the intervals are 19°."*

⚠ fn. 174 also carries an OCR/editorial gloss: the source's *"31° per day"* for Mars is flagged in
the transcription as an error for 0°31′. Nothing in the engine depends on it.

Dykes's framing: *"this is really a general theory of easternness and westernness, but is being
applied here as a set of fitness criteria when finding the house-master."*

---

## 4. ★ Māshā'allāh's "own glow" — gender, not sect, and the sign follows the hemisphere

> "**17** And the strong one is if it is in a stake or what follows a stake, and it is luminous in
> its own place, in its own glow (and that is if the planet was male, by day above the earth in a
> male sign, and by night under the earth in a female sign; and if it was feminine, by night it is
> above the earth and by day under the earth), far from the rays." — Nativities Ch. 1.23, 17
> (`:1257`)

fn. 196: *"Māshā'allāh's account of this rejoicing condition is at odds with later accounts. In
later texts, diurnal (not male) planets should be above the earth during the day, and under the
earth at night (and for nocturnal planets the reverse); and the planet should be in a sign of its
own gender, not that of the chart."*

Three distinct features, all in `app.py`'s `DOMAIN_RULE_OPTIONS[1]`: (i) **male/female, not
diurnal/nocturnal** — so Mars is male with no exception stated; (ii) the sign's gender **follows the
hemisphere** (male sign by day above, *female* sign by night below); (iii) for feminine planets
**hemisphere only**, no sign condition. `01_appendices_a_and_b.md` and the glossary's *Hayyiz* are
the other witnesses; this is the primary one.

---

## 5. Distributions, profections and the other timing methods — read and recorded, not implemented

Implementation is on hold pending *Revolutions* / Persian Nativities IV
(`project_timing_deferred_pending_revolutions`). What the text gives:

### 5a. ★ The distribution rates

> "**21** Then how[ever] many degrees it traveled in the bound, and how many minutes, direct the
> degrees from the degree in which the releaser is, by degrees of the ascensions of the signs in
> that city, for each degree (of the degrees of ascensions) a year, and for every 5′ a month, and
> for every 1′ six days, and for every 10″ a day. **22** So direct them in this way until it goes
> out to the next bound, and the distribution will belong to the lord of that bound."
> — Nativities Ch. 1.18, 21–22 (`:903`)

**1° = 1 year, 5′ = 1 month, 1′ = 6 days, 10″ = 1 day** — by *ascensions in that city*. The
Timing page's flat 1°/year is labelled as not this (`app.py:4294`).

### 5b. Distributor vs. lord of the year — the text contradicts itself

> "**33** And know that the lord of the distribution is like a tender [of sheep], and the lord of
> the year like a hireling; so if the tender committed himself to his sheep in a powerful way, the
> hireling would have not power over harming the sheep." — Nativities Ch. 1.23, 33 (`:1336`)

> "**2** And know that turning is the foundation of the work of the stars and [their] appointed
> time, and it is stronger <than> the distributor of time." — Nativities Ch. 1.24, 2 (`:1480`)

fn. 245: *"But this seems to contradict Ch. 1.23, 33 above, which said that the distributor is
stronger. This should probably read that it is stronger when combined with the distributor."* ⚠
Recorded as an unresolved internal disagreement (§12 #3).

### 5c. Other rules in Ch. 1.23–1.24

- 1.23, 34: the distributor *"has authority over many years according to [the size of] its bound
  (and the lord of the rays is like that)"*.
- 1.23, 37: *"an infortune corrupts four signs, unless it is received; and if it was received from an
  opposition, it does grant but then corrupts according to its position."* (`:1360`)
- 1.23, 60: *"the Head does not increase and the Tail does not decrease, but the Head strengthens
  the governor and the Tail introduces illnesses into the body in that distribution."* (`:1412`)
- 1.24, 1: profection *"is a year or a month for every sign; then it returns every twelve months to
  the Ascendant, and every twelve years."* (`:1478`)

### 5d. The six-method list (Ch. 2.22, 1)

> "look at [1] the course of the planets and their connections, and [2] the stakes, and [3] the Lot
> of Fortune and the Lot of the Invisible, and [4] the ascensions of the signs <and> from the
> periods of the planets (the greatest, the middle, and the least), and [5] the distributor of time
> and [6] the lord of the year" — Nativities Ch. 2.22, 1 (`:4328–4348`)

fn. 271 reads these as: [1] primary directions (or transits, fn. 272), [2] ages of life by
quadrant, [3] Lots of Fortune and Spirit, [4] Valens's ascensions-and-periods method, [5]
distributions, [6] profections of the Ascendant.

### 5e. Parents' timing — three different keys in one book

| Passage | Key |
|---|---|
| 4.3, 16–17 (Bizidaj) | direct to the light of Mars: *"for every degree of it a month; and if it went beyond that, then make it years"*; if Mars is powerful, *"make it days"* |
| 4.12, 3 (al-Khayyāt) | *"for every degree a year and for every sign a year"* (fn. 173: the second *"could be a profection"*) |
| 4.13, 2 / 4.20, 38–43 | directed Lot of the father **plus** Saturn's transit: *"when Saturn passes over it in his transiting, before he casts his light upon it"* (fn. 179: a combination of distributions and transits) |
| 4.20, 23 | Lots of the parents *"by degrees of ascension … for each degree a year"* |
| 3.8, 3 (siblings) | *"direct the Lot to the infortunes, a year for every degree, by degrees of ascensions"* |

### 5f. Valens's years from the Lot of Fortune — stated twice, with different numbers

> "**35** if you found the Lot made unfortunate from an opposition, it indicates his chronic
> illness, up to 7 years; and if it was from the right triplicity, then up to 9 years; and if it was
> from its right square, up to 10 years; and if it was from its left trine, up to 3 years; and if it
> was from the twelfth from it, then up to 12 years; and if it was in the second from it, then up to
> 2 years." — Nativities Ch. 1.37, 35 (`:2800`)

> "**4** if it was made unfortunate from the opposite, it indicates a chronic illness at 7 years; if
> it was from the first sextile, then at 3 years; if it was from the second sextile, then at 11
> years; if it was from the first square, then at 4 years; if it was from the second square, then at
> 10 years; if it was from the first trine, then at 5 years; if it was from the second trine, then
> at 9 years. **5** And if the infortune was in the second from it, then at 2 years, if it was in the
> twelfth from it, then at 12 years." — Nativities Ch. 6.5, 4–5 (`:8345`, Figure 60)

And the sign table: **1.37, 36 gives Aries 19, Taurus 25**; **6.5, 6 gives Aries 15, <Taurus 25>**
(Taurus supplied by Dykes from Valens). ⚠ Same doctrine, same source (Anth. III.12), two different
tables in the same book (§12 #8). Figure 61 illustrates 6.5.

### 5g. Marriage timing (7.4)

Profection of the year to the sign of the Lot of wedding (7.4, 4: *"if the year made the rounds
from the nativity, so that it reached the sign in which the Lot of wedding was, and Saturn is not
looking, then he will marry"*), Jupiter's transit to Venus's natal sign or its lord (7.4, 1–3, 6),
and the quarters of the circle for age (7.4, 9–17, Ptolemy).

---

## 6. ★ The Lot of Fortune (Ch. 1.37, 1–4) — and the nearest thing to a Spirit formula

> "**1** The Lot of Fortune and its lord indicate the condition of the body just as the Ascendant
> and its lord do, because the Lot of Fortune is 'the Ascendant of the Moon,' just as <the
> Ascendant [itself]> is the Ascendant of the Sun. **2** And the knowledge of that is if you
> multiplied what has already passed of the day by what [is] the houses of the portions of its
> hours, then you cast it out from the place of the Moon, [and] it will be cut off at the position
> of the Lot of Fortune. **3** And likewise the Lot of Fortune is the Ascendant of the Moon by night,
> and likewise the Lot of the Invisible by day is the Ascendant of the Moon." — Nativities Ch. 1.37,
> 1–3 (`:2712`)

fn. 494: *"Māshā'allāh now describes the usual formulas for the Lot of Fortune: by day from the Sun
to the Moon and by night the reverse, the result being projected from the degree of the Ascendant."*

So the Sun→Moon formula is **Dykes's gloss on ¶3**, not Sahl's sentence; Sahl's own ¶2 is an
hour-based construction (`app.py:3929` says exactly this). ¶3's *"the Lot of the Invisible by day is
the Ascendant of the Moon"* is the closest the corpus comes to a Spirit formula: it identifies
Spirit-by-day with Fortune-by-night, which implies Moon→Sun by day — but it never states it, and a
grep of every corpus file finds no Spirit formula anywhere. `app.py:3934` ("formula from the course
tables") stands.

¶4 has the Lot *"<advancing>"* (Dykes's supplement, fn. 495) as the first condition for its good
effect — one of the sites for the advancing question (§10).

---

## 7. The Lots, as stated (every formula in the book)

Each row: what the text says, where, and the reversal-by-night **as the text has it**. "Dykes" marks
formulas that exist only in the apparatus. This is the table `LOT_DEFINITIONS` is audited against in
`10_…`.

| Lot | Formula as stated | Night | Where |
|---|---|---|---|
| Fortune | hour-based (¶2); Sun→Moon from Asc (fn. 494) | reversed (fn.) | 1.37, 1–3 |
| Constitution | *"from the Sun to his foundation … project it from the degree of the Moon … by night from the Moon to the degree of her foundation … projected from the Sun"* | both ends change | 1.34, 13 (`:2453`, p. 358); fn. 436: "foundation" *"sounds like the fourth place from the Sun, but is perhaps 0° Leo"* |
| Assets (Māshā'allāh) | *"count from the lord of the second to the second place, and you add on top of that the degrees of the Ascendant"* | none stated | 2.15, 1 |
| Assets / "livelihood" (Dorotheus) | *"count from Jupiter to Saturn by day, and by night the reverse of that, and cast it out from the Ascendant"* | reversed | 2.15, 17; fn. 209: Abū Ma'shar's "Lot of life"; *"identical to the generic Lot of children"* |
| Siblings (Hermes) | Saturn→Jupiter from Asc, *"for one who was born by day and night"* | **not** reversed (fn. 120 recommends reversing) | 3.11, 2 |
| Siblings / number (Valens) | Mercury→Jupiter, *"by night and day"* | not reversed (fn. 121: in Dorotheus it *is* reversed) | 3.11, 3; ¶4 *"both of the Lots are correct, so work with them both together"* |
| Native male/female | lord of the Moon's house→Moon by day, *"by night the contrary"*, + Asc | reversed | **3.13, 20** (`:5075`) |
| Exaltation (Theophilus) | Sun→its exaltation degree by day; Moon→hers by night; from Asc | both ends change | 4.1, 6 |
| Father | Sun→Saturn by day, Saturn→Sun by night | reversed | 4.14, 1 |
| Father, Saturn under the rays | Mars→Jupiter | none stated | 4.14, 2 |
| Mother | Venus→Moon by day *"(and by night the contrary)"* | reversed | 4.14 fn. 198 (Dykes) |
| Children (Theophilus per Abū Ma'shar) | Jupiter→Saturn *"by night and by day"* | not reversed | 5.1, 91 |
| Children (Hermes per fn. 51) | Jupiter→Saturn by day, reversed | reversed | 5.1, 91 fn. 51 |
| Children (Hermes per Sahl) | Mercury→Saturn | none stated | 5.1, 92 |
| Timing of children | Mars→Jupiter from Asc | none stated | **5.3, 2 and 8** |
| Male / female children | Moon→Jupiter; Moon→Venus | none stated | 5.3, 16 (fn. 85: Carmen has Sun→Jupiter) |
| Chronic illness | Saturn→Mars by day, *"by night the contrary"* | reversed | 6.3.4, 2; 6.3.5, 1 |
| Slaves | Mercury→Moon by day, *"by night the reverse"* | reversed (fn. 281: reading "and" for "or") | 6.10, 20 |
| Men's marriage | Saturn→Venus | none stated | 7.1, 5; 7.1, 223; **7.2, 44** |
| Women's marriage | Venus→Saturn | none stated | 7.1, 6; 7.1, 224; 7.2, 44 |
| Venus → 7th | *"from Venus to the stake of marriage"* / *"to the house of marriage … cast out from the Ascendant"* | none stated | 7.1, 10; 7.1, 145 |
| Passion (Erōs) | Fortune→Invisible *"by day"* | (fn. 11: reversed) | 7.1, 141; fn. 11 on 7.1, 9 |
| Men's / women's deception | Sun→Venus; Moon→Mars, *"by day and by night"* | not reversed | 7.1, 220–221; fn. 139: the Sun→Venus Lot can only fall in signs 11–3 |
| Sun→Moon from Venus | *"<and projected from Venus>"* (Dykes) | not reversed in Sahl (fn. 237: reversed in Carmen) | 7.4, 8 |
| Killing | lord of Asc→Moon by day, reversed, from Asc | reversed | 8.2, 17 |
| **Death** | Moon→degree of the 8th, *"and cast out from Saturn"* | not reversed | 8.6, 1; ⚠ fn. 89: *"Reading with the Māshā'allāh MSS for 'Ascendant'"* — **the projection from Saturn is an emendation; Sahl's MSS say Ascendant** |
| Travel | lord of 9th→9th, *"by night and day"*, from Asc | not reversed | **Ch. 9, 9** (preamble); 9.3, 4 (Antiochus); 9.4, 37 |
| Religion | (unstated; fn. 72: Moon→Mercury; fn. 116: *"could easily be the Lot of Spirit"*) | — | 9.5, 3 |
| Work / action | Mercury→Mars by day, *"by night the contrary"* | reversed | 10.1.1, 14 |
| Work / expedition | Saturn→Moon *"by day and night"* | **not** reversed (fn. 165: *"Paul instructs us to reverse it by night, but Abū Ma'shar says not to. We should follow Paul"*) | 10.2.5, 1 |
| Authority / work and craft (Māshā'allāh) | *no formula in Sahl*; fn. 166: *"defines this in the same way as the Lot of fathers (Sun-Saturn)"*; Fig. 63: ☉→♄, ASC **(R)** | Fig. 63 marks reversed | 10.2.5, 4–14 |
| Valor / courage | (unstated; fn. 214: Hermetic courage, Mars→Fortune, reversed) | — | 10.3, 1, 8, 11 |
| Friends | *"<from the Moon to Mercury> by day, and by night the contrary"* (angle brackets = Dykes) | reversed | Ch. 11, 5; **Sahl's own statement 11.1, 29**: *"count by day from the Moon to Mercury (and by night the contrary of that), and on top of it is added the degrees of the Ascendant"* |
| Desire (Erōs again) | Fortune→Spirituality by day, *"by night the converse"* | reversed | **11.2, 4–5** |
| Necessity | (fn. 62: Spirit→Fortune by day, reversed) | reversed | **11.4, 18** fn. 62 |
| Enemies | M: Mercury→"Lot of the Moon" (Fortune); E: Mercury→Moon; Latin: lord of 12th→12th | (Fig. 71) | 12.1, 48–49, Figure 71 |
| Riding animals | Sun→Saturn *"by day and night"* | not reversed | 12.2 fn. 18 (Dykes's private MS) |
| Spirit / the Invisible | **named only** (1.37, 3; 2.22, 1; 6.3.9; 6.6; 7.1, 141; 9.5, 73; 11.2, 5) | — | no formula anywhere in the corpus |

Two things the table makes visible:

- **Sahl's night-reversal is inconsistent by Lot**, and Dykes's footnotes recommend reversing three
  Lots the text does not (siblings, expedition, Sun→Moon-from-Venus). `LOT_DEFINITIONS` records
  each as the text has it, with the apparatus as a separate row where it differs — the right shape.
- ⚠ **Figure 63 marks the Sun→Saturn authority Lot (R)** and 4.14, 1 reverses the father Lot it is
  "defined in the same way as"; `LOT_DEFINITIONS['work_authority']` does not reverse. Recorded as a
  ⟨CHOICE⟩ in `10_…` §5; not changed.

---

## 8. Māshā'allāh's "in the houses" sections — the source of the two prose tables

The Reference Guide's *"lords of other places in the Nth (Masha'allah)"* (`MASHAALLAH_LORDS`) draws
on twelve sections, all present and all Māshā'allāh's by Dykes's attribution:

| Lord of | Section | Lot of the topic in the houses |
|---|---|---|
| 1st | 1.36, 78–97 | 1.37 (Fortune) |
| 2nd | 2.14, 9–28 | 2.15, 3–14 |
| 3rd | 3.10 | 3.12 |
| 4th | 4.11 | 4.14, 11–25 |
| 5th | 5.1, 78–90 | 5.1, 93–108 |
| 6th | 6.3.4, 12–23 | 6.3.5 |
| 7th | 7.1, 205–216 | 7.1, 225–237 ⚠ |
| 8th | 8.5 | 8.6 |
| 9th | 9.4, 23–34 | 9.4, 37–45 |
| 10th | 10.2.4 | 10.2.5, 4–14 |
| 11th | 11.1, 16–27 | 11.1, 35–38 |
| 12th | 12.1, 35–46 | 12.1, 48–55 |

Each section ends with the same operating condition, e.g. 6.3.4, 24: *"Work this topic if the sixth
sign and its lord are free of the infortunes and the fortunes do not testify to them"* — i.e. these
readings are for the **unaspected** case only. The Guide's table does not carry that condition;
`PLANETS_IN_HOUSES`/`MASHAALLAH_LORDS` present the readings unconditionally.

⚠ 7.1, 225–237: fn. 141: *"in the Māshā'allāh text, this Lot is explicitly said to be the
Sun-Venus Lot mentioned in 220, not the Venus-Saturn Lot."* The "Lot of marriage in the houses"
delineations belong to the deception Lot, by Dykes's reading.

5.1, 85 (lord of the 5th in the 8th) is *"[illegible] they will survive and will be miscarried"* —
the cell the Guide resolves (`09_prose_tables_2026-09-08.md`).

---

## 9. ★ Spear-bearing — read and recorded; not implemented

The brief names four places. There are more, and the glossary is explicit that there is no single
definition: *"A special configuration in a chart showing eminence and prosperity, of which there
were several types and definitions"* (`sahl_glossary.md:437`). Synonyms in the glossary: *right-
siding*, *honor guard / paying honor*, *dastūriyyah*, *doryphory*, *bodyguarding*.

### 9a. Ch. 2.5 — the aspect-and-dignity definition (Antiochus's "first definition")

> "**2** If you found one of the two planets in square or sextile to its companion, and they were
> both in their exaltations or their houses, or one of them was in its exaltation and the other in
> its house, or one of its shares, and each one of the two was casting rays upon its companion,
> then that is a strong right-sidedness. **3** And if they were not in their houses nor exaltations,
> but they were both of the sect of the day or the sect of the night, then that is also called
> right-sidedness (though it is below [the first version])." — Nativities Ch. 2.5, 2–3 (`:3614`)

fn. 121: *"The discussion in 2-3 represents a version of the first definition of Antiochus (see
Schmidt 2009, pp. 247ff). For more examples, see Ch. 10.2.7."* Note that ¶2 does not mention a
luminary at all — *"one of the two planets"*; ¶1 asks for *"the diurnal planets … right-siding by
day, and the nocturnal ones by night"*; ¶4–8 then delineate *"Mars right-siding for the Sun or
Moon"*, etc. ¶9 adds a reversal (fn. 125: *"the fortunes are in the stakes, and the luminaries act
as their spear-bearers"*).

### 9b. Ch. 4.15, 4 — the sect condition and the Sun/Moon asymmetry (`:6081`)

> "**4** Look at the spear-bearing of the Sun and Moon: for if the planets which are not [of the
> sect] have the spear-bearing of the luminaries, then the parents will not be fortunate, and
> especially if Mars is behind the Sun, and Saturn behind the Moon: judge for both of the parents
> that they will be disreputable [and] low." — Nativities Ch. 4.15, 4

fn. 212: *"Rhetorius prefers morning stars to spear-bear for the Sun, and evening stars the Moon."*
fn. 213: *"I believe this means different things for the Sun and Moon. For the Sun and Mars, it
probably means that Mars is in an earlier degree than the Sun ('behind' him zodiacally), but so that
he will rise before the Sun in the morning. For the Moon and Saturn, it probably means that Saturn is
in a later degree than the Moon ('behind' her in diurnal motion), but so that she is applying to
him. Some types of spear-bearing make these distinctions of diurnal motion and zodiacal degree, for
the Sun and Moon respectively."*

### 9c. Ch. 10.2.1, 10–15 — Ptolemy's version

> "**10** … if the luminaries were both in male signs, in the stakes (or one of them), and especially
> if they were both in their own domain and the planets formed an honor-guard for them (and that is
> if the planets were eastern from the Sun and western from the Moon), then one whose nativity was
> like that will be an elevated king, and especially if the planets eastern from the Sun were in the
> stakes … **14** And if the luminaries were not in the stakes, and there was an honor-guard (and it
> is spear-bearing) in the stakes, and they are not looking at them, then the native will be
> revered, known in the cities." — Nativities Ch. 10.2.1, 10–14 (`:12029–12035`)

fn. 129 on ¶1: *"That is, spear-bearing. See the Glossary and 10ff below, as well as Ch. 10.2.7."*
fn. 141 on ¶14: *"in this example Ptolemy does allow the spear-bearing planets to be either in a
stake or configured to it."* 10.2.6, 2 ("the upper posts") is a further variant: fn. 168 *"This seems
to be a version of spear-bearing."*

### 9d. Ch. 10.2.7 — the seven examples (Figures 64–70)

| # | Asc | Data as given | What is called spear-bearing |
|---|---|---|---|
| 1 | ♍ 6° | ☿ ♎ 4°, ♀ ♍ 21°, ☽ ♍ 6°; Sun not given | ☿ and ♀ *"come to be in a position of paying honor from the Sun, without a connection from him to them, and without their position being at sunrise except that they are eastern from him"*; ♀ pays honor to the Moon *"setting after her"* |
| 2 | ♈ 19° | ☉ ♈; ♀ ♓ 8°, ☿ ♓ 29°, ♂ ♓ 24°, ♄ ♑ 9° | *"these four planets … eastern from the Sun and on his right side, and his honor-guard"* — a king |
| 3 | ♎ (late) | ♄ ♍ 19°, ☉ ♏ 26°, Lot of father ♑ | ♄ *"in the honor guard of the Sun and his right side, and in [Saturn's] easternization in the early mornings"* → father elevated; ♄ in the 12th → father killed (fn. 201) |
| 4 | ♉ 9° | ☉ ♒ 25° on the MC, ♃ ♒ 1°, ☽ ♓ 9°, ☿ ♓ 12°, ♄ ♈ 13° | ♃ *"in his easternization from the Sun, and Saturn and Mercury in their westernization from the Moon"*; fn. 203: Asc/MC *"impossible for any latitude"* |
| 5 | ♉ 3° | ☉ ♍ 14°, ♀ ♌ 26° | *"the easternization of Venus alone, through a connection"*; fn. 206: *"the Sun is not angular by sign, nor … by dynamic division"* |
| 6 | ♈ 3° | ☉ ♒ 16°, ☿ ♒ 5° | ☿ *"in the honor guard of the Sun and his right side, in his own bound, eastern"* — a philosopher; fn. 208: the Sun again not angular |
| 7 | ♐ 9° | ☉ ♈ 8°, ☽ ♐ 2°, ♃ ♑ 14°, ♀ ♈ 2° | ♀ and ♃ pay honor to the Sun *"in their easternization in the early mornings"*; ♃ to the Moon *"in his westernization from her"*; fn. 209: *"Only Venus can truly be easternizing, and then only if retrograde. But they are both eastern"* |

What the examples share: **for the Sun, a planet in an earlier zodiacal degree ("eastern from him",
"on his right side"), with no aspect requirement stated and no visibility requirement (ex. 1 fn.
191: "close enough that they do not make a morning rising out of the rays"); for the Moon, a planet
in a later degree ("setting after her", "westernization from her").** Angularity of the luminary
is *not* required in examples 5 and 6 (Dykes flags both). The bound (ex. 6) and sect (ex. 1 fn. 189
*"'domain' … should probably be read as 'sect'"*) appear as qualifiers. Example 3 and 4 tie the
spear-bearer's house rulership to *why* the eminence (fn. 201).

### 9e. Why this is not implementable from the text alone

Three definitions coexist: (A) 2.5's mutual aspect + dignity/sect, with no luminary required; (B)
Ptolemy's 10.2.1, eastern-of-Sun / western-of-Moon in or configured to the stakes; (C) the 10.2.7
degree-order reading with the fn. 213 asymmetry, luminary angularity optional. They give different
answers on ordinary charts, and 7.3, 2 even uses *"the spear-bearing planets"* of **Venus**. The
glossary says "several types and definitions" and does not choose. **Recorded; no fixture, no code.**
The TNAC course material named in the brief as the possible arbiter was not opened in this pass.

---

## 10. "Advancing" — the primary-motion sense, stated in four places

- 1.29, 25 fn. 312: *"مقبل. That is, moving toward the angular degrees by primary motion."*
- 2.13, 12–14 with fn. 172–173: *"advancing in the two ways"* = *"angular both dynamically (by
  quadrant division) and by sign"*.
- 7.8, 39 / 10.3, 17: *"bravery and valor in the soul are from the advancement of the stars, if
  they were advancing [and] safe"*; fn. 231: *"the eastern quarter from the Ascendant to the
  Midheaven is advancing, while the quarter from the Midheaven to the Descendant is declining or
  retreating … the planet is moving up towards the horizon (the Ascendant) or the Midheaven, being
  dynamically angular or succeedent and not cadent."*
- 2.13, 43–45 vs 10.1.1, 22–26: the same Māshā'allāh sentence twice; 2.13, 43 reads *"received"*
  (مقبول) where 10.1.1, 24 reads *"advancing"* (مقبل) — fn. 186 and fn. 19 both prefer *advancing*
  as *"the proper contrast to retreating."*

This is the Fig. 90 / `project_advancing_two_senses` matter; nothing new decides it, but the four
statements are consistent with each other (primary motion toward an axis), and 2.13, 12–14 shows
Sahl using *both* the quadrant and the sign sense at once.

---

## 11. Other engine-relevant doctrines

### 11a. ★ The three 15° ascensional bands (2.13, 48–51; 2.16, 3 fn. 222; *Aphorisms* #45)

> "**48** … if the first lord of the triplicity of the glowing one is in a stake or what follows it,
> and that is the 15° which follows it, by degrees of ascensions: for if it was like that, it
> indicates praise and good fortune (and what is less [than that] in degrees is preferable). **49**
> Now if it was in the second 15°, it indicates his good fortune is below the first [type]. **50** And
> if it was in the third 15°, it indicates [what is in] the middle of assets. **51** And what is after
> that in degrees, up to the next stake, is of the nativities of the poor." — Nativities Ch. 2.13,
> 48–51 (`:3939–3959`)

fn. 222 (on 2.16, 3): *"a better, more faithful account of the method is in Māshā'allāh's version
above (Section 2.13, 48). In Carmen (I.28, 7) one measures out 45° in ascensions out from the degree
of an axis (not zodiacal degrees)."* *Aphorisms* fn. 57 says #45 *"is misstated here"* and
*"repeated correctly in Sahl's Nativities Ch. 2.13, 48-51."* 2.3, 4 (Dorotheus) has a coarser
version: *"the first degree of the sign up to the end of [the first] half of it by ascensions."*

### 11b. Grading the planet of work by dignity and condition (10.1.1, 34–46)

> "**35** So if the planet was in its house, it grants the middling work of the lowest work. **36**
> Now if it was in its house and its bound or in its house and its face, it grants more preferable
> works. **37** And if it was in its exaltation, it grants the preferable [and] more elevated of the
> ranks … **40** And if the planet was retrograde, then judge for him half of that work … **41** And
> if it was burned under the rays, then it subtracts from that work of his, one-third of it … **44**
> And if the planet of work was in its own fall, it grants the worst of works."
> — Nativities Ch. 10.1.1, 35–44 (`:11480–11490`)

fn. 25: *"It seems odd that burning would only take away one-third, while retrogradation would take
away one-half."* 10.1.3, 25–26: a trine *"makes it fortunate and grants to it … whether it is a
fortune or infortune"*; a square *"undermines it; and if it was a fortune, it will not corrupt it."*
10.1.3, 32: the Sun with the planet of work corrupts it *"(except with Mercury)"* … *"if it was with
[the Sun] in [the same] degree"* — an in-the-heart exception.

### 11c. Sign categories (1.38) and fertility lists — three lists, two of them disagree

- 1.38, 8: *"The signs of darkness are Libra, Capricorn."* 1.38, 9: *"the burned place of the signs
  is the end of Libra and the beginning of Scorpio."* (Compare the engine's 15♎–15♏ Via Combusta,
  which it does not source to Sahl.)
- **Ch. 3, 10**: *"the signs of many children are Cancer and its triplicity, and the signs hindering
  [them] are Leo, Virgo, and Capricorn; and the rest of the signs are middling."*
- **5.1, 8**: *"the signs of sterility are Gemini, Leo and its triplicity, Capricorn, Virgo, the
  beginning of Taurus, and the middle of Libra; and those abundant in offspring are Cancer and its
  triplicity (and Scorpio indicates an abundance of children as well as their death)."*
- Slave signs: 4.5, 27 = 6.10, 1: *"Taurus and its triplicity: the harshest of them is Capricorn,
  and the middling one of them is Virgo, and the more elevated of them is Taurus."*
- Signs of kings: 2.8, 5: *"Cancer, Aries, Leo, and Sagittarius."*

### 11d. Twelfth-parts — used, never defined

2.6 (Sun, Ascendant, Moon and the infortunes' twelfth-parts), 4.9 (*"the share of the twelfth part
of the degree of the Sun indicates the condition of the father"*), 4.2, 18, 4.5, 14, 4.15, 6, 6.2,
47, 10.1.1, 6. No sentence gives the construction. `app.py:5832` is right.

### 11e. Fixed stars for eminence (2.2) and the eye-harming degrees (6.2, 48–72)

2.2 lists thirty stars with Dykes's corrected table. 6.2 gives **four** lists of harmful degrees —
Dorotheus/al-Andarzaghar (¶49–55), Rhetorius (¶60–68, with fn. 81–89 noting where Rhetorius's own
numbers differ), the Bizidaj (¶69–72), Nawbakht (¶73–75) — summarised in **Figure 59**. They
overlap but are not identical (fn. 80). Not in the engine.

### 11f. Aspect grading and reception, in passing

- 4.17, 12–13: a *separating* opposition = *"the native's hatred for the father"*; a *connecting*
  opposition = *"quarreling without hatred"* (fn. 238).
- 8.3, 1–10 (Māshā'allāh): the infortune the lord of the Ascendant connects with, read by house.
- 9.4, 10–12: reflection/transfer of light between lord of the Ascendant and lord of the ninth,
  with the reflector's rulership deciding enslavement vs. freedom.
- 1.22, 10: *"the planets, in the condition of their retrogradation, are not powerful (neither the
  fortunes among them nor the infortunes), even though they still do good and evil"* (fn. 177 ≈
  *Aphorisms* #38).

---

## 12. Internal disagreements, collected

| # | Item | Statements |
|---|---|---|
| 1 | Dignity ranking for the house-master | 1.20, 2 (bound first) vs *Questions* 13, 7 vs glossary p. 777 — see `01_on_questions.md` §3 |
| 2 | Five-degree rule scope | 1.18, 19 *all houses* (Ptolemy) vs 1.22, 9 and *Aphorisms* #44 *stakes* |
| 3 | Distributor vs lord of the year | 1.23, 33 distributor stronger; 1.24, 2 profection *"stronger <than> the distributor"*; fn. 245 |
| 4 | Moon under the rays | 1.19, 6 = 15°; Abū Ma'shar VII.2, 61 = 12° |
| 5 | Mars's western orb | 1.22 table 18°; Abū Ma'shar VII.2, 31 = 15° (the engine's) |
| 6 | Night reversal of Lots | siblings (3.11, 2–3, not reversed; fn. 120–121 recommend reversing); expedition (10.2.5, 1 not reversed; fn. 165 reverse); Sun→Moon from Venus (7.4, 8; fn. 237); authority (Fig. 63 (R), no formula in text) |
| 7 | Lot of children | 5.1, 91 (Jupiter→Saturn unreversed, "Theophilus") vs fn. 51 (reversed, "Hermes") vs 5.1, 92 (Mercury→Saturn, "Hermes") — Hermes is credited with two different formulas |
| 8 | Valens's Fortune-years | 1.37, 35–36 vs 6.5, 4–6: aspects give 9/10/3 vs 3/11/4/10/5/9; Aries 19 vs 15 |
| 9 | Fertile / sterile signs | Ch. 3, 10 vs 5.1, 8 (Gemini, Taurus-start, Libra-middle added; Scorpio double-valued) |
| 10 | Lot of marriage in the houses | 7.1, 225–237 delineates the Saturn–Venus Lot in Sahl; fn. 141: Māshā'allāh's text means the Sun–Venus Lot |
| 11 | Lot of death projection | 8.6, 1 "from Saturn" is Dykes's emendation from the Māshā'allāh MSS and Carmen IV.3, 16; Sahl's MSS read "Ascendant" (fn. 89) |
| 12 | Lot of enemies | three formulas (12.1, 48–49, Fig. 71): M Mercury→Fortune, E Mercury→Moon, Latin lord-12→12 |
| 13 | Lot of religion | fn. 72 Moon→Mercury vs fn. 116 "could easily be the Lot of Spirit" |
| 14 | Received vs advancing | 2.13, 43 *"received"* vs 10.1.1, 24 *"advancing"*, same sentence (fn. 186, 19) |
| 15 | Sect of the primary malefic | 4.20, 31: Mars the main malefic *both* day and night for the father, because Saturn is the father's significator by night (fn. 288) |
| 16 | Lord of the tenth in the signs | 10.1.3's heading says "lord of the tenth"; fn. 65: *"This chapter actually describes the planet of work in the signs, not the lord of the tenth"* |
| 17 | Spear-bearing | three definitions (§9e); glossary: "several types and definitions" |
| 18 | Mars's daily motion | 1.22 fn. 174 *"31° per day"* flagged in transcription as an error for 0°31′ |
| 19 | Impossible configurations | 2.3, 50 fn. 107 and 10.2.1, 2 fn. 130 (all four in exaltation and in the stakes); 10.2.7 ex. 4 fn. 203 (Asc/MC impossible at any latitude) |

---

## 13. Where the engine and the text now stand

Handled in `10_on_nativities_citation_audit.md`; summary only:

- **Corrected (citation text only, no value moved):** the five chapter-locator errors the 05 review
  found and eight more this pass found (5.2→5.3; 7.4→7.2 twice; 3.1.2→fn. 121 on 3.11, 3;
  10.2.9→fn. 72 on 9.5, 3; 3.12→3.13; two more "9.1, 9" preamble misfilings; the Fig. 63 "Sun-
  Mercury" claim), and the *"same breakpoints independently"* solar-phase comment.
- **Open ⟨CHOICE⟩ items surfaced, not changed:** `work_authority` unreversed vs Fig. 63 (R); Lot of
  death's Saturn projection being an emendation; Mars 15° west (Abū Ma'shar's, now labelled so).
- **Confirmed negative claims:** no Lot of Basis anywhere in the corpus; no Spirit formula anywhere
  in the corpus (1.37, 3 comes closest).
- **Pinned:** every "On Nativities Ch. X" in `app.py` names an existing chapter
  (`tests/test_nativities_citations.py`; the vendored list is checked against the file when the
  corpus is present). Paragraph numbers are not pinned — the OCR cannot support it reliably.

---

## 14. What is *not* synthesized

The topical delineations — assets (Ch. 2), siblings (3), parents (4), children (5), illness (6),
marriage (7), death (8), travel and religion (9), occupation and kings (10), friends (11), enemies
and animals (12) — are read but not transcribed: roughly 190,000 words of "if the lord of the Nth
was in the Mth" and "if Saturn looked at Venus". The general machinery they share (§1–§11) is what an
engine can use; the Māshā'allāh "in the houses" sections are already in the app through the Guide
(§8), and their unaspected-case condition is the one thing from them worth carrying back.

Figures 48 (Ptolemaic ages), 49–52 (rectification), 55–56 (Valens years, 1.37), 57 (degrees of
nobility), 58 (death of the mother example), 59 (eye-harming stars), 60–61 (Valens years, 6.5),
62 (al-Andarzaghar's death items), 63 (three Lots of work), 64–70 (spear-bearing), 71 (three Lots of
enemies) were all read from the OCR tables; none of the diagram images was opened.
