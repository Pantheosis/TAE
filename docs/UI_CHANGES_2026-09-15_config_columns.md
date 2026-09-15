# UI changes 2026-09-15 -- the config file, with magic off, and column_config on the tables

Branch `config-columns-2026-09-15` off `main` at `d589e78`. Items 6 and 7 of
`UI_FRAMEWORK_REVIEW_2026-09-15_SECOND_OPINION.md`: the missing
`.streamlit/config.toml` and `st.column_config` on the tables. Engine half of
`app.py` untouched, byte-identical to `main` (compared directly, not by
reading the diff).

## What was asked

**Item 6.** `Executable/.streamlit/config.toml`, with exactly two sections
and a comment on each saying why it is there: `[runner] magicEnabled = false`
(the app has no bare expressions, so magic costs parsing and rewriting for
nothing) and `[client] toolbarMode = "minimal"` (the Deploy button and the
toolbar are not for a study companion). No `[theme]`: the app follows the
viewer's own theme and the pictures have their own palette control. The same
option in `tests/conftest.py`, set before the first `AppTest` is built, so
the suite does not depend on the working directory. A new test proving the
app has no bare expression anywhere -- an AST fact, not an assertion taken on
faith -- and measurements of one `AppTest` render of the Chart and the Timing
page, magic on and off, three runs each, so this branch's own numbers are in
this note rather than carried over from the review.

**Item 7.** `st.column_config` on three kinds of column, widths and header
text only -- no DataFrame value changes anywhere, since `tests/fixtures/
tables.json` pins every table's own columns and the doctrine fixtures compare
cell values:

1. The Strength and Weakness tick grids: each testimony column's header
   loses its leading sentence number ("78 excellent place" reads "excellent
   place"), the number moving into the header's tooltip.
2. Every text-heavy `Value`/`Text`/`Reading`/`Source`/`Note`/`Notes`/
   `Quotation`/`Sentence`/`Standing` column, wherever it appears, gets
   `width="large"` so the cell is not cut off.
3. The columns that actually hold only `"Yes"`/`"No"`/`""` get
   `width="small"` as plain text -- no `CheckboxColumn`, no boolean
   conversion.

## What was built

### The config file

`Executable/.streamlit/config.toml`:

```toml
[runner]
# The app has no bare expressions, so magic does nothing but cost: parsing and
# rewriting the script is over half of every AppTest render (measured 2026-09-15).
magicEnabled = false

[client]
# The Deploy button and the toolbar are not for a study companion.
toolbarMode = "minimal"
```

`tests/conftest.py` sets the same option directly, near the top, before
`EXECUTABLE_DIR` is even computed and long before any test builds an
`AppTest`:

```python
from streamlit import config as _st_config
_st_config.set_option("runner.magicEnabled", False)
```

**`desktop_launcher.py` is untouched.** Its own comment already explains why:
the frozen build carries no `.streamlit/config.toml` (`build.spec` bundles
`app.py`, `atlas.db` and `app_icon.ico` and nothing else), so it passes
`--client.toolbarMode minimal` as a flag, which outranks a config file
whether or not one is present. `magicEnabled` is not passed as a flag at
all, and does not need to be: the live server compiles the script once
(with whatever `runner.magicEnabled` a config file gives it, or the
built-in default), so the half-a-render cost this branch removes is a
harness cost, not a served one -- the new config file's `[runner]` section
matters to `pytest`, not to a reader's click.

**A new test file, `tests/test_config_2026_09_15.py`,** three tests:

- the config file exists, parses, and carries exactly `magicEnabled = false`,
  `toolbarMode = "minimal"` and no `[theme]` table;
- an AST walk of the whole of `app.py` finds no `ast.Expr` statement whose
  value is not a call, an `await`, a `yield`, or a string constant (the
  docstring case) -- **the count is 0, asserted and reported in the failure
  message** were it ever not;
- the same fact read off the UI half alone, by source text, so a UI-only
  regression is caught even where the engine half is checked separately.

**The magic on/off numbers, this branch, the owner's venv, three runs each,**
`tests/conftest.py`'s own `make_app()`, no `-n`:

| Page | magic on | magic off |
|---|---|---|
| Chart | 0.747, 0.463, 0.462 s (mean 0.56 s) | 0.199, 0.195, 0.195 s (mean 0.20 s) |
| Timing | 0.509, 0.530, 0.523 s (mean 0.52 s) | 0.241, 0.245, 0.249 s (mean 0.25 s) |

The first Chart run at 0.747 s is a cold start (import and first compile);
the other five settle at what the second opinion already reported (Chart
0.45 to 0.20 s, Timing 0.50 to 0.24 s) -- this branch changes nothing about
the app that would move those numbers, and re-measures them only because the
config file is new.

### column_config

**Two small helpers**, added beside `_finding()` in the UI half, both purely
name-based -- neither reads a cell's value, so neither can change one:

```python
_WIDE_TEXT_COLUMNS = {'Value', 'Text', 'Reading', 'Source', 'Note', 'Notes',
                       'Quotation', 'Sentence', 'Standing'}

def _wide_text_columns(df):
    return {col: st.column_config.TextColumn(width="large")
            for col in df.columns if col in _WIDE_TEXT_COLUMNS}

_YES_NO_COLUMNS = {'Connected', 'Match', 'Sees ASC', 'Above horizon',
                    "Domain (hayz)", "Of the chart's sect", 'Averse to its place',
                    'Rules differ'}

def _yes_no_columns(df):
    return {col: st.column_config.TextColumn(width="small")
            for col in df.columns if col in _YES_NO_COLUMNS}
```

`_finding()` -- which builds most of the app's tables -- now wires both in
once: `column_config={**_wide_text_columns(_df), **_yes_no_columns(_df)}`,
which reaches every one of its 33 call sites for free, since the dicts are
empty (`column_config={}`) wherever a table has none of these columns.

**`_yes_no_columns`'s set is not the brief's list read literally.** The
brief named `Connected, Received, Match, Sees ASC, Mutual, Active` as the
columns to check; this app was read column by column before any of them
were touched, the same way item 1's citation was read rather than assumed
("Ch. 5" in the brief's example, "Ch. 3" in this app's actual citations):

- `Received` (the Reception table) holds a planet's name or `"each other"`,
  never `"Yes"`/`"No"` -- left alone.
- `Active` (three different columns of that name: Topical Lots, the
  *fardar*, the Ages of Man) holds lowercase `"yes"` or `""`, and in the
  Topical Lots table sometimes a full sentence
  (`"NO -- Saturn is not under the rays"`) -- left alone; `width="small"`
  would cut the sentence off, which is the opposite of what this item asks.
- No column named `Mutual` exists anywhere in the app; `"Mutual"` is a
  *value* of the reception table's `Direction` column, not a column of its
  own.
- `Sees ASC` is kept despite printing `"No (averse)"` rather than a bare
  `"No"`: it is the brief's own named example, unambiguous either way, and
  the width fix is cosmetic regardless of the exact string.
- Four further columns qualify by the brief's own fallback clause -- "any
  other column whose values are only `Yes`/`No`/`''`" -- found by checking
  every rendered table's actual cell values across all five charts and both
  reading depths: `Above horizon`, `Domain (hayz)` and `Of the chart's sect`
  (the Dignities page's Sect table) and `Averse to its place` (its Topical
  House Lords table).
- `Rules differ` (the Aspects table) holds `"Yes"` or `""` and is included
  on the same fallback clause.
- The distribution tables' `Now` column (seven tables: the *jar bakhtar*,
  the Midheaven and fourth, the small days, the mighty days, the planets'
  own measure, the releaser's and the house-master's own distributions)
  holds lowercase `"yes"` or `""` -- the same shape as `Active`, and left
  alone for the same reason.

