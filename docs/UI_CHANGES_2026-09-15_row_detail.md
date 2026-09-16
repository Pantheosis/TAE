# UI changes 2026-09-15 — "why this fired": row detail on Strength & Weakness

Branch `row-detail-2026-09-15` off `main` at `5c5f55d`. Item 12 of
`UI_FRAMEWORK_REVIEW_2026-09-15_SECOND_OPINION.md` (brief #5), scoped as that
item says: Strength & Weakness first and alone.

## What was asked

Every rule the app applies names its sentence. The two tick grids on the
Configurations page (Strength & Weakness tab; Sahl, The Introduction Ch. 3,
78–88 and 91–100) show a tick per planet per testimony and, in the Answer key
expander, the testimonies in words. What they did not show is **why** a tick
fired — which of the chart's own facts satisfied the sentence. Select a
planet's row and see, for each ticked testimony, the sentence and the facts
that met it.

Three constraints: every existing output of the two evaluators stays
byte-identical; the panel invents no doctrine; a selection reruns the grid's
block and not the page.

## The canon rule, and how it was kept

The panel restates the evaluator's own reasoning for a tick — the sentence it
already cites and the chart values it already tested — and adds no rule, no
reading and no wording of doctrine that is not in the code's labels, its
docstrings and the Answer key. Concretely:

- the **sentence** shown for a testimony is the label string itself, verbatim,
  as the Answer key prints it (including its trailing paragraph number);
- every **fact** is a value the evaluator holds in a local name at the point
  it decides that testimony — nothing is recomputed on the page, and nothing
  is looked up that the branch did not already read;
- where the evaluator computes a value it does not name, the fact names it as
  the code does (`speed_in_lon`, `triplicity_day`, `EXCELLENT_PLACES`), not
  as the text does.

Nothing was left un-itemised: every one of the twenty-one testimonies carries
at least one fact from the branch that decides it, so no testimony had to be
shown with a bare label.

## A. The engine

Two functions changed, one added, none removed (AST diff of every top-level
function against `origin/main`): `evaluate_strength_of_planets`,
`evaluate_weakness_of_planets`; added `_fact(name, value)`, the formatter that
writes one `"Fact: Value"` string (booleans yes/no, degrees to two places, a
set of signs in zodiac order, a set of numbers ascending, `None` or an empty
collection as `none`).

Inside each evaluator, beside `labels = []`, a `testimonies = []` and a
three-line closure `_add(n, label, *facts)` that appends the label to `labels`
exactly as `labels.append(label)` did and a dict `{"n", "sentence", "facts"}`
to `testimonies`. Each `labels.append(...)` became an `_add(...)` with the
same label text and the facts named below. The row gains one key at the end,
`Testimonies`; `Planet`, `Strength Testimonies` / `Weakness Testimonies`,
`Count` and `Labels` are untouched, in the same order.

Three loops gained a collecting list so the facts could be read off values
the loop already computes: 82 records each connected partner with the
whole-sign place and sign it already looks up; 94 records the aspect name of
each hit beside the partner it already records; 97 keeps the last `my_rulers`
it computed. 81's configuration facts read the aspect name of the pair rows
the `any(...)` already iterates.

### The facts, by testimony

The paragraph number, the value the code tests, and the fact string(s).

| n | the value the code tests | fact string(s) |
|---|---|---|
| 78 | `house` (whole-sign) in `EXCELLENT_PLACES` | `Whole-sign place: 10` · `Excellent places: 1, 4, 5, 7, 10, 11` |
| 79 | `ess['Domicile'/'Exalt'/'Triplicity'/'Term'/'Face']`, `acc['Joy']` | `Share of dignity: Term` (the keys that are true, in the branch's own order) |
| 80 | `acc['Retrograde']` false; `data['speed_in_lon']` in hand | `Retrograde (accidental): no` · `Speed in longitude: 0.96` |
| 81 | no row with the other member in `effective_infortunes()` by Conjunction/Square/Opposition | `Infortunes: Mars, Saturn` · `Configuration with Mars: Aversion` · `Configuration with Saturn: Aversion` |
| 82 | every connected partner's `other_house`/`other_sign`; `ess['Fall']` | `Connected with: Moon, Venus, Jupiter` · `Moon: whole-sign place 9, Gemini` (one per partner) · `Fall (essential): no` |
| 83 | `quadrant_house` in `ANGLE_HOUSES \| SUCCEDENT_HOUSES`; `quadrant_house_strict` | `Quadrant division: 8` · `Angular and succedent divisions: 1, 2, 4, 5, 7, 8, 10, 11` · (five-degree case) `Quadrant division, strict: 9` |
| 84 | `signed_from_sun`, `visible_floor` | `Signed distance from the Sun (negative is eastern): -48.29` · `Visible floor: 6.00` |
| 85 | `planet_is_diurnal == (sect == 'Diurnal')` | `Planet is diurnal: yes` · `Sect: Diurnal` |
| 86 | `sign in FIXED_SIGNS` | `Sign: Taurus` · `Fixed signs: Taurus, Leo, Scorpio, Aquarius` |
| 87 | the one-degree distance from the Sun | `Distance from the Sun: 0.53` · `Window: 1.00` |
| 88 | `gender`, `quadrant_house`, `sign` against the masculine/feminine sets | `Gender: Masculine` · `Quadrant division: 8` · `Quadrant gender: Feminine` · `Sign: Gemini` · `Sign gender: Masculine` |
| 91 | `house in CADENT_HOUSES` and `_averse_to_ascendant(...)` | `Whole-sign place: 6` · `Cadent places: 3, 6, 9, 12` · `Averse to the Ascendant: yes` |
| 92 | `acc['Retrograde']` true; `data['speed_in_lon']` | `Retrograde (accidental): yes` · `Speed in longitude: -0.12` |
| 93 (and 99's western clause) | `acc['Combust']`, `acc['UnderBeams']`, `signed_from_sun` | `Combust (accidental): yes` · `Under the beams (accidental): no` · `Signed distance from the Sun (positive is western): 5.53` |
| 94 | each hit's `other` and `r['aspect_name']` | `Connecting with Saturn: Square` (one per hit) |
| 95 | `sep`, `con` from `_sahl_enclosed` | `Separating from: Mars` · `Connecting to: Saturn` |
| 96 | `ess['Fall']` | `Fall (essential): yes` |
| 97 | `_averse97`; `_sep97` with `my_rulers['domicile'/'exaltation']` | `Connecting with, averse to the Ascendant: Mars` · `Separating from: Venus` · `Domicile lord of its degree: …` · `Exaltation lord of its degree: …` |
| 98 | `alien_rulers['domicile'/'exaltation'/triplicity_key_local]` | `Domicile lord where it sits: Mercury` · `Exaltation lord where it sits: -` · `Triplicity lord where it sits (triplicity_day): Saturn` |
| 99 | `node_dist`, `lat` | `Distance from the nearer node: 1.25` · `Latitude: 0.14` |
| 100 | `ess['Detriment']` | `Detriment (essential): yes` |

Two readings of the table worth stating. 98's exaltation lord prints `-`
where the sign has none, because that is what `get_essential_rulers` returns
and the fact names the value as the code holds it. 84's and 93's signed
distances keep the code's sign convention in the fact's name (negative
eastern for 84, positive western for 93) rather than translating it into a
word the branch does not compute.

## B. The page

`_tick_grid` renders its grid with `on_select="rerun"`,
`selection_mode="single-row"` and `key=<title, lower-cased and underscored,
+ "_grid">` — `strength_of_the_planets_grid`, `weakness_of_the_planets_grid`.
The grid's DataFrame and `column_config` are exactly what they were. When a
row is selected, `_row_detail(row, total, locator)` draws under the grid, before
the Answer key expander: a subheader `Sun: 7 of 11 testimonies` (the weakness
grid likewise, of 10), then per ticked testimony in numerical order a caption
`Sahl, The Introduction Ch. 3, 78` (the locator read off the grid's own
citation, the same string the column tooltips use), the sentence, and the
facts as a `Fact` / `Value` table — or one caption line when there is one
fact. The page splits each fact at its first `": "`; the engine's fact names
never contain one. With no selection nothing is drawn.

In `sahl_strength()` each grid is one named `@st.fragment` —
`_strength_grid_block()` and `_weakness_grid_block()` — whose body is the one
call of `_tick_grid`, so the subheader, citation, grid, panel, Answer key and
notes are all drawn inside it. A selection reruns that block and nothing
else. Both grids, both reading depths.

The only new page strings are the panel's: `": "`, `" of "`,
`" testimonies"`, `", "`, `"sentence "`, `"Fact"`, `"Value"`. None carries a
digit; every number the panel prints is a paragraph number, a count, a total
or a chart value.

## What the browser showed

The worktree's server on port 8522, `preview_start(url=...)`, the
Configurations page at 1400×900, on the chart the app opened with (the
owner's last-used saved chart, not the fixture default).

**Pointer events reached the page this time.** The Strength & Weakness tab
answered a click by element reference, and the Sun's row marker answered a
click by coordinate — after one mis-scaled click of mine that landed in the
sidebar's time input and focused it without changing anything. The earlier
branches' notes had synthetic clicks not arriving at all; here they did.

**The panel:** `Sun: 8 of 11 testimonies` under the grid, with the Sun's
ticks on that chart — 78, 80, 81, 82, 83, 85, 86, 88 — each as a caption
`Sahl, The Introduction Ch. 3, n`, the sentence, and a Fact / Value table:
78 `Whole-sign place 10`, `Excellent places 1, 4, 5, 7, 10, 11`; 80
`Retrograde (accidental) no`, `Speed in longitude 1.01`; 81 `Infortunes Mars,
Saturn`, `Configuration with Mars Sextile`, `Configuration with Saturn
Aversion`; and so on, the Answer key and notes expanders standing after it.

**Fragment rerun, not page rerun** — the fragments branch's measurement: take
references to every `[data-testid="stDataFrame"]` node, change one thing,
count how many of those exact nodes are still `document.contains(...)`-true.
With the Sun's panel open (28 dataframe nodes on the page), the Moon's row
marker was clicked:

| zone | nodes referenced | still attached |
|---|---|---|
| before the strength grid | 8 | **8** |
| inside the strength fragment: the grid, the Answer key's table, the Sun's eight fact tables | 10 | 3 — the grid itself the same node, 7 redrawn |
| the weakness grid | 1 | **1** (same node) |
| after the weakness grid | 9 | **9** |

The heading read `Moon: 2 of 11 testimonies`, and the strength block then
held four dataframes: the grid, the Moon's two fact tables, the Answer key's.
Every table outside the strength fragment — 18 of 18 — was left in place;
only nodes inside the fragment, which it redrew, were replaced. (The
fragments note recorded the control: a full rerun detaches every table.)

**Preferences:** `~/.local/share/TraditionalAstrologyEngine/preferences.json`
hashed `e39f0610…6455` before with `_launches: 10`, `f429be60…c06c30` after
with `_launches: 12` — two page loads, each a session. With the count set back
to 10 the file hashes to the before value, so the launch count is the only
change. No preference was touched; a selection writes nothing.

## What the harness showed

AppTest's `Dataframe` element has no selection method, but a selection can be
seeded through the widget's key — `st.session_state[key] = {"selection":
{"rows": [0]}}`, the schema Streamlit documents on `DataframeState` — and the
panel then renders under the harness. Seeded, the default chart gives `Sun: 7
of 11 testimonies`, the seven captions 79…88, the seven sentences equal to
the row's labels, and each Fact / Value table equal to the row's facts split
at `": "`; the weakness grid seeded at the Moon's index gives `Moon: 2 of 10
testimonies` with 93 and 98. Unseeded, no panel, no Fact / Value table, and
each grid's block is exactly Subheader, Caption, Dataframe, Expander, Status
(the notes expander carries an icon, which AppTest renders as a Status
element).

## The differential

`tests/test_row_detail_2026_09_15.py`, 66 tests:

- **A.** both evaluators on all six fixture charts, on `origin/main`'s
  `engine.py` (exec'd into its own namespace) and on this branch: with
  `Testimonies` dropped the rows are equal as values and as `repr` text —
  **12 (evaluator, chart) pairs, every one equal**;
- **B.** for every row on every chart: the list of `n` equals the paragraph
  numbers `_tick_grid`'s own regex parses from the labels, in order; each
  sentence is the label at the same index; `Count` is the length of both;
  every testimony has at least one fact; every fact is `"Fact: Value"` with no
  `": "` and no digit in the name; the keys are the old four then
  `Testimonies`;
- **C.** the default chart's Sun (79, 80, 81, 82, 83, 85, 88), Saturn (78,
  79, 80, 81, 82, 83, 85, 88) and Moon's weakness (93, 98), pinned by number
  and by facts, several read back against the chart's own functions
  (`get_wsh_house`, `get_effective_house`, `get_zodiac_sign`,
  `get_essential_rulers`, the dignity flags);
- **D.** the two fragments exist and are decorated; `_tick_grid` is called
  once in each and nowhere else; the grid carries `on_select`,
  `selection_mode` and the key derived from the title; the panel's strings
  carry no digit; no panel on either depth without a selection; the seeded
  panels above, inside the fragment's block, with the other grid untouched;
  both grids selected at once; the panel's captions name only the grids'
  paragraph numbers; `tests/fixtures/tables.json` equals `origin/main`'s.

**Existing tests changed, none weakened:**

| file | change |
|---|---|
| `test_fragments_2026_09_15.py` | the fragment inventory expects four names (`_strength_grid_block`, `_weakness_grid_block` beside the two wheels); renamed to say so |
| `test_symbol_font_2026_09_15.py` | the SVG comparison against main made symmetric — `_normalise` on both sides — since main has carried the font from `5c5f55d`, this branch's base; the three "is main's" tests failed on main itself for that reason. The `"<style>" in here` assertions stay; the `here != there` lines, true only while main lacked the font, are gone. The same repair the symbol-font branch made to the clickable wheel's proof |

No existing test compares whole rows of these evaluators with `==`
(`test_astra_audit_repro.py` reads `Labels`, `test_prose_counts.py` reads the
source), so none needed `Testimonies` dropped.

`tests/fixtures/tables.json` is unchanged. Full suite: **2424 passed, 1
skipped, 6 xfailed in 27.44s**, `-n auto` on the owner's venv; 2358 to 2424 is
the 66 new tests and nothing else.

## Not built, under the canon rule

Nothing of the item was left out for the two grids. What was deliberately not
done: no fact was reconstructed from the text where the code does not compute
it — 96 and 100 show the one flag the branch tests and no sign or lord it does
not look up; 95's `severe` grade, which `_sahl_enclosed` returns but the label
does not report, is not shown, since the page would be naming a distinction
the table does not make. The other evaluators' tables are the item's "rest",
one table at a time, and are not touched here.
