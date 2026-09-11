# Astrology Engine: Independent Adversarial Audit for Claude

Date: 2026-09-11  
Artifact reviewed: supplied `Archive.zip`; no engine code was changed.

## Verdict and implementation instructions

**The engine is not yet a faithful implementation of all the supplied texts.** Several foundational tables and spherical transformations are correct, but reproducible defects change historical dates, active time lords, horizon-based condition, and the ordering or classification of planetary events. Passing the existing tests does not resolve those defects.

This report distinguishes **14 implementation or reporting defects** (F01–F14) from **five source, interpretation, or approximation issues** (C01–C05). F11, F13, and F14 concern presentation/provenance; they are not evidence that the underlying ephemeris is wrong. C01 establishes a definite mismatch with an additional supplied source, but applying that source to the shared table requires a source-policy decision. C02 is an existing, defensible selection between conflicting witnesses.

For Claude:

1. Fix F01–F03 first. Preserve separate concepts for civil age, elapsed time, and the active solar-return cycle.
2. Add the numerical/source examples below as regression cases before changing the affected calculations. The appendix contains a runnable harness that exposes the current failures without editing the application.
3. Fix F04–F10 next. Ordered configurations require actual event order, with sufficient numerical precision to resolve it.
4. Address F11–F14 as reporting and boundary corrections. Do not round astronomical inputs merely to make their display look right.
5. For C01–C05, retain the cited alternatives and identify the selected witness or approximation. Do not silently merge traditions or “correct” a historically different table into a single universal one.
6. Reconcile tests that encode an old interpretation with the source, rather than treating those tests as source authority. Record changed behavior and source choices in the changelog.

Priority means impact on this application: **P1** broad or substantial incorrect results; **P2** incorrect results under identifiable conditions; **P3** local boundary, display, or provenance problems. No claim is made about the predictive validity of astrology; the audit concerns implementation of the supplied material.

## Reviewed version, evidence, and limits

Archive SHA-256:

`733c61a1cd6dae1bb832882f54bf7829733d26d7873d51e5fa0d4343aeabc7ae`

Application: `Executable/app.py`, 13,460 lines. Its SHA-256 is:

`d925498bfcbb397781d9ba6ae9bc1bf84751146a052d0dbb1258dfce52894520`

The extracted application was compared with the original ZIP member and is byte-for-byte unchanged. The ZIP contains 1,741 files, including repository history and repeated source material. Counts of repeated transcriptions are not counts of independent witnesses.

All application line numbers below refer to this version of `Executable/app.py`. Source paths are relative to the extracted archive:

| Citation key | Supplied file | How citations are identified |
|---|---|---|
| S-Intro | `consolidated_texts/sahl_introduction_ch3.md` | Sahl, *Introduction*, chapter 3, numbered sentence; printed **Sahl I** page |
| S-Aph | `consolidated_texts/fifty_aphorisms.md` | Aphorism number, sentence number, printed **Sahl I** page |
| S-Nat | `consolidated_texts/on_nativities.md` | Sahl, *On Nativities*, chapter/subchapter and sentence; printed **Sahl I** page |
| AM-VII | `consolidated_texts/abu_mashar_book_vii.md` | *Great Introduction*, book/chapter/sentence; printed **Gr. Intr.** page |
| AM-Full | `consolidated_texts/gr_intr/abu_mashar_great_introduction.md` | Additional supplied full transcription; same book/chapter/page convention |
| PN4 | `consolidated_texts/pn4/pn4_complete/persian_nativities_iv.md` | *Persian Nativities IV*, book/chapter/sentence; printed **PN IV** page |

**Do not interchange the page and figure numbers of these volumes.** For example, Gr. Intr. Figure 98 is not PN IV Figure 98. Authorial text, Dykes's editorial notes, and inserted project notes are separate kinds of evidence. Prior audit/adjudication files were useful leads; their assertions were not accepted as independent proof. The full AM transcription is additional evidence, not automatic authorization to replace every existing profile.

There are no PDFs in this archive. In particular, the TNAC/Course PDFs cited by the project are not supplied here. Comparisons below are against the supplied transcriptions and identified tables; this was not a new comprehensive photographic/OCR collation. Missing source images and absent course material limit what can be certified. Thousands of prose combinations, all UI paths, all dates, and every selectable doctrine combination have not been exhaustively proven correct.

Execution used Python 3.12.14, pyswisseph 2.10.3.2 / Swiss Ephemeris 2.10.03, pytest 9.1.1, pandas 3.0.5, timezonefinder 8.3.0, and Streamlit 1.63.0. The archive specifies Python 3.14 and Streamlit 1.62.0; those two runtime differences are a validation limitation. Core calculations were loaded up to the UI marker, with preferences disabled. Full PN4 timing bundles were executed, not merely their isolated arithmetic helpers.

In this environment, a sample `swe.calc_ut(2451545.0, swe.MARS)` returned flag `260` (`SPEED | MOSEPH`): **Moshier fallback was actually used**. The real-chart results are reproducible under that configuration. This audit does not claim independent JPL verification of planetary positions or equivalent precision at every historical epoch. The linear/quadratic event cases are explicit synthetic ephemerides with known exact solutions; they are not purported historical charts.

## Prioritized defects

| ID | Priority | Affected behavior | Classification |
|---|---|---|---|
| F01 | P1 | Julian dates validated and shifted using Gregorian date arithmetic | Definite calendar error |
| F02 | P1 | Fractional time-lord changes frozen until a civil birthday | Definite timing error |
| F03 | P1 | A future solar return selected as the current year | Definite interval-selection error |
| F04 | P2 | Hayz/contrary domain use a false horizon proxy | Definite coordinate error |
| F05 | P2 | Escape reported after the original conjunction already succeeds | Definite event-order error |
| F06 | P2 | Coarse ingress times reverse contact-versus-ingress order | Definite numerical error |
| F07 | P2 | A retrograde excursion across a sign boundary is missed | Definite event-search incompleteness; real frequency unmeasured |
| F08 | P2 | Sahl's departing receiver relationship is reversed | Definite relationship error; conjunction of clauses remains interpretive |
| F09 | P2 | Abū Maʿshar connection survives positive separation under one minute | Definite textual boundary error |
| F10 | P2 | Completed eastern solar-phase thresholds stay in the previous phase | Definite textual boundary error |
| F11 | P3 | “Active point” displays the start of a distribution segment | Definite reporting inconsistency |
| F12 | P3 | A fardār subperiod owns its own advertised end instant | Definite floating-boundary error |
| F13 | P3 | A whole entered arcminute is displayed one minute low | Definite sexagesimal round-trip defect |
| F14 | P3 | Available table/formula authority is described as absent | Definite provenance/count errors |

