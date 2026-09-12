# Phase 3 — the change list

Ranked by **(source clarity × wrongness) ÷ effort**. Each item gives its Phase 2 class, the verbatim
source sentence, what the code does now with `app.py:LINE`, the concrete change, and **the fixture
that would prove it** — positive case and negative control, in the style of
`tests/test_doctrine_fixtures.py` (`test_<name>` / `test_<name>_control_<negation>`).

**Nothing here is implemented.** This is a reading pass; `app.py` is untouched.

Items marked **⟨CHOICE⟩** are interpretive, not corrections. The alternatives are named.

---

# Tier 1 — do first (high clarity, high wrongness, trivial effort)

## C-01 — `NOT_IMPLEMENTED_COVERAGE` states a falsehood about the corpus ★ highest

**Class 3.** Source clarity: maximal. Wrongness: maximal (the claim is simply untrue and is shown to
users). Effort: one string.

**Source:** the chapter exists — `abu_mashar_book_vii.md:1812–1857`, AM VII.7, ¶1–22, pp. 485–487,
fns. 247–253.

> "All of the masters of the stars have mentioned the casting of the planets' rays…" — AM VII.7, 1

**Code now** — `app.py:4150`:

> `("Abu Ma'shar VII.7", "The casting of rays according to Ptolemy. The chapter begins on a page not photographed.")`

**Change:** rewrite the entry. VII.7 is complete; what is absent is the **tables** it assumes —
hourly times (*hōriaioi chronoi*, fn. 250: "special tables in the *Almagest*") and the
ascensions↔degrees inverse tables (fn. 251) — all computable. The entry should also carry ¶22
(the opposition ray needs no tables) and the ¶18/¶21 anchor asymmetry.

**Fixture:**

```python
def test_coverage_does_not_claim_an_unphotographed_chapter_that_exists():
    # Positive: no NOT_IMPLEMENTED_COVERAGE entry may say a chapter is
    # unphotographed when the corpus carries page markers for it.
    entry = _coverage_entry("Abu Ma'shar VII.7")
    assert "not photographed" not in entry.lower()

def test_coverage_control_vii6_degree_table_is_still_absent():
    # Negative control: the VII.6, 13/36 entry claims "No table for them in
    # this corpus," and that remains TRUE -- verified 2026-09-07 by grep over
    # consolidated_texts/. This entry must NOT be rewritten.
    entry = _coverage_entry("Abu Ma'shar VII.6, 13 and 36")
    assert "No table for them in this corpus" in entry
```

The control is the point: it stops a blanket sweep of the coverage list from deleting entries that
are still correct.

---

## C-02 — The advancing comment is now partial: *On Times* names the schemes and Sahl takes a side

**Class 3.** Source clarity: high (prose + Figure 44). Wrongness: incompleteness, not error.
Effort: comment only.

**Source:**

> "and this position of the circle indicates **slowness and delay, according to the statement of the
> ancients**. **12** And as for Māshā'allāh, indeed **he differs from them** … (and it is what is
> from the degree of the fourth), [then] turned back towards the Midheaven … **14** And that is **the
> closest of the two statements**." — *On Times* Ch. 1, 11–14

**Figure 44** (p. 233) shows both wheels; I read the image. Left = quadrants (ASC→MC and DSC→IC
quick). Right = hemispheres (rising half quick).

**Code now** — `app.py:4152–4156`, `app.py:4284–4332`. Frames the quadrant sense as Abū Ma'shar's,
distinct from Sahl's stake/succedent sense. Both true; neither mentions that **Sahl knew the
quadrant scheme, attributed it to "the ancients," and preferred Māshā'allāh's hemispheres**.

**Change:** extend the comment block at `app.py:4284` with the *On Times* attribution. **No
behaviour change** — and the caveat belongs in the comment: *On Times* Ch. 1 is about quickness of
**timing**, not strength, so it does not by itself license a third strength scheme.

**Fixture:** none. Documentation. The negative control is that `ADVANCING_BY_QUADRANT_FIG90` and
every testimony-(83) verdict are byte-identical before and after.

---

## C-03 — Cite Sahl's own glossary instead of the external course glossary

**Class 3 (citation quality).** Effort: two strings.

**Source:**

> "**Advancement, advancing** … Refers to being (1) **dynamically angular or succeedent, i.e. moving
> by primary motion toward an axial degree**." — `sahl_glossary.md` p. 771

**Code now** — `app.py:4728` and the note at `app.py:7026` cite "the course glossary" (*TNAC Course
Glossary*, external to the corpus).

**Change:** cite `sahl_glossary.md` p. 771, in the primary volume. Keep the TNAC reference if
wanted; the point is that the claim no longer depends on a document outside the corpus.

**Fixture:** none (string change). Control: no computed value moves.

---

# Tier 2 — cheap, well-attested, genuinely new behaviour

## C-04 — Dark signs and the burned place: the two categories attested identically in two works

**Class 1.** Source clarity: maximal — **stated twice, in two separate works, verbatim identical**.
Effort: two constants.

**Source:**

> "of them are signs which are said to be dark, and they are **Libra and Capricorn**." — Intro Ch. 1, 18
> "The signs of darkness are **Libra, Capricorn**." — Nat. Ch. 1.38, 8
>
> "of them is a place called the 'burned place,' and it is **the end of Libra and the beginning of
> Scorpio**." — Intro Ch. 1, 19
> "And the burned place of the signs is **the end of Libra and the beginning of Scorpio**." — Nat. Ch. 1.38, 9

**Code now:** `grep -ci "burnt\|combusta\|dark sign"` → **0**. Neither exists.

**Change:** add `DARK_SIGNS = {'Libra', 'Capricorn'}` and report the burned place **as Sahl states
it — without degrees**. See ⟨CHOICE⟩ C-05 for the degree question.

**Fixture:**

```python
def test_dark_signs_are_libra_and_capricorn(engine):
    assert engine["DARK_SIGNS"] == {"Libra", "Capricorn"}

def test_dark_signs_control_scorpio_is_not_dark(engine):
    # Negative control: Scorpio adjoins the burned place and is NOT a dark
    # sign in either witness. The two categories are separate.
    assert "Scorpio" not in engine["DARK_SIGNS"]
```

