# Open decisions — everything deferred across the seven passes, in one sitting's worth

`main` @ `70e6ce2`, 1024 passed / 2 xfailed. Written 2026-09-08. **Nothing decided, nothing
implemented**; `app.py` and the tests are untouched. Line numbers are `main`'s.

Frequencies are measured over **400 random charts** (years 1200–2000, latitudes −50° to +60°,
seed 20260908) plus the six fixture charts, 2,842 planet placements in all; the script is
reproducible from `synthesis/`'s description below each figure. "Placements" means one planet in
one chart; "charts" means whole charts.

Eighteen items. The owner named fifteen; three more came from sweeping the artifacts (**D-16**,
**D-17**, **D-18**). Ordered by what each unblocks, most first.

## Summary table

| # | Question (answer A/B or yes/no) | Recommendation | Confidence | Cost | Unblocks |
|---|---|---|---|---|---|
| **D-1** | Build VII.7's ascensional ray-casting as a static chart quantity, labelled Ptolemy's, or leave it under the timing deferral? | **Build it** (static; not a direction) | medium | subsystem | Aph. #45, *Nat.* 2.13, 48–51, C-16, ascensional distributions (04 Q10) |
| **D-2** | When a connection is both a non-reception (Kind II/IV) and a Māshā'allāh minor-dignity reception, does the refusal win? | **Yes — refusal wins** | high | one function | the ¶63 xfail, C-18, C-24 |
| **D-3** | Does Sahl's *On Times* fall under the *Revolutions* deferral? | **For implementation, yes; for reading, no** | medium-high | none | `04_timing_open_questions.md` §4 items 2–4 |
| **D-4** | Reverse `work_authority` (Sun→Saturn) at night? | **Yes** | high | one line | — (a displayed Lot, 46% of charts) |
| **D-5** | Which burned-place span: none (Sahl), 15♎–15♏, or 19♎–3♏? | **None as Sahl's; keep 19–3 where the table is Abū Ma'shar's; drop the 15–15 label** | high | small | C-04 |
| **D-6** | Carry Māshā'allāh's "work this if the house and its lord are free of the infortunes and the fortunes do not testify" condition on the two house tables? | **Yes, as a column, not a filter** | high | one function | the Dignities-page displays |
| **D-7** | Expose the contradicted sign categories as two readings by work? | **Yes, never merged** | high | small | C-11, App. B ¶7/¶33 (C-17) |
| **D-8** | Keep two dignity orderings (house-master vs general) as separate constants? | **Yes, never merged** | high | small | C-20, any dignity-rank display |
| **D-9** | The 7-place ranking: printed order (…11, 9, 5) or manuscript B's (…11, 5, 9)? | **Printed, labelled as Dykes's conflation** | low-medium | one line | C-09 |
| **D-10** | Photograph *Great Introduction* V.21 to attest `WELLED_DEGREES`? | **Yes** | high | a shoot | Favor & Recompense's provenance; the `1240-01-04` fixture |
| **D-11** | Project the Lot of death from Saturn (Dykes's emendation) or from the Ascendant (Sahl's MSS)? | **Saturn, labelled as an emendation; switch optional** | medium-high | one line | — (93% of charts change sign) |
| **D-12** | Keep the 12° orb for the Head (as for the Tail)? | **Yes; fix the citation only** | high | one string | — |
| **D-13** | Soften a malefic that rules the Ascendant (*Choices* 1, 12)? | **Switch, default off** | high | one function | C-15 |
| **D-14** | Suppress the withdrawing penalty for 3rd/9th/12th significators (*Questions* 1, 18–20)? | **No — note only** | medium-high | note | C-14 |
| **D-15** | Mars's western under-the-rays orb: 15° (Abū Ma'shar) or 18° (Sahl)? | **Keep 15; add a switch like the Moon's** | medium | one line + radio | — |
| **D-16** | 9th-house Mercury: follow the Guide's printed columns or its content? | **Content (current); annotate** | medium | one string | — |
| **D-17** | Per-topic reassignment of the angles: caveat or implement? | **Caveat only** | high | note | C-23 |
| **D-18** | Which spear-bearing definition, if any? | **None yet; read the course material first** | high | subsystem | the spear-bearing report items |