### F01 — Julian calendar handling is internally inconsistent

**Functions:** `parse_iso_date` (10676–10682), `pn4_datetime_from_jd` (10633–10641), `calculate_traditional_chart` (170 onward), and the sidebar's LMT/manual-offset conversion (11424, 11435).

**Authority:** The Swiss Ephemeris programmer manual, §9.1, explicitly distinguishes Julian and Gregorian calendar flags in `swe_julday` / `swe_revjul`. Python's `datetime` calendar is proleptic Gregorian. These are technical calendar requirements, not an invented medieval passage. See [Swiss Ephemeris calendar functions](https://www.astro.com/swisseph/swephprg.htm), [Python datetime/date objects](https://docs.python.org/3/library/datetime.html), and [USNO Julian-date conversion](https://aa.usno.navy.mil/faq/JD_formula).

**Reproduction:**

- `parse_iso_date('1300-02-29')` returns `None`, although this is a valid Julian date.
- `pn4_datetime_from_jd(swe.julday(1300, 2, 29, 12, swe.JUL_CAL))` raises `ValueError: day is out of range for month`. The JD is `2195942.0`.
- Enter local Julian **1300-03-01 00:30**, with an offset of **+02:00** (also the LMT offset at 30° E). The app subtracts two hours with `datetime`, producing Gregorian-components `1300-02-28 22:30`, then interprets those components as Julian. Actual JD: **2195941.4375**. Correct JD: `swe.julday(1300,3,1,0.5,swe.JUL_CAL)-2/24` = **2195942.4375**. The chart moves **one full day**.

**Expected:** Julian UT date is February 29 at 22:30. Calendar validation, offset arithmetic, formatting, and conversion must agree on which calendar a date belongs to.

**Implementation requirement:** Carry a JD or calendar-tagged date representation through arithmetic. Do not use Gregorian `datetime` as the validator/carrier of every Julian civil date. Define the reform-date policy, reject nonexistent dates under that policy, and handle rounding across midnight as a date carry rather than clamping the time. Cover Julian-only leap days, positive/negative offsets across midnight, and the reform boundary. Fixing only the Swiss flag does not fix this defect.

### F02 — Fractional fardār and distribution clocks are truncated to whole years

**Functions:** `pn4_timing_bundle` (10752, 10773, 10777, 10787 and releaser-current selection), calling `pn4_fardar_at_age` and `pn4_distribution_at_age` with completed civil years.

**Source:** PN4 IV.1.5–6, pp. 364–365: the main lord stands alone for “an amount of one-seventh of its years,” then other planets partner for one-seventh each. IV.1.11, p. 365 explicitly gives the Sun's initial subdivision as “1 year, 5 months, 4 days, and approximately 6 hours.” PN4 III.1.13, p. 288 gives **one degree/year, 5′/month, 1′/six days, 10″/day**; III.1.15–16 changes the partner when the direction reaches another body/ray. PN4's introductory explanation of Figure 22, pp. 62–63, likewise changes the distributor on a specific date within a year.

**Reproduction A:** Birth **2000-01-01 12:00 UT**, 0° N, 0° E, target **2001-07-01**. The bundle uses noon for a target date.

| Quantity | Actual | Required by the fractional periods |
|---|---|---|
| Elapsed years, using the engine's own 365.2425-day mapping | `1.4976351328` | Same |
| Age passed into fardār selector | `1` | Fractional elapsed time |
| Main/sub-lord | Sun/Sun | **Sun/Venus** |
| Sun/Sun subperiod end | `1.4285714286` years | Already passed |

**Reproduction B:** Same birth, target **2012-10-21**. Elapsed time is `12.8051910717` years. The bundle marks Mars current for `[8.0091665718, 12.7058199578)`, while Saturn is current for `[12.7058199578, 12.9447901601)`. Its own date table says Saturn began **2012-09-15**, yet the “Now” mark remains on the Mars row beginning **2008-01-04**.

**Expected:** Subperiods and continuous directions change at their fractional endpoints. These examples are far enough beyond the boundaries that choosing 365.25 instead of 365.2425 days does not rescue the whole-year result.

**Implementation requirement:** Separate elapsed time from the ordinal year used for annual profections and age labels. Apply the documented civil-day mapping consistently to the dated distribution rows and their current selection. Do not blindly make every annual technique fractional. Retain the distinction between the idealized 360-day rate ladder and the modern conversion to calendar dates; see C05.

### F03 — The selected current revolution can lie in the future

**Functions:** `pn4_timing_bundle` (10752–10769, 10895–10902), `pn4_solar_revolution_jd`, `pn4_monthly_revolution_jd` callers.

**Source:** PN4 I.2.1–3, pp. 148–149: the solar year concludes when the Sun “came back to his position in which he was at the root”; the next year starts with motion from that returned position. I.2.4 requires positions “for that time.” Civil birthday components are not the specified astronomical boundary.

**Reproduction:** Birth **2000-01-01 23:00 UT**, 43.7792° N, 11.2463° E; target **2003-01-01**, evaluated at 12:00 UT.

- Target JD: `2452641.0`.
- Selected “current” return: `2452641.185873726`, **2003-01-01 16:27:39 UT**, still 4h 27m 39s in the future.
- `day_of_year = -0.185873726`; month is incorrectly initialized to 1; the monthly revolution is also future; `small_days_current is None`.
- The correct containing cycle began **2002-01-01 10:39:26 UT** (`2452275.94405034`). Its twelfth monthly revolution began **2002-12-03 04:47:56 UT**.

**Expected:** `return_n <= target_jd < return_(n+1)`, with target inside month 12 of that cycle. A selected date before this year's return still belongs to the preceding return cycle.

**Implementation requirement:** Use a civil-age estimate only to seed a search. Bracket the target by adjacent actual returns; derive the monthly and daily clocks from that bracket. Keep the cycle index consistent for techniques sourced to that annual cycle. Test immediately before, exactly at, and immediately after returns, including returns on the adjacent civil day.

### F04 — Planetary hayz still uses ecliptic longitude as a horizon test

**Function:** `evaluate_accidental_dignities`, especially 1426 and its Hayz/ContraryDomain branches. The correct `_sin_altitude` helper is already used elsewhere, so the application can disagree with itself.

**Source:** AM-VII VII.1.37–39, pp. 411–412, and VII.6.13, pp. 478–479: for the male/diurnal case, “by day above the earth and by night below the earth.” VII.1 fn. 24 discusses the ambiguity between gender and sect and the Mars exception. The test below uses Jupiter and does not depend on resolving that ambiguity.

