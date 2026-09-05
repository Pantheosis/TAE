# Verification of the Sol 5.6 code-conformance report (C01–C25) against `Executable/app.py`

Verified: 2026-09-05. Report under review: `/home/apothic/Downloads/Sol 5.6 Audit/claude_code_conformance_handoff_app3.md` (targets `app(3).py`, 5,881 lines).

## Read this first: the file moved while it was being verified

`app.py` was **edited and committed during this verification**. When I began it was 5,881 lines (byte-for-byte the state Sol audited, mtime 06:14). At 11:04 commit `2e277dd "Finish the directed-agency refactor; fix quadrants and blocking gates"` landed (+78/−19), and uncommitted edits continued to arrive afterward (5,940 → 5,953 → 6,044 lines by the time I stopped; `git status` shows `M app.py`). Consequences:

- **Five of the six P0 claims (C01–C05) were fixed by `2e277dd` while I was checking them.** They are classified STALE/FALSE below *against HEAD*, but they were accurate against the file Sol audited. I re-traced each fix rather than taking the commit message on trust; the traces are in the sections.
- **Line numbers in this document are from a single grep taken late in the session (file at ~6,014 lines) and may already be off by tens of lines.** Every citation also names the function and quotes the exact snippet, so locate by those, not by number.
- `python3 -m py_compile app.py` passed at every snapshot I took (5,881 / 5,940 / 5,953 lines), including the last.

I did not edit `app.py` or any other file except this report.

## Summary

| Classification | Count | Claims |
|---|---:|---|
| CONFIRMED BUG | 7 | C11 (narrow), C16, C19, C20 (one citation only), C22 (minor), C24 (narrow), C25 (minor) |
| ALREADY-CONSIDERED, DEFENSIBLE | 7 | C06, C07, C08, C17, C18, C21, C23 |
| OPEN QUESTION | 6 | C09, C10, C12, C13, C14, C15 |
| STALE/FALSE | 5 | C01, C02, C03, C04, C05 — all fixed in `2e277dd` (11:04) after Sol's report was generated |
| NOT VERIFIABLE HERE | 0 | (the Swiss-Ephemeris-dependent items were all decidable by static tracing; no live-app run was needed for any verdict) |

None of the seven confirmed bugs is a core-doctrine defect on the scale of the original P0 items. Ranked by effect on chart output they are: C11 > C16 > C22 > C25 > C19 > C24 > C20 (see the closing list).

Sources consulted (OCR Markdown in `/home/apothic/Desktop/Fifty Aphorism OCR Project/`): `aspect_conditions_final/sahl_introduction_ch3.md`, `aspect_conditions_final/abu_mashar_book_vii.md`, `on_nativities_final/on_nativities.md`. Quotations below are from those files.

---

## P0

### C01 — "Sahl connection uses the wrong planet's orb" — **STALE/FALSE (fixed in `2e277dd`)**

**What Sol described was true of the audited file.** At the 5,881-line state, `_is_connected_sahl()` read `light = PLANETARY_ORBS.get(row['light_name'], 7.0)` and used it for all three branches. Trace of Sol's fixture (natural light Moon, natural heavy Saturn, directed applicant Saturn, 10° applying): orb = Moon's 12 → `10 <= 12` → **True**. Sol's expected asymmetric answer was False (Saturn's 9).

**Why this was a genuine defect and not the "dissenting reading" the docstring defends.** The long docstring (still present, `_is_connected_sahl`, ~1108–1170) argues *asymmetric vs reciprocal* orbs — whether either planet's light suffices — and cites 19, 6, 10 against 13 and 18 plus the 5,405-pair statistic. That argument is sound and untouched. But it is a different question from the one Sol raised. The docstring's own first sentence is "The APPLYING planet's own light governs", and the applying planet is the directed `row['applicant']` that `_pairwise_configurations()` computes at "2b. Who is actually approaching whom" — which the function never read. So on the ~4% of pairs where applicant ≠ light_name the file asserted one rule and ran another. The commit message for `2e277dd` says exactly this ("asserted the corrected doctrine and implemented the superseded one").

**Current code (HEAD):**
```
if row['motion'] == 'Applying':
    actor = row['applicant'] or row['light_name']          # ~1187
    return remaining <= PLANETARY_ORBS.get(actor, 7.0)
if row['signs_apart'] == 0:
    return remaining <= PLANETARY_ORBS.get(row['light_name'], 7.0)   # ~1195, §10 "THE LIGHT ONE departs ... one-half of ITS body"
return remaining <= 1.0                                     # ~1199, §9 flat degree, no owner named
```
Re-trace of Sol's fixture: actor = Saturn, orb 9, `10 <= 9` → **False**. Ordinary Moon→Saturn unchanged. The per-branch ownership (applicant for application; standing light for same-sign separation because §10 says "the light one"; nobody for §9's cross-sign degree) is exactly what Sol's sketch asked the implementer to decide, and each branch now carries its citation. The out-of-sign body strike at "4. Sahl's out-of-sign connection by body" already used the striking planet's own orb (`gap <= PLANETARY_ORBS.get(earlier, 7.0)`), so it was consistent before and after.