**The tick grids.** `_tick_grid()` now builds one `column_config` per call:
`Planet` and `Count` at `width="small"`, and for each testimony column a
`TextColumn(label=..., help=..., width="small")` where the label is the
column's words with the leading sentence number stripped and the help is
the chapter locator read off the call's own `citation` argument, plus that
number:

```python
_CITATION_LOCATOR = re.compile(r'^(.*), [\d\s,-]+$')
```

`citation` arrives as `"Sahl, The Introduction Ch. 3, 78-88"` (Strength) and
`"Sahl, The Introduction Ch. 3, 91-100"` (Weakness) -- **Ch. 3 in this app,
not the brief's illustrative "Ch. 5"** -- so the regex strips the trailing
run of sentence numbers and leaves `"Sahl, The Introduction Ch. 3"`; each
column's help reads e.g. `"Sahl, The Introduction Ch. 3, 78"`. Read directly
off the rendered proto (`configurations`, `1240-05-23`):

```
"78 excellent place": {"label": "excellent place", "width": "small",
                        "help": "Sahl, The Introduction Ch. 3, 78", ...}
```

Where a future `_tick_grid` call's citation does not end in a run of
numbers, the regex does not match and the help falls back to
`"sentence {num}"` alone, per the brief -- not exercised on this branch,
since both existing calls carry a numbered citation.

**Every `st.dataframe` call given `column_config`,** by heading (a `--` marks
a table reached through `_finding()`, already covered by the wiring above and
not touched at its own call site):

