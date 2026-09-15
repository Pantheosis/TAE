# Phase 2 — reconciliation of the *Persian Nativities* I–III and ITA passes against `app.py`

Four Phase-1 artifacts, one document. Every doctrine they raise, classified against what the code
does and claims, deduplicated, with the owner's decisions pulled out at the end.

Inputs: `01_persian_nativities_iii.md` (PN III, the Latin *On Rev. Nat.*; 27 differences against
PN IV), `01_persian_nativities_i.md` (BA + JN; 46 doctrines), `01_persian_nativities_ii.md`
(TBN + Abū Bakr; 25 doctrines), `01_ita_rulings_audit.md` (63 entries with verdicts; §C, §D).
`app.py` at **origin/main, 16,443 lines, HEAD `bd7e370`** — line numbers below are from that file,
not from the artifacts (which cite the synthesis branch). Open PRs #21 (Andarzaghar table), #22
(Rhetorius affliction), #23 (victor-weights note) read by `gh pr diff`. Rulings in the corpus repo's
`process/astra_2026-09-11/*_ruling.md` and `process/OWNER_RULING_PLACES_VS_DYNAMICS_2026-09-11.md`.

Classes as `02_reconciliation.md`: 1 newly available · 2 contradicts an implementation · 3 contradicts
a claim (user-facing) · 4 confirms · 5 still absent.

**Text status of the witnesses.** PN III is the Kindle text layer (no OCR; clean). PN I, PN II and
ITA are **unread OCR** — every quotation from them is (OCR, unverified) unless it falls on one of ITA's
32 photographed pages (71–76, 112–123, 206–208, 213–216, 224–229, 395) or on ITA p. 332, which the
owner has now read on the page. Nothing from PN I or PN II may be quoted on a page until the marker
OCR supersedes the embedded one.

---

## Class 3 — Contradicts a current claim (user-facing)

Seventeen items. Two are already fixed on open PRs; fifteen remain. The first five are false or
stale statements; 3.6–3.17 are places where a page or comment says "this app's" or "no text" and a
text in hand says it.

### 3.1 ⚠ `PN4_ASCENSION_RULE`: "the formula stated in no text in hand" — it is stated, by al-Qabīsī

`app.py:8742–8752` (`PN4_SEMIARCS_UNAVAILABLE`, the 'anything else' string) and `:10536` (the turning
direction's refusal): *"Ptolemy's as Dykes identifies it (III.1, 12 fn 16; VI.2, 21 fn 33), the formula
stated in no text in hand."* Also the Releaser tab, `:15821`: "the proportional semi-arcs, is not built".

**Against it:** ITA VIII.2.2b–e, al-Qabīsī IV.11c–12c, pp. 362–364 — the "hours of the distance from
the angle", the significator of the right circle (RA), of the region (OA), "one-sixth of [the
difference] … multiply it by the hours of the distance from the angle: … the 'equation'" (OCR,
unverified); ITA Appendix E, pp. 402–407, the formula PromMD − [(SigMD/SigSA) × PromSA], worked with
and without latitude, "Al-Qabīsī's method is essentially the same as this" (OCR, unverified). ITA
entry 21.

**Fix:** the third string → "stated by al-Qabīsī (ITA VIII.2.2) and worked by Dykes (Appendix E)";
GAP-37 (f) is no longer an outside-corpus import. Building it is decision 5. **Remains.**

### 3.2 Victors page and `VICTOR_WEIGHTS`: the "older" label's witnesses — FIXED on #23

PN II §7.1 and ITA entry 25 together. The one corpus passage giving 'Umar weights, Abū Bakr II.5.14
(PDF p. 248, OCR, unverified), has triplicity 3 / bound 2 — the "newer" order; the bound-first order
is al-Qabīsī I.22 (ITA p. 81) "certain people put the bound before the triplicity" (OCR, unverified),
unattributed. PR #23 (`VICTOR_WEIGHTS` comment at `:8337`; the Victors page paragraph) now says
exactly that and keeps the course's label by the owner's ruling of 2026-09-15. **Nothing remains.**

### 3.3 Kollēsis across a sign boundary — FIXED on #22

ITA entry 31: Dykes, ITA III.7 comment, p. 136, "the Arabic, unlike the Greek, does not distinguish
connections within the same sign (kollēsis) from those in different signs (sunaphē)" (OCR, unverified).
PR #22 commit `76db959` confines kollēsis to the same sign, cites p. 136 on the row, and pins it
(`test_kollesis_is_the_same_sign_connection`). **Nothing remains.**

### 3.4 ⚠ `docs/COURSE_COVERAGE_2026-09-14.md` is stale in its header and in gap 10

