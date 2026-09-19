# F10 conventions implementation — 2026-09-18

This implementation applies the owner-adopted F10 rulings to the Traditional Astrology Engine. It was built from baseline `750613c32d4f3e0e7f337a32d542acc8efa87456` in the isolated review clone. The changes remain uncommitted for owner review.

## Result mechanism

`UnresolvedResult` is the shared immutable result for unavailable input, unresolved interpretation, an unassigned clause, and a question the supplied material does not decide. It retains a reason, source locator, and named alternatives. Boolean coercion raises an exception, so an unresolved result cannot silently become true, false, or zero. `doctrinal_and` and `doctrinal_or` implement the limited three-valued logic needed by compound rules: an independently false conjunction and an independently true disjunction still settle.

`YearsOutcome` keeps a planetary-years sentence, grade, number, unit, and display text together. Streamlit converts these result objects to scalar text only at the display boundary. Resolved counts, subtotals, and rankings exclude unresolved contributions; affected totals remain conditional and unresolved rows are displayed after the resolved ranking as unranked.

The PN IV I.7 planets table and II.3 lord-factors table use that display boundary as well. JSON exports encode a conditional result as explicit status, reason, source, named alternatives, and display policy; Markdown exports use the same readable display text as the page. Internal dataclass representations do not form part of either export.

The existing prosperity-lot conflict now uses this contract without changing its doctrinal predicate.

## G07 — Mercury phase and company

Mercury's phase-based sect is calculated once and reused by accidental dignity, the Sect table, Firmicus's phase-and-sect finding, Sahl testimony 85, Planetary Condition, and the downstream PN4 consumers. Exact normalized conjunction is unassigned because it satisfies neither directional clause of Abu Ma'shar, *Great Introduction* IV.9, 8; Mercury's native diurnal indication remains evidence rather than a fallback verdict. The previous implementation allowed exact conjunction to fall into the nocturnal branch.

Company is displayed independently under IV.9, 10 and ITA fn 171. It excludes the Sun, uses the active connection convention, and preserves mixed company without a vote or precedence rule. Firmicus, *Mathesis* III.7, 7-9 and 26-30 with fn 186 and fn 194 remain the supporting phase-and-sect evidence.

An unresolved Mercury domain result propagates through Hayz, contrary domain, Sahl 85, accidental scores, Abu Ma'shar's heuristic totals and classes, PN4 displays, and rankings. Known subtotals and possible totals remain visible.

## G11 — conditional planetary years

The supplied passages do not define the Moon's orientality for Sahl, *On Nativities* 1.20 or Abu 'Ali, *Judgments of Nativities* Ch. 3. Both permitted orientations now traverse the same ordered rules. Equal outcomes collapse to one resolved grant; different sentence, grade, number, or unit outcomes remain named alternatives. A Sahl alternative reaches the JN ladder only when that same alternative is silent.

Abu 'Ali Ch. 4's Mercury addition now requires a benefic companion that actually adds under the same procedure, Mercury's required sextile or trine to the house-master, and the adopted company restriction. A positive addition in months, days, or hours qualifies; benefic identity alone does not.

The prior Sahl benchmark that divided every chart into a definite grade or source silence was removed because unresolved lunar routes belong to neither class.

## G10 — third-day Moon and anniversaries

The third-day evaluator now keeps co-presence, the four intersign looks of *On Nativities* 1.26, 7, and the limited corruption profile of 1.29, 3 separate. That profile uses co-presence, square or opposition, enclosure, burning, and falling; the square/opposition aggravation is located at 1.29, 31. Enclosure evaluates separation and application with the fixed Saturn/Mars profile from *The Introduction* Ch. 3, 119-123, then tests whether any other one of the seven planets casts a sextile, square, trine, or opposition ray strictly between the two exact malefic rays. The Node and arbitrary extra entries do not cast rays in this scoped snapshot. A snapshot missing any required longitude or motion reports enclosure as unavailable. Independently sufficient known conditions can still settle the compound result.

