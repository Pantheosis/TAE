# UI changes 2026-09-17 — "Here & Now" on the nativity sidebar

Branch `here-and-now-2026-09-17` off `main` at `bd8fdd9` (the merge of
PR #77, readability C). Brief: `HERE_NOW_BRIEF_2026-09-17.md` on the
Desktop. Two commits: the feature with its tests, then this note.

## What was asked

The owner's ruling of 2026-09-17: "Here" is a **stored home place**, set by
the reader from the birthplace the sidebar has already resolved — not
browser geolocation, not an IP lookup; the app is desktop only and offline
and nothing here may need the network. Four parts: a `home_place`
preference with a strict validator; a "Set as home" button under the
resolved-place box, with a caption naming the home in force and a "Forget
home" button; a "Here & Now" button directly under the Nativity header
that casts a chart for the home at this moment by this computer's clock,
disabled with a reason when no home is stored; and an injectable clock so
no test depends on the wall clock. Page text under the readability
ceilings, in this app's voice; the sidebar's state rules kept; `engine.py`
changes limited to the key, its validation and the clock provider; the
example chart's export byte-identical to main.

## What was built

### The preference

`'home_place'` is in `engine.PREFERENCE_KEYS`, with the value
`{"label": str, "lat": float, "lon": float}`. `engine.home_place_is_valid`
admits exactly that shape: a dict whose keys are exactly the three; the
label a string that is not empty or blank; the coordinates `float`
instances — an `int` is refused, because the app writes floats
(`json.dumps` of `43.7792`) and a hand-edit that wrote `43` is not the
app's own file; a `bool` is refused by the same test; finite and in range
through `coordinates_in_range`, which **moved from `app.py` to
`engine.py`** so that the file's validator and the sidebar's one
validation of a pair are the same rule (the app takes it back through its
star import; `app.py` keeps `COORDINATE_RANGE_MESSAGE`). `preference_is_valid`
dispatches the key to it, so `load_preferences` drops a malformed entry
the way it drops every other malformed preference: silently, the app
opens on the defaults, the button stands disabled, the entries beside it
are kept. (The launch then writes the file back for its own count, so the
dropped entry is gone from the file after the first launch — that is the
existing behaviour of `_launches`, not something this branch added.)

The launch's copy of the preferences into `st.session_state` (app.py, the
`_prefs` block under the Nativity header) carries `home_place` like the
others; a seeded `session_state` wins over the file, as it does for every
preference. "Set as home" writes both the session's copy and the file,
through `_remember('home_place', …)`, which compares first; "Forget home"
pops the session's copy and calls `_forget`.

### "Set as home", the caption, "Forget home"

Under Birthplace, directly after the resolved-place box
(`location_box`), inside the `else` arm of the one validation of the
coordinates — so the button is drawn only when a place is resolved and in
range, which is where `_resolved_lat`/`_resolved_lon` are written. A new
`_resolved_label` is written at the same site under the same condition:
the label the box shows (`location_query`: an atlas label such as
"Florence, 16 (IT)", or "Manual [43.7792, 11.2463]", or a loaded record's
own label). The callback `_set_home_place` reads the three `_resolved_*`
keys — the values of the run the button was drawn in, which are the
values the box beside it showed — builds the dict with `float()`
coordinates, checks it with `home_place_is_valid`, and remembers it.

