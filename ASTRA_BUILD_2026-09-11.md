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

## 7. Report