---

## C-05 ⟨CHOICE⟩ — The burned place has no degrees in Sahl; the glossary gives two competing spans

**Class 1 + interpretive.** Source clarity for the *span*: **low, deliberately**.

**Source — Sahl gives no degrees at all** (both witnesses above). The only degrees in the corpus:

> "**Some astrologers** identify it as between **15° Libra and 15° Scorpio**; **others** between the
> exact degree of the fall of the Sun in **19° Libra** and the exact degree of the fall of the Moon
> in **3° Scorpio**." — Glossary p. 774

Neither is attributed to Sahl.

**Alternatives:** (a) no degrees — report the sign boundary only, which is all Sahl says;
(b) 15° Libra – 15° Scorpio; (c) 19° Libra – 3° Scorpio.

**Recommendation: (a) by default, with (b) and (c) as switch options** — matching how this project
already handles the Moon-rays split (`app.py:6433`) and the domain rule (`app.py:536`).

**Fixture:**

```python
def test_burned_place_default_reports_no_degree_span(engine):
    # Positive: the default reading is Sahl's own -- a sign boundary, not a span.
    assert engine["BURNED_PLACE_SPAN"] is None

def test_burned_place_control_switch_offers_both_named_spans(engine):
    # Negative control: neither named span may become the silent default.
    assert set(engine["BURNED_PLACE_OPTIONS"]) == {None, (195.0, 225.0), (199.0, 213.0)}
```

---

## C-06 — Crooked/straight signs, latitude-dependent

**Class 1.** Source clarity: high for the base rule (Sahl's own prose), high for the inversion
(**Figure 3 + glossary, two independent statements**). Effort: one function; latitude is already in
the chart data.

**Source:**

> "the ones **straight in rising are from Cancer to the end of Sagittarius** … arises in more than
> two equal hours … **6** And those **crooked in rising are from Capricorn to the end of Gemini** …
> arises in less than two equal hours" — Intro Ch. 1, 5–6

> "**In the northern hemisphere**, the signs from Capricorn to Gemini are crooked (**but in the
> southern one, straight**); those from Cancer to Sagittarius are straight (**but in the southern
> one, crooked**)." — Glossary p. 776

And **Figure 3** (p. 41), whose two halves each carry both labels (N. lat. / S. lat.) — read
directly.

**Code now:** `grep -ci crooked` → **0**.

**Change:** `is_straight_in_rising(sign, latitude)`, inverting below the equator. Cite Intro Ch. 1,
5–6 for the base rule and **Figure 3 + glossary p. 776** for the inversion — *not* Ch. 1, 5–6, which
states only the northern case.

**Frequency:** affects **100% of southern-hemisphere charts** — every sign's classification flips.
Analytically, 6 of 12 signs are straight in either hemisphere, so a naive northern-only rule is
wrong for **every placement in a southern chart**.

**Fixture:**

```python
def test_cancer_is_straight_in_the_north(engine):
    assert engine["is_straight_in_rising"]("Cancer", lat=51.5)   # London

def test_crooked_straight_control_inverts_in_the_south(engine):
    # Negative control: the SAME sign at a southern latitude must invert.
    # This is the whole content of Figure 3 and glossary p. 776; a northern-
    # only implementation passes the first test and fails this one.
    assert not engine["is_straight_in_rising"]("Cancer", lat=-33.9)  # Sydney
```

⚠ Note the tension with *Choices* Ch. 2, 5, which calls Cancer "most intense in **crookedness**" —
against this rule. Dykes proposes (fn. 11) that Sahl means the *ruling planet's* quickness, not
ascensional quickness. That reconciliation is Dykes's, not Sahl's; do not encode it.

---

## C-07 — Two one-line rules from Appendix A

**Class 1.** Source clarity: good (but see the appendix-wide caveat). Effort: minimal.

> "The testimonies of the **connection of the Moon** with a planet are **stronger in the Ascendant or
> the Midheaven**." — Appendix A ¶14 [S14]

> "The **harm of the Nodes to the inferior planets is more powerful** than their harm to the superior
> planets." — Appendix A ¶67 [S66]

