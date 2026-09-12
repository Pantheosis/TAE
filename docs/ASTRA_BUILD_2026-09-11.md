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
