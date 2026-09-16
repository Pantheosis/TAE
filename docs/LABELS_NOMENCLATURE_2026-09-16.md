# Nomenclature and status on the pages -- 2026-09-16

Branch `labels-nomenclature-2026-09-16` off `main` at `765b417`. Five
findings of the independent UI review of 2026-09-16 (Astra) -- F07, F09,
F10, F11, F15 -- with its evidence rows E09, E10, E11 and E12 as the
acceptance cases, under the owner's rulings. One dead test is retired with
them.

Nothing here is new doctrine. Every change renames, qualifies or reconciles
something the evaluators already compute. The two connection tests,
`_is_connected_sahl` and `_is_connected_abu_mashar`, and every boolean
downstream of them are untouched; the AST diff of `engine.py` against main
is one added helper and two changed functions, listed at the end.

## F10 -- the aspects table in Dykes's words

The review's E11 read the default chart's first Moon/Sun row as **Applying
Planet = Moon -> Sun**, **Motion = Separating**, **Connected = Yes**, and
asked the reader to work out why three columns seemed to disagree. They do
not disagree: they are three different facts, and only the third was being
printed as a verdict instead of as a state.

**`Applying Planet` -> `Connecting planet`.** The arrow, and the cause in
parenthesis when the heavier planet is the one closing, stay exactly as they
were. The heading is the texts' own verb: the light planet "connects with"
the slower one (Gr. Intr. VII.5, 9), "going straightaway to" it (Sahl, The
Introduction Ch. 3, 6).

**`Motion` keeps Applying / Separating.** They are Dykes's words for the two
kinetic states, and the engine's own comment on the branch that computes
them says so.

**`Connected` (Yes/No) -> `Connection`, with the states the code has.** The
mapping, state by state, with the branch it comes from and the sentence it
is named from:

| State | The branch that decides it | Locator |
|---|---|---|
| **Applying** | connected, `row['motion'] == 'Applying'` | Sahl Ch. 3, 6 ("going straightaway to"); Gr. Intr. VII.5, 9-11 ("going towards" the connection) |
| **Under a single blanket** | connected, `row['motion'] == 'Separating'` -- `_is_connected_sahl`'s separation window, half the light planet's body in one sign, a full degree across a boundary | Sahl Ch. 3, 7 ("the position of two men under a single blanket"), 9-11 |
| **Not yet** | not connected, `row['motion'] == 'Applying'` | Sahl glossary, *Applying*: "not yet connecting by the relevant degrees, are only 'wanting' to be connected" |
| **Separated** | not connected, `row['motion'] == 'Separating'` | Sahl Ch. 3, 10; glossary, *Separation* |
| **--** | not connected and `aspect_name == 'Aversion'`: not configured at all | Sahl Ch. 3, 23 ("looking is from sign to sign") |

The owner's brief named the second state **Under one blanket**. The page
carries **Under a single blanket**, which is the phrase as Dykes prints it
at Ch. 3, 7, under the binding rule that spellings are as on the pages. It
is the only place where this branch departs from the brief's wording, and it
departs toward the source.

An aversion row that holds Sahl's out-of-sign connection by body (Ch. 3,
20-21) is connected without a looking, and is named by its own motion like
any other row; its `Strength` cell still says which planet strikes into
which. Every other aversion row now reads `--` where it used to read `No`,
which is what the rest of that row's kinetic columns already read: `No` said
"not connected" where the truth is "no configuration to connect in".

**There is no Complete state**, and this is deliberate. Sahl 7 ("its
connection has come to an end") and Gr. Intr. VII.5, 11 ("then it has
completed its connection") both name completion at the exact minute, but
neither connection test branches on exactness. The only `deviation == 0`
branch in `engine.py` is in `_pairwise_configurations`, where it settles the
MOTION as Applying; Abu Ma'shar's `1e-9` in `_is_connected_abu_mashar` is
machine tolerance at exactness, as its own comment says, not his minute.
Printing Complete would be this app's distinction, not the texts'. A test
asserts that no row on any fixture chart prints it.

### What each profile can produce

Over the six fixture charts, 126 rows per profile:

- **Sahl** produces all five: Applying, Under a single blanket, Not yet,
  Separated, `--`. His window after exactness is the only source of the
  second.
- **Abu Ma'shar** produces four: Applying, Not yet, Separated, `--`. He has
  no post-exact window -- "if the light one passed by the slow one by one
  minute or by less than that, then it has already separated" (VII.5, 16;
  the same at 34) -- so his rows go from applying straight to separated, and
  every aversion row of his is a dash, since VII.5, 14 denies the
  out-of-sign case outright.

`Rules differ` is unchanged and still compares the two tests' booleans. A
test walks every row of every fixture chart under both profiles and asserts
that the displayed state is connected exactly when `_is_connected()` is
true, so a later edit cannot make the column drift from the test it reports.

### Help and caption

