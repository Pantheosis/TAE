# UI changes 2026-09-17 — "Here & Now" on the nativity sidebar

Branch `here-and-now-2026-09-17` off `main` at `bd8fdd9` (the merge of
PR #77, readability C). Brief: `HERE_NOW_BRIEF_2026-09-17.md` on the
Desktop. Two commits: the feature with its tests, then this note; then,
after the adversarial pass (`HERE_NOW_ADVERSARIAL_REPORT_2026-09-17.md` on
the Desktop), one fix commit and this note's update — see "The fix round"
at the end.

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

### The layout: one row above the Nativity header (the owner's ruling)

The owner's ruling on the preview of PR #78: the first layout was too
cluttered — the home's controls intermixed with an already crowded
nativity sidebar — and the set/forget controls must be sequenced, out of
sight until wanted. The layout is now:

- **One row at the very top of the sidebar, above the "Nativity"
  header**: `_here_now_slot, _home_slot = st.sidebar.columns([3, 2])`.
  Left, the "📍 Here & Now" button (`width="stretch"`); right, an
  `st.popover` (`width="stretch"`) labelled **"Home"** when a home is set
  and **"Set home"** when none is. The two controls fill the row.
- **Inside the popover**: the caption "Home: <label> · lat, lon" (or,
  with no home, "Resolve a place under Birthplace, then set it as
  home."), the **Set as home** button (stretched; enabled only while this
  run resolved a place in range; help "Keep the place resolved under
  Birthplace as the home that Here & Now casts a chart for."), and
  **Forget home** (stretched) when a home is set.
- **Under Birthplace: nothing of this branch's.** The section's direct
  children, from its header to the chart-name box, are exactly main's —
  measured on an archive of main and pinned in a test (below).

**Which container the home controls ended in, and why.** The popover is
drawn into the row's right column *from further down the script*, after
the Birthplace block — `with _home_slot.popover(...)` at the site where
the first layout drew "Set as home" under the resolved box. Both columns
are created before the header, so the row stands at the top of the
sidebar in the DOM; each control is drawn into its column later, where
the state it needs exists: the "Here & Now" button once the preferences
have been read (the same site as before, now `_here_now_slot.button`),
the popover once this run's `lat`, `lon` and `location_query` exist. So
"Set as home" is still handled inline, at its own site, from **this
run's** resolved values — the fix round's rule, the edit-and-click
gesture still writes the place the box shows — and nothing reads
`_resolved_*` from the run before. (The alternative, drawing the popover
at the top and deferring the press's effect to the foot, would have had
the press read values resolved later in the same run, which is the same
thing with more state; the slot needs none.) The dict is built with
`float()` coordinates, checked with `home_place_is_valid`, compared with
the home in force, and remembered when it differs.

The "Here & Now" button and the popover's label were drawn or chosen
before the press was seen — the popover's label is passed when it is
created, and the press is handled inside it — so when the home has
changed the site sets `_home_changed` and the run is repeated from the
sidebar's foot (beside `_delete_now`, where every field has been drawn
and a rerun costs nothing; the flag is popped, so once). "Forget home"
and "Here & Now" keep their `on_click` callbacks, which run before the
widgets of the rerun they trigger, so after Forget the button is drawn
disabled and the label reads "Set home" at once. A rerun from sidebar
height is not available (the delete confirmation learned that: it
abandons the run before the date, time and place widgets are drawn).

AppTest sees inside a popover: it is a `Block` of type `"popover"` under
the column, its label in `proto.popover.label`, its children reachable
by `at.sidebar.button(key=...)` and `.caption` as any other block's.
No fallback to an expander was needed.

### "Here & Now"

In the top row's left column: `_here_now_slot.button("📍 Here & Now",
key="_here_and_now", width="stretch", …)`, drawn at the site under the
preferences block where the first layout drew it under the header. The
glyph is an emoji, as the sidebar's other buttons' glyphs are (📂, 🗑,
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
   hours (quarter-hours preserved: 5.5, 5.75). The offset is checked with
   `utc_offset_in_range` **before anything is written** (H5: never an
   offset outside the number_input's bounds; a clock cannot give one
   short of a broken `TZ` string): outside it the cast is refused — the
   callback returns with every box as it was and one sentence in the
   notice slot beside the picker, "This computer's clock has an offset
   outside ±14 hours, so Here & Now cast nothing.", which the next load,
   new chart, save or cast clears. (The first commit wrote Manual and the
   wall time and skipped only the offset, a wrong chart cast silently;
   the fix round made it refuse.)
5. **The moment**: `date_input_key` = `YYYY-MM-DD` of the local clock,
   `time_input_key` = `time(h, m, s)`.
6. **The place**: `manual_coords_key` = True, `manual_lat_key` /
   `manual_lon_key` = the home's floats, `loaded_location` =
   `{"label", "lat", "lon"}` so the coordinate fields show the home's name
   under the loaded-label rule rather than "Manual [lat, lon]".
7. **State**: `_loaded_without_standard` and `_record_notice` popped —
   the first is answered by the standard just written, the second
   describes fields the boxes no longer hold. `_readings_pending`, the
   "'X' was saved under other readings" question with its Open/Keep
   buttons, is **left standing**, by finding rather than by symmetry:
   the cast makes it neither false nor answered — X was saved under other
   readings still, the picker still names X, and which readings the chart
   is read under is the reader's to say, which the cast does not say. An
   edit of the date keeps the question on main too. The picker's caption
   then reads both "Edited since it was saved." and "Saved with other
   readings.", which is the truth. The picker and `last_chart` are left as they are: a loaded record
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

At the top of the sidebar, above "Nativity", one row: "📍 Here & Now"
(148 px wide at the sidebar's 300 px) and, beside it, "Set home ▾"
(96 px) — greyed button and "Set home" until a home is set. Opening "Set
home" shows "Resolve a place under Birthplace, then set it as home." and
the "Set as home" button, disabled until the green resolved-place box
holds a place. Once pressed, the row reads "📍 Here & Now" enabled and
"Home ▾"; opening "Home" shows "Home: Petoskey, MI (US) · 45.3733,
-84.9553", "Set as home" and "Forget home". Nothing else changes in the
sidebar: the nativity's boxes and the Birthplace section are main's. A
press of "Here & Now" fills the date, time, standard and coordinate boxes
and the page reads the chart of this moment; with a saved chart loaded,
the strip reads "Jason Armfield (modified) · 2026-09-17 13:03:36 ·
America/Detroit -04:00 · Petoskey, MI (US) 45.37, -84.96" and the
picker's caption says "Edited since it was saved."

## Tests

`tests/test_here_and_now_2026_09_17.py`, 48 tests, AppTest, preferences
switched on against a `tmp_path` `XDG_DATA_HOME` as `test_preferences.py`
does. A button drawn disabled takes no click under AppTest (nor in a
browser), so tests that seed a home in `session_state` do it before the
first run.

- No home: the button disabled with its help, the popover labelled "Set
  home" with its caption; "Set as home" enabled with Florence resolved,
  disabled with no atlas match and with a latitude of 91.
- The top row (layout round): the sidebar's first child is a
  `flex_container` of two `column`s, the left holding exactly the
  "📍 Here & Now" button, the right exactly one `popover`; the "Nativity"
  header is the second child. With and without a home.
- The Birthplace section is exactly main's (layout round): the direct
  children from the "Birthplace" header to the chart-name box, for the
  harness's manual pair and for Florence through the atlas, equal the
  sequence measured on an archive of main — before and after "Set as
  home" — and no "Set as home" element stands among the sidebar's direct
  children.
- "Set as home" on the atlas's Florence: the file holds
  `{"label": "Florence, 16 (IT)", "lat": 43.77925, "lon": 11.24626}` with
  float coordinates, the caption names it, the button is enabled with its
  help; the same press again leaves the file's bytes and mtime unchanged;
  "Forget home" removes it from the file and the session and disables the
  button on that run.
- The edit-and-click gesture (fix round): the city text set to "Paris"
  and the button clicked before one `run()` writes Paris's atlas label
  and coordinates, the caption names it and the top button is enabled on
  that run; a latitude set to 10.0 and clicked in one run writes
  `Manual [10.0000, …]`. Both fail on the first commit's `app.py`
  (Florence written for Paris); both pass unchanged with the popover,
  whose button is found by key.
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
- The out-of-bounds clock (fix round): `timezone_at` patched to None and
  `local_clock` to +15 — every box as it was, no `utc_offset_key`, no
  `loaded_location`, exactly the one warning, the strip still the example
  chart; a +14 clock then casts (2026-09-18, 14.0) with the warning gone.
  Fails on the first commit's `app.py` (a cast at 2026-09-18).
- The readings question (fix round): a record saved under Abu Ma'shar's
  connection rule loaded, the question standing, then Here & Now — the
  question and "Open saved readings" still drawn, `_readings_pending`
  still the record, both picker captions, the strip "Other (modified) ·
  2026-09-17 14:34:56"; "Keep current readings" answers it as before.
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
- Preview of the first layout (superseded by the layout round below) on
  the coordinator's launch entry at port 8531 (cloned data),
  1400 × 900 and 1920 × 1080, light and dark: the disabled button under
  the header at y 132 with the header at 76, its tooltip on hover; "Set
  as home" 97 px wide under the resolved box; the caption and "Forget
  home"; the cast chart on the Chart page and the strip; "Forget home"
  disabling the button on the same run. The clone's home was forgotten
  and its launch count put back to 99 before the preview was stopped.
- Full suite `-n auto`: 3731 passed, 1 skipped at the first commit; 3734
  passed, 1 skipped after the fix round; 3737 passed, 1 skipped after the
  layout round (main: 3688 passed, 1 skipped).
- Preview of the layout round on the clone at port 8531, 1400 × 900 and
  1920 × 1080, light and dark: the row at y 76 (button 148 × 40 at x 20,
  popover 96 × 40 at x 184, 16 px between), the "Nativity" header at
  y 132 against main's 76 — **the height cost is one row, 56 px, in every
  state**, with and without a home, since nothing stands under Birthplace
  any more (the first layout cost 112 px with no home and about 206 with
  one). The popover open with a home: a 295–300 px panel at y 120 holding
  the caption (two lines), "Set as home" and "Forget home" at 247 px;
  open without one: a 358 px panel with the sentence and "Set as home" at
  310 px. "Forget home" in the panel disables the button and relabels
  the popover "Set home" on the same run; "Set as home" in the panel (the
  clone's Petoskey resolved) enables it and relabels "Home" on the same
  gesture; "Here & Now" from the row casts (strip "Jason Armfield
  (modified) · 2026-09-17 13:03:36 · …"). No horizontal scroll at either
  width. The clone's home (Alanson, MI, the owner's own on the clone when
  this round began) put back and its launch count restored.

## What was left

Nothing of the brief. Two departures, stated: the sea case is Standard
time under the ocean zone rather than Manual, for the reason above (the
Manual path exists and is tested with the finder patched); and the
repeated hour of a fall-back takes Manual with the true offset, which the
brief did not ask for and which keeps the button from being refused one
hour a year.

## The fix round

From `HERE_NOW_ADVERSARIAL_REPORT_2026-09-17.md` (36 instants across DST
gaps and repeats, 25 hand-edited file shapes, the lifecycle, the live
gesture). One must-change and two cheap items, one commit.

1. **"Set as home" wrote the previous run's place.** Type a city (or a
   coordinate) and click the button without Enter: the mouse-down blurs
   the box, the blur commits the text and requests a rerun, the click
   requests another, and an `on_click` callback ran with `_resolved_*`
   from the run before the edit — live on the clone, Madrid in the box,
   "Home: Berlin" written. Now the press is handled at the button's site
   from this run's `lat`, `lon`, `location_query`, with the foot rerun
   described above keeping the top button right on the same run;
   `_resolved_label` is gone. Verified live on the clone at port 8531:
   Berlin resolved, "Madrid" typed over it with no Enter, "Set as home"
   clicked with the pane's mouse — the box "Madrid, 29 (ES)", the caption
   "Home: Madrid, 29 (ES) · 40.4165, -3.7026", the top button enabled on
   that run. Pinned by the edit-and-click tests above.
2. **The H5 guard refuses instead of casting wrong** (step 4 above).
3. **`_readings_pending` left standing**, with the reasoning in step 7
   above and the callback's own comment; tested.

### Seen in passing (main's, not this branch's)

The same staleness as item 1 exists on `main` in F02's toggle callback,
`_manual_coords_switched`: it reads `_resolved_lat`/`_resolved_lon` from
the previous run, so a city typed over and the coordinate toggle clicked
without Enter starts the fields at the previous place. Not touched here;
the "Set as home" fix — handle at the site from this run's values, rerun
from the foot — is the model if the owner wants it closed.

### Design consequences for the owner

- **Sidebar height.** After the layout round: one row of 56 px (40 + 16)
  above the "Nativity" header, in every state — the home's controls are
  inside the popover and nothing stands under Birthplace. (The first
  layout cost about 112 px with no home and about 206 with one; the
  owner's ruling replaced it.) Nothing scrolls sideways.
- After Here & Now the coordinate toggle behaves as for a loaded record
  (F02's rule): switching it off shows the city box's last text and casts
  that place at the cast time.
- A Manual offset in force before the press stays in `utc_offset_key`
  underneath a Standard cast and returns if Manual is chosen again — the
  same as loading a Standard record over a Manual box.
- An int coordinate in a hand-edited file is refused (deliberate); a
  hand-edited label is shown whole, escaped as the resolved box escapes.
- The refusal sentence of item 2 stands in `_record_notice`, the slot
  whose comment says it describes the record, not the click; it is the
  one sentence slot the sidebar has beside the picker, and the sentence
  is cleared by everything that clears that slot. If the owner would
  rather it had a slot of its own, that is a one-key change.

## The layout round

The owner's ruling on the preview of PR #78, applied in one commit:
behaviour and validation unchanged; the "Here & Now" button and a "Home"
/ "Set home" popover in one row above the Nativity header, the home's
caption, "Set as home" and "Forget home" inside the popover, and the
Birthplace section returned to exactly main's layout. The container and
the reason are in "The layout" above; the tests and the preview
measurements in their sections. `engine.py` untouched this round; the
fixture untouched; the length guards silent.