Items that were once open and are **not**, so they do not reappear below: exaltation degrees
(Standard, `08` §4); the convertible-sign speed rankings (neither, `03` #11); "upright" stakes
(Sahl's, C-21); the sixth antiscia pair (never, `03` #1); `MOON_RAYS_ORB`, `DOMAIN_RULE`,
`EASTERN_RULE`, `LOT_HOUSE_CUSP` (already switches); the Lot of expedition's reversal (both rows
present); Aphorism #45 (ascensional, decided 2026-09-07).

---

## D-1 — VII.7's ray-casting: build it as a static quantity, or leave it deferred? (C-16 ⟨SCOPE GATE⟩)

**Question.** Is Abū Ma'shar VII.7 — Ptolemy's casting of rays by ascensions — a *timing*
technique (deferred with *Revolutions*) or a *chart* quantity (in scope now)?

**Both sides.** For "timing": Dykes's fn. 247 on VII.7, 1 calls it *"normally called 'primary
directions' in English-language astrology"* — his apparatus, not the text. For "chart quantity":
the text computes where a planet's ray falls **at the moment of the chart**, from its hours of
distance from the stakes and the ascensions (*"the rays of the planet are in that degree and
minute"*, VII.7, 16), and says nothing about time. Abū Ma'shar's own framing, VII.7, 1–2: *"All of
the masters of the stars have mentioned the casting of the planets' rays, although many of them
have differed from the others. And we will state their disagreement about it in another book …
we will state what Ptolemy … said."*

**Engine today.** `app.py:4283–4291`: recorded in `NOT_IMPLEMENTED_COVERAGE` as complete text
lacking only the tables it presupposes (VII.7 fns. 250–251, all computable). Aspects are zodiacal
throughout (`_pairwise_configurations`, `:1035`).

**What changes.** If built: a second, ascensional ray position per aspect beside the zodiacal one;
no existing number moves — the zodiacal aspect stays as VII.5's rule. If left: nothing.

**Cost.** A subsystem: right and oblique ascensions for the latitude, hourly times, the four
quadrant cases (VII.7, 4–13), the two lookups and their correction (14–19), the right/left
asymmetry (¶18 adds to the *nearest* candidate, ¶21 to the *more distant* — unexplained, test both).

**Unblocks.** The largest set on this list: *Aphorisms* #45 (ascensional by policy, currently
abstained), *On Nativities* 2.13, 48–51 (the three 15° ascensional bands, in the coverage list),
C-16 itself, and the ascensional half of distributions (`04` Q10 — the rates are known, the
ascensions are not).

**Recommendation.** Build it, labelled *"Ptolemy's method as reported by Abū Ma'shar (VII.7,
1–2)"*, and keep it out of anything that advances a point through time. **Medium confidence**:
the text supports the static reading plainly, but the owner has held every ascension-dependent
item behind PN IV, and PN IV may prescribe a different ray-casting for its own purposes.

---

## D-2 — ¶63: does non-reception override a minor-dignity reception? (the strict xfail)

**Question.** For one connecting pair, when the engine finds both a non-reception (Kind II: the
applicant stands in the receiver's fall; Kind IV: the receiver is in its own fall) and a reception
by triplicity-with-bound, is the reception suppressed?

**Both sides.** For refusal:

> "**40** … if they connected with a planet from its fall (such as if the lord of the Ascendant is
> connecting with Mars from Cancer …), it indicates the corruption of the sought matters, and it
> will not turn out well. **41** And likewise if they were connecting with a planet from their own
> fall: it does not accept them." — *Questions* Ch. 1, 40–41

> "when [Mercury] went out from his sign, he was connecting with Mars, and **he does not accept
> [Mercury]**" — *Questions* Ch. 1, 63, Sahl's own chart; fn. 27: *"Mercury would be connecting to
> Mars from the sign of Mars's fall (see 40 above)."*