**Code now:** zero citations to Appendix A anywhere. The Node machinery exists (the Moon's nodes are
computed; `app.py:4145` records that other planets' nodes are not).

**Change:** two graded labels.

⚠ **Carry the provenance.** Appendix A rests on **one consulted manuscript** (Nuruosmaniye 2785/3),
patched from the Latin *Propositions of al-Mansūr*. Weaker than *On Nativities* or the
*Introduction*. Label accordingly.

**Fixture:**

```python
def test_node_harm_is_greater_for_the_inferiors(engine):
    # Positive: Venus with the Head takes the stronger grade.
    fig = pdata(Venus=(100, VENUS), Saturn=(100, SAT), Node=(100, NODE))
    rows = engine["evaluate_node_harm"](fig)
    assert _grade(rows, "Venus") > _grade(rows, "Saturn")

def test_node_harm_control_superiors_are_not_exempt(engine):
    # Negative control: S66 says the inferiors are harmed MORE, not that the
    # superiors are unharmed. Saturn must still be graded, just lower.
    fig = pdata(Saturn=(100, SAT), Node=(100, NODE))
    assert _has(engine["evaluate_node_harm"](fig), Planet="Saturn")
```

The control guards the exact failure mode the brief warns about — turning "more powerful for X" into
"only for X."

---

# Tier 3 — moderate effort, high doctrinal value

## C-08 — Overcoming, superiority and decimation

**Class 1.** Source clarity: **high — three sources agree** (§4.6 of the reconciliation). Effort:
moderate; the sign-distance machinery already exists at `_pairwise_configurations`
(`app.py:905`).

**Source:**

> "And the aspect of the **second sextile is stronger than the first**, and the second square is
> stronger than the first square, and the second trine is stronger than the first trine (and this
> aspect is called '**superiority**')." — Intro Ch. 2, 59

> "**Overcoming.** When a planet is in the **eleventh, tenth, or ninth sign** from another planet
> (i.e., in a superior sextile, square, or trine); being in the **tenth sign is considered
> decimation**, a more domineering or even harmful position." — Glossary p. 787

> "Right … aspects are those **earlier in the zodiac** … For example, **if a planet is in Capricorn,
> its right aspects will be towards Scorpio, Libra, and Virgo**" — Glossary p. 791

**Code now:** `grep -ci "overcom\|superiority\|decimat"` → **0**. Aspects are computed
undirectionally.

**Change:** add dexter/sinister to each configured pair; label the 11th/10th/9th-from relation as
overcoming, and the 10th case as decimation.

**Frequency:** of the 12 whole-sign relations, 6 are non-conjunction non-opposition aspects, so
**every aspecting pair except conjunctions and oppositions carries a direction** — roughly 75% of
configured pairs gain a label.

**Fixture — use the glossary's own worked example, which is free:**

```python
def test_glossary_capricorn_right_aspects(engine):
    # Glossary p. 791: a planet in Capricorn casts RIGHT aspects toward
    # Scorpio, Libra and Virgo -- the 11th, 10th and 9th from it.
    assert engine["aspect_side"]("Capricorn", "Scorpio") == "right"
    assert engine["aspect_side"]("Capricorn", "Libra") == "right"
    assert engine["aspect_side"]("Capricorn", "Virgo") == "right"

def test_glossary_capricorn_control_left_aspects(engine):
    # Negative control, from the same sentence: Pisces, Aries and Taurus are
    # LEFT. A sign-distance implementation that forgets direction passes
    # nothing here.
    for s in ("Pisces", "Aries", "Taurus"):
        assert engine["aspect_side"]("Capricorn", s) == "left"

def test_overcoming_is_the_left_caster(engine):
    # A planet in Scorpio is in the 11th from Capricorn, so it OVERCOMES the
    # Capricorn planet -- and casts its aspect leftward onto it.
    assert engine["overcomes"]("Scorpio", "Capricorn")

def test_decimation_is_the_tenth_only(engine):
    # Libra is the 10th from Capricorn: decimation. Scorpio (11th) overcomes
    # but does NOT decimate.
    assert engine["decimates"]("Libra", "Capricorn")
    assert not engine["decimates"]("Scorpio", "Capricorn")
```

⚠ Carry Dykes's fn. 46 warning: Sahl uses "first/second" the other way round in *Scito* Ch. 95, a
work outside this corpus and therefore uncheckable.

---

## C-09 — The three good-place schemes, and what each is *for*

**Class 1.** Source clarity: high for the sets (prose + Figures 5, 6, 7); **partly reconstructed for
the 7-place ranking** — see ⟨CHOICE⟩ below. Effort: moderate, mostly presentational.

**Source:**

> "Four of them are called the 'stakes' … And these stakes indicate **what is already present** …
> **33** four of them are said to be **what follows the stakes** … **34** they indicate **what is
> coming to be** … **35** four of them are said to be **falling from the stakes** … **36** they
> indicate **what has already elapsed**" — Intro Ch. 2, 31–36 *(the 8-place system; **Figure 5**)*

> "the strongest of the places … is the **Ascendant** … **38** Then the **Midheaven** … **39** Then
> the stake of the **west** … **40** Then the stake of the **earth** … **41** Then the **eleventh** …
> **42** Then the **ninth** … because it is the house of the joy of the Sun. **43** Then the
> **fifth** … **44** these seven places are praised" — Intro Ch. 2, 37–44 *(**Figures 6, 7**)*

And the glossary explains why both exist without either being wrong:

> "The **seven-place** scheme … advantageous **for the *native*** … The **eight-place** scheme …
> advantageous **for a planet *in itself***." — Glossary p. 771

**Code now** — `app.py:4618`: `EXCELLENT_PLACES = {1, 4, 5, 7, 10, 11}`, from *Introduction* Ch. 3,
78 (stakes + succedents ∩ places that look at the Ascendant). **That derivation is correct** and the
comment at `app.py:4611–4617` states it well. But it is one of at least three schemes Sahl gives,
and the other two are Ch. 2's.

**Change:** add the 8-place and 7-place schemes as named, separately-labelled readings; do not merge
any of them into a single house-strength number. Attach the glossary's "for the native / for the
planet itself" distinction to the UI so the difference is legible rather than looking like a bug.

**⟨CHOICE⟩** The 7-place *ranking* is a Dykes conflation. fn. 42: **B** reads 11, **5, 9**;
**H** and **L** read 11, **9, 5**; the printed text takes H/L's order **plus** B's Sun's-joy note.
Alternatives: `1,10,7,4,11,9,5` (printed) or `1,10,7,4,11,5,9` (**B**).

**Fixture:**

```python
def test_the_three_schemes_are_distinct_sets(engine):
    assert engine["EIGHT_PLACE"]     == {1, 2, 4, 5, 7, 8, 10, 11}   # Ch.2, 31-36; Fig. 5
    assert set(engine["SEVEN_PLACE_RANKED"]) == {1, 10, 7, 4, 11, 9, 5}  # Ch.2, 37-44; Fig. 6
    assert engine["EXCELLENT_PLACES"] == {1, 4, 5, 7, 10, 11}        # Ch.3, 78

def test_scheme_control_the_eighth_house_splits_them(engine):
    # Negative control, and the whole reason both schemes exist: the 8th is
    # a strong place FOR A PLANET (8-place) and "intense misfortune" for the
    # NATIVE (Ch.2, 46). Any merge into one score destroys this.
    assert 8 in engine["EIGHT_PLACE"]
    assert 8 not in engine["SEVEN_PLACE_RANKED"]
    assert 8 not in engine["EXCELLENT_PLACES"]

def test_scheme_control_the_ninth_splits_ch2_from_ch3(engine):
    # And the 9th separates Ch.2's seven from Ch.3's six: cadent, but it
    # looks at the Ascendant and carries the Sun's joy.
    assert 9 in engine["SEVEN_PLACE_RANKED"]
    assert 9 not in engine["EXCELLENT_PLACES"]
```

---

## C-10 — The joys: four, and two of them weak

**Class 1.** Source clarity: **mixed, and that is the finding**. Effort: small.

| Place | Joy | Attestation |
|---|---|---|
| 9th | Sun | Intro Ch. 2, 42 — **manuscript B only** (fn. 42) |
| 3rd | Moon | Intro Ch. 2, 45 — Arabic |
| 6th | Mars | Intro Ch. 2, 48 — **supplied from the Latin**, printed in `⟨ ⟩` (fn. 43) |
| 12th | Saturn | Intro Ch. 2, 49 — Arabic |

**Code now:** `grep -ci "joy"` → **0**.

**Change:** add the four **with their attestation grades**. **Do not add Mercury's (1st) or Venus's
(5th)** — they are not in this chapter, and a seven-joy display would be exactly the pattern
completion the brief forbids.

**Fixture:**

```python
def test_corpus_supports_exactly_four_joys(engine):
    assert set(engine["JOYS"]) == {3: "Moon", 6: "Mars", 9: "Sun", 12: "Saturn"}

def test_joys_control_mercury_and_venus_are_absent(engine):
    # Negative control: Intro Ch.2 gives no joy for the 1st or the 5th. The
    # familiar seven-joy scheme is NOT in this corpus.
    assert 1 not in engine["JOYS"] and 5 not in engine["JOYS"]

def test_joys_control_two_are_marked_weakly_attested(engine):
    # The 9th/Sun is manuscript B only; the 6th/Mars is Latin-supplied.
    assert engine["JOY_ATTESTATION"][9] == "manuscript B only"
    assert engine["JOY_ATTESTATION"][6] == "supplied from the Latin"
```

---

## C-11 ⟨CHOICE⟩ — The contradicted sign categories: expose both, merge neither

**Class 1 + interpretive.** Source clarity: **each list is clear; the pair is contradictory.**
Effort: small per category.

### Four-footed

> "those having four feet: and they are **Aries, Taurus, and the beginning of Capricorn, and the end
> of Sagittarius**." — Intro Ch. 1, 13 *(Dykes's fn. 5: "But see Nativities Ch. 1.38, 1.")*
>
> "Gemini, Libra, and Aquarius have two feet; **Aries, Leo, Taurus have four feet**; and the ⟨first⟩
> half of Sagittarius has two feet, and the other has four feet." — Nat. Ch. 1.38, 1

Leo is in one, Capricorn in the other. **The union is in neither.**

### Voice

> "**half a voice**: Capricorn, Aquarius, and **Virgo**. **21** … [full] voices: Aries, Taurus,
> Gemini, Leo, Libra, Sagittarius. **22** … do not have a voice: Cancer, Scorpio, Pisces."
> — Intro Ch. 1, 20–22 *(three classes)*
>
> "**powerful voice**: Gemini, **Virgo**, and Libra. **26** … **balanced** voice … Aries, Taurus,
> Leo, and Sagittarius. **27** … **weak** of voice … Capricorn and Aquarius. **28** … do not have a
> voice … Cancer and its triplicity." — Nat. Ch. 1.38, 25–28 *(four classes)*

**Virgo moves from the bottom class to the top.**

### Barren

Aries barren in Intro Ch. 1, 23 only; Sagittarius barren in Nat. 1.38, 16 only. (And Nat. ¶17
contradicts its own ¶15 on Capricorn/Aquarius, reported as a competing opinion.)

**Change:** implement each as **two named readings selected by work**, never a union. This has a
consumer inside the corpus: Appendix B ¶7 and ¶33 both branch on the four-footed list.

**Fixture:**

```python
def test_four_footed_differs_by_work(engine):
    assert "Leo" in engine["FOUR_FOOTED"]["On Nativities"]
    assert "Leo" not in engine["FOUR_FOOTED"]["Introduction"]
    assert "Capricorn" in engine["FOUR_FOOTED"]["Introduction"]
    assert "Capricorn" not in engine["FOUR_FOOTED"]["On Nativities"]

def test_four_footed_control_no_merged_list_exists(engine):
    # Negative control -- the failure mode the brief names. No reading may
    # contain BOTH Leo and Capricorn; that union is in neither witness.
    for reading in engine["FOUR_FOOTED"].values():
        assert not {"Leo", "Capricorn"} <= set(reading)

def test_voice_virgo_flips_class_between_works(engine):
    assert engine["VOICE"]["Introduction"]["Virgo"] == "half"
    assert engine["VOICE"]["On Nativities"]["Virgo"] == "powerful"
```

---

## C-12 — Triplicity humors and directions

**Class 1.** Source clarity: high (prose ¶34–41, and **Figure 4** agrees cell for cell). Effort:
data only. The triplicity **lords** are already implemented; the other two columns are not.

| Triplicity | Humor | Direction |
|---|---|---|
| ♈♌♐ | yellow bile | east |
| ♉♍♑ | black bile | **south** |
| ♊♎♒ | blood | **west** |
| ♋♏♓ | phlegm | **north** |

**Code now:** `grep -ci humor` → **0**.

⚠ **Two humor schemes now exist in the corpus and they attach to different things**: Sahl assigns
humors to **triplicities** (above); Abū Ma'shar VII.9 assigns them to **planets** (Saturn black bile,
Mars yellow bile, Venus and Moon phlegmatic). Not a contradiction — different carriers — but a
"humor" field must say which. Note that **no planet is assigned blood** in VII.9.

