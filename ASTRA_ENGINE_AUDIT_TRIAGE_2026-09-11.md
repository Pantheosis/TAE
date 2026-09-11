# Triage of Astra's adversarial engine audit (2026-09-11)

Source: `~/Desktop/astrology_engine_adversarial_audit_for_claude.md` (audited app.py 13,460
lines, sha d925498b...). Its reproduction harness was extracted verbatim and run against
engine main **96fd547** in a detached worktree with the root venv: **all 23 expectations
still fail, all 4 controls pass** -- nothing in the audit has been addressed. Nothing was
changed here; this file is the triage, untracked.

## Classes

**A. Genuine defects, confirmed in the code, no decision record contradicts them (build):**

| ID | P | One line | Code check |
|---|---|---|---|
| F01 | P1 | Julian dates validated/shifted with proleptic-Gregorian `datetime` | `parse_iso_date`, `pn4_datetime_from_jd`, sidebar offset arithmetic |
| F02 | P1 | fardār and distribution clocks fed `pn4_completed_years` (II.3, 1's count, correct for the profection) so fractional periods freeze until the civil birthday | `pn4_timing_bundle` passes `age` to `pn4_fardar_at_age` / `pn4_distribution_at_age` |
| F03 | P1 | the "current" solar return can be in the future (target before this year's return) | `pn4_solar_revolution_jd(..., age)` seeded from civil age, no bracketing |
| F04 | P2 | hayz "above the earth" is `(lon - asc) % 360 > 180`, while `_sin_altitude` exists and is used for the syzygy | `evaluate_accidental_dignities` line ~1426 |
| F05 | P2 | Escape reported although the original body contact happens first | `evaluate_escape` never compares the two contact times |
| F06 | P2 | ingress bisected to 0.02 d, then used as a hard cutoff against a contact bisected far finer | `_bisect_crossing` / `_perfection_day` |
| F07 | P2 | endpoint-only sign comparison misses a retrograde in-and-out of a sign within one step | `_simulate_forward_uncached` |
| F08 | P2 | Sahl 3, 97 "separating from a planet receiving it": the code tests whether the SEPARATING planet rules the OTHER's degree -- reversed | line ~6166: `planet in (other_rulers['domicile'], other_rulers['exaltation'])` |
| F09 | P2 | `_is_connected_abu_mashar` keeps a pair connected up to 1' past exact; its own comment quotes VII.5, 34 "BY 1' OR LESS ... HAS ALREADY SEPARATED" | the `> 1/60` test inverts the sentence it cites |
| F12 | P3 | `offset // each` floating boundary: a subperiod's returned `sub_to` fed back gives the same expired subperiod | `pn4_fardar_at_age` |
| F13 | P3 | `get_degree_string(30 + 1/60)` -> 00', `int()` truncation of a float just under 1 | `get_degree_string` |

**B. Endpoint-only or reporting (build, small):**

| ID | Note |
|---|---|
| F10 | eastern thresholds use `<=`; VII.2, 11-14 says the phase is left WHEN the degrees are COMPLETED, so exactly 6°/10°/15°/18° east is already out. Measure-zero in real charts; western side stays inclusive (VII.2, 31-34). Do not swap every `<=`. |
| F11 | "Active point" prints the segment's start degree, not the degree reached at the target (I.6, 6 with fn 34). Rename or compute. |
| F14 | three stale provenance comments: `_twelfth_part_sign` / `pn4_twelfth_part` say the construction is "supplied from convention" (Gr. Intr. V.18, 1-3 states it -- already work order PN4R-4n-2); `test_base_tables.py` calls the faces "no table in corpus" (Gr. Intr. V.15, Fig. 54 has it); `WELLED_DEGREES` comment says "all 62 cells" and there are 64 (Fig. 62 has 64; PN IV Fig. 98 has 62). Numbers all verified correct by the audit. |

**C. Source-policy items -- already decided or now decided; no build from the audit:**

| ID | Status |
|---|---|
| C01 | Virgo's participating triplicity lord: ANSWERED by the text, 2026-09-11. Gr. Intr. V.14, 7 (p. 295): partner is Mars "except that Mercury acts as partner to them both in Virgo especially"; Figure 53's earth row reads `♂ (and ☿ when in ♍)`; fn 100: Mercury "rather than (or in preference to) Mars" (from Carmen I.1, 5). READY: `get_essential_rulers` returns Mercury as Virgo's partner, Mars for Taurus/Capricorn, caption "in preference to Mars (fn 100)"; consumers are the Chart caption (12292) and the Reference table (13391) only, no score. Also: help text at 13176/13183 cites "Figure 53" for PN IV's seven ages without naming the volume -- Gr. Intr. has its own Figure 53 (this one); name the volume. |
| C02 | Wells: RESOLVED 2026-09-09 -- engine follows Gr. Intr. Fig. 62; PN IV Fig. 98 differs in 3 cells and is transcribed as printed. The audit agrees. |
| C03 | 5° rule: SETTLED by the owner's ruling of 2026-09-11 (`OWNER_RULING_PLACES_VS_DYNAMICS_2026-09-11.md`): angles only, inclusive, planets only, longitude proxy kept and labelled; the `five_degree_all_cusps` switch is to be retired. The audit's "scope choice" is therefore closed; its unit discrepancy (diurnal vs zodiacal) stays a labelled proxy. |
| C04 | ray interpolation anchor (`as written`/`distant` vs `nearest`, 3.86° apart in its example): a reading the engine already keeps as distinct; the audit asks only that it stay labelled. |
| C05 | III.1, 13 `25"` -> `25"'`: photo-confirmed and applied in the corpus on 2026-09-11 (PN IV repairs D-07); engine caveat text is a READY wording order there. The audit's dimensional test agrees the engine's arithmetic is right. |

## Recommendation

Build A + B as one branch, `astra-audit-2026-09-11`, in a detached worktree; keep Astra's
harness as `tests/test_astra_audit_repro.py` (adapted to any interface changes) so the 23
expectations become the regression. F01-F03 first as the audit says; F02 needs the
elapsed-years mapping decision the audit flags (365.2425 is the project's Fig. 22
calibration -- keep it, label it). C01 is answered by V.14, 7 / Figure 53 / fn 100 and is READY; no owner question remains.