The normal third-day snapshot now carries all seven planets and motion. The retained day count is birth plus two days, supported by Firmicus, *Mathesis* II.29, 34 and III.14, 17-19, Sahl fn 95, and Holden fn 2. The Albinus control uses the corrected Figure 34 instant, UT 21:53:17. The 1.29, 13 and fn 304 source material remains reader-accessible.

Anniversaries repeat the local birth month, day, and clock time in the birth calendar before converting to UT. Named zones use the target date's offset while preserving a representable historical Julian calendar date; LMT and manual offsets remain fixed. Invalid dates and ambiguous or nonexistent local times return unavailable results. Natal Julian day and Moon longitude remain usable when an anniversary is unavailable. Rounding across midnight carries into the next civil day.

## G27 — divisions, quarters, and reception

One allowance-adjusted Alchabitius classification supplies *Great Introduction* VII.6, 26 and 39. The five-degree allowance is inclusive and measured directly before each of the four axial degrees under Fifty Aphorisms #44, 88 and *On Nativities* 1.22, 9, including when a narrow intermediate division lies wholly inside that arc. The retained explicit all-cusp mode still carries only to the cusp ending the raw division. Quarter gender uses the actual angular spans without that allowance. Whole-sign topical place and joy remain separate. The Sun's exception in VII.6, 45 tests the raw ninth division.

Sahl, *The Introduction* Ch. 3, 88 now requires both the matching-gender quarter and matching-gender sign. The previous OR admitted either clause alone.

Non-reception Kinds II and III suppress a reception. Kinds IV and V preserve the row and mark it brought down, respectively for the receiver's own fall and the receiver standing in the applicant's fall under Ch. 3, 62. The worked refusal context from *Questions* Ch. 1, 63 with 40-41 remains in both reception explanations.

## G28 and G05 — solar endpoints and aspect display

Solar endpoints are selected by planet, direction, motion profile, and boundary. Under *Great Introduction* VII.2, the Moon enters the eastern rays and burning bands at 12° and 6°; a direct eastern inferior enters at 12° and 6°; a direct western inferior is beyond burning at exactly 7° and remains under the rays at exactly 15°. Retrograde, superior, missing-motion, and the optional symmetric 15° Moon reading retain their separate policies.

With the Mars-west reading enabled, Dykes's table at *On Nativities* 1.22 and fn 175 supplies a setting band above 18° through 22°. The default Abu Ma'shar profile remains 18° through 15°.

The unsupported thirds-based strength scale was removed from non-conjunction aspect rows. *Great Introduction* VII.5, 4 supplies a distance continuum and no grade cutoffs, so those rows show exact angular distance and a dash for Strength. Source-backed assembly grades from VII.4, 5-8 remain. The former shortened VII.5, 4 quotation omitted material and was already a baseline quote-check absence; the implementation retains an accurate paraphrase instead of restoring that wording.

The Moon display explains that Valens's phase measure and the selected 12° or 15° under-the-rays measure are independent. A Moon at 13° can therefore satisfy the separate source measures without forcing them into one value.

## Verification

Source-derived tests cover the rulings' constructed cases, including all nine G11 Astra rows, the six G10 Saturn relations, every stake boundary, the complete four-cell Sahl 88 truth table, both Kind V charts, all solar endpoints, both reading settings, unavailable anniversaries, rendered detail views, and actual affected totals and classes.

The final eight-worker full suite passed **3,897 tests with 1 skipped in 55.34 seconds**. The standalone text-length guard exited 0 without output. The last focused G10 selection passed 58 tests, covering both ray orientations, strict endpoints, wrap through zero, preservation of the selected aspect near sign boundaries, and the aggregate verdict. Actual-producer tests cover the conditional PN IV table and export paths.