**Fixture:**

```python
def test_triplicity_directions_are_not_the_modern_mapping(engine):
    # Positive: Sahl's directions, from Intro Ch.1, 34-41.
    assert engine["TRIPLICITY_DIRECTION"]["Fire"]  == "east"
    assert engine["TRIPLICITY_DIRECTION"]["Earth"] == "south"
    assert engine["TRIPLICITY_DIRECTION"]["Air"]   == "west"
    assert engine["TRIPLICITY_DIRECTION"]["Water"] == "north"

def test_humor_control_planet_and_triplicity_schemes_are_separate(engine):
    # Negative control: Sahl's humors are on triplicities, Abu Ma'shar's on
    # planets. Blood has a triplicity (Air) but NO planet in VII.9.
    assert "blood" in engine["TRIPLICITY_HUMOR"].values()
    assert "blood" not in engine["PLANET_HUMOR_VII9"].values()
```

---

# Tier 4 — larger, or scope-gated

## C-13 — Abū Ma'shar VII.9: planetary natures and significations

**Class 1.** Source clarity: high. Effort: **large but mechanical** (data entry, ~34 paragraphs).

Temperaments table at `01_abu_mashar_vii_7_to_9.md` §C2. Three features that a flat qualities table
would destroy:

- **Saturn is given two temperaments in one sentence** — "cooling, drying, black bile … **but
  sometimes it is cooling [and] wet**" (VII.9, 3).