**Recommendation:** nothing further; add the fixture as a regression test when a test suite exists. The sidebar help (~5631ff) still says "the applying planet's OWN light governs", which is now true.

### C02 — "Handing-over reverses directed agency" — **STALE/FALSE (fixed in `2e277dd`)**

Audited state: `fast, slow = r['light_name'], r['heavy_name']` (old 1701). Sol's fixture (directed Saturn→Moon) emitted Moon→Saturn. This was a real defect by the file's own lights, twice over: (a) `_pairwise_configurations()` quotes the note on Fifty Aphorisms #19, "it would only be possible for Saturn to be the one HANDING OVER if he is retrograde" — the file's own cited authority that handing-over is directed; (b) `evaluate_returning()` reads §67 as directed ("67 names the mover as the one handing over. So the subject is the applicant") while `evaluate_handing_over()`, the function that implements §67, did not.

Current: `fast, slow = r['applicant'] or r['light_name'], r['receiver'] or r['heavy_name']` (~1760) with a comment citing 67 and 76. Power and Nature are then tested on `fast`'s own position, which meets Sol's acceptance criteria.

Sol's second point — Management is emitted for *separating-but-still-connected* pairs — is **ALREADY-CONSIDERED**: the docstring states "Management (76, 'any application or connection hands over management') is the unconditional baseline for every Connected pair." That "any application or connection" wording is Dykes' footnote 90 on §73 ("In 76, Sahl says that any application or connection hands over management"), so the paraphrase is sourced. Exposing motion on the row would be a harmless UI addition, not a correction.

### C03 — "Blocking Type I omits the blocker → target connection" — **STALE/FALSE (fixed in `2e277dd`)**

Audited state: Type I required `speed[blocked] > 0 and speed[blocker] > 0` and `applying(blocked, target)` only; `applying()` tested motion alone. Sol's fixture (blocker separating from target) emitted a block. Reproduced by trace.

Current: an additional gate `if not applying(blocker, target): continue` (~1674), and `applying()` itself now requires direction and connection (see C04). Hand-trace of Sahl's Fig. 13 (Moon 8, Mars 10, Saturn 12 Gemini): Moon→Saturn 4° ≤ Moon's 12 (Sahl) / ≤ 15 assembly (Abu); Mars→Saturn 2° ≤ Mars's 8 / 15 → both legs pass under both profiles, block emitted. Separating-middle variant now returns nothing.

One honest caveat for the record: I could not find the blocker→target requirement *stated* in either source. Sahl 35 and Abu 91 both say only that the middle one "blocks the one with the fewest degrees from connecting with the heavy one, until it passes by it", and Abu's own example (92: Saturn 20°, Mercury 15°, Venus 20° Aries) has the middle and heavy bodies at the same degree, which Dykes' fn. 173 calls inverted and declines to use. The new gate is therefore a conservative reading ("a middle planet already separating from the target is moving out of the way, not standing in it"), not a literal one — it reproduces both worked figures and it is documented in place, so I have no objection, but it should not be described as source-mandated.

### C04 — "Blocking Type II omits connection gates and uses natural roles" — **STALE/FALSE (fixed), with one sub-demand defensibly declined**

Sol's three sub-points against the audited file, and their current status:

1. *Neither leg had to satisfy `_is_connected()`.* Now the **body leg** does: `applying()` (~1630–1638) returns `_is_connected(r)` after checking motion and direction, and Type II calls `applying(uniting, heavy)` (~1718). The **looking leg is still gated on `row['motion'] == 'Applying'` only** (~1703). That is correct and Sol's "both legs must meet the active author's connection rule" would be a regression: Sahl's own Fig. 14, which the docstring reproduces (Moon 10° Scorpio, Mars 15° Taurus, Saturn 23° Taurus), has the Moon 13° from exact opposition to Saturn — outside her 12° light under Sahl and outside Abu's 12° aspect limit. Gating the looking leg would make the author's worked figure return nothing. (Mars→Saturn at 8° passes Sahl's 8 exactly and Abu's 15, so the body-leg gate keeps Fig. 14 positive.)
2. *`looking, heavy = row['light_name'], row['heavy_name']`.* Now `row['applicant'] or ..., row['receiver'] or ...` (~1707).
3. *`applying(a, b)` did not verify `a` is the applicant.* Now `if (r['applicant'] or r['light_name']) != a: return False` (~1636).

