# Build from the final adjudication and the 2026-09-11 rulings -- plan and running log

Branch `astra-build-2026-09-11`, cut from main 96fd547 in the detached worktree
`Executable_astra/`. Corpus branch `astra-session-2026-09-11` (c7e50bb). Written before any code
change; the report sections at the end are filled as work lands.

## 0. Pin check (done before building)

- Origin/main is 96fd547, the sha the brief names. Every function the 38 orders and the audit
  name was compared mechanically between the lanes' pin 9e0834d and 96fd547: ten differ, all
  in docstrings, comments or citation labels only (the `pn4_first_ninth_part_lord` difference
  recorded in ENGINE_SHAS.md is the label of the adjacent `PN4_MONTHLY_TURN_OPTIONS`
  constant, not the function). No code-level drift; the orders apply as written.
- Astra's harness re-run on this worktree at 96fd547: 23 FAIL / 4 PASS, as the triage says.
- Baseline suite: see §6.
- The measures harness (`process/adjudication/tools/harness.py`) loads the engine by
  `git show <sha>:app.py`; the FINAL-A1 re-measure under the divisions is a PREDICATE change
  (`get_wsh_house` -> `get_effective_house`), so it runs at 96fd547 with no new pin. Post-build
  measurements will be run at the commit that carries them, and that sha is recorded here.

## 1. Phase 1 -- the engine audit (F01-F14, C01)