For the reception: *Introduction* Ch. 3, 54–55 (Māshā'allāh's triplicity-and-bound reception), and
Mars is the night triplicity lord of Cancer and holds its first bound — so the reception rule, read
alone, fires. Sahl does not state a precedence between Ch. 3, 54–55 and Ch. 3, 58–62. But Ch. 3, 51
says of the contrary of reception that the astrologer *"does not acknowledge it, he does not accept
it"*, and Sahl's own worked example applies exactly that.

**Engine today.** `evaluate_non_reception` (`:3418`) reports Kind II for Mercury→Mars from Cancer;
`evaluate_reception` (`:2974`) also reports "Mars receives Mercury via triplicity, bound".
`tests/test_sahl_question_chart.py:130` holds the disagreement as a **strict xfail**.

**What changes.** With refusal winning: reception rows are suppressed where a Kind II or IV
non-reception holds for the same pair. Measured: **11.9% of reception rows (76 of 638) are such
pairs, in 15% of charts (62 of 406)**; among the fixtures, `1240-10-05` has one (Moon→Venus). The
xfail flips to a pass and must be un-marked. Downstream, every evaluator that reads reception
(returning with suitability, handing-over harmony, Aph. #2's restraint) sees fewer receptions.

**Cost.** One function: a precedence check in `evaluate_reception` under the Sahl profile.

**Unblocks.** The xfail; C-18 (reception as additive "good on top", which needs a clean reception
predicate); C-24 (the *Questions* 1, 24 vetoes, which are the same refusal).

**Recommendation.** **Refusal wins — high confidence.** The author applying his own rule to his own
chart is the strongest evidence this corpus produces, and Ch. 1, 40–41 states the rule generally.
The one reservation: it is a horary chart, and Abū Ma'shar's Figure 143 (fn. 205) treats these very
configurations as *favor* rather than refusal — a different author's different doctrine, which the
Abū Ma'shar profile can keep.

---

## D-3 — Is *On Times* under the *Revolutions* deferral?

**Question.** May the engine implement timing doctrine that is Sahl's (*On Times*) before PN IV
arrives, or does the deferral cover all timing?

**Both sides.** For "in scope": *On Times* is Sahl's own, complete in the corpus, and gives a
releaser candidate set and the granting rule outright — *"if the ruler was in a stake, eastern, it
grants its greater years; or if it was in what follows the stakes, it grants its middle years; and
if it was falling, it grants its lesser years"* (*Times* Ch. 4, 7) — and the lesser-years
conversion (*Times* Ch. 11, 24). For "deferred": Ch. 4, 4 presupposes the natal technique rather
than defining it (*"Direct it just like you direct the [longevity] releaser"*), the two longevity
procedures in Ch. 4 are unadjudicated (`04` §3 #3), and *Nat.* 1.20, 10 contradicts *Times* 4, 7 on
where the greater years are granted (`04` §3 #2). `00_inventory.md` raised exactly this: *"a
decision will be needed on whether Sahl-only timing counts as in scope."*

**Engine today.** The Timing page (`:7381`) shows the annual profection and a symbolic 1°/year
direction labelled *"NOT a distribution"* (`:6391`). Nothing from *On Times* is implemented.

**What changes.** "In scope" would admit: the sign-type time units (*Times* 2, 2–7), the
granting rule (4, 7), the lesser-years conversion (11, 24), the hemisphere quick/slow scheme
(1, 12–14) — each of which conflicts with another passage (`04` §3). "Deferred" changes nothing.

**Cost.** None to decide; each admitted item is small individually but each carries a disagreement.

**Unblocks.** `04_timing_open_questions.md` §4 items 2–4 partially; nothing in `03`.

**Recommendation.** **Deferred for implementation, in scope for reading — medium-high
confidence.** The reason is not that *On Times* is Sahl's; it is that every rule it gives is
contradicted by another passage in the corpus and PN IV is the only source that could break the
ties. The one exception worth admitting now is display-only: the planetary-years table (Fig. 146)
with *Times* 4, 7's placement rule beside *Nat.* 1.20, 10's, both labelled.

---

## D-4 — Reverse the `work_authority` Lot at night?

**Question.** Should `LOT_DEFINITIONS['work_authority']` (Sun→Saturn, projected from the
Ascendant) reverse by night?

**Both sides.** For reversal: Figure 63 in the current OCR reads **☉→♄, ASC (R)**
(`abu_mashar_book_vii.md` — no: `on_nativities.md:12194`); Dykes's fn. 166 says Māshā'allāh
*"defines this in the same way as the Lot of fathers (Sun-Saturn)"*, and the Lot of the father is
*"by day from the Sun to Saturn and by night from Saturn to the Sun"* (*Nat.* 4.14, 1). Against:
Sahl's own text at 10.2.5, 4–14 gives **no formula at all** — the Sun→Saturn identification is
entirely Dykes's apparatus — and Fig. 63's (R) column has been wrong before (an earlier OCR read its
glyphs as Mercury→Venus; `10` §3 row c).

**Engine today.** `app.py:4092–4103`: `reverse_at_night=False`, with the note recording the open
point.

**What changes.** The Lot moves on **every nocturnal chart** (50% of charts) — its **sign changes
in 90% of those, 46% of all charts**. One row of the Topical Lots table; no other consumer.

**Cost.** One line (`reverse_at_night=True`).

**Unblocks.** Nothing queued; it corrects a displayed value.

**Recommendation.** **Reverse — high confidence.** Both witnesses for the formula (fn. 166 and
Fig. 63) reverse it, and the only argument against is that the figure's column has erred before —
but the prose footnote agrees with it here.

---

## D-5 — The burned-place span (C-05)

**Question.** Which degree span does the engine attach to "the burned place": none (Sahl's
wording), 15° Libra–15° Scorpio, or 19° Libra–3° Scorpio?

**Both sides.** Sahl gives no degrees, twice: *"the burned place of the signs is the end of Libra
and the beginning of Scorpio"* (*Nat.* 1.38, 9; *Intro* Ch. 1, 19 the same); *Intro* Ch. 3, 110
likewise, with fn. 120 supplying 19–3 from Abū Ma'shar. The glossary p. 774: *"Some astrologers
identify it as between 15° Libra and 15° Scorpio; others between … 19° Libra and … 3° Scorpio."*
Abū Ma'shar's own: *"the burned path (and that is Libra and Scorpio)—and harsher than that is if it
was from 19° Libra up to 3° Scorpio, because those are the fall of the luminaries"* (VII.6, 40;
the Moon's corruption 71 uses the whole signs). *Choices* Ch. 9, 41 adds *"in Libra, if she went
beyond 10°"* — a third datum matching neither span.

**Engine today.** Three things at once: `HARSH_BURNED_PATH = (199, 213)` (`:4765`) used inside the
Abū Ma'shar table (VII.6, 40, `:5572`) and the Moon's corruption (`:6111`); a "Via Combusta
15 Libra–15 Scorpio" flag in Special Degrees labelled *"external convention, not from these
sources"* (`:4345–4371`, `:7023`); and no Sahl burned-place category (C-04 unimplemented).

**What changes.** Measured over placements: **15–15 fires on 9.6%, 19–3 on 4.3%, the two whole
signs on 18.7%**. (a) no span: the Sahl category is a label on Libra/Scorpio placements with no
degree test; (b) or (c): a degree test. The Abū Ma'shar table is unaffected under any answer — its
19–3 is his own text.

**Cost.** Small: one constant and its label; the switch pattern already exists.

**Unblocks.** C-04 (dark signs and the burned place as Sahl's categories).

**Recommendation.** **(a) — no degrees attributed to Sahl, high confidence**; keep VII.6, 40's
19–3 where the table is Abū Ma'shar's (it already is); retire or rename the 15–15 "Via Combusta"
flag, which no source in hand states.

---

## D-6 — Māshā'allāh's operating condition on the house tables

**Question.** Should the *Topical House Lords* and *Planets in Houses* displays carry Māshā'allāh's
stated condition that his readings apply only when the house and its lord are unafflicted and
unwitnessed?

**Both sides.** The condition is stated at the end of every "lord of the Nth in the houses"
section, e.g. *"Work in this chapter if the lord of the third and the third [itself] were free of
the infortunes, and the fortunes do not witness"* (*Nat.* 3.10, 14); *"Work this topic if the sixth
sign and its lord are free of the infortunes and the fortunes do not testify to them"* (6.3.4, 24);
likewise 7.1, 217; 9.4, 35; 10.2.4, 13; 11.1, 28; 12.1, 47; 4.11, 24. The Reference Guide's table
(the engine's authority for the cells) does not carry it. Nothing argues against the condition
existing; the question is only whether the Guide's silence licenses dropping it.

**Engine today.** `MASHAALLAH_LORDS` and `PLANETS_IN_HOUSES` are displayed unconditionally
(`:6340–6341`, `:7091–7102`).

**What changes.** Measured with whole-sign aspects (infortune with the lord or square/opposite;
fortune with it or in any aspect): **only 10% of house-lord rows (482 of 4,872) meet the
condition.** A column "Māshā'allāh's reading applies: Yes/No" would say "No" nine times in ten. A
filter would empty the table.

**Cost.** One function (the aspect test exists in `_pairwise_configurations`).

**Unblocks.** Nothing queued; it changes what the Dignities page claims.

**Recommendation.** **Yes, as a column, not a filter — high confidence that the condition is the
text's**; medium on its exact shape (the text's "free of the infortunes" is by assembly, square or
opposition elsewhere in Sahl; "the fortunes do not witness" is any aspect).

---

## D-7 — The contradicted sign categories (C-11)

**Question.** Implement four-footed, voiced and barren signs as two named readings selected by
work, or pick one?

**Both sides.** Four-footed: *Intro* Ch. 1, 13 has *"Aries, Taurus, and the beginning of Capricorn,
and the end of Sagittarius"*; *Nat.* 1.38, 1 has *"Aries, Leo, Taurus … and the other [half of
Sagittarius]"*. Leo is in one, Capricorn in the other. Voice: *Intro* Ch. 1, 20 puts Virgo in
*"half a voice"*; *Nat.* 1.38, 25 in *"powerful voice"*. Barren: Aries only in *Intro* 1, 23;
Sagittarius only in *Nat.* 1.38, 16; and *Nat.* 5.1, 8 vs *Nat.* Ch. 3, 10 differ again on
sterility (`01_on_nativities.md` §11c).

**Engine today.** None of these categories exists (`03` C-11: grep → 0).

**What changes.** New labels only; no number moves. Appendix B ¶7 and ¶33 branch on the
four-footed list and would need the reading named.

**Cost.** Small: three small tables keyed by work.

**Unblocks.** C-11; the Appendix B consumers in C-17.

**Recommendation.** **Two readings, never a union — high confidence.** The union is in neither
witness, and `03` #2 already forbids merging.

---

## D-8 — Two dignity orderings (C-20)

**Question.** Keep *Questions* Ch. 13, 7's ordering and *Nativities* 1.20, 2's as separate,
context-labelled constants, or choose one?

**Both sides.** *"the triplicity is below the house, and likewise the bound below the triplicity,
and the face below the bound"* (*Questions* 13, 7 — a planet's rank; exaltation unplaced).
*"the stronger of them is the lord of the bound, then the lord of the house, then the lord of the
exaltation, then the lord of the triplicity, then the lord of the image"* (*Nat.* 1.20, 2 —
house-master selection). Glossary p. 777: domicile > exaltation > triplicity > bound > face
(*"often listed in the following order"*). The bound is first in one and third in another.

**Engine today.** No ordering constant exists; the almuten weights (`VICTOR_WEIGHTS`, verified
against the Handy Tables) are a fourth thing and are not this.

**What changes.** New constants only; no number moves.

**Cost.** Small.

**Unblocks.** C-20; any future dignity-rank display; the house-master (when PN IV lifts the hold).

**Recommendation.** **Keep both, never merge — high confidence.** They answer different questions
and the corpus says so.

---

## D-9 — The 7-place ranking's order (C-09 ⟨CHOICE⟩)

**Question.** In the ranked seven good places (*Intro* Ch. 2, 37–44), is the tail "11, 9, 5"
(printed; manuscripts H, L) or "11, 5, 9" (manuscript B)?

**Both sides.** fn. 42: B reads 11, 5, 9; H and L read 11, 9, 5; the printed text takes H/L's
order **plus** B's note that the ninth is the Sun's joy — a conflation Dykes made. The ninth's
joy (Ch. 2, 42) is itself B-only (C-10).

**Engine today.** No 7-place scheme; `EXCELLENT_PLACES` is Ch. 3, 78's six (`:4790`).

**What changes.** The order of two entries in a display; no number.

**Cost.** One line.

**Unblocks.** C-09's ranked list.

**Recommendation.** **Printed order, with the conflation stated in the note — low-medium
confidence**; two manuscripts against one, but the printed text is not any manuscript's.

---

## D-10 — Photograph *Great Introduction* V.21 for `WELLED_DEGREES`?

**Question.** Shoot Book V.21 (a part of the volume never covered) to attest the wells table, or
leave the constant labelled unattested?

**Both sides.** Provenance is settled and is not re-investigated here: the constant predates the
OCR project (initial commit); no OCR'd page carries its values; no shoot covers Book V; the Handy
Tables have no wells table; both glossaries define the term without degrees; the citation *"V.21
(Dykes, Fig. 98)"* is false — Fig. 98 is *"Speed relative to apogee"*. VII.5 fn. 203 confirms the
wells are in V.21. Against a shoot: cost and the fact that the values may well be right.

**Engine today.** `WELLED_DEGREES` (`:4329`) feeds Special Degrees (`:4375`) and Favor & Recompense
(`:2928`, `:2960`); the `1240-01-04` fixture exists because it marks Capricorn 22 a Well.

**What changes.** Measured: **16.9% of placements sit in a Well** — so a wrong cell changes a
displayed flag and the Favor & Recompense trigger on roughly one placement in six. Until shot,
the honest label is "unattested".

**Cost.** A shoot of one chapter; then a pin in the base-tables style.

**Unblocks.** Favor & Recompense's provenance; the base-table audit's one open row (`08` §5).

**Recommendation.** **Shoot it — high confidence.** It is the only load-bearing table with no
authority in hand, and the fix is a page.

---

## D-11 — Lot of death: from Saturn or from the Ascendant?

**Question.** Project the Lot of death (Moon → degree of the eighth) from Saturn, as printed, or
from the Ascendant, as Sahl's manuscripts read?

**Both sides.** Printed text: *"taken by night and day from the Moon to the degree of the eighth
place, and cast out from Saturn"* (*Nat.* 8.6, 1). fn. 89: *"Reading with the Māshā'allāh MSS for
'Ascendant.' This is the Lot as reported by Dorotheus (Carmen IV.3, 16)."* So Saturn has three
witnesses (Māshā'allāh's own treatise, Dorotheus, Dykes's edition); the Ascendant has Sahl's two
manuscripts.

**Engine today.** `:4056–4061`: `project='Saturn'`, presented as the text's ("PROJECTED FROM
SATURN, not the Ascendant").

**What changes.** The Lot's **sign changes in 93% of charts** between the two projections. One row
of the Topical Lots table.

**Cost.** One line, or a second row / switch.

**Unblocks.** Nothing queued.

**Recommendation.** **Keep Saturn, label it an emendation — medium-high confidence.** The
emendation rests on the source Sahl was copying and on Dorotheus; the note should stop calling it
Sahl's own words.

---

## D-12 — The Head's 12° orb

**Question.** Keep 12° for the Head as well as the Tail in weakness (99)?

**Both sides.** For both nodes at 12°: *"if she is with the Head or Tail in [one] sign, there being
less than 12° between them"* (*Intro* Ch. 3, 107); *"they are with the Head or Tail [of the Moon's
Dragon], and between them are 12° or less"* (VII.6, 52; the Sun's own orb is 4°, ¶53). For the
Tail only: *"if it was with the Tail, being distant from it by 12°"* (*Nat.* 1.21, 12), while ¶11
gives the Head no orb — and 1.21 is about the house-master's *years*, not weakness.

**Engine today.** `:5121–5124`: 12° for either node with |latitude| < 1°, citing Ch. 3, 107 **and**
1.21, 12.

**What changes.** Nothing numeric under the recommendation. If the Head were dropped: **3.6% of
placements** lose the label (the Tail fires on 3.7%).

**Cost.** One string.

**Unblocks.** Nothing.

**Recommendation.** **Keep 12° for both; drop 1.21, 12 from the citation — high confidence.** Two
sources give both nodes the orb; the Tail-only passage is about something else.

---

## D-13 — Chart-relative benefic/malefic (C-15)

**Question.** Should a malefic that rules the Ascendant have its penalty softened?

**Both sides.** *"that infortune was good for him, because the infortunes are perhaps more fitting
for him, since [one] may be the lord of the original Ascendant"* (*Choices* Ch. 1, 12). Four
sentences later: *"the infortunes are unjust in nature … there is no escape from their injustice"*
(*Choices* Ch. 1, 16–17).

**Engine today.** `FORTUNES`/`INFORTUNES` are fixed sets (`:4395–4396`); every malefic test is
absolute.

**What changes.** A malefic rules the Ascendant in **32% of charts** (Aries, Scorpio, Capricorn,
Aquarius rising). With the switch on, that malefic's afflictions in those charts are graded down —
across Sahl's weakness (94–95), Abū Ma'shar's misfortune (48–50), enclosure, and the Moon's lists.

**Cost.** One function (a "fitting infortune" predicate) and a radio.

**Unblocks.** C-15.

**Recommendation.** **Switch, default off — high confidence.** Sahl contradicts ¶12 in the same
chapter; a default would take the weaker of his two statements.

---

## D-14 — Advancement matched to the nature of the matter (C-14)

**Question.** Suppress the withdrawing penalty when the significator's topic is one of departure?

**Both sides.** *"if the question was about the nature of retreating, such as travel, moving, a
detained person's exit from his prison, and being released from sorrows, then look for these
matters from the place of retreat and withdrawal"* (*Questions* Ch. 1, 18–20). Sahl states it in a
horary frame and never restates it for nativities; the strength testimony (83) is unconditional in
*Intro* Ch. 3, 83.

**Engine today.** Testimony 83 "Advancing" is an unconditional positive (`:4923–4925`); no
topical modifier exists.

**What changes.** Measured: **29% of all placements are withdrawing**; the lord of the 3rd, 9th or
12th is withdrawing in **30–32% of charts** each. Option (b) would remove the penalty for those
lords in those charts.

**Cost.** A note (a); or a topical significator model (large) for (b).

**Unblocks.** C-14.

**Recommendation.** **(a) note only — medium-high confidence.** The doctrine is general in form but
attested only for questions, and the project's standing preference is the narrower reading.

---

## D-15 — Mars's western orb: 15° or 18°?

**Question.** Keep Abū Ma'shar's 15° for Mars going under the rays on the western side, or offer
Sahl's 18°?

**Both sides.** *"westernizing … until there are 22° between Saturn and Jupiter and [the Sun] …
(and 18° between Mars and [the Sun]) … in the degrees of setting until there come to be 15°
between them and the Sun"* (VII.2, 30–31) — Mars's under-the-rays band starts at 15°. Sahl's table
(*Nat.* 1.22, Dykes's table `:1113–1115`): Mars *"westernizes at 18°"*, and fn. 175 works his
western figure to about 18°. The two authors differ on this one cell; both agree on 18° east.

**Engine today.** `SOLAR_RAYS_ORB['Mars'] = (18.0, 15.0)` (`:731`); the comment now attributes the
15 to Abū Ma'shar alone (corrected 2026-09-08).

**What changes.** Mars between 15° and 18° west of the Sun: "westernizing" today, "under the rays"
under Sahl — a solar-phase label and the weakness/strength tests that read it. Rare (a 3° band on
one planet, roughly 1% of Mars placements).

**Cost.** One line, plus a sidebar radio if offered — the pattern of `MOON_RAYS_ORB`.

**Unblocks.** Nothing.

**Recommendation.** **Keep 15, add the switch — medium confidence.** The Moon already has one for
the same kind of disagreement; consistency argues for it, and nothing argues for changing the
default.

---

## D-16 — 9th-house Mercury: the Guide's columns or its content?

**Question.** The Reference Guide (p. 34) prints Mercury's 9th-house PN4 cells against its own
headings — *Good/of sect*: *"Bad reports and journeys; defamed in religion, bad assets and
commerce"*; *Bad/contrary*: *"Good journeys, true visions, good religious reputation, good reason
and management"*. Follow the printed columns or the evident content?

**Both sides.** The Guide is the authority the prose-table pins hold the code to (`09` §5), which
argues for the columns as printed. The content is plainly swapped, which argues for the code's
current reading. PN4 itself is not in the corpus, so the swap cannot be checked at source.

**Engine today.** `PLANETS_IN_HOUSES[9]['Mercury']` = Good *"Priests, wizards; good journeys, true
visions."*, Bad *"Seers, sacrificers; defamed in religion, bad assets."* — the sensible way round;
the pin holds it and the docstring says so (`09` §3).

**What changes.** Mercury is in the 9th in **8.6% of charts** (two of the six fixtures:
`1240-09-18`, `1240-10-05`). Under "columns", those charts' Good and Bad readings swap.

**Cost.** One string either way; a pin update.

**Unblocks.** Nothing.

**Recommendation.** **Content (current), annotated — medium confidence.** A transcription authority
that contradicts itself on one row is not evidence for the row; but this is a decision *about the
Guide*, and PN4 would settle it.

---

## D-17 — Per-topic reassignment of the angles (C-23)

**Question.** Implement *On Questions*' per-topic house tables (eight figures) or caveat only?

**Both sides.** *"the Ascendant indicates the doctor, the Midheaven indicates the sick person, the
seventh sign indicates the illness, and the fourth sign indicates the medicine"* (*Questions* Ch.
6, 2, Fig. 37), and a full twelve-house war scheme (7.7, 91–101). Against implementing: the engine
is natal; *Intro* Ch. 2, 4–29 fixes the house meanings, and no text reconciles the two.

**Engine today.** Fixed house significations throughout.

**What changes.** Nothing numeric under the caveat.

**Cost.** A note; a large model otherwise.

**Unblocks.** C-23.

**Recommendation.** **Caveat only — high confidence.**

---

## D-18 — Which spear-bearing definition, if any?

**Question.** Choose among the three definitions in the corpus — or none until the TNAC course
material is read?

**Both sides.** (A) *Nat.* 2.5, 2–3: mutual square/sextile with both dignified, or same sect — no
luminary required. (B) *Nat.* 10.2.1, 10 (Ptolemy): *"the planets were eastern from the Sun and
western from the Moon"*, in or configured to the stakes. (C) *Nat.* 10.2.7's seven examples:
earlier degree for the Sun (*"without a connection from him to them, and without their position
being at sunrise"*), later degree for the Moon, luminary angularity optional (fn. 206, 208), with
4.15, 4 fn. 213's Sun/Moon asymmetry. The glossary: *"several types and definitions."* Full record
in `01_on_nativities.md` §9.

**Engine today.** Nothing; VII.2, 12 and 17–18 name the solar-phase bands that make a planet
*"suitable for … spear-bearing"* and the engine records that band as a strength (25).

**What changes.** A new finding table; no existing number.

**Cost.** A subsystem, and three of them if all definitions are exposed.

**Unblocks.** The spear-bearing items of `04_tier1_and_spearbearing_report.md`.

**Recommendation.** **None yet — high confidence that no definition should be chosen from the
corpus alone.** The three give different answers on ordinary charts; the course material named as
the possible arbiter has not been opened, and it is the cheapest next step.

---

## Method note for the frequencies

Charts: 400 random (`random.Random(20260908)`; year 1200–2000, day 1–28, hour 0–24, latitude −50 to
+60, longitude −120 to +120) through `calculate_traditional_chart`, plus the six `CHARTS` dates at
Florence. Burned-path and Node figures are over the seven planets' placements (2,842). The
Māshā'allāh condition used whole-sign aspects (infortune conjunct/square/opposite the lord; fortune
in any aspect). The ¶63 overlap ran `evaluate_non_reception` and `evaluate_reception` under
`doctrine(SAHL)` and matched Kind II/IV pairs against reception rows by (received, receiver). No
engine code was changed to obtain any figure.