**Reproduction:** **2000-01-01 01:40 UT**, 51.5° N, 0° E.

- Jupiter: longitude `25.235793606°`, latitude `−1.264402680°`.
- Ascendant: `204.643526961°`; nocturnal chart; Jupiter in masculine Aries.
- Actual geocentric altitude: **−0.144034942°**, below the horizon.
- Longitude-only proxy `(Jupiter_lon - Ascendant) % 360 > 180` says above.
- Returned `Hayz=False`; expected **True** under the engine's sect/gender choice.

Another case, **2026-06-01 01:44 UT**, same location: Saturn is approximately **1.926° below** the horizon and is also misclassified.

**Mathematical oracle:** Rotate the actual ecliptic vector, including latitude, into equatorial coordinates. Then `sin h = sin φ sin δ + cos φ cos δ cos(ARMC − α)`. The appendix uses a Cartesian rotation rather than calling the engine's altitude helper.

**Implementation requirement:** Supply true horizon facts to the accidental evaluator. Specify geocentric versus topocentric altitude and refraction consistently; the present geocentric convention is sufficient to demonstrate this error. Do not decide a body's hemisphere solely from its longitude relative to the Ascendant. Retain the separate Mars/source-profile decision.

### F05 — Escape fails to check whether the original contact happens first

**Function:** `evaluate_escape` (3210–3283), particularly the search at 3265–3276.

**Source:** AM-VII VII.5.119, p. 472, Figure 139 and fn. 197: after the applicant changes signs, another planet is “closer to it than [the first one], so its connection is with the other planet, and its connection with the first one is nullified.” The footnote describes Venus encountering Saturn's body while Mercury escapes. S-Intro 3.57 fn. 77, p. 61, independently explains why connecting with the original planet **before another** can complete the original situation.

**Exact synthetic reproduction:** Longitudes in degrees and time `t` in days:

- Moon: `1 + 13t`.
- Mars: `29 + 0.5t`.
- Saturn: `40 + 0.03t`.

Mars enters Taurus at `t=2`; Moon follows at `29/13 = 2.2307692308`. Moon–Mars conjoins at **2.24 days**. Moon–Saturn conjoins later, at **3.0069390902 days**. Nevertheless the engine reports **Moon: Escaped Mars; Connected Instead With Saturn**. The first contact was not nullified.

**Real ephemeris reproduction:** At JD **2451587.0** (**2000-02-12 12:00 UT**), simulate the seven planets for 100 days at the default one-day sampling interval. The engine reports Mars escaping Jupiter and meeting Moon instead. Mars enters the destination sign at approximately `39.5546875` days; Mars–Jupiter unites at **53.7778320313** days, before Mars–Moon at **54.0581054688** days. The original conjunction precedes the alleged substitute by about **6h 43m**.

**Implementation requirement:** Compare the original target with competing contacts after ingress, not merely before the target first leaves its sign. Enforce the closer/intercepting condition at the relevant stage and reject an Escape once the original connection has succeeded. Keep body contact and aspect contact explicit according to the selected passage; do not assume any later conjunction is an interception.

### F06 — Ingress precision is too coarse for the logical cutoff it controls

**Functions:** `_bisect_crossing` (2847–2859), `_simulate_forward_uncached` (2877–2912), and `_perfection_day` (2979–3032); callers include sign-limited connection and lunar-portion searches.

**Source:** PN4 II.22.1–4, pp. 264–265: use the planets the Moon connects with “so long as she is in her [current] sign”; otherwise the empty-course alternative applies. AM-VII VII.5.119 also explicitly orders contact and sign change. These rules require correct event ordering, not a particular historical numerical algorithm.

**Reproduction:** `Moon(t)=29.636+13t`, `Sun(t)=89.948+t`, in degrees/day. Exact sextile occurs at **0.026 day**; Moon leaves Aries at **0.028 day**, 2.88 minutes later. With `horizon_days=1, step_days=0.25`:

- Recorded Moon ingress: **0.0234375 day**, about 6.57 minutes too early.
- `_perfection_day(..., target=60, before_day=recorded_exit)` returns **None**.
- The same call with the true cutoff `0.028` finds the sextile at approximately `0.02587890625`.

The default ingress bisection tolerates a **0.02-day bracket** (28.8 minutes); contact bisection uses a much smaller tolerance. Treating the coarser midpoint as an exact exclusion boundary reverses the order.

**Implementation requirement:** Use compatible event precision, or retain time brackets and refine overlapping brackets until order is established. Exact simultaneity requires an explicit boundary policy. Display rounding is separate from event resolution. Merely increasing the simulation horizon cannot fix this error.

### F07 — Retrogradation can hide two sign crossings inside one sample interval

**Function:** `_simulate_forward_uncached`, endpoint-only sign comparison at 2899–2904.

**Source:** AM-VII VII.5.117–119, pp. 471–472, orders stations, retrograde movement, and sign changes. S-Aph #48, sentences 99–102, p. 87, explicitly distinguishes stations toward retrogradation from stations toward direct motion. A station does not imply that sign membership is constant between the sampled endpoints.

**Exact synthetic reproduction:** Mercury has

`λ(t)=29.99+0.12t−0.12t²`, `v(t)=0.12−0.24t`, for `0 <= t <= 1` day.

The endpoints are both 29.99° Aries, but Mercury reaches 30.02° at the station. It crosses 30° at `(1−sqrt(2/3))/2 ≈ 0.0917517095` day and recrosses at `(1+sqrt(2/3))/2 ≈ 0.9082482905` day. With one-day sampling the engine returns **`sign_exits=[]`**, although it finds a first station near day 0.5.

**Classification limit:** This proves search incompleteness for a smooth, speed-consistent ephemeris. It is not a measured frequency estimate for actual Mercury charts.

**Implementation requirement:** Divide intervals at extrema/stations and search each monotonic interval for all crossings. Apply the same completeness reasoning to relative-longitude extrema when searching aspects; a sign-change-only root search cannot in general find two roots with equal-sign endpoints. Distinguish “searched and none exists” from “not established within the search window.”

### F08 — Sahl's receiver is looked up in the wrong planet's position

**Function:** `evaluate_weakness_of_planets` (6074–6204), especially 6165–6168.

**Source:** S-Intro 3.97, p. 67: “it is separating from a planet receiving it.” The reception direction is unambiguous in 3.52, p. 60: Moon in Aries connects with Mars, and “he receives her because [Aries] is his house.” Thus the departed planet must own a relevant dignity **at the departing planet's position**. Sentence 97 fn. 99 says: “I am not sure that these conditions must both exist at once.” That concerns whether its two clauses are conjoined, not which planet receives which.