- **Mercury is both convertible and fixed** — "inclines to the natures of the planets and signs he
  mixes with, [although] **an equal balance of dryness and coldness is in him**" (VII.9, 23).
- **The Moon's heat is derivative** — "in her is **incidental** heat, **because her glow is from the
  Sun**" (VII.9, 33).

⚠ VII.9, 2 must be displayed with the lists:

> "**not everything we state in this chapter** … will be gathered together within a single man …
> according to **the condition of the planet in itself and its condition in the houses of the
> circle**."

⚠ Eight passages are textually unstable (§C4), one of which reverses meaning (¶9: "inclination
**towards** them" vs Lemay's "hostile to them"). Mark them.

**Fixture:**

```python
def test_saturn_carries_both_temperaments(engine):
    assert engine["PLANET_NATURE"]["Saturn"]["primary"] == ("cold", "dry")
    assert engine["PLANET_NATURE"]["Saturn"]["alternate"] == ("cold", "wet")

def test_nature_control_no_other_planet_has_an_alternate(engine):
    # Negative control: Saturn is the ONLY planet VII.9 gives two
    # temperaments to. Mercury's duality is a different shape (convertible
    # plus a fixed balance), not a second temperament.
    alts = [p for p, v in engine["PLANET_NATURE"].items() if v.get("alternate")]
    assert alts == ["Saturn"]
```

---

## C-14 ⟨CHOICE⟩ — Advancement matched to the nature of the matter

**Class 2.** Source clarity: high for the sentence; **its reach beyond horary is the open question.**
Effort: note (small) or topical modifier (large).

> "if you were asked about a sought matter, and it was **in the nature of advancing** … **20** But if
> the question was about **the nature of retreating, such as travel, moving, a detained person's exit
> from his prison, and being released from sorrows**, then look for these matters **from the place of
> retreat and withdrawal**." — *Questions* Ch. 1, 18–20

**Code now** — `app.py:4722–4747` scores testimony (83) "Advancing" as an unconditional positive.

**⟨CHOICE⟩** (a) note only — surface the qualification where advancement is explained;
(b) topical modifier — suppress the advancement penalty for 3rd/9th/12th significators.

**Recommendation: (a).** ¶18–20 is stated in a horary frame and Sahl does not restate it natally.
The doctrine is general in form, but "general in form" is not the same as attested for nativities,
and this project's standing preference is the narrower reading.

**Fixture (if (b) were taken):**

```python
def test_withdrawing_is_not_penalised_for_a_travel_significator(engine):
    rows = engine["evaluate_strength"](fig, topic="travel")
    assert not _has(rows, Label="Withdrawing (83)", Planet="Jupiter")

def test_advancement_control_still_penalises_for_an_acquisition_topic(engine):
    # Negative control: 18 names advancement for matters of arrival. The
    # SAME withdrawing placement must still be penalised for the 2nd.
    rows = engine["evaluate_strength"](fig, topic="assets")
    assert _has(rows, Label="Withdrawing (83)", Planet="Jupiter")
```

---

## C-15 ⟨CHOICE⟩ — Benefic/malefic as chart-relative

**Class 2.** Source clarity: **contested inside Sahl's own chapter.** Effort: moderate.

> "that infortune **was good for him**, because the infortunes are perhaps **more fitting for him**,
> since [one] may be **the lord of the original Ascendant**" — *Choices* Ch. 1, 12

Against, four sentences later:

> "the infortunes are **unjust in nature** … there is **no escape from their injustice**"
> — *Choices* Ch. 1, 16–17

**⟨CHOICE⟩** (a) leave absolute (current); (b) soften the malefic penalty when the malefic rules the
Ascendant. **Given ¶16–17, this must be a switch, not a default.**

**Fixture:**

```python
def test_fitting_infortune_softens_when_it_rules_the_ascendant(engine):
    # Saturn rules the Ascendant (Capricorn rising) and squares the Moon.
    with engine["reading"]("fitting_infortune", True):
        assert _grade(engine["evaluate"](fig), "Saturn square Moon") > BASELINE

def test_fitting_infortune_control_off_by_default_and_unchanged_elsewhere(engine):
    # Two negative controls: the switch is OFF by default (Ch.1, 16-17), and
    # even ON it must not soften a Saturn that rules nothing in the chart.
    assert engine["reading_default"]("fitting_infortune") is False
    with engine["reading"]("fitting_infortune", True):
        assert _grade(engine["evaluate"](fig_saturn_rules_nothing), "Saturn square Moon") == BASELINE
```

---

## C-16 ⟨SCOPE GATE⟩ — Abū Ma'shar VII.7, the ray-casting algorithm

**Class 1.** Source clarity: high for the procedure; **one internal asymmetry unresolved**. Effort:
**large** — the whole ascensional apparatus.

**Blocked on a decision, not on sources.** fn. 247 calls this "primary directions," which is deferred
territory; what it *computes* is a static chart quantity. Both readings are laid out at
`01_abu_mashar_vii_7_to_9.md` §B8. **This is the user's call, and it should be made explicitly.**

If taken, three things travel with it:

1. **The ¶18/¶21 anchor asymmetry** — ¶18 says add to the *nearest* of the two candidate positions,
   ¶21 to the *more distant*. Unexplained. Test both.
2. **The framing** — VII.7, 1–2 says the tradition disagrees and this is **Ptolemy's** method, not
   Abū Ma'shar's own verdict. It may not be labelled "Abū Ma'shar's rule."
3. **It unblocks two currently-absent items** that need ascensional degrees: *Fifty Aphorisms* 45
   (the decided ascensional correction) and *On Nativities* Ch. 2.13, 48–51 (the three 15°
   ascensional bands) — both currently in `NOT_IMPLEMENTED_COVERAGE`.

**The one free piece, independent of the gate:**

> "as for the opposition, [a planet] casts its ray into the opposition of its sign, **in the same
> degree and minute**." — VII.7, 22

This **confirms** existing behaviour rather than changing it — the code already computes oppositions
zodiacally. Its real value is as evidence that VII.7 treats the *other four* aspects as **not**
zodiacally exact, which is a substantive difference from the VII.5 scheme the code implements. Worth
a source note; not a change.

---

## C-17 — Appendix A's remaining natal conditions, and Appendix B's matrix

**Class 1.** Effort: large. Source clarity: **weakest in the corpus.**

~23 conditions in Appendix A (`01_appendices_a_and_b.md` §A2); the three-axis handing-over lookup in
Appendix B (§B1–B2).

⚠ **Provenance caveats that must ship with any of it:** Appendix A = one consulted manuscript patched
from a Latin centiloquy. Appendix B = **no source photographs exist anywhere in the project**, five
`⟨missing⟩`/`[uncertain]` marks, two "meaning unclear" footnotes, and no partition between natal,
horary and solar-revolution material.

**Two items must not be implemented at all:**

- **Appendix A ¶35 [S35]** — the detested-connection pairs. Dykes prints the tidy opposite-domicile
  scheme (Mars–Venus, Jupiter–Mercury, Sun–Saturn) over irregular manuscript readings, on his own
  admission that his version is "**astrologically more appropriate**." The regularity is the reason
  to distrust it.
- **Appendix A ¶64 [S64]** — "in one [and the same] of the circles parallel to the meridian … or in a
  corresponding path … it is **the most preferable aspect**." Dykes: "*This sounds like being in the
  same declination, but I would expect a different word for that; **perhaps** it means that they are
  each equidistant from the meridian in right ascension?*" A strong claim whose referent its own
  translator cannot fix. **Above all, it must not be folded into the antiscia family.**

**Fixture (the guard, which is the useful part here):**

```python
def test_antiscia_pairs_remain_five(engine):
    # The standing rule, now under new pressure: the glossary supplies the
    # antiscia FORMULA (p. 772) and Appendix A 64 gestures at a meridian
    # relation. Neither licenses a sixth sign pair.
    assert len(engine["EQUAL_DAYLIGHT_PAIRS"]) == 5

def test_antiscia_control_aquarius_scorpio_absent(engine):
    assert frozenset({"Aquarius", "Scorpio"}) not in engine["EQUAL_DAYLIGHT_PAIRS"]
```

---

# Ranked summary

| # | Item | Class | Clarity | Wrongness | Effort | Choice? |
|---|---|---|---|---|---|---|
| **C-01** | VII.7 coverage entry is false | 3 | max | max | trivial | |
| **C-02** | Advancing comment: *On Times* names the schemes | 3 | high | partial | trivial | |
| **C-03** | Cite Sahl's glossary, not the course glossary | 3 | high | low | trivial | |
| **C-04** | Dark signs + burned place | 1 | max (2 works) | absent | trivial | |
| **C-05** | Burned-place degree span | 1 | **low** | absent | small | ⟨CHOICE⟩ |
| **C-06** | Crooked/straight, latitude-dependent | 1 | high | absent | small | |
| **C-07** | Appendix A ¶14, ¶67 | 1 | medium | absent | trivial | |
| **C-08** | Overcoming / decimation | 1 | high (3 sources) | absent | moderate | |
| **C-09** | Three good-place schemes | 1 | high (+recon.) | partial | moderate | ⟨CHOICE⟩ on the ranking |
| **C-10** | The four joys | 1 | mixed | absent | small | |
| **C-11** | Contradicted sign categories | 1 | each clear, pair contradictory | absent | small | ⟨CHOICE⟩ |
| **C-12** | Triplicity humors + directions | 1 | high | absent | trivial | |
| **C-13** | VII.9 natures + significations | 1 | high | absent | large | |
| **C-14** | Advancement matched to the matter | 2 | high sentence, open reach | — | small–large | ⟨CHOICE⟩ |
| **C-15** | Chart-relative benefic/malefic | 2 | contested | — | moderate | ⟨CHOICE⟩ |
| **C-16** | VII.7 ray-casting | 1 | high | absent | **large** | ⟨SCOPE GATE⟩ |
| **C-17** | Appendices A and B in bulk | 1 | **weakest** | absent | large | partly forbidden |

## What not to do

Collected, because each is a live temptation created by this corpus:

1. **Do not add the sixth antiscia pair.** The glossary's formula (p. 772) is not the pair list.
2. **Do not merge the four-footed, voice or barren lists** across Sahl's two works.
3. **Do not present a seven-joy scheme.** The corpus has four, two weakly.
4. **Do not print a degree span for the burned place as Sahl's.** He gives none.
5. **Do not implement Appendix A ¶35's pairs** — Dykes's tidy reconstruction over irregular
   manuscripts.
6. **Do not implement Appendix A ¶64** — its own translator cannot identify the configuration.
7. **Do not merge the good-place schemes** into one house-strength number.
8. **Do not encode the *namūdār*** (`DOCTRINAL_CAVEATS.md`); a glossary definition of what it is for
   is not a method.
9. **Do not treat Figure 47's Mercury row as data** — it contradicts its own prose in the printed
   book (verified against the photograph). Prefer *On Times* Ch. 3, 16.

---
---

# ADDENDUM — changes arising from the previously-omitted chapters

*On Times* Chs. 4–11, *On Choices* Chs. 3–13 and *On Questions* Chs. 2–18 have now been read.
Eight new items, and three amendments to items above. Same ranking basis.

## Amendments to existing items

| Item | Amendment |
|---|---|
| **C-02** | **Strengthened.** The hemisphere division is not confined to a timing chapter — Sahl **uses** it operationally in a second work (*Choices* Ch. 6, 16–17 and 6, 30). Still comment-only: no passage applies it to *strength*. |
| **C-04, C-06** | **Strengthened.** Crooked/straight and the burned path have **downstream consumers inside the corpus** (*Choices* Ch. 3, 18; Ch. 7, 22; Ch. 3, 6 and 3, 9). They are not inert categories. |
| **C-09** | **Extended to four schemes.** *Choices* Ch. 9, 12–13 gives excellent = **1, 10, 11**, corroborating the glossary's hedge — and **demotes the 7th and 4th**, both stakes. Add to the fixture. |
| **C-10** | **Fixture must change.** *Choices* Ch. 7, 11 has "let Venus always be in her exaltation, house, triplicity, or **joy**" — Sahl **presupposes Venus has a joy without locating it**. Assert "four **located**," not "exactly four exist." |
| **C-05** | *Choices* Ch. 9, 41 adds "in Libra, if she went beyond **10°**" — a third burned-path datum matching **neither** glossary span. Add as a third named alternative or, better, as evidence for option (a), no span. |

---

## C-18 — ★ The quantified testimony rule, with "safe" defined by enumeration

**Class 1.** Source clarity: **high — stated once, plainly, with the definition inline.**
Effort: moderate. This is the most directly implementable new doctrine in the whole pass.

> "**three testimonies** … the **lord of the Ascendant, the lord of the sought matter, and the
> Moon**. **49** … one of the two is safe, he will attain to **one-third** … **50** … two
> testimonies … **two-thirds**. **51** And if all … were **safe from retrogradation, burning, the
> infortunes, and falling** … **all** of what he sought. **52** And if … they were **received** …
> it will **add good on top of that**." — Questions Ch. 1, 48–52

**Code now:** `grep -ci "one-third|two-thirds"` → **0**. No fractional outcome scale exists.

**Change:** a "safe" predicate over the four named afflictions, and a thirds count over the three
testimonies. ⚠ Note this is a **question**-chart rule; for a natal engine its value is chiefly the
**definition of "safe"**, which is wider than the glossary's.

**Fixture:**

```python
def test_safe_requires_all_four_freedoms(engine):
    # Questions Ch.1, 51 enumerates: retrogradation, burning, the infortunes, falling.
    assert engine["is_safe"](direct=True, burned=False, afflicted=False, cadent=False)

def test_safe_control_each_affliction_alone_breaks_it(engine):
    # Negative control, four ways -- the glossary's Safe (p.791) names only the
    # infortunes, so an implementation built from the glossary passes the
    # positive test and fails two of these four.
    for kw in ("retrograde", "burned", "afflicted", "cadent"):
        assert not engine["is_safe"](**{**SAFE_BASE, kw: True}), kw

def test_thirds_scale(engine):
    assert engine["attainment_fraction"](safe_count=1) == pytest.approx(1/3)
    assert engine["attainment_fraction"](safe_count=2) == pytest.approx(2/3)
    assert engine["attainment_fraction"](safe_count=3) == pytest.approx(1.0)

def test_thirds_control_reception_is_additive_not_a_fourth_testimony(engine):
    # 52 makes reception "add good on top of that" -- it must not raise the
    # count above three or become a fourth testimony.
    assert engine["attainment_fraction"](safe_count=3, received=True) == pytest.approx(1.0)
```

---

## C-19 — ★ Figures 33/34: the corpus's only dated, located, fully worked chart

**Class 1 (fixture, not behaviour).** Source clarity: **maximal.** Effort: small — the data is
given. **This is the highest-value item in the addendum**, because it tests machinery the engine
already has rather than adding any.

**Source** — Questions Ch. 1, 54 gives nine positions; Figure 34 gives the reconstruction
(**5 July 824 AD Julian, 3:18:10 AM LMT −02:57:40, Baghdad 44e25'/33n21, "Sassanian" zodiac, whole
signs**). Full table and the nine judgments at `01_on_questions.md` §2.

**Every judgment Sahl draws survives the MS-vs-modern discrepancy** (Venus is 6° out, but Sahl draws
no judgment from Venus). And ¶65's claim that Jupiter is with the Tail — **absent from ¶54's listed
data** — is confirmed by the modern recomputation, which independently validates the reconstruction.

**Change:** add as a golden fixture alongside the existing `test_figN_*` set.

⚠ **Use the stated longitudes as inputs; do not recompute from the date.** Figure 34 uses a
**Sassanian** (sidereal) frame, and recomputation would import an ayanamsha question the fixture
does not need.

**Fixture:**

```python
# Questions Ch.1, 54: Sahl's own worked question about authority.
SAHL_AUTHORITY = pdata(Asc=(80.0,), MC=(330.0,), Sun=(102,SUN), Moon=(167,MOON),
                       Mercury=(87,MERC), Mars=(38,MARS), Venus=(123,VENUS),
                       Jupiter=(350,JUP), Saturn=(66,SAT))

def test_sahl_authority_moon_opposes_jupiter_applying(sahl):
    # 57: "the Moon ... connecting with Jupiter from an opposition."
    row = _pair(sahl, SAHL_AUTHORITY, "Moon", "Jupiter")
    assert row["aspect_name"] == "Opposition" and row["Motion"] == "Applying"

def test_sahl_authority_mercury_separated_from_jupiter(sahl):
    # 56: "I found the lord of the Ascendant separated from the lord of the
    # sought matter." Mercury 27 Gemini is past Jupiter's 20 Pisces square.
    row = _pair(sahl, SAHL_AUTHORITY, "Mercury", "Jupiter")
    assert row["Motion"] == "Separating"

def test_sahl_authority_moon_is_in_the_fourth(sahl):
    # 57: "found her in the stake of the earth." Virgo, from a Gemini Asc.
    assert sahl["get_wsh_house"](167.0, 80.0) == 4

def test_sahl_authority_control_venus_is_not_load_bearing(sahl):
    # Negative control and the reason this fixture is safe: the MS gives Venus
    # 3 Leo, the modern recomputation 9 Leo. Sahl draws NO judgment from her,
    # so no assertion here may depend on her position.
    assert "Venus" not in _planets_named_in(SAHL_AUTHORITY_JUDGMENTS)
```

---

## C-20 — ⟨CHOICE⟩ The general dignity ranking, which disagrees with *On Nativities*

**Class 1 + interpretive.** Source clarity: each statement clear; **they conflict.**
Effort: small.

> "And the **triplicity is below the house**, and likewise the **bound below the triplicity**, and
> the **face below the bound**." — Questions Ch. 13, 7

**Code now:** no dignity-strength ordering constant exists.

⚠ Three orderings, and `app.py:4160` already quotes the second:

| Source | Order | Context |
|---|---|---|
| Questions Ch. 13, 7 | house > triplicity > bound > face *(exaltation unplaced)* | a planet's rank |
| **Nativities Ch. 1.20, 2** | **bound** > house > exaltation > triplicity > image | **house-master** selection |
| Glossary p. 777 | domicile > exaltation > triplicity > bound > face | general listing |

**The bound is first in one and third in another.** Contexts differ, so this is plausibly not a flat
contradiction — but it must not be flattened into one constant.

**Fixture:**

```python
def test_dignity_orderings_are_kept_separate_by_context(engine):
    assert engine["DIGNITY_ORDER"]["Questions 13, 7"]   == ["house","triplicity","bound","face"]
    assert engine["DIGNITY_ORDER"]["Nativities 1.20, 2"] == ["bound","house","exaltation","triplicity","image"]

def test_dignity_control_no_merged_ordering_exists(engine):
    # Negative control: no reading may put the bound both first and third.
    # And the Questions chain must NOT silently gain an exaltation slot --
    # 13, 7 does not place it.
    assert "exaltation" not in engine["DIGNITY_ORDER"]["Questions 13, 7"]
```

---

## C-21 — "Upright" stakes

**Class 1.** Source clarity: **high for Sahl's sentence; three sources disagree on the scope.**
Effort: small. Figure 32 illustrates it.

> "the stakes are **upright**: that is, if the Midheaven **is the tenth sign**, and the Midheaven is
> **not the ninth sign** nor the stake of the earth the third." — Questions Ch. 1, 47

**Code now:** no "upright" concept.

⚠ Sahl excludes only the **9th**; the glossary (p. 796) excludes the **9th and 11th**; Dykes's
fn. 25 **allows** the 11th. **Implement Sahl's**, and name the other two in the note.

**Fixture:**

```python
def test_upright_requires_the_mc_in_the_tenth_sign(engine):
    assert engine["stakes_are_upright"](mc_whole_sign_house=10)

def test_upright_control_ninth_fails_but_eleventh_is_not_excluded_by_sahl(engine):
    # Sahl's sentence excludes the 9th and says nothing about the 11th. The
    # glossary excludes both; Dykes's fn.25 allows the 11th. This control
    # pins the implementation to Sahl rather than to the glossary.
    assert not engine["stakes_are_upright"](mc_whole_sign_house=9)
    assert engine["UPRIGHT_READING"] == "Questions Ch.1, 47 (excludes the 9th only)"
```

---

## C-22 — The three approaches are a ranked fallback

**Class 1 (display).** Source clarity: high. Effort: trivial.

> "**And if there was not anything of what I mentioned**, then look for a transfer … **And if you do
> not find** a planet … then look for a collection … So from these **three approaches** comes the
> judgment of all sought matters." — Questions Ch. 1, 26–30

**Code now:** `evaluate_transfers_of_light` (`app.py:1512`) and `evaluate_collections_of_light`
(`app.py:1585`) are reported independently and unconditionally.

**Not a bug** — showing everything is right for a study tool. **Change: record the precedence in the
UI note**, so the student knows Sahl consults them in order. No computation change.

**Fixture:** none (display). Control: both evaluators keep returning all rows.

---

## C-23 — ⟨CHOICE⟩ The per-topic reassignment of the angles

**Class 1 + interpretive.** Source clarity: high (eight figures). Effort: **large** if implemented;
**trivial** as a caveat.

> "the **Ascendant indicates the doctor**, the **Midheaven indicates the sick person**, the
> **seventh sign indicates the illness**, and the **fourth sign indicates the medicine**."
> — Questions Ch. 6, 2 *(Figure 37)*

Plus a full twelve-house war scheme (Ch. 7.7, 91–101, Figure 41) and six more figures.

⚠ In tension with *Introduction* Ch. 2, 4–29's **fixed** house significations. The natural
reconciliation (Ch. 2 as default, per-topic tables as overrides) is **stated in neither text**.

**Recommendation: caveat only.** The engine is natal; per-topic horary house tables have no natal
application. What is worth saying is that fixed house meanings are one topic's assignment.

---

## C-24 — Two one-line general rules

**Class 1.** Effort: trivial.

> "the infortunes' looking at the Ascendant is **easier than their looking at the Moon**."
> — Choices Ch. 9, 8

> "if you found the **lord of the Ascendant or the Moon in the place of the sought thing** … it will
> be accomplished, **unless the Ascendant was the fall of the lord of the sought thing, or it was
> burned up in it**." — Questions Ch. 1, 24

The first is a stated precedence between the two chief significators; the second a pair of vetoes
already matching the glossary's *Not-reception*, now sourced from the primary text — with fn. 22's
exception attached: *Introduction* Ch. 3, 61 requires the other planet have **no dignity** in the
connecting planet's sign, "otherwise this would be a case of **reception**."

---

## C-25 — ⚠ Do not source a victor-in-questions doctrine to Sahl

**Class 3 (provenance guard).** Effort: a note.

Dykes, after Questions Ch. 1:

> "the **1493 Latin version** … has a short paragraph 'On the corruption of the Ascendant,' which is
> attributed to **Māshā'allāh** and describes the use of **some kind of victor in questions**. But it
> **evidently did not appear in the Arabic manuscripts of Sahl**."

Given that this engine is named for the victor (*almuten* / *mubtazz*), record explicitly that
whatever victor doctrine it implements **cannot be sourced to *On Questions***. The glossary's
*Victor* entry (p. 796) and *On Nativities* remain valid sources; the Latin paragraph does not.

---

## Revised "what not to do" list

Adding to the nine above:

10. **Do not merge the dignity orderings** — bound-first (Nativities 1.20, 2, house-master) and
    bound-third (Questions 13, 7, general rank) belong to different questions.
11. **Do not implement either convertible-sign speed ranking.** Questions Ch. 9, 79 (Capricorn
    quickest, **Cancer slowest**) and Choices Ch. 2, 5 (**Aries and Cancer quickest**) invert on
    Cancer, and Dykes's proposed reconciliation cuts against Choices when applied.
12. **Do not take the glossary's "upright"** over Sahl's own narrower sentence.
13. **Do not cite Sahl for a victor in questions** — Latin accretion (C-25).
14. **Do not recompute Figures 33/34 from the date** — the frame is Sassanian; use the stated
    longitudes.
15. **Do not assert "the corpus has exactly four joys."** It **locates** four and **presupposes** a
    fifth (Venus's) without locating it.
