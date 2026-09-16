# The hostile pass answered -- 2026-09-16

Branch `hostile-fixes-2026-09-16` off `main` at `5e90402` (the merge of the
hostile pass itself, PR #57). The five **High** findings of
`docs/HOSTILE_PASS_2026-09-16.md` and two of its Medium friction items, M3
and M4. **M1 is not touched**: whether the Configurations *Verdict* should
adopt the Dignities *Lean*'s margin of one at |Net| = 1 is doctrine and the
owner's to rule, and its strict `xfail` stands exactly as the pass left it.

No doctrine, no evaluator, no table. `tests/fixtures/tables.json` is
unchanged (`git diff main` on it is empty): no table was renamed or added,
and the recovery panel adds none.

## The root cause, and the rule that answers it

The pass named it in one sentence: **the sidebar validates the draft
against form, never against what the ephemeris or the engine can actually
consume, and the calculation and the target bundle run at module level
*before* `st.navigation(...).run()`.** So an input that passes the form
checks and then raises takes the whole script down -- no page, no recovery
panel, and a navigation bar that is drawn but inert.

The rule this branch holds to:

> Every input that can make the engine raise is validated at the sidebar
> stage into `chart_ok = False` with a message, and anything loaded from
> disk is validated for type and range **before it reaches a widget key**.

That is the same shape as F02's coordinates (validated as a draft, before
the widget can clamp them) and F01's date (committed only when it parses),
extended to the two things neither covered: what the **ephemeris** can
reach, and what a **stored record or preferences file** holds.

---

## H1 -- a birth date the ephemeris cannot reach

**Was:** any year from 3002 to 9999 (the Date help and `parse_iso_date`
both take years 1-9999) gave a raw `swisseph.Error` in the page body, with
the top bar present but dead.

**Now:** the span is measured, not assumed. `swe.calc_ut` answers from
Julian Day **625000.5** and raises at **2818000.5** -- `swe.revjul` puts
those at -3001 February and 3003 April, and both ends were checked by hand
(`test_the_span_is_the_one_the_ephemeris_answers_to` keeps checking them).

A chart is never one position, though: every date the app is given is
**searched forward from**. Measured, at the top of the span:

| search | reaches past its date |
|---|---|
| the Timing page's 15th indicator, the revolution's lord through its sign (Saturn's horizon in `pn4_further_indicators`) | **900 days** |
| the natal page's gestation Moons (`evaluate_gestation`) | about 380 days |
| the next revolution of the year (`jd_sr_next`) | up to 365 days past the target |

So a usable date is one with a search's room above it -- which a date
inside the *raw* span need not have: a birth in **3002** is answered by
`swe.calc_ut` and then raises in the gestation search (seen before the fix
went in). `EPHEMERIS_SEARCH_DAYS = 950.0` is that room, and the app's last
moment is

```python
EPHEMERIS_JD_LAST = min(civil_to_jd(3001, 1, 1, 0.0),
                        EPHEMERIS_JD_MAX - EPHEMERIS_SEARCH_DAYS)
```

which is the second of the two, by some four months: **3000-09-20 is the
last date this app casts**, and it casts on every page (checked on Chart,
Dignities, Configurations, Timing, Victors and Lots, and as a target from
four different births). The sentence the sidebar prints names the round
span, as a limit stated to a reader should:

> This app's ephemeris covers 3000 BC to 3000 AD; the date is outside it.

It is asked where the moment is finally in UT, offset and all -- after the
LMT / named-zone / manual branch, before `calculate_traditional_chart_jd`
-- and answered like any other invalid input: `chart_error` set, `chart_ok`
False, the box that was about to announce a UT overwritten with the error.
The shell, the top bar, Reference and Sources all stay; every page that
reads the chart opens with `_recovery_panel`, which prints the same
sentence. The Date field's own parse is untouched: years 1-9999 still
parse, and the range check refuses what the parse accepts.

The bottom of the span is unreachable from the Date box (the parser will
not take a year below 1), and is checked all the same.

## H2 -- the Timing target, from either box

**Was:** *Target by = Age* with a large age (the `number_input` had
`min_value=0` and **no upper bound at all**), or *Target by = Date* with a
far date, drove `pn4_timing_bundle` -> `pn4_solar_revolution_jd` past the
ephemeris and killed the shell exactly as H1 did.

**Now**, three things:

1. **The target is bounded**, by the same `date_in_ephemeris` the birth
   date uses -- which is why the 950-day room is measured from the
   *bundle's* furthest search and not just the natal page's.
2. **A target out of reach keeps the last valid one**, which is what F17
   already does for a target that will not *parse*, and the Timing page
   says so in the target's own row:
   `The target is beyond this app's ephemeris (3000 AD); keeping <date>.`
3. **The Age box has a `max_value`**, computed from this chart's birth year
   (`max_target_age`), counted down from the last year covered because the
   limit falls inside that year: 1760 on the 1240 default, 1017 on
   1982-11-19, 10 on a 2990 birth. The age AT the bound still casts; one
   year past it -- which only a store can now hold, a saved record's
   `target_age` or a carried-over session -- gets the sentence and the kept
   target.

No exception handler was needed at the bundle's boundary: with the target
bounded this way, nothing in the bundle leaves the ephemeris.

## H3 -- a saved record with a type-wrong field

**Was:** `_validate_chart_mapping` checked the *shape* -- string names,
dict entries -- and never the field types the sidebar and the engine
consume. An int `time_string` had no `.split`, a str latitude would not
compare with the widget's float bounds, `"abc"` was not an `int()`. Each
crashed the whole script on load; as the `last_chart` it made the app
**dead-on-open**.

**Now:** `chart_record_fault(entry)` (engine, section 0) reads a record
before any of it is written into a widget key, and returns the first field
it cannot load, as (the field's name for a reader, what it is not).
`_validate_chart_mapping` is deliberately left checking the shape alone:
raising there would condemn the whole *file* -- the loader would copy it
aside and open with an empty picker -- when one entry is at fault.

What is a fault, and what is not:

- **A wrong type is a fault.** `date_string`, `time_standard`,
  `location_query`, `target_mode`, `target_date` must be text;
  `time_string` must be `HH:MM:SS`; `lat`, `lon`, `utc_offset`,
  `target_age` must be numbers, with `lat` in [-90, 90], `lon` in
  [-180, 180] and `target_age` a whole number of years, zero or more.
- **A number written as text counts as that number.** `'43.7792'` is that
  latitude: `_records_match` already reads it as that latitude when it
  decides whether a record has been edited (pinned by
  `test_the_coordinates_are_compared_as_numbers_to_four_places` on main),
  so a loader that refused it would have the app calling one record two
  things at once. `record_number()` coerces; the loader writes the
  **number** into the widget key, which is what the widget needed all
  along. Text that is not a number is a fault.
- **A wrong VALUE inside the right type is not a fault** -- it goes where
  the app already handles a bad draft. A `date_string` of `"not-a-date"`
  loads into the date box and gets the box's own error (F01, and a test on
  main pins exactly that); a `target_date` that will not parse keeps the
  last target that did (F17); a `time_standard` the app no longer offers
  raises the "saved before the time standard was stored" flag. **This is
  the one place the brief's rule is read down**: it asks for `date_string`
  and `target_date` to be "parseable", and parse failures are left to the
  draft rules that already cover them, because refusing the record outright
  would take away behaviour that is pinned on main.
- A field the record does not carry, or carries as `null`, is never a
  fault: records written before a field existed still load.

### The presentation chosen (H3 asks for one of two)

**The sidebar warning.** The record keeps **its own name in the picker** --
no ` (unreadable)` suffix -- the load is refused, the form is left exactly
as it was, and the sidebar says, beside the picker:

> 'Rec' could not be loaded: its time is not a time of day as HH:MM:SS.

The suffix was not chosen because a name is the record's identity here: it
is the key in the file, the thing Save, Replace and the bin are keyed by,
and decorating it in the one list the reader picks from would make the
record harder to delete, not easier.

Three consequences follow from "nothing was loaded", and all three are
implemented:

- **`last_chart` is not remembered** for a record that would not load: the
  app should not open on a chart it cannot open.
- **The launch survives one.** The autoload points the picker at the record
  only when the record loaded, so the app opens with **no chart loaded**
  and the sentence beside the picker -- where it used to open on a
  traceback with no page reachable at all.
- **It is not called "modified", and it does not name the chart.** The
  fields never held it, so they cannot have been edited away from it; and
  the strip must not title the chart on the screen with a record that is
  not on the screen. (That last one was **found in the browser** during
  this branch's own live check: the strip read `Type wrong · 1982-11-19
  11:44:00` over the nativity the boxes were still holding. It now reads
  `Unsaved chart`, and a test pins it.)

The record itself is untouched on disk, and stays in the mapping, so a
later save of another chart writes it back exactly as it was found.

## H4 -- a corrupt preferences file

**Was:** `load_preferences` kept the known keys and never looked at their
values, so a `"_launches": "many"` met `int(...)` and a `"last_chart":
["a"]` met a dict lookup, both at module level, on **every page**: the app
would not open.

**Now:** `preference_is_valid(key, value)` checks every key against the
type or the option tuple **its own widget** is built from --
`_launches` an int >= 0, `last_chart` a string, the nine checkbox keys
bools, and the ten option keys against `CONNECTION_PROFILES`,
`EASTERN_RULE_OPTIONS`, `DOMAIN_RULE_OPTIONS`, `LOT_HOUSE_CUSP_OPTIONS`,
`PN4_MONTHLY_TURN_OPTIONS`, `READING_DEPTH_OPTIONS`, `WHEEL_LAYOUT_OPTIONS`,
`WHEEL_ORDER_OPTIONS`, `WHEEL_VIEW_OPTIONS` and `TARGET_MODE_OPTIONS`
themselves (read at call time, since most are defined further down the
engine). An entry that fails is **dropped**, so the reading falls to its
default, and nothing is written until the next `_persist` / `_remember`
does it. Silently, because preferences are silent by design: nothing
announces that a reading was *restored* either.

The renames of 2026-09-10 run **before** the check, so a value written
under an old option name is brought forward and then passes.

A guard test asserts that **every** key in `PREFERENCE_KEYS` (plus
`last_chart`) has a rule that accepts a real value and refuses a wrong one:
a preference added without one would be dropped on every read, silently,
with nothing to say the reading no longer persisted.

## H5 -- a saved UTC offset outside +-14

**Was:** `_restore_chart` wrote the stored offset into `utc_offset_key` and
Streamlit pulled it to a bound -- to the **minimum**, the wrong direction:
a stored 99 cast the chart at **UTC-14:00** with no warning, and a re-save
wrote `-14.0` into the record. That is F02's seeded-clamp class, fixed for
the coordinates and missed here.

**Now** the offset is read against the widget's own bounds before the
widget exists (`utc_offset_in_range`, `UTC_OFFSET_LIMIT = 14.0`, engine):

- out of range, the offset is **not written to the widget**; the rest of
  the record still loads;
- the sidebar says
  `'Rec' was saved with a UTC offset of 20, outside ±14; check the time standard.`
- the box keeps **0.0**, the offset a chart is cast at by default;
- the record keeps its 99 or 20 on disk, and the strip reads
  `<name> (modified)` -- because the stored record and the boxes really do
  differ, which is the truth of it;
- a re-save writes **what the box holds**, never the clamp.

Nothing is silently clamped, and no chart is cast confidently at a wrong
offset.

## M3 -- the name the picker keeps for itself

Save refuses `-- New Chart --` with
`st.sidebar.error("That name is reserved; choose another.")`, and refuses
any name that differs from the sentinel only by case or spacing
(`--new chart--`, `-- NEW  CHART --`): they read as the same option in the
list. A whitespace-only name keeps its existing refusal ("Enter a name
before saving."). `-- New Chart 2 --` still saves: only the sentinel itself
is reserved. The sentinel is now a named constant, `NEW_CHART_SENTINEL`,
used by the new code.

## M4 -- the one Timing control that did not survive navigation

`pn4_day_point` ("Also direct, for the small days ... from") was a plain
`st.selectbox` with a key and no `_persist`, so Streamlit dropped its state
whenever the page was not rendered and the choice reset on every walk away
and back. It goes through `_reading_select` with the store key
`_pn4_day_point`, like the *View*, *Wheel layout* and *Inner wheel*
controls beside it. Its options are the revolution's own planets, houses
and Lots, so a stored choice this chart does not offer falls to the first
option, which is what `_reading_select` does with one.

**For the owner, not decided here:** it is now remembered across
navigation, not across runs. It is a reading of sorts -- *which* point the
small and mighty days are directed from -- and it is the kind of thing a
reader would plausibly want to find where they left it next time. Adding
`_pn4_day_point` to `PREFERENCE_KEYS` would do that in one line. It is
**not** added in this branch: that is the owner's call, and a test pins
that the key is not in `PREFERENCE_KEYS` and not in the file.

---

## What changed, by function

**`engine.py`** -- section 0 (persistence and validation) only; nothing
doctrinal, no evaluator touched.

| function | change |
|---|---|
| `_validate_chart_mapping` | docstring only: says why it checks the shape and not the fields, and points at `chart_record_fault` |
| `_is_real_number` | **new** -- a finite int/float, never a bool |
| `record_number` | **new** -- a stored field as the number it means, text included |
| `_is_clock_string` | **new** -- `HH:MM:SS` as a real time |
| `CHART_RECORD_FIELDS` | **new** -- each field, its name for a reader, what it must be |
| `_chart_field_is_usable` | **new** -- one field against its rule |
| `chart_record_fault` | **new** -- the first field of a record that cannot be loaded, or None |
| `UTC_OFFSET_LIMIT`, `utc_offset_in_range` | **new** -- the widget's bounds, where the loader can read them |
| `PREFERENCE_BOOL_KEYS`, `_preference_option_tuples`, `preference_is_valid` | **new** -- what each preference must be |
| `load_preferences` | **changed** -- drops an entry that fails its rule (renames first); docstring |

**`app.py`** -- the sidebar and two page controls: `NEW_CHART_SENTINEL` and
`_is_reserved_name`; the ephemeris constants and `jd_in_ephemeris` /
`date_in_ephemeris` / `max_target_age`; the target block (bounded, with
`target_range_note`); the H1 check before the calculation; `_restore_chart`
(reads the record first, returns whether it loaded, refuses an out-of-range
offset) and `_apply_selected_chart`, the launch autoload, the `_record_notice`
line beside the picker, `_store_chart`, the Save refusal, `chart_modified` /
`_picked_loaded`, `chart_name`, `_chart_strip`, the Age `number_input`, the
target row's message, and the day-point selectbox.

## The tests

**`tests/test_hostile_pass_2026_09_16.py`** -- the eight strict `xfail`
markers over the six open defects are **removed**, and nothing else in the
file is touched. They pass as written:

- `test_a_birth_year_past_the_ephemeris_keeps_the_shell`
- `test_reference_survives_a_birth_year_past_the_ephemeris`
- `test_a_large_timing_age_keeps_the_shell`
- `test_a_far_timing_date_keeps_the_shell`
- `test_a_type_wrong_saved_field_keeps_the_shell` (five parameters)
- `test_a_corrupt_last_chart_does_not_kill_the_launch`
- `test_corrupt_preferences_do_not_kill_the_launch` (two parameters)
- `test_an_out_of_range_saved_offset_is_refused_not_silently_clamped`

M1's `xfail` stands.

**`tests/test_hostile_fixes_2026_09_16.py`** (new) -- what "no exception"
does not describe: the measured span and the last date the app casts; the
Age box's bound on two charts, the age at it and the age past it; the
bundle boundary from a 2990 birth at age 20; the sentence each unreadable
field gives itself, the form standing, the record untouched on disk, the
strip not naming it, a record missing a field still loading, and the launch
surviving an unloadable `last_chart`; the offset reported rather than
clamped and the re-save that writes the box's value; every preference key
valid and invalid, through `load_preferences` and through a launch with
`ALMUTEN_NO_PREFERENCES` unset and `XDG_DATA_HOME` on a tmp path; the
reserved name in three spellings and a name that merely resembles it; and
the day point surviving navigation while staying out of the preferences
file.

## The live check

Worktree server on port **8527**, `XDG_DATA_HOME` pointed at a **scratch
copy** of `~/.local/share/TraditionalAstrologyEngine/`, so the owner's own
charts and preferences were never in the path.

- **Year 3100 typed into the Date box.** The sidebar box under *Time
  standard* turned red with *This app's ephemeris covers 3000 BC to 3000
  AD; the date is outside it.*; the main area kept its **Chart** header and
  showed the recovery panel with the same sentence and *Correct the
  nativity in the sidebar; the reference tables and the sources stay
  available.* The top bar (*Part 1: the nativity*, *Part 2: prediction*,
  *Reference*) was **live**: Reference -> Reference tables opened and drew
  *Dignities by sign* and the rest in full, with the sidebar error still
  standing. No traceback anywhere.
- **A type-wrong record** (`"time_string": 1144`) selected in the picker:
  the yellow sidebar warning *'Type wrong' could not be loaded: its time is
  not a time of day as HH:MM:SS.*, the boxes unchanged (1982-11-19,
  11:44:00, Standard time), the strip reading *Unsaved chart*, the page
  drawn, no traceback.
- **A record with `utc_offset: 20`** selected: *'Offset twenty' was saved
  with a UTC offset of 20, outside ±14; check the time standard.*; the rest
  of the record loaded (Manual UTC offset, 1982-11-19), the offset box
  holding **0.00** and the box below reading *Manual offset UTC+00:00*;
  *Edited since it was saved.* under the picker and *Offset twenty
  (modified)* in the strip. No traceback.
- **`"_launches": "x"`** (with `"_wheel_layout": "Sideways"` beside it) in
  the scratch `preferences.json`: the app **opened** on a fresh server, the
  counter restarted at 1 and the layout stood at its default *Square*. The
  same open also autoloaded `last_chart`, which was by then the
  offset-twenty record, and showed its warning rather than a traceback.

**The owner's two data files, hashed before and after the whole session:**

```
dd817c155cb23a2cbb1d8b79b1e13d7fc33f798d6bce6c9290d211c924fd921d  saved_charts.json
4070389306f868fe8cabd5c18c9a244b35b8361101d61a99326a748a32bf1519  preferences.json
```

Equal, both files.

## Page text

Three new sentences, and they are the ones the brief names:

- `This app's ephemeris covers 3000 BC to 3000 AD; the date is outside it.`
- `The target is beyond this app's ephemeris (3000 AD); keeping <date>.`
- `That name is reserved; choose another.`

and two messages a loaded record gives about itself:

- `'<name>' could not be loaded: its <field> is not a <what>.`
- `'<name>' was saved with a UTC offset of <x>, outside ±14; check the time standard.`

No dates, no finding ids, no filenames, no build process; "this app", as
the house style has it. `tests/test_prose_counts.py` passes unchanged.