| Page | Table | Columns |
|---|---|---|
| Chart | Calculation | Value (wide) |
| Chart | Planetary Positions | Sees ASC (narrow) |
| Configurations | Strength of the Planets | tick grid (11 testimony columns, Planet, Count) |
| Configurations | Weakness of the Planets | tick grid (10 testimony columns, Planet, Count) |
| Configurations | Aspects, aversions and connections -- | Connected, Rules differ (narrow) |
| Dignities | Sect | Above horizon, Domain (hayz), Of the chart's sect (narrow) |
| Dignities | Topical House Lords (Masha'allah) | Averse to its place (narrow) |
| Findings | Mars in his own domicile, by sect (Abu Bakr) | Source, Text (wide) |
| Findings | Mercury's phase against the sect -- | Reading (wide), Match (narrow) |
| Lots | Classical Lots | Standing (wide) |
| Victors | Prenatal Lunation (Syzygy) | Value (wide) |
| Sources | Readings in force | Reading (wide) |
| Reference | The natures of the planets (Gr. Intr. IV.1) | Source (wide) |
| Timing | The revolution of the year | Value, Source (wide) |
| Timing | The image of the revolution of the year: its points | Source (wide) |
| Timing | The reading checklist -- I.7, 2-6, the revolution's Ascendant | Source (wide) |
| Timing | Indicators of the year, in Abu Ma'shar's order | Source (wide) |
| Timing | The sign of the terminal point and its lord: root, revolution, lord and refinement tables (4) | Source (wide) |
| Timing | Indicators 6-19: the fact each one reads | Source (wide) |
| Timing | The lord of the orb (VI.1) | Source (wide) |
| Timing | The governor: testimony, condition and first-month tables (3) | Source (wide) |
| Timing | When a luminary is lord of the year: the proxies | Source (wide) |
| Timing | The turning of the houses of the root: turning and triplicity tables (2) | Source (wide) |
| Timing | The releaser and the house-master: candidates, short-life testimonies | Source (wide) |
| Timing | The house-master directed: direction, revolution-facts, turning tables (3) | Source (wide) |
| Timing | The house-master directed: the lord-of-Ascendant / degree-of-Ascendant redirection tables | Source (wide) |
| Timing | The father's Lot: harmers table, from-lot / from-second direction tables | Source (wide) |
| Timing | The nine methods for the days and hours: weeks, month, ninth-part tables (3) | Source (wide) |
| Timing | The lords of the triplicity of the sect light, over the life | Source (wide) |
| Timing | Additions and subtractions to the house-master's years (Abu 'Ali) -- | Reading (wide) |
| Timing | The triplicity lords of the twelve houses, al-Andarzaghar -- | Source (wide) |
| every `_finding()` call not listed above (29 more, of 33 total) | -- | whatever of the nine wide-text or eight yes/no names its own columns carry, or none (several do carry one -- e.g. Chart's "Degrees of nobility and rank" has a `Note` column, Findings' "Places harming the eyesight" has `Source` and `Text` -- all reached by the one wiring into `_finding()`, none touched at its own call site) |

Thirty-seven direct call sites (two of them -- the house-master's and the
father's Lot's redirection tables -- render twice each per run, from one
call site inside a loop) plus the two helpers' wiring into `_finding()`
(covering 33 further call sites) and the tick-grid rewrite (2 call sites).
`grep -c "column_config=" app.py` reads 39: 37 direct, plus `_finding` and
`_tick_grid` themselves.

**Not touched, and why:** every distribution table's `Now` column and every
`Active` column (the *fardar*, the Ages of Man, the Topical Lots), for the
reasons given above; `Received` (a planet's name, not Yes/No); the "answer
key" expander tables under the tick grids (`Planet`, `Strength Testimonies`
or `Weakness Testimonies`, `Count`) -- their text column's name does not
match the wide-text set and the brief scoped item 1 to the grid itself.

## What the tests showed

`tests/fixtures/tables.json` **did not change** -- confirmed both by `git
status` on the file and by `tests/test_pages_render.py` passing unmodified,
with no `UPDATE_TABLE_FIXTURE=1` run. No table gained, lost or reordered a
column; `column_config` is a display instruction carried alongside the
`st.dataframe` call, not part of the DataFrame the fixture reads.

**Two new files.**

`tests/test_config_2026_09_15.py` (3 tests): the config file's contents; the
whole-app AST scan (bare expressions: **0**, as expected); the UI-half-only
AST scan.

`tests/test_column_config_2026_09_15.py` (23 tests): every one of the nine
pages still renders at both reading depths with no exception (18 cases); the
Strength and Weakness grids' `column_config` read off the rendered proto
carries the right `label`, `help` and `width` for a first and a last column,
and `Planet`/`Count` at `width="small"`; a `_finding()` table's `Value` and
`Text` columns read `width="large"`; a direct (non-`_finding`) table's
`Source` column reads `width="large"` the same way; the Dignities Sect
table's three Yes/No columns read `width="small"`, `type_config.type ==
"text"` (never a checkbox), and their own rendered values are still only
`"Yes"`/`"No"`.

**Full suite:** `2269 passed, 6 xfailed in 44.12s`, `-n auto`, the owner's
venv. 2243 to 2269 is these 26 tests and nothing else.

The engine half of `app.py` -- everything above
`# 4. STREAMLIT UI INTEGRATION` -- is byte-identical to `main` at `d589e78`,
compared directly.
