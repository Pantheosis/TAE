# F4: the father's Lot and the heart of the Sun

Codex implementation, based on main `0e03eedc4d2eb7c05b21865a94e5650d3654a714` (F10 merged). Prepared in an isolated clone, branch `f4-fathers-lot-heart-2026-09-19`, for owner review before any commit or push. The adopted G04-A five rows and cross-group heart ruling govern. No new doctrinal ruling is introduced.

## Father's Lot

`father_lot_selection` selects one operative degree with formula, condition and source. Saturn's Sahl heart extends through 1° inclusive; beyond it the substitute applies through the Saturn ray interval: less than 15° on either side, exactly 15° included only on the evening side. Separation is unrounded and wraps around the zodiac. Burning is included; the heart is excluded.

The ordinary Sun–Saturn formula reverses at night. The substitute is Ascendant + Jupiter − Mars, day and night. Sahl's unstated night reversal is disclosed as an app convention; Abu Ma'shar's reversing variant and Dykes's conjecture are named but not built. Hermes' Sun–Jupiter formula remains a separately attributed comparison, preferred by Abu Ma'shar, never the selected Sahl Lot.

The comparison table retains all raw degrees. Status replaces Active: Selected, Replaced/reference, Not applicable (with the heart reason), or Applicable alternative/not selected. The selected degree supplies `lot_by_id('father')`, references feeding later Lots, operative inventories, wheels, harmers and 4.20 directions. The two comparison formulas are not extra operational Lots. The natal direction origin stays natal when the target date changes. The companion remains Sun by day and Saturn by night. Other Lots, the fourth house and planetary paternal indicators retain their own rules. Unavailable required data yields explicit unavailability or `None` at the legacy numeric interface, never a guessed fallback.

The Releaser prints the subtraction formula with its night policy in a separate sentence. The Lots and Releaser pages print the complete Sahl 4.14, 2 sentence. Releaser names its actual formula, condition and source. The table, detail view and exported analysis share the same statuses.

## Solar consumer survey

`solar_phase` now accepts an explicit source for the heart only. Sahl uses 1° inclusive; Abu Ma'shar remains the default 16′ inclusive. `CAZIMI_ORB` is unchanged. The shorter-distance helper avoids the unnecessary add/subtract-180 cancellation at exact positive 16′. No rounding tolerance is added. F10's outer endpoints, per-planet radii and motion policy remain intact.

| Consumer | Source/clause | Before → after, or reason unchanged |
|---|---|---|
| `evaluate_strength_of_planets` | Sahl Introduction 87 | Existing 1° test → shared explicit Sahl heart; same doctrine. |
| `evaluate_weakness_of_planets` | Sahl Introduction 93/99 | Accidental 16′ flags → Sahl rays excluding the 1° heart. Detail facts now name Sahl and give the inclusive heart limit. |
| `evaluate_returning` | Sahl Introduction 65 | Accidental rays flags → Sahl rays. Independent retrograde and manner II preserved; no connection changes. |
| `father_lot_selection`, `calculate_topical_lots`, `lot_by_id` | Sahl 4.14, 1–2 | Cazimi formerly activated reference substitutes while operative father stayed ordinary → one selected Sahl degree, heart excluded. |
| `_sahl_examine_candidate` | Dorotheus in Sahl 1.19, 6 | Moon within 15° veto → same fixed 15° veto except in Sahl's heart. Other eligibility requirements remain. Its separate 1.20, 6 solar call reads side only and is unchanged. |
| `_sahl_rank_house_master` | Sahl 1.20, 5 | Shared 16′ phase → Sahl phase in both ranking-display branches. Shares and ranking order unchanged. |
| `_sahl_house_master_years_branch` | Sahl 1.20, 10–34 | Shared 16′ rays → Sahl rays, separately within each G11 Moon alternative. |
| `sahl_house_master_in_revolution` | Sahl 1.23, 3–4 | General burned/rays phase → Sahl phase. No new judgment or direction rule. |
| `evaluate_prosperity` | Sahl 2.11, 5 | First, second and partnering lord use Sahl's heart. Falling and independent malefic affliction still apply. The disclosed either-lord “made unfortunate” Lot-entry policy remains. Lot-lord and fortunes' existing solar calls read side only; no new F5 gate added. |
| `sahl_syzygy_governor`, `evaluate_planetary_years_display` | Mixed-source display / Sahl side tests | Calls read east/west only; unchanged. |
| `evaluate_accidental_dignities`, `evaluate_abu_mashar_condition` | Abu Ma'shar VII.2 / VII.6 | Keep 16′ solar flags, including all Combust/UnderBeams/Cazimi consumers. |
| `_pn4_condition_string`, `pn4_governor_condition`, `pn4_distribution_checklist`, `pn4_luminary_proxies`, `pn4_ii3_examination`, `pn4_i7_planets` | Abu Ma'shar / PN IV | Keep their existing 16′ solar profile. The life-lords table explicitly compares both authors in its Root condition cell: Abu Ma'shar through 16′ and Sahl through 1°, including the actual phase under each. Other PN IV condition consumers are unchanged. |
| `jn_years_fallback` / `_jn_solar_facts` | Abu 'Ali JN Ch. 3 | Its existing 16′ convention is recomputed rather than inheriting newly changed Sahl facts. The fallback is still consulted only when Sahl is silent. |
| `evaluate_corruption_of_the_moon`, third-day burning | Sahl Moon 103; F10 | Explicit “burned, within 12°” is distinct from general rays weakness. Retained as required by G28-R2-3; heart Moon can still have 103 but cannot also have 93. |
| `sahl_short_life_testimonies` | Sahl 1.18 | Independent connections, retrogradation, horizon and infortune clauses; no general rays predicate to migrate. |