Then, whenever a valid home is in force: the caption
`Home: <label> · <lat:.4f>, <lon:.4f>` (for example
"Home: Florence, 16 (IT) · 43.7792, 11.2463"; the label goes through
`escape` as the resolved box's does) and the "Forget home" button.

All three buttons carry `key`s and `on_click` callbacks. A callback runs
before the widgets of the rerun it triggers, which is what makes the top
of the sidebar right on the same run: after "Forget home" the "Here & Now"
button, drawn far above, is drawn disabled at once, and after "Set as
home" it is enabled at once. Processing the press inline where the button
stands would have left the top button one run stale, and a rerun from
sidebar height is not available (the delete confirmation learned that: it
abandons the run before the date, time and place widgets are drawn).

### "Here & Now"

Directly under the `Nativity` header, the first thing drawn after it
(before the flash, the store-error notice, the record notice and the
picker): `st.sidebar.button("📍 Here & Now", key="_here_and_now", …)`.
The glyph is an emoji, as the sidebar's other buttons' glyphs are (📂, 🗑,
💾) — the app's symbol font covers the 26 astrological glyphs only, so
"⌖" would have fallen to the system font. `help` is "Cast a chart for the
home place at this moment, by this computer's clock." when a valid home
is in force and "Set a home place under Birthplace first." when not, and
then `disabled=True`; Streamlit's tooltip wrapper is outside the button,
so the disabled button shows its reason on hover (checked on the
preview).

The callback `_here_and_now`:

1. **The instant**, once: `engine.now_utc()`.
2. **The zone at the home**: `TimezoneFinder().timezone_at(lng=lon, lat=lat)`.
3. **A named zone**: the instant converted with `pytz.timezone(name)`;
   `time_standard_key` = Standard time. The sidebar's own Standard branch
   then asks the same finder the same question and resolves the same
   offset from the same name, so the UT in the standard box is the instant
   that was taken. One exception: the repeated hour of a fall-back (02:30
   on 2026-10-25 in Europe/Rome happens twice), which that branch refuses
   as ambiguous, correctly. The callback checks with
   `zone.localize(…, is_dst=None)` and at that hour writes **Manual** with
   the offset the instant actually has, so the chart is cast at every
   moment of the year.
4. **No zone**: `engine.local_clock(instant)` — the instant as this
   computer's clock shows it — and Manual with that clock's offset in
   hours (quarter-hours preserved: 5.5, 5.75), written to `utc_offset_key`
   only when `utc_offset_in_range` admits it (H5: never an offset outside
   the number_input's bounds; a clock cannot give one).
5. **The moment**: `date_input_key` = `YYYY-MM-DD` of the local clock,
   `time_input_key` = `time(h, m, s)`.
6. **The place**: `manual_coords_key` = True, `manual_lat_key` /
   `manual_lon_key` = the home's floats, `loaded_location` =
   `{"label", "lat", "lon"}` so the coordinate fields show the home's name
   under the loaded-label rule rather than "Manual [lat, lon]".
7. **State**: `_loaded_without_standard` and `_record_notice` popped —
   both describe the record that was loaded, and the boxes no longer hold
   it. The picker and `last_chart` are left as they are: a loaded record
   then reads "(modified)" in the strip with "Edited since it was saved."
   under the picker, which is the truth. The Prediction target keys
   (`_target_mode`, `_target_date`, `_target_age`) are not touched: a
   chart cast now is at age 0 on those pages, which is correct. Nothing
   is saved; Save works as before on the cast chart.

The date box's Julian/Gregorian rule and the ephemeris span need no
handling — now is Gregorian and inside the span — and the docstring says
so; no code was added for it.

**A finding about the sea.** The brief expected `(0.0, -30.0)` to have no
zone and to take the Manual path. The timezonefinder this app ships
(8.3.0) answers an ocean zone there — `Etc/GMT+2` — and at every point at
sea (`Etc/GMT` at the pole, `Etc/GMT-12` at the date line); its
`timezone_at_land` returns None at sea, but the sidebar's own branch calls
`timezone_at`, and the callback must agree with the sidebar or the cast
would be refused with "Timezone boundary not found". So at sea the cast is
**Standard time under the ocean zone** (10:34:56 under `Etc/GMT+2` for
12:34:56Z), which is right. The no-zone path stays as a guard for a None,
which the sidebar also provides for, and the tests reach it by patching
`TimezoneFinder.timezone_at` to return None.

### The clock

`engine.now_utc()` returns `datetime.now(timezone.utc)`;
`engine.local_clock(instant)` returns `instant.astimezone()`. The callback
reads both through `engine.` at call time, so a monkeypatch on the module
object holds whether the app took the names through its star import or
not. `datetime.astimezone` itself cannot be patched (a built-in type's
attribute), which is why the local reading is a function too. The tests
patch after `make_app()`, because `make_app` reloads the engine when the
preferences environment moves and a reload puts the real functions back.

### What a reader sees

Under "Nativity": the button "📍 Here & Now", greyed with the tooltip
"Set a home place under Birthplace first." until a home is set. Under the
green resolved-place box: "Set as home"; once pressed, the caption
"Home: Petoskey, MI (US) · 45.3733, -84.9553" (two lines at the sidebar's
300 px) and "Forget home" under it. A press of "Here & Now" fills the date,
time, standard and coordinate boxes and the page reads the chart of this
moment; with a saved chart loaded, the strip reads "Jason Armfield
(modified) · 2026-09-17 11:45:12 · America/Detroit -04:00 · Petoskey, MI
(US) 45.37, -84.96" and the picker's caption says "Edited since it was
saved."

## Tests

`tests/test_here_and_now_2026_09_17.py`, 42 tests, AppTest, preferences
switched on against a `tmp_path` `XDG_DATA_HOME` as `test_preferences.py`
does. A button drawn disabled takes no click under AppTest (nor in a
browser), so tests that seed a home in `session_state` do it before the
first run.

- No home: the button disabled with its help; "Set as home" present with
  Florence resolved, absent with no atlas match and with a latitude of 91.
- "Set as home" on the atlas's Florence: the file holds
  `{"label": "Florence, 16 (IT)", "lat": 43.77925, "lon": 11.24626}` with
  float coordinates, the caption names it, the button is enabled with its
  help; the same press again leaves the file's bytes and mtime unchanged;
  "Forget home" removes it from the file and the session and disables the
  button on that run.
- A home in the file is carried into a fresh session; the manual pair is a
  home too; nothing is written under the harness guard.
- The validator: the good shape and a polar pair admitted; nineteen
  malformed shapes refused (not a mapping, a string, None, empty and blank
  labels, a numeric label, int coordinates, a bool, a string coordinate,
  NaN, inf, 91, -91, 181, a missing field, a missing label, an extra key,
  an empty mapping); six of them read from a file by a launch that opens
  on the defaults with the entry beside them kept; a seeded malformed home
  refused by the button.
- Here & Now at 2026-09-17T12:34:56Z with the Florence home: date
  "2026-09-17", time 14:34:56, Standard time, the home's coordinates and
  `loaded_location`, the widgets drawn from the keys, the resolved box
  "**Florence, 16 (IT)** … · Europe/Rome", "UT 2026-09-17 12:34:56" in
  the standard box, the strip "Unsaved chart · 2026-09-17 14:34:56 ·
  Europe/Rome +02:00 · Florence, …", no "Session State API" warning, no
  store written, the preference unchanged.
- January: 13:34:56 under CET. At sea: 10:34:56 under `Etc/GMT+2`. No
  zone (patched) with a +05:30 clock: 18:04:56, Manual, 5.5, then 5.75,
  then a -10 clock giving 2026-09-16 16:00:00. The repeated hour: Manual
  +2.0, no error, UT as taken.
- The target keys untouched on the Timing page; the picker still "-- New
  Chart --" when nothing was loaded.
- A loaded record ("Before", 1983-11-19) then Here & Now with a Petoskey
  home: the store's bytes untouched, the picker still "Before", the strip
  "Before (modified) · 2026-09-17 08:34:56 … America/Detroit -04:00",
  "Edited since it was saved."; Save as "Cast now" writes a record with the
  cast chart's date, time, standard, label and coordinates beside the old
  record, unchanged.
- A legacy record's "saved before the time standard" warning cleared by
  the cast.
- The four new page strings under 300 characters, none saying "the app".

`tests/test_hostile_fixes_2026_09_16.py`: `_valid_preference` and
`_invalid_preference` gain a rule for `home_place`, which that file's
"a rule per key or nothing" test demands of every key in
`PREFERENCE_KEYS` (its parametrised test grows by one). No other existing
test changed.

## Checks

- `python tests/test_text_lengths_2026_09_17.py` prints nothing;
  `ALLOWED_LONG` is empty.
- `python tests/tools/prose_preserved.py main --engine` prints nothing.
- The fixture regenerated once (`UPDATE_TABLE_FIXTURE=1`, 85 passed);
  `git diff --stat tests/fixtures/tables.json` empty.
- The example chart's Markdown export, taken from `_analysis_markdown`
  under AppTest on an archive of `main` and on the branch: 220,351 bytes
  each, one differing line, the `engine_file_sha256` row.
- Preview on the coordinator's launch entry at port 8531 (cloned data),
  1400 × 900 and 1920 × 1080, light and dark: the disabled button under
  the header at y 132 with the header at 76, its tooltip on hover; "Set
  as home" 97 px wide under the resolved box; the caption and "Forget
  home"; the cast chart on the Chart page and the strip; "Forget home"
  disabling the button on the same run. The clone's home was forgotten
  and its launch count put back to 99 before the preview was stopped.
- Full suite `-n auto`: 3731 passed, 1 skipped (main: 3688 passed,
  1 skipped).

## What was left

Nothing of the brief. Two departures, stated: the sea case is Standard
time under the ocean zone rather than Manual, for the reason above (the
Manual path exists and is tested with the finder patched); and the
repeated hour of a fall-back takes Manual with the true offset, which the
brief did not ask for and which keeps the button from being refused one
hour a year.