Four columns now carry their definition on the heading itself
(`column_config`), so the term is defined where it is read rather than in
the notes expander: `Connecting planet`, `Motion`, `Connection` (all five
states, each with its locator) and `Orientation` ("Dexter, Dykes's right:
the ray cast to earlier degrees of the zodiac; sinister, his left: to later
ones"). Dexter/Sinister are kept as the headwords, on the owner's ruling:
Dykes's own headword is right/left, but "right" collides with VII.6's right
side of the Sun and with right-sidedness.

One sentence under the table says why the three columns can differ in one
row: *A separating pair stays connected inside Sahl's window (The
Introduction Ch. 3, 7-10), which is why Connecting planet, Motion and
Connection can differ in one row.*

`Connection` is given a medium column width, because the default cuts "Under
a single blanket" mid-word. The width of a state's name is not a reason to
shorten the name the text gives it.

### The default chart's Moon/Sun row, after

`Connecting planet` **Moon -> Sun**, `Motion` **Separating**, `Connection`
**Under a single blanket**, `Rules differ` **Yes** -- the pair is 5 deg 32'
past their conjunction, inside the Moon's half-body of 6 deg (her light is
12 deg, Ch. 3, 14) and so still connected for Sahl, and separated for Abu
Ma'shar. Under his profile the same row reads **Separated**.

## F07 -- a bounded search is not an absence

`_finding()` takes an `absent=` keyword. When it is given and the data is
empty, the finding keeps its own heading and prints that sentence instead of
dropping its title into `_gap`, which `_absent()` prints as "Not present in
this chart: ...".

One finding passes it: **Forward-Looking Conditions** (revoking, resistance
and escape, all three of them read out of `_simulate_forward`). Its sentence
is *No qualifying event found within 200 days of the chart; later events
were not evaluated.* The 200 is not typed on the page: the block reads
`sim['horizon_days']`, the horizon the simulation actually ran to, and the
citation, the glance and the notes on that finding now interpolate the same
value. `tests/test_prose_counts.py` pins that they all do.

Nothing else on the page takes `absent=`, and the reason is that nothing
else is a bounded search:

- **Favor & Recompense** tests the chart moment -- a planet in its own fall
  or a well with a connecting dispositor. Only the *Recompense (days)*
  column comes out of the simulation, and it is a column of a row, not the
  row's existence. An empty table there is a real absence.
- **Prevented connections** merges Sahl's blocking, nullification and
  cutting (all instantaneous) with Abu Ma'shar's two further cuttings
  (forward-simulated). Its emptiness is therefore mostly an absence, and
  saying otherwise would overclaim in the other direction.

## F09 -- the approximation travels with the value

`_chart_strip()`, which every page carries, prints `Hour lord <planet>
(equal-hour approximation)` whenever `chronocrats['Approximate']` is true --
the circumpolar case, where no sunrise or sunset exists and the temporal
hour is undefined. The Chart page's fuller warning is untouched.

On the review's E10 fixture (2025-06-21 12:00 at 69.6492, 18.9553 under a
manual UTC+00:00 offset) the strip's second line now ends **Hour lord
Mercury (equal-hour approximation)** on Chart, Configurations and Timing
alike. The default chart's strip is unqualified, and a test asserts both.

## F15 -- one heading, and help that describes the app

**The duplicate heading.** Two consecutive `st.subheader('Topical Planets in
Houses', ...)` stood on the Dignities page with incompatible help. The one
saying the Rhetorius and Firmicus texts are *not in hand* is removed; the
one saying both are in hand, that the Reference Guide's summary is still
what the table prints, and that it has not been checked against them, is
kept. That is the true sentence: Rhetorius (Holden) and Firmicus's *Mathesis*
Book III, including III.2-III.13, are both filed in the corpus, and the app
already quotes Rhetorius Chs. 26-28 and 41-42 in a table of its own and
*Mathesis* III.7 in another. The reservation in the surviving sentence is
also true and is why it survives rather than being replaced: what the table
prints is still the Guide's summary, unchecked against the two texts.

**The contradictory Net/Verdict caption.** The Configurations caption said
Net and Verdict are kept "only because the Rhetorius/PN IV delineations on
the Dignities page have to pick one of two readings", while the Dignities
page says in as many words that neither is chosen. The caption now says what
that page does: it prints both the good and the bad reading for each
placement and chooses neither, showing this Net as a lean, and a Net of zero
is Indeterminate on both pages. The doctrine sentences around it -- that Abu
Ma'shar enumerates the conditions and never totals them, that VII.6 gives no
weighting and no tie rule, and that the counts are to be read in preference
to the number -- are untouched. The same sentence inside that table's notes
expander is corrected the same way.

**The mighty-days note.** The note under the small days said "Only the
revolution's Ascendant is directed", while the page carries a working
selector that directs any planet, house or Lot of the revolution and prints
both its small days and its profected mighty days. It now says that: the
table below directs the revolution's Ascendant, and the selector above
carries out IX.7, 31's extension. The mighty-days caption already named the
selector and is unchanged.

## F11 -- the classical Lots' provenance

The classical note promised that all four of Fortune, Spirit, Exaltation and
Basis carry their provenance below, and the provenance panel under the
Topical Lots table excluded them, as the position table does.