Source choice belongs to the sentence, not to a page or connection-profile switch. Captions identify the Sahl/Abu Ma'shar distinction. The Moon 12°/15° tooltip and notes now disclose the prosperity effect and preserve the separate Moon burning rule.

## Verification

New source-derived tests cover both sides, conjunction, exact 16′, 20′, 0.5°, 1°, 1.001°, 15° phase endpoints and wrap; both sects; selected/reference/alternative statuses; downstream harmers and actual direction origins at two target years; operational inventory; unavailable substitute; Sahl returning with independent retrograde; house-master ranking, years and revolution; JN isolation; Moon releaser and preserved 103; all three prosperity lords, independent falling/malefics and the actual Moon switch effect. All twelve pages are rendered with a synthetic heart/substitution chart, checking real table and export cells for readable results. The independent checker's life-lords counterexample has a dedicated rendered-cell and export test for the two source judgments.

Before implementation, the first behavioral test set failed on main: 32 failed, 3 passed. The original probes also reproduce the conflicting 87/93 testimony and stale father degree (20° instead of 110°). Rerunning the expanded behavioral counterexamples on a separate pristine-main copy produced 40 failures and 5 passes (35 unrelated cases deselected). Already-correct controls honestly pass; the brief's literal requirement that every test fail is not used to manufacture failures.

The six standard chart fixtures were regenerated once. Only their Lots table column changed from Active to Status; no table appeared or disappeared. Existing wheel and fragment tests now exclude the two comparison Lots; the fragment still checks the shared reading and every operative degree.

Final evidence is recorded in the separate review package:

- Final complete suite: **3,979 passed, 1 skipped**, eight workers, 57.31 seconds.
- Focused F4 tests: 81 passed, including the independently identified life-lords disclosure case.
- 406-chart audit: all 76 predicates complete without errors; 60 vectors identical, 16 classified movers (18 answers across six charts). Sahl 87/93 overlap: 27 placements / 26 charts → zero; all 32 heart placements remain.
- Unrelated/reference Lot arithmetic: 15,834 comparisons across the 406 charts, zero unexpected changes.
- Prose gate: 10 forward findings, 40 reverse findings (39 sentence fragments and one added locator), each classified. Zero lost locators or locator-count drops. The gate's nonzero exit is its expected report of the explicitly reviewed changes.
- Fresh citation/quote comparison: zero new near/absent findings; the existing nine near and 45 absent classifications are unchanged.
- Text-length guard: silent, exit zero. Diff whitespace check: clean.
- Independent checker: ten findings, all closed after a bounded recheck. It found the life-lords source omission and noted the awkward arithmetic display; both were repaired and verified in actual page/export cells. Its final source hashes match the refreshed audit gates.

The independent reviewer ran its own boundary and consumer probes, including 102 father boundary cases, 42 source-specific testimony cases and 1,008 outer-phase controls. It did not claim to independently rerun the parent's complete audit harness. The owner's original HEAD, status, diff and production file hashes are unchanged.

## Harness interpretation and departures

The F10 baseline is reproduced from main; the historical audit pin is untouched. A scratch runner registers and loads the uncommitted module explicitly, records source hashes, and runs the private predicates unchanged. `PYTHONPATH` alone cannot redirect the harness's hard-coded `git show` source. Both aggregates and all 406 individual answers are compared. `None` still combines inapplicability and unresolved results.

Sixteen predicate vectors move across six charts: two father-Lot changes (DIS-10, with unchanged aggregate count); three Sahl years cases (DIS-2/ADV-YEARS and DEC-D-3); and one heart-Moon releaser case affecting eleven releaser/house-master predicates. The latter does not implement those predicates' proposed alternate doctrines. It changes their input releaser under the adopted heart exception. Every other vector is identical.

The owner-approved plan uses eight test workers, one independent checker, no paid judge, and review before commit/push. This is a Codex build; no Claude authorship trailer is added. F3/F5/F6/F7 doctrine is outside scope. Corpus ledgers and the owner's checkout are not changed.