**Reproduction A:** Moon at **190.5°**, speed 13°/day; Venus at **190°**, speed 1°/day. Moon has just separated from Venus in Libra. Venus is the domicile lord of Moon's position and is the former receiver. The separating-receiver label is absent.

**Reproduction B:** Moon **95.5°**, Saturn **95°**, Jupiter moved to **120°** to remove the Cancer exaltation confound. The engine prints **“Separating from saturn, which would have received it (97)”**. Saturn has no domicile or exaltation at 5.5° Cancer. Moon owns Saturn's sign, the reverse relationship.

Use the appendix's remaining-planet fixture, whole-sign Ascendant 0°, and diurnal sect. These reproduce the current independently evaluated separating clause; choosing a strict AND policy for the whole sentence may change whether the whole testimony is emitted, but cannot make its reversed receiver lookup correct.

**Implementation requirement:** Evaluate the departed receiver's dignities at the departing planet's longitude. Reuse a directed reception definition appropriate to Sahl. Separately document whether sentence 97 requires both conditions at once; do not import Abū Maʿshar's reverse reception into Sahl to justify the reversal.

### F09 — An actually separated planet remains “connected” for up to one minute

**Function:** `_is_connected_abu_mashar` (2010–2045), separating branch at 2041.

**Source:** AM-VII VII.5.16, p. 446: “if the light one passed by the slow one by one minute or by less than that, then it has already … SEPARATED.” VII.5.34, p. 452 repeats “by 1' or less” and distinguishes continuing to blend in nature from still connecting.

**Reproduction:** Moon **10.005°**, speed 13°/day; Saturn **10°**, speed 0.03°/day. The pair kernel correctly reports `motion='Separating'`. `_is_connected_abu_mashar(row)` nevertheless returns **True**. The Moon is **18 arcseconds past** exact conjunction.

**Expected:** Not connected; a separately applicable blending-in-nature rule may remain true. This example avoids the floating-point representation of exactly 1′.

**Implementation requirement:** Remove the physical one-arcminute post-exact grace interval from the connection predicate. Treat tiny machine uncertainty at exactness separately, and preserve the distinct nature/blending state. Regression cases must include exact contact, 18″ past, over 1′ past, both aspect orientations, and retrograde relative motion.

### F10 — Solar-phase endpoint inclusivity contradicts the eastern sequence

**Function:** `solar_phase` (1355–1378), with effects on accidental and Abū Maʿshar conditions.

**Source:** AM-VII VII.2.11–14, p. 414: when Saturn/Jupiter complete 6° and Mars 10°, “they have already gone past burning”; when they complete the next 15°/18° limits they become strongly easternizing. VII.2.40–41, p. 418 similarly says a **full 7°** has passed burning and completion of **12°** begins strong easternization for the inferior sequence described there. By contrast VII.2.31–34, p. 417 enters the new western phase **at** its threshold. Cazimi is explicitly inclusive at 16′ (VII.2.7–9, fn. 29); preserve that separate rule.

**Reproduction:** Set Sun longitude to 100° and take the **opening eastern** sequence.

| Planet longitude | Elongation | Actual phase | Source phase |
|---|---:|---|---|
| Saturn 94° | 6° east | Burned | Under the rays |
| Saturn 85° | 15° east | Under the rays | Strong easternization/outside these phases |
| Mars 90° | 10° east | Burned | Under the rays |
| Mars 82° | 18° east | Under the rays | Strong easternization/outside these phases |
| Mercury 93° | 7° east | Burned | Under the rays |
| Mercury 88° | 12° east | Under the rays | Strong easternization/outside these phases |

**Implementation requirement:** Specify phase transitions for the relevant direction through the synodic cycle. Do not simply replace every `<=` with `<`: the western approach has different endpoint ownership. For Mercury/Venus, longitude side alone also cannot represent every approaching/departing condition. The eastern returning inferior sequence has a printed **6°** at VII.2.44 versus **7°** earlier; fn. 43 explicitly flags that discrepancy. Preserve a documented reading there instead of pretending it is settled by the generic table.

### F11 — The distribution's “Active point” is a segment origin

**Functions:** `_pn4_seg_degree` (10695–10703), `pn4_timing_bundle` year-row construction (10813–10819), compared with `pn4_revolution_image` (around 9900).

**Source:** PN4 I.6.6, p. 161 requires the endpoint of the distribution. Footnote 34 explains: “the very degree which the distribution had reached.” III.1.11–16 distinguishes the bound/distributor and the changing position within the direction.

**Reproduction:** Birth **2000-01-01 12:00 UT**, equator/Greenwich; target **2001-01-01**. Even using the current integer-age convention to isolate this from F02:

- Selected segment begins at age `0.5781971568`, at **12° Aries**.
- The year-indicator row prints **“Active point: 12° Ari 00'”**.
- At age 1 the directed longitude is **12.4564706979°** = **12° Aries 27′** to whole minutes. The revolution-image path computes the degree reached using the age, not the segment start.

**Implementation requirement:** Show the endpoint calculated at the applicable time, or rename this field explicitly to “segment start/bound entry.” A segment-entry value must not masquerade as the reached point. This is a reporting correction; it is distinct from F02's incorrect choice of the current segment.

### F12 — A fardār subperiod fails at its own advertised endpoint

**Function:** `pn4_fardar_at_age` (10312–10345), specifically `offset // each`.

**Source:** PN4 IV.1.5–6, pp. 364–365: seven successive equal subdivisions in sphere order, starting with the main lord. The arithmetic subdivision of the Sun's ten years gives Sun, Venus, Mercury, then Moon at `30/7` years. The same instant cannot remain inside an expired subdivision under the half-open convention already used for the main periods.

**Reproduction:** Obtain `r = pn4_fardar_at_age(4.0, 'Diurnal')`. It returns Mercury as sub-lord and `sub_to=4.285714285714286`. Feed **that exact returned value** back into the function. It still returns Mercury, with the same expired `sub_to`. Expected next sub-lord: **Moon**.

**Implementation requirement:** Compare consistently constructed boundaries or use a documented numerically stable subdivision scheme. Test each returned end value, its immediate floating predecessor/successor, main-period changes, nodes, and the 75-year restart. F02's whole-year call masks rather than cures this independent boundary error.

### F13 — Sexagesimal formatting loses an entered whole minute

**Function:** `get_degree_string` (265–270).

**Source/context:** PN4 I.6.2, p. 159 explicitly specifies the Ascendant by “degree and minute.” AM-Full V.18.3, p. 301 likewise uses degree-and-minute input. One degree contains 60 arcminutes; this test concerns preservation of an exactly intended minute, not a new historical rounding convention.