Sol's reproduction ("both legs outside both authors' limits still emits a block") no longer reproduces, because the body leg must now be connected.

### C05 — "Whole-sign house is used as a quadrant" — **STALE/FALSE (fixed), one residual OPEN sub-point**

Confirmed against the source before the fix landed. Sahl 88 defines the quarters by the *angles*, not by signs: "the masculine quarters of the Ascendant (and they are from the Midheaven to the Ascendant, and from the fourth to the seventh) ... feminine ... (from the seventh to the Midheaven, and from the Ascendant to the fourth)". The audited file computed `quadrant_house` at the top of `evaluate_strength_of_planets()` and then tested WSH `house` for §88 (old 3971–3974); `evaluate_abu_mashar_condition()` did the same for §§28/29/45/46 via `in_masculine_quadrant = house in MASCULINE_QUADRANT_HOUSES` (old 4423). The constants' comment ("In Whole-Sign-House terms") was a project translation, not a source reading.

Current: `_q88 = (... quadrant_house in MASCULINE_QUADRANT_HOUSES ...)` (~4131) and `quadrant_house = get_effective_house(lon, natal_houses); in_masculine_quadrant = quadrant_house in ...` (~4585–4586). §88's two clauses are now one entry (`_q88 or _s88` → single label), which also settles the C22 sub-point for §88.

