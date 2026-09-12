# Base lookup tables audited against their authorities — 2026-09-08

Read-only pass, per the brief: every base lookup constant in the engine half of `app.py`, its
authority, a mechanical cell-by-cell diff, and a pin where the table is right. **No value was
changed.** Pins for the tables that match are committed with this report
(`tests/test_base_tables.py`, 83 tests). Baseline `main` @ `7ef73df`, 892 passed / 2 xfailed,
re-run before anything was touched.

Method: the engine half is executed as a module; each table is compared to a literal transcribed
from the named authority (corpus first, then *TNAC Handy Tables from Part 1*, then a stated
convention), never from the code's own comment. Two tables are prose (delineation strings) and were
compared by token overlap against the *TNAC Reference Guide for the Planets and Places* and then
read row by row where the overlap flagged anything.

## 1. Tables that match — and are now pinned

| Table (`app.py`) | Authority | Diff | Pin |
|---|---|---|---|
| `DOMICILES` `EXALTATIONS` `DETRIMENTS` `FALLS` | Handy p. 1 wheel; detriment/fall derived as the opposite sign | 7×4 identical | `test_domicile_exaltation_detriment_fall_match_handy_p1[×7]` |
| exaltation **degrees** (only two are used: the sect light's, in `_lot_point` for the Lot of Exaltation) | Handy p. 1 "Standard exaltations": Sun 19♈, Moon 3♉; corpus witnesses VII.6, 40 *"19° Libra up to 3° Scorpio, because those are the fall of the luminaries"*, Questions Ch. 1, 42 *"3° of Scorpio (which is her fall)"* | identical (the Hermes column would give 18/2) | `test_the_engine_uses_the_standard_exaltation_degrees…` |
| `TRIPLICITY` | **corpus**: Sahl *Introduction* Ch. 1, 35–41 and Figure 4; Handy p. 1 agrees | 4×3 identical | `test_triplicity_lords_match_sahl_figure_4[×4]` |
| `SIGN_ELEMENT` | *Introduction* Ch. 1, 14–17 | identical | `test_sign_elements…` |
| faces from `CHALDEAN_ORDER` (algorithm) | **convention** — the Chaldean faces from Aries 0 (Mars, Sun, Venus…). *No face table in corpus or course*: the glossary defines a face as 10° (p. 779) without lords; the Handy Tables have none | all 36 lords as the standard sequence | `test_face_lords_follow_the_chaldean_order_from_aries[×36]` |
| `BRIGHTNESS_DEGREES` | **corpus**: Abū Ma'shar Figure 61 (V.20), `abu_mashar_book_vii.md:2181`, itself verified cell by cell against the p. 306 photograph in the OCR pass | all 12 rows identical; every code width (e.g. "3K") equals its range | `test_brightness_degrees_match_figure_61_sign_by_sign[×12]` |
| `JOY_HOUSES` | *Introduction* Ch. 3, 128 | identical | `test_joys_match_introduction_ch3_128` |
| `MASCULINE_SIGNS` `FEMININE_SIGNS` | *Introduction* Ch. 1, 2–3 | identical | `test_sign_genders_alternate_from_aries…` |
| `FIXED_SIGNS` | *Introduction* Ch. 1, 9 | identical | `test_fixed_signs…` |
| `EXCELLENT_PLACES` {1,4,5,7,10,11} | *Introduction* Ch. 3, 78 + fn. 92 (*"allows only six good places"*) | identical | `test_excellent_places…` |
| `MALEFIC_HOUSES` {6,8,12} | *Introduction* Ch. 2, 46–47 | identical | `test_malefic_houses…` |
| `PREFERRED_DOMICILE` | *Introduction* Ch. 3, 129 | identical | `test_preferred_domiciles…` |
| `DIURNAL/NOCTURNAL_SECT_PLANETS` | glossary *Sect*; Handy Lesson 10 | identical | `test_sect_of_the_planets` |
| `PLANETARY_ORBS` | **corpus**: *Introduction* Ch. 3, 13–17; Handy p. 28 "Bodies or orbs" | identical | `test_planetary_orbs…` |
| `WEIGHT_ORDER` (= `CHALDEAN_HOUR_ORDER`) | Chaldean order, heaviest first (convention; Handy p. 35 hours presuppose it) | identical | `test_weight_order…` |
| `AVERAGE_DAILY_MOTION` | Handy p. 2 "Average daily speeds" | all within 1.5″/day (Saturn +0.0004°, Moon −0.0003°) | `test_average_daily_motion…[×7]` (2″ tolerance) |
| `DAY_LORD_BY_WEEKDAY` | Handy p. 35, hour 1 of each day | identical | `test_day_lords…` |
| planetary hours (algorithm) | Handy p. 35 | all **168** cells reproduced | `test_planetary_hours_cycle…` |
| `SOLAR_BURNED_ORB` `SOLAR_RAYS_ORB` `SOLAR_SETTING_DEGREES` `CAZIMI_ORB` | **corpus**: VII.2, 7, 11, 13, 30–31, 37, 40, 44, 48, 51, 60–61, 72–74 | identical | `test_solar_orbs_match_great_introduction_vii_2` |
| `HARSH_BURNED_PATH` | VII.6, 40 | identical | same test |
| `EQUAL_ASCENSION_PAIRS` (56), `EQUAL_DAYLIGHT_PAIRS` (68–73), `NATURAL_OPPOSITION_PAIRS` (76), `NATURAL_SEXTILE_PAIRS` (77) | **corpus**: VII.5 | all four identical | `test_natural_connection_pairs_match_vii_5` |
| `MASHAALLAH_LORDS`, `PLANETS_IN_HOUSES` (shape only) | — | 12×12 and 12×7×2 complete | `test_prose_tables_have_full_shape` |

**What these pins would have caught:** the bounds transposition had an exact analogue possible in
every one of these — two adjacent lords swapped in a triplicity row, a face sequence started one
planet off, a brightness span shifted, a day lord off by one weekday. Each now fails on the cell.

Skipped, as the brief asked, and said so: `VICTOR_WEIGHTS` and `VICTOR_PLACES_VALUES` (verified
2026-09-06 against Handy pp. 33–34). Also not re-diffed: `MASCULINE_QUADRANT_HOUSES` (verified
2026-09-06 against Figure 90); `ESSENTIAL_DIGNITY_WEIGHTS` is the newer victor weighting by
construction.

## 2. Mismatches — nothing numeric; two prose tables carry cell defects

### 2a. `PLANETS_IN_HOUSES` — authority: *TNAC Reference Guide*, "Planets in the Nth" (Rhetorius Ch. 57 / PN4 II columns)

Nine of the twelve houses match the Guide row for row (1, 2, 4, 5, 7, 9, 10, 11, 12). Defects:

| Cell | Code | Guide | Defect |
|---|---|---|---|
| 3rd, Sun, Good | *"Good for marriage/religion; travel with good status"* | Sun Good: *"Bad death for father; serious in counsel, responsible for management of public things, religious honors"* / PN4 *"Travel due to Sultan…"* | **cell is Venus's row** (*"Good for marriage and being religious, especially with Jupiter"* / *"Travel, with good and status…"*) |
| 3rd, Mars, Bad | *"Bad death for father, evil reports, difficult travels"* | Mars Bad: *"Worse than by night?"* / *"Evil reports…difficult travels…"* | *"Bad death for father"* is the **Sun's** Good line, bled down |
| 6th, Moon, Good/Bad | *"Health and bodily stability"* / *"Fluctuating health, bodily weakness"* | **"?" / "?"** | **unsourced text where the Guide has none** |
| 8th, Moon, Good/Bad | *"Sudden inheritance, finding money"* / *"Passive and sick"* | **"?" / "?"** | **Mercury's** *"(Evening by night): sudden inheritance, finding money, fortunate; passive and sick"* attributed to the Moon |
| 8th, Sun, Bad | *"Wealthy, benefit from death of women; negligence"* | Sun Bad: *"See above"* / *"Leisure but without benefit, poor way of life, negligence or laziness"* | *"Wealthy, benefit from death of women"* is **Venus's Good** |
| 8th, Venus, Good | *"Marry late; benefit from underclass/commerce"* | Venus Good: *"Wealthy, benefit from death of women, easy death"* / *"Benefit from underclass or base work; much spending"* | *"Marry late"* is **Venus's Bad**; *"commerce"* is **Mercury's** PN4 |

The Guide also prints "?" for the Moon's PN4 column in the 2nd and 10th; the code's cells there carry
only the Rhetorius text, which is correct.

**What would move if corrected:** displayed delineation strings only — the "Topical Planets in
Houses" table and the Rhetorius/PN4 expander on the Dignities page. No number, no score, no fixture
identity (`tables.json` pins headings and columns), no chart in the fixture set changes anything
but text. This is a ⟨CHOICE⟩ only in one respect: the 6th/8th Moon cells have no Guide text at all,
so "correct" there means either blank/"?" or a sourced sentence from Rhetorius Ch. 57 / PN4 II
directly, which are outside the corpus.

### 2b. `MASHAALLAH_LORDS` — authority: *Reference Guide*, "The lords of other places in the Nth (Masha'allah)", which cites Sahl *Nativities* 1.36, 2.14, 3.10, 4.11, 5.1, 6.3.4, 7.1, 8.5, 9.4, 10.2.4, 11.1, 12.1

143 of 144 cells overlap their Guide row (the two flagged by the heuristic — (6, lord of 2nd) and
(8, lord of 5th) — were read: the first is a fair paraphrase). The one defect is not a
transposition: cell (8, lord of 5th) reads *"[UNCERTAIN — the source reads '[illegible] they will
survive and will be miscarried' … do not rely on this cell]"* (the SOL56 audit's C-something fix),
while the **Guide reads it as "Children premature or miscarried."** The course guide resolves what
the OCR could not. What would move: one displayed string.