**Reproduction:** `get_degree_string(30 + 1/60)` returns **`00° Tau 00'`**, while the sexagesimal input is **`00° Tau 01'`**. Binary representation leaves the fractional-minute product just below 1, and `int()` truncates it. Controls: `360` wraps to 0° Aries, and `−1/60` displays 29° Pisces 59′ correctly.

**Implementation requirement:** Define the display policy explicitly, including decimal-to-sexagesimal tolerance/rounding and carry at 60′/30°/360°. Preserve whole-minute round trips without shifting computational longitudes or rounding them before bound/ordinal-degree tests. This is a display defect; it does not establish a one-minute ephemeris error.

### F14 — Provenance claims lag behind the supplied corpus

**Affected locations:** `_twelfth_part_sign` (6909–6923); `pn4_twelfth_part` and surrounding comments (9840–9856); `tests/test_base_tables.py` face section around line 86; `WELLED_DEGREES` provenance comment (4999 onward).

**Source and reproduction:**

- AM-Full V.18.1–3, p. 301, Figure 57 explicitly gives 2½-degree twelfth-parts, begins with the sign itself, and instructs multiplying the within-sign degree/minute by **12** and projecting from that sign's beginning. The code's comment instead says the construction is supplied from convention because it is absent from the available texts. Check `pn4_twelfth_part(35.25)`: **93°**, correctly Taurus 5°15′ → Cancer 3°. The numerical result needs no correction; the “unattested” claim does.
- AM-Full V.15.1–7, pp. 295–296, Figure 54 explicitly specifies the face sequence beginning Aries/Mars and proceeding through planetary spheres. All **36** implemented face rulers match. The test heading “convention; no table in corpus or course” is now false as a claim about the supplied corpus.
- Gr. Intr. Figure 62, p. 308, and `WELLED_DEGREES` contain **64** entries: `sum(len(v) for v in WELLED_DEGREES.values()) == 64`. The comment says “all 62 cells.” PN IV's different Figure 98 has 62; see C02.

**Implementation requirement:** Update provenance and counts without changing these matching numerical tables. Record that the additional full transcription supplies corroboration; this does not silently override the project's source precedence or establish that every new AM-Full chapter is already implemented.

## Source and interpretation issues: preserve the disagreement

### C01 — Virgo's participating triplicity lord differs from the shared table

**Priority:** P2 if the shared reference is represented as implementing AM-Full V.14; otherwise a required scope/profile disclosure.

**Functions/data:** `TRIPLICITY` (1103–1108), `get_essential_rulers` (4221–4242), reference rendering around 13387.

**Exact source:** AM-Full V.14.7, pp. 294–295: the earth-triplicity partner is “Mars—except that Mercury acts as partner to them both in Virgo especially.” Figure 53 includes Mercury in Virgo; fn. 100 explains Mercury “rather than (or in preference to) Mars.”

**Reproduction:** `get_essential_rulers(165)['triplicity_participating']` returns **Mars** for 15° Virgo. A literal single-partner implementation of the quoted exception yields **Mercury**. Taurus and Capricorn retain Mars.

**Assessment:** The mismatch to this passage is definite. It is not proof that the general earth table is historically wrong for every other source. Current essential scoring uses the active day/night lord, so do **not** claim this automatically changes all dignity scores. Decide whether to provide an AM-specific Virgo exception, an additional/preferred-partner representation, or an explicit statement that the shared table follows a different witness. Test those three earth signs in both sects after the policy is chosen.

### C02 — The two wells tables genuinely disagree

**Functions/data:** `WELLED_DEGREES`; `evaluate_special_degrees` and other well consumers.

**Exact sources:** AM-Full V.21, Figure 62, p. 308; PN4 VIII.15, Figure 98, p. 547. AM-Full V.21.4, p. 307 itself says authorities disagree about the degrees. These are the discrepant memberships:

| Position to test | Gr. Intr. Fig. 62 | PN IV Fig. 98 | Current engine |
|---|---|---|---|
| Aries 28°30′: ordinal 29th | Well | Not a well | Well |
| Gemini 11°30′: ordinal 12th | Well | Not a well | Well |
| Gemini 12°30′: ordinal 13th | Not a well | Well | Not a well |
| Pisces 27°30′: ordinal 28th | Well | Not a well | Well |

**Reproducible predicate:** for each longitude `x`, compare `int(x % 30)+1` with the corresponding sign's listed ordinal degrees. The rows occur at AM-Full lines 6538–6571 and PN4 lines 11259–11291.

**Assessment:** Current data correctly follows the selected Gr. Intr. table. Do not replace it with the PN IV reprint or take the union. Disclose the selected authority for PN4 consumers. The count error in its comment is F14, not a reason to remove two correct Gr. Intr. entries. Intervals printed to 59′ should not create uncovered final arcseconds: ordinal nth degrees cover `[n−1,n)`.

### C03 — The five-degree house rule uses a disclosed longitude approximation

**Functions:** `get_effective_house` (4177–4211), downstream advancement/condition functions.

**Exact sources:** S-Aph #44.88–89, pp. 86–87, gives the angular carryover; fn. 56 says it is measured “in diurnal motion.” S-Nat 1.18.19, p. 295 ends “and likewise in all of the houses.” S-Nat 1.22.9 also speaks specifically of stakes. These support a real scope question (all cusps versus stakes), distinct from the coordinate-unit question.

**Reproduction of the unit discrepancy:** Set obliquity `23.4392911°`, latitude `60° N`, Ascendant `90°`, and set ARMC to `OA(90°)−90°`. Generate the Alcabitius cusps with `swe.houses_armc(..., b'B')`. At longitude **85.1°**, the zodiacal gap to the Ascendant is **4.9°**, so `get_effective_house` returns house 1. The gap in rising/diurnal rotation, `OA(90°)−OA(85.1°)`, is **5.0564664596°**. It lies outside a five-degree diurnal-motion band under that reading.

**Reproduction of the scope choice:** With equal illustrative cusps `0,30,...,330`, longitude **58°** returns house 2 with `angles_only=True` and house 3 with `angles_only=False`.

**Assessment:** The numerical approximation is certain and already admitted in the function's documentation. Choosing the editor's diurnal interpretation as operative makes this an implementation gap; literal zodiacal examples and the scope variation require explicit treatment. Do not equate quadrant membership, whole-sign place, and angular strength. Preserve strict house membership separately. The comment claiming the application lacks OA geometry is stale: it now has OA helpers, but a body-aware house-strength method still requires a carefully stated convention.

### C04 — Ray interpolation remains a reading choice, not just an inverse-trigonometry test

**Function:** `cast_rays_by_ascension` (5246–5282), with `_hours_from_stake` and inverse RA/OA helpers.

