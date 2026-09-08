# *On Nativities* citation audit — every `app.py` claim about the text, checked against the text

Baseline: `main` @ `bb1e1ce`, 1015 passed / 2 xfailed (re-run at the start of this pass, 137 s).
Branch: `on-nativities-2026-09-08`. Date: 2026-09-08.

**All `app.py:LINE` numbers below are the baseline's (bb1e1ce).** The corrections add eleven
lines (the solar-phase comment block +5, the Fig. 63 note at `:3910` +2, three note strings +4),
so post-fix positions from `:684` on are shifted by up to +11; §6 gives the corrected text so each
site can be found by content.

## 1. Method

1. Read `on_nativities.md` end to end (13,090 lines) in twenty-two 600-line slices, 2026-09-08,
   before opening any citation. The Phase 1 record is `01_on_nativities.md`.
2. Listed every line of `app.py` containing `Nativities`. **88 lines** (the brief's "85" is close;
   the exact number depends on what one counts). Two further case-insensitive hits — `:2489` and
   `:4993` — are quotations of *Introduction* Ch. 3 that happen to contain the word "nativities",
   not citations, and are excluded. Seven more locators sit on continuation lines of those 88 (a
   note string's second line, the "further Lots" list) and are audited as sub-rows **a–g**.
3. For each, located the cited chapter and sentence in the OCR and compared the claim with the
   sentence, quoting the text where they differ.
4. Classification, applied by content first and locator second:
   - **supported** — the cited sentence exists at the cited place and says what is claimed
     (quotations verbatim or with marked elisions);
   - **paraphrase-fair** — not verbatim, but a fair account of the passage;
   - **paraphrase-misleading** — the passage exists but the claim over-states or mis-describes it;
   - **unsupported** — the text does not say it;
   - **passage-not-found** — nothing at the cited locator says it (wrong chapter, wrong
     sub-chapter, or a chapter that does not exist). Where the sentence exists elsewhere, the
     row says where.

## 2. Counts

| Class | Main rows (88) | Sub-rows a–i (9) | Total (97) |
|---|---|---|---|
| supported | **74** | 0 | 74 |
| paraphrase-fair | 3 | 0 | 3 |
| paraphrase-misleading | 4 | 0 | 4 |
| unsupported | 0 | 2 | 2 |
| passage-not-found | 7 | 7 | **14** |

So: **74 of 88 citation lines are clean as written; 14 are not, and 7 of the 14 point at the wrong
chapter.** The nine sub-rows are continuation lines of those 88 (or, for h–i, a comment block
without the word "Nativities" that the edit script's occurrence count turned up); seven of the
nine are wrong. No computed value was wrong at any site; every defect is in the *locator* or in a
claim *about* the source. The 20 rows classed below paraphrase-fair (4 misleading, 2 unsupported,
14 not-found) are all corrected in this branch (§6); row 7's wording was adjusted in the same
block; rows 40 and 68 (paraphrase-fair) are left as they are. No doctrine or value in `app.py`
was changed.

Compared with `05_review_of_04_2026-09-07.md`, which sampled 22 sites and found 5 defects: all 5
are confirmed here, and **9 more locator defects** are new (`:4017`, `:4023`, `:4027`, `:3975`,
`:4094`, `:4306`, `:7313`, `:7431`, `:3917`), plus two **unsupported** claims about Figure 63
(`:4088–89`, `:3912–14`) — both describe a glyph column that the current OCR does not have.
Two of the new ones (`5.2` for 5.3, `7.4` for 7.2) were in `05`'s own "verified" list: `05`
checked the OCR *line* and quoted it correctly, but the line sits under a different sub-heading
than the one cited. Reading the line is not the same as reading the heading above it.

## 3. The table

Text is quoted from `on_nativities.md`; `:N` is its line. ✓ = the wording in `app.py` matches.

| # | `app.py` | Claims | Text | Class |
|---|---|---|---|---|
| 1 | 503 | 10.2.7, 22 has Mercury at ♒ 5° "in his own bound"; fn. 198 gives ♑ 0–7 to Mercury | 10.2.7, 21–22 `:12432`: *"the Sun in Aquarius 16°, and Mercury with him, 5°. So look at Mercury … in his own bound, eastern"*; fn. 198 `:12398`: *"the first 7° of Capricorn are indeed ruled by Mercury"* | supported |
| 2 | 552 | Guide's Māshā'allāh table draws on 1.36, 2.14, 3.10, 4.11, 5.1, 6.3.4, 7.1, 8.5, 9.4, 10.2.4, 11.1, 12.1; cell [8][5] illegible in Sahl | All twelve "lord of the Nth in the houses" sections exist at those chapters (`01_on_nativities.md` §8); 5.1, 85 `:6744`: *"[illegible] they will survive and will be miscarried"* | supported |
| 3 | 644–647 | 1.23, 17 quoted | `:1257` ✓ verbatim | supported |
| 4 | 685 | *"Sahl gives the same breakpoints independently in On Nativities Ch.1.22, 1-8"* | Sahl's table `:1113–1115` has **Mars westernizes at 18°** (engine 15°, from VII.2, 31), and 1.22 has **no "burned" figure at all** — the 6° of ¶1 is the nine-day *"considered to be eastern"* floor | **paraphrase-misleading** — corrected |
| 5 | 690 | Saturn/Jupiter *"burned to 6 deg, under the rays to 15 deg (… On Nativities 1.22, 1 and 6)"* | ¶1 `:1117`: *"if there were 6° … they are considered to be eastern … but if they were less than that, they will not be fit"*; ¶6 `:1137`: *"the power of easternization … is when 15° have passed them"*. The 15 is Sahl's; the 6 is not a burn orb | **paraphrase-misleading** — corrected |
| 6 | 692 | Mars *"burned to 10 deg, under the rays to 18 deg east (… 1.22, 3 and 6)"* | ¶3: *"he does not easternize until there are 18° between him and the Sun"*; no 10 anywhere in 1.22; Mars west = 18 in the table | **paraphrase-misleading** — corrected |
| 7 | 694 | Venus/Mercury *"12 deg east, 15 deg west (… On Nativities 1.22, 7-8)"* | ¶7–8 `:1139`: *"there are 12° between them and the Sun … if there were 15° between them and the Sun, they will have gone out of the rays"* ✓; the "burned to 7" is VII.2's and the following lines say so | paraphrase-fair — wording adjusted |
| 8 | 730–732 | 1.19, 6 quoted; 1.22 covers only the five planets | `:953` ✓ (elision marked); 1.22, 1–8 name only ♄♃♂♀☿ | supported |
| 9 | 735 | seven-day setting allowance at 1.22, 2–4 | ¶2 *"not considered western until there are 22°"*; ¶4 *"enter under the rays on the seventh day"*; fn. 173, 175 | supported |
| 10 | 740 | Mars's 22 *"is his figure from Sahl's On Nativities 1.22 table"* | table: ♂ *considered western* 22° | supported |
| 11 | 759 | docstring: solar phase per VII.2 and 1.22 | — | supported |
| 12 | 873 | 1.23, 17: gender not sect; Mars male, no exception | ¶17 *"if the planet was male … and if it was feminine"*; no Mars clause; fn. 196 contrasts later sect-based texts | supported |
| 13 | 958 | comment header | — | supported |
| 14 | 3503 | 1.22, 9's own footnote cross-references Aphorism #44 | fn. 176 `:1165`: *"This sentence represents Sahl's Aphorism #44"* | supported |
| 15 | 3508 | stakes twice (Aph. #44, 88; 1.22, 9) | ¶9 `:1157` ✓ | supported |
| 16 | 3509–3513 | 1.18, 19 quoted, incl. *"AND LIKEWISE IN ALL OF THE HOUSES"* and Dykes *"This is Ptolemy's 5-degree rule"* | `:899` ✓; fn. 139 `:919`: *"This is Ptolemy's 5° rule in Tet. III.10"* | supported |
| 17 | 3533 | as 15 | — | supported |
| 18 | 3536 | as 16 | — | supported |
| 19 | 3833 | no Lot of Basis anywhere, incl. *On Nativities* | `grep -i "lot of basis"` over all 15 corpus files: no hit; the whole book was read | supported |
| 20 | 3876 | Sahl gives many Lots more than once with conflicting formulas | `01_on_nativities.md` §7 | supported |
| 21 | 3927–3931 | Fortune: *"The Ascendant of the Moon"* (1.37, 1); Sun→Moon reversed is fn. 494 on 1.37, 3; ¶2 is hour-based | `:2712` ✓; fn. 494 `:2724` ✓ | supported |
| 22 | 3934 | Spirit named at 11.2, 4–6 | 11.2, 5 `:12717`: *"the Lot of Spirituality"* ✓ | supported |
| a | 3937 | *"notes on Ch. 9.5, 73 and Ch. 11.1, 5 confirm the identity"*; formula nowhere in corpus | 9.5 fn. 121 `:12568` ✓; the second is **Ch. 11 preamble ¶5** fn. 9 `:12592` (11.1, 5 is *"a friend to sheikhs"*). Formula: no corpus file has one; 1.37, 3 comes closest | **passage-not-found** (preamble) — corrected |
| 23 | 3949–3952 | 4.1, 6 quoted | `:5129` ✓ | supported |
| 24 | 3955–3958 | 2.15, 1 quoted | `:4026` ✓ (*"and you add"* → *"and add"*) | supported |
| 25 | 3961–3964 | 2.15, 17 quoted | `:4060` ✓ | supported |
| 26 | 3967–3970 | 3.11, 2 and 3.11, 4 quoted | `:4931` ✓ | supported |
| 27 | 3973 | 3.11, 3 *"Taken by night and day"* | `:4931` ✓ | supported |
| b | 3975 | *"The note on Ch. 3.1.2, 1 adds that in Dorotheus this one is … for the NUMBER of siblings"* | **No Ch. 3.1.2 exists.** The note is fn. 121 on 3.11, 3 `:4945`: *"This is in fact Dorotheus's Lot of the number of siblings"* | **passage-not-found** — corrected |
| 28 | 3979 | 4.14, 1 quoted | `:5927` ✓ | supported |
| 29 | 3984 | 4.14, 2 quoted | `:5927` ✓ | supported |
| 30 | 3991 | 4.14 fn. 198 quoted | `:6021` ✓ verbatim | supported |
| 31 | 3997–4000 | 5.1, 91 *"by night and by day"*; fn. 51 attributes to Theophilus | `:6764`, `:6778` ✓ | supported |
| 32 | 4003–4006 | fn. 51 *"the usual calculation … is that of Hermes"* | `:6778` ✓ | supported |
| 33 | 4010–4013 | 5.1, 92 Mercury→Saturn "Hermes" | `:6764` ✓ | supported |
| 34 | 4017 | *"Ch. 5.2, 2 and 8"* for the Mars→Jupiter timing Lot | 5.2 is *On sterility*; ¶2 there is *"look at the sign in which the Lot of children is"*, ¶8 *"Venus was opposing Saturn"*. The Lot is **5.3, 2** `:6875` and **5.3, 8** `:6883` (heading `:6868`) | **passage-not-found** — corrected |
| 35 | 4023 | Men's marriage: *"7.1, 223 and Ch. 7.4, 44"* | 7.1, 223 `:9315` ✓; **7.4 has 19 sentences**. The second statement is **7.2, 44** `:9475` | **passage-not-found** — corrected |
| 36 | 4027 | Women's marriage, same locators | 7.1, 224 ✓; 7.2, 44 | **passage-not-found** — corrected |
| 37 | 4031–4034 | 7.1, 141 + fn. 11 quoted | `:9105`; fn. 11 on 7.1, 9 `:8699` ✓ | supported |
| 38 | 4038–4040 | 6.3.4, 2 and 6.3.5, 1 quoted | `:8018`, `:8074` ✓ | supported |
| 39 | 4043–4045 | 6.10, 20 quoted | `:8615` ✓ (fn. 281: "and" read for "or") | supported |
| 40 | 4048–4051 | 8.6, 1 *"cast out from Saturn"*, "not the Ascendant" | `:10730` ✓ — **but** fn. 89: *"Reading with the Māshā'allāh MSS for 'Ascendant'"*: Saturn is Dykes's emendation; Sahl's MSS say Ascendant | paraphrase-fair (emendation not stated) |
| 41 | 4054–4057 | 8.2, 17 quoted | `:10406` ✓ | supported |
| 42 | 4060–4062 | Travel: *"Ch. 9.1, 9"*, quote | 9.1, 9 `:10850` is *"the Moon and her lord in the stake of the west"*. The quote is the **Ch. 9 preamble ¶9** `:10812` (also 9.3, 4; 9.4, 37) | **passage-not-found** — corrected |
| 43 | 4065–4068 | 10.1.1, 14; Fig. 63 names | `:11462`; Fig. 63 `:12189–12196` ✓ | supported |
| 44 | 4071–4075 | 10.2.5, 1 *"BY DAY AND NIGHT"*; Abū Ma'shar agrees; Dykes prefers Paul | `:12187`; fn. 165 `:12198` ✓ | supported |
| 45 | 4079 | fn. 165 | ✓ | supported |
| 46 | 4084 | 10.2.5, 4–14 is Māshā'allāh | fn. 166 `:12214` ✓ | supported |
| c | 4088–4089 | *"Fig. 63's glyph column reads Sun-Mercury, but the prose is followed here"* | Fig. 63 in the current OCR `:12194`: **☉→♄, ASC (R)**. It reads Sun-Saturn and marks night reversal; 4.14, 1 reverses the father Lot. The row has `reverse_at_night=False` | **unsupported** — note corrected; reversal left as a ⟨CHOICE⟩ (§5) |
| 47 | 4092 | Friends: *"Ch. 11.1, 5"* | Ch. 11 **preamble** ¶5 `:12574`, where *"<from the Moon to Mercury>"* is in Dykes's angle brackets (fn. 7); Sahl's own formula is **11.1, 29** `:12644` | **passage-not-found** — corrected |
| d | 4094 | *"The note on Ch. 10.2.9 identifies it: 'the Moon-Mercury Lot …'"* | **No Ch. 10.2.9 exists** (10.2 ends at 10.2.7). The quote is fn. 72 on **9.5, 3** `:11154` ✓ verbatim | **passage-not-found** — corrected |
| 48 | 4099 | Desire: *"Ch. 11.4, 5"* | **11.2, 4–5** `:12717` ✓ quote | **passage-not-found** — corrected |
| 49 | 4105 | Necessity: *"Ch. 11.5 (Dykes' note 62)"* | **No Ch. 11.5**; four subchapters (`:12598`, `:12713`, `:12743`, `:12811`; printed contents `sahl_frontmatter_reference.md:424–430`). fn. 62 is on **11.4, 18** `:12904` ✓ quote | **passage-not-found** — corrected |
| 50 | 4111–4114 | 12.1, 48, Fig. 71, fn. 15 quoted | `:13029–13039` ✓ verbatim | supported |
| 51 | 4119–4122 | 12.1, 49 = Lot of slaves per Fig. 71 | Fig. 71 row E ✓ | supported |
| 52 | 4131–4135 | 10.3 fn. 214 quoted | `:12486` ✓ | supported |
| 53 | 4139 | 7.1, 220 | `:13313` ✓ | supported |
| 54 | 4143 | 7.1, 221 | ✓ | supported |
| 55 | 4285 | Dykes's note on 10.3 (advancing) | fn. 231 `:12546` | supported |
| 56 | 4290–4293 | 1.20–1.23 releaser/house-master; 1.20, 2 ranking quoted | `:969` ✓ verbatim | supported |
| 57 | 4294–4297 | 1.18, 20–22 rates quoted | `:903` (¶21) ✓ verbatim | supported |
| 58 | 4298–4300 | 2.13, 48–51 three 15° ascensional bands; Aph. #45 misstated per note 57 | `:3939–3959` ✓; *Aphorisms* fn. 57 `fifty_aphorisms.md:264`: *"repeated correctly in Sahl's Nativities Ch. 2.13, 48-51, but is misstated here"* ✓ | supported |
| 59 | 4301 | 2.2 thirty fixed stars, Sahl's epoch | `:2995ff` table ✓ | supported |
| 60 | 4303 | 2.6 and 4.9 twelfth-parts | `:3620`, `:5802` ✓ | supported |
| 61 | 4305 | further Lots: 1.34, 13 (p. 358, "foundation" uncertain) | `:2453`, p. 358 marker `:2441`; fn. 436 *"sounds like the fourth place from the Sun, but is perhaps 0° Leo"* ✓ | supported |
| e | 4306 | *"male/female (3.12, 20)"* | 3.12, 20 `:5003` is the Lot of siblings in the twelfth. The male/female Lot is **3.13, 20** `:5075` | **passage-not-found** — corrected |
| — | 4306–4308 | Venus→7th (7.1, 10 and 145); Sun→Moon from Venus (7.4, 8); religion (9.5, 3); riding animals (12.2 fn. 18) | `:8681`, `:9111`; `:9739`; `:11154`; `:13471` ✓ | supported (part of row 61) |
| 62 | 4342 | 1.22, 9 | ✓ | supported |
| 63 | 4449–4451 | 10.3 fn. 231 quoted | `:12546` ✓ verbatim | supported |
| 64 | 4817 | 1.22, 9 | ✓ | supported |
| 65 | 4915–4918 | 1.22, 1 quoted; *"Mars at 15 degrees (1.22, 3 and its note)"* | `:1117` ✓ verbatim; fn. 174 ✓ | supported |
| 66 | 4930–4933 | 6° is the nine-day *"considered to be eastern"* allowance; Mars's 15 is Dykes's inference at fn. 174 | ¶1 *"in up to nine days"*; fn. 174 *"I think it is safe to say that he is considered eastern at 15°"* ✓ | supported |
| 67 | 4935 | label text | ✓ | supported |
| 68 | 5111 | 12° orb for Head **or Tail** from Ch.3, 107 and 1.21, 12 | 1.21, 12 `:1046`: *"if it was with the Tail, being distant from it by 12°"* — **Tail only**; ¶11 (Head) states no orb | paraphrase-fair |
| 69 | 5550 | 1.22, 9 quoted | ✓ | supported |
| 70 | 5832 | 2.6 states no twelfth-part formula | ✓ (none in 2.6, 4.9, or anywhere) | supported |
| 71 | 6375 | 2.13, 48–51 | ✓ | supported |
| 72 | 6949 | 1.19, 6 = 15° | ✓ | supported |
| 73 | 7010 | entering rule repeated at 1.22, 9 | ¶9 second half ✓ | supported |
| 74 | 7047 | 1.23, 17 hemisphere | ✓ | supported |
| 75 | 7065 | as 74 | ✓ | supported |
| 76 | 7109 | Sources page: *"which Sahl gives independently in On Nativities 1.22 and al-Biruni corroborates: burned to 6° … 10° … 7° …; under the rays to 15°, 18° east / 15° west …"* | same as rows 4–6: no burn boundary in Sahl; Mars west 18 | **paraphrase-misleading** — corrected (displayed text) |
| 77 | 7119 | 1.23, 17 paraphrase | ✓ | supported |
| 78 | 7220 | stakes twice | ✓ | supported |
| 79 | 7221 | 1.18, 19 all houses | ✓ | supported |
| 80 | 7226 | five-degree rule, both statements | ✓ | supported |
| 81 | 7310 | Topical Lots header | ✓ | supported |
| 82 | 7312 | *'the second place'* (2.15, 1) | ✓ | supported |
| f | 7313 | *'the degree of the eighth place', 'the ninth' (… 8.6, 1; 9.1, 9)* | 8.6, 1 ✓; *"to the ninth"* is Ch. 9 preamble ¶9 | **passage-not-found** — corrected |
| 83 | 7410 | stakes twice | ✓ | supported |
| 84 | 7411 | 1.18, 19 quoted | ✓ | supported |
| 85 | 7419 | 1.19, 6 | ✓ | supported |
| 86 | 7425 | 1.23, 17 paraphrase | ✓ | supported |
| 87 | 7430 | 2.15, 1 | ✓ | supported |
| g | 7431 | 9.1, 9 | preamble | **passage-not-found** — corrected |
| h | 3917 | comment on `LOT_HOUSE_CUSP_OPTIONS`: *"(2.15, 1; 8.6, 1; 9.1, 9)"* — a line without the word "Nativities", found by the edit script's occurrence count; same line: *"Dykes' note 207 on 4.14 glosses the assets Lot as 'from the lord of the second to the second'"* | preamble ✗; fn. 207 `:6067` (on 4.14, 41) ✓ *"the Lot of assets or money is taken from the lord of the second to the second"* | **passage-not-found** (the 9.1, 9 part) — corrected; the note-207 part supported |
| i | 3912–3914 | *"Fig. 63's row for Ch. 10.2.5 renders as 'Mercury -> Venus' where the body text at 10.2.5, 1 plainly reads 'from Saturn to the Moon'"* | Fig. 63 in the current OCR `:12193`: **♄→☽, ASC (R)** — the table agrees with the prose on the bodies; it differs only in marking night reversal, which the prose (*"by day and night"*) does not have | **unsupported** — corrected |

## 4. What could not be verified

- **Figure 63 as an image.** Only the OCR table was read (`:12189–12196`). If the printed figure's
  glyph column really does read Sun–Mercury, the code's earlier note was reporting the page and the
  OCR has since corrected it; either way the *current text* reads ☉→♄, and the note now says so.
- **al-Bīrūnī §481–82** (`:685`, `:7109`): not in the corpus. Dykes's statement that it agrees is
  taken from his comment; not checked.
- **TNAC Handy Tables Lesson 18** (`:3934`, the Spirit formula): outside this pass.
- **Reference Guide pp. 16–39** (`:552`): verified visually in the prose-tables pass, not re-opened.
- **Chapter 6.3.2's aphorisms** are, in Dykes's words, *"particularly atrocious"* and *"largely lack
  astrological context"*; nothing in `app.py` cites them, which is correct.

## 5. Findings that are the owner's, not this pass's ⟨CHOICE⟩

1. **`work_authority` reversal.** The text gives no formula for Māshā'allāh's Lot; Dykes's fn. 166
   says it is *"the same way as the Lot of fathers (Sun-Saturn)"*, Fig. 63 marks it **(R)**, and
   the father Lot (4.14, 1) reverses at night. `LOT_DEFINITIONS['work_authority']` has
   `reverse_at_night=False`. Not changed (a value); recorded.
2. **Lot of death from Saturn.** `:4050` presents the Saturn projection as Sahl's; fn. 89 makes it
   an emendation from the Māshā'allāh MSS and *Carmen* IV.3, 16. The engine follows the edited
   text, which is defensible; the note could say "per Dykes's emendation".
3. **Mars 15° west.** Was already Abū Ma'shar's choice; the comment now stops claiming Sahl agrees.
4. **Head's 12° orb** (`:5111`) rests on *Introduction* Ch. 3, 107, not on 1.21, 12, which gives 12°
   for the Tail only.
5. **The Māshā'allāh house tables' operating condition** — *"work this topic if the [house] and its
   lord are free of the infortunes and the fortunes do not testify"* (2.14 fn./6.3.4, 24/7.1, 217/
   9.4, 35/10.2.4, 13/11.1, 28/12.1, 47) — is not carried by `PLANETS_IN_HOUSES` /
   `MASHAALLAH_LORDS`. A doctrine matter, out of scope here.

## 6. Corrections applied (citation text only)

| Baseline line | Before | After |
|---|---|---|
| 684–695 | *"Sahl gives the same breakpoints independently … burned to 6 deg … (VII.2, 11-13; On Nativities 1.22, 1 and 6)"* etc. | Sahl credited with the under-the-rays figures only; states he gives no burn boundary and that his Mars westernizes at 18; each row now reads "the 15/18/12-15 also On Nativities …" |
| 3937 | `Ch. 11.1, 5 confirm the identity` | `Ch. 11, 5 -- the chapter preamble -- confirm the identity` |
| 3975 | `The note on Ch. 3.1.2, 1 adds` | `Dykes' note 121 on Ch. 3.11, 3 adds` |
| 4017 | `Ch. 5.2, 2 and 8` | `Ch. 5.3, 2 and 8` |
| 4023, 4027 | `Ch. 7.4, 44` | `Ch. 7.2, 44` |
| 4060 | `Ch. 9.1, 9` | `Ch. 9, 9 (the chapter preamble; restated at 9.3, 4 and 9.4, 37)` |
| 4088–4089 | `Fig. 63's glyph column reads Sun-Mercury, but the prose is followed here` | Fig. 63 in the current OCR reads Sun-Saturn, marked (R); this row does not reverse — open CHOICE |
| 4092 | `Ch. 11.1, 5` | `Ch. 11, 5 (the chapter preamble) and Ch. 11.1, 29` |
| 4094 (+1 line) | `The note on Ch. 10.2.9 identifies it` | `Dykes' note 72 on Ch. 9.5, 3 identifies it`; adds that the preamble's Moon-to-Mercury words are Dykes's bracketed supplement and 11.1, 29 is Sahl's own |
| 4099 | `Ch. 11.4, 5` | `Ch. 11.2, 4-5` |
| 4105 | `Ch. 11.5 (Dykes' note 62)` | `Ch. 11.4, 18 (Dykes' note 62)` |
| 4306 | `male/female (3.12, 20)` | `male/female (3.13, 20)` |
| 7108–7109 (displayed) | *"which Sahl gives independently in On Nativities 1.22 and al-Biruni corroborates: burned to …"* | *"Sahl's On Nativities 1.22 and al-Biruni give the under-the-rays figures independently (Sahl states no burn boundary, and his Mars westernizes at 18°, not 15°): burned to …"* |
| 3917, 7313, 7431 (one comment, two displayed strings) | `8.6, 1; 9.1, 9)` | `8.6, 1; Ch. 9, 9)` |
| 3912–3914 | *"Fig. 63's row for Ch. 10.2.5 renders as 'Mercury -> Venus' where the body text … reads 'from Saturn to the Moon'"* | the current OCR's Fig. 63 reads ♄→☽ (R); it agrees with the prose on the bodies and differs only on night reversal |

**What moves for users:** two strings on the Sources page and the Lots-page help text (rows 76,
f, g), plus the Standing/Source column of five rows in the Topical Lots table. No number changes.

## 7. The pin — `tests/test_nativities_citations.py`

What can be held mechanically is the **chapter number**: every `On Nativities Ch. X.Y` in `app.py`,
and every `Ch. X.Y` inside a `LOT_DEFINITIONS` row whose source is Sahl, must name a heading that
exists. The list of 173 headings (12 chapter-level, 161 sub-level) is vendored so the test runs in
CI; with the corpus on disk a third test re-derives the list from the file and fails if the two
drift.

On the baseline the pin fails with exactly the non-existent chapters this audit found —
`('friends', '10.2.9')`, `('necessity', '11.5')`, `('siblings_valens', '3.1.2')` — and passes after
the corrections. It would **not** have caught the wrong-but-existing chapters (5.2, 7.4, 11.4, 3.12,
9.1, 11.1): paragraph numbers cannot be pinned from this OCR (bold markers, LaTeX degree signs and
footnote superscripts make a bare "44" ambiguous), and a locator test that works for a third of
cases is worse than none. Those six are the class only a re-read finds — which is what this pass
was.