## 3. Tables with no authority in corpus or course — the list the brief asked for

| Table | What it feeds | Finding |
|---|---|---|
| **`WELLED_DEGREES`** (`app.py:4307`) | "Welled Degree" in Special Degrees; `in_well` in **Favor & Recompense** (the new 1240‑01‑04 fixture row exists because Capricorn 22 is in this list) | Cited in the code to *"Abū Ma'shar V.21 (Dykes), Fig. 98"*. **In this corpus Figure 98 is "Speed relative to apogee"** (`abu_mashar_book_vii.md:76`) and V.21 is not present — fn. 203 only points to it (*"For the wells, see Ch. V.21"*). The glossary defines welled degrees (p. 797) without a table; the Handy Tables and Reference Guide have none. **Unverifiable here, and the citation is wrong as written.** This is the exact condition that let the bounds error live. Highest priority to source: photograph *Great Introduction* V.21's table (the book is the one the aspects/conditions captures came from). **Resolved 2026-09-08:** V.21 was photographed and is in the corpus (Abū Ma'shar pp. 303–310, Figures 59–64). The table is **Figure 62** (`abu_mashar_book_vii.md`, p. 308 of Abū Ma'shar's volume); the chapter citation was right and only the figure number was wrong. Nine signs matched; Aries lacked 29, Gemini had 13 for 12, Pisces lacked 28 — corrected in `app.py` and pinned cell by cell in `tests/test_base_tables.py` (`WELLS_FIG62`, plus a corpus re-derivation test). |
| faces (`CHALDEAN_ORDER` algorithm) | face lord everywhere | Convention only; pinned as the standard sequence so it cannot drift, but no corpus or course table confirms it. |
| `PLANET_GENDER` (`:4748`) | Strength testimony 87 | Reference Guide genders: Saturn *"Masculine (but sometimes viewed as neutral or feminine)"*, **Mercury *"Masculine, but perhaps varies"*** — the code leaves Mercury `None` ("left unassigned rather than guessed"). Documented divergence, not an error; the owner's call whether the Guide's "masculine" should apply. |
| `GEOCENTRIC_DISTANCE_RANGE` (`:4489`) | apogee proxy (VII.6, 23) | Modern proxy, already labelled as such in the code. |
| `STATION_SPEED_TOLERANCE` 0.003 | stations | App's own figure; the code says so. |
| `WELLED_DEGREES`-adjacent: the "Via Combusta 15♎–15♏" band | Special Degrees | Labelled "external convention" in the code; the corpus has Sahl's narrow band and VII.6, 40's — both already implemented separately. |

## 4. Where corpus and course disagree — ⟨CHOICE⟩, not picked

- **Exaltation degrees**: Handy p. 1 gives a *Standard* and a *Hermes* column (Sun 19/18, Moon 3/2,
  Saturn 21/20, Mars 28/27, Venus 27/26; Jupiter and Mercury 15/15). The engine uses Standard, and the
  corpus witnesses (VII.6, 40; Questions 1, 42) side with Standard. No action.
- **Places**: `EXCELLENT_PLACES` is Ch. 3, 78's six; *Introduction* Ch. 2 gives an 8-place (presence)
  and a 7-place (goodness) scheme, the latter including the 9th. Different questions, already recorded
  in `03_changes.md` C‑09. No action here.
- Nothing else disagreed.

## 5. Could not verify

- ~~`WELLED_DEGREES` (above).~~ Pinned 2026-09-08 against Figure 62 (V.21).
- The Reference Guide's own transcription of Rhetorius/PN4 — it is the course's table, taken as
  authority; PN4 is not in the corpus.
- Handy p. 32 (joys mapped onto exaltations) is an image; the joys were pinned to the corpus instead.