**Exact source:** AM-VII VII.7.14–19, pp. 486–487: construct two candidate rays, divide their difference by six, multiply by hours from the stake, and add to the nearer position for left rays. VII.7.20–21 subtracts the aspect arc for right rays, then says to add to the **more distant** position. VII.7.22 places opposition at the opposite sign in the same degree/minute.

**Reproduction:** `cast_rays_by_ascension(25, 80, 23.4392911, 36, anchor)`; inspect `Right sextile`.

| Quantity | Degrees / hours |
|---|---:|
| Candidate from right ascensions | 320.768775390° |
| Candidate from city ascensions | 298.156162772° |
| Distance from stake | 2.488532713 seasonal hours |
| `as written` / `distant` result | 307.534867143° |
| `nearest` result | 311.390071019° |

The two choices differ by **3.855203877°**. The independent coordinate tests do not adjudicate that historical choice. The implementation also interprets “add” as moving toward the other candidate along a signed circular arc and caps the interpolation at the candidate difference; those are operational interpretations, not words supplied verbatim by the passage.

**Assessment/action:** The inverse RA/OA mathematics checks out within its domain. Preserve the anchors as distinct readings and document signed circular interpolation and endpoint behavior. Do not relabel one as universally Ptolemaic merely because it passes round-trip tests. Validate examples at 0/360°, every stake, southern latitudes, and the admitted polar-domain boundary. Retain explicit refusal where the inverse OA is not uniquely applicable.

### C05 — The supplied hourly rate contains a dimensional contradiction

**Functions:** `pn4_arc_to_time`, `pn4_format_arc_time` (around 7648–7659), plus callers that convert directed arcs to calendar dates.

**Exact source:** PN4 III.1.13, p. 288, currently transcribed at line 6145: “every 10\" one day, and every 25\" one hour.” Footnote 17 identifies an idealized year of twelve 30-day months. The quoted two arc units cannot both be correct.

**Reproducible dimensional test:**

- `pn4_arc_to_time(10/3600)` → **1 day**.
- `pn4_arc_to_time(25/3600)` → **2 days 12 hours**, not 1 hour.
- `pn4_arc_to_time(25/216000)` → **1 hour**: 25 thirds of arc = 25/60 arcsecond = 10″/24.

**Assessment:** The text's dimensions are definitely inconsistent. The likely correction is **25‴**, and a prior supplied audit claims photographic confirmation, but that prior assertion is not an independently rechecked photograph in this review. Verify the original page before changing the transcription. The engine's 360-day arithmetic is internally correct on this test; do **not** alter it to make 25 arcseconds equal an hour.

Separately, a **365.2425-day** mapping for dated directions is a modern implementation choice calibrated in the project to PN IV's Figure 22. The ancient idealized months do not by themselves establish that mapping. Keep symbolic years/months and elapsed civil days labeled and testable, particularly when repairing F02. A modern calendar mapping and the source's 360-day fractional notation are not interchangeable units.

## What the audit positively verified

These are bounded results, not a blanket certificate for the entire engine.

| Area | Independent/source-grounded check | Result |
|---|---|---|
| Egyptian bounds | AM-Full V.9, p. 287, Fig. 47: parsed all 60 width/lord cells and compared cumulative endpoints; 180 interior/edge probes | All matched; every sign totals 30° |
| Chaldean faces | AM-Full V.15, pp. 295–296, Fig. 54: all 36 rulers | All matched |
| Brightness bands | AM-Full V.20, pp. 305–306, Fig. 61: expanded printed counts independently | All 360 ordinal-degree categories matched |
| Wells | AM-Full V.21, p. 308, Fig. 62, all entries | All 64 matched; different PN IV witness retained in C02 |
| Planetary years | AM-Full/AM-VII VII.8, p. 487, Fig. 146: 7 planets × 5 values | All 35 cells matched; explicit Head/Tail periods are 3/2 years |
| Twelfth-parts | AM-Full V.18.1–3 formula; Taurus 5°15′ with −360° and +720° equivalent inputs | All yielded Cancer 3° |
| RA/declination | Independent Cartesian rotation at 720 longitudes × 3 obliquities | Maximum differences: RA `5.69e−14°`, declination `7.11e−15°` |
| Oblique ascension | Independent horizon/rising equation at 10,800 cases, latitudes −60°, −36°, 0°, +36°, +60° | Maximum difference `1.14e−13°` |
| Ascensional domain | Existing targeted tests cover inverse round trips and polar refusal | Passed; these test implemented geometry, not ray-source interpretation |
| Existing selected suite | Eight modules listed below, including doctrine/source fixtures | **451 passed**, no skips |

The existing test modules executed were `test_base_tables.py`, `test_spherical_math.py`, `test_differential_oracle.py`, `test_doctrine_fixtures.py`, `test_decisions_2026_09_08.py`, `test_abu_mashar_citations.py`, `test_sahl_citations.py`, and `test_nativities_citations.py`. Source tests were run with `CORPUS_DIR` set. This is **not** a claim that the whole UI/switch-matrix suite passed. The differential fixture in this archive contains 748 cases with seven fields, or 5,236 field comparisons; that should not be conflated with a differently sized earlier audit run. Agreement with an existing fixture is regression evidence, not independent historical authority.

### Units, coordinates, epochs, and normalization assessment