Step 0: Astra's harness is adopted as `tests/test_astra_audit_repro.py` BEFORE any fix, one
test per expectation, all red; each fix turns its test green (the audit's own instruction).
Then F01, F02, F03 (Timing output on ordinary charts), then F04-F09, F12, F13 (defects),
F10, F11, F14 (boundary/reporting), C01 (Virgo's partner: Mercury, "in preference to" Mars,
Gr. Intr. V.14, 7 + Fig. 53 + fn 100). The 365.2425-day Fig. 22 mapping stays, labelled.
F01 note: the reform policy (Julian before 1582-10-15) already exists in
`calculate_traditional_chart`; the defect is the proleptic-Gregorian `datetime` carrier and
the offset arithmetic, not the policy.

Discipline for every phase: (a) the order's fixture sentence is grepped in the corpus at its
current sha and the passage read before code is written; (b) every rule gets a positive
fixture and a near-miss; (c) one commit per order id / audit id; (d) Phase 2 is taken in
output-impact order -- items that change ordinary charts first, display-only additions last,
the fixed-star table (PN4R-4n-7) last of all.

## 2. Phase 2 -- the 27 READY orders, each dispatched against the canon

No unit question: PN4R-4m-1, PN4R-4p-8, PN4R-4n-2 (= F14), GAP-27, CONV-SOLAR_BURNED_ORB,
PN4R-4e-2, GAP-3, DIS-9, PN4R-4l-7, DIS-10, GAP-2, PN4R-4c-4, PN4R-4f-6, PN4R-4g-5 (#15),
PN4R-4h-4, PN4R-4i-5, PN4R-4n-7, GAP-34, PN4R-4a-2, REL-2-3.
Places (topic language), consistent with the canon: PN4R-4g-2 (row 9's three houses, whole
sign), PN4R-4a-1 (whole-sign aspect).
Judgment calls, recorded here and on the page:
- PN4R-4n-5 (revolution image filed by quadrant house): I.6, 2 STATES the house computation
  ("by their degrees and minutes ... the ascensions of the right circle"); the canon's dispatch
  is for texts that use strength or topic language and are silent on the unit. Built as
  ordered, the caption saying the unit is the author's instruction for this figure.
- GAP-37 / PN4R-4b-4 (planets "in the Midheaven" directed by right ascension): the order says
  `get_effective_house` (division WITH the 5-degree carry-over). Built AS ORDERED, the boundary
  declared on the page as a reading. Doubt recorded for the owner (not resolved here): the
  canon confines the 5° rule to power, and this test is neither strength nor topic, so whether
  the carry-over belongs in it is open. (A first draft of this plan chose the division without
  the carry-over on its own; that was a silent resolution and is withdrawn.)
- CONV-ESSENTIAL_DIGNITY_WEIGHTS (1.7, 7's tie-break "in a stake"): strength language
  ("stronger") -> division, said on the row.
STOP (unit conflict with the canon, for the owner):
- GAP-31, IX.9, 13's place test: the order counts "in a stake or in what follows a stake" by
  WHOLE-SIGN place; the sentence is strength language ("in a suitable condition in terms of the
  rotation of the circle ... in rank, power, and class") -> the canon says divisions. Rows for
  11 and 12 and 13's "in its sign" half are built; 13's place half prints "unit awaits the
  owner" with both readings named and neither applied.
The 4 BLOCKED orders REL-5-7, REL-5-1, REL-5-2, REL-5-3 are unblocked (row 3: the quadrant
releaser stands); built with the pinned selector.

## 3. Phase 3 -- decision-sheet rows

Row 1 (A1): re-measure FINAL_A1 under the divisions FIRST (predicate `FINAL_A1_divisions.py`,
harness at 96fd547), then the grant from 1.20, 7-34 with each sentence printed; 13 and 14-15
printed, not applied; On Times 4, 7 relabelled the question-chart rule; one reader added to
`D3_GRANT_READERS`; the display's 1.20 column moves to `get_effective_house`.
Row 2 (A2): caption naming the join, IX.8, 32 + fn 129 printed, IX.8, 30's turning as PN IV's;
IX.8, 32 a ROLE restriction (III.1, 5); 1.16, 4 not covered by the "1.16 exception".
Row 3 (A3, REJECTED): selector stands; the Lot of Fortune candidate tested by whole-sign place
(a change); the meeting/fullness degrees flagged as an open reading (division kept, declared);
`five_degree_all_cusps` retired; reading (1) rewritten with the warrant the ruling names and
the attribution addendum; `get_effective_house` docstring rewritten (1.18, 19 read as the four
stakes; geometry exists, longitude kept by choice).
Row 4 (A12): Lot of death source/confidence/STANDING/test re-pinned; this Lot's `cusp8` defaults
to the Alcabitius cusp, whole-sign carried degree as a labelled variant.
Row 5 (A4): Aphorism 45 as printed with fn 57; 2.13, 48-51 built under its own name for the sect
light's first triplicity lord (read in the corpus first); the per-planet grade as the ENGINE'S
GENERALISATION, labelled; OA at the horizon / RA at the meridian declared; D-23 refusal.
Rows 6 (A5), 9 (D-5 relabel), 10 (D-15 relabel), 11 (D-18 two tables), 12 (REL-2-6 seven
places), 13 (12.175 d), 15 (GAP-39: D-19 docstring + VII.6, 52 own-node flag): from their orders.
Row 14: nothing.

## 4. Phase 4 -- corpus

`DOCTRINAL_CAVEATS.md` Aphorism 45 entry rewritten per FINAL-A4; the engine's three false
sentences about the corpus reading 25″ / lacking Figure 43's glyphs corrected (engine side).

## 5. Phase C page wording (no dependency) -- applied where the function is touched anyway,
listed in §7.

## 6. Suite counts

- Baseline, main 96fd547: 2723 passed (12:04).
- After Phase 1 (5ed5841, C01): 2758 passed (12:11), 0 failed.

## 6a. FINAL-A1 re-measured under the divisions (row 1's precondition)

Predicate `process/adjudication/measures/FINAL_A1_divisions.py` = FINAL_A1.py with the
house-master placed by `get_effective_house` (Alcabitius divisions, 5° at the stakes) instead
of `get_wsh_house`; every other reading unchanged. Harness at engine 96fd547, 406 charts:

| Predicate | definite grade under 1.20, 7-34 in full |
|---|---|
| FINAL_A1.py (whole signs, the FINAL card's unit) | 82.3% (316/384) |
| FINAL_A1_divisions.py (divisions, the ruling's unit) | 83.3% (320/384) |

22 charts name no house-master in both. The figure replaces FINAL-A1's 82.3% on the page and
in the report; the sentence counts are re-derived by the grant function itself once built.

## 7. Report (running)

### Phase 1 -- the engine audit: DONE, all 23 expectations green

| Id | Commit | What changed |
|---|---|---|
| harness | d7cf4d1 | 23 expectations adopted as `tests/test_astra_audit_repro.py` before any fix |
| F01 | a48884a | `civil_calendar` policy in one place; `CivilDate`/`CivilMoment` carriers; `civil_local_to_jd_ut`, `calculate_traditional_chart_jd`; the sidebar subtracts the offset on the JD; `parse_iso_date` validates in the date's own calendar; chart dict carries `geo_lat`/`geo_lon` |
| F13 | 0d7a30b | `get_degree_string` in total minutes with a 1e-6' tolerance, truncation kept |
| F02 F03 F11 F12 | 55410ff | three counts of the year (`age` civil, `cycle` returns, `elapsed` 365.2425 d) with a "Count of the year" row; the containing return bracketed; "Active point" = degree reached; fardar sub-periods half-open against their own boundaries; wheel/strip "now" on the elapsed clock |
| F04 F09 F10 | 2d65f7d | hayz by altitude when the horizon is supplied (`Hemisphere by` says which); connection ends at exactness (VII.5, 16, 34); eastern phases exclusive at completion, western inclusive |
| F05 F06 F07 F08 | 9c8212b | escape only when the capture precedes the original contact; ingress bisected to 1e-4 d; steps split at stations; Sahl 3, 97's receiver judged at the departing planet's degree |
| F14 + PN4R-4n-2 | 0fe9684 | twelfth-part provenance = Gr. Intr. V.18, 1-3 (Fig. 57) in four places + register; faces = V.15 Fig. 54; wells "64 cells" |
| C01 | (next) | Virgo's partner Mercury "in preference to" Mars (V.14, 7; Fig. 53 Gr. Intr.; fn 100); "Figure 53 (PN IV)" in the Ages help |

Readings declared in code, not silently taken: the 365.2425-day mapping (kept, labelled); the
ecliptic-proxy fallback for hayz when no horizon is supplied; fn 99's open conjunction of 3, 97's
two clauses (each applied on its own); 1e-9 degree machine tolerance at exactness (F09).

### Phase 2 (READY orders) and Phase 3 (sheet rows), in commit order

| Id / row | Commit | Note |
|---|---|---|
| CONV-SOLAR_BURNED_ORB | 93d5725 | VII.2, 44 as printed (6°) for the direct eastern inferior; `solar_phase` takes the motion; band labelled |
| PN4R-4m-1 (+ follow-up) | 83200c0, aa21ba6 | III.2, 43 keyed to types 4, 5, 6 (the first commit landed with its tests red -- a gate bug in the build script, repaired in the follow-up) |
| PN4R-4p-8 | a8f6ff8 | method 8 wraps at day 30 (IX.7, 39) |
| PN4R-4n-5 (+ follow-up) | dbc0700, aa21ba6 | image filed by the revolution's cusps (I.6, 2), ordered from the cusp; judgment call recorded in §2 |
| PN4R-4g-2 | 0be78b3 | row 9 from the three Ascendants (II.6, 1), whole-sign places |
| Row 13 / PN4R-4d-1 | 8bffc00 | 12 + 1/6 + 1/120 d; three figures printed; 365.25 pinned |
| Row 10 / DEC-D-15 | 58975f6 | "Dykes's table for Sahl, fn 175" |
| Row 9 / DEC-D-5 | f471483 | 19°–3° kept, relabelled Gr. Intr. VII.6, 40 borrowed; readings recorded |
| Row 12 / REL-2-6 | 12c7893 | `SAHL_GOOD_PLACES`, whole-sign place |
| REL-2-3 | c95dd23 | 1.16, 4 named on the unwitnessed luminary's row and in NOT_APPLIED |
| GAP-3 | fa38cf3 | 1.23, 33 and 1.24, 2 side by side; "ranks by scope" |
| GAP-27 | 4b0e071 | the seven-day grant is method 2; caption, comment, register |
| Row 15 / GAP-39 | 1f72824 | VII.6, 52 own nodes (mean, declared); D-19 cited |
| Row 3 (engine orders) | 1f72824 + 2295574 | `five_degree_all_cusps` retired; `get_effective_house` docstring per the ruling |
| Row 4 / FINAL-A12 | 4ed3a91 | Lot of death: stated by Gr. Intr., printed in Sahl; cusp "by equation" as the row's own rule; whole-sign variant row |
| Row 7 / FINAL-A6 | 42259b9 | 1.7, 2 cited |
| Row 8 / FINAL-A7 | 02e615d | the stand-in applied and named; the Moon directed |
| Row 2 / FINAL-A2 | cb2fb94 | the join named; IX.8, 32 + fn 129 beside it; IX.8, 30's turning table; III.1, 5 and 1.16, 4 limits |
| Rows 3, 6, 12 wording; reading (5) | 8d621de | readings (1)–(7) rewritten to the canon and its attribution; the Lot by whole-sign place; column renamed (fixture regenerated for it) |
| Row 1 / FINAL-A1 | d00a116 | `sahl_house_master_years` from 1.20, 7-34 by the division; display column moved; On Times relabelled; D-3 control admits the one reader; register addenda |
| Row 5 / FINAL-A4 | 9f3bf52 | `evaluate_ascensional_bands`: 2.13, 48-51 for the sect light's first triplicity lord; the per-planet grade labelled the engine's generalisation; Aphorism 45 as printed, not applied |
| PN IV repairs wording | 8fde819 | the three 25″ / Figure 43 sentences now past tense |
| Phase 4 (corpus) | 589cfc8 | DOCTRINAL_CAVEATS.md Aphorism 45 entry per FINAL-A4; FINAL addenda + FINAL_A1_divisions.py in the next corpus commit |

`tests/fixtures/tables.json` was regenerated deliberately, each time verified by a set comparison
of every page's (table, columns) entries: 8d621de (one column renamed; row 2's turning table
added), d00a116 (two columns of the planetary-years table renamed), 9f3bf52 (one table added),
65ce626 (one column name), 47ddfc2 (two tables), 839e208 (the orb table's columns, the proxies
table, the angle-planet tables), 349301b, 49d2f3b (one table each).

### Phase 2, second and third groups (after the full-suite gate at 5ed5841: 2758 passed)

| Id / row | Commit | Note |
|---|---|---|
| citation form | 65ce626 | "Aphorism #45" for the checker (its floor had tripped in the full suite: 1959 passed, 1 failed at 8fde819) |
| Row 11 / DEC-D-18 | 47ddfc2 | right-sidedness (2.5, 1-3) and the honor-guard (10.2.1, 10-15), display only, readings named |
| PN4R-4e-2 | 045bac9 | VI.1, 8's column beside VI.1, 10's |
| PN4R-4l-7 | 79b885d | II.3 twelfth-parts computed |
| PN4R-4a-1, 4a-2 | 924b6d1 | III.7, 35's "not looking" read (three readings declared); 42 against every distribution, named |
| DIS-9 | ce51745 | caveat row and comment name 7.4, 17; 5.3, 11-12; 6.5, 1 |
| PN4R-4i-5 | 92e6480 | II.22, 23-25 row for any lord of the year; fn 319's void stand-in named as not read |
| PN4R-4h-4 | 1b14860 | IX.2, 5's primary and partners |
| GAP-37 / PN4R-4b-4 | 839e208 | planets in divisions 1, 10, 4 directed; unit = the order's (division with carry-over), recorded as a reading for the owner |
| GAP-2 | 18dd4ad | the year of the turning reaching the partner's body |
| PN4R-4f-6 | 349301b | VI.2, 4-5 triplicity lords with conditions |
| PN4R-4g-5 | e3b6909 | #15 computed from VI.6, 1's three lords; #16-17 stay NOT tracked |
| GAP-34 | ae45dd1 | VI.4 class, IX.2, 33 pairs, V.20 degree classes on II.3's rays |
| PN4R-4c-4 | d5fc5a0 | small and mighty days from any point (selector) |
| GAP-31 | 49d2f3b | IX.9, 11-12 as facts; **13's place half STOPPED** (unit: order says whole-sign place, canon says division) |

### Phase 2, fourth group (the four BLOCKED REL-5 orders, unblocked by the owner's row 3, and the two remaining READY orders)

| Id / row | Commit | Note |
|---|---|---|
| DIS-10 | 1027d99 | `sahl_father_lot_harmers`: 4.20, 31's harmers by sect (Mercury "if he was unfortunate" shown as a judgment not made; Saturn by night under 36's "from hostility"); 4.20, 32's two directions (the Lot's degree, and the Sun by day / Saturn by night) via `sahl_house_master_direction(start_lon=, target_planets=, sun_target=)`; fn 288 quoted as Dykes's, not applied; 33-35's choice not made |
| REL-5-7 | 1027d99 | 1.23, 13-14 applied when a 1.23, 12 flag stands: the lord of the Ascendant directed in the house-master's stead, then the Ascendant's degree; 13's aggravation named; 1.23, 6 added to the not-applied list |
| REL-5-1 | 29b835d | 1.19, 6 applied in `_sahl_examine_candidate`: the Moon within 15° of the Sun "not fit", the fullness consulted; Sahl's own 15 for this gate, separate from the Chart page's 12/15 switch; out of `SAHL_RELEASER_NOT_APPLIED` |
| REL-5-2 | 29b835d | 1.20, 6 applied: a candidate in the places with no lord looking stands when a dignity lord is eastern with a share at the Ascendant's degree ("a share" read as any of the five, declared); that lord is house-master "by 1.20, 6"; a looking lord stays preferable; out of the not-applied list |
| REL-5-3 | 29b835d | `sahl_short_life_testimonies`: 1.18, 1-4 counted (readings on each row: the Moon's first perfection followed forward; 4's two clauses one testimony, fn 130), 5-7 "equivalent, not counted" (fn 126, 129), 8/9/10 quoted by the count; beside the releaser, NOT disqualifying it |
| PN4R-4n-7 | de4f5a8 | `SAHL_FIXED_STARS` (28, On Nativities 2.2's table in Dykes's identifications; the two Sahl does not carry left out, the two doubtful marked), `pn4_fixed_stars_in_image` (I.6, 7) and `pn4_fixed_stars_in_revolution` (III.8, 9); positions from a Swiss Ephemeris `sefstars.txt` found at run time (a package in the venv ships one) through a private link-only directory so the planets stay on Moshier (flag pinned by test); refuses with a sentence when absent; "the very degree"/"with" = within 1°, declared; both "not computed" captions reworded |

Fixture regenerations in this group: 1027d99 (the father's-Lot tables), 29b835d (the short-life table), de4f5a8
(the fixed-star tables on five of the six fixture dates). **Portability note for the owner:** the fixed-star tables
appear in `tests/fixtures/tables.json` only because this interpreter carries a star catalogue
(`kerykeion/sweph/sefstars.txt` in the root venv); on a machine without one the page says "not computed" and
`test_pages_render`'s fixture comparison will differ by those tables, and the fixed-star unit test skips.
One test rewritten to the source: `test_abu_connection_ends_one_minute_past_exact` had pinned the
inversion of VII.5, 16; it is now `..._at_exactness_not_a_minute_past_it`. `tests/fixtures/
tables.json` did NOT move: none of the six fixture charts changes a table cell under F04-F10.

## Close (2026-09-11, evening)

- Full suite at de4f5a8: 1981 passed, 1 failed -- the REL-2-3 fixture had Venus eastern with a share at the
  Ascendant, which is 1.20, 6's case since REL-5-2; re-pinned with Venus western (ea12528).
- Full suite at ea12528: **1982 passed, 0 failed** (9m 32s).
- **Collected count: main 96fd547 collects 2723, this branch 1982.** The whole difference is
  `tests/test_switch_matrix.py` (1977 -> 1154): retiring the five-degree all-cusps reading (row 3) removed a
  two-valued dimension of the switch matrix. Every other file grew (audit harness +27, base tables +8,
  decisions +2, doctrine fixtures +44, revolution wheels +1). So the "before/after" figures the prompt asks for are
  2723 / 1982, and the second is not a loss of coverage but a retired switch.
- Corpus branch `astra-session-2026-09-11`: ec439a5 (589cfc8 the Aphorism 45 caveat entry; ec439a5 the FINAL
  addenda file and `FINAL_A1_divisions.py`). The FINAL_ADJUDICATION files and the Astra rulings were not edited.
- For the owner (the only class of question left): GAP-31's IX.9, 13 place half (order: whole-sign place; canon:
  division -- STOPPED, 49d2f3b); GAP-37's unit built as the order says (division with carry-over) with the doubt
  recorded (839e208); PN4R-4n-5 judged no conflict (see above). The fixed-star fixture's portability note (fourth
  group) is a second, practical item.
- Merge: `astra-build-2026-09-11` fast-forwarded into `main` in the shared tree after this commit; not pushed.

## Review round (2026-09-11, from `BUILD_FIX_PROMPT_2026-09-11.md`; the checker's report `BUILD_CHECK_REPORT_2026-09-11.md` §2, §5 and the cloud review of PR #1)

Appended, not rewritten. One commit per item; the builder does not certify its own work.

| Item | Commit | What was done |
|---|---|---|
| A1 / D1 CONV-ESSENTIAL_DIGNITY_WEIGHTS | 8c43dc4 | Built as the order words it: `sahl_syzygy_governor` applies 1.7, 4 (direct, looking at the syzygy's sign), 1.7, 3 (the eastern one preferred, the engine's solar-phase side; the Sun has no side), 1.7, 7's tie-break (a stake by the DIVISION -- strength language under the canon, said on the page -- or own dignity); "stronger in its [own] place" (4) and 5-6 not modelled, a tie left a tie, said. Conditions read at the NATIVITY (Dykes's comment; the order's predicate), declared. The almuten row relabelled "Almuten by 5/4/3/2/1 points (the course's technique; the weights are stated in no text in hand)". The log's earlier "said on the row" (§2) was wrong: there was no row until this commit. Fixture: a lord in aversion dropped while the almuten names it; a retrograde lord dropped; the tie-break and a declared tie. `tables.json`: one table added on the victors page for each of the six dates ("Governor of the syzygy degree: the five lords under 1.7, 3-7", 7 columns). |
| A2 / D2 1.20, 11 "enhanced" | 9b1d0dc | `_sahl_1_20_grade`: `q == 4 and enhanced`, `night and enhanced` (11 as printed, 7-9 with fn 152). Fall-through checked by probe: the fourth retrograde -> "1.20 silent"; under the rays direct -> 18; both -> 21; the fifth by night retrograde -> 23. Fixture pins all six. Readings string: the requirement said; 12 vs 23 for a diurnal planet in the eleventh, eastern, in a share, retrograde named as a conflict as printed (23 applied). |
| A2 re-measure | 525e19f | Both corpus measures (`FINAL_A1.py`, `FINAL_A1_divisions.py`, `grade_1_20`) carry the same two one-line changes; harness at engine 9b1d0dc, 406 charts. See the table below. Restated in the `sahl_house_master_years` docstring and in `SAHL_1_20_READINGS` on the Releaser page; corpus addendum in `FINAL_ADJUDICATION_2026-09-11_ADDENDA.md`. |

### FINAL-A1 re-measured with 11's "enhanced" (review D2)

| Predicate | at c6d3b3a, old measure | at 9b1d0dc, measure fixed |
|---|---|---|
| FINAL_A1.py (whole signs) | 82.5% (320/388) | **82.0% (318/388)** |
| FINAL_A1_divisions.py (divisions) | 83.5% (324/388) | **82.5% (320/388)** |

The denominator is 388, not §6a's 384: REL-5-2's 1.20, 6 (29b835d) names four more house-masters
(the checker's §5 notes the same), and all four receive a grade. So the build's 82.3% / 83.3%
(316/384, 320/384 at 96fd547) had become 82.5% / 83.5% by c6d3b3a before D2; D2 moves two
house-masters by whole signs and four by the division from "greater (11)" to no sentence (a
retrograde planet in the fourth, not under the rays, reaches nothing in 1.20 -- the same as the
other stakes). The retrograde-under-the-rays and under-the-rays cases keep a definite grade (21,
18) and do not move the figure.

### Rows added after the re-measure

| Item | Commit | What was done |
|---|---|---|
| A3 / D3 Carmen I.28 | 57318ba | The photograph (p. 108) read by this session: I.28, 5 third 15° "middling in assets and good fortune" (= 2.13, 50); 6, after these degrees up to the next stake, "needy [and] wretches" (= 51). `SAHL_2_13_BANDS[2]` and [3] carry the two Carmen sentences; the notes sentence "Carmen's third band ("needy") differs from Sahl's 50" dropped; the band strings pinned. Corpus: `DOCTRINAL_CAVEATS.md` Aphorism 45 entry corrected to "band for band". |
| A4 / D4 Lots STANDING | d2e6bbe | The paragraph's last sentence rewritten to FINAL-A12's page wording: stated by Abū Ma'shar (Gr. Intr. VIII.4, 226; VIII.6, 69), Sahl 8.6, 1 as printed agrees, his manuscripts reading the Ascendant (fn 89); "emendation" out of the sentence (the `LOT_DEFINITIONS` comment keeps the word for the manuscript history). Pinned in `test_d11`. |
| A5 / D5 DEC-D-5 | 4540d5e | Condition 110's clause now carries both readings beside the borrowing label: 15° Libra–15° Scorpio "often defined" (Dykes, Carmen p. 258 fn 104; Course Glossary) so "no source in hand states it" is withdrawn; Dorotheus's own (Carmen p. 258 §6) a different construction. The comment above `BURNED_PLACE_SIGNS` rewritten (no "in no source in hand"; no "used only where the table is his"). Pinned in the 110 fixture. |
| A6 + B3 portability | f2c7d80 | Owner's decision (b): `ephe/sefstars.txt` shipped (137 KB, copied unmodified from kerykeion 5.12.9, AGPL-3.0 -- the app's licence; `ephe/README.md`); `_fixed_star_catalogue_ready` looks there FIRST (`Path(__file__).parent / 'ephe'`, the `atlas.db` directory), then `$SE_EPHE_PATH`, the user data dir, site-packages; the private link re-pointed at the file found; `build.spec` `datas` carries it; `BUILD_NOTES.md`'s invariant restated (no `.se1` bundled or needed, the planets on Moshier; `set_ephe_path` called once at a link-only directory, the flag test pins 260). Tests: the bundled file is the one found; the fallback with every `sefstars.txt` invisible (the Timing page says "Not computed", the unit test skips). `tables.json`'s nine star tables are now deterministic on every checkout; the fourth group's portability note is closed. |
| B1 precedence | f1a9cdf | `sahl_short_life_testimonies` testimony 7: `(', '.join(retro_partners) or 'none') + ' (reception not tested here)'`; the fixture pins the caveat with and without a retrograde partner. |
| B2 double call | 7ea2bc0 | `pn4_timing_bundle` computes `pn4_governor` once; `governor_condition` reads its primary. No output change. |
| B4 dead `if True:` | 23c8f28 | Deleted in `evaluate_escape`, the append dedented. (A second, pre-existing `if True:` in the UI's `_restore_chart` is not the finding's and was left.) |
| C GAP-31 (ruled: DIVISIONS, adopted reading) | 47cc309 | IX.9, 13's place half built with `get_effective_house` in the revolution; "Met" is yes when the division is 1/4/7/10 or 2/5/8/11 AND 12's sign condition holds in the revolution. The row carries the three statements separately -- (i) the text supplies the requirement, (ii) the canon its operational interpretation, (iii) Alcabitius and the axial 5° from that convention -- and the QUALIFIED confidence with IX.5, 4 fn 106 (p. 602) quoted, IX.5, 9 (p. 603) as the closest parallel, V.1, 28 fn 15 beside it. "Unit awaits the owner" dropped from row and captions; the caption says the unit is the canon's. Fixture: on the tenth cusp met; the cusp 6° on (ninth division) not met; 4° on (carried) met; a stake with no testimony -> no; without cusps "not computed". THE ORDER'S "WHOLE-SIGN PLACE" IS CORRECTED BY RULING. Corpus: a dated addendum to `OWNER_RULING_PLACES_VS_DYNAMICS_2026-09-11.md` with both witnesses verified (fn 106 at `persian_nativities_iv.md` line 12345, IX.5, 4 on p. 602, IX.5, 7-9 on p. 603; fn 15 at line 8461, p. 400). |

The owner's GAP-31 ruling, quoted: "DIVISIONS -- approved as an ADOPTED DYNAMIC-FITNESS READING, not as the
text's own unit. Build 13's place half with `get_effective_house` (Alcabitius divisions, the 5° allowance at the
four axial degrees). Record on the page, as three separate statements, and pin the strings: (i) PN IV IX.9, 13
supplies the requirement itself: 'in a stake or in what follows a stake', together with the additional
sign-condition requirement ('as well as in its sign', from 12); (ii) the project canon
(OWNER_RULING_PLACES_VS_DYNAMICS_2026-09-11.md) supplies its operational interpretation -- strength/fitness
language -> the divisions; (iii) Alcabitius and the axial 5° allowance come from that adopted convention, not from
the text. Historical confidence in the exclusive division reading stays QUALIFIED: the witness to cite is PN IV
IX.5, 4 fn 106 (p. 602), where Dykes glosses 'rotation' as 'either to their being in the good or bad places, or to
their dynamic angularity (advancing or withdrawing), here and in 7, 11, and 14' -- both spatial readings expressly
left open in the closest parallel (IX.5, 9, p. 603, fortunes 'in the stakes or what follows them' -> 'might, power,
rank, reputation, class, and their endurance', the same triad as IX.9, 13). Cite fn 106 on the page as the
sign-vocabulary witness (it is closer and more directly comparable than V.1, 28 fn 15, which may be cited beside it
but not instead). Drop 'unit awaits the owner'; the row cites IX.9, 13 and the caption says the unit is the canon's."

### GAP-37 / PN4R-4b-4 (ruled: (e) EXACT AXES, numerical tolerance only)

| Item | Commit | What was done |
|---|---|---|
| C GAP-37 | c71be46 | `pn4_axis_of(lon, asc, mc)`: on the Ascendant / Midheaven / IC degree by `PN4_AXIS_TOLERANCE = 1e-9` degrees (floating-point equality, documented, not an orb); the Descendant not an axis (fn 15). `pn4_timing_bundle` lists EVERY planet: on an axis -> directed as that degree is (Asc by OA, MC/IC by RA, unchanged); otherwise `PN4_SEMIARCS_UNAVAILABLE` = "Requires proportional semi-arcs; calculation unavailable." with no fall-back to RA or OA. `get_effective_house` and the carry-over leave the path. Caption item (5) and `PN4_ASCENSION_RULE`'s three strings rewritten ("a planet on the degree itself (numerical tolerance, no orb)"; 'anything else' = the sentence, "Not a prohibition: III.1, 5 directs all planets and Lots", the method "Ptolemy's as Dykes identifies it (III.1, 12 fn 16; VI.2, 21 fn 33), the formula stated in no text in hand" -- both footnotes verified in the corpus: fn 16 at `persian_nativities_iv.md` line 6125, fn 33 at line 9122). Tests: the signed-offset table (dl in {-6, -3, 0, +3, +6}: only 0 selects RA), the exact Asc and IC, the tolerance's edge (2e-9 out, 5e-10 in), wraparound (axis at 0, a point 1e-12 under 360), independence from `FIVE_DEGREE_CARRYOVER`, a real chart with Saturn moved onto the MC and 3° past it (tenth division, unavailable), Venus on the Ascendant, Mars on the IC; the tautological comparison to `get_effective_house` is gone. THE ORDER'S UNIT (division with carry-over) IS SUPERSEDED BY RULING. `tables.json`: the seven angle-planet tables under "The distribution from the Midheaven and the fourth" (2 + 2 + 2 + 1 on four dates) removed -- no fixture planet stands on an axial degree to the tolerance; the two meridian tables per date stay. Corpus: the (e) addendum to `OWNER_RULING_PLACES_VS_DYNAMICS_2026-09-11.md`. |

The owner's GAP-37 ruling, quoted: "(e) EXACT AXES, numerical tolerance only. ... 'In the Ascendant / Midheaven /
fourth' means ON the axial degree, recognised with a documented NUMERICAL tolerance (floating-point equality, not an
astrological orb -- no 3°, no 5°, no band). The three axial degrees themselves stay directed exactly as now (Asc by
OA, MC and IC by RA). Every planet not on an axis is listed with the sentence 'Requires proportional semi-arcs;
calculation unavailable.' -- a computational gap, NEVER a prohibition: III.1, 5 directs all planets and Lots. Do not
fall back to RA or OA to produce a number; do not say PN IV excludes the planet. `get_effective_house` leaves this
path entirely; the 5° carry-over and the divisions have no role in method selection. ... The Descendant stays out
(fn 15: omitted by the author)."

**Left for the next order (authorised by the owner, AFTER the PR merges -- not in this round):** (f) Ptolemy's
proportional semi-arc direction for off-axis points, an OUTSIDE-CORPUS IMPORT authorised by the owner, to be
labelled on the page "Ptolemy's method as Dykes identifies it (III.1, 12 fn 16; VI.2, 21 fn 33); the formula is
stated in no text in hand"; readings to declare when built: body vs ecliptic projection, upper vs lower
culmination, the Descendant's descension, the tolerance. The engine's `_semiarcs`, `_ra_decl`,
`_oblique_ascension` are the primitives. When (f) lands, the "unavailable" sentence is replaced by the arc.

### D. The checker's notes (§2 "notes that are not defects")

| Item | Commit | What was done |
|---|---|---|
| GAP-37 test | c71be46 | Superseded by ruling (e): the signed-offset table replaces the "3° past in, 6° past out" near-miss; the tautological comparison to `get_effective_house` is gone. |
| DEC-D-15, PN4R-4n-2 / F14 | (this commit) | The page strings pinned in the tests that already cover the functions: `test_d15_mars_west_orb_...` asserts the checkbox label and "Dykes's table for Sahl (the chapter head of On Nativities 1.22, with fn 175 ...)" with "Gr. Intr. VII.2, 31"; `test_ii3_lists_the_planets_whose_twelfth_parts_...` asserts the row's Source "II.3, 2; VI.4; Gr. Intr. V.18, 3 (Figure 57)", the `_twelfth_part_sign` PROVENANCE line and the caption's "is stated at Gr. Intr. V.18, 1-3 (Figure 57)". |
| PN4R-4c-4 | (this commit) | The day-direction selector's help says the "houses" of IX.7, 31 are offered as the revolution's Alcabitius cusps -- a reading; the sentence names no degree. |
| GAP-2 | (this commit) | The row's text now says 1.23, 23's "in an excellent position relative to the Ascendant" (1.24, 5 the same) is not judged; pinned. |
| PN4R-4a-2 | (this commit, log only) | Recorded here, as the checker asked: III.7, 42 is checked against the RELEASER'S DISTRIBUTION as the fourth distribution, not the house-master's direction the order named, because the house-master's direction (`sahl_house_master_direction`) is a target list -- the arcs from the house-master's degree to each cutter -- not a bound distribution with a distributor and partner, and III.7, 42 asks which distribution's distributor and partner confirm the indication; the releaser's is the one bound distribution the page has that the order's list lacked. A departure from the order's letter, right in substance; the cell names its distribution. |
| PN4R-4n-7 | (this commit) | Alphecca and Menkalinan relabelled: not "doubtful in Sahl" -- fn 73 "Sahl (following al-Andarzaghar) classifies this as Jupiter-Mercury", fn 75 "... with Jupiter-Mars"; the table shows Rhetorius's nature with Sahl's named; the comment corrected; pinned. |

### Review round: suite and shas

- Full suite in the worktree at 3b5fce2: **1990 passed, 0 failed** (8m 47s). Collected 1982 -> 1990: A1 +4
  (the governor fixtures), A2 +1, A3 +1, A6 +2 (the bundled catalogue; the absent-catalogue fallback).
- `tests/fixtures/tables.json` moved twice, deliberately: 8c43dc4 (+1 table per date on the victors page,
  "Governor of the syzygy degree: the five lords under 1.7, 3-7"); c71be46 (-7 angle-planet tables under
  "The distribution from the Midheaven and the fourth", the ruling (e) leaving no fixture planet on an axis).
- Corpus `astra-session-2026-09-11`: 7c1f1cd (the two measures, the D2 addendum, the caveats correction, the
  rulings addendum; the check prompt, the check report, the fix prompt and the GAP-37 reading filed).
- Not certified by the builder: the owner will have the checker re-run its §2 and §5 against 3b5fce2.

### Review round, follow-up (2026-09-11, later): the Windows build

The owner's Windows build of the branch printed "Not computed: no Swiss Ephemeris star catalogue
(sefstars.txt) is available to this interpreter" while the Linux run shows the tables. Read from the
code, not reproduced (no Windows box here): the file is in the bundle (`_internal/ephe/sefstars.txt`),
so the failure was in the attach -- a symlink (refused on Windows without Developer Mode), the copy
into `%APPDATA%\TraditionalAstrologyEngine\ephe_stars`, or Swiss Ephemeris's narrow `fopen` on that
path -- and `except Exception: return False` turned it into the wrong sentence. Fixed (this commit):
the bundled directory is attached DIRECTLY (`swe.set_ephe_path(ephe/)`; it holds only the catalogue and
a README, so the Moshier invariant stands, the flag test pins it), with no link, copy or user directory;
the link-or-copy path remains for a catalogue found elsewhere; and the refusal now says WHY, in the
order tried ("no sefstars.txt at the bundled path ..." / "found ... but Swiss Ephemeris could not read
it from ...: <exception>"), so the next Windows screenshot is diagnostic. Tests: the bundled directory
attached directly; a found-but-unreadable catalogue reported with the exception; the absent case's
refusal names the path. Whether this is the Windows cause is for the owner's next build to show.

### Page text carries no build process (owner, 2026-09-11, evening)

The owner, reading the Windows build: "strip metacommentary from the build process from the final
product. Referencing D3 & OCR artifacts isn't helpful to the end user." Policy, applied in one commit
across every page string in `app.py` (about a hundred strings) and pinned by
`test_page_strings_carry_no_build_process` (every non-docstring string literal is scanned):

- KEPT: volume locators and footnotes; "a reading"; "not built"; "stated in no text in hand"; quoted
  sentences; the units and the dispatch stated as a rule ("strength language -> the division").
- DROPPED: dates; decision / order / finding ids (D-4, DEC-D-18, FINAL-A1, order GAP-39, PN4R-4c-4,
  REL-5-7); process filenames (`PN4_REPAIRS_...`, `synthesis/13_open_decisions.md`,
  `process/TIMING_SOURCES_REPORT...`, `OWNER_RULING_PLACES_VS_DYNAMICS`); "the owner", "ruled",
  "decision sheet row", "the second blind reading"; "since <date>", "the earlier default", "retired
  2026-09-11"; the OCR / corpus-repair narrative (the Timing notes' D-3 and 25″ paragraphs, ad81dd6).
- REPHRASED: "the owner's ruling of 2026-09-11 (FINAL-A1)" -> nothing or "this app's convention";
  "the canon's dispatch" -> "this app's convention for strength language"; "(decision D-23)" in every
  polar refusal -> "the ascension has no unique inverse there"; "the corpus" (meaning the texts) ->
  "these texts" / "the texts' own vocabulary"; "the project canon (OWNER_RULING_...)" in IX.9, 13's
  statement (ii) -> "This app's convention on places and strength".
- Comments and docstrings keep every id, date and filename: they are the audit trail.
- While there, four stale scope claims on the Sources page were corrected (`NOT_IMPLEMENTED_COVERAGE`
  still listed the releaser and house-master, 1.18's ascensional distribution, 2.13's bands and the
  thirty fixed stars as not implemented; what remains unbuilt of each is named instead), and the
  Reference page's planetary-years caption no longer says nothing in the app grants years.

### Third check (`BUILD_PAGETEXT_CHECK_REPORT_2026-09-11.md`, engine 9970578): READY for PR #2; its residue taken

The checker found no doctrine lost in the page-text pass, the four scope corrections right, the eight
polar refusals true of their sites; suite 1992 green; `git diff 4c3f516 2332217` empty. Its residue,
all low, taken in one commit: P1 -- the Windows-shaped refusal ("found ... could not read it; then no
sefstars.txt at the bundled path ...") no longer denies its own first clause: the fall-through reads
"no other sefstars.txt in $SE_EPHE_PATH, the user data directory or site-packages" when the bundled
file was found and failed; tested with the bundled file the only one visible. P2 -- six residual
process strings the pass missed ("corpus disagreement #3", "The corpus's own vocabulary" -- the guard
was case-sensitive --, "unattested in this corpus", "not in this corpus", "became legible only when the
missing pages were rephotographed", "deliberately incomplete for weeks") reworded; the guard now
case-insensitive with "this corpus", "corpus disagreement", "rephotograph", "for weeks" added
(the "order XX" marker kept case-sensitive so "order of", "ORDER BY" pass). P3 -- the VII.6, 52
own-nodes entry left `NOT_IMPLEMENTED_COVERAGE` (it is built; the reading is on the Configurations
row). P4 -- a star the attached catalogue cannot read is now named on the Timing page with its
exception (`fixed_star_missing_note`) instead of vanishing; tested. The checker's §7: the corpus
spells III.1, 13's thirds `25""` (ASCII), not the ‴ glyph the page prints -- the page's glyph is the
printed book's and stands.

## GOV-1.7 (2026-09-11, evening; branch `governor-1.7-2026-09-12` from main 2d47c45)

The syzygy-governor row rebuilt on the owner's ruling after Astra's blind reading
(`process/astra_2026-09-11/1.7_governor_packet.md`, `1.7_governor_independent_ruling.md`,
`1.7_governor_ruling.md` -- option 3, BOTH). The build checks had flagged two readings the row
carried by implication (the Sun never in 3's eastern pool; 7 scored as a sum); Astra ruled on
those and on three more (the syntax and order of 3-7; the Moon's side; the moment) and raised the
stakes' unit.

| Item | What was done |
|---|---|
| The verdict | `sahl_syzygy_governor` now names a planet only where the text's clear subcases decide: (1) eligible = direct and looking (4, as eligibility); (2) 3's preference among claim-holders, not a veto -- a western eligible candidate is set aside only by an eastern one with at least as many claims on the degree ("if [one] had superior claims over the rest"); the Sun's side is NOT APPLICABLE, so 3 neither prefers nor sets him aside; (3) 7's clear subcase -- a listed advantage (a stake by the division; own house, exaltation, triplicity, bound; the image not restored) against none; (4) one left -> the governor with its steps; more -> "unresolved between X and Y", the profiles printed, the unmodelled stages named (`SAHL_1_7_UNMODELLED`: 4's "stronger in its [own] place", 5-6, 7's ranking among advantage-holders). 1.20, 2-4's ranking not imported. |
| The model | The arithmetic as built at 8c43dc4 kept as `model_pick` / `model_how`, on the page as "This app's approximation of 1.7 (one point a listed condition)" with the disclosure in Astra's words (`SAHL_1_7_MODEL_DISCLOSURE`): the eastern pool first, the Sun having no side; one point a listed condition; 4's place strength and 5-6 omitted; equal totals model ties. The candidates table carries "Model points" and "Model" (the pick) columns. |
| Stakes | The canon's division kept (owner), with Astra's notation on the row: the text's own word for the stakes is the counted sign (The Introduction Ch. 2, 31). |
| Declared | The Moon's side by the same rising-before-the-Sun rule (Gr. Intr. VII.2, 4 names her right and left, not "eastern"); every condition in the NATAL chart (the natal context of Dykes's comment extended to 3-7). |
| Tests | The only eligible lord; the Sun retained against an eastern rival -> unresolved, the model's pick beside it; 3's preference not a veto (a western Jupiter with three claims not set aside by an eastern Mercury with one; a western Mars with one claim set aside); 7's advantage-vs-none, and two advantage-holders unresolved with the model calling a tie; the page strings pinned (adjacent literals joined before matching). |
| `tables.json` | The governor table on the victors page gains two columns ("Model points", "Model") on all six dates; nothing else moved. |
| Page text | Under the no-build-process rule: no ids, dates or filenames on the row or in the caption. |

## 2026-09-12: the page-text review and the owner's decisions (branch `governor-1.7-2026-09-12`, PR #3)

The review of every string the pages print is `process/astra_2026-09-11/PAGE_TEXT_REVIEW_2026-09-11.md`
(corpus d1b8835). Taken:

| Commit | What |
|---|---|
| 60979d8 | LOT-BASIS (`process/astra_2026-09-11/LOT-BASIS_order.md`): the Lot of Basis is stated at Gr. Intr. VIII.4, 22-24 ("the Lot of firmness and survival, the Lot of the Ascendant's support", fn 67 the Greek Basis): Fortune to the Invisible from the Ascendant, reversed at night, coincident with the Lot of Venus and Sahl's Lot of passion (VIII.4, 24; VIII.7, 5). Built as a `LOT_DEFINITIONS` row; the app's unsigned-shorter-arc construction retired; the Lot of Spirit's provenance corrected to Gr. Intr. VIII.3, 28-29 (it had said "the course tables"). Fixture: a night chart where the constructions differ. NOT YET CHECKED BLIND. |
| 6907f8f | A3-A9: three sentences overtaken by the canon and GAP-37 (the quadrant-divisions help, the special-degrees help, the Sources page's III.1, 12 summary); the turning tables' three refusal wordings replaced by the one sentence ruled for the semi-arc gap; the syzygy help leads with the governor; the layout help; a typo. |
| d683f4e | B, on the owner's ruling that course material not in hand is not cited: every "Lesson N", worksheet line number, "Handy Tables", "Course Glossary", "course materials" and "course default" off the pages; the exaltation degrees cited to Gr. Intr. V.5 (Figure 38) and V.7 (Figure 39) instead; ibn Ezra's victor and the almuten labelled techniques from outside these texts; the coverage list's photography narrative and a code constant's name dropped. The reading-depth radio and its labels stay (owner). The guard test now flags course citations. `tables.json`: "Course default" -> "Default". |
| 80625db | C and D: Alchabitius (Dykes's spelling; the Latin form he prints), PN IV (the title), whole-sign as the adjective (Dykes's usage), Dykes's, fn N, Ch. N; the app as the actor; "Chronocrator Matrix" without its gloss; Lots, not Arabic Parts (Dykes's usage). `tables.json`: three headings / one column renamed. |

Suite at 80625db: 1995 passed, 0 failed (8:50). Also on this branch: ff64ae8 / 950297f / e5124d3 (the
Chart intro rewritten and the Square layout's paragraphs), 4e84e44 (the lesson captions under the
page headers excised).

Left open, for the owner: the two delineation tables ("Rhetorius / PN IV readings for these
placements" and "Masha'allah readings for lord placements") are paraphrases of the course's
Reference Guide for the Planets and Places (Dykes 2023), and their two [UNCERTAIN] cells name it;
the Guide is course material not in hand. Either the tables stand as the one named exception, or
they go, or the Masha'allah one is re-sourced to Sahl's own chapters (in hand) and the Rhetorius
one dropped. Not decided here.

The Reference Guide item above is closed: the owner supplied the Guide (corpus `course/TNAC_Reference_Guide_for_the_Planets_and_Places.pdf`, filed with its own statement of sources), so it is in hand and the two delineation tables now cite it by name with the Guide's sources -- Rhetorius Ch. 57 / Mathesis III (not in hand; the Guide's summary the witness) and PN IV Book II's lord of the year in the places, applied to natal planets, the Guide's reading -- and the Masha'allah table Sahl's lords-of-places chapters. The two [UNCERTAIN] cells (the Moon in the sixth and eighth, where the Guide prints ?) stand as pinned.

### Fourth check (`BUILD_PR3_CHECK_REPORT_2026-09-12.md`, engine ea43229): three wording defects, taken

The checker walked Astra's nine policy cases through `sahl_syzygy_governor` by probe -- all nine AS
RULED -- and found the LOT-BASIS arithmetic, the coincidence with the passion Lot, the quotations
and the Reference Guide citations as they should be. Three defects, all wording, fixed in one
commit: D1 -- the Reference page had said Hermes's exaltation degrees "differ by a degree for
Saturn, Mars, the Sun, Venus and the Moon", the old Handy Tables claim re-attached to Gr. Intr. V.7
Figure 39, which contradicts it (Figure 39 differs only for Jupiter and Mercury, the 16th degree of
Cancer and of Virgo); corrected, and the constant's comment with it. D2 -- the coverage list's
Figure 90 entry said "computed for the chart, not scored"; nothing computes it (the set is read by
no function); now "recorded; neither computed for the chart nor scored". D3 -- the governor row's
verdict credited "1.7, 3's eastern preference" as a step of any governor when anyone had been set
aside by 3, including a western Moon and the Sun; the verdict now names who was set aside by whose
preference ("1.7, 3's preference for the eastern Jupiter set aside Venus") and who by 7; the
checker's probe is a test. Two of the checker's notes for the owner: the unweighted count of claims
in 3's "at least as many claims" lets an eastern image-lord set aside a western house-lord (the
builder's operationalisation, written into the ruling's work order, not a choice the owner made in
words); and the Releaser tab's warrant, after the course citations came out, rests on Carmen fn 187
and fn 109 for the dispatch but no longer says where Alchabitius specifically and the axial-only
five degrees come from.

The owner's decision after the fourth check (2026-09-12): note 1 (the unweighted count of claims in 3's
preference) stands as built and declared; note 2 -- the two course citations are RESTORED (a9c8314):
a citation reproduces nothing, and the Releaser tab now says Alchabitius and the axial-only five
degrees are the course's (Lesson 3, A Chart Tour, §4-5; the Course Glossary s.v. Advancement) and the
retired-switch note that 1.18, 19's four stakes are the course's reading (Lesson 3 §4-5); the guard
allows exactly these two strings. The exposure for a public release is the two delineation tables,
paraphrases of the Reference Guide's cells: work order `process/astra_2026-09-11/DELIN-TABLES_order.md`
(re-derive the Masha'allah table from Sahl's chapters and the PN IV column from Book II, each cell
citing its sentence; the Rhetorius column by permission, by acquisition, or dropped). Not started.

## 2026-09-12: the repository tidied for release

The build logs, audits, briefs and `synthesis/` moved under `docs/` (this file included); references
in comments and docstrings updated; nothing reads them at run time. `README.md` rewritten; the
desktop build workflow now runs on a `v*` tag (or by hand) and attaches the zips to a GitHub release
on this repository instead of keeping artifacts; `TAE-Releases` retired to a pointer.

## 2026-09-13: the lords of the triplicity over the life (F-4)

The brief `docs/TRIPLICITY_LORDS_OF_LIFE_BRIEF_2026-09-13.md` asked which passage grounds a
whole-life table of three triplicity lords in succession, and whether the Ascendant (which fits
Janus's one data point) or the sect light (VI.2, 4's point) is the right key. Corpus search:
the division is Sahl's, *On Nativities* 2.11, 1-4 (Theophilus; fn 148: *Carmen* I.24), with
2.13, 39 and 2.17, 5, always for the luminary's triplicity; no text keys it to the Ascendant,
whose triplicity lords are the upbringing lords (1.29). No text gives years. Owner's rulings:
no years shown; the Ascendant rows built as a labelled comparison, off by default. Built
`triplicity_lords_of_life()` beside `pn4_turning_triplicity_lords()`, sharing a factored-out
`_triplicity_lords_in_sect_order()`; the VI.2, 4-5 rows and their test unchanged. Timing page,
last tab, before the *fardar*. Three tests, one on the Pontiac 1990 chart. Details in
`docs/synthesis/16_open_features.md` F-4.

## 2026-09-13: the citation check and the second-model pass (PRs #12 and #13)

Every citation in `app.py` (1,421) was resolved against the corpus's numbered sentences by
`process/citation_check_2026-09-13/` in the corpus repository (1,404 resolve; the 17 that do not
are Carmen via footnotes, three untranscribed Gr. Intr. chapters, one heading-as-sentence, one
false match), then judged sentence by sentence by Claude Haiku 4.5 and triaged by hand. One
defect survived: the misquotation of IX.8, 123 at the head of the releaser section (PR #12). A
long-context pass by Gemini over the three author-blocks with the figures attached reported eight
findings; four held against the text and the photographs, four did not (its reading of Figure
142 was of the wrong image; its reading of Figure 121 was wrong too, and the builder confirmed it
wrongly -- caught by the check below; the further 1.38 sign categories are a coverage note, not a
defect).

Owner's rulings on the five, built on `gemini-findings-2026-09-13` (PR #13):

- **Sahl's degrees of nobility and rank** (*On Nativities* 1.38, 39-41, Figure 57): his own
  table of the rule Gr. Intr. V.22, 4 also states, eight signs to Figure 64's twelve, six of the
  eight disagreeing. `NOBILITY_DEGREES` and `evaluate_nobility_degrees` (the Ascendant, the Sun,
  the Moon; the sect light "superior"); a Chart-page finding beside Special Degrees; the table on
  the Reference page. Abū Ma'shar's V.22 tables are now behind *Course text and supplement* only
  (off the Course-text tab on Configurations; a second column on the Reference page at that
  depth). The Figure 57 cells are from the transcription, not yet read off the page (Sahl I
  p. 378).
- **The Lot of the father, Saturn under the rays**: Gr. Intr. VIII.4, 75 prefers Hermes' form
  (Sun → Jupiter by day, reversed by night) to the Mars → Jupiter form Sahl gives at 4.14, 2 (VIII.4,
  74: "some of the people"; fn 92: Dorotheus). A `father_burnt_abu` row, `supplement=True`,
  shown only at that depth on the Lots page and among the revolution's day-points; the same
  Active test as Sahl's row. `LOT_DEFINITIONS` 37 → 38.
- **The revolution wheel's label**: I.6, 2 asks for the houses by degree (the Alchabitius cusps),
  and I.6, 5 for the terminal point profected from the Lot of Fortune and the rest of the
  indicators; the wheel keeps Dykes's whole signs (fn 33) and the Ascendant's arc, and the caption
  now says so. No change to the drawing (owner).
- Wording: Figure 121's note gains Saturn's sign (the Moon 29°59' Aquarius, Saturn 1° Cancer, his
  trine ray to 1° Pisces -- the photograph and fn 149); Figure 26 named as the revolution example,
  and the bounds ring's comment says Figure 51 has none; the "nothing in Sahl" claim on the V.22
  tables withdrawn.

Tests: Figure 57 pinned cell by cell; the evaluator on a constructed chart; the Reference page's
subheaders and the new table; the lot count; `tables.json` regenerated (the new Chart finding on
two of the six charts, the Reference table, the Book V table gone from the Course-text view).

The blind check (`process/astra_2026-09-11/BUILD_PR13_CHECK_REPORT_2026-09-13.md`) held (a)-(g)
with seven findings, all applied before merge: Figure 121 restored (above); the father Lot's
second form quotes VIII.4, 75 whole and carries Dykes's fn 93 objection in its standing; the
"every wheel" claim narrowed (Figure 51 has no bounds ring); the sect-light note quotes 1.38, 40
as written for both sects; Figure 57 prints bare degrees and the pages now say the ordinal
reading is the app's (Figure 64's manner); the out-of-sect gloss softened; the Lots table's
heading names Abū Ma'shar's row when the supplement shows it; a stale harness comment.

## 2026-09-14: Figure 57 read off the page

The owner photographed Sahl I p. 378. Seven rows match the transcription cell for cell; the
seventh row is **Capricorn** (♑ 12°, 13°, 20°), not Scorpio -- a glyph error in the corpus
transcription, carried into PR #13. `NOBILITY_DEGREES`, its comment, the Chart finding's notes
and the test pin corrected; the corpus row and the photograph
(`images/p378_sahl_i_figure_57_2026-09-14.jpg`) committed there. Read against Figure 64: Sahl's
empty signs are now Libra, Scorpio, Sagittarius, Pisces; Capricorn has Abū Ma'shar's 12, 13, 20
without his 14; still six of the eight disagree. The printed caption says "Ch. 1.28, 41" -- a
misprint in the book (the table is in 1.38, fn 528 calls it sentence 41); the app already cites
1.38 and names the figure without the caption's chapter, so no page text moves. Also verified
from the photograph: sentences 42-45 and fnn. 528-529 as transcribed.

## 2026-09-14: Mercury's phase against the sect (coverage list, gap 10)

Source: Firmicus, *Mathesis* III.7 (Dykes), the excerpt read off the owner's photographs:
sentences 7-9 and 26-30 with fnn 186 and 194. The reading is fn 194's: Mercury as a morning
star in a diurnal nativity or an evening star in a nocturnal one matches the sect and gives
"the success that comes from Mercury's phase matching that of the chart"; the other two
pairings are the mismatch fn 186 names and produce "less respected and independent uses of
the intellect and skill". `evaluate_mercury_phase_sect(planetary_data, sect)` returns one row
for every chart from `solar_phase`'s side (eastern = morning star, western = evening star);
the Chart page shows it under Course text and supplement beside the degrees of nobility, both
footnotes quoted whole in its notes. Display only; no verdict reads it. Pinned in
`tests/test_mercury_phase_sect_2026_09_14.py` (the four pairings by hand, the side against
`solar_phase` across 0°, and the 1240 Florence chart: Diurnal, morning star, match).

## 2026-09-14: the Lots of Jupiter and Saturn (coverage list, gap 2)

Abū Ma'shar's seven planetary Lots (VIII.3, 17-50; the list at VIII.6, 7-14): the app carried
Fortune, the Invisible, Venus's (`desire`), Mercury's (`necessity`) and Mars's (`courage`), not
Jupiter's or Saturn's. Two rows added, `supplement=True` like the father Lot's VIII.4, 75 form,
since Sahl's Nativities has neither: **Lot of Jupiter (prosperity, aid, victory)** -- by day from
the Invisible to Jupiter, reversed by night, from the Ascendant (VIII.3, 40-41; VIII.6, 13); **Lot
of Saturn ("the burdensome")** -- by day from Saturn to Fortune, reversed by night, from the
Ascendant (VIII.3, 37-38; VIII.6, 14), the courage construction with Saturn for Mars. Both
quoted whole in their notes. The Lots heading at the supplement depth now says three rows of
his. `LOT_DEFINITIONS` 38 → 40. Test: the formulas by day and by night on the 1240-05-23 chart.

Open to the owner: the course teaches these two under Lesson 18 ("the Hermetic planetary Lots",
as Victory and Nemesis), so whether they belong at the course-text depth rather than the
supplement is a ruling, not a build question; the supplement is the conservative default. Filed
from the corpus text only; Valens (Riley) was filed the same day and is not cited here.

## 2026-09-14: the natures of the planets, Gr. Intr. IV.1 (coverage list, gap 5)

Source: Abu Ma'shar, *Great Introduction* IV.1, 6-12, his report of what Ptolemy said of each
planet's nature (his own objections, 15-43, are not tabled). `PLANET_NATURES_IV1` holds one row
per planet in the app's order: the hot/cold and wet/dry read off the sentence, the sentence's
words verbatim, and the sentence number. The Reference page shows it under Course text and
supplement only, after the degrees of nobility; nothing in the engine reads it. Pinned in
`tests/test_planet_natures_iv1_2026_09_14.py` (seven rows, the order, every quotation in the corpus).

## 2026-09-14: the Moon's phases after Valens II.36 (coverage list, gap 3)

Valens, Anthologies II.36 (Riley's `35K;36P`), read whole from the corpus file: eleven phases,
eight with a degree from the Sun (45, 90, 135, 180, 225, 270, 315, 360), the new moon, the first
visibility and "when it first begins to wane" with none; then "What Each Phase Indicates" with a
ruler to a day for six of them. Built as `VALENS_MOON_PHASES` and `evaluate_moon_phase_valens`,
one row for the chart's Moon by its waxing angle `(Moon - Sun) % 360`, shown on the Chart page
under "Course text and supplement" only (display only; the render fixture is untouched since the
default depth hides it). The text's degrees stand at both ends of the crescent, quarter, gibbous,
second gibbous and second quarter; the app's boundaries are the new moon to 12° after the
conjunction and the final visibility from 12° before it, first visibility 12-45, full moon 180-192,
and the waning phase 192-225 (placed between full and second gibbous, where the "Indicates" list
puts it). The page says so, and quotes the whole "Indicates" passage as Riley has it.

## 2026-09-14: Morin's rules for aspects into good and bad houses (coverage list, gap 7)

Source: Morin, *Astrologia Gallica* 21.II.X (Holden, pp. 105-110), OCR'd to the corpus today.
Built as a supplement, display-only finding on the Chart page after the nobility degrees:
`MORIN_ASPECT_RULES` (eight rows, Fortune/Infortune x favorable/adverse ray x fortunate/unfortunate
house, Morin's own clause, or the same clause marked "one clause for both kinds of house" where
the text gives one clause to both) and `evaluate_morin_aspects()`, which reads the app's existing
whole-sign aspect pairs and takes the aspected planet's whole-sign house as the house the ray falls
into. The chapter never lists the unfortunate houses; 6, 8 and 12 are the app's reading and the
page says so. The "unless it rules over the location" exception is quoted, not tested. The notes
quote the four governing sentences whole; the fixture is unchanged because the default depth hides
the finding. Test: `tests/test_morin_aspects_2026_09_14.py`.

## 2026-09-14: places harming the eyesight (coverage list, gap 1)

`EYESIGHT_PLACES` and `evaluate_eyesight_places()`: Sahl 6.2's four lists (al-Andarzaghar 49-55,
Rhetorius 61-68, the Bizidaj 70-72, Nawbakht 74) and Abu Ma'shar's VI.20, 4-9, each span as
printed, none reconciled; the Sun, Moon and Ascendant tested against them; the rules' conditions
ride in the Text column. The Chart finding is at the supplement depth only: the 1240-05-25 chart
(the Moon 13° Cancer, Praesepe) showed a row at Course text, and `tables.json` was not regenerated.
Readings I was unsure of: 49's "passed half [of it] until she completes 18°" as 15°00'-18°00';
50's bare "(and in 23)" as the 23rd degree; Nawbakht's "the middle of Taurus" as the 15th-16th;
Abu Ma'shar's single longitudes (21°08' Cancer, 15°20' Sagittarius) as the whole degree they fall
in. 73 (Aries first degrees, Capricorn last: "sickly") and VI.20, 3 (Libra, Leo, no degrees) are
not rows. Test: `tests/test_eyesight_places_2026_09_14.py`.

After the check (`BUILD_EYESIGHT_CHECK_REPORT_2026-09-14.md`): the lord of the Ascendant, which 6.2, 48
names, is now read (the domicile lord of the rising sign; one row carrying both roles when it is a
luminary); the Ascendant degree itself is said to be this app's addition; "al-Dafārah" as printed;
Abu Ma'shar's bare 20° and 22° declared as measured whole degrees; "to fourteen" degrees of disagreement.

## 2026-09-15: al-Andarzaghar's triplicity lords by house (coverage list, gap 9)

Source: al-Qabisi I.57b-68 as Dykes prints it in ITA I.13 (pp. 71-76, the corpus file's
marker OCR read against the running text, no photograph needed: every al-Andarzaghar sentence
reads clean; the only oddity is the page break splitting "be-/ginning" at pp. 71-72, and fn
168's "phrased to as to" typo lies outside the quoted words). `ANDARZAGHAR_TRIPLICITY_LORDS`
holds the twelve entries, three verbatim fragments each and the sentence whole;
`evaluate_andarzaghar_triplicity_lords(asc_lon, sect)` gives twelve rows, the Dorothean lords
of each whole-sign house's triplicity in the chart's sect order (the app's reading of
"first/second/third"; I.58's "stronger in being and place" rule is quoted, not weighed). Shown
under Course text and supplement on the Timing page's last tab beside Sahl's lords over the
life, kept apart from them. Pinned in `tests/test_andarzaghar_triplicity_lords_2026_09_15.py`
(every quote a substring of the corpus span; 0° Aries Diurnal: house 1 Sun, Jupiter, Saturn,
house 4 Venus, Mars, Moon; by night the first two swap). No fixture moved.

## 2026-09-15: affliction and fortification after Rhetorius (coverage list, gap 6)

Source: Rhetorius, *Astrological Compendium* (Holden), Chs. 26, 27, 28, 41, 42, pp. 21-24 of the
corpus file; pp. 21 and 24 read off the page images (`pdf024.pdf`, `pdf027.pdf`): the OCR and the
page agree word for word in all four chapters quoted, no sentence differed. `RHETORIUS_AFFLICTION_CONDITIONS`
(13 entries) and `evaluate_rhetorius_affliction(planetary_data, asc_lon, sect)`; a supplement-only
`_finding` on the Chart page, Chs. 27, 41, 42 (and 28, 26, 34) quoted whole in its notes. Readings made:
(1) "aspected by malefics" by whole sign, the four aspects, not co-presence; (2) "besieged" by Ch. 41's
7 degrees, body or ray of any two planets (Ch. 41 names no malefics), the nearest on each side being the
"no other casting a ray in between"; (3) "applying to a destructive [star]" by whole sign, the planet the
swifter, no degree; (4) "becomes in kollêsis" by Ch. 34's three degrees, where Ch. 27's fn 1 sends the word,
read bodily since Ch. 34 lacks the "or by aspect" of Chs. 37 and 39, and with a malefic (the sentence's
object); (5) "is opposed" by any planet, whole sign; (6) "disposed of by one badly situated in the
ineffective houses": the domicile lord in 2, 3, 6, 8 or 12 from the Ascendant, "badly situated" read as
just that; (7) Ch. 26 dominance from the Cancer/Aries example (the other in the 10th sign counted from
the planet, and the 9th and 11th for "another kind"), reported neutrally since the chapter names no harm;
(8) Ch. 42 "terms" read with the Egyptian bounds, "stronger houses" as Ch. 28's 1, 4, 7, 10, 5, 9, 11;
"in proper phase" and "well-configured" are listed but NOT tested -- the chapters define neither. Ch. 41
read literally fires often (five of seven planets on 1240-05-23); it is the text. Test:
`tests/test_rhetorius_affliction_2026_09_15.py` (verbatim texts against the pp. 21-24 span, hand-built
charts for each tested condition, the 1240 chart).

After the check (`BUILD_RHETORIUS_CHECK_REPORT_2026-09-15.md`): kollēsis by degrees alone, across a sign
boundary (Ch. 34 names three degrees, not the sign); the malefic frame said to be Ch. 27's; the
"stronger houses" = Ch. 28 equation said to be the app's. Open to the owner: Ch. 41's besieging read
with any two planets as besiegers, as the chapter has it (four of the seven planets on 1240-05-23),
under the heading "Afflicted" that Ch. 27 gives it -- restricting the besiegers to the malefics is a
ruling, not a reading the text makes. The corpus has "Kollèsis" where p. 23 prints "Kollêsis".

The besieging question answered from the text (ITA IV.4.2, photographed and OCR'd the same day): the
besieging that afflicts is between the malefics (Abbr. IV.21-25; al-Qabisi III.28b), and enclosure by
the fortunes is a condition of its own (Gr. Intr. VII.6 as ITA quotes it; BW VIII.76). The row is
limited to Saturn and Mars, a fourteenth row "enclosed by the fortunes" added under Fortified, the
sentences quoted in the notes; a third body or ray between breaks either. `LOT`-style count 13 -> 14.

After the ITA rulings audit (entry 31): kollēsis is the same-sign connection -- Dykes distinguishes it
from sun-aphē across signs (ITA III.7 comment, p. 136) -- so the across-the-boundary reading made
after the check is reversed; the same sign required again, now with his definition cited.

Reconciliation decision 3 (owner, 2026-09-15): the breaker is ITA's, not Rhetorius's "any third".
A malefic besieging is loosened by the Sun or a fortune aspecting the planet by a friendly aspect
(its body counted with the rays, Figure 102) under seven degrees (Gr. Intr. VII.6; al-Qabisi
III.28b); an enclosure by the fortunes is broken by a malefic body or ray in the region (Dykes's
comment). Both are said on the row rather than dropping it; the besiegers are now found among the
malefics (or the fortunes) alone, so a third body of another kind neither makes nor breaks either.

## 2026-09-15: the victor weights' "older" label, kept with a note (owner's ruling)

The PN II synthesis found the one corpus passage that attributes weights to 'Umar -- Abu Bakr, On
Nativities II.5.14, through al-'Anbas -- giving triplicity 3, bound 2 (the "newer" order), and Dykes's
2010 introduction saying the weighted victor is not found in Sahl or Masha'allah. The course prints
the "older method" as bound 3, triplicity 2. Owner's ruling: keep the course's label as printed, with
a note on the Victors page and in `VICTOR_WEIGHTS`'s comment citing Abu Bakr II.5.14; the bound-before-triplicity order itself is al-Qabisi's "certain people" (ITA I.22),
so only the attribution to 'Umar/Masha'allah is unwitnessed (ITA rulings audit, entry 25). No number changes.

## 2026-09-15: the reconciliation's text fixes (Class 3) and decisions 1-2, 4-8, 10, 12, 15-17, 19-20

Text only, from `docs/synthesis/02_reconciliation_pn_ita.md` (§1 Class 3, every remaining item;
§7's decisions the owner ruled "as recommended"). No computation changes; no number moved. Every
"this app's" that Dykes states is cited to him (the audit's §C locators); PN I/II passages are
paraphrased on pages and quoted only in comments and docs, marked (OCR, unverified), as are ITA
passages off the photographed pages. Branch base `origin/victor-weights-note-2026-09-15` with
`origin/main` (#18, #20, #21) merged in, since 3.8, 3.10 and decision 20 edit text those PRs added.

- 3.1 / decision 5 (relabel only): `PN4_ASCENSION_RULE`'s third case, `PN4_TURNING_DIRECTION_REFUSED`,
  the VI.2, 21 cusp rows, the Timing page's III.1, 12 captions and the "does not settle" expander now
  say the formula is "stated by al-Qabisi (ITA VIII.2.2) and worked by Dykes (ITA Appendix E), not
  built" -- "stated in no text in hand" was false. Comments above `PN4_SEVEN` and `PN4_ASCENSION_RULE`
  carry the locators. Pin moved: `test_pn4_printed_reference_tables_derive_from_the_rules` asserted the
  false phrase and now asserts the true one.
- 3.4 / decision 20: `docs/COURSE_COVERAGE_2026-09-14.md` rewritten -- header no longer says ITA,
  Firmicus, Morin, Rhetorius are outside the corpus; gaps restated against #15-#21 (seven built); the
  Mars row moved under "a corpus text behind it" (Abu Bakr II.1.0, in his domicile by sect); "Not gaps"
  kept.
- 3.5 / decision 7: the Releaser tab's caption (5) names al-Qabisi IV.3's three opinions on the
  fullness's degree (Ptolemy's, the sages', Valens's; ITA VIII.1.2) in place of "no text says"; the
  Moon default is Valens's, the sages' tie rule named and not adopted. Docstring of
  `calculate_prenatal_syzygy` and the readings comment updated.
- 3.6 / decision 1: the Reference page's years caption names the three witnesses for 39 1/2 (Gr. Intr.
  VII.8 with Fig. 146; Abu Bakr I.16; PN IV I.8, 12) and the three for the ordinary mean 69 1/2 /
  66 1/2 (Masha'allah, Book of Aristotle III.1.8; Abu 'Ali, Judgments of Nativities Ch. 4; the Latin
  Gr. Intr. Fig. 108 in ITA VII.2), and says the app keeps 39 1/2. `PLANETARY_YEARS`'s comment no
  longer says the matter was closed by construction.
- 3.7: "this app's convention for strength language" (the Victors page's governor caption, the PN IV
  governor caption, the Releaser tab's unit paragraph) is now Dykes's proposal, ITA Introduction §6,
  with Alchabitius kept as the app's choice among the quadrant systems; the allowed Lesson 3 citation
  stays beside it.
- 3.8: Morin's unfortunate houses -- the 6/8/12 equation stays the app's, the three cited as the
  tradition's difficult averse places, ITA IV.4.1 fn 43 (p. 224, photographed) quoted on the finding.
- 3.9: Valens's Moon phases -- the 12° boundaries are Abu Ma'shar's markers (Abbr. II.27-31, ITA
  II.10.5) applied to Valens's phases, said on the glance, the notes, the comment and the tags; his
  fourth marker (12° before the opposition) named as not used.
- 3.10: al-Andarzaghar's sect order of first/second/third is al-Qabisi's own (I.16, ITA I.7; Gr. Intr.
  V.14, 6 and Sahl 10.2.7, 16 checked in the corpus) -- "this app's reading" dropped from the docstring,
  the comment and the notes.
- 3.11 / decision 6: the almuten relabelled -- "al-Qabisi's weights, ITA I.18; a technique not in
  Sahl" on the syzygy table's row; the governor caption gives the five strengths and fn 210; the
  Victor of the Chart help says the weights and the five places are al-Qabisi's (I.18; VIII.1.4), the
  Day/Hour/Places rows ibn Ezra's, with fn 211's critique. Comments at the almuten scoring and
  `ESSENTIAL_DIGNITY_WEIGHTS`. Pin moved:
  `test_syzygy_governor_rows_are_on_the_victors_page_with_the_relabelled_almuten`.
- 3.12 / decision 2: `get_effective_house`'s "by choice" is now al-Qabisi's "five equal degrees" (ITA
  VIII.1.3; "equal degrees" the ecliptic per ITA VI.1.1 fn 2); the comment above
  `FIVE_DEGREE_ALL_CUSPS` and the Releaser tab's caption (1) name his "or any house" as another
  author's reading, the four stakes kept as ruled, no code alternative restored.
- 3.13: the 15 Libra-15 Scorpio burnt path cited to al-Qabisi III.29 (ITA IV.3) in place of the Course
  Glossary -- the condition-110 clause, the `DARK_SIGNS` comment, the evaluator comment.
- 3.14: Mercury's sect as a morning star cited to Gr. Intr. IV.9 (ITA V.11) in `planet_sect_is_diurnal`'s
  docstring, the hayz comment, the Mathesis comment and the finding's notes; BA II.11's contrary rule
  named as not imported (Dykes: a corruption of Paul).
- 3.15: the names Basis, Victory, Nemesis cited to ITA VI.1.4, VI.1.7, VI.1.8's headings on the three
  Lot rows' sources.
- 3.16: the governor row's Moon note cites al-Qabisi III.8a (ITA II.10.1) for right = eastern, on the
  page and in the comment; the pinned "Gr. Intr. VII.2, 4 names her right and left" kept verbatim.
- 3.17: the seven good places -- Dykes's p. 121 comment (photographed: Sahl "explicitly uses" the
  Timaeus-Dorotheus seven, "praiseworthy", "stronger") and Introduction §6 cited on caption (6) and in
  the `SAHL_GOOD_PLACES` comment.
- Decision 4: the Lot of friends' confidence from "settled" to "reversed at night after al-Andarzaghar
  (al-Qabisi V.14a, ITA VI.2.45), Masha'allah (BA III.12.1) and Dykes's note 72; Abu Ma'shar
  unreversed (Abbr. VI.53; the Latin Gr. Intr. VIII.4)". Formula unchanged.
- Decision 8: the Figure 57 caption (Reference page) and the Chart finding's notes carry Dykes's
  point-at-the-end resolution (ITA I.3 fn 23: 19° for "the nineteenth", the point where the ordinal
  span 18°-19° ends) and name al-Qabisi I.53's third table (ITA VII.9, Figure 118) as disagreeing with
  both and not tabled; the ordinal reading stands as ruled.
- Decision 10: the printed 1.20, 14-15 flag and the coverage entry carry 'Umar's degree reading (Book
  of Nativities I.4.3: one condition does not harm a superior; a "serious" impediment gives the lesser
  years as months or days); "serious" undefined, not coded.
- Decision 12: `docs/synthesis/16_open_features.md` F-5, 'Umar's 30° profection at 12 1/6 days per
  degree (TBN II.4-8; al-Qabisi IV.8), recorded, not built.
- Decision 15: `SAHL_1_7_UNMODELLED` names al-Qabisi IV.5's tie-breaks (stronger in its place; nearer
  the releaser's degree) as another author's procedure, not borrowed.
- Decision 16: `NOT_IMPLEMENTED_COVERAGE` gains "ITA VIII.1.3 (al-Qabisi IV.4-6), with its directions at
  VIII.2.2": his whole releaser and house-master procedure, unbuilt; `16_open_features.md` F-6 the same.
- Decision 17: al-Qabisi IV.4 named on the Releaser tab as the quadrant witness (caption (1)); the Lot
  by whole sign stays as ruled.
- Decision 19: `docs/synthesis/13_open_decisions.md` D-24, the mighty days' ascensional variant (PN
  III IX.7 method 6; PN IV fn 176) recorded, the zodiacal arithmetic kept.
- The Sources page's "How citations are written" now says what *ITA I.22 (al-Qabisi)*, *Abu Bakr, On
  Nativities II.5.14*, *'Umar al-Tabari, Book of Nativities I.4.3*, *Masha'allah, Book of Aristotle
  III.1.8*, *Abu 'Ali al-Khayyat, Judgments of Nativities Ch. 4* and *Abbr. II.27* locate.
- Not done here: decision 5's build (the semi-arcs), 3 (on #22, already fixed), 9, 11, 13, 14, 18 (builds
  or after the marker OCR), 3.2 and 3.3 (fixed on #23 and #22).

Tests: the six named files 403 passed; the whole suite 2040 passed. Two pins moved, both on strings
this order told me to change (above); `tests/test_prose_counts.py` untouched.

## 2026-09-15: the Moon on the third day and the fetus's stay (decision 18)

Reconciliation decision 18 (owner): two course-text findings on the Chart page, Sahl canon, not
gated by the reading depth, display only.

**The Moon on the third day (Sahl)**, cited "Sahl, On Nativities 1.29, 11-12; 1.26, 7".
`evaluate_moon_third_day(chart_data)` -> `third_day_positions(jd)` (the Moon, Sun, Saturn and Mars
by swisseph at birth + 3.0 days) -> `moon_third_day_rows(third, natal_infortunes, asc)`, pure.
The reading of "the third day of the Moon": three days after the birth moment, the birth hour
kept -- Sahl's own words elsewhere are "the position of the Moon, where she is on the third day
from the nativity" (9, 3) and "the position of the Moon on the third day, the seventh, and the
fortieth day" (1.30, 22); no sentence fixes the hour, and the page says the hour is the app's.
"Corrupted" in 1.29's own terms, 1.29, 3 ("safe from the infortunes, burning, and falling"): an
infortune looking by whole sign (the infortunes where they stand on the third day), burned within
the Moon's twelve degrees (Introduction Ch. 3, 103, as `evaluate_corruption_of_the_moon` reads it),
or falling from the stakes by the whole-sign place from the Ascendant OF THE NATIVITY (1.30, 33);
nothing else of the ten defects. The four-footed sign is 1.38, 1's list (`FOUR_FOOTED['On
Nativities']`, the second half of Sagittarius from 15°). Rows: the Moon's degree and place; four
feet; the infortunes looking; burning; falling; corrupted; 1.26, 7 met or not; 1.29, 11's last
clause (the triplicity lords and the fortune in a stake NOT tested, said); 1.29, 12's first clause
("the two infortunes were in the Ascendant or seventh" read as both natal infortunes in the
whole-sign 1st or 7th, said; the second clause not tested, said). Fn 303 (the alternative reading:
the fortune not corrupted on that day) and fn 304 quoted in the notes.

**The fetus's stay (Sahl)**, cited "Sahl, On Nativities 1.8-1.9". `evaluate_gestation(chart_data,
lat, lon)`. What 1.8 lets the app compute: 5-6 only -- the meeting before the birth (the last New
Moon, from `sahl_prenatal_meeting_and_fullness`; fn 40 allows the lunation generally, so the
opposition is a further row when it was the nearer lunation) and its Ascendant erected for that hour
at the birthplace. NOT computed, said on the row: the three divisions of 3-4 and their reading in
7-13 -- the divisions are framed "from the degree of the Ascendant" of a chart the sentence does not
name; Dykes (fn 38, his comment) assumes the pre-conception lunation, which no sentence of 1.8 shows
how to find (the conception is 1.10's matter). 1.9, 1-10 computed as written by
`gestation_moons(jd)` + `gestation_1_9_rows(natal, past, renewed, asc)`, pure: the three Moons
(fn 45), the year read as the calendar anniversary at the birth hour (`_anniversary_jd`; a Julian
year of 365.25 days only where the digits name no day -- Feb 29), the aspects whole-sign via
`_sahl_looks`; every sentence of 2-10 whose condition holds is a row (9's "trine of the Moon or
Ascendant" tests both), the sextile and her own sign named by none and said so. 1.9, 11 (the
meeting of the conception) and 12-13 (the stays; fnn 54-55's 258/273/288) presented, not computed.
Dykes's fnn 47, 49, 51, 53 quoted on the rows they concern. On 1240-05-23 the meeting fell at
sunrise on the birth day, so its Ascendant equals its degree -- a coincidence of the fixture, checked.

Tests: `tests/test_moon_third_day_2026_09_15.py` -- the third-day Moon against swisseph at
jd + 3 computed in the test; hand-built four-footed-and-afflicted (Leo, Mars square) and
not-four-footed cases, falling and burned separately; 1.38, 1's list; every quotation verbatim in
the corpus (sups and entities stripped); the gestation rows carry their sentences, the anniversary
against `swe.julday` (1240 a leap year: 366 back, 365 on); each of 1.9, 2-10 hit once and the
sextile by none. `tables.json` regenerated: on the chart page for each of the six dates two tables
added ("The Moon on the third day (Sahl)" and "The fetus's stay (Sahl)", Item/Value/Text); the
sign-categories table (11 columns, inside its own expander, which the inventory does not read as a
heading) is now listed under "The fetus's stay (Sahl)" as the last preceding subheader instead of
"Special Degrees & Conditions" / "Degrees of nobility and rank" / "Quadrant divisions (Alchabitius)"
-- the same table, re-attributed; nothing else moved.

## 2026-09-15: the years ladder as a supplement fallback (decision 9)

Owner's ruling (reconciliation decision 9): the house-master's years ladder of Abu 'Ali (*Judgments of
Nativities* Ch. 3-4, PN I pp. 233-235, photographed 2026-09-15) and 'Umar (*Book of Nativities* I.4.3, PN II
pp. 13-14), applied ONLY where Sahl's grading prints "1.20 silent". Sahl 1.20 stays the canon and is never
overridden. Engine: `JN_YEARS_LADDER` (the three place sentences, the preface, the four demotion sentences,
the ranks greater / middle / lesser / months / days), `JN_YEARS_TABLE` (Ch. 4's table; the luminaries' middle
years are 69 1/2 and 66 1/2 there against this app's 39 1/2, recorded in `JN_YEARS_TABLE_DIFFERS` and printed on
the row), `TBN_YEARS_RULE` (I.4.3's first paragraph whole), `TBN_YEARS_DIFFERENCES` (where 'Umar differs, by
place), `JN_CH4_ADDITIONS` and `SAHL_1_21_8` (the disagreement), `JN_YEARS_NOTE`, `JN_YEARS_CITATION`, and
`jn_years_fallback(planet, planetary_data, cusps, sect, essential)`, which calls `sahl_house_master_years` and
returns None wherever it grades. Page: the Releaser tab's house-master block, under Course text and supplement
only, when the grade is None -- the class, the count, the steps with their sentences, 'Umar's sentences, the
note; and a last column on the planetary-years table (Fardar, Ages & Reference Tables tab) beside each
"1.20 silent" cell, at that depth only, so `tests/fixtures/tables.json` (course-text depth) is untouched.

The reading of Ch. 3 (said in the note): the place by the division, as 1.20 is placed; ONE STEP for each
impediment the chapter names -- not oriental, peregrine, retrograde, burned up -- since its own three
sentences step angle-not-oriental to middle, occidental-and-peregrine to lesser, and all four to days ("from
the quality of the lesser years and months ... to days"), and "you will observe it likewise for the rest of the
planets' impediments, because it is one rule"; no step below days; "peregrine" = none of the five shares (the
chapter's ladder head names domicile, exaltation, triplicity -- a planet in bound or face alone is not
stepped); "burned up" = the app's under-the-rays fact, as 1.20's grading reads it; the Sun takes no orientality
step; "free from the bad ones" is not tested, since Ch. 4's additions and subtractions are not built.

Which "silent" cases the ladder covers (from `_sahl_1_20_grade` and the 19/22 fallback): (a) a stake,
retrograde and NOT under the rays, unless alien and westernizing (22 takes that) -- JN: greater, stepped by
retrograde and by not-oriental / peregrine as they hold; (b) the eleventh or fifth, direct, not enhanced, in a
share or eastern (a share and westernizing; a share and burned; alien and eastern; the Sun in a share; by day
the fifth even when enhanced, 11's parenthesis being nocturnal) -- JN: middle, stepped; (c) the ninth, a share
without easternization, or alien and eastern, not both retrograde and burned -- JN: lesser, stepped to months
or days; (d) the third, direct, alien and eastern -- JN: lesser, stepped to months (days if burned). The
second, eighth, sixth and twelfth are never silent. On the six fixture charts no house-master is silent
(Mercury on 1240-01-04 is, in the table: lesser, 20 -- peregrine, retrograde); 1240-02-02 (Florence, 14:30)
has the Moon silent as house-master and pins the Releaser-tab render.

Where JN and Sahl disagree: JN Ch. 4, "the square or opposite rays of the fortunes add or subtract nothing
from the kadukhudhāh"; Sahl 1.21, 8 as Dykes emends it, the fortunes from a square or opposition "will <not>
withhold years, but will even add the equivalent of its lesser years" (fn 160: 8-14 "do match TBN I.4.4").
Both are quoted in the note; neither is applied, the app's 1.21 declaration standing. Where 'Umar differs
from JN (quoted on the row): his greater years ask the Ascendant or Midheaven and the planet's own hayyiz;
the eleventh by day and the fifth by night are greater-years places for him; a peregrine planet in an angle
or follower keeps "its own years whether it were peregrine or whatever its condition was -- unless it were
burned up"; a cadent planet under fall, retrogradation, peregrination or descension drops to hours, not by
steps. His reading of the superiors (I.4.3, "not so much ... a serious impediment") is decision 10's note on
1.20, 14-15 and is not repeated. Test: `tests/test_years_ladder_2026_09_15.py` (every sentence verbatim in
the photographed spans and in `on_nativities.md`; Ch. 4's table row by row; Sahl graded -> None; the silent
cases' classes; the supplement column; the Releaser tab at both depths). No fixture moved.

After the check (`BUILD_LADDER_CHECK_REPORT_2026-09-15.md`): the note says the single steps between
Abu 'Ali's stated cases (one, two, four impediments) are the app's reading of "one rule", and that the
count of months or days is 'Umar's and Sahl's, not the chapter's; 'Umar's "greater years" for the
succedent flagged as Dykes's emendation (fn 82); his I.4.4 sentence -- greater years in an angle
"oriental or not oriental" -- quoted against the ladder's orientality step.

## 2026-09-15: proportional semi-arcs (decision 5)

Reconciliation decision 5 (owner): III.1, 12's third case -- "what is not in these three positions is
directed according to what we stated in our book", the method PN IV defers and Dykes identifies as
Ptolemy's proportional semi-arcs (fn 16; VI.2, 21 fn 33) -- is built from the two texts in hand that
state it: al-Qabisi, Introduction IV.11-12 (ITA VIII.2.2b-e, pp. 362-364: the significator's hours
from the angle, the "significator of the right circle", the "significator of the region", the
"equation" of a sixth of their difference by the hours) and Dykes's Appendix E (ITA pp. 402-407:
Gansten's form `PromMD - (SigMD / SigSA) * PromSA = Arc`, which p. 406 shows to be al-Qabisi's with
the 6 cancelled). The `PN4_SEMIARCS_UNAVAILABLE` sentence is gone from its three sites.

**The method** (`semi_arc_direction(sig_lon, sig_lat, prom_lon, prom_lat, ramc, geo_lat,
obliquity)`, with `semi_arc_terms` for one point): RA and declination of each point from its
longitude AND latitude (`swe.cotrans`); ascensional difference `asin(tan phi tan delta)`; diurnal
semi-arc 90 + AD, nocturnal 180 minus it (closed from one AD, as `_semiarcs`); the signed meridian
distance from the upper meridian (RA - RAMC, positive east, before culmination) and from the lower;
the formula, the arc modulo 360; returned with every term for the page. Choices where the texts are
silent, all in the docstring: (1) MD is SIGNED, positive before the meridian in primary motion, so one
formula serves every quadrant and Dykes's +24 23' 27" / +5 43' 16" come out as printed; (2) the
significator's side of the horizon (|MD| <= DSA, the horizon itself counted above) picks the
meridian and the semi-arcs for BOTH points, the promittor's MD taken from that meridian even when it
stands on the other side of the horizon -- for a promittor below coming to a significator above this
equals its rise (OA less the Ascendant's OA) plus its share of its own diurnal arc, proved in the
tests; (3) direct only: a promittor past the place comes round (arc near 360, outside the 120-year
table), converse directions not built; (4) a point that never rises or sets (|tan phi tan delta| >= 1)
refuses with a sentence naming which point, and the distribution refuses above the polar circle as
the Ascendant's does. Al-Qabisi's join across quarters (IV.12c: to the angle between, then from it,
summed) is a DIFFERENT, approximate procedure (it uses the angle's semi-arc for the first leg) and is
not built; the single formula is exact there. The page directs the DEGREE of each point (latitude
0), as the two built cases direct degrees and as Appendix E fn 27 says al-Qabisi's tables did; the
engine takes latitude and the fixture holds both of Dykes's forms. No new unit helper: the Timing
page already reports arcs through `_pn4_distribution_rows` and `pn4_format_arc_time` (III.1, 13), and
the terms table uses the same.

**The fixture** (`tests/test_semiarcs_2026_09_15.py`): Dykes's chart, p. 402's figure -- 4 September
2010, 2:15:09 PM CDT, Minneapolis 93w15'49" 44n58'48" -- cast by `calculate_traditional_chart`
(19:15:09 UT) reproduces the figure's Saturn 4 Libra 33, Venus 26 Libra 57, MC 29 Virgo 15, Ascendant
7 Sagittarius 47, and then EVERY printed term of both examples to the arc-second: A (with latitude,
p. 406) RAMC 179 19' 33", RA Venus 203 43' 00", RA Saturn 185 02' 49", MD 24 23' 27" and 5 43' 16",
DSA 75 57' 21" and 90 10' 46", arc 19 34' 20" (engine 19 34' 20.0"); B (degrees only, p. 407) RA
205 00' 51" / 184 11' 10", MD 25 41' 18" / 4 51' 37", DSA 79 26' 40" / 88 11' 16", arc 21 18' 36"
(engine 21 18' 36.0"). Also: the formula on his printed inputs alone; (b) a significator on the
Midheaven or the fourth gives the promittor's MD (the RA direction); (c) on the Ascendant or
Descendant gives the promittor's OA difference (the OA direction); (d) declination 0 gives 90 and 90
at every latitude, the solstices' arcs swap; the sign and meridian choices; the refusal; the
distribution's segments dated by the engine's own arcs with Venus's body row opening at the B arc;
the bundle directing all seven of Dykes's planets.

**The three sites.** (1) `PN4_ASCENSION_RULE['anything else']` now reads "applied to the degree of
every point on none of the three axial degrees ... stated by al-Qabisi (ITA VIII.2.2) and worked by
Dykes (ITA Appendix E)"; the reference table's caption follows. (2) `pn4_timing_bundle`'s
`angle_planets`: every planet off an axis gets `pn4_distribution_by_semi_arcs` (its degree through
the bounds, `_pn4_distribute` with the semi-arc measure, distributor and partner as everywhere) and
`pn4_semi_arc_terms_rows` -- the significator, the opener of the period now running (or "the period
open at birth"), the promittor reached next: longitude, RA, declination, signed MD naming its
meridian, semi-arc naming its hemisphere, arc in degrees and III.1, 13's time. The page prints them
under a new subheader "The planets, each with its measure under III.1, 12" (help: the sentence, the
formula, the choices), the terms table captioned `PN4_SEMIARCS_SOURCES` = "al-Qabisi, Introduction IV
(ITA VIII.2.2); Dykes, ITA Appendix E"; the refusal sentence is `PN4_SEMIARCS_REFUSED`. (3)
`pn4_turning_rows`: `PN4_TURNING_DIRECTION_REFUSED` is gone -- the turning code needs only where the
direction stands, so `pn4_semi_arc_stand` gives "by proportional semi-arcs: in {sign}, standing from
{degree}; distributor X, partner Y (age a to b)" for planets and Lots (III.1, 12 fn 16) and for
houses other than 1, 10, 4 and for displaced cusps (VI.2, 21 fn 33); the sign is the opening degree's,
since every sign start is a bound start. `_turning_chart` in the doctrine tests now carries a
horizon (armc from the Ascendant's OA). Captions touched: the meridian section's item (5), the
turning table's, the Sahl house-master's, III.7, 42's (the planets' own directions do not confirm
themselves), the "does not settle" expander's entry.

**Cells moved.** `tests/fixtures/tables.json` regenerated (`UPDATE_TABLE_FIXTURE=1`): 84 lines added,
none removed -- for each of the six fixture dates, seven distribution tables (the ten distribution
columns) and seven terms tables (Point, Longitude, Right ascension, Declination, Meridian distance,
Semi-arc, Arc) under the new subheader; no fixture planet stands on an axial degree, so all seven are
the third case on every date. No existing table changed shape. Under the harness's target date the
1240 charts are past the 120-year table, so their turning cells say so, as the other distributions
do.

**Left to the owner.** Whether the page should direct the planets' BODIES (Appendix E part A,
"modern computer programs") rather than their degrees (part B, al-Qabisi's tables); the engine does
either. Whether the planets' semi-arc distributions should count for III.7, 42's confirmation
(not done: no sentence asks it). PN IV's own sentence still states no method; the row and the help
say the method is taken from ITA.

After the check (`BUILD_SEMIARCS_CHECK_REPORT_2026-09-15.md`; the arithmetic recomputed independently and
found within 1" of Dykes's page): the by-counting house rows stand from the CUSP's degree when it shares
the sign -- VI.2, 1/21/23/25 direct a house from its cusp, no sentence from the sign's first degree -- and
defer to the displaced-cusp row when it does not; III.1, 12 quoted as printed in the subheader help;
fn 27's "probably" kept. Fixture rows for the by-counting houses changed accordingly.

## 2026-09-15: fortune and livelihood, the seven classes (decision 11)

Reconciliation decision 11 (owner): the prosperity classifier from Sahl, *On Nativities* Ch. 2 (canon),
with the Book of Aristotle III.2.0's frame and Abu 'Ali's twelve worked charts (JN Ch. 7, Figures 10-21)
as fixtures. Built: `evaluate_prosperity(chart_data)` with `PROSPERITY_SAHL` (forty sentences, each
verbatim in `on_nativities.md`, tested), `PROSPERITY_ALSO` (the BA/JN parallels, the quotations tested
against `pn1_photographed.md`), `PROSPERITY_CLASSES` (Sahl's 2.1, 3-9 numbering; 4 duplicates 2 per
Dykes's comment and is not a key); the Chart page finding "Fortune and livelihood: the seven classes
(Sahl)", rows Class / Ground / Sahl / Also, one row the class and one per further rule met. Display
only. The DELIN-TABLES order (2.14, the lord of the second in the places) is not touched.

**The spine.** Theophilus's paragraph as Sahl carries it, 2.11, 1-5 (fn 148: *Carmen* I.24, 1-8 -- the
source of Abu 'Ali's charts), with 2.3, 1-2 and 2.13, 40 ("let your reliance be on ... the positions
of the lords of the triplicities of the luminaries in the excellent and bad places"): the first and
second lords of the sect light's triplicity by whole-sign place, strong (a stake or what follows one,
fn 149) or falling, and "under the rays" the one further weakness Sahl names (2.11, 5; `solar_phase`'s
Burned / Under the rays). Both strong: class 1 (both in the stakes 2.3, 2's greatest good fortune;
otherwise 2.3, 18's assets without fame). Both weak: class 6. One and one: 2.11, 2's "benefit in the
time of the strong one", the first lord's time the beginning of life (2.13, 39) -- first strong /
second weak is class 2, the reverse class 5. When both fall, 2.3, 6 sends the reading to the Lot:
2.20, 1 and 2 confirm class 6; 2.3, 7 (its "eastern or cleansed" read as "and", fn 87) and 2.3, 9 raise
to class 1; 2.16, 2 and 2.16, 4 ("all" read as both fortunes and both infortunes) give class 3, in that
precedence. "Cleansed of the infortunes" for the spine lords is listed as facts and not judged (the PN IV
governor rows' convention; 2.11, 4 makes the aspect an increase or subtraction; Abu 'Ali's charts read
the places alone -- Figures 11 and 12 have a lord squared by Mars and are prosperity and a kingdom).
For the Lot, its lord and the lords of places, 2.20, 1's own gloss is applied: an infortune with it, or
in its square or opposition, by whole sign.

**Listed under the class, not moving it** (the chapter gives no order for combining them; the twelve
charts apply none): 2.11, 4 the partnering lord (with 2.19, 5 when in the seventh); 2.3, 12 the eleventh
from the Ascendant; 2.16, 5 the motley mixture (its third place disputed, fnn 225-226); 2.16, 6
(bracketed from BA III.2.3, 6) as a supplement row, shown under Course text and supplement only; the
falling of 2.17, 4, 5 (fn 232: not of the sect), 7 (the eleventh from the Ascendant and from the Lot --
Sahl's own, so course text; BA III.2.1 [1.7] and Valens II.21 as Also), 8, 10, 11; the rising of 2.19, 1
(every infortune in a stake, every fortune in what follows), 2; the earnings of 2.21, 1 (the bound by
`EGYPTIAN_TERMS`), 2, 3, 4. The Moon's separation and connection (2.17, 10; 2.19, 2) by degree within
her orb (`PLANETARY_ORBS`) when motions are present. The 15 degrees by ascensions (2.13, 48-51; 2.3, 4-5
with fnn 82-83; 2.16, 3 with fn 222) as a grade row beside the class when the chart carries `armc`,
`obliquity`, `geo_lat`: oblique ascension from the Ascendant, oblique descension from the seventh,
right ascension from the Midheaven and the fourth, the nearest stake behind the lord; bands of 15;
the class itself stays by whole sign. Tested at the equator with obliquity 0.

**Left, with the sentence.** 2.19, 6, "And a native whose planets you find in the bad places from the
Ascendant, and they are looking at the Lot of Fortune, and its lord in an excellent place, then at the
end of his life he will have a good livelihood" -- BA III.2.4 [4.5] has "the stars traversing from the
east toward the Midheaven", and which planets are meant is unsettled; by whole sign it fires on Figure
17 (three planets in the sixth square the Lot, Venus in the fourth), whose verdict is poverty. 2.19,
3-4 (the sect's contrary planets looking at the Lot; the lords in each other's houses, fn 248 garbled),
7-9; 2.17, 6, 12-14 and 2.18 (the lord of the meeting or fullness); 2.20, 3-6; 2.16, 3 except as the
grade; 2.2's fixed stars (already on the coverage list); 2.4-2.10 and 2.12-2.15.

**The twelve fixtures** (`tests/test_prosperity_2026_09_15.py`, each hand-built by sign, 0 degrees
unless a degree is printed, the Lot by `lot_by_id`; a planet at 0 degrees in the Sun's sign is in his
heart, not burned, so no sign-only chart reads 2.11, 5). Pass, the class Abu 'Ali states: Figure 10
(class 6, both lords cadent), Figure 11 (class 1 by 2.3, 18, both succedent; diurnal per the text against
the caption), Figure 12 (class 1, all in angles; Saturn in the eleventh listed), Figure 13 (class 1;
Saturn the third lord "brings them down"), Figure 17 (class 6), Figure 19 (class 5: Mars burned and
squared by Saturn, Venus in the fourth; the Lot at 7 Sagittarius as printed). xfail(strict), Dykes's
footnote quoted: Figure 14 (fn 51: Gemini not succedent, Scorpio not cadent -- by whole sign both lords
in the fifth, class 1, not middling), Figure 15 (fn 52: the Sun in a watery sign, not fiery -- class 5,
not 1), Figure 16 (fn 53: "Saturn is not cadent" -- class 1, not the labor stated), Figure 18 (fn 56:
the Sun in the seventh sign, cadent only by quadrant -- class 5, not 6), Figure 20 (the rise rests on
the Moon as third lord in the Midheaven and a Lot "of the nature of Venus", neither a rule Sahl states;
fn 60 on the Lot -- class 6, not 5), Figure 21 (fn 62: the Lot cannot be where printed; computed it
falls in Capricorn -- class 2, not 5; the Sun's application to Saturn unreceived listed, not judged).
Six of twelve reproduce; five of the six that do not are the ones Dykes himself flags.

`tables.json`: one table added on the Chart page for each of the six dates ("Fortune and livelihood:
the seven classes (Sahl)", 4 columns). The sign-qualities table that follows it has no subheader of its
own and takes the nearest heading, so its inventory line now carries this finding's title instead of
the one that happened to precede it on each date (Special Degrees / Quadrant divisions / Degrees of
nobility): a heading artifact of the inventory, no table changed.

After the check (`BUILD_PROSPERITY_CHECK_REPORT_2026-09-15.md`): 2.3, 18 read as it is written -- a planet in
what follows a stake, or falling by sign, yet in the stake by degrees (the quadrant cusps) -- and cited only
when that holds; a succedent grade without it rests on 2.11, 1-2 and says so. 2.17, 2-3 rendered as Falling
rows (a strong lord, or the Lot or its lord in an excellent place, with an infortune on it), listed not
classing. 2.3, 7's "and the rays" and "from a strong position" restored, the latter said untested. Open to
the owner: whether the Lot's gate is Sahl's "made unfortunate" (2.3, 6) rather than Abu 'Ali's "both cadent";
whether 2.17, 8 ("even if he was a king") should class; 2.3, 19-21 and 2.19, 6 as listed rows or named as
not read.

Owner's rulings on the check's four open points (all as recommended): the Lot's gate stays Abu 'Ali's
both-cadent, with Sahl's wider "made unfortunate" (2.3, 6) named as not applied; 2.17, 8 listed, not
classing; 2.3, 19-21 as listed Decline rows; 2.19, 6 as a listed Rising row on 2.17, 7's footing, BA's
difference in the places named.

## 2026-09-15: Abu Bakr's eye-degrees (On Nativities II.7.3) beside Sahl's

Decision 14 of the PN reconciliation (E4). `EYESIGHT_PLACES` gains a third source, `_EYE_ABUBAKR`
("Abu Bakr, On Nativities II.7.3"), fifteen rows after Abu Ma'shar's seven, each quoting its clause of
the paragraph on PN II p. 238 ("And it must be known that in some signs are some degrees which destroy
vision:", the rule sentence on every row) verbatim from the owner's photographs, the place from Dykes's
footnotes 1025-1034 (Thurayya the Pleiades; the nebula in Cancer; Dafira, Adhafera, and the stars near
the Lion's tail; the face and sting of the Scorpion; the point of the arrow; the spine of Capricorn; the
Pitcher). The `sentence` field is `'p. 238'`, the chapter having no sentence numbers. Sahl's 32 rows and
Abu Ma'shar's 7 are untouched, and the Source column keeps the three lists apart: fn 1024 says the list
is Masha'allah's (Book of Aristotle III.6.2), Dykes calls Sahl's somewhat different, and nothing is
reconciled between them. The finding's citation names the third source; its notes carry the paragraph
whole and say the four points tested are unchanged.

**Ordinal readings taken** (as the existing rows read Figure 57: "the sixth" is 5°00'-6°00', half-open;
neighbouring ordinals one span, as Rhetorius's "seventh, eighth" already is): Taurus "the sixth, ninth,
and tenth degrees" as 5-6 and 8-10 (two rows); Cancer "from the ninth degree up to the fifteenth" as
8-15; Leo "the eighteenth degree, the twenty-seventh, and twenty-eighth" as 17-18 and 26-28 (fn 1028 on
the first, fn 1029 on the pair); Scorpio "the nineteenth and twenty-eighth" as 18-19 and 27-28, no place
named; Dorotheus's Scorpio "the eighth degree, the ninth, tenth, and twenty-second" as 7-10 and 21-22,
two rows whose Place and printed span say "according to Dorotheus"; Sagittarius "the first, seventh,
eighth, and ninth degree" as 0-1 and 6-9; Capricorn "from the twenty-sixth up to the twenty-ninth" as
25-29; Aquarius "the sixth degree, tenth, and nineteenth" as 5-6, 9-10, 18-19.

**Not built**: Hugo's own variants of the list (BA III.6.2, fns 36-43), known only from unverified OCR
of PN I, so neither quoted nor rowed (named in the code comment only); Abu Bakr's rule sentences on
pp. 237-238 (the Sun and Moon besieged, the Moon decreased in light in the sixth, the Tail in the
Ascendant degree, Mars the lord of the sixth, and the rest), which the evaluator does not compute -- the
page says so in one sentence.

Tests: `tests/test_eye_degrees_abubakr_2026_09_15.py` (row counts per source 32/7/15 pinned; the fifteen
spans; every quotation a substring of the photographed page, footnote markers stripped, skipped where the
corpus is absent; the Moon at 9°30' Cancer and 27°30' Leo; the Dorotheus rows; half-open ends; the page
strings). `test_eyesight_places_2026_09_14.py` filters its pin to the two older sources and adds Abu
Bakr's row where 8° Cancer and 0°30' Sagittarius now hit it. `tables.json` unchanged: no fixture chart
has a point in one of the new spans.

## 2026-09-15: Mars in his own domicile by sect (Abu Bakr II.1.0)

Decision 13 (E3 of `02_reconciliation_pn_ita.md`; gap 9 of `COURSE_COVERAGE_2026-09-14.md`): the one
Lesson 10 row with a corpus witness, built as a supplement finding after the page was photographed
(`pn2/pn2_photographed.md`, the block under `*[PN II p. 142]*`; the PDF-text OCR is no longer the witness).

Built: `ABU_BAKR_MARS_II_1_0` (the four sentences of the paragraph verbatim, the footnote marker dropped;
the fortune-aspect clause and Dykes's fn 652 on *insanus* carried for the notes), `ABU_BAKR_MARS_NO_SENTENCE`,
and `evaluate_mars_abu_bakr(planetary_data, sect, ascendant_lon)` beside the other evaluators; on the
Dignities page under the Sect table, shown at the supplement depth only, display only, with a
"Sources and editorial notes" expander that prints the paragraph whole. The condition is the one the
text states -- Mars **in his own domicile** (Aries, Scorpio), the chart's sect choosing the sentence: by
night "a good soldier ... always conquering", by day "lazy in those things in which he ought to make money
... violent and unsound" (fn 652 named on the row) -- not "of the sect" or "contrary to the sect" at large.
Two further cases from the same paragraph: Mars in a domicile of Saturn (Capricorn, Aquarius: "a fatty
liver ..."), and, as a second row when he stands in the whole-sign tenth, the Midheaven sentence ("it was
already stated that if Mars would appear in the Midheaven, and he would rejoice in his own place ..."),
where "rejoice in his own place" is quoted and not tested since the text does not say which place. When
none reaches him, one row says so. Readings, this build's: domicile by sign; the Midheaven as the
whole-sign tenth; "it was already stated" left as a back-reference (the earlier passage falls in the
unphotographed pp. 23-112); the fortune's aspect on "a Mars so disposed" quoted in the notes, not tested.

Test `tests/test_mars_abubakr_2026_09_15.py`: every sentence a substring of the photographed page (skipped
where the corpus is not on the machine); Scorpio by night the soldier, Aries by day the lazy one with fn 652,
Capricorn under either sect the Saturn-domicile sentence, Gemini the no-sentence row, the tenth a second
row (and alone, no no-sentence row). `tables.json` unchanged: the finding is hidden at the default depth.

Left, per decision 13: the other Lesson 10 rows (Rhetorius's and Abu Bakr's of/contrary-to-sect
delineations for the other planets) -- the course's digest is their only witness in hand, and they are not
built. E3's two companions from the same synthesis item, I.12.3 (Mars destroying nourishing by day) and
II.1.1 (Saturn in the Midheaven by night), stay OCR-only and unbuilt.

## 2026-09-15: additions and subtractions to the house-master's years (Abu 'Ali, JN Ch. 4)

The second half of *Judgments of Nativities* Ch. 4 (PN I pp. 235-236, photographed 2026-09-15; fn 27-28),
built DISPLAY ONLY at the supplement depth on the owner's work order. Sahl 1.20 stays the grant of the
house-master's years; the app's 1.21 declaration ("the 1.21 additions" not applied) stands; no sum is formed
and nothing is scored. Engine: `JN_CH4_SENTENCES` (the chapter's five sentences and fn 27-28, verbatim;
'nothing' is `JN_CH4_ADDITIONS` already on the ladder), `JN_CH4_GRADES` (the three grades of the fortune's
addition in the chapter's words: years, months, days or hours), `ABU_BAKR_I15_ADDITIONS` (PN II pp. 129-130,
four sentences) and `TBN_I44_ADDITIONS` (PN II pp. 15-16, five sentences) as witnesses, `JN_CH4_ADDITIONS_NOTE`,
`JN_CH4_ADDITIONS_CITATION`, `evaluate_jn_years_additions(house_master, planetary_data)` (one dict a planet:
planet, aspect, effect adds / subtracts / nothing / not decided, the lesser years, the grades, the sentence,
the reading) and `jn_years_additions_rows` (the same in words). Bundle key `hm_years_additions`. Page: the
Releaser tab, directly under the house-master's years and the supplement's ladder, under Course text and
supplement only -- a `_finding` titled "Additions and subtractions to the house-master's years (Abu 'Ali;
supplement, display only)" with the rows, the glance, and the Sources expander quoting the chapter whole,
fn 27-28, the note, Abu Bakr and 'Umar. `JN_YEARS_NOTE` now says the additions are "listed below planet by
planet and not applied" where it said they were not built.

Readings (said in the note): joined and the aspects by WHOLE SIGN, as the app's other Abu 'Ali readings are
('Umar's "or were with it in one sign" beside it); the fortunes Jupiter and Venus, the bad ones Saturn and
Mars; the luminaries, unnamed by the chapter, get no row ('Umar's sentence on the Sun is quoted as a witness
only); the lesser years from `PLANETARY_YEARS`, whose lesser column Ch. 4's table matches; a fortune's square
or opposition and a bad one's sextile or trine are listed as rows that "add or subtract nothing", since the
chapter rules on them; the three grades are printed on every fortune row at the same count and the grade
is NOT decided, no text defining "middling in strength" or "more unsound" (the app's pattern for 'serious'
in TBN I.4.3); the bad one's subtraction and Mercury's addition are not graded, the chapter grading the
fortune's addition only. Mercury is Dykes's reading (fn 28), marked so on the row: adds when with or
aspecting a fortune (whole sign) and himself sextile or trine to the house-master; subtracts when with or
aspecting a bad one and himself square or opposite; the house-master itself is not counted as his company;
where fn 28 decides nothing -- joined to the house-master, in neither company, in both, or in a company
whose aspect fn 28 does not pair with -- the row says "not decided" and why.

Witnesses. Abu Bakr I.15 has the rule in the same shape ("the fortunes add to the native's years by
conjunction or the sextile or trine aspect, but the infortunes subtract by their conjunction or square
aspect or the opposition"), grades the aspecting planet by ITS place and condition (angles: the lesser
years; retrograde, burned or unfortunate: months; days or hours under more) where Abu 'Ali says "middling"
and "more unsound", and differs twice: a bad one's trine or sextile "from a good place" ADDS its lesser
years, and a fortune "by any aspect ... will always add". 'Umar I.4.4 has the fortunes add their lesser
years when the house-master is not under the rays, an impeded or besieged fortune add months or days, the
bad ones subtract from the square, opposition or "with it in one sign", the fortunes' square and
opposition add (with Sahl 1.21, 8, against Abu 'Ali -- already quoted on the ladder), and the Sun cut off or
add by his own aspects. Both quoted in the expander; neither applied. Test:
`tests/test_jn_years_additions_2026_09_15.py` (every sentence and both footnotes verbatim in the photographed
spans; Jupiter trine adds 12 at three undecided grades; Saturn square subtracts 30; a bad one's trine
nothing; Venus joined adds 8, Jupiter square nothing; Mercury's four fn 28 cases; no row in aversion; the
Releaser tab at both depths). `tables.json` untouched (course-text depth).

## 2026-09-15: witnesses in hand -- the pages' "not in hand" claims amended; the third day of the Moon counted inclusively (Firmicus II.29, 34)

Text only, no computation, for the first six; a one-constant change with its finding's strings for the last.

1. Timing page, "What Persian Nativities IV does not settle". The releaser paragraph now says what two texts
in hand state of the open items: al-Qabisi's choice among the five and the house-master's order with its
tie-breaks (ITA VIII.1.3, al-Qabisi IV.4-6, pp. 355-357 -- the stronger lord in the releaser's place that
looks at it, down the order until one does; equals by the stronger in its own place, then the nearer degree;
no lord looking, the releaser unfit and the next taken), and Abu 'Ali's addition and subtraction (Judgments
of Nativities Ch. 4: a fortune joined or in trine or sextile adds its lesser years, an infortune joined or in
square or opposition subtracts its own, the other rays of each nothing). Stated there, not built; the choice
stays Sahl's. The Indian-rule paragraph adds that the ninth-parts are al-Qabisi's and Abu Ma'shar's too (ITA
VII.5, al-Qabisi IV.16-17, Abbr. VII.22-23, Figure 110) and that no text in hand makes the first ninth-part's
lord the lord of the year. The other four paragraphs untouched.
2. Reference page, planetary-years caption: Valens VII.5 is in hand (Riley's translation, his 4K;5P). His
Sun sentence quoted -- "The sun has half of 120 years and hence receives 60; its minimum period is 19. The
total is 79, half of which is 39 years, 6 months." -- the Moon's said to be the same; 39 1/2 now has four
witnesses to the ordinary mean's three. His Venus is "a complete period of 84" (half 46), not Figure 146's
82: named as a variant not adopted. The PLANETARY_YEARS comment says the same (four and three).
3. Dignities page, "Topical Planets in Houses" help: Rhetorius Ch. 57 and Mathesis III.2-III.13 are in hand;
the Guide's summary is still what the table prints and it has not been checked against them (not attempted).
4. Timing page caption (the paragraph on the Judgments of Nativities not in hand -- it is there, not on the
Sources page, and the Reference page has no decisions table): one sentence that al-Qabisi's own account of
the releaser and house-master (ITA VIII.1.3) is in hand and stands beside Sahl's in the Sources page's
coverage table, not built.
5. Configurations page, right-sidedness notes: Rhetorius Chs. 23-25 (the doryphory in three kinds, the
out-of-sect kind, trine and square over sextile) and Ch. 53 (each planet's doryphory of the Sun) named as
witnesses to the doctrine that arbitrate neither definition.
6. Docstring of the semi-arc direction: ITA's glossary (p. 382) has converse directions as an allowance of
"some later astrologers".

The third day of the Moon. MOON_THIRD_DAY_DAYS 3 -> 2, the birth day counted as the first. The witness is
Firmicus's worked chart, the nativity of Albinus (Mathesis II.29, 21-22 and 34; Figure 34: Mar 14 303 AD JC,
10:43:13 PM, LMT -00:49:56, Rome 12e29 41n54; the Moon 14 58' Cancer, Mars 11 18' Aquarius): "on the third
day the Moon, being established in Leo, full of light, flung herself into the rays of Mars (and this day,
that is the third, operates in a very powerful way in nativities)" (fn 136 -> III.14, 17-19, where the third
day "just like the first" decrees). By swisseph (UT 23:33:09, Julian calendar) the Moon is 0 12' Leo one
day after the birth (168 from Mars), 14 51' Leo two days after (182, on his opposition ray), 29 47' Leo three
days after (196, past it). So the third day is birth + 2. Every rendered string and the notes say "two days
after the birth, the birth day counted as the first (Firmicus, Mathesis II.29, 34, in the nativity of
Albinus; III.14, 17-19)", the birth hour kept; the "this app's reading of the hour" sentence replaced by the
witness; Sahl's sentences stay the rule. New test `tests/test_third_day_albinus_2026_09_15.py` (Albinus's
JD -> the third-day Moon in Leo within 3 degrees of Mars's opposition, one day short and three days past,
the constant 2); `tests/test_moon_third_day_2026_09_15.py` repinned to + 2.0 and the new string.

## 2026-09-16: DELIN-TABLES build A -- the Masha'allah table from Sahl

The first of the three DELIN-TABLES builds (plan of 2026-09-16, s.1-2 and s.7): the 144 cells of
`MASHAALLAH_LORDS` ("Topical House Lords (Masha'allah)", Dignities page) are no longer the Reference
Guide's wording. Every cell is this app's paraphrase of Sahl's own sentence for that [placed-in][ruled]
pairing, read whole from On Nativities' twelve lords-of-places passages -- the lord of the first 1.36,
79-97; the second 2.14, 9-28; the third 3.10, 1-13; the fourth 4.11, 2-23; the fifth 5.1, 78-90; the
sixth 6.3.4, 12-23; the seventh 7.1, 205-216; the eighth 8.5, 2-13; the ninth 9.4, 23-34; the tenth
10.2.4, 1-12; the eleventh 11.1, 16-27; the twelfth 12.1, 35-46 (the sentence ranges confirmed
chapter by chapter; the Guide's "1.36, 78-97" and "6.3.4, 12-24" include the lead-in and the
application sentence). Course text; nothing supplement-gated.

Cell shape. `{'text': <paraphrase>, 'cite': <locator>}`, the locator "chapter, sentence" and a range
where the cell rests on two or three sentences ("1.36, 88-89"; "2.14, 17-19"). `evaluate_house_lords()`
prints the text with the locator in parentheses in the same cell ("... (1.36, 83)"), so the page's
column count is unchanged; the export's citation line for the table names Sahl's passages. Sahl's own
conditions stay inside the cell wherever his sentence has one -- if received, if a fortune or an
infortune looked at it, if the lord of the Ascendant looked at it, if the Moon is corrupted -- and
the Guide's compressions had dropped most of them (restored in some twenty cells: [1][2], [2][2],
[3][1], [3][4], [4][4], [5][4], [6][2], [6][4], [7][2], [8][4], [9][2], [10][4], [11][2], [12][4],
[1][4], [1][8], [7][9], [12][1], [12][5] among them). Dykes's forms throughout: the Sultan, received,
looked at it.

Empty cells: none. Every one of the twelve passages has a sentence for all twelve places, so no cell
is a dash; the help says so, and `test_the_count_of_empty_cells_is_what_the_help_states` pins the
count at zero.

Cell [8][5], the lord of the fifth in the eighth: Sahl 5.1, 85, which Dykes prints as "[illegible]
they will survive and will be miscarried" -- the bracket is the translator's (manuscript E smudged
and a line across the photograph, his fn 47), not this project's. The cell says the children survive
but premature or miscarried, that the manuscript is smudged there, and gives fn 47's sense (the
children suffer or die, the survivors premature); its locator is "5.1, 85 fn 47". No [UNCERTAIN]
marker anywhere in the table.

The application sentences. The caption's quotation of 3.10, 14 ("Work in this chapter if the lord
of the third and the third [itself] were free of the infortunes, and the fortunes do not witness")
is verbatim; the seven "likewise" locators (4.11, 24; 6.3.4, 24; 7.1, 217; 9.4, 35; 10.2.4, 13;
11.1, 28; 12.1, 47) each resolve to that chapter's closing condition. The caption said the condition
is "stated at the end of every lord-of-the-Nth section"; it is not -- 1.36, 2.14 and 8.5 have none,
and 5.1, 91 is a variant Dykes cannot assign (fn 49) -- so it now says "eight of the twelve", the
locators unchanged.

Where Sahl's sentence and the Guide's cell disagreed in substance (the Guide's gist first, then
Sahl's; the cell follows Sahl):

1. [7][1] the lord of the first in the seventh. Guide: "very eager; subordinate to spouse". Sahl
   1.36, 90: many lawsuits, deceptive, subordinate to women in their speech. "Very eager" has no
   source in the sentence; lawsuits and deception were missing.
2. [7][3] the lord of the third in the seventh. Guide: "Marries a relative; brothers hostile or
   marry his women". Sahl 3.10, 7: his brothers marry some of his women and have children by them,
   or else are hostile. "Marries a relative" is 7.1, 207 (the lord of the SEVENTH in the THIRD),
   carried across the diagonal. One of the fourth check's six spot-checked cells; the check found
   it matched the Guide, which it did.
3. [7][5] the lord of the fifth in the seventh. Guide: "Younger spouse; children hostile; deluded
   about women; servant children". Sahl 5.1, 84: children mostly from his maids and serving-women,
   hostile to him, and he deceives himself about the women. "Younger spouse" is 7.1, 209 (the lord
   of the seventh in the fifth), the same diagonal carry.
4. [7][6] the lord of the sixth in the seventh. Guide: "Sick/slave spouse; low-status spouse; bad
   reputation due to spouse". Sahl 6.3.4, 18: associates with women of no social esteem, and bad
   words are said of him. "Sick/slave" is 7.1, 210 (the lord of the seventh in the sixth).
5. [7][7] the lord of the seventh in the seventh. Guide: "spouse has rank of maternal relatives".
   Sahl 7.1, 211: a well-known woman, an equal match, whom he loves (fn 132: "well-known" read with
   al-Rijal for two uncertain words). No maternal relatives.
6. [12][6] the lord of the sixth in the twelfth. Guide: "native sickly or ongoing health problems".
   Sahl 6.3.4, 23: hostile to people of no social esteem, and they come to harm. No illness of the
   native.
7. [5][9] the lord of the ninth in the fifth. Guide: "children religious/educated". Sahl 9.4, 27:
   children in a country not his own, and he will marry; his eye delights in them. Nothing of
   religion or education.
8. [5][10] the lord of the tenth in the fifth. Guide: "Abundance of children; illness/death if
   harmed". Sahl 10.2.4, 5: the children have a chronic illness or disease and die, and hardship
   from the Sultan -- unconditional, and no abundance.
9. [12][10] the lord of the tenth in the twelfth. Guide: "works with large animals/secrets". Sahl
   10.2.4, 12: dispossessed by the authorities, griefs and hardship from them. No animals, no
   secrets.
10. [7][12] the lord of the twelfth in the seventh. Guide: "secret relationships/cheating". Sahl
    12.1, 41: mixes with low women with defects, and they are hostile. No cheating.
11. [11][4] the lord of the fourth in the eleventh. Guide: "bad condition unless received by
    fortune". Sahl 4.11, 20: unless received by the lord of its house; a fortune looking is a
    further improvement, not the condition.
12. [8][2] the lord of the second in the eighth. Guide: "assets taken if connecting to 8th". Sahl
    2.14, 21 distinguishes the direction: if IT connects with the lord of the eighth, assets taken
    by force and he a tax-gatherer; if the lord of the eighth connects with IT, gain from the dead
    and inheritances. Both halves now in the cell.
13. [8][3] the lord of the third in the eighth. Guide: "will not survive OR get inheritance". Sahl
    3.10, 8: the brothers' women do not survive AND they get inheritances in relation to women
    (fn 115 on the tense). Conjunction, not alternative.
14. [1][1] the lord of the first in the first. Guide: "(subject to other conditions)". Sahl 1.36,
    79-81 states them: connecting with a planet in the Midheaven, rank from the Sultan by that
    planet's dignity, or through the loss of religion and honor if it is in its fall. Now in the
    cell.

Smaller wording differences (the Guide's "ruler"/"government/authority" for Sahl's "the Sultan";
"steady employ of the Sultan" for "work for government"; "lives by walking" for "itinerant") are
resolved to Dykes's words without being counted here.

Page. The table's help names Sahl's twelve passages as the source of every cell's wording, says the
conditions are kept and the locator printed, states the count of empty cells (none) and the
illegible cell, and cites the TNAC Reference Guide for the Planets and Places (Dykes, 2023) once,
as the origin of the arrangement (the twelve chapters as a grid), not of the wording. The "Topical
Planets in Houses" help gains one clause: unlike the lords table, it still prints the Guide's
summary (builds B and C). No date, file, or process on the page.

Tests. `tests/test_prose_tables.py`: the lords half of the Guide transcription (`LORDS_PAGE`,
`MASHAALLAH_LORDS_GUIDE`, `MASHAALLAH_LORDS_ANCHORS`, the two lords tests) deleted; in its place
`MASHAALLAH_LORDS_SENTENCES`, 144 rows of (placed_in, ruled, cite, anchors) -- the locator and three
words the cell text and Sahl's sentence share, exact-word on both sides -- and tests that the
fixture covers every cell once; every cell is {'text','cite'} with non-empty text, its cite equal
to the fixture's and matching `^\d+(\.\d+)*, \d+(-\d+)?( fn \d+)?$`, its anchors in its text, no
[UNCERTAIN]; the fourth check's six spot-checked cells as a named regression set ([7][3] must not
say "relative"); [8][5]'s cite carries "fn 47" and its text "smudged"; the count of dash cells is
what the help states (0); the reader prints text + " (cite)". The planets-in-houses half of the
file is untouched. The docstring rewritten to say what the file now pins. The corpus is private, so
the anchors are all the app repo carries; the checker's sentence table (all 144: placed-in, ruled,
cite, file line, the sentence's first six words) is in the corpus repo's process directory beside
the plan. `tables.json` regenerated once: unchanged, since it inventories headings and column
names, and neither changed. Whole suite 2806 passed, 1 skipped, 6 xfailed (main: 2665 / 1 / 6).

After the check (`BUILD_DELIN_A_CHECK_REPORT_2026-09-16.md`: 144 cells verified, none defective, three
notes): [12][1] hangs "in its nature" on the planet as 1.36, 96 does, not on the place; [5][10] names
the children as the ones who meet the hardship from the Sultan (10.2.4, 5); the structural-guard
comment in `tests/test_base_tables.py` no longer says the lords table is audited against the Guide.

## 2026-09-16: DELIN-TABLES build B -- the PN IV column from Book II

The second of the three DELIN-TABLES builds (plan of 2026-09-16, s.1 and s.3, with s.7's decisions:
locator in-cell; the Moon's sixth and eighth filled from VII.8, labelled transit). The PN IV halves
of `PLANETS_IN_HOUSES` ("Topical Planets in Houses", Dignities page) are no longer the Reference
Guide's wording: all 168 (7 planets x 12 houses x Good/Bad) are re-derived from Abu Ma'shar, On the
Revolutions of the Years of Nativities, Book II's chapters on the lord of the year in the houses of
the circle -- Saturn II.6, Jupiter II.9, Mars II.12, the Sun II.15, Venus II.18, Mercury II.21, each
read whole -- and, for the Moon, VII.8, 1-12. Course text; nothing supplement-gated. The application
of a lord-of-the-year chapter to natal planets is the Guide's reading and the help says so in so many
words.

Cell shape. `PLANETS_IN_HOUSES[house][planet]` is `{'Rhetorius': {'Good': {'text','cite'}, 'Bad':
{...}}, 'PN IV': {'Good': {...}, 'Bad': {...}}}`. The reader keeps the page's two columns, If Well
Placed and If Badly Placed, and prints in each `Rhetorius: <text> · PN IV: <text> (<locator>)`
(`planets_in_houses_cell()`); a half with no sentence prints as a dash and no locator. The Rhetorius
halves' cite is '' in this build -- they still print the Guide's summary exactly as this app had
carried it, verbatim, with no locator, and the help says so. Twenty-one Rhetorius halves are dashes
pending build C: the four where the Guide prints "?" (the Moon in the 6th and 8th) and seventeen
where the app's merged cell had carried only the PN IV reading of the Guide row (Jupiter 1st, 2nd,
3rd, 6th, 8th, 12th Bad; the Sun 3rd Bad and 12th Good; Venus 3rd Good and Bad, 5th Bad, 12th Good;
Mars 9th and 11th Bad, 12th Good; Saturn 11th Bad, 12th Good). A first cut of this build had filled
those seventeen from the Guide's own Rhetorius column in short; that was reversed before the check
as the wrong direction -- the order's point is to stop reproducing the Guide's wording, and build C
re-derives every Rhetorius half from Rhetorius Ch. 57 and Mathesis III within days -- so no Guide
wording is added by this build, and `RHETORIUS_DASHES` in the tests names the twenty-one. The
export's citation line for the table names both sources as they now stand.

The split. Each Book II chapter states, per house or house-pair, a suitable-condition reading and a
not-received / made-unfortunate / retrograde reading, and the good/bad halves follow that split
exactly; every Saturn-Mercury half has its own sentence, so none is a dash. The text's own conditions
stay inside the cell (in his own house or received; alien, not received; retrograde; eastern; if Mars
looked at him with a harmful aspect; the lord of the sixth made unfortunate; if the root of his
nativity indicated children). Grouped houses cite the group's sentence: the four stakes for all six
planets (Saturn II.6, 1-3; Jupiter II.9, 1-3; Mars II.12, 1-5; the Sun II.15, 1-3; Venus II.18, 1-5;
Mercury II.21, 1-4), with the per-stake clause each chapter adds kept in that stake's cell (Jupiter's
"because of" clauses in II.9, 2; Mars's Midheaven, west and fourth in II.12, 2 and 5; the Sun's three
in II.15, 2; Venus's fourth in II.18, 5; Mercury's "seventh and fourth especially" in II.21, 3); the
eleventh-or-fifth and the ninth-or-third for all six; the second-or-eighth and the sixth-or-twelfth
for Jupiter, the Sun, Venus and Mercury, while Saturn and Mars have a sentence for each of those
four houses on its own. The chapters' extra group sentences are folded into the halves they qualify
with their locator led inline, since a half has one locator field: Saturn's four falling places
(II.6, 22-23 into his 2nd, 6th, 8th, 12th Bad; II.6, 24 into their Good), Jupiter's four places not
looking at the Ascendant (II.9, 15-16 into his 2nd, 6th, 8th, 12th Bad), Venus falling from the
stakes or what follows them (II.18, 18 into her 3rd, 6th, 9th, 12th Bad), and Mercury's retrograde
clause (II.21, 4 into his 1st and 10th Bad, inside the 4th and 7th's locator range).

The Moon. II.22 has no per-house list: sentence 13 says to judge her in the houses "in the manner of
... the rest of the planets", and Dykes's fn 312 sends the reader to VII.8, her transit through the
twelve houses -- the only such list PN IV has. Her twelve PN IV readings are VII.8, 1-12, one per
house, each beginning "By transit:" and citing `VII.8, n`. VII.8's sentences carry no condition on
her state (each is one mixed list of what happens "so long as she is in it"), so no good/bad split is
made: each reading sits whole in the half its balance belongs to (1st, 3rd, 7th, 9th, 10th, 11th
Good; 2nd, 4th, 5th, 6th, 8th, 12th Bad -- the 7th opens with the parents' disagreement but is
otherwise good) and the other half is a dash. The 6th and 8th [UNCERTAIN] markers retire: the Guide's
"?" there was the absence of a Moon chapter in Book II, not a doubt in the doctrine. (The Guide also
prints "?" in its PN IV column for the Moon in the 2nd and 10th and leaves the other eight blank; all
twelve are now VII.8.) Twelve PN IV halves are dashes, all the Moon's; the help states the count.

Mercury in the 9th. The code had kept the Guide's two halves swapped against the Guide's own headings
(D-16, 2026-09-08: the Guide p. 34 prints "Bad reports and journeys ..." under Good and "Good
journeys, true visions ..." under Bad). II.21, 8-9 settles it the code's way: sentence 8 -- he travels,
sees what he loves on the journey, good visions with a true interpretation, good spoken of him for his
religion -- is the reading with no adverse condition (the sentence states none at all, only "<in the
two times>"), and sentence 9 -- something detestable and damage on the journey, doubts in religion,
bad visions, loss in business -- is the "bad condition, made unfortunate, not received" reading. Good
is 8, Bad is 9, for the 3rd as for the 9th; the Guide's 3rd-house row already had them that way round.
`test_mercury_in_the_ninth_reads_as_ii21_8_and_9` pins it.

Where the Guide's PN IV half and the text disagree in substance (the Guide's gist first, then the
text's; the cell follows the text):

1. The Sun in the 1st and the 10th, Good. Guide: "High rank, good with authorities, management,
   victorious". II.15, 2: in the Ascendant or Midheaven, increase in rank, renowned, a voice among his
   class, good from the Sultan. "Management" and "victorious over enemies" are the seventh's clause
   of the same sentence.
2. The Sun in the 4th, Good and Bad. Guide: "Increase in rank, gain good, commended, especially
   victory over enemies" / "Little benefit, or harm, in enemies". II.15, 2: in the fourth, good
   because of real estate, fathers and old men; 3: little benefit, fear of the Sultan. The enemies
   are the seventh's.
3. The Sun in the 7th, Good and Bad. Guide: "... especially in land, fathers, ancestors" / "Little
   benefit, or harm, land, fathers, ancestors". II.15, 2: in the seventh, different managements,
   victorious over enemies, healthy in body, sees what he loves from women. The land and fathers are
   the fourth's -- the Guide carries the 4th's and 7th's clauses across each other.
4. Mars in the 7th, Bad. Guide: "Misfortune from Martial things and especially illnesses and
   marriage". II.12, 5: in the west, ailments, illnesses, cutting by iron, different distresses, and
   victorious over his enemies. No marriage in the sentence; the victory over enemies was missing.
5. Saturn in the 2nd, Bad. Guide: "Corrupted, from abject sources". II.6, 14: the corruption of assets,
   vegetation and fields, from sinking or water. Flood, not abject sources.
6. Saturn in the 10th, Bad. Guide: "Manager for others; blamed; low work". II.6, 3: he assumes the
   responsibility for someone else, blamed and accused; if a corrupting planet looks at him, harm and
   something detestable. No "low work".
7. Venus in the 10th, Bad. Guide: "Some spoiling, bad reputation". II.18, 2 puts the spoiling on the
   retrograde case of the GOOD reading (he gains what was said, from a direction not good, some of it
   spoiled); the Bad is II.18, 3-4 (disturbed way of life, loss, evil reports, quarrels; Saturn's
   pains, Mars's burning and theft). The retrograde clause is in the Good half now.
8. Venus in the 12th, Bad. Guide: "Leisure time and illness; something bad from enemies, the confined,
   punishment". II.18, 15 for the twelfth is the enemies, the confined, confinement and punishment
   alone; "leisure time and illness" is the sixth's sentence (14).
9. The Sun in the 11th, Good. Guide: "delight in friends and brothers". II.15, 4: he sees what he loves
   from his brothers and delights in children; friends enter only in the Bad (5, friends who have
   authority undermine him).
10. Jupiter in the 2nd, Good. Guide: "Leisure, little work". II.9, 10 continues: except that benefits
    are produced for him without seeking, or because of the dead -- present in the Guide's 8th, dropped
    from its 2nd. Restored.

Smaller compressions (the Guide's "Sultan/govt", "authorities" for Dykes's "the Sultan"; its
"underclass" kept, being Dykes's own word) are resolved to Dykes's words without being counted.

VI.3 (the revolution's planets in the natal places, 9-17 for the first) is a revolution chapter and is
not in this table. The Timing page's indicators caption ("Facts, not judgments: the delineation
chapters behind these rows ... are not built") gains one clause: VI.3 belongs there with them, not in
the natal Topical Planets in Houses table, which reads Book II. Nothing else on the Timing page moves.

Page. The table's help says what each half is: the PN IV halves this app's paraphrases of Book II's
lord-of-the-year chapters applied to natal planets (the Guide's reading, followed and named), the split
kept only where the chapter makes it, the conditions kept, the locator printed; the Moon from VII.8 by
transit, one half per house; twelve PN IV dashes, all the Moon's; the Rhetorius halves the Guide's
summary exactly as carried, without a locator, until re-derived, twenty-one dashes pending that (the
Guide's four "?" and the seventeen the app never carried); the Guide cited once
as the arrangement's origin. The caption under the subheader and the export citation say the same in a
line. No date, file, or process on the page; "the Sultan", "received", "made unfortunate", "eastern",
"laboring", "quarreling" as Dykes has them.

Tests. `tests/test_prose_tables.py`: the planets half of the Guide transcription (`GUIDE_PAGE`,
`PLANETS_IN_HOUSES_GUIDE`, `PLANETS_IN_HOUSES_ANCHORS`, the four planets tests including the two that
required the [UNCERTAIN] markers) deleted; in its place `RHETORIUS_HALVES`, a literal copy of the
Rhetorius halves only (so build C can retire it in turn), and `PN4_HALVES_SENTENCES`, 168 rows of
(house, planet, half, cite, anchors) -- the locator and three words the half's text and the cited
sentence share, or ('', []) for a dash -- and tests that the fixture covers every half once in grid
order; every PN IV half has text; a cite matches `^(II\.\d+|VII\.8), \d+(-\d+)?$` or is '' with the
text a dash; anchors in the text; the Moon's twelve cites all `VII.8, n` with exactly one filled half
per house beginning "By transit:"; no dash outside the Moon's row and the count what the help states
(12); the Rhetorius dashes exactly the twenty-one named (`RHETORIUS_DASHES`); no [UNCERTAIN] anywhere; Mercury 9th as
II.21, 8 and 9; the reader's cell format (a formatted half, a dash-dash, a dash on one side, and the
row function against the formatter). `tests/test_base_tables.py`'s shape guard follows the new nesting.
Two guards outside the table's own tests had to learn the change: `test_abu_mashar_citations.py`'s
Book VII paragraph-range scan read "VII.8, 12" as the Great Introduction's VII.8 (which ends at 8) --
it now skips a citation whose nearest preceding book label on the line is "PN IV"; and the F15 heading
test's pin on the old help sentence ("both texts are now in hand") is re-pinned on the new help. The
anchors were checked by script against the corpus sentences (168 rows, none missing on either side)
before the push; the checker's sentence table (house, planet, half, cite, file line, the sentence's
first six words) is in the corpus repo's process directory beside the plan and build A's. `tables.json`
regenerated once: unchanged, since it inventories headings and column names, and neither changed.
Whole suite 2977 passed, 1 skipped, 6 xfailed (build A: 2806 / 1 / 6).

After the check (`BUILD_DELIN_B_CHECK_REPORT_2026-09-16.md`: 168 PN IV halves verified, one defective,
three notes): Venus 2nd Bad "practices" (Dykes's spelling); the Moon 3rd keeps VII.8, 3's "some of him
and his parents" as printed; the Moon 10th says "takes away the same" with fn 106's guess marked as
his, not stated as the sentence's; the Timing caption's clause about VI.3 now says the II.6-21 rows are
not built as revolution readings, beside the natal table whose PN IV halves paraphrase Book II.

## 2026-09-16: DELIN-TABLES build C -- the Rhetorius column from Rhetorius Ch. 57 and Mathesis III

The third of the three DELIN-TABLES builds (plan of 2026-09-16, s.1 and s.4, with s.7's decisions:
locator in-cell; Rhetorius pp. 51, 52 and 81 photographed and spliced, so Ch. 57 is whole). The
Rhetorius halves of `PLANETS_IN_HOUSES` ("Topical Planets in Houses", Dignities page) are no longer
the Reference Guide's summary: all 168 (7 planets x 12 houses x Good/Bad) are re-derived from
Rhetorius, Astrological Compendium Ch. 57 (Holden), the significations of the twelve houses, read
whole in his order (the twelfth first), and, where Rhetorius is silent on the planet in the place or
says only something general, from Firmicus Maternus, Mathesis III.2 Saturn, III.3 Jupiter, III.4
Mars, III.5 the Sun, III.6 Venus, III.7 Mercury and III.13 the Moon (Dykes), each read whole
(III.8-III.12, Mercury with another planet, not used). Every Mathesis sentence cited was read against
its page photograph. Course text; nothing supplement-gated.

Counts (as pushed at f43e4f3; the after-the-check counts are at the end). 121 halves rest on both
texts, 7 on Rhetorius alone (the Moon in the fifth, the sixth's Bad, the seventh, and the eighth's
Good, where Firmicus's Moon is missing, III.13, 19-22, and Saturn in the third's Good), 23 on
Firmicus alone (the eleventh's Saturn, Jupiter, Mars and Mercury, whose Rhetorius paragraphs are
the fifth's; the Sun in the tenth's Bad, whose Rhetorius paragraph is lost; and the halves where
Rhetorius gives the planet no reading of that valuation), 17 dashes.
Locators: Rhetorius by chapter, house and Holden's page (`Ch. 57, the sixth, p. 76` -- he has no
sentence numbers; the page is the one the sentence begins on), Firmicus by chapter and sentence
(`III.2, 8`), both when both are used (`Ch. 57, the first, p. 52; III.2, 1-2`); the reader prints
each half's locator after its text.

The sect rule (plan s.4.2) as applied. The good/bad halves follow the sentence's own valuation.
Where the only distinction a text makes is sect, the reading goes whole into the half its balance
belongs to and keeps the text's prefix -- "By day", "By night", "In sect", "Out of sect" -- and a
reading that mixes good and ill goes whole where its balance lies, wording kept. Two examples:
Saturn in the second, where Rhetorius (p. 59) and Firmicus (III.2, 8-13) both give a diurnal and a
nocturnal reading, is "By day: the livelihood increases slowly ... undistinguished, unnoticed and
poor in spirit" (Good) and "By night: the loss of children ... the paternal and maternal
inheritance squandered ... serious and perpetual illnesses" (Bad); Mars in the sixth, where both
texts only condemn him (Rhetorius p. 78, III.4, 36-37), has a dash for its Good half and the
by-day/by-night gradation ("especially by day") inside the Bad. Eight planets in a place have no
good reading in either text and so a dash: Saturn, Jupiter and Mars in the sixth, Mars in the
seventh, and Saturn, Mars, the Sun and Venus in the twelfth; their by-day or in-sect mitigations
("by day the evils are moderate", "in sect in his own house or exaltation the evil is moderated")
sit inside the Bad half, since a mitigation is not a good reading. The Guide's "Worse than by
night?" cells (Mars in the third and sixth) were this strain made visible; they retire. Where a
text has a neutral or mixed reading with no sect distinction (Jupiter in the third, "neither good
nor bad but a balanced moderation"; Saturn in the eleventh, "middling goods ... after his thirtieth
year"), it sits whole in the Good half and the Bad is a dash. Where the two texts differ on the
same sect reading (Saturn in the ninth by night: Rhetorius "recluses, inventors of apothegms,
interpreters of dreams, philosophers", Firmicus "the anger of the gods, the hatred of emperors"),
each sits in the half its own valuation belongs to and the cell says whose reading it is. The
texts' own conditions stay in the cell (with the Sun in the Ascendant; a planet in the tenth; not
under the beams; Jupiter's trine; ruling the Lot of Fortune or the Ascendant; in a woman's chart);
long enumerations (the signs' variations, the lists of trades and of illnesses) are compressed.

The translators' reassignments. Holden's note to p. 65 and Dykes's fn 35 (III.2, 14) say that
Rhetorius's second set of third-house paragraphs (pp. 65-67, Saturn to the Moon by day and night)
is the ninth's, repeated there at pp. 89-91; Holden's notes to pp. 97 and 99 and Dykes's fn 56
(III.2, 54) say that his second set of eleventh-house paragraphs for Saturn, Jupiter, Mars and
Mercury (pp. 97-99) is the fifth's, the Sun's and Venus's being the eleventh's own, and the Moon's
(p. 100) repeating the fifth's -- which Firmicus III.13, 31 says the eleventh does, so it stands for
the Moon. Each such paragraph serves only the house it belongs to; the third's Rhetorius halves rest
on his genuine third-house sentences (pp. 62-64: the Moon ruling there, Saturn and Mercury making
revelations from dreams, Venus bestowing favors from women, Jupiter and Saturn without Mars showing
good fortune) and on Firmicus, and the eleventh's Saturn, Jupiter, Mars and Mercury on Firmicus
alone. Lost paragraphs: Rhetorius's Moon in the twelfth (p. 47, the manuscripts break off after her
first words), the sixth (p. 79) and the eighth (p. 87), and his Sun in the tenth (p. 94); the
first sets supply what they have (the Moon in the twelfth and sixth as the Sun there for the
father, p. 43 and p. 75; the Moon in the eighth by night, p. 84; the Sun and Moon in the Midheaven
without the malefics, p. 92). Firmicus's Moon in the fifth to the eighth is missing (III.13,
19-22; Dykes's fnn 284-285 supply Rhetorius for the fifth and seventh), so the Moon's fifth and
seventh are Rhetorius alone, her eighth has a Good half from Rhetorius's first set and a dash, and
her sixth has a dash for Good and Rhetorius's first-set sentences for Bad. The plan's s.4.5
expectation that III.13 has her in all twelve places was wrong; the dashes the plan expected to
retire in the sixth and eighth retire on one side only.

Where the Guide's Rhetorius half and the texts disagree in substance (the Guide's gist first, then
the text's; the cell follows the text):

1. Saturn in the third, Good and Bad. Guide: "Initiates, religious chiefs" / "Recluses" -- the
   ninth's paragraph (p. 65), which the translators reassign. Rhetorius's third-house sentence
   (p. 63) is revelations from dreams with Mercury; Firmicus III.2, 14-16 is idle and slow,
   seeking nothing from the patrimony, sacrilegious with Mercury and the Moon.
2. Jupiter in the third, Good. Guide: "Balanced moderation" (kept), but the Guide's Bad was blank
   and its source (III.3, 10) has no bad reading; the dash stands and Rhetorius's "good fortune
   with Saturn, without Mars" (p. 64) joins the Good.
3. Mars in the third, Bad. Guide: "Worse than by night?". Neither text has a sect reading for
   Mars in the third; III.4, 15 (envy, a bad conscience about a great crime) is the Bad.
4. Mercury in the third, Good and Bad. Guide: "Divination, astrologers" / "Priests, magicians" --
   the ninth's paragraph (p. 66). Rhetorius's third-house sentences (pp. 62-63) are revelations
   from dreams with Saturn and foretelling the future with the Moon; Firmicus III.7, 12-14 has
   priests, magicians, chief physicians, mathematicians, all as one good reading; no bad reading.
5. The Moon in the third, Good. Guide: "With Saturn: slow, unsuccessful, sacrilegious (Firmicus)"
   -- that is III.13, 13, a bad reading, printed under Good. It is in the Bad now, with Rhetorius's
   haruspex and blasphemer with Saturn (p. 62); the Good is her rulership sentence (p. 62) and
   III.13, 10-12.
6. Mars in the sixth, Bad. Guide: "Worse than by night?". Rhetorius (p. 78): "especially by day";
   Firmicus (III.4, 36-37) makes no sect distinction. The Bad carries "especially by day".
7. The Sun in the sixth, Good. Guide: "With Jupiter and Venus, better than by night". III.5, 43 says
   Jupiter and Venus with him mitigate the evil when nothing is in the Midheaven; there is no
   "by night". The Good is the planet-in-the-tenth reading (p. 78; III.5, 42-43).
8. Venus in the sixth, Bad. Guide: "See above". The Bad is the by-day-and-night reading (p. 78;
   III.6, 29-32); the Good is the planet-in-the-tenth reading only.
9. The Sun in the seventh, Good. Guide: "Administrators". Rhetorius (p. 81): bad luck with marriage
   and children but prosperity and wealth; the administrators are III.5, 47, under the Moon's and
   Jupiter's conditions.
10. The Sun in the eighth, Good and Bad. Guide: "Father's early death, healing" / "See above". The
    father's early death (p. 86; III.5, 67) is a bad reading, and "healing" is III.5, 72-74's
    mitigation of the illnesses; neither text has a good reading, so the Good is a dash.
11. Mars in the ninth, Good. Guide: "Glory, unpunished". Rhetorius (p. 89) and III.4, 67-73 give the
    unpunished, sophists, exorcists, and Firmicus "good for life and glory"; the Guide's Bad was
    blank, but Rhetorius's first set (p. 88: blasphemers without Jupiter and Venus, a wanderer
    afflicted by demons with the Lot of Fortune in the sixth or twelfth) and III.4, 69 fill it.
12. Saturn in the eleventh, Good. Guide: "Middling goods over time" -- that is III.2, 54; the
    Rhetorius column had also carried the fifth's paragraph. Firmicus alone now; Bad a dash.
13. Mars in the eleventh, Good. Guide: "Many goods, dignity" -- III.4, 82 (Rhetorius's paragraph is
    the fifth's). Firmicus alone; Bad a dash.
14. Mercury in the eleventh, Good and Bad. Guide: "Ingenious, accounts" / "Spending, agents". The
    Bad is the fifth's paragraph (p. 99, Holden's fn 3); III.7, 52 has no bad reading. Dash.
15. The Moon in the eleventh. Guide: "Rulers, favored, good from parents" / "Living abroad,
    estrangements, orphanhood" -- kept in substance, now with Firmicus III.13, 31's statement that
    the eleventh repeats the fifth, so the Rhetorius paragraph stands here.
16. Saturn in the twelfth, Good. Guide: blank. Rhetorius (p. 46): "by day, more moderate" is a
    mitigation; the Good stays a dash and the mitigation sits in the Bad.
17. Jupiter in the twelfth, Good. Guide: "Fights against superiors" -- a bad reading (p. 46) printed
    under Good. It is the Bad now; the Good is III.3, 65-66's subtle trade (goldsmiths, gilders,
    mosaic workers) when neither the Sun nor Saturn opposes him.
18. Mercury in the twelfth, Bad. Guide: "Danger from slaves". Rhetorius (p. 47): vespertine, a
    busybody; opposed by Mars, condemned for state secrets, forgeries, mismanagement or slaves;
    III.7, 58-59 the informants, forgers and poisoners, the greatest condemnations by slaves.
19. The Moon in the twelfth, Good. Guide: "Luckiness/authority (with fortunes)". III.13, 32: by
    night with Jupiter and Venus, or one of them, partilely in the Ascendant. The condition is in
    the cell.
20. Mercury in the second. Guide: "Evening star by night: good at business" / "Morning star by
    night: obscure, bad, poor; evening star by day: good at learning, poor" -- kept in substance;
    Rhetorius's oriental reading (p. 57) joins the Good and his under-the-beams reading the Bad.

Smaller compressions (the Guide's "Sailing, poor livelihood" for the Moon in the first, its
"Squanders money" for Mercury in the fifth) are resolved to the texts' words without being counted.

OCR. Four corrections in `mathesis/mathesis_photographed.md` (left uncommitted in the corpus repo for
the coordinator, listed at the end of the sentences file): the last eleven lines of p. 176 (the end
of III.3, 42 and all of 43-44) restored from the photograph; the sentence numbers 69-74 of III.5
(p. 201) and 57-64 of III.6 (p. 212), which the OCR had set as footnote superscripts; fn 281's
Latin. Nothing else in the cited sentences differed from the pages. Rhetorius Ch. 57 (PDF OCR, and
the three photographed pages) read clean.

Page. The help says what the Rhetorius halves are (Ch. 57 by chapter, house and page; Mathesis
III.2-III.7 and III.13 by chapter and sentence where Rhetorius is silent; both cited when both are
used), states the sect rule in one sentence, names the translators' reassignments and the lost
paragraphs, counts the seventeen dashes, keeps the PN IV paragraph and the Guide's one citation as
the arrangement's origin, and drops the "still prints the Guide's summary" clause; the caption
under the subheader and the export citation line say the same in a line. Spellings on the page:
"Firmicus", "Mathesis", "Rhetorius"; no date, file or process.

Tests. `tests/test_prose_tables.py`: `RHETORIUS_HALVES` (the literal transcription) and
`RHETORIUS_DASHES` retired for `RHETORIUS_HALVES_SENTENCES`, 168 rows of (house, planet, half, cite,
anchors) -- the locator and three words the half's text shares with the cited passage, at least one
from each source where two are cited, or ('', []) for a dash -- and tests that the fixture covers
every half once in grid order; every Rhetorius half has text; a cite matches
`^Ch\. 57, the [a-z]+, p\. \d+(; III\.\d+, \d+(-\d+)?)?$` or `^III\.\d+, \d+(-\d+)?$` or is ''
with the text a dash, and a Rhetorius cite names the cell's own house; anchors in the text; the
dash count what the help states (17) and the eight no-good-reading planets dashed on the Good side
only; the sect prefixes; no Guide compression or "(Firmicus)" tag surviving; no [UNCERTAIN]; the
reader's cell format with both locators. `GUIDE_PAGE` and every Guide-page reference are gone from
the file and its docstring is rewritten. `tests/test_base_tables.py`'s shape guard is unchanged (the
shape did not change; its comment follows). The F15 heading test's pin on the old help sentence is
re-pinned on the new one. The anchors were checked by script against the corpus (168 rows) before
the push; the checker's sentence table (house, planet, half, locators, corpus lines, first six words,
anchors) and the OCR corrections are in the corpus repo's process directory,
`BUILD_DELIN_C_SENTENCES_2026-09-16.md`. `tables.json` regenerated once: unchanged, since it
inventories headings and column names. Whole suite 3136 passed, 1 skipped, 6 xfailed (build B: 2977 / 1 / 6).

After the check (`BUILD_DELIN_C_CHECK_REPORT_2026-09-16.md`: 165 halves verified, three defective,
one docstring, one log count; the owner's rulings in `DELIN-TABLES_C_ruling_2026-09-16.md`), on the
same branch:

- F2, the Moon in the fourth, Good: Rhetorius p. 71's Sun-in-the-Ascendant clause is his out-of-sect
  branch (a day chart); it now reads "by day, with the Sun in the Ascendant, thought worthy of
  praise ..." inside the Good half, whose "In sect (by night)" prefix covers only the mother's
  sentence.
- F3, Venus in the ninth, Bad: the Saturn-and-Mars clause is Rhetorius's in-sect sentence and
  Firmicus III.6, 45 (by night); it is split off as "in sect (by night), with Saturn and Mars ..."
  and the locator is `Ch. 57, the ninth, pp. 65-66, 90; III.6, 42-43, 45`.
- F4, Saturn in the first, Bad: III.2, 5's second condition restored -- "with no benefic in a good
  place joined to them by a strong ray, if Mars takes up the waxing Moon's rays, a violent death".
- F7 (ruled): the reassigned paragraphs are the ninth's and the fifth's text. Rhetorius pp. 65-67 are
  folded into the ninth's Saturn, Jupiter, Mars, Venus, Mercury and Moon halves, Rhetorius first,
  and pp. 97-99's Saturn, Jupiter, Mars and Mercury into the fifth's, each cited under the house it
  belongs to beside the house's own pages (`pp. 65, 88-89`; `pp. 72-74, 98`). What the reassigned
  copies add: Saturn's "surrounds some of them with hindrances" (p. 65), Jupiter's "consecrated" and
  "fond of gold (or of oracles)" (p. 65), Mercury's "in opposition to Mars, sacrilegious persons and
  temple-robbers" (p. 66, now the ninth's Bad beside III.7, 40-43, no longer Firmicus alone), the
  Moon's "in honor", "acquisitive", "in dishonor", "seek sanctuary" (p. 67); Jupiter's "victors in
  contests, divine doctrines" (p. 98), Mars's "friends among the powerful", "the power of the
  sword", "changes of place and living abroad on account of strange events", "restored to their own
  country" (pp. 98-99), Mercury's "the bearing of a demigod", "agents, accounting offices,
  astronomers" (p. 99), Saturn's "losing what they had acquired" (p. 98).
- F6 (ruled): Holden's fn 4 to p. 65 keeps the Sun paragraph there in the third (its "ignoble or
  servile duties in temples" is III.5, 31's clause), and the Venus paragraph there names "the God or
  the Goddess". The Sun in the third's Good gains "God-fearing, inspired by the gods" and its Bad
  "ignoble or servile duties in temples", both citing p. 65 beside Firmicus; Venus in the third's
  Good gains the paragraph's by-night reading (good prophets, explainers of prodigies, divines; with
  Jupiter, managers of women advancing through them), and its Bad, a dash before, fills from the
  paragraph's in-sect sentence, which is a bad reading -- "involved with demons or wearing rags in
  temples ... with Saturn or Mars in conjunction, square or opposition, disputes on account of women,
  quarrels, misfortunes and ingratitudes" (`Ch. 57, the third, pp. 65-66`) -- with the cell noting
  that this page's sect label ("in sect") is the reverse of the ninth's copy (p. 90, "out of sect")
  and of Firmicus (III.6, 42, by day).
- F10 (ruled): Venus in the twelfth's Good, a dash before, fills from III.6, 70-71 (Dykes's fn 176
  places the run in the twelfth): "joined by a ray with Jupiter, freed from the attack of the
  preceding malice ... increases to the patrimony through their own actions, and excluded from every
  disgrace of vice, if the Moon does not regard her, so placed with Jupiter, from the opposition";
  69, the Saturn clause of the same run, joins the Bad (`III.6, 63-65, 69`).
- F5 (ruled): a half whose sentences run over a page break or fold in the house's earlier general
  sentences cites the page range (`Ch. 57, the second, pp. 57-61`), and the ninth's and fifth's
  halves that rest on a reassigned paragraph cite its page in a list beside their own
  (`pp. 65, 88-89`); `RHETORIUS_CITE` admits `p. N`, `pp. N-M`, `pp. N, M-K` and a Firmicus list
  (`III.6, 42-43, 45`), and the test checks the pages and sentences ascend and that `p.` names one
  page. Sixty-five halves changed locator on this account alone (every one the checker listed and
  the page-break cases besides: Saturn, Sun, Venus and the Moon in the first's Good, Jupiter in the
  second's Good, the Sun in the fourth's Bad, Mercury in the fifth's Bad, Venus in the sixth's and
  the tenth's Bad, Venus in the eighth's Good, the Moon in the ninth's Good and the tenth's Bad).
- F12: `evaluate_planets_in_houses`'s docstring says each half prints with its own locator.
- F16: the Rhetorius-alone membership above corrected (Jupiter in the third's Good cites both; the
  seventh was the Moon in the sixth's Bad).
- F18: Jupiter in the fourth's Good says "forbidden activities" as Holden has it; the two lacuna
  asides ("the sentence is broken / damaged") leave the rendered cells of Saturn in the eighth's Bad
  and the Sun in the fourth's Bad (the sentences file keeps the note); the Sun in the sixth's Good
  keeps only III.5, 42's reading and its Bad takes III.5, 43's mitigation (`III.5, 40-43`).
- The three balance placements (Mars in the fourth's Good, Mars in the eighth's Good, Venus in the
  fifth's Bad) stand as built; Saturn in the ninth by night stands.

Counts after: 123 halves on both texts, 8 on Rhetorius alone (the Moon in the fifth, the sixth's
Bad, the seventh, and the eighth's Good; Saturn in the third's Good; Venus in the third's Bad), 22
on Firmicus alone, 15 dashes (Jupiter and Mercury in the third's Bad; Saturn, Jupiter, Mars and the
Moon in the sixth's Good; Mars in the seventh's Good; the Sun in the eighth's Good and the Moon in
the eighth's Bad; Saturn, Mars and Mercury in the eleventh's Bad; Saturn, Mars and the Sun in the
twelfth's Good). Ninety-three halves changed in all (text, locator or both). The help and caption
say fifteen dashes and describe the page-range locators; `tables.json` regenerated once, unchanged.
Whole suite 3136 passed, 1 skipped, 6 xfailed.

Delta pass (the checker on 0b3a5b1): 93 changed halves verified, none defective, ready to merge. One note acted on: Jupiter 9th Bad had gained an attributed editorial aside on Holden's "fond of gold" (his conjecture of oracles); it leaves the rendered cell as the two lacuna asides did.

## 2026-09-17: JN Ch. 4 rows amended after Astra's reading

The owner's JN-CH4 ruling of 2026-09-16 adopted Astra's reading whole (`process/astra_2026-09-11/JN-CH4_ruling_2026-09-16.md`,
`JN-CH4_astra_ruling.md`, the packet `JN-CH4_packet.md`, in the corpus repo). Labels, witness cells, two luminary rows
and the note; no row's arithmetic changed; the finding's title unchanged; Sahl 1.20's grant, the "1.21 additions not
applied" declaration and the display-only standing untouched. Branch `jnch4-amendments-2026-09-17` off 579316f.

Row by row (`evaluate_jn_years_additions`, `jn_years_additions_rows`; a new column 'Witnesses', prose-wide):
- (a) The zero rows -- a fortune's square or opposition, a bad one's sextile or trine -- keep 'Ch. 4' "adds or subtracts
  nothing" and now print in 'Reading' "0 -- explicitly neither adds nor subtracts (Abu 'Ali, Ch. 4)" (`JN_CH4_ZERO`);
  'Witnesses' for the fortune: "'Umar I.4.4: adds its lesser years if not retrograde, burned up or impeded"; for the
  bad one: "Abu Bakr I.15: adds its lesser years from a good place (to the significator of life, his term) · 'Umar
  I.4.4: subtracts if it seizes the house-master without a fortune's aspect (fn 87 reads 'seized' as besieged)"
  (`JN_CH4_WITNESSES`). 'Umar's seized sentence and fn 87 added to `TBN_I44_ADDITIONS` ('seized', 'fn87'), verbatim.
- (b) A fortune's addition keeps the three grade columns; 'Reading' now "k years; if middling, k months; if more
  unsound, k days or k hours -- strength grade not determined here"; 'Grade' reads "not determined: no text defines
  ..." where it read "not decided" (never "years"); 'Witnesses' "'Umar I.4.4: months if retrograde or burned up".
- (c) Mercury: 'Ch. 4' carries "Dykes fn 28: conjectural interpretation" (`JN_CH4_FN28_LABEL`) in every case; the
  paired cases read "Dykes fn 28 (conjectural interpretation): with or aspecting Venus, himself sextile to the
  house-master -- adds 20 years" (effect 'adds' / 'subtracts', 'literal' the same); the unpaired cases -- with a
  fortune but square, opposite or joined to the house-master; with a bad one but trine, sextile or joined -- "not
  decided under fn 28: this pairing is unstated · Abu 'Ali's sentence read literally: adds 20 years" / "subtracts 20
  years" (effect 'not decided', 'literal' 'adds' / 'subtracts'); with neither "not specified; not an explicit zero"
  (effect 'not specified'); with both "mixed associations: authorial result unresolved" (effect 'unresolved').
  'Witnesses' quotes Abu Bakr's Mercury sentence. "With" is declared this app's convention (whole sign, the
  house-master not counted as company) in the note.
- (d) Two luminary rows after the loop over the five, always present when there is a house-master (a luminary that is
  itself the house-master has none): 'Ch. 4' "no explicit luminary modifier specified here" (`JN_CH4_NO_LUMINARY`,
  also the row's 'sentence'), the grade cells dashes. The Sun: 'Looks at the house-master' computed by whole sign as
  for the others ("in aversion (whole sign)" when averse), 'Reading' "'Umar: subtracts 19 years (square)" for joined,
  square or opposition with "; with reception, months or days (no unit chosen) -- reception not tested here" (this app
  does not test 'Umar's "reception in the same place"; the clause is shown, not computed), "'Umar: adds 19 years
  (trine)" for trine or sextile, "'Umar: none of his cases applies (in aversion)" otherwise; 'umar' in the dict
  'subtracts' / 'adds' / None; 'Witnesses' "'Umar I.4.4: subtracts his lesser years by conjunction, square or
  opposition; adds them by trine or sextile; with reception in those three, months or days (no unit chosen) -- the 19
  is Ch. 4's table reused" ('sun_reception' added to `TBN_I44_ADDITIONS`, verbatim). The Moon: 'Reading' "not
  specified"; 'Witnesses' Abu Bakr's luminaries sentence paraphrased with the unclear antecedent flagged ('luminaries'
  added to `ABU_BAKR_I15_ADDITIONS`, verbatim); his "Lord of the kadukhudhāh joined to the Sun" sentence not used
  (fn 618). The 19 is read from `JN_YEARS_TABLE['Sun'][2]` inside the same function; no new reader of the table.
- (e) Verified: no row stating Abu 'Ali is gated by a witness's condition -- the evaluator's five-planet loop decides
  by the whole-sign look alone, the witnesses' conditions live in `JN_CH4_WITNESSES` only (a test reads the source
  for the words). The brief's "`umar` list" is `evaluate_jn_years`'s (the ladder), not this evaluator's, which never
  had one. The subtracting bad one's row is unchanged ('Reading' "the chapter's sentence", 'Witnesses' a dash).
- Note: `JN_CH4_ADDITIONS_NOTE` replaced with Astra's suggested note in this app's forms ("this app", "Abu 'Ali",
  "Abu Bakr", "'Umar", straight quotes, " -- "), plus the sentences the old note carried that the ruling keeps (the
  fortunes and bad ones named, the lesser years Ch. 4's column, "joined" by whole sign, Mercury's "with" as this
  app's convention, 'Umar's "or were with it in one sign" as the one clause that specifies a sign). The `_finding`
  glance names the explicit zero, "Mercury by Dykes's fn 28, a conjecture", the Sun and Moon with their witnesses,
  and the Witnesses column; its Sources expander quotes the four added sentences (Abu Bakr on the luminaries; 'Umar's
  seized sentence with fn 87, and the Sun's reception sentence) and says Abu Bakr's grading is "a different grading,
  not a definition of Abu 'Ali's". 'Witnesses' added to `_WIDE_TEXT_COLUMNS` (one line; the column is prose).
- Comment only: the block header now says Ch. 4 is p. 235 (photographed 2026-09-15, read against the page
  2026-09-16), the old "pp. 235-236" being wrong -- p. 236 is Ch. 5.

The corpus OCR item (PN I p. 235's middle-years cells "43 $1\frac{1}{2}$"): already repaired by the witness pass
(corpus `process/proofing_2026-09-16/WITNESS_PASSAGES_READ_REPORT_2026-09-16.md` §3 row 5); confirmed
`pn1/pn1_photographed.md` line 861 reads "43 ½" and the other middle-years cells (45 ½, 40 ½, 69 ½, 66 ½) likewise,
matching `JN_YEARS_TABLE`. No photograph read, no corpus file edited.

Tests (`tests/test_jn_years_additions_2026_09_15.py`, 14): the Ch. 4 span re-pinned to end at the p. 236 marker
(the file now carries Masha'allah III.1.8 before Abu 'Ali, so the old end heading preceded the start and the span
came out empty on main); the 'Umar span now includes its footnotes (fn 87); the existing sentence-to-page pins kept
and the six new sentences held to the page; the zero rows' text and witnesses; a fortune row's reading string and no
'Grade' reading "years"; Mercury's four cases (and joined) by constructed charts; the Sun row in each of 'Umar's
cases (square, opposition, joined, trine, sextile, aversion) and the Moon row; the luminaries present with no other
planet looking, absent when the house-master; the note's "conjectural" and "implementation conventions" and no smart
quotes; no witness condition in the five-planet loop's source; the Releaser tab at both depths with the new note's
phrases. `tables.json` regenerated once without -n: unchanged (the finding renders at the supplement depth only).
Pre-existing on main 579316f against the current corpus and left for the mechanic: `test_years_ladder_2026_09_15.py`
(pins the pre-repair "43 $1\frac{1}{2}$") and `test_andarzaghar_triplicity_lords_2026_09_15.py` (a split ITA marker).

After the blind check (corpus `process/astra_2026-09-11/BUILD_JNCH4_AMEND_CHECK_REPORT_2026-09-17.md`: 0 defects,
5 notes), three notes applied: (6) Mercury's literal-reading cell qualifies the +20 as Astra's case mapping asks --
"read literally: adds 20 years (if the fortune is one 'which add[s]')"; the -20 cell is unqualified, the sentence
having no condition for the bad ones; (7) the note's "with" convention now reads "whole sign -- in one sign or in any
whole-sign aspect, as fn 28 has "with or in aspect to" -- the house-master itself not counted as his company", which
is what `_prosperity_looks` does; (19) the unreachable "none of Saturn, Jupiter, Mars, Venus or Mercury ... looks at
it" fallback row dropped from app.py (a luminary row is always present under a house-master). Tests pin the two
strings. Rebased onto main after #67 and #68; `tables.json` regenerated once without -n.
## 2026-09-17: DELIN-TABLES C and B amended after Astra's readings

Build C (#64, with the after-check rulings of `DELIN-TABLES_C_ruling_2026-09-16.md`) had sorted the
Rhetorius/Firmicus readings into the Well/Badly Placed halves by valuation, with "By day" / "By night"
/ "In sect" / "Out of sect" prefixes. Astra's reading of the same evening (`DELIN-C_astra_ruling.md`,
adopted whole in `DELIN-C_ruling_2026-09-16.md`) rules that shape misstates the texts, which divide by
sect and by conditions and not by good and bad; Astra's reading of build B (`DELIN-B_astra_ruling.md`,
adopted in `DELIN-B_ruling_2026-09-16.md`) rules the PN IV halves' headings and the Moon's placement
misstate Book II and VII.8. This build converts the merged table to both rulings, per
`BUILD_DELIN_CB_AMEND_BUILDER_BRIEF_2026-09-16.md` and its addenda of 2026-09-17. Nothing was re-derived:
every cite build C had stands, and each merged half was RE-SHAPED into entries, going back to the cited
passage only where re-shaping needed the author's own axis label or a condition the merged half had
compressed away.

Shape. `PLANETS_IN_HOUSES[house][planet]['Rhetorius']` is a LIST of testimony entries `{'author',
'cite', 'axis', 'text', 'portional', 'conditional'}` -- the author one of Rhetorius, Firmicus,
"Rhetorius, as summarized by Dykes"; the cite Rhetorius's by chapter, house and page(s) or Firmicus's
by chapter and one sentence or one run, or `III.13 fn 284` / `fn 285`; the axis the author's OWN
division (`by day`, `by night`, `in sect`, `out of sect`, `unsplit`, `general malefic`, `general
benefic`), never converted -- Saturn "by day" is not "in sect", and a half prefixed "In sect (by night)"
by build C is now an `in sect` entry with the prefix gone; `portional` where Firmicus states the
placement so, printed "(portionally)"; `conditional` where the entry's whole reading rests on a
stated configuration beyond the placement and the axis (the sixth key is this build's, not in the
brief's five: item 7's rule -- a cell over ~60 words prints its unconditional entries and sends the
rest to the row's detail -- needs the classification to be explicit and testable, and a heuristic
on the text would not be). The PN IV halves keep their `{'Good', 'Bad'}` keys and are headed "If in a
suitable condition" / "If in a bad condition" on the page. The Moon's PN IV halves are the pointer
"see the Moon's table below (VII.8, by her transit)" with cite '', and her twelve readings are
`MOON_IN_HOUSES_VII8`, one unsplit reading per house.

Counts. 352 entries: 196 by Rhetorius, 152 by Firmicus, 4 by Rhetorius, as summarized by Dykes (the
Moon's fifth and seventh, by night and by day each, fnn 284-285); no cell without an entry (build C
had left 15 halves dashed, but every one of those cells has testimony under the author's own axis --
Saturn, Jupiter and Mars in the sixth, Mars in the seventh and Saturn, Mars and the Sun in the
twelfth had only adverse readings, and adverse testimony is testimony). Axes: 139 unsplit, 78 by day,
78 by night, 10 in sect, 9 out of sect, 20 general malefic, 18 general benefic; 36 portional, 60
conditional. Of build C's 153 halves with text, the 123 that cited both authors became two entries,
one per author, and the 30 that cited one became one; 34 further entries come from splitting one
author's clauses by his own division or into their own configuration records (Firmicus's III.2, 1-3
and 4-5 for Saturn in the first; his Mars in the seventh into five, III.4, 38-41, 42-43, 44-45,
46-49, 50-51; his Moon in the third and twelfth; Rhetorius's Mercury in the second by night, by day
and the first set); the 38 general class entries and the 4 summaries are new. General class
testimony (Ch. 57's "the malefics there ..." / "the benefics ...") is entered for both members of the
class in the houses whose sections carry such a sentence -- the malefics' in the first, second,
third, fourth, sixth, eighth, ninth, tenth, eleventh and twelfth (the eleventh's is a good reading:
as rulers of lots, houses or triplicities without evil positions they render the nativity good),
the benefics' in the first, second, third, fourth, fifth, eighth, ninth, eleventh and twelfth -- with
their conditions (the first's needs the malefic aspecting the Sun and the Moon; the eighth's "Jupiter
and Venus alone" and "Saturn and Mars without Jupiter and Venus" need both members). A sect word
the translator supplies in brackets (Holden's "[by night]" for Saturn in the second and "[there by
day]" for Saturn in the fifth, whose copy printed under the eleventh says it; Dykes's "<by night>"
for III.2, 8, "<by day>" for III.2, 36, III.4, 38, III.7, 26 and 39, "[by day]" for III.13, 9) is kept
as the axis with the supplement named in the text.

Conditions restored from the passages, where the merged half had compressed them away: Jupiter in
the first, III.3, 2 (a malefic resisting by a contrary ray diminishes most of it); the Sun in the
first, III.5, 2 (the malefics near his rays weaken the eyesight); Venus in the first, III.6, 10 (the
lacuna and "a wife at an early age"); Saturn in the second, III.2, 11 ("exposing their bodies to
danger in daily works"); Mars in the second, III.4, 13 (the dangers stay even with Jupiter and Venus
joined); Saturn in the fourth, Rhetorius p. 68 (in sect in Jupiter's domicile or exaltation:
stationary, loss of the inheritance; hidden things; the children destroyed); Mars in the fourth,
III.4, 25 (Firmicus's own three conditions for lunatics, beside Rhetorius's); Venus in the fourth,
III.6, 20 (Mercury joined portionally by a ray); Venus in the sixth, III.6, 32 (Firmicus's own
"estranged from the pivots" record, beside Rhetorius's); Mars in the sixth, III.4, 37 (the portional
qualification, and the flag); Mars in the seventh, III.4, 40-41 (his own house from the diameter, the
Hour-marker not in his house) and 42-43 (alien signs); Mars in the eighth, III.4, 55 and 57 (the
Moon in the second with Jupiter averse; gladiators without Venus or Jupiter); Saturn in the eighth,
III.2, 34 (Mars not regarding); Mars in the ninth, III.4, 71 (Jupiter not in the Hour-marker for the
exorcists); Saturn in the tenth, III.2, 46 (by night in all the pivots, orphanhood); the Moon in the
tenth, III.13, 27 fn 286 (the manuscripts' "borne towards Saturn"); the Moon in the fourth, III.13,
16 (Saturn in another pivot and Venus in the Setting, Firmicus's own, no longer blended with
Rhetorius's cadent ruler). "Especially if matutine" and "more so by day" stay inside Mars in the
sixth's Rhetorius entry as the strengthener and gradation they are; "if under the beams" stays as
its branch. "The full Moon moving toward Mars" (p. 77) is no entry. The Moon in the sixth has
Rhetorius's two entries: the transfer of the Sun's sentence to the mother with its qualification
(p. 75), and the spleen sentence with the Sun-conjunction clause and its scope noted (pp. 76-77).

Saturn in the first, as printed in the third column:

> Rhetorius (by day): A loud outcry at the birth and what is done for the native through sound (the translator does not know what this means); first born or first reared, or a lack of brothers before him -- as always when he is angular, where he makes the first born or first reared or destroys the brothers before him [Ch. 57, the first, pp. 51-52] · Rhetorius (by night): Damages, opposition and hardships, and actions in wet places [Ch. 57, the first, p. 52] · Rhetorius (unsplit): First-born or first-raised [Ch. 57, the first, p. 48] · Firmicus (by day): The birth announced by a great cry; the eldest of all the brothers, or, if one was born before him, that older one separated from the parents (by day in all four pivots he always makes the first-born or the first nourished, or the brothers born before destroyed -- the destruction is the translator's filling of a lacuna from Rhetorius -- haughty and encouraged by a spirit of pride) (portionally) [III.2, 1-3] · Firmicus (by night): Hindered by the greatest sluggishness and always pressed down by great labor; for some, actions around water, always worn out by laborious dealings (portionally) [III.2, 6-7] · 2 conditional entries in the row's detail

Mars in the sixth, as printed:

> Rhetorius (unsplit): Injury to the feet, harm in matters concerning slaves, uprisings of enemies and dangers abroad, and injury in the part of the body ruled by the sign he is in; cuts, burns, the bites of wild animals, attacks, wounds and attacks by robbers, especially matutine, and under the Sun's beams hidden sicknesses of the internal organs or hemorrhage by the sign, more so by day; sicknesses, injuries, dangers and plots on account of slaves or of persons convicted or arrested, especially by day; angular by day, in general the danger of sudden death [Ch. 57, the sixth, pp. 76-78] · Rhetorius (general malefic): The malefics here make sicknesses or injuries involving the feet, and the loss of money [Ch. 57, the sixth, p. 75] · Firmicus (unsplit): Many evils: he harms the children and makes an unevenness of life, and decrees illnesses according to the nature of the signs -- in the crooked signs premature death, sometimes the lame and hunchbacks; here the vices of all illnesses are determined, if the place is discovered portionally and Mars is in that sign portionally (portionally) [III.4, 36-37]

The row's detail (select the planet's row in the structural table) prints every entry of the list
in full, the two conditional Firmicus records of Saturn in the first included.

B amendments (items 9-13). The two condition columns are headed "If in a suitable condition" and
"If in a bad condition"; the help says the qualifications in each entry control and that a suitable
reading's condition can be inferred. Mercury in the ninth and third, II.21, 8, ends "(condition not
explicitly stated in II.21, 8)". Every grouped locator names its sharing -- the four stakes ("II.6, 1-2
(shared with the 4th, 7th and 10th)"), the eleventh-or-fifth, the ninth-or-third, the second-or-eighth
(Jupiter, the Sun, Mercury, and Venus's suitable half), the sixth-or-twelfth (Jupiter, Mercury, and
Venus's suitable half): 116 halves. Saturn's four falling places, II.6, 22-24, are carried whole in
his second, sixth, eighth and twelfth bad halves beside each house's own sentence -- 22's "in the
revolution", 23's intensifications (not received: harsher, dispossessed, hardship, evil said of him,
illness from cold and moisture or cold and dryness; retrograde: harsher again), 24's residual
leisure -- where build B had compressed 23 to "harsher if not received"; Jupiter's II.9, 15-16 and
Venus's II.18, 18 likewise gain their premise "in the revolution". The visible caption under the
subheader is Astra's adaptation paragraph verbatim, followed by the sources line; the subheader text
is unchanged. The Moon leaves the two condition columns: her halves point to "The Moon in the houses
-- PN IV VII.8, by her transit", a table under the main one (House, Reading, Locator, Natal Moon
here), whose help says it is a natal analogy from a transit chapter that supplies no condition split;
one unsplit row per house, mixed readings intact, "(from this indication)" restored where the
sentence has it (2, 3, 5, 9, 11, 12), fn 99/101/110's "different" beside "conflicting" (5, 6, 11),
fn 106's guess marked as the translator's (10), VII.8, 3's "some of him and his parents" as printed;
VII.8 was not re-read (read against the photographs on 2026-09-16 by another pass). The export
carries the Moon's table under the Dignities page beside the planets table, whose rows now carry
the three text columns and an `Entries` list.

Page. The help for Topical Planets in Houses is rewritten whole for the three-column table: what the
third column is (both texts, each entry under its author with the author's own division and its
conditions, because the texts do not divide by well and badly placed), general testimony labelled,
"portionally" printed, a dash defined as absence of testimony, the translators' reassignments and
the lost paragraphs, the counts (352; 196, 152, 4; no cell without one), the ~60-word rule and the
row's detail, the condition columns and their inferred-condition note, the shared locators and the
falling-places layer, every PN IV half with text, the Moon's pointer, and the Guide cited once, in
its existing form, as the arrangement's origin. The Timing page caption (VI.3 beside the natal
table "whose PN IV halves paraphrase Book II's sentences as natal readings") is left alone, as the
addenda say. No date, file or process on the page.

Tests. `tests/test_prose_tables.py`: `RHETORIUS_HALVES_SENTENCES` retired for `RHETORIUS_ENTRIES`,
352 rows of (house, planet, author, axis, cite, anchors) in list order -- the anchors carried over
from build C's rows where they still fit the entry's text and passage, picked afresh otherwise, all
352 checked by script against the corpus (for a Rhetorius cite the text of the cited pages, for a
Firmicus cite the cited sentences, for a summary the footnote); `PN4_HALVES_SENTENCES` with the
shared annotations and the Moon's twelve rows as the pointer with cite ''; `MOON_VII8_SENTENCES`, the
Moon's twelve (house, cite, anchors), checked likewise. The nine tests the list shape retired are
each replaced by a successor that keeps what its predecessor guarded: the shape (the list, the six
keys, the three authors, the seven axes); the PN IV pin; the shared locators naming each other back;
the Moon's halves the pointer; the VII.8 pin and the text's reservations; no PN IV dash (the count
the help states, none); Mercury 9th and 3rd as II.21, 8 and 9 with the annotation; the falling-places
layer whole; every entry pinned to its passage (author allowed, axis allowed, cite matching the
three patterns, the house in a Ch. 57 locator the cell's house, pages and sentences ascending and a
Firmicus run contiguous, no build-C sect prefix, no [UNCERTAIN], portional only for Firmicus); no
empty cell and the author counts the help states; general testimony for both class members in the
pinned houses and for no other planet; the axes the authors' own (Saturn 1st, Jupiter 1st, Mars 1st,
Jupiter 2nd, the Moon 6th, Venus 9th's two copies, the four summaries); the conditions constitutive
(III.2, 4-5 whole and flagged; III.4, 36-37 portional; no full-Moon configuration; 60 conditional,
36 portional); no Guide wording; the readers' formats (the PN IV half, the pointer, the entry, the
cell under and over the word budget, the rows' keys, the Moon table's rows and the natal mark); the
help's counts and phrases, the caption, the headings and the Moon table on the rendered page; and
a seeded row selection printing every entry of the list. `tests/test_base_tables.py`'s shape guard
follows the list shape and the Moon table; `test_fragments_2026_09_15.py` admits the fifth fragment
(the planets block with its row detail, the tick grids' pattern). `tables.json` regenerated once,
without -n: one new table on the Dignities page. Whole suite 3325 passed, 1 skipped, 6 xfailed, with
3 failures and 1 error that are main's, not this branch's -- `test_jn_years_additions_2026_09_15.py`,
`test_years_ladder_2026_09_15.py` and `test_andarzaghar_triplicity_lords_2026_09_15.py` read JN
Ch. 3-4 and the Andarzaghar table from the corpus, whose text moved under them on 2026-09-17 (they
fail identically on a clean checkout of 579316f and skip where the corpus is absent).

Judgment calls, for the check (each with the passage): (1) Venus in the third and ninth, Rhetorius
pp. 65-66 and 90 -- the two copies of one paragraph reverse the sect labels (p. 65: in sect,
demons; p. 66: by night out of sect, good prophets; p. 90: out of sect, demons; in sect, good
prophets): each house's entries take its own page's labels and say what the other copy has. (2)
Saturn in the fifth, Rhetorius pp. 73 and 97 -- the fifth's own paragraph has "[there by day]"
supplied by the translator, the copy printed under the eleventh says "by day": the entry is `by
day` citing both and says which copy says it. (3) The Sun in the first, Rhetorius pp. 52-53 --
the kings sentence is not marked by sect and "[with Saturn]" is Cumont's from Firmicus: an `unsplit`
entry with the supplement named; the Saturn-or-Mars destroyer clause follows "But by night" and
Firmicus III.5, 22 has it by night, so it sits in the by-night entry. (4) The Moon in the fourth,
Rhetorius p. 71 -- the Sun-in-the-Ascendant clause stays in the out-of-sect entry (the check's F2
ruling) with Holden's "muddled" note kept. (5) Mars in the twelfth and Venus in the twelfth,
Rhetorius p. 44 -- "Mars and Venus found in this house make wife-slayers" is joint occupancy of the
place, kept as a condition inside each planet's entry (unlike the full Moon moving toward Mars, a
configuration of bodies not both in the place). (6) The Moon in the sixth, Rhetorius pp. 76-77 --
"The Sun and the Moon in conjunction there make madmen" is joint occupancy too and goes inside the
spleen entry, so that the brief's two entries stand. (7) The general benefic sentence of the third
(p. 63) is an intensifier of the ruler's judgment ("especially if a benefic chances to be in this
house"): entered with the ruler's condition, flagged conditional. (8) Rhetorius's first-set
sentences on p. 48 for Saturn ("first-born or first-raised") and Mercury ("intelligent, prudent,
ingenious") are entered as `unsplit` -- build C had folded p. 48 into the other planets' halves but
not Saturn's; the Firmicus configuration records build C never cited (III.3, 7; III.7, 10-11; III.4,
65-66; III.6, 47-49; III.2, 49-53) stay out, re-shaping not re-deriving. (9) Firmicus's III.6, 17-18
(Venus in the third: "good, if Jupiter regards her") and III.3, 58 (Jupiter in the eleventh: the
fasces "if the Sun and Venus join him") are the author's primary statement for the placement, so
they are not flagged conditional though their content is conditioned; the flag marks entries whose
whole reading is a configuration record (III.2, 4-5; III.3, 9; III.6, 69; 70-71 and the like).