**Residual open point (Sol's own fourth bullet):** the fix uses `get_effective_house()` — the 5°-carryover version — for the gender-quadrant test, with no recorded reason for choosing it over `get_house_number()`. Sol explicitly asked that this be decided rather than assumed. It is a defensible choice (the carryover is a stakes rule and the gender quadrants are bounded by the stakes) but it is undocumented at the call sites. Also, Abu Ma'shar's quadrant definition is in Great Introduction VI.26, which is not in the OCR corpus (Book VII only), so the Abu half rests on the constants' comment rather than on text in hand.

### C06 — "One UI profile creates cross-author hybrid doctrines" — **ALREADY-CONSIDERED, DEFENSIBLE**

The exact concern is written down at the reception site in `evaluate_abu_mashar_condition()` (~4450ff): "That is a live doctrinal choice, not a detail ... 43's 'not received' therefore fires on about 81% of placements under the Sahl profile against about 8% under Abu Ma'shar's -- a ten-fold swing ... It is left profile-driven deliberately, because the sidebar's own help text says every downstream table reads that setting, and comparing the two authors across the whole app is the point of having the switch." The sidebar help (~5655) says "Everything downstream -- transfer, collection, blocking, handing over, reception -- reads this setting", and the affected table headers carry the active rule in their titles (e.g. "Reception — {CONNECTION_PROFILE} rule"). Sahl-only material (§§56–57 reception, non-reception) already keys on `sahl = CONNECTION_PROFILE == 'Sahl'` and `_sahl_body_row()`.

Sol's `DoctrineProfile` refactor is an architecture preference, not a correctness finding; the hybrid is disclosed, labelled, and intentional. If the owner later wants author-pinned canonical tables, the cheapest path is a per-evaluator `profile=` argument defaulting to the global, not a rewrite.

---

## P1

### C07 — "Split Sahl banishment from Abu Ma'shar wildness" — **ALREADY-CONSIDERED, DEFENSIBLE**

`evaluate_wildness()` docstring: Sahl's "banished" (64) "doesn't explicitly frame this as whole-sign Aversion to everyone -- that sharper ... definition is a later refinement (Dykes' footnote there ...) that Abu Ma'shar's ... VII.5, 79-82 reflects, and which this function implements." The body then reports the one case where the two definitions demonstrably diverge — an out-of-sign body connection (20–21) — as a `Note` on the row: "Wild by Abu Ma'shar's whole-sign definition only ... so it is not 'banished' by Sahl's own wording at 64" (~1526). The UI header names both (~6014).

Sol's stronger claim — that Sahl's "none of the planets connects to" should be read as *degree*-connection, so that a planet with sign-aspects but no live connection is "banished" — is not supported by the source apparatus: Dykes' fn. 86 on §64 says "This seems to be an early form of 'wildness,' described in ITA III.10 as a state in which a planet lacks any planets even *looking* at it (i.e., it is in aversion to all other planets)." Separate booleans would be a presentation choice; there is no textual defect here.

### C08 — "Reflection Type I is only unbound geometry" — **ALREADY-CONSIDERED, DEFENSIBLE**

The docstring already says what Sol wants said: "for a natal (non-topical) chart there's no 'sought matter' to reflect toward, so this reports which Whole-Sign House(s) the collector's own further aspects reach, for the reader to interpret" (~1539). The row label is `'I (Collection)'` with detail "...its own rays reach houses [...]". Renaming to "Potential reflection geometry" and accepting a nominated target are cosmetic/feature requests. No defect.

### C09 — "Require a current connection or label simulations as candidates" — **OPEN QUESTION**

Sol is right that the forward-sim evaluators start from any *applying* whole-sign configuration without `_is_connected()`, and right that some of the sources say "connecting". But the sources do not all say it, and the code records no position either way:

| Evaluator | Source wording | Gate in code | Assessment |
|---|---|---|---|
| Revoking (`evaluate_revoking`, ~2024) | VII.5 117: "a planet **is connecting** with a planet, but before it reaches it, it retrogrades" | Applying only | Ungated, no rationale recorded. Under Abu's own §27 a planet 40° from exact is not yet "connecting". Real tension. |
| Cutting Type II (~2332ff) | 123: "a light planet **is connecting** with a planet heavier than itself" | Applying only | Same tension. |
| Cutting Type I | 121: "a planet **wants** a connection" | Applying only | Defensible as-is. |
| Resistance (~2050) | 118: "**wanting** a connection with the heavy one" | Applying only; comment "T must actually want H" | Defensible as-is. |
| Escape (~2127) | 119: "**going towards** the connection" | Applying only | Defensible as-is. |

So the actionable part is two evaluators (Revoking, Cutting II). Either gate them on `_is_connected(r)` under the active profile, or tag their rows "approaching candidate outside current connection" when not connected. Adding the gate is a one-line change each; the "candidate" tag preserves more information.

Horizon censoring: Sol's worry ("do not convert 'not found within 200 days' to 'does not occur'") is already handled where it matters. `_simulate_forward()`'s docstring: "A near-term cutoff, not an indefinite search -- a condition not found within the horizon is reported as 'none found'". Revoking searches only up to the station (which is inside the horizon by construction); Escape and Cutting I/II require the event to be found or skip the row. **The one place a censored search does become a positive** is Abu §44 emptiness of course in `evaluate_abu_mashar_condition()` (~4715): `exit_day = sign_exits[0] if sign_exits else sim['horizon_days']`, so a slow planet with no sign exit in 200 days and no perfection in 200 days is called empty of course. Worth a guard (`if not sign_exits: fall back to the present-tense proxy` or label the result "no perfection within 200 days").

### C10 — "Sahl §§56–57 are overgeneralized" — **OPEN QUESTION (rationale recorded, but thin; project policy favors Sol)**

The generalization is deliberate and documented twice (`evaluate_reception` docstring ~2523, and the §56 comment): "Sahl names the Moon in both, as he does throughout 49-57, but neither mechanism has anything lunar in it and 58 immediately widens the same shape to 'the Moon or the lord of the Ascendant,' so both are applied to any planet with the paragraph number on the row."

Two problems with that rationale. §58 widens to "the Moon or the lord of the Ascendant" — not to every planet — and §58 is the *non*-reception paragraph, so it is being used to license a generalization of two *reception* rules. And the project's own standing rule (per its memory notes) is "retain the narrower/original source's definition rather than a later author's expansion" — an inference from §58 is narrower still than an author's expansion. For §57 the sim horizon already excludes the slow planets, so in practice the generalized rows come from Sun/Mercury/Venus.

Sol's proposal (Moon-only by default; keep the generalized mode but mark it `inferred generalization`) is consistent with the project's own policy and cheap: a `planets = ['Moon']` default with the current loop kept behind a flag, and the row's `Grade`/`Direction` carrying "(inferred generalization)" when the planet is not the Moon.

### C11 — "Sahl §57 does not calculate emptiness of course or the next-sign interval correctly" — **CONFIRMED BUG (narrow: the next-sign bound)**

Two separate points in Sol's claim, one confirmed, one defensible.

**Confirmed — the after-ingress search is unbounded.** In the §57 block (~2780–2815): `ingress = exits[0]`, then for each other planet `target = _configuration_target_at(sim, planet, other, ingress + 0.05)` and `day = _perfection_day(sim, planet, other, target, after_day=ingress)` with **no `before_day`**. Sahl 57 says "she passed over into **the next sign** and connected with the lord of her first sign". The first perfection found after ingress can lie two or more signs later (realistic for Mercury/Venus/Sun; rare but possible for the Moon) and is still reported as "after the sign change". `_perfection_day()`'s whole-sign revalidation at the moment of perfection mostly self-limits this (the target computed at ingress will usually no longer match once the planet has moved on a sign), but not rigorously — if the other planet has also moved a sign the relation can match again. The fix is exactly Sol's step 5: compute the second exit (`exits[1]` if present, else skip/censor) and pass `before_day=second_exit`. Also, if `exits[1]` is absent the row should be censored rather than reported.

**Defensible — the emptiness test.** Sol wants a *prospective* no-perfection-before-exit test. That is Abu Ma'shar's definition (VII.5 78), and the file knows it: the Abu §44 comment (~4700ff) says "Sahl's own base concept (Ch.3, 63 ...) is present-tense: not currently connecting or uniting with any planet. Abu Ma'shar sharpens this into the real, prospective definition used here". §57 is Sahl's rule under Sahl's profile, and Sahl 63 reads "when the Moon is not connecting with any of the planets, and not uniting with one" — present tense. Using the present-tense test in a Sahl-owned rule is the source-faithful choice. One inconsistency to note: the §57 test uses `_connected()` (any connected pair, applying *or separating*), whereas the Moon-defect [9] "wild" test for the same §63 concept (~5183) requires applying-and-connected. Sahl's "not connecting ... and not uniting" reads as application; the two Sahl-owned tests should agree.

### C12 — "Implement Abu Ma'shar's recovered reception expansion (§§134–142)" — **OPEN QUESTION (coverage gap; claim accurate)**

Verified in the OCR: §§134–142 are present (`abu_mashar_book_vii.md` ~1550–1560), including 134's harmonious-sign "acceptance" (Dykes fn. 209: "a more general sense of ... 'reception' which is *not* based on dignities"), 135 (fortunes accept each other; Mars and Saturn from assembly/sextile/trine), 136–142 (strong/middling/below grades, Sun–Moon, Mercury in Virgo, mutuality). `evaluate_reception()` implements 129–133 only and says so. This is a scope decision for the owner, not a defect: nothing currently emitted is wrong, and Sol's own note that 134's final clause is corrupt argues for caution. If implemented, keep it as separate rows with `basis`/`grade`/`source_range` as Sol proposes — do not fold into the 129–133 grades.

### C13 — "Abu Ma'shar configurations still absent" — **OPEN QUESTION (coverage gap; claim accurate)**

Grep confirms: only VII.5 97–100 ("Two Natures") is acknowledged as unmodeled (in `evaluate_handing_over`'s docstring); §§29–31 (multiple-planet priority), §§38–52 (latitude), §§53–77 (natural/equal-ascension/sign-affinity), §§104–116 (returning tree) are referenced nowhere in `app.py`. The project memory records that Two Natures was *deliberately* dropped as Abu-only. A "not implemented" coverage panel is a fair, cheap ask; implementing the rest is a project decision.

### C14 — "Abu §8 uses the wrong definition of a fortunate Moon" — **OPEN QUESTION (already self-flagged in code)**

The function's own docstring (~4265ff) says it: "One exception, and it is inconsistent: 8's 'while the Moon is made fortunate' is still gated on zero of SAHL's ten defects. Reading 'fortunate' as 'zero defects' is this app's own -- in this chapter's vocabulary being made fortunate means satisfying 1-14 -- and on either list the Moon has no defects in under 1.5% of charts, so 8 almost never fires. Left as-is rather than replaced by another guess, but flagged." Gate at ~4402: `moon_corruption_count == 0`.

So Sol is re-raising a known, documented inconsistency; the code does not claim to be right. Sol's proposal (show both an `Abu-good-fortune` flag and an `uncorrupted` flag rather than using Sahl invisibly) is reasonable. Implementation note: the good-fortune conditions 1–14 for the Moon depend on reception rows and enclosure but not on §8 itself (which excludes the Moon), so a non-recursive helper is feasible by running the 1–14 block for the Moon first.

### C15 — "Abu enclosure has remaining directed-role issues" — **OPEN QUESTION (roles fixed; separating-leg gate is the residual)**

- *Natural `light_name`/`heavy_name` in Type 1's separating/connecting form*: **fixed in `2e277dd`** — now `(r['applicant'] or r['light_name']) == planet and (r['receiver'] or r['heavy_name']) == sep_t` (~3774–3777).
- *Separating leg still gated on `_is_connected(r)`* (~3775): **still true**, and the docstring makes it hard to defend — it calls this second form of §57 "Sahl's mechanism" ("that second form IS Sahl's mechanism"), and `_sahl_enclosed()` was corrected precisely on this point with a long comment (Fig. 25: the Moon 3° past Mars across a sign boundary, so "requiring _is_connected here made the chapter's own worked figure return nothing"). If the two forms are the same mechanism, the Abu branch should follow. Against that: there is no Abu worked figure for the separating form (Fig. 145 is the by-degree type), so nothing in *his* text forces the looser reading. A reviewer must decide; the code should at least say which reading it takes and why the two branches differ.
- *§61's dissolution extended to every by-sign-enclosed planet*: the comment (~3813ff) gives a reasoned defense (60 vs Dykes' note vs 61's bare look). It is an inference and could be labelled so on the row ("60-61, inferred"), but it is documented.

### C16 — "Via Combusta is from neither active source as implemented" — **CONFIRMED BUG (provenance/labeling)**

`evaluate_special_degrees()` flags `195.0 <= lon <= 225.0` (15° Libra–15° Scorpio, ~3605) with the bare label "Via Combusta" and a docstring that gives no source. Both authors' own spans are implemented *elsewhere* and correctly: Abu VII.6 40 ("in the burned path (and that is Libra and Scorpio) — and harsher ... from 19° Libra up to 3° Scorpio") at `in_burned_path = 180 <= lon < 240` / `in_harsh_burned_path = 199 <= lon < 213` in the Abu condition table (~4674–4679); Sahl 110 ("at the end of Libra and the beginning of Scorpio", fn. 120 noting the 19°–3° variant) at `199.0 <= lon < 213.0` in the Moon-defect list (~5179). The 15°–15° span is the later (Lilly-era) convention. The UI help (~5876) calls it "a historically 'burnt' span", which is not a source flag.

Fix: relabel the row "Via Combusta (conventional 15° Libra–15° Scorpio; not Sahl 110 / Abu VII.6 40, which are shown in their own tables)" or drop it in favor of the two sourced tests. Cheap; touches one string and one docstring.

### C17 — "Mars setting conflict must stay visible" — **ALREADY-CONSIDERED, DEFENSIBLE**

Verified both figures in the OCR. Abu VII.2 30: "until there are 22° between Saturn and Jupiter and [the Sun] in the west (and 18° between Mars and [the Sun])"; 31: "in the degrees of setting until there come to be 15°". On Nativities 1.22 with Dykes' fn. 175: "If Mars is at 22°, then after 7 days ... about 18° between them." The constants block records the conflict explicitly (~552–559): "Mars carried 22 here, which is his figure from Sahl's On Nativities 1.22 table, not from the chapter this constant cites." `solar_phase()` cites VII.2 for the setting band and uses 18. The choice is documented; per-source thresholds in the output would be a nicety.

### C18 — "Five-degree carryover is only an ecliptic approximation" — **ALREADY-CONSIDERED, DEFENSIBLE**

Sahl's own statement of the rule is in zodiacal degrees: Fifty Aphorisms #44, 88 (quoted above `get_effective_house`): "if the stake was 10 degrees of Aries, then indeed every planet which has less than 5 degrees between it and the stake, is truly counted as being in the stake." Dykes' phrase "as measured in diurnal motion, hence Sahl's reference to the 'rear' of the stake" explains the *direction* ("rear"), not a unit of measure. Subtracting ecliptic longitudes from cusps is the literal implementation of the example Sahl gives. (The 15°-past-the-stake rule in On Nativities 2.13, 48–51 *is* in ascensions, but that is a different rule and is not what this function implements.) An "ecliptic" caveat in the docstring would be harmless; a right-ascension rewrite is not required by the text.

### C19 — "Masha'allah delineation overstates corrupt text" — **CONFIRMED BUG (data fidelity, one cell)**

Verified. On Nativities (children chapter) 85: "The lord of the fifth in the eighth: [*illegible*] they will survive and will be miscarried.<sup>47</sup>". Fn. 47: "The word I have translated as 'miscarried' ... can also mean being very premature. The text here not only suffers the smudging found throughout E, but has a line from a faulty photographing process which runs directly across every word. Sahl probably means that his children will suffer or die, and those that do survive will be premature." `MASHAALLAH_LORDS[8][5] = "Children premature or miscarried"` (line 416) presents Dykes' conjecture as the text, with no uncertainty marker, while neighbouring cells are literal paraphrases.

Minimal safe fix without restructuring the whole table: change that one string to e.g. `"Text corrupt (illegible; Dykes' conjecture: children suffer or die, survivors premature)"`. The structured `{text, confidence, source_note}` record Sol proposes is the better long-term shape for the whole table (other cells in the corpus carry `[*uncertain*]` too), but this cell is the only one Sol identified and the only one I checked.

### C20 — "Lot metadata cleanup" — **CONFIRMED BUG for one citation; the other two sub-points are already handled**

- **Lot of Fortune citation (~3289–3292):** `source='Sahl, On Nativities Ch. 1.37, 1 (and throughout)'`, `note='"The Ascendant of the Moon" (2.1, 1)'`. Verified: the phrase "the Ascendant of the Moon" is at **1.37, 1** ("because the Lot of Fortune is 'the Ascendant of the Moon,'"). Ch. 2.1 is "Classes of good fortune & misery: al-Andarzaghar" and contains no such phrase. So `source` is right and the `note`'s "(2.1, 1)" is the mistyped reference. Note also that Sahl's prose at 1.37, 2 gives a *different* (hour-based) construction; the Sun→Moon-from-the-Ascendant formula the code uses is stated in Dykes' fn. 494 on 1.37, 3 ("Māshā'allāh now describes the usual formulas ... by day from the Sun to the Moon and by night the reverse, ... projected from the degree of the Ascendant"). Fix: note → `'"The Ascendant of the Moon" (1.37, 1); formula per Dykes\' note 494 on 1.37, 3'`.
- **Lot of Basis:** STALE/FALSE — already named `'Lot of Basis (unattested in the sources here)'` (~3236), with a docstring paragraph ("BASIS IS NOT ...") and the UI help (Classical Lots subheader) saying the same. Moving it to a separate section is optional.
- **Alternative father Lot:** ALREADY-CONSIDERED — the row is `confidence='conditional'` with note "'Now if Saturn was under the rays, then count from Mars to Jupiter.' Shown always; apply it only when Saturn is in fact under the rays." (~3342–3347). Auto-marking it active/inactive from `accidental['Saturn']['UnderBeams']` would be a small improvement; the current state is disclosed, not wrong.

---

## P2

### C21 — "Source flags and app scores must be separate products" — **ALREADY-CONSIDERED, DEFENSIBLE**

- Essential score (`evaluate_essential_dignities`, ~441–486): detriment −5, fall −4, peregrine −5 can stack (a planet in detriment is nearly always peregrine). The file labels this "the older Hellenistic net dignity score ... retained separately" (Abu-condition docstring) and it feeds only the app's own delineation switch.
- Abu condition verdict (~4889ff): "NOT Abu Ma'shar's. He enumerates these conditions; he nowhere adds them up, and no weighting or tie rule appears anywhere in VII.6. Counting the labels and subtracting is this app's own convenience ... labelled as a heuristic everywhere it is shown." Tie → Good (`net >= 0`, ~4931) is acknowledged as invented. The UI column is "Verdict (heuristic)" (~5844). The four VII.6 section counts are reported separately from `Net`.
- Planet-in-house `Lean` (~5390) inherits `Condition`; the `PLANETS_IN_HOUSES` comment says Good/Bad is "selected by the planet's own net dignity score".

Sol's `source_findings / source_counts / experimental_score` structure is a cleaner shape, but nothing here is presented as source doctrine. No defect.

### C22 — "Count numbered testimonies, not emitted strings" — **CONFIRMED BUG (minor; §88 already fixed)**

- §88: fixed in `2e277dd` (one entry, see C05).
- §94 (`evaluate_weakness_of_planets`, ~4204): the loop over rows appends one label per infortune, so Saturn and Mars can each add a vote to a testimony Sahl counts once.
- §97 (~4223, ~4227): per-planet duplicates for each clause. Reporting the two *clauses* separately is deliberate and documented (translator's fn. "not sure that these conditions must both exist at once"), but per-planet duplication is not.
- `'Count': len(labels)` (~4254) therefore over-counts against the "ten ways" Sahl announces (§90). Same pattern in the Sahl Moon-defect list (§104 and §109 append once per qualifying planet, ~5040–5110); the Abu condition table already applies "one entry per paragraph" at 28/29/45/46 and dedupes reception (~4820), so the file's own stated principle is being applied unevenly.

Fix: build labels as a dict keyed by paragraph (or collect matching planets and emit one string per paragraph, listing them), and report `Count` = number of distinct paragraphs. Presentation-level; no doctrinal output is wrong, only the tallies.

### C23 — "Thresholds and proxies need project-assumption labels" — **ALREADY-CONSIDERED, DEFENSIBLE (two labels missing)**

Checked each: apogee is labelled `'Apogee circle, approximated (23)'` (~4524) with a constants comment calling it "a modern proxy ... An approximation, flagged as such"; Sahl §99's node orb is labelled `'(99, 12 deg orb not in the source)'` (~4247); Abu §48's bound width has an "interpretive choice" comment (~4778) but the emitted label `'within a bound (N deg) (47-48)'` does not say so; the station threshold `abs(speed) <= 0.02` (~4526) and the `abs(lat) < 1.0` "without latitude" proxy carry no label at all. Two-string fix if wanted; nothing doctrinally wrong.

### C24 — "Calendar limits" — **CONFIRMED BUG (narrow input limitation)**

`calculate_traditional_chart()` (~71–81) correctly passes `swe.JUL_CAL` for dates before 1582-10-15 and documents why. But the date arrives via `datetime.strptime(date_string, "%Y-%m-%d")` (~5527), which validates in the proleptic Gregorian calendar. So a Julian leap day in a century year not divisible by 400 — 1500-02-29, 1400-02-29, 1300-02-29, 1100-02-29, ... — raises `ValueError` and cannot be entered, exactly as Sol says. (Post-1582 century years are Gregorian in both, so 1700/1800/1900-02-29 are correctly rejected.) Saved-chart metadata stores `date_string` only, with no calendar field. Historical time-zone handling already separates "LMT (Local Mean Time)" from "Standard time (pytz)" (~5541ff), which covers Sol's last point.

Fix: parse Y-M-D with a regex, validate the day against the Julian month length when `(y,m,d) < (1582,10,15)`, and call `swe.julday()` directly rather than constructing a `datetime` for pre-reform dates (the rest of the pipeline uses `jd`; `local_dt` is used only for display and for the pytz branch). Add `"calendar": "julian"|"gregorian"` to the saved-chart entry.

### C25 — "Cutting and nullification labels overclaim" — **CONFIRMED BUG (minor labeling)**

- Nullification `Because` string ends `'; the other perfects first but is not cut off'` (~2319). The code never computes which contact perfects first — the winner is the rank-0 uniting and `r` is any lower-ranked (or larger-deviation same-rank) applying contact. Dykes' note on 47 says the aspect "*may* perfect first". The string asserts more than is established. Fix: `'; the other contact remains valid and may perfect first'`, or compare `abs(deviation)` and only say "perfects first" when the other's remaining arc is smaller.
- Type III "candidate" status: `evaluate_blocking()`'s docstring carries the caveat ("With no topical significators nominated, a row here says a blocking pattern exists ..., not that any particular sought thing is obstructed"); `evaluate_cutting_the_light()` and its UI help do not, although Sahl 32 defines cutting in terms of "the lord of the Ascendant and the lord of the sought thing". A one-sentence caveat in the docstring/help would match the blocking table.
- Types I/II under-detection when the original aspect never perfects (`exact_day is None` → row skipped): a known limitation of the design, correctly censored (no false positive), not a bug. Documenting it is enough.

---

## What to fix first (CONFIRMED BUG items, ranked by effect on chart output)

1. **C11 — bound the §57 after-ingress search to the next sign** (`evaluate_reception`, §57 block): pass `before_day=exits[1]` (censor the row if there is no second exit). Without it, "just like reception / UNDERMINED after the sign change" rows can name a perfection that happens signs later. Affects Sahl-profile reception output for Sun/Mercury/Venus (and, rarely, the Moon). Also make the §57 emptiness test and the Moon-defect [9] test agree on applying-only.
2. **C16 — relabel or drop the 15° Libra–15° Scorpio "Via Combusta" row** in `evaluate_special_degrees` and its UI help: it is neither author's span, and both authors' own spans are already computed elsewhere. Appears on any chart with a planet in that 30° band.
3. **C22 — count testimonies per paragraph, not per matching planet**, in `evaluate_weakness_of_planets` (§94, §97) and the Sahl Moon-defect list (§104, §109). Only the `Count` column and the defect tally are affected.
4. **C25 — soften the Nullification `Because` string** ("may perfect first" / "remains valid") and add the topical-significator caveat to the Cutting docstring/help.
5. **C19 — mark `MASHAALLAH_LORDS[8][5]` as corrupt text** (Dykes' conjecture), one string.
6. **C24 — accept Julian leap days before 1582** by parsing Y-M-D without `datetime` for pre-reform dates, and record the calendar in saved charts. Real but rare input.
7. **C20 — fix the Lot of Fortune `note` reference** "(2.1, 1)" → "(1.37, 1)", and point the formula at Dykes' note 494 on 1.37, 3.

Items worth a decision but not a fix (OPEN QUESTION): C09 (gate Revoking and Cutting II on connection, and guard the Abu §44 no-exit case), C10 (Moon-only default for §§56–57 per the project's own narrower-source policy), C14 (show both Moon flags), C15 (make the Abu separating leg agree with the Sahl branch, or say why not), C05-residual (state why `get_effective_house` rather than strict cusps is used for gender quadrants), C12/C13 (coverage panel).