- The core uses longitude/latitude in **degrees**, angular speed in **degrees/day**, distance in **AU**, and Swiss `calc_ut` with UT input. Geographic longitude is east-positive. The ecliptic-to-equatorial rotation sign and the RA/OA sign convention were checked independently; no radians/degrees conversion defect was found in those tested helpers. The relevant external API reference is [Swiss Ephemeris programmer documentation, §§3, 9, 14, 18.6](https://www.astro.com/swisseph/swephprg.htm).
- The tested direction geometry concerns the **ecliptic degree** (zero ecliptic latitude). That can be appropriate for the cited degree-based construction; it must not be reused as the actual planet's horizon position. F04 is precisely that distinction.
- The application uses modern tropical ephemeris calculations; it does not reconstruct the cited Persian/Indian zījes. Apparent versus geometric positions, UT versus dynamical time, date-of-equinox versus a fixed epoch, and ephemeris fallback are conventions to record. No independent historical zīj, JPL, fixed-star/precession, or extreme-epoch accuracy certification was performed. Do not claim that agreement with the implemented Swiss library proves agreement with every ancient numerical example.
- Whole-sign houses and quadrant houses are separate computed quantities. Their different answers are not, by themselves, a defect. The rule selecting which to use must come from the relevant passage; C03 isolates an actual unit discrepancy in the strength/carryover layer.
- Canonical longitude normalization works in `get_essential_rulers` and `pn4_twelfth_part`. The lower-level `_pairwise_configurations` is not generally periodic for arbitrary unnormalized inputs: Moon −350° or 730° with Saturn 70° raises `KeyError`, while Moon 10° works. This is a **contract/robustness limitation**, not a demonstrated normal-chart failure, since Swiss supplies canonical longitudes. At an exposed boundary, normalize or reject such inputs explicitly; do not silently assume external callers use the Swiss contract.
- Formatting/truncation, physical event tolerances, ordinal degree membership, and floating endpoint ownership are different problems. F06, F09, F10, F12, and F13 give separate tests. Fixing one global epsilon is not a sound substitute for specifying each boundary.
- Searches over a finite horizon cannot establish that an event never happens. Preserve horizon-limited language. F07 additionally shows that sampling may miss an event *inside* the declared horizon.

## Reproduction appendix

The following script is audit code only. Save it outside the engine, e.g. as `audit_reproductions.py`, install the application's requirements in a disposable environment, and run:

```bash
python audit_reproductions.py /absolute/path/to/extracted/Archive
```

It loads the computation portion of `Executable/app.py` without changing it. `FAIL` means the current engine does not satisfy the cited expectation; the script continues so all cases can be inspected. Several IDs have more than one check. The metadata and interpretation checks have their exact calls/source locations in F14 and C01–C05 rather than brittle assertions about comment wording.
```python
from pathlib import Path
from datetime import datetime, date, timedelta
from unittest.mock import patch
import os, sys, math, tempfile

os.environ['ALMUTEN_NO_PREFERENCES'] = '1'
os.environ['XDG_DATA_HOME'] = tempfile.mkdtemp(prefix='astrology-audit-')
import swisseph as swe

base = Path(sys.argv[1]).resolve()
app = base / 'Executable/app.py'
source = app.read_text()
e = {'__name__': 'audit_engine', '__file__': str(app)}
exec(compile(source.split('# 4. STREAMLIT UI INTEGRATION')[0], str(app), 'exec'), e)
failed = 0

def check(name, ok, detail):
    global failed
    failed += not ok
    print(('PASS ' if ok else 'FAIL ') + name + ': ' + str(detail))

def P(lon, speed=1.0, lat=0.0):
    return dict(longitude=float(lon), latitude=float(lat), distance=1.0,
                speed_in_lon=float(speed), speed_in_lat=0.0, speed_in_dist=0.0)

def fixture(**overrides):
    p = {n:P(l,v) for n,l,v in [
        ('Sun',280,1), ('Moon',160,13), ('Mercury',270,1.2),
        ('Venus',300,1.1), ('Mars',210,.5), ('Jupiter',90,.08),
        ('Saturn',330,.03), ('North Node',200,-.05)]}
    p.update(overrides)
    return p

# F01. These deliberately reproduce the current input adapter.
check('F01 Julian validation', e['parse_iso_date']('1300-02-29') is not None,
      e['parse_iso_date']('1300-02-29'))
j = swe.julday(1300,2,29,12,swe.JUL_CAL)
try:
    got = e['pn4_datetime_from_jd'](j)
    check('F01 Julian reverse conversion', (got.year,got.month,got.day)==(1300,2,29), got)
except ValueError as exc:
    check('F01 Julian reverse conversion', False, repr(exc))
local = datetime(1300,3,1,0,30)
current_adapter_ut = local - timedelta(hours=2)
actual = e['calculate_traditional_chart'](current_adapter_ut,0,30)['julian_day']
expected = swe.julday(1300,3,1,0.5,swe.JUL_CAL)-2/24
check('F01 current offset adapter', abs(actual-expected)<1e-8, (actual,expected))

# F02/F03/F11. Target dates use the application's documented noon convention.
c = e['calculate_traditional_chart'](datetime(2000,1,1,12),0,0)
b = e['pn4_timing_bundle'](c,0,0,date(2000,1,1),date(2001,7,1),'forward')
check('F02 fardar', b['fardar']['sub_lord']=='Venus', b['fardar'])
b = e['pn4_timing_bundle'](c,0,0,date(2000,1,1),date(2012,10,21),'forward')
check('F02 distribution', b['current']['distributor']=='Saturn', b['current'])
c3 = e['calculate_traditional_chart'](datetime(2000,1,1,23),43.7792,11.2463)
b3 = e['pn4_timing_bundle'](c3,43.7792,11.2463,date(2000,1,1),date(2003,1,1),'forward')
check('F03 containing return', b3['jd_sr']<=2452641.0 and b3['month']==12,
      (b3['jd_sr'],b3['month'],b3['day_of_year']))
b1 = e['pn4_timing_bundle'](c,0,0,date(2000,1,1),date(2001,1,1),'forward')
# Use age 1 to isolate the presentation defect from the fractional-age defect.
oa = e['_oblique_ascension'](c['ascendant'],c['obliquity'],0)
endpoint = e['_lon_with_oblique_ascension'](oa+1,c['obliquity'],0)
check('F11 active degree', b1['year_rows'][1]['Active point']==e['get_degree_string'](endpoint),
      (b1['year_rows'][1]['Active point'],endpoint))

# F04. Independent Cartesian rotation and zenith dot product.
c4 = e['calculate_traditional_chart'](datetime(2000,1,1,1,40),51.5,0)
p = c4['planetary_data']; jup = p['Jupiter']
lam, beta, eps, theta, phi = map(math.radians,
    [jup['longitude'],jup['latitude'],c4['obliquity'],c4['armc'],51.5])
x = math.cos(beta)*math.cos(lam)
y = math.cos(beta)*math.sin(lam)*math.cos(eps)-math.sin(beta)*math.sin(eps)
z = math.cos(beta)*math.sin(lam)*math.sin(eps)+math.sin(beta)*math.cos(eps)
sinalt = math.sin(phi)*z+math.cos(phi)*(math.cos(theta)*x+math.sin(theta)*y)
acc = e['evaluate_accidental_dignities'](p,c4['houses'],c4['sect'])
assert sinalt<0 and c4['sect']=='Nocturnal' and 0<jup['longitude']<30
check('F04 Jupiter hayz', acc['Jupiter']['Hayz'] is True,
      {'Hayz':acc['Jupiter']['Hayz'],'altitude':math.degrees(math.asin(sinalt))})

# F05/F06. Patch only the external ephemeris within this isolated process.
def linear_ephemeris(p):
    ids = {e['PLANET_SWE_IDS'][n]:v for n,v in p.items()}
    def calc(t, who, *args):
        v = ids[who]
        return ((v['longitude']+t*v['speed_in_lon'])%360,0,1,
                v['speed_in_lon'],0,0),260
    return calc

p = {'Moon':P(1,13),'Mars':P(29,.5),'Saturn':P(40,.03)}
with patch.object(swe,'calc_ut',linear_ephemeris(p)):
    sim = e['_simulate_forward_uncached'](p,0,horizon_days=6,step_days=.1)
    rows = e['evaluate_escape'](p,sim)
    bad = [r for r in rows if r['Planet']=='Moon' and r['Escaped']=='Mars'
           and r['Connected Instead With']=='Saturn']
    check('F05 synthetic escape', not bad, bad)

p = {'Moon':P(29.636,13),'Sun':P(89.948,1)}
with patch.object(swe,'calc_ut',linear_ephemeris(p)):
    sim = e['_simulate_forward_uncached'](p,0,horizon_days=1,step_days=.25)
    exit_day = sim['events']['Moon']['sign_exits'][0]
    contact = e['_perfection_day'](sim,'Moon','Sun',60,before_day=exit_day)
    check('F06 contact before exit', contact is not None, (exit_day,contact))

# F05, real ephemeris corroboration. No location is needed for conjunction order.
p = {}
for name in ['Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn']:
    xx, _ = swe.calc_ut(2451587.0,e['PLANET_SWE_IDS'][name])
    p[name] = dict(zip(['longitude','latitude','distance','speed_in_lon',
                        'speed_in_lat','speed_in_dist'],xx))
sim = e['_simulate_forward_uncached'](p,2451587.0,horizon_days=100,step_days=1)
bad = [r for r in e['evaluate_escape'](p,sim) if r['Planet']=='Mars'
       and r['Escaped']=='Jupiter' and r['Connected Instead With']=='Moon']
check('F05 real escape', not bad,
      (bad,e['_body_union_day'](sim,'Mars','Jupiter'),e['_body_union_day'](sim,'Mars','Moon',after_day=39.6)))

# F07. Both longitude and reported speed describe the same quadratic.
def retro_ephemeris(t, who, *args):
    return (29.99+.12*t-.12*t*t,0,1,.12-.24*t,0,0),260
with patch.object(swe,'calc_ut',retro_ephemeris):
    sim = e['_simulate_forward_uncached']({'Mercury':P(29.99,.12)},0,
                                          horizon_days=1,step_days=1)
    crossings = sim['events']['Mercury']['sign_exits']
    check('F07 two sign crossings', len(crossings)==2, sim['events']['Mercury'])

# F08. Check the departing-receiver branch under the current Sahl policy.
for tag,p,expected_word in [
    ('missing',fixture(Moon=P(190.5,13),Venus=P(190,1)),'venus'),
    ('reversed',fixture(Moon=P(95.5,13),Saturn=P(95,.03),Jupiter=P(120,.08)),'saturn')]:
    ess = e['evaluate_essential_dignities'](p,'Diurnal')
    acc = e['evaluate_accidental_dignities'](p,tuple(range(0,360,30)),'Diurnal')
    rows = e['evaluate_weakness_of_planets'](p,ess,acc,0,'Diurnal')
    labels = next(r['Labels'] for r in rows if r['Planet']=='Moon')
    hit = any(x.startswith('Separating from') and expected_word in x.lower() for x in labels)
    check('F08 '+tag, hit if tag=='missing' else not hit, labels)

# F09. Eighteen arcseconds post-exact, avoiding the exact-one-minute float.
r = e['_pairwise_configurations']({'Moon':P(10.005,13),'Saturn':P(10,.03)})[0]
check('F09 separated', not e['_is_connected_abu_mashar'](r),
      (r['motion'],e['_is_connected_abu_mashar'](r)))

# F10. Opening eastern thresholds. Western controls must stay inclusive.
for name,lon,want in [('Saturn',94,'Under the rays'),('Saturn',85,None),
                      ('Mars',90,'Under the rays'),('Mars',82,None),
                      ('Mercury',93,'Under the rays'),('Mercury',88,None)]:
    got = e['solar_phase'](name,lon,100)[0]
    check('F10 '+name+' '+str(lon), got==want, (got,want))
check('western control', e['solar_phase']('Saturn',106,100)[0]=='Burned',
      e['solar_phase']('Saturn',106,100))

# F12/F13. Exact advertised endpoint and an entered sexagesimal minute.
r = e['pn4_fardar_at_age'](4.0,'Diurnal')
r2 = e['pn4_fardar_at_age'](r['sub_to'],'Diurnal')
check('F12 subperiod endpoint', r2['sub_lord']=='Moon', r2)
check('F13 minute round trip', e['get_degree_string'](30+1/60)=="00° Tau 01'",
      e['get_degree_string'](30+1/60))

# Selected non-defect/source-policy controls.
check('twelfth-part source formula', e['pn4_twelfth_part'](35.25)==93,
      e['pn4_twelfth_part'](35.25))
check('source wells count', sum(map(len,e['WELLED_DEGREES'].values()))==64,
      sum(map(len,e['WELLED_DEGREES'].values())))
check('25 thirds equal one symbolic hour',
      e['pn4_arc_to_time'](25/216000)['hours']==1,
      e['pn4_arc_to_time'](25/216000))
print('Failing expectation count:',failed)
```

Observed on the reviewed version: **23 failed expectations and four passing controls**. Repeated IDs are separate witnesses of the same defect, not 23 distinct findings. The script exits normally after printing them; an absent exception is not a clean bill of health. F14 is established by comparing the cited comments with the available passages and by the numeric controls.

When refactoring, adapt the harness to the new input interfaces while preserving the source-derived expected outcomes. In particular, the F01 offset case deliberately reproduces the old UI adapter; route it through the repaired calendar adapter in the permanent regression test. A deliberate rename to “segment start” is an alternative reporting resolution for F11.

## Completion criteria for the implementation pass

- Julian-only leap dates survive validation, offsets, chart calculation, and round-trip display under one calendar policy.
- Current timed states agree with the dates printed for them; the target is bracketed by the correct annual and monthly returns.
- Actual planetary altitude drives hemisphere-dependent conditions throughout the application.
- Escape and other ordered phenomena reject later substitutes after successful original contact. Event searches resolve close ordering and stationary excursions.
- Source-specific separating and solar-phase boundaries are tested on both sides of exactness, including relevant retrograde cases.
- Fardār endpoint ownership and sexagesimal display have explicit, consistent numerical policies.
- Each differing tradition/approximation in C01–C05 remains traceable to its witness; passing tables are not overwritten to resolve a different volume's reading.
- Re-run the affected tests and the existing relevant suite on the project's pinned runtime. Record any source-policy changes separately from definite bug fixes.