- Header of "Gaps whose only witness in hand is the Handy Tables": *"Source texts not in the corpus
  (Morin, Antiochus, Firmicus, Rhetorius, Ptolemy's Tetrabiblos, al-Qabisi/ITA, Lehman)."* ITA is in
  the corpus (`ita/`, 32 photographed pages and a provisional OCR) and three of the list's gaps are
  built from it or from the course since: gap 1 (eyesight, merged #20, `EYESIGHT_PLACES` `:6209`),
  gap 7 (Morin, merged #18, `:6093`), gap 9 (Andarzaghar, open #21), gap 10's Mercury half
  (`8f96202`, `:1644`), gap 2 (the Lots of Jupiter and Saturn, `:5388`, `:5398`).
- Gap 10: *"the per-planet of/contrary-to-sect delineations of Lesson 10 (Rhetorius, Abu Bakr)"* under
  "only witness … Handy Tables". PN II §7.2: Abū Bakr II.1.0 (PDF p. 168, OCR, unverified) is a corpus
  witness for the Mars row — Mars in his domicile by night "a good soldier", by day "lazy in those
  things in which he ought to make money" — with the condition **in his domicile, by sect of chart**,
  not "contrary to sect" at large.

**Fix:** rewrite the header; move the Mars row to "gaps with a corpus text behind them"; mark gaps
1, 2, 7, 9, 10 as built. **Remains.**

### 3.5 Releaser tab caption (5): "no text says" what the fullness's degree is when neither luminary is above the earth

`app.py:15728`: *"when both or neither is above the earth the app takes the Moon's degree; no text
says."* ITA VIII.1.2, al-Qabīsī IV.3, p. 352: Ptolemy — "the degree of the luminary which was above the
earth"; "certain ones of the sages" — one on the eastern degree and the other on the western, "the
degree of the east is the degree of the prevention"; Valens — "the degree in which the fullness is —
wanting the degree of the Moon" (OCR, unverified). ITA entry 47.

**Fix:** replace "no text says" with the three opinions; the Moon default is Valens's. Whether the
sages' tie rule is adopted is decision 7. **Remains.**

### 3.6 The years table presents 39½ without its three dissenters

`app.py:8519–8529` (the `PLANETARY_YEARS` comment: "must not be 'corrected' … established by an
independent source reconstruction, 2026-09-09") and the Reference page's years table. The number is
Class 2.1; the *claim* is that the matter is closed. Against it: BA III.1.8 (pdf p. 105) and JN Ch. 4
(pdf p. 279), Sun 69½ / Moon 66½ (OCR, unverified — but the arithmetic (120+19)/2, (108+25)/2 is
exact in both); ITA VII.2, the Latin *Gr. Intr.* Figure 108, p. 332, Sun "69½", Moon "66½" — **read on
the page by the owner; the OCR is correct.** PN I #1, ITA entry 9.

**Fix:** a note on the Reference page's table naming the three ordinary-mean witnesses beside the
three for 39½ (§6 row 1). The value is decision 1. **Remains.**

### 3.7 "This app's convention for strength language" is Dykes's published proposal

`app.py:14985` and `:15391` ("this app's convention"); `:15710` cites Lesson 3 and the Course Glossary.
ITA Introduction §6, pp. 15–20: the four ambiguous concepts and Dykes's "possible solution" — "(1)
adopt whole signs for topics; … (3) apply Nechepso's eight-place scheme to quadrant-based dynamical
divisions" (OCR, unverified); p. 16 "al-Qabīsī definitely uses quadrant houses"; VIII.1.3 fn 17 "such as
Porphyry or Alchabitius Semi-Arc". ITA entries 19, 40, 46. The ruling already attributes the dispatch
to "the translator's course convention" (OWNER_RULING addendum §1); ITA is the translator's own book
for it.

**Fix:** cite ITA Introduction §6 beside Lesson 3; keep Alchabitius as the app's choice among quadrant
systems (no text names it). **Remains.**

### 3.8 Morin's unfortunate houses: "the 6th, 8th and 12th are this app's reading"

`app.py:6099`. ITA IV.4.1, al-Qabīsī III.28c + fn 43, p. 224 (**photographed**): "cadent from the
Ascendant. That is, being in aversion to it … particularly the twelfth, eighth, and sixth; the second
sign is also cadent from the Ascendant but is not considered as difficult". ITA entry 34.

**Fix:** cite fn 43 as the parallel; keep "the app's" for the equation with Morin's phrase. **Remains.**

### 3.9 Valens's Moon phases: the 12° boundaries called "this app's"

`app.py:14442` ("Eight of his boundaries are degrees he gives; the rest are this app's"). ITA II.10.5,
Abbr. II.27–31, p. 108: the Moon's eight properties — the conjunction, "if she receded from him by 12°",
90°, "distant from the opposite of the Sun by 12°", the opposition, "if she would add 12° on top of the
opposite", 90°, "distant from the Sun by 12°" (OCR, unverified). ITA entry 32: three of the four
boundaries the page calls its own are Abū Ma'shar's; his fourth (12° before the opposition) is not used.

**Fix:** the note says the 12° markers are Abū Ma'shar's applied to Valens's phases, and names the one
not used. **Remains.**

### 3.10 PR #21: the triplicity lords' sect order called "this app's reading"

PR #21's docstring, comment and page text: "this app's reading of 'first, second, third'". ITA I.7,
Abbr. I.86, pp. 46–47: "the diurnal judge of these is the Sun and [then] Jupiter, but the nocturnal one
Jupiter and [then] the Sun"; al-Qabīsī I.16b–e the same (OCR, unverified). ITA entry 29 — al-Qabīsī is
the author of the Andarzaghar report, so his own table settles his own word. (#21's blind check
attests the order at *Gr. Intr.* V.14, 6 and Sahl 10.2.7, 16 too.)

**Fix:** on #21 before merge, or after: cite I.7 / I.16 and drop "the app's reading". **Remains.**

### 3.11 The weighted almuten "a technique from outside these texts; the weights are stated in no text in hand"

`app.py:14960` (the syzygy table's Almuten row), `:14992–14993` (the Victors page). ITA I.18,
al-Qabīsī I.22, p. 81: "the Lord of a domicile has five strengths, and the Lord of the exaltation
four, and the Lord of the triplicity three, and the Lord of the bound two, and the Lord of the face
one"; I.77 the victor of a topic; VIII.1.4, al-Qabīsī IV.7, p. 357: the victor over the native from
the Ascendant, the luminaries, Fortune and the syzygy (OCR, unverified); fn 210 "only the primary
triplicity Lord receives points" — which is what `evaluate_victors` (`:8355`) does. ITA entries 26, 61.
Ibn Ezra's worksheet rows (Day, Hour, Places) remain outside.

**Fix:** "the weights and the five places al-Qabīsī's (I.22, IV.7); the worksheet ibn Ezra's"; quote
fn 211 (with Dorothean triplicities and Egyptian bounds "the victor will always be either the
domicile or exalted Lord … but for a few degrees of Pisces and of Cancer") as the standing critique.
Decision 6. **Remains.**

### 3.12 `get_effective_house`'s five degrees "in ecliptic longitude, by choice"

`app.py:4541` docstring. ITA VIII.1.3, al-Qabīsī IV.4, p. 355: "by five equal degrees and less" (OCR,
unverified) — "equal degrees" being *Gr. Intr.*'s term for ecliptic measure (VI.1.1 fn 2, p. 281).
ITA entry 18. **Fix:** cite al-Qabīsī's "equal degrees" as a text's own unit. **Remains.**

### 3.13 The 15° Libra–15° Scorpio burnt path cited to the Course Glossary

`app.py:5630–5634` and `:8227` ("Dykes, Carmen p. 258 fn 104; the Course Glossary"). ITA IV.3,
al-Qabīsī III.29, p. 222: "the burnt path (which is the last half of Libra and the first half of
Scorpio)" (OCR, unverified). ITA entry 45. **Fix:** cite al-Qabīsī III.29 — a primary text in hand —
in place of the Course Glossary (the page-text rule forbids the course on pages anyway). **Remains.**

### 3.14 Mercury's sect as a morning star sourced to Firmicus's translator only

`app.py:1644` (Mathesis III.7, fnn 186, 194) and the hayz derivation `:1781`. ITA V.11, *Gr. Intr.*
IV.9.1312–38, pp. 276–277: "if [Mercury] is arising [before the Sun] he becomes diurnal, but when he
sets [after the Sun] he will be nocturnal" (OCR, unverified). ITA entry 33. And the contrary rule the app
must not import — BA II.11 "Mercury is made diurnal with diurnal stars and nocturnal with nocturnal
ones" (pdf pp. 71–73, OCR, unverified) — is called a corruption of Paul by Dykes twice (BA fn 50; ITA
fn 171). PN I #30. **Fix:** cite *Gr. Intr.* IV.9 on the finding and in the hayz comment. **Remains.**

### 3.15 The names "Basis", "Victory", "Nemesis" carry no source

`app.py:5130` (basis: "fn 67: the Greek Lot of Basis"), `:5388` and `:5398` (Jupiter "prosperity, aid,
victory", Saturn "the burdensome"). ITA VI.1.4 "The Lot of Basis", pp. 285–286 (Abbr. VI.7; *Gr.
Intr.* VIII.3.560–78 "this Lot matches the Lot of Venus"); VI.1.7 "The Lot of Victory or Jupiter";
VI.1.8 "The Lot of Nemesis or Saturn" (OCR, unverified). ITA entries 24, 37. **Fix:** cite the section
headings for the names. **Remains.**

### 3.16 The governor row's Moon note: "the texts name only right and left"

`app.py:4782–4783` ("Gr. Intr. VII.2, 4 names her right and left, not …"). ITA II.10.1, al-Qabīsī
III.8a, p. 98: the superiors from the rays to the opposition "are called 'eastern' and 'right'" (OCR,
unverified) — the bridge right = eastern, stated. ITA entry 4. **Fix:** cite III.8a. **Remains.**

### 3.17 The seven "good places" presented as the app's identification alone

`app.py:15729–15731` (caption (6): "no sentence defines 16's phrase, so the …"). ITA III.4 comment,
p. 121: Sahl "explicitly uses the seven-place arrangement of Timaeus and Dorotheus in his Introduct.
§4"; Introduction §6, p. 18: Dorotheus calls the seven "good" and "strong" (OCR, unverified). ITA
entry 2. **Fix:** cite pp. 18, 121 beside fn 372. **Remains.**

---

## Class 2 — Contradicts an implementation

Six items. Two are covered by existing rulings and stand; the rest are the owner's to make (§7).

### 2.1 ⚠ The luminaries' middle years, 39½ — three witnesses each way

**Code:** `PLANETARY_YEARS` `app.py:8530–8538` (Sun and Moon `'middle': 39.5`), consumed by
`sahl_house_master_years` `:9601` and `_sahl_1_20_grade` `:9533` (the middle-years cells of the 1.20
grid), and the Reference page's table.

**For 39½:** *Gr. Intr.* Figure 146 (VII.8, 3–8, the 2020 Arabic volume; rebuilt and pinned
2026-09-07); Abū Bakr I.16, PDF p. 159: "by the halving of their greater years and the addition of their
lesser years, and the halving of all of them assembled together" → 60 + 19 = 79, /2 = 39½ (OCR,
unverified; PN II §7.7); the course's Lesson 5 table. The app's comment adds Valens VII.5 and PN IV
I.8, 12 (the Moon's 39½ — Abū Ma'shar again, not independent).

**For the ordinary mean, 69½ / 66½:** BA III.1.8, pdf p. 105 (OCR, unverified; PN I #1); JN Ch. 4,
pdf p. 279 (OCR, unverified); the Latin *Gr. Intr.* Figure 108, ITA p. 332, **read on the page by the
owner.** Dykes calls 69½ "traditional" at PN II fn 625.

**The artifacts disagree with each other:** PN I #1 files it Class 2 "three-against-one"; PN II §7.7
files it Class 4 "do not reopen"; ITA entry 9 "CONTRADICTS the two cells". The tally is now even.
**No ruling covers it** (the 2026-09-09 settlement was a build decision, not an owner ruling). The
app keeps 39½ unless the owner rules otherwise — decision 1.

### 2.2 The five-degree rule at the four axial degrees only — a RULING; al-Qabīsī reads "any house"

**Code:** `get_effective_house` `:4541`, `FIVE_DEGREE_ALL_CUSPS = False` `:4540`, comment `:4530–4539`
("READ AS THE FOUR STAKES, the course's reading … The `five_degree_all_cusps` preference … retired").

**Against it:** ITA VIII.1.3, al-Qabīsī IV.4, p. 355: "every planet which was before the degree of the
Ascendant **or any house** by five equal degrees and less, its strength will be valid in the house
which follows it" (OCR, unverified) — stated inside the releaser procedure; ITA Introduction §6, p. 12,
gives the all-cusps form to Ptolemy. ITA entry 17. (BA I.4, pdf p. 61, is a weak extra witness for the
Ascendant only — Dykes fn 41 "unclear to what end"; PN I #33.)

**Ruling:** `OWNER_RULING_PLACES_VS_DYNAMICS_2026-09-11.md` lines 17–19 ("It never applies at the eight
intermediate cusps") and Addendum §2 ("'Likewise in all of the houses' (1.18, 19) read as the four
dynamic stakes only is the course's reading; say so"). **The ruling stands for Sahl's three
sentences**; what is new is a primary text of another author reading the phrase literally. Decision 2.

### 2.3 The Lot of friends reversed at night, confidence "settled"

**Code:** `LOT_DEFINITIONS` friends row `:5335–5342` (`reverse_at_night=True`, `confidence='settled'`,
source Sahl 11, 5 and 11.1, 29 with Dykes's note 72).

**Against the reversal:** ITA VI.2.45, p. 320 — Abbr. VI.53 and *Gr. Intr.* VIII.4.1464–69 "in the day
and night from the Moon to Mercury" (OCR, unverified). **For it:** al-Qabīsī V.14a "And al-Andarzaghar
said it is taken conversely in the night"; Dykes fn 104 "This should be reversed at night"; BA III.12.1
reversed (pdf p. 222, OCR, unverified; PN I #15); Sahl as the row reads him. ITA entry 52. **No
ruling.** Fix: the confidence string; the formula stays (three for, one against). §6 row 3; decision 4.

### 2.4 The enclosure breaker on PR #22: "a third body or ray between the two breaks either"

**Code (unmerged):** #22's `RHETORIUS_AFFLICTION_CONDITIONS` besieging row and its note ("A third body
or ray between the two breaks either, as the same passage says of a fortune's ray within seven
degrees").

**Against "any":** *Gr. Intr.* VII.6.1244–60 in ITA IV.4.2, p. 225 (**photographed**): the loosening is
"if the Sun or a certain one of the fortunes aspected the besieged planet by an aspect of friendship,
and there were less than 7° between"; al-Qabīsī III.28b "a fortune or the Sun … from a trine or
sextile aspect"; BA II.6, pdf pp. 68–69: the Sun's ray from any aspect within 4°–5° of the Moon
"shatters the siege" (OCR, unverified; PN I §3). Dykes's own generalisation, p. 228: "a benefic planet
will break … a malefic enclosure … a malefic planet will break … a benefic enclosure". "Any third
body or ray" is Rhetorius Ch. 41's construction alone. ITA entry 30.

**Ruling:** the owner had the malefic limit and the fortunes' row answered "from ITA IV.4.2 rather
than by ruling" (#22 body); the breaker was not asked. §6 row 4; decision 3.

### 2.5 The releaser's candidates classified by whole sign (the Lot included) — a RULING; al-Qabīsī uses quadrant houses

**Code:** `_sahl_examine_candidate` `:9337` (`unit='division'` for strength, places by whole sign),
the decision-sheet row 3 change (the Lot by whole-sign place).

**Against it:** ITA VIII.1.3, al-Qabīsī IV.4, p. 355: "you will look for the releaser in the angles
and in their followers according to how the twelve houses of the circle are calculated through the
degrees of the hours of the Ascendant" — fn 17 "Al-Qabīsī is telling us to use quadrant-style houses
… for this longevity method" — the conjunction, prevention and Fortune "fit … only … in these eight
places" so calculated (OCR, unverified). ITA entry 15.

**Ruling:** `REL-2-1_ruling.md` and `REL-2-1_phase2_ruling.md` (whole-sign base for Sahl 1.15;
decision-sheet row 3). **Stands**; a different author's procedure. Decision 17 (name him on the tab;
revisit row 3 or not).

### 2.6 Sahl's degrees of nobility (Figure 57) tested as the span N−1..N — a RULING; Dykes resolves the ordinal to a point

**Code:** the Figure 57 finding (PR #13, `0f1c310`: "read as ordinals, said so").

**Against the span:** ITA I.3 fn 23, p. 29: "widespread inconsistency between cardinal and ordinal
numbers … My sense is that the authors probably meant 'at the end of the nineteenth degree, namely at
19°'" (OCR, unverified); VII.9.2–3, Figures 116–118, pp. 347–349, printed as ordinals; and al-Qabīsī
I.53 (Figure 118) is a **third** table — Taurus "3rd, 15th, 27th", with Sahl's Taurus 3 against Abū
Ma'shar's 8th. ITA entry 36.

**Ruling:** the owner's on PR #13 (memory: "Figure 57's degrees read as ordinals, said so"). Stands;
decision 8 is whether the page adds Dykes's resolution and al-Qabīsī's table.

### Not Class 2, though an artifact says so

- **PN I #3** says the app "applies ±¼ with a 12° orb to both" nodes on the house-master's years. It
  does not: the Releaser tab (`:15829`) prints "Not applied: … the 1.21 additions", and no code
  adjusts `sahl_house_master_years` by a node. PN II §7.5 has it right (Class 5). The artifact is
  corrected here; the app is unchanged.
- **PN III item 22** (mighty days by ascensions) is Class 4 for what is built — the Arabic's
  arithmetic — with the Greek's variant to record (§6 row 5). Not a contradiction.
- **PN I #8**: Dykes, PN I Appendix B (5), pdf p. 387, calls Sahl 1.23, 2's direction of the
  house-master "apparently an error … the *jārbakhtār* is thus being conflated with the *kadukhudhāh*"
  (OCR, unverified). `sahl_house_master_direction` `:9926` implements Sahl as he states it and quotes
  him. An editorial verdict, not a text; the caption may carry it. Class 4.

---

## Class 1 — Newly available, buildable

Ranked by what each group unblocks. Size: small = one function and a row; medium = a subsystem
touching an existing page; large = a new page or a new procedure. Canon-only applies throughout: BA,
JN, TBN, Abū Bakr and al-Qabīsī are corpus, not course text, so every item here is a labelled
supplement row unless Sahl states the same rule (said where it does).

### Group A — al-Qabīsī's direction arithmetic (unblocks the most)

**A1. Proportional semi-arcs** — al-Qabīsī IV.11c–12c (ITA VIII.2.2b–e, pp. 362–364) and Dykes's
Appendix E (pp. 402–407) with its worked example as the fixture. **Medium.** Dependencies: none new —
`sahl_releaser_distribution` `:9910` already computes OA/RA from obliquity and latitude. **Unblocks:**
PN IV III.1, 12's third case in the three places that refuse it (`PN4_ASCENSION_RULE` `:8743`,
`PN4_TURNING_DIRECTION_REFUSED` `:10536`, the VI.2, 21 turning at `:10701`), GAP-37 (f), and the
distribution of every non-axial point. The readings it must declare are the two Appendix E works
(with and without latitude). ITA entry 21, §D2. Decision 5.

**A2. Al-Qabīsī's releaser and *kadukhudhāh* procedure whole** — ITA VIII.1.3, pp. 353–356: eleven
places per luminary with sign-gender gates, the Moon's rays, quadrant houses with 5° at every cusp,
three orderings of the lords, tie-breaks (own place, nearest degree, the Sun's relations), the
four-sign exception. **Large.** Dependencies: A1 for its directions; 2.2 for the 5° at every cusp. A
second longevity procedure beside Sahl's; the course teaches Sahl's. ITA §D1. Decision 16.

**A3. The nearest-degree tie-break for the governor** — al-Qabīsī IV.5, p. 356: equal claimants that
all aspect, "the one which was stronger in [its own] place"; equal there, "the one which was closer to
the degree of the releaser" (OCR, unverified). **Small** (a sentence in `SAHL_1_7_UNMODELLED` `:4786`
or a declared parallel). ITA entry 5; the 1.7 governor ruling covers the note. Decision 15.

**A4. The fullness's tie rule** — the "certain sages'" eastern degree (3.5). **Small.** Decision 7.

### Group B — the house-master's years (one machinery: `_sahl_1_20_grade` `:9533`)

**B1. JN Ch. 3's years ladder** (pdf pp. 408, 278; OCR, unverified) — angle → greater, succedent →
middle, cadent → lesser, each "own domicile/exaltation/triplicity, oriental, free from the bad ones,
retrogradation and burning"; not oriental → one grade down; occidental and peregrine → middle to
lesser; occidental, peregrine, retrograde, burned → "the lesser years and months … to days". **TBN
I.4.3's first block** (PDF p. 40) is the same ladder in 'Umar — oriental, angular, in *ḥayyiz*,
dignified → greater; oriental, dignified, succedent → middle; cadent → lesser; "with fall,
retrogradation, and peregrination, or descension" → hours by the lesser years (OCR, unverified). Two
witnesses; the app grades by Sahl 1.20's thirty-four sentences and prints "1.20 silent" where none
reaches the case (`:9644`; the docstring at `:9527–9530` puts the silent share at 18% of the 388 tested cells by whole sign). **Small**, as a labelled fallback for the silent cells
only. Dependencies: none — the grade's inputs (angularity, orientality, peregrinity, retrogradation,
burning) exist. **Do not merge Abū Bakr I.15's grid** (PDF pp. 154–155: dignified in the 4th, 5th or
11th → *lesser*; the 9th, 6th, 12th → months), which is a variant (PN II §7.6, the D-8 principle).
PN I #2, PN II §2. Decision 9.

**B2. Sahl 1.20, 14–15 read by TBN I.4.3 as a degree rule** — "peregrination and setting and
retrogradation or burning up does not harm the higher planets so much as it does the inferior planets.
But if the higher planets were impeded by a serious impediment, it signifies months or days according
to the number of its own lesser years" (PDF p. 40, OCR, unverified). Moves the `NOT_IMPLEMENTED_COVERAGE`
entry (`:5533` list, "14-15 unclear in sense (fn 156)") from "not applied" to rulable: one such
condition does not demote a superior; a "serious" one (undefined) gives the lesser years as months or
days. **Small** once "serious" is defined; a note otherwise. PN II §7.3. Decision 10.

**B3. Sahl 1.21, 14's condition** — TBN I.4.4, PDF p. 41: the Venus/Jupiter hope applies "if the
*kadukhudhāh* were burned up, and [therefore] it signified nothing" (OCR, unverified), the condition
Sahl fn 170 guessed. **Tiny**: carry it in the Releaser tab's printed note; the 1.23, 12 flag already
exists (`hm_redirect` `:13478`). PN II §7.4.

### Group C — the prosperity classifier (one machinery with the DELIN-TABLES order: whole-sign "lord of X in Y" lookups and condition reads)

**C1. The seven-fold frame's computable core** — BA III.2.0–III.2.6 (pdf pp. 117–135) in its original
order, JN Ch. 7's clean rules and twelve worked charts (pdf pp. 287–298), Abū Bakr II.2.0 (PDF
p. 193), and Sahl 2.1–2.21 — the course text — which states each rule and scrambles the frame. The
core: both sect triplicity lords angular / succedent / cadent; the Lot and its lord free and regarding
the Ascendant; the eleventh from the Lot (C2); the Moon's separation and application; the lords of
Asc/MC/11th as fallback. **Medium–large.** Dependencies: C2; the marker OCR of PN I before any BA/JN
sentence is quoted. The app has no prosperity classifier (Sahl 2.1–2.21 uncited beyond 2.2/2.3's
stars). PN I #22. Decision 11.

**C2. The eleventh from the Lot of Fortune** — BA III.2.1 `[1.7]` "strong like the eleventh from the
east" (fn 89: Valens II.21); JN Ch. 7, Ch. 11; Abū Bakr II.2.0 "the 11th from the Ascendant and the
11th from the Lot of Fortune" (all OCR, unverified). Zero occurrences in `app.py`. **Small**, a
whole-sign count. PN I #20.

**C3. The first-15° rule for the sect light's triplicity lord** — BA III.2.1 `[1.3]` "from the first
degree of the sign up to the fifteenth, wholly with the degrees of the arisings of the Sun, and it in a
pivot"; JN Ch. 7 "in the first 15° of the sign … the other degrees of the angle after the aforesaid 15
… as if in a succedent"; Abū Bakr II.2.2 "from the beginning of the sign … up to the middle"; TBN
III.1.1 [2] Dorotheus's three 15° bands "between the degree of the planet and the degree of the angle",
unit unstated (all OCR, unverified). The app has `SAHL_2_13_BANDS` `:9801` in ascensions from the
axial degree. The texts disagree on the measure (sign-start vs axial degree; zodiacal vs ascensional);
Dykes's Sahl fn 82–83 and the existing bands are the reading to follow. **Small** on top of `:9801`.
PN I #21, PN II §7.18.

**C4. The lords of the angles in the angles** — ITA I.15, al-Qabīsī I.73–76, pp. 77–79: sixteen cells
("The presence of the Lord of the Ascendant in the Ascendant signifies his fortune … through himself";
the lord of the tenth in the seventh, "victory in contentions and from the purposes of wives") and
I.14's house meanings by angularity (OCR, unverified). **Small**; 16 of the DELIN-TABLES order's 144
cells, from a text in hand. ITA entry 23, §D4.

**C5. JN Ch. 8 / BA III.2.4's time of fortune** — oriental and above the earth → the beginning of
life; the places by age (1st–2nd, 10th–11th, 7th–8th, 4th–5th); the Lot → the beginning, its lord →
the end; direct the Lot of Fortune to the bodies and rays of the fortunes and infortunes (pdf
pp. 300–301, OCR, unverified). **Medium**; timing-deferred. Depends on A1 for the Lot's direction off
the axes. PN I #23.

**C6. JN Ch. 50's weighting caution** — one testimony "routine", two stronger, three complete;
cadent/movable weak, succedent/common stronger, angles/fixed strongest; equal contraries "both should
be thrown out" (OCR, unverified). **Small**, two lines. PN I #41.

### Group D — timing variants (record; the canon rule keeps them off the pages unless ruled otherwise)

**D1. 'Umar's 30° profection at 12⅙ days per degree** — TBN II.4, II.5, II.6.2, II.8 (PDF pp. 55–70)
and al-Qabīsī IV.8 (ITA VIII.2.1, pp. 358–360; fn 30 "al-Qabīsī uses 30° increments in his profections
instead of whole-signs") (OCR, unverified). Two authors in hand; Dykes calls it 'Umar's departure from
Hellenistic practice (PN II Intro PDF p. 21). **Medium.** A named alternative to the monthly profection
for `16_open_features.md`. PN II §7.10, ITA entries 22, §D10. Decision 12.

**D2. The parents' points in the revolution at 59′ 08″ a day** — TBN II.5: the father's lesser
condition "the degree of the 4th house [in the revolution]", the mother's the Moon's degree, at the
same rate as the SR Ascendant (OCR, unverified). **Small** on top of `PN4_SMALL_DAYS_RATE` `:9042`.
PN II §7.11 rider.

**D3. Profection triggers by topic** — JN Ch. 26 and Abū Bakr II.9.18: the profection reaching the
seventh sign, **or the SR Ascendant being the 7th sign** → betrothal; movable many, common two, fixed
one (OCR, unverified). Sahl carries the marriage and children cases; the SR-Ascendant trigger is not
his. **Small.** PN I #42.

**D4. JN Ch. 1's first-year timing** — direct the Ascendant "by giving a month to each degree" in the
first year, years beyond (OCR, unverified). **Small.** PN I #43.

**D5. The parents' *hīlāj* chains** — JN Ch. 19 (father by day Sun → Saturn → Lot of the Father → the
4th's degree; mother Venus → Moon → Lot → MC; the aspecting lord of the five dignities as
*kadukhudhāh*); Chs. 17–18 the years comparison; Abū Bakr II.5.13 the same Dorothean chain (OCR,
unverified). Sahl 4.12 is JN's abbreviation; the app directs the Lot of the father, the Sun or Saturn
(Sahl 4.20, 31–32). **Medium.** PN I #44, PN II §7.13.

**D6. BA IV.16's weekly/daily/hourly rulers** — seven-day cycles from the lord of the Ascendant in
descending order (Da. 189; Carmen IV.1.57) (OCR, unverified). A different scheme from the planetary
week the app uses. **Small**; a note. PN I #37.

**D7. BA IV.8's four-way rule** and the *jārbakhtār*–*sālkhudhāy* tiebreak "the stronger and luckier
place of whichever one under the natal root" (Da. 178) (OCR, unverified) — a natal-strength tiebreak
where PN IV II.1, 25 ranks by order and `pn4_governor` `:10964` follows PN IV. **Record only.** PN I #36.

**D8. PN III [V.10], Latin only** (pdf pp. 138–139; fn 680 "not reflected in Pingree"): the Moon's
twelfth-part aspected by malefics; "if the Moon is not being aspected by any [planet], nor does she
aspect the Ascendant, he will strive to acquire something in that year but he will not acquire it";
"the Sun burning up the planets is worse than a malevolent". No Arabic witness. **Record, do not
build.** PN III item 21.

### Group E — natal conditions, small and independent

**E1. The Moon on the third day** — BA III.9.1 `[1]`, III.9.2 `[1]` "the place of the Moon under the
third day of the nativity"; JN Ch. 1 end, Ch. 27 ("commingled to Mars or in his domicile or bound …
foreign travels"); Abū Bakr II.11 (fn 1235: Dorotheus Excerpt XX); **Sahl 1.29, 11–13, 1.30, 28** —
course text. **Small**: the Moon 72 h after birth. PN I #24. Decision 18.

**E2. Gestation** — BA III.1.10 `[2]`: 258 days with the Moon at the Descendant, +2½ days per
twelfth counter-clockwise to 288 (OCR, unverified); **Sahl 1.8–1.9** the course citation; Abū Bakr
I.4.1 the Trutine, Appendix C Dykes's arithmetic ("I myself have not practiced this"). **Small.**
PN I #25, PN II §7.21. Decision 18.

**E3. Lesson 10's Mars row from Abū Bakr II.1.0** (3.4) with I.12.3 "Mars destroys nourishing,
especially in diurnal nativities, and especially if he were above the earth" and II.1.1 Saturn in the
MC by night "very fearful" (OCR, unverified). **Small**, a supplement row, **after the marker OCR**.
PN II §7.2. Decision 13.

**E4. A second eye-degree list beside Sahl 6.2, 48–75** — Abū Bakr II.7.3 (= Māshā'allāh's, BA
III.6.2; Taurus 6, 9, 10; Cancer 9–15; Leo 18, 27, 28; Scorpio 19, 28 and per Dorotheus 8, 9, 10, 22;
Sagittarius 1, 7, 8, 9; Capricorn 26–29; Aquarius 6, 10, 19) and Hugo's own variants (BA fns 36–43:
Leo 18, 28, 29; Scorpio 17, 19; Aquarius 10, 18, 19) (OCR, unverified). Dykes: Sahl's list is "somewhat
different". **Small**: a second column on the #20 finding (`EYESIGHT_PLACES` `:6209`), **carried as two
lists, never reconciled**. PN II §7.14, PN I #46. Decision 14.

**E5. Small sentences for existing rows** — Abū Bakr I.17 "we must consider the type of the native
and his age" for the distribution page's help (PN II §7.12); JN Ch. 3's Lot-as-*hīlāj* restriction to
the domicile/exaltation/bound lord and the Asc/Lot/syzygy gender exemption (PN I #6b); BA III.11.1 /
al-Andarzaghar "these two Lots must be used together" for `slaves` + `enemies_necessity` (PN I #17b);
JN Ch. 10's triplicity lords of the Ascendant as thirds of life, "the Lord of the Ascendant testify to
the first Lord … the Lord of the Midheaven to the second … the Lord of the seventh place to the third"
(PN I #45 — #21's Ascendant rows, off by default, are the place); TBN II.2's "whether it aspected the
Ascendant or not" for the *jārbakhtār* (already the app's reading, PN IV III.1, 11). All (OCR,
unverified); all **tiny**.

**E6. The *jār kanār*** — BA III.1.10: a sixth, last-resort releaser (the Sun in a male sign or the
Moon in a female, angular or succedent, with the lord of the Ascendant or MC aspecting "from the
direction of the tenth") (OCR, unverified). Not in Sahl. **Small**; a note. PN I #39.

**E7. Al-Qabīsī and Abū Ma'shar doctrines in hand the coverage list does not know** (ITA §D, all
OCR, unverified; the canon rule asks of each whether the course teaches it): enclosure by sign (IV.4.2
second kind); facing (II.11, al-Qabīsī III.5); al-Qabīsī's synodic stages (II.10.1–2, III.9–10) and Abū
Ma'shar's easternness ending at 90° (fn 27, p. 97) against the app's hemisphere option; the Moon's and
superiors' elemental quarters (II.12); the lord of the turn (VIII.2.3); transits by apogee and latitude
(VIII.2.4); the *namūdār* (VIII.1.2); bodyguarding in three authors (III.28, pp. 206–216 — the app has
none); times or changes (IV.7); the bright/dark/smoky/empty degrees (VII.7, two tables that disagree);
al-Qabīsī's increasing-fortune degrees (I.53, Figure 118); the Lots the app lacks (§D14, twenty-odd,
with the releaser Lot's fn 22 "probably wrong"); the pains of the planets in the signs (I.4), the
colours of the places (I.17), planetary friendship (III.27), the bust (VIII.4), the opening of the
portals (VIII.3.4). Sizes small to medium each; none ranked here — they wait on a canon ruling.

---

## Class 4 — Confirms

Sixty-six rows. The headline of all four passes: the Latin *On Rev. Nat.* agrees with the Arabic
on every apparatus sentence the app rests on in Books I–V and independently witnesses three PN IV
printed defects (D-07, P-02, P-03); BA/JN/TBN/Abū Bakr agree with Sahl on every Lot and rate the app
carries; ITA confirms 31 of 63 rulings and readings outright. "Cite" = a citation to add; no behaviour
moves.

| Item | Source(s) | App location |
|---|---|---|
| The Moon's division of the year among her connections | PN IV II.22, 2 (the Latin II.22 divides among the proxies; Dykes 2010 "does not make sense to me") | `pn4_moon_portions` `:11267` |
| The Sun's proxies: Leo in root and revolution; the hand-over | PN IV II.13, 1 (Latin garbled, "configured with") | `:11646–11732` |
| II.3, 9–12 read by reception | PN IV II.3, 11 (Latin "configured to benevolents") | `:11775` |
| Indicator #7's void-Moon fallback | PN IV II.1, 12; fn 326 (the Greek has it; the Latin alone dropped it) | year-lord indicators row 7 |
| Indicator #11 = the turning (VI.2) | PN IV II.1, 16 (Latin "period or orb", fn 331) | the refusal row |
| The nineteen ranked on II.1, 25 | PN IV II.1, 25 (Latin ranks only first > second > third) | nine citations |
| The unit key (years / months and days / days and hours) | PN IV III.1, 6 = PN III III.1 | chart-level keying |
| The three-case ascension rule; the third case deferred to another book | PN IV III.1, 12 = PN III III.1 (both defer; "semi-arcs" is Dykes's gloss in both) | `PN4_ASCENSION_RULE` `:8743` |
| The rate ladder's bottom rung in thirds (D-07) | PN IV III.1, 13; PN III fn 485 "Reading with Schmidt for *tertia*" | `:8613` |
| III.2's partner ranking and the longevity gate | PN IV III.2, 103–106, 110–111 = PN III III.2 | `:11301` |
| Fixed-star places in the revolution (six) and the root (four) | PN IV III.8, 9; I.6, 7 (Latin lists fewer) | `pn4_fixed_star…` `:12186` |
| Ninth-parts 3° 20′ (P-02) | PN III III.9 "200', namely 3 1/3 degrees exactly" | `:11153` |
| The Nodes last in both sects, no sub-periods; Head before Tail (P-03) | PN IV IV.7, 23–26; IV.1, 8 = PN III IV.1, IV.8 | `pn4_fardar_sequence` `:10348` |
| The diurnal *fardār* sequence | PN IV IV.1, 3 = PN III IV.1 (fn 586 dismisses Schmidt's "wherever") | `:10348` |
| The transit grade's three rungs (degree, bound, sign) | PN IV V.1, 3 = PN III V.1 (the moiety rungs 4–6 are Arabic only) | `_pn4_transit_grade` `:10736` |
| Mighty days on zodiacal degrees, 12d 4h 10m 30s | PN IV IX.7, 25, 28 | `:9104` |
| Small days at 59′ 08″ a day | PN IV IX.7, 29; **TBN II.2, II.5, II.6.1** (two centuries older); al-Qabīsī IV.13b (ITA p. 367) | `:9042`, `:8835–8869` |
| The III.1 example not a fixture | PN III III.1 differs from PN IV III.1, 19 in five places; Dykes corrects it in both volumes | (none; method only) |
| Releaser order follows Sahl 1.15 | BA III.1.5, JN Ch. 2, TBN I.4.1, Abū Bakr I.15, al-Qabīsī IV.4 all differ — see §6 row 7 | `sahl_releaser` `:9860` |
| Both *hīlāj* and *kadukhudhāh*: Sun in Aries/Leo, Moon in Taurus/Cancer | BA III.1.9; JN Ch. 3; al-Qabīsī IV.6 (ITA p. 356) | `SAHL_BOTH_AT_ONCE` `:9266` — cite |
| The distribution rate 1° = 1 y, 5′ = 1 m, 1′ = 6 d, 10″ = 1 d | BA III.1.10 = Sahl 1.18, 21 | `sahl_releaser_distribution` `:9910` |
| The *jārbakhtār* = the bound lord of the Ascendant "whether it aspected … or not" | TBN II.2; Abū Bakr I.17; fn 145 (BA's is the *hīlāj*'s) | the Ascendant distribution |
| The house-master directed as Sahl 1.23, 2 states | BA III.1.7 `[6.1]`; Dykes App. B (5) calls it an error — caption may say so | `sahl_house_master_direction` `:9926` |
| The two-share rule and bound-first ranking | BA III.1.6; TBN I.4.2; al-Qabīsī IV.5 fn 21 "Dorotheus … the preferred and older approach" | `SAHL_DIGNITY_RANK` `:9254`, `DIGNITY_ORDER` `:5717` — cite fn 21 |
| 1.20, 10–11's greater-years cells | TBN I.4.3 second block (Sahl fn 151) | `_sahl_1_20_grade` `:9533` |
| Lot of death: Moon → 8th, cast from Saturn | BA III.8.0 `[4]`; Abbr. VI.36; *Gr. Intr.* VIII.4.1098–1106 (Latin "by equal degrees"); al-Qabīsī V.11a — none reads the Ascendant | `:5263` (+ `death_ws`) — cite |
| Lot of the killer (day lord of Asc → Moon) | BA III.8.1 `[9]` = Sahl 8.2, 17 (III.8.0's sects reversed, partly Dykes's bracket) | `:5296` |
| Lot of travel, lord 9 → 9th, unreversed | BA III.9.1 `[9]` | `:5302` |
| Lot of money, lord 2 → 2nd | BA III.2.1 `[1.8]` | `assets_lord2` `:5153` |
| Sibling Lots, both unreversed | BA III.3.2 (fn 12); ITA VI.2.5 (fn 28: the Valens attribution "a misattribution") | `:5165` — note fn 28 |
| Children's Lots: Jupiter → Saturn reversed (Hermes), Theophilus unreversed; Mars → Jupiter unreversed | BA III.5.1; ITA VI.2.13–14; al-Qabīsī V.8a | `:5218`, `:5232` |
| Marriage Lots unreversed | BA III.7.1 (fn 7: men reversed by night — BA's own); ITA VI.2.21, 23 three witnesses unreversed, Dykes fnn 58, 62 dissenting | `:5238` — a note |
| Lots of disease, works, desire, necessity, spirit, exaltation, mother | BA III.6.3, III.10.1, III.12.1; Abū Bakr I.14 (Spirit "Absence"); JN Ch. 30 fn 166; ITA VI.1.2, VI.2.40–41 | `:5253`, `:5307`, `:5343`, `:5349`, `:5115`, `:5147` |
| Lot of slaves reversed; paired with Mercury → Fortune | BA III.11.1 (reversal ambiguous; JN fn 130) | `:5258`, `:5355` |
| Lot of Basis = Fortune → Spirit, reversed; = the Lot of Venus | ITA VI.1.4; *Gr. Intr.* VIII.3.560–78; al-Qabīsī V.4f | `:5130` — cite (3.15) |
| The father Lot's second form, Sun → Jupiter (Hermes) | ITA VI.2.7; al-Qabīsī V.6b–7a | `father_burnt_abu` `:5194` — cite |
| Lots of Jupiter and Saturn | ITA VI.1.7–8; al-Qabīsī V.5c, V.11d | `:5388`, `:5398` — cite (3.15) |
| Void of course sign-bounded, no 30° clause | BA II.8 (fn 41) | `:10777`, `_pn4_luminary_connections` `:11224` |
| Besieging by bodies or rays; the fortunes' row | BA II.6 (the 7° interval BA's own); ITA IV.4.2, al-Qabīsī III.25b–26 | `:6611`; #22 |
| The 12° node orb for either node | BA II.5 "any star"; Intro 3, 107; VII.6, 52 | `:7203` |
| The nine-day rule; Venus/Mercury 19° | BA II.1–II.2 = Sahl 1.22 (Dykes fn 171) | `:1485` |
| Twelfth-parts ×12 from the sign itself | BA II.14; al-Qabīsī IV.15 (fn 59: quadrant houses for the houses' twelfth-parts) | `_twelfth_part_sign` `:7942` |
| The 5° above the Ascendant | BA I.4 (fn 41 "unclear to what end"); al-Qabīsī IV.4 "five equal degrees" | `get_effective_house` `:4541` — cite (3.12) |
| *Firdāriyyāt* years, starts, sevenths | BA IV.17–25 (Hugo omits the Nodes-last rule, fn 228) | `:10348`, `pn4_fardar_subperiods` `:10365` |
| True solar returns (tropical) | PN IV I.4, 31; BA IV.1's 6⅕ h (sidereal) differs ~20 min/yr by age 60 | the SR computation |
| Abū Bakr's middle-years construction gives 39½ | Abū Bakr I.16 — **one side of §6 row 1**, not a confirmation on its own | `:8530` |
| The mother from the tenth | TBN III.4.2; Abū Bakr II.5.0; fn 270 calls it a misreading of *Tet.* III.6 — docs, not page | the PN IV VI.2, 8 row |
| The 15° eminence bands | TBN III.1.1 [2] = Carmen I.26; Abū Bakr II.2.2; unit unstated — ascensional stays Sahl's | `SAHL_2_13_BANDS` `:9801` |
| The seven good places = Timaeus/Dorotheus's seven | ITA pp. 18, 121 | `SAHL_GOOD_PLACES` `:9265` — cite (3.17) |
| The stakes' ambiguity is Dykes's own statement | ITA I.12 fn 149; III.4 fn 32 | the 1.7 governor row — cite |
| Sect/hayz all three conditions; Mars excepted | ITA III.2, Abbr. III.3; al-Qabīsī I.78 (*halb* vs domain) | `:1781` — cite |
| Whole-sign aspects, none out of sign | ITA III.6, *Gr. Intr.* VII.5.722–41 fn 40; fn 47 (al-Qabīsī); BA II.16 fn 90 | the aspect table |
| Per-planet orbs, no moiety; Saturn–Moon example | ITA II.6, Abbr. II.11–12, *Gr. Intr.* VII.4.354–89; al-Qabīsī 6°, BA 3° the other two ranges | `PLANETARY_ORBS` `:1919` |
| Cazimi 16′; under the rays 15/15/18, 7, Moon 12 | ITA II.9 al-Qabīsī III.7; II.10.1–2, 5; Glossary p. 384 | `CAZIMI_ORB` `:1573`, `solar_phase` `:1575` |
| The burnt path's two bands | ITA IV.3, *Gr. Intr.* VII.6.1192–1218; al-Qabīsī III.29 | `:5630`, `HARSH_BURNED_PATH` `:6809` — cite (3.13) |
| Dispatch: whole signs for topics, divisions for strength | ITA Introduction §6 | `:14985` — cite (3.7) |
| The Moon's eleven corruptions | ITA IV.5, Abbr. IV.26–31 | `:7846–7890` |
| Rhetorius Ch. 26's dominance (9th/10th/11th) | ITA IV.4.1 p. 223; Glossary p. 386 (Abū Ma'shar names the tenth and eleventh) | #22 |
| Only the sect's triplicity lord scores in the almuten | ITA I.18 fn 210 | `evaluate_victors` `:8355` |
| "Looking" = whole-sign aspect for the house-master; the meeting's lord-looking test for all candidates; the Ascendant last | ITA VIII.1.3 fn 18; al-Qabīsī IV.4 pp. 354–355 | Releaser tab captions (2), (5), (7) — cite |
| The Moon's side by rising-before-the-Sun = "right" | al-Qabīsī III.8a (ITA p. 98) | `:4782` — cite (3.16) |
| Mercury diurnal as a morning star | *Gr. Intr.* IV.9 (ITA V.11) | `:1644` — cite (3.14) |
| Morin's 6/8/12 as the tradition's difficult averse places | ITA fn 43 p. 224 (photographed) | `:6099` — cite (3.8) |
| The 12° phase markers | Abbr. II.27–31 | `:14442` — cite (3.9) |
| The triplicity lords' sect order | Abbr. I.86; al-Qabīsī I.16 | #21 — cite (3.10) |
| `NOT_IMPLEMENTED_COVERAGE`'s descriptions (latitude connection, masculine/feminine degrees, advancing quadrants) | ITA III.7.2; VII.8 ("we have followed this teaching as a most potent one"); I.11 fn 143 | `:5533` list |

---

## Class 5 — Still absent

Grouped by the volume that now witnesses them; none is buildable without a decision the owner has
not been asked, or is delineation the canon rule keeps off the pages.

**From PN III / PN IV (Latin and Arabic both, unbuilt):**
- The quarters of the year (PN III III.8, pdf p. 108 = PN IV III.8, 48–50; the Latin cleaner, without
  the convertible-sign condition at 48). Computable; not built.
- The transit's duration by planetary period, "orb" = *periodos* (PN III V.1 = PN IV V.1, 27–35).
- The transit moiety rungs (PN IV V.1, 4–6; Figure 83's orbs are Dykes's table, not the text's).
- The substitute lord (PN IV II.23, 41; III.8, 15–16; PN III fn 468 confirmed) — Dykes doubts it in
  both volumes.
- II.5, 59–64's delineation of aspects by condition (the 2010 rewrite = the Arabic); the Moon's sign
  "close to the power" of the year's Ascendant (II.22, 14); the Nodes' delineations (IV.7, 20–23).
- The ascensional variant of the mighty days — §6 row 5, for `13_open_decisions.md`.

**From PN I (BA/JN):**
- **The 1.21 additions**, including the nodes' quarter — JN Ch. 4; TBN I.4.3–4; Abū Bakr I.15 (twice,
  once inverted); Sahl 1.21. Printed on the Releaser tab, not applied (`:15829`). PN I #3's claim that
  the app applies ±¼ is wrong (see Class 2's tail). If built, JN's "the square or opposite rays of the
  fortunes add or subtract nothing" (OCR, unverified) contradicts Sahl 1.21, 8 as Dykes emends it. §6
  row 6.
- Paul's male/female children Lots (Moon → Jupiter, Moon → Venus; BA III.5.1 fn 17) — now with a
  formula in the corpus; `NOT_IMPLEMENTED_COVERAGE` "male/female (3.13, 20)".
- Venus → the 7th's pivot (reversed by night, BA fn 87) and Sun → Moon "added to Venus by day,
  subtracted by night" (fn 31) — BA supplies the night rules the coverage entry lacks.
- The Lot of Boldness (JN Ch. 34 gives no formula; `courage` `:5375` is the Hermetic Mars → Fortune).
- Mercury's sect by company (BA II.11) — do not import (3.14).
- Spear-bearing (BA II.12, Dykes's reconstruction; JN Chs. 6, 16; TBN III.1.1 [1] "garbled") — DEC-D-18,
  display only, stands.
- Twelfth-parts beyond the Moon's (BA III.4.3, III.10.8; Sahl 2.6, 4.9) — coverage entry stands.
- BA IV.2–IV.7, the lord of the year per planet (al-Andarzaghar's layer) — canon-only; PN IV IV.4, 4–11
  says Abū Ma'shar kept it for one sect.
- The Lot of the *Hīlāj* (Valens III.7; BA fn 120; ITA VI.2.2 fn 22 "probably wrong") — no formula.
- BA II.17's ascensional-time "regards" — Dykes: "a historical exercise"; do not build.

**From PN II (TBN / Abū Bakr):**
- The parents' directions (TBN II.5, III.4; Abū Bakr II.5.9–5.13; the one worked chart unrecoverable
  from this OCR).
- The sterile signs, four lists (TBN III.6; Abū Bakr II.6.3; Sahl's two in `BARREN` `:5674`) — the note
  could cite four.
- Mastery (Abū Bakr II.12.2–12.8, 12.46; the Moon-application override Dykes singles out) — Sahl Ch. 10
  is the course text; no mastery significator in the app.
- *Dusturiyyah* for rank and parents (TBN III.1.1 [1], III.4.1–2).
- Rearing (TBN I.3's four determinations; Abū Bakr I.12's eight significators) behind Sahl 1.1.
- The time of an illness by quadrant, clockwise (Abū Bakr II.7.37) — a second witness for Sahl 6.5, 1's
  exception; nothing to build.
- The 29°-rising partnership of the lord of the 2nd (Abū Bakr I.15 end; fn 623 Morin).
- TBN I.4.8 [10]'s half-years-at-sign-end killer and I.4.7's six malefics — fn 123 "a minority Persian
  doctrine".
- Abū Bakr II.7.7's dark degrees — Dykes cannot identify them.

**From ITA:**
- The masculine/feminine degrees (three schemes; Abū Ma'shar "most potent") — coverage entry stands.
- The wells' Latin/al-Qabīsī cells (Figures 114–115) — edition differences; a note when the page is read.
- The Ascendant degree among the eyesight places — "this app's addition" (`:6327`); ITA silent.

---

## 6. Disagreements among the sources themselves

These are the owner's rulings to make, flagged as such. Every witness on each side; "(OCR)" = OCR,
unverified.

| # | Question | Side A | Side B | App does | Status |
|---|---|---|---|---|---|
| 1 | **The luminaries' middle years** | **39½ / 39½**: *Gr. Intr.* Fig. 146, the 2020 Arabic volume (VII.8, 3–8); Abū Bakr I.16, PDF p. 159 (OCR) — the construction in prose; the course's Lesson 5 table. (The app's comment also cites Valens VII.5 and PN IV I.8, 12 — the latter Abū Ma'shar again.) | **69½ / 66½**: BA III.1.8, pdf p. 105 (OCR); JN Ch. 4, pdf p. 279 (OCR); the Latin *Gr. Intr.* Fig. 108, ITA p. 332 (read on the page by the owner). Dykes: "traditionally 69½" (PN II fn 625). | 39½ (`:8534`, `:8537`) | **Ruling** — decision 1 |
| 2 | **'Umar's weights and the "older" label** | **Bound 3 > triplicity 2, "al-Tabari/Masha'allah"**: the course, *Handy Tables* p. 33; the order (not the names) al-Qabīsī I.22 "certain people" (ITA p. 81, OCR). | **Triplicity 3 > bound 2 as 'Umar's**: Abū Bakr II.5.14 via al-'Anbas, PDF p. 248 (OCR; Jag. names "Aseme-zael", fn 956); al-Qabīsī's own order (I.22); Dykes, PN II Intro pp. 15–17: not in Sahl or Māshā'allāh, 'Umar a Ptolemaic count (fn 48). | Both computed; label kept as printed | **Ruled** 2026-09-15 (#23) |
| 3 | **Lot of friends, reversed at night?** | **Reversed**: Sahl 11.1, 29 as the row reads him (Dykes's note 72); BA III.12.1, pdf p. 222 (OCR); al-Andarzaghar via al-Qabīsī V.14a (OCR); Dykes fn 104. | **Unreversed**: Abbr. VI.53; *Gr. Intr.* VIII.4.1464–69 (Latin), ITA p. 320 (OCR). | Reversed, "settled" (`:5335`) | **Ruling** — decision 4 |
| 4 | **The enclosure breaker** | **Any third body or ray**: Rhetorius Ch. 41 (Holden), on #22. | **A fortune or the Sun only, friendly aspect, < 7°**: *Gr. Intr.* VII.6.1244–60 and al-Qabīsī III.28b (ITA IV.4.2 p. 225, photographed); **the Sun's ray within 4°–5°**: BA II.6, pdf pp. 68–69 (OCR); **opposite quality**: Dykes ITA p. 228. | Any (on #22, unmerged) | **Ruling** — decision 3 |
| 5 | **Mighty days: zodiacal degrees or ascensions?** | **Zodiacal, × 12d 4h 10m 30s**: PN IV IX.7, 25, 28 (the Arabic; the arithmetic only works on zodiacal degrees); TBN II.4's 12⅙ days per degree is zodiacal too (OCR). | **Ascensions**: PN III IX.7 method 6, pdf p. 144 (the Greek via Schmidt and Dykes 2010, "Convert the following 30º into ascensions"); PN IV fn 176 (Birchfield: "would make more sense"). | Zodiacal (`:9104`) | **Ruling** — decision 19; record in `13_open_decisions.md` |
| 6 | **The nodes' quarter of the years** | **Head +¼, Tail −¼**: Sahl 1.21, 11–12 (12° for the Tail only); JN Ch. 3 (no orb, graded by closeness; Tail worse with a luminary house-master) (OCR); TBN I.4.4 (Tail with a *malefic* house-master within 12° −¼; Head with a *benefic* within 12° +¼) (OCR); Abū Bakr I.15 second statement (OCR); BA II.5 12° "for any star" (OCR). | **Head −¼**: Abū Bakr I.15 first statement, PDF p. 156 (OCR). | Not applied | Ruling only if the 1.21 additions are built |
| 7 | **Releaser candidate order** | **Sahl 1.15** (day Sun, meeting, Ascendant; night Moon, fullness, Lot, Ascendant). | BA III.1.5 (Sun/Moon → Asc → Lot → syzygy); JN Ch. 2 and TBN I.4.1 (Lot if preventional, Asc if conjunctional — Hermes's rule at BA III.1.9); Abū Bakr I.15 (+ a sect-swap "certain sages"); al-Qabīsī IV.4 (both luminaries in either sect before the syzygy). (all OCR) | Sahl | **Ruled** (1.15_readings Q1); name the variants on the tab |
| 8 | **House-master ranking** | **Bound first**: Sahl 1.20, 2; TBN I.4.2; Dorotheus (al-Qabīsī fn 21 "the preferred and older approach"). | **Domicile first**: Abū Bakr I.15 (OCR); al-Qabīsī IV.5 "some"; Glossary p. 777. | Bound first | **Ruled** (D-8: record, do not merge) |
| 9 | **The five degrees: four stakes or every cusp?** | **Four stakes**: the course (Lesson 3); the owner's ruling of 2026-09-11. | **Any house**: al-Qabīsī IV.4 (ITA p. 355, OCR); Ptolemy per Dykes p. 12; Sahl 1.18, 19 read literally; BA I.4 (Ascendant only). | Stakes only (`:4541`) | **Ruled**; decision 2 is whether to add the alternative |
| 10 | **The wells** | The 2020 Arabic *Gr. Intr.* photographs (`WELLED_DEGREES` `:5609`). | The Latin *Gr. Intr.* Fig. 114 and al-Qabīsī Fig. 115 (ITA p. 346, OCR — tables are the OCR's weakest ground) differ in several cells and from each other. | Arabic | Note when the page is read |
| 11 | **The eye-harming degrees** | Sahl 6.2, 48–75 (`EYESIGHT_PLACES` `:6209`, #20). | BA III.6.2 Hugo's own (fns 36–43) (OCR); Abū Bakr II.7.3 = Māshā'allāh's (OCR). | Sahl | Two columns, never merged — decision 14 |
| 12 | **The sterile signs** | Sahl *Intro* 1, 23 and *Nat.* 1.38, 16–17 (`BARREN` `:5674`). | TBN III.6 (Leo, Taurus, Capricorn, Libra, Aquarius); Abū Bakr II.6.3 (Gemini, Leo, Virgo) (OCR); fn 308's four rival lists. | Sahl's two | Note only |

---

## 7. Owner's decisions required

Answer by number ("1 yes, 2 no, 3 as recommended").

1. **Keep 39½ for the luminaries' middle years, and add a Reference-page note naming the three
   ordinary-mean witnesses (BA III.1.8, JN Ch. 4, the Latin *Gr. Intr.* Fig. 108)?** Recommended:
   yes — three each way, and the 39½ side is the Arabic *Gr. Intr.* the app cites for the rest of the
   table plus the course; the note is owed either way.
2. **Leave the five-degree rule at the four stakes (as ruled) and add a note that al-Qabīsī IV.4 reads
   "any house", rather than restoring `five_degree_all_cusps` as a declared alternative in the
   releaser search?** Recommended: note only — the ruling stands for Sahl, and a code alternative
   would import another author's procedure into Sahl's selector.
3. **On PR #22, make the besieging row's breaker ITA's (a fortune or the Sun, friendly aspect, under
   7°) rather than Rhetorius's "any third body or ray"?** Recommended: yes — the row's besieging
   definition is already ITA IV.4.2's by the owner's earlier instruction, and the breaker should match
   it, with Rhetorius Ch. 41's "any" named as his.
4. **Downgrade the Lot of friends' confidence from "settled" to "reversed after al-Andarzaghar
   (al-Qabīsī V.14a), BA III.12.1 and Dykes; Abū Ma'shar unreversed"?** Recommended: yes — text only,
   the formula stays.
5. **Relabel `PN4_ASCENSION_RULE` now and build the proportional semi-arcs from al-Qabīsī IV.11–12 with
   Appendix E's example as the fixture?** Recommended: yes to both — the relabel is a correction, and
   the build unblocks the third case in three places at once.
6. **Relabel the almuten "the weights and the five places al-Qabīsī's (I.22, IV.7); the worksheet ibn
   Ezra's", quoting fn 211 as the standing critique?** Recommended: yes — a correction, not a number
   change.
7. **Replace "no text says" on the fullness's degree with the three opinions, keeping Valens's Moon
   default and not adopting the "certain sages'" eastern-degree tie rule?** Recommended: as stated —
   name the three, adopt none.
8. **Keep Figure 57's ordinal-span reading (as ruled) and add Dykes's point-at-the-end resolution and
   al-Qabīsī's Figure 118 as a third table on the page?** Recommended: yes — the ruling stands, the
   page gets the two readings.
9. **Build JN Ch. 3's / TBN I.4.3's years ladder as a labelled supplement fallback for the "1.20
   silent" cells only?** Recommended: yes, after the marker OCR — small, two witnesses, and it fills
   the only blank output on the Releaser tab.
10. **For Sahl 1.20, 14–15, carry TBN I.4.3's degree reading in the printed note without defining
    "serious impediment" in code?** Recommended: yes — the note; the definition is not in any text.
11. **Build the prosperity classifier's computable core from Sahl 2.1–2.21's sentences with BA III.2.0's
    frame, after the marker OCR?** Recommended: yes — medium, course text throughout, and the
    DELIN-TABLES order shares its machinery.
12. **Record 'Umar's 30° profection at 12⅙ days per degree in `16_open_features.md` as a named
    alternative, and not build it?** Recommended: record only — canon; the course's profection is the
    monthly one.
13. **Add Lesson 10's Mars row from Abū Bakr II.1.0 as a supplement row after the marker OCR?**
    Recommended: yes, then — the only corpus witness for any Lesson 10 row.
14. **Add Abū Bakr II.7.3's / Hugo's eye-degree lists as a second column on the #20 finding, carried as
    separate lists?** Recommended: yes, after the OCR — two lists, never reconciled.
15. **Name al-Qabīsī IV.5's nearest-degree tie-break in `SAHL_1_7_UNMODELLED`'s note rather than
    borrowing it into the governor?** Recommended: name only — a different technique of a different
    author.
16. **Leave al-Qabīsī's whole releaser/*kadukhudhāh* procedure unbuilt and record it in
    `16_open_features.md`?** Recommended: yes — large, and the course teaches Sahl's.
17. **Name al-Qabīsī IV.4 on the Releaser tab as the quadrant witness and leave decision-sheet row 3
    (the Lot by whole sign) as ruled?** Recommended: yes — the ruling stands.
18. **Build the Moon on the third day (Sahl 1.29, 11–13) and gestation from the Moon's distance to the
    Descendant (Sahl 1.8–1.9) as two small findings?** Recommended: yes — both are course text; BA and
    JN are the witnesses, not the citations.
19. **Record the mighty days' ascensional variant (PN III IX.7 method 6; PN IV fn 176) in
    `13_open_decisions.md` and keep the zodiacal arithmetic?** Recommended: yes — the Arabic's
    arithmetic is the built text; the variant is the one place the Greek is arguably better astronomy.
20. **Rewrite `COURSE_COVERAGE_2026-09-14.md`'s header and gap list (3.4) in the same text-only PR as
    3.5–3.17?** Recommended: yes — one PR, no number changes, every "this app's" that Dykes states
    cited to him.

---

## 8. Counts and what to do first

| Class | Count | Notes |
|---|---|---|
| 3 — contradicts a claim | **17** | 2 fixed on open PRs (#22 kollēsis, #23 the weights' witnesses); 1 on #21 itself (3.10); 14 remain — 4 false or stale statements (3.1, 3.4, 3.5, 3.6), 10 self-attributions Dykes states |
| 2 — contradicts an implementation | **6** | 3 covered by rulings and standing (2.2, 2.5, 2.6); 3 for the owner (2.1 the years, 2.3 friends, 2.4 the breaker) |
| 1 — newly available | **28 items in 5 groups** (+ ITA §D's fifteen doctrines awaiting a canon ruling) | A1 unblocks the most; B1 is the smallest with a visible effect |
| 4 — confirms | **66** | The Latin agrees with the Arabic on everything the app rests on in Books I–V; every Lot and rate agrees across BA/JN/TBN/Abū Bakr/ITA |
| 5 — still absent | **28** | The 1.21 additions are the one with three new witnesses and a stated internal contradiction |
| Source disagreements | **12** | 5 are rulings to make (rows 1, 3, 4, 5, and 9's alternative); 4 already ruled; 3 notes |

The pattern of `02_reconciliation.md` holds a third time: the corpus grew by four volumes and the
code's behaviour survived. No sentence the app builds from PN IV is contradicted by the Latin; no Lot
or rate it carries from Sahl is contradicted by Māshā'allāh, Abū 'Alī, 'Umar or Abū Bakr; and where
ITA cuts against the app it cuts against *labels* — "no text in hand", "this app's", "no witness",
"settled" — not against numbers. The two numbers in question (39½; the five degrees' scope) are
even splits between authors, not errors.

**The next build session should do, in this order:** (1) one text-only PR carrying 3.1, 3.4–3.17 and
decisions 4, 6, 7 — every claim corrected or cited to Dykes, no number changes, the 39½ note included
however decision 1 goes; (2) the proportional semi-arcs (A1) with ITA Appendix E as the fixture, which
retires `PN4_SEMIARCS_UNAVAILABLE` in three places; (3) the JN/TBN years ladder (B1) for the "1.20
silent" cells. Before anything from PN I or PN II reaches a page, the marker OCR of both volumes must
supersede the embedded text layers — every BA, JN, TBN and Abū Bakr quotation above is unverified, and
the two artifacts say so on every line.