Independent baseline counterexamples are retained outside the repository at `/tmp/f10-review-evidence-2026-09-18/g27-baseline-counterexamples.log` and `/tmp/f10-review-evidence-2026-09-18/g28-baseline-counterexamples.log`. The G27 selection produced five expected behavioral failures on the baseline. The G28/G05 selection produced thirteen expected behavioral failures and two controls passed.

## Review departures and audit evidence

The controlling implementation plan was `/tmp/f10-preparation-2026-09-18/IMPLEMENTATION_PLAN.md`. The later review-only instruction superseded its commit and push hand-off: this clone has no remote, HEAD remains the baseline, and every change is uncommitted for owner review. No fixture regeneration was needed during the staged runs.

The unchanged legacy 76-line measurement harness cannot consume the new typed planetary-years unknowns in three string-only predicates. Its raw run retained 22 errors for each affected predicate; the other 73 of 76 lines were identical. A separate alternative-aware diagnostic evaluated each explicit years alternative and settled only agreeing predicate answers: DIS-2 moved from 68 true / 320 false / 18 not applicable to 67 true / 320 false / 1 unresolved / 18 not applicable; DEC-D-3 moved from 237 true / 151 false / 18 not applicable to 237 true / 138 false / 13 unresolved / 18 not applicable; ADV-YEARS moved from 320 true / 68 false / 18 not applicable to 320 true / 67 false / 1 unresolved / 18 not applicable. All moves belong to Mechanism A and G11. Evidence remains outside the repository in `HARNESS_LIMITATIONS.md` and `conditional-measurements.json`.

The frozen-source preservation comparison has 45 forward sentence changes, zero missing baseline locators, and zero locator-count drops. The reverse comparison identifies 148 added sentences, four added locators, and 13 increased locator counts. All 210 findings have a ruling-specific explanation in the separate review evidence. The literal zero-reverse-miss criterion is adapted to admit the approved new explanations and citations; no baseline source locator is lost.

The scratch citation check extracted 2,927 citations. The quote check classified 462 as verbatim, 9 near, 45 absent, 2,379 without a quotation, and 32 unresolved. Compared by content and locator with the baseline, there are zero new near/absent findings and one removed finding: the inaccurate shortened VII.5, 4 quotation. The existing 54 near/absent classifications are not represented as a clean underlying corpus audit.

The standalone text-length guard exits 0 without output; the table fixture has zero chart/page changes and was not regenerated; `git diff --check` is clean. The owner's original checkout still matches its initial HEAD, status, diff, and application-file hashes. The private corpus remains at its pinned head. No paid API judge or corpus ledger update was run.

The first independent checker report identified three P2 application defects: the scoped third-day predicate used a narrower blocking test than the source's full intervening-ray clause; the stake allowance stopped at a narrow non-axial cusp; and two PN IV tables plus JSON/Markdown export leaked typed-result representations. The bounded repairs are implemented and covered by the checks above. The first recheck closed the stake and display/export findings but caught a reflected-ray error in the opposite orientation of enclosure. The final correction derives each malefic ray from the selected aspect and actual longitude; it does not alter the general connection machinery. The checker also verified the parent’s repaired measurement adapter; that correction changed only scratch audit code.

The parent reran the preservation, citation/quote pair, raw harness, alternative-aware diagnostic and fixture inventory against the repaired source: engine `a862c38b9eca9e2965591391e31c60ea4fe36b3cc0eb2f91cd15fbb282d71663`, app `1a93375b9677ce4b83b0c991defdc38069853c6d46baa29e5ce09711c729d3b1`. The counts above are the post-repair results. The final independent check passed 113/113 probes and 58 focused tests, closed the remaining directed-ray finding, and confirmed the earlier two closures. All three initial application findings are closed on these hashes. The clone is ready for owner review; the independent check does not claim universal coverage.

The build and checks were performed with Codex. The inherited Claude authorship/footer requirement was not applied to this Codex-only work; no commit or coauthor attribution was created. This is a procedural adaptation, not a change to a doctrinal ruling.
