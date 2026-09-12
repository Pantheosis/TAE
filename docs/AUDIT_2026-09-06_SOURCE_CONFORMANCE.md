# Source-conformance audit of `Executable/app.py` — session of 2026-09-06

Audited at `7e9f139`; fixes landed as `d8e07d2` + `892467c`, fast-forwarded onto `main`.
Sources: `/home/apothic/Desktop/Fifty Aphorism OCR Project/consolidated_texts/`
(`sahl_introduction_ch3.md`, `abu_mashar_book_vii.md`, `on_nativities.md`, `fifty_aphorisms.md`,
`images/`), plus `/home/apothic/Documents/TNAC/` (Glossary, Handy Tables, Reference Guide).
Previous audit doc: `SOL56_CODE_AUDIT_VERIFICATION.md` (2026-09-05).

**Beware:** `/home/apothic/almuten_engine/app.py` (1,308 lines) is a stale copy one directory
above the real file. Use absolute paths; a shell cwd reset bit two sessions running.

## 1. Headline results

1. **VI.26 §3 is resolved.** The Figure 90 reshoot
   (`images/am_supp_IMG_20260902_233845__page_0_Figure_22.jpeg`) is rotated 90°; its right
   margin carries the line-beginnings of VI.26 §3: `3 Now | rants whic | Ascendan | heaven, |
   setting to | called "a | eastern, | while th | which ar | to the set | fourth t | are calle |
   feminine | left." 4 ( | the ear`. With the figure's dashed arrows (ASC→MC, DSC→IC) and Dykes'
   fn. 231 on *On Nativities* 10.3 ("the eastern quarter from the Ascendant to the Midheaven is
   advancing, while the quarter from the Midheaven to the Descendant is declining or retreating"),
   Abu Ma'shar's *advancing quadrants* = primary motion toward the meridian. That is a separate
   condition from stakes/succedents (he lists both, VII.3 §2–5). Sahl's "advancement" is his own
   Ch.3 §4 ("in a stake or what follows a stake"); Sahl's Figure 9 shades sectors
   1,2,4,5,7,8,10,11. **No conflict; Sahl §83 stands as implemented.** Third witness for quadrant
   genders: recovered p. 282, *On Nativities* 1.10 §74.
2. **Sahl's connection orb**: no new evidence; asymmetric reading kept.
3. All worked figures reproduce: Sahl Figs. 10–17, 25; Abu Ma'shar Figs. 126–129, 136, 142,
   144, 145. Figures opened: Abu Ma'shar 90, 112, 114, 115, 118–121, 124, 126–129, 131, 136,
   142–145; Sahl 9. Victor wheels checked cell-by-cell against Handy Tables pp. 33–34 images.

## 2. Defects found and fixed (`d8e07d2`)

| # | Defect | Source | Rate before → after (sampled charts) |
|---|---|---|---|
| F1 | Planetary Condition table `sort_values(by="Net (heuristic)")` after column renamed to `Net` in `7e9f139` — KeyError on every Abu Ma'shar view | — | crash → renders |
| F2 | Sahl §81 tested "either member is an infortune", so Mars/Saturn lost the testimony against any partner | Ch.3 §81 | 283/480 Mars+Saturn placements wrong → 0 |
| F3 | VII.6 §4 and the separating/connecting form of §57 required `_is_connected()` on the separating leg; under the pinned Abu profile VII.5 §34 ends connection at 1′, so both were dead. New `_is_separating_in_nature()` per VII.5 §17/§35 (in the nature until the sign changes) | VII.6 §4, §57 | §4: 1/1,680 → 43/840 |
| F4 | VII.5 §137 "he receives her from all signs" skipped when Sun–Moon in aversion | VII.5 §137 | missing in 32% of charts → 0 |
| F5 | VII.5 §134 "two signs of one planet" fired on same-sign pairs | VII.5 §134 | 26% of §134 rows spurious → 0 |
| F6 | VII.6 §64 "eclipsed": `lun_eclipse_how` at Greenwich geopos, then a 12° proxy that also counted solar eclipses. Now `lun_eclipse_when` contact times, global; penumbral-only labelled | VII.6 §64 | 3/240 false → 0; 2019-01-21 eclipse detected |
| F7 | VII.6 §9 "increasing in light" used geocentric distance for the Moon; now waxing (VII.2 §62–71; Sahl §112) | VII.6 §9 | 47.5% agreement → exact |
| F11 | Moon hands over Power only from Taurus/Cancer (Sahl §75–76 restricts §70) | Ch.3 §75–76 | — |
| F16 | VII.6 §44: no sign exit inside the 200-day horizon no longer counted as "empty of course" (present-tense proxy instead) | VII.6 §44 | — |
| F17 | §46 excludes the burned band (VII.2 §40); §141 mutual reception graded "Strong" under Abu | — | — |

## 3. Configurable readings (sidebar expander "Configurable readings"; defaults follow the narrower/original text)

| Global | Default | Alternative | Sources |
|---|---|---|---|
| `FIVE_DEGREE_ALL_CUSPS` | False (stakes) | all cusps | Aph. #44 §88 and *Nat.* 1.22 §9 (stakes) vs *Nat.* 1.18 §19 "and likewise in all of the houses". Flips §83 for ~6% of placements. **The old docstring's claim that no source says "any cusp" was false.** |
| `EASTERN_RULE` | `'hemisphere'` (rays excluded) | `'VII.2 band'` (15/18–90° east; 90→15° west) | VII.6 §27/§45 vs VII.2 §14–21, §29–31. Superiors: 52% vs 25% |
| `MOON_RAYS_ORB` | 12 | 15 | VII.2 §61, §72–73 vs *Nat.* 1.19 §6 |
| `DOMAIN_RULE` | Abu Ma'shar (VII.1 §37, VII.6 §13) | Masha'allah (*Nat.* 1.23 §17: male by night under the earth **in a female sign**; feminine by hemisphere only) | |
| `LOT_HOUSE_CUSP` | `'whole-sign place'` (ASC degree carried into the Nth sign) | `'quadrant cusp'` | *Nat.* 2.15 §1, 8.6 §1, 9.1 §9; moves assets/death/travel/enemies Lots |

Note: Moon-rays and VII.2-band switches are inert on most charts (Moon 12–15° from Sun; superior in the rays or past the square). Not a bug.

## 4. Label/provenance corrections

- VI.26 comment block and coverage entry rewritten as resolved; `ADVANCING_BY_QUADRANT_FIG90` kept as Abu Ma'shar VII.3 §2 (not scored).
- VII.2 §37 is now legible ("burned until … 7 degrees"): the inferiors' 7° is a reading, not an inference.
- Sahl §84 label: "eastern, 6/15+ deg from the Sun (84; 'considered eastern', *Nat.* 1.22 §1)" — 6° is the nine-day fitness allowance, not visibility; Mars's 15° is Dykes' inference (1.22 fn. 174).
- Sahl §99 label: the 12° node orb is in Sahl (Ch.3 §107; *Nat.* 1.21 §12).
- Lot of Fortune note → 1.37 §1 + Dykes fn. 494. Lot of Spirit: named by Sahl; formula is Handy Tables L18. Work-expedition Lot: Sahl's unreversed text is the default row; Paul's night reversal is a second row. Classical Lots `Standing` now derived from `LOT_DEFINITIONS` (`892467c`).
- Chart page quadrant label: "advancing/retreating — Sahl Ch.3, 4-5". `configurations_view` key on the segmented control (`892467c`).
- `NOT_IMPLEMENTED_COVERAGE` = 17 rows (10 → 17): + VII.5 §32–33 mixing by ray; *Nat.* 1.20–1.23 releaser/house-master; 1.18 §20–22 distributions ("for each degree of ascensions a year, every 5′ a month, every 1′ six days, every 10″ a day"); 2.13 §48–51 ascensional bands; 2.2 thirty fixed stars; 2.6/4.9 twelfth-parts; further Lots (constitution 1.34 §13 recovered p. 358; male/female 3.12 §20; Venus→7th 7.1 §10/§145; Sun→Moon from Venus 7.4 §8; religion 9.5 §3; riding animals 12.2 fn. 18).

## 5. Verified correct — do not re-audit

Solar phase orbs (per planet, asymmetric, cazimi 16′, Mars setting 18°); domain/hayz with Mars hemisphere-only and §36 both-halves; quadrant genders {4,5,6,10,11,12}; bodies 15/12/9/9/8/7/7; Abu 15°/12° activation and 1′ separation; Sahl §20–21 out-of-sign body connection; §§56–57 Moon-only with §57 bounded to the next sign; non-reception five kinds; cutting/nullification precedence (§44); blocking I/II incl. §40/§94 exception by arc; Strength 78–88 and Weakness 91–100 scopes and single-vote counting; Sahl's ten and Abu Ma'shar's eleven Moon corruptions kept apart; VII.6 §2, 3, 7, 10, 14, 19–20, 22/38, 28/45 Sun clauses, 29/46 Moon as third inferior, 31 (Venus/Mercury vs Sun's pace), 33, 35, 39, 42, 48 (labelled), 49, 50, 52–55, 56–61; victor weights and both places wheels; all 31 evaluator outputs rendered exactly once; `MASHAALLAH_LORDS` spot-checked; all 34 (now 35) Lot formulas against prose.

## 6. Still open / deferred

- Remaining configurable choices are exposed, not decided: see §3.
- VII.6 §8 "Moon made fortunate" is still the zero-corruptions proxy (flagged in code).
- VII.5 §29–31 (priority of several connections), §38–52 (latitude), §53–77 (natural connections), §97–100, §104–116 (returning tree): unimplemented, listed.
- Releaser/house-master and true distributions: the largest gap; nothing in the app.
- Opus's Streamlit pass (2026-09-06) found no tracebacks on any page under any switch; contents of Reflection/Favor tables and the Timing/Victors pages were not content-checked there.
- Test scripts from the session (synthetic-figure harness, 240-chart frequency sampler) lived only in the session scratchpad; the figure cases above are the regression set to rebuild if a test suite is started.

## 7. Where things are

- Repo: `/home/apothic/almuten_engine/Executable/` (git root), `main` @ `892467c`. Branch `audit-2026-09-06-fixes` = same commit, deletable.
- Memory note: `~/.claude/projects/-home-apothic-almuten-engine/memory/project_advancing_two_senses.md`.