Their four `LOT_DEFINITIONS` rows do carry the same three fields every other
Lot's does -- `source`, `confidence` (the Standing column) and `note` (the
Editor's note) -- so **the four rows are included in the provenance panel**,
first, ahead of the topical rows. No text is written for them. The position
table above is unchanged: those four keep their positions in the Classical
Lots table at the top of the page, which is where they belong. The note now
names the panel it sends the reader to rather than the table it sits under.

## The retired differential

`tests/test_engine_split_2026_09_15.py::test_every_reading_and_chart_evaluates_as_main_did`
compared every evaluator on main's engine half against `engine.py`, over six
charts and fourteen switch states. It cut main's `app.py` at the UI marker
to get that half. Since the split merged, main's `app.py` has no engine
above the marker, so the test could only take its skip branch, on every run,
forever. It is deleted, with `_main_engine_namespace` and the three pieces
of scaffolding only it used (`run_evaluators`, the `EVALUATORS` inventory
and `_READING_OF_SWITCH`), and the imports that went with them. A comment
in its place points at `docs/ENGINE_SPLIT_2026-09-15.md`, where the run is
recorded. The per-reading value tests and the thread tests in that file
stand.

## The fixture diff, in words

`tests/fixtures/tables.json` was regenerated serially
(`UPDATE_TABLE_FIXTURE=1 ... pytest tests/test_pages_render.py`, no `-n`).
It changes in twelve lines and nowhere else: in each of the six charts'
Configurations slot, in the one table "Aspects, aversions and connections",
`Applying Planet` becomes `Connecting planet` and `Connected` becomes
`Connection`. No table is added or removed, no other column name moves, and
no column order changes.

Three guards compare this branch against main and had to record that
change rather than forbid it:

- `conftest.with_2026_09_16_renames()` brings main's copy of the fixture
  through the two renames; `test_row_detail_2026_09_15.py::test_the_tables_fixture_is_mains`
  and `test_input_state_2026_09_16.py::test_the_table_fixture_is_the_one_main_carries`
  use it, so they go on pinning every other column of every other table.
- `test_input_state_2026_09_16.py::test_the_page_functions_are_mains_own_one_guard_line_apart`
  (F05's dedent, proved against main's AST) now compares statement by
  statement: a page function not listed in `CHANGED_2026_09_16` must still
  be main's own body exactly, and for the four that are listed, every
  differing statement must carry one of the words that names this branch's
  edit, and every one of those words must be used. A later branch that
  edits a page adds its own entry, or the test fails and says which
  statement moved.

## The engine diff

AST diff of `engine.py` against `origin/main`:

- **added**: `_connection_state(row, connected)` -- the state mapping above,
  with the passages it is named from in its docstring.
- **changed**: `evaluate_ptolemaic_aspects` -- two dict keys renamed, the
  connection cell built by the new helper instead of `'Yes' if ... else
  'No'`, and one sentence of its docstring.
- **changed**: `point_summary` -- the wheel's planet panel copies seven
  columns of the aspects row by name, and two of those names moved. This is
  a forced consequence of the rename, not a second decision: without it the
  panel would read `None` for both.
- **unchanged**: `_is_connected_sahl`, `_is_connected_abu_mashar`,
  `_is_connected`, `_rules_differ`, `_pairwise_configurations`, and every
  evaluator downstream. No module-level statement changed.

## Tests

New: `tests/test_labels_nomenclature_2026_09_16.py`, 37 tests -- the column
names, the Moon/Sun row under both profiles, every state each profile can
produce and none it cannot, the state against `_is_connected()` on all six
charts under both profiles, the absence of a Complete state, the four help
strings read off the rendered dataframe's own proto (hover cannot be
screenshotted), the caption under the table, the empty forward finding's
heading and horizon sentence and its absence from the "Not present" line,
the AST check that exactly one `_finding` call takes `absent=`, the polar
strip on three pages, the single Dignities heading and its surviving help,
the two reworded captions, the alternate-point control, the four classical
provenance rows, and the retirement above.

Changed (what they read, not what they check):

- `tests/test_sahl_question_chart.py` -- the Moon/Jupiter row of Sahl's own
  worked question chart, `Connected == 'Yes'` becomes `Connection ==
  'Applying'` (applying and connected); and the Venus negative control's
  row tuple reads `Connection`.
- `tests/test_clickable_wheel_2026_09_15.py` -- the wheel panel's seven
  copied columns.
- `tests/test_prose_counts.py::test_forward_horizon_is_quoted_correctly` --
  from "the page types the engine's number" to "the page interpolates it and
  types it nowhere", which is what F07 made true.
- the three main-comparison guards above.

The full suite: 2515 passed, 1 skipped, 6 xfailed.

## The live check

Run from this worktree on port 8526 with `XDG_DATA_HOME` pointed at a scratch
copy of the owner's data directory. The Configurations page's Aspects &
Connections tab renders the eleven columns headed `Light Planet, Aspect,
Heavy Planet, Connecting planet, Motion, Orientation, Exact Orb Dist,
Bodies, Strength, Connection, Rules differ`, with Not yet, Applying, `--`,
Separated and Under a single blanket all visible in the first ten rows. The
owner's `preferences.json` and `saved_charts.json` hash the same before and
after.
