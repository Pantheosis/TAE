# The saved-chart lifecycle -- 2026-09-16

Branch `record-lifecycle-2026-09-16` off `main` at `ab497fd`. Finding F04 of
the independent UI review of 2026-09-16, with its own reproductions E05 and
E06 as the acceptance cases. It builds on the branch merged as PR #52
(`docs/INPUT_STATE_2026-09-16.md`): the sidebar is a draft, the chart is a
committed input (`chart_ok`, `chart_error`), the pages are module-level, and
Save already refuses an invalid draft.

## What was asked

The review found a record's identity, its collisions and its recovery all
ambiguous or destructive at once:

- a first save reported success while the strip still said **Unsaved chart**
  and the picker still held only **-- New Chart --**, its options having been
  built before the Save button ran;
- an edited record kept its saved name with nothing to say the two had
  parted;
- **-- New Chart --** kept the edited date and place -- a deselection, not a
  new chart;
- saving an existing name replaced the record with no collision review, and
  the bin removed a record on the press, with no confirmation and no undo;
- a malformed store showed an empty picker with no warning, and the next
  save destroyed the only copy of the bytes;
- and the in-memory mapping was mutated before the disk was written, so a
  failed write left the session holding a record the file did not have.

No doctrine, no evaluator, no page text beyond the seven sentences below.
`tests/fixtures/tables.json` is unchanged (`git diff main` on it is empty).

## The seven items

**1. A save selects and names the record.** A successful write leaves the
name in `_select_after_rerun` and calls `st.rerun()`; the next run copies it
into `chart_picker` *before* the picker is drawn, because a widget's key
cannot be assigned once the widget exists (Streamlit 1.62 raises
`StreamlitAPIException` outright). The picker then lists and selects the
record and the strip names it. `_apply_selected_chart` is the picker's
`on_change` and does not fire for a selection made this way, which is right:
the fields already hold the values that were written. The success message
`Saved '<name>'.` rides over the rerun in `_saved_flash` so that it is still
beside the picker that now names the record.

**2. Modified.** `_chart_record()` is the committed input as a record -- the
same ten fields Save writes -- and `_records_match()` compares it with the
selected record. Numbers are compared as floats to four decimals (the
coordinates are written to four places, and JSON reads a whole number back
as an int). A field the **stored** record does not carry is not compared at
all: a record written before the time standard or the target was stored with
a chart has not been "edited since it was saved" for lacking them, and must
not be accused of it. When the picker names a record and the fields have
moved, the strip's first part reads `<name> (modified)` and a caption under
the picker reads **Edited since it was saved.** The harness leaves the
picker at `-- New Chart --`, so every other test's strip still reads
*Unsaved chart*.

**3. New clears the form.** Selecting `-- New Chart --` runs
`_new_chart_form()` inside the picker's own `on_change`: the eight sidebar
keys go back to `EXAMPLE_CHART` (the 1240-05-23 14:30 LMT Florence chart,
now the one place those defaults are written, the widgets' own `setdefault`
calls reading them from it), the target keys are dropped so the Timing
page's `setdefault` seeds them afresh, and `loaded_location` goes with them.

*The reading taken:* it clears **the form and nothing else**. The
preferences file is not touched and `last_chart` is not forgotten, so the
next launch still opens on the last chart saved or loaded. A new chart is an
unsaved draft; it has nothing for a later session to be opened on, and
forgetting the last chart would make "I want to start a fresh nativity" also
mean "and lose where I was", which is not what the reader asked for.

**4. A same-name save asks before replacing.** If the name exists and the
stored record matches the input, `'<name>' is already saved as it is.` and
nothing is written. If it exists and differs, the first press writes
**nothing**: it sets `_replace_pending` (with the record it was asked
about), and under the Save button stands
`'<name>' exists. Replace it?` with **Replace** and **Keep both** in a row.
Replace overwrites and selects; Keep both writes `<name> (2)` -- the first
free `(n)` -- and selects that. The question stands only while the name in
the box and the nativity in hand are the ones it was asked about: any other
change in the sidebar rewrites one or the other and the question goes with
it.

**5. Delete confirms.** The bin sets `_delete_pending` and the sidebar shows
`Delete '<name>'?` with **Delete** and **Keep**. Keep clears the flag;
Delete removes the record, writes, forgets `last_chart` if it pointed there
(as before), resets the picker to `-- New Chart --` and reruns.

One thing the browser taught this branch, and the reason the code is shaped
as it is: **a rerun from beside the picker throws the sidebar's fields
away.** `st.rerun()` there abandons the run before the date, time and place
widgets are drawn, and Streamlit discards the state of a widget a run did
not draw -- so the boxes came back holding the example nativity. The
question therefore lives in a placeholder (`delete_box`) that **Keep** can
clear without a rerun, and **Delete** only records what was asked
(`_delete_now`); the writing and the rerun happen at the foot of the
sidebar, where every field has been drawn. Two tests pin it: after Keep and
after Delete the boxes still hold the nativity they held.

**6. An unreadable store is preserved, never overwritten.** In `engine.py`,
`load_saved_charts()` copies a store it cannot read beside itself as
`saved_charts.json.unreadable-<YYYYMMDD-HHMMSS>` before returning `{}`, and
leaves the copy's name in the module-level `LAST_STORE_ERROR`
(a module name, not a second return value, so the public signature the
harness's callers use is untouched). The same bytes are never copied twice
-- a reader who opens the app repeatedly against one broken file gets one
copy, not one per launch -- and two different wrecks inside one second each
keep their own. The sidebar says once per session: `Saved charts could not
be read. The original file was kept as <filename>.` Saving afterwards writes
a fresh store, which is now safe.

**7. In-memory state follows disk success.** `_store_chart()` builds a copy
of the mapping, writes it, and only then assigns it into
`st.session_state["saved_charts"]`, remembers `last_chart` and selects the
record. The delete does the same with the remaining mapping. A write that
returns False leaves the session exactly as it was, under the error the app
already printed.

## Engine functions changed

`engine.py`, section 0 only, nothing doctrinal:

- `load_saved_charts()` -- resets `LAST_STORE_ERROR`, and on an unreadable
  store preserves the bytes and records the copy's name before returning
  `{}`;
- `_preserve_unreadable_store()` -- new helper (the copy, once per content);
- `LAST_STORE_ERROR` -- new module-level name.

`_read_chart_mapping()` and `write_saved_charts()` are unchanged; the
signature of `load_saved_charts()` is unchanged, which is what
`tests/test_doctrine_fixtures.py` calls it by.

## What the browser showed (port 8524, this worktree)

Run with `XDG_DATA_HOME` pointed at a scratch directory holding a **copy**
of the owner's `saved_charts.json` and `preferences.json`; the real
directory was never on the path. Input was DOM-driven (the pane's own key
events did not commit a Streamlit text box).

- It opened on **Jason Armfield** with no modified mark. Editing the date to
  1982-11-20 gave **"Jason Armfield (modified) · 1982-11-20 11:44:00 ·
  America/Detroit -05:00 · Petoskey, MI (US) 45.37, -84.96"** and *Edited
  since it was saved.* under the picker.
- **-- New Chart --** put back 1240-05-23, 14:30:00, LMT, the coordinate
  toggle off and *Florence* in the search box, resolving to Florence, 16
  (IT); the strip read **Unsaved chart · 1240-05-23 14:30:00 · LMT
  +00:44:59 · Florence, 16 (IT) 43.78, 11.25**.
- Saving **Live Check A**: *Saved 'Live Check A'.* above the picker, the
  picker on the name, the strip and the wheel's hub naming it -- all in the
  one interaction.
- Pressing Save again unchanged: *'Live Check A' is already saved as it is.*
  and the file untouched.
- Date to 1240-05-24, Save: *'Live Check A' exists. Replace it?* with
  **Replace** and **Keep both**, and the file still holding 1240-05-23.
  **Keep both** wrote **Live Check A (2)** and selected it, the first record
  standing. Date to 1240-05-25, Save, **Replace**: the record overwritten in
  place, still three records, the picker back on **Live Check A**.
- The bin: **Delete 'Live Check B'?** with **Delete** and **Keep**. Keep
  left the record and the boxes exactly as they were; Delete removed it,
  dropped `last_chart`, reset the picker to **-- New Chart --** and left the
  nativity in the boxes (1240-06-01) where it was.
- Malformed bytes into the scratch store, reload: **"Saved charts could not
  be read. The original file was kept as
  saved_charts.json.unreadable-20260915-230811."**, the picker holding
  nothing but `-- New Chart --`. Saving **After the wreck** wrote a fresh
  store with that one record, and the recovery file still held the original
  48 bytes.

The owner's own directory before and after, unchanged:

| file | sha256 |
|---|---|
| `saved_charts.json` | `dd817c155cb23a2cbb1d8b79b1e13d7fc33f798d6bce6c9290d211c924fd921d` |
| `preferences.json` | `4070389306f868fe8cabd5c18c9a244b35b8361101d61a99326a748a32bf1519` |

Both hashes are identical before and after the check, and neither file's
mtime moved.

## What the tests pin

`tests/test_record_lifecycle_2026_09_16.py`, 16 tests:

| Reproduction | What is pinned |
|---|---|
| E05, item 1 | after the rerun the picker lists and holds the name, `chart_picker` is the name, the strip's first part is the name, and the record is on disk |
| E05, item 2 | `<name> (modified)` and the caption appear on an edit and go on an edit back; a record compared on its own fields; the harness's picker stays at `-- New Chart --` |
| E05, item 3 | every sidebar key back to the example nativity, `loaded_location` gone, the strip *Unsaved chart*, the record itself untouched |
| E05, item 4 | the info message and an unchanged file; the warning, the two buttons and an unchanged file on the first press; Replace overwrites and selects; Keep both writes `(2)` then `(3)` and selects it; another sidebar change clears the question |
| E05, item 5 | the bin's warning and two buttons with the file unchanged; Keep leaves record, file and **boxes** alone; Delete removes the record, resets the picker and leaves the boxes alone |
| E06, item 6 | the sidebar error naming the recovery file, the file holding the original bytes, an empty picker; a fresh store after the next save with the bytes still beside it; the message shown once per session; one copy per content, two for two wrecks, and `LAST_STORE_ERROR` back to None on a readable store |
| item 7 | a write that fails leaves `st.session_state["saved_charts"]` as it was, under the existing error, with no file written -- for the save and for the delete |

`tests/test_chart_input.py` passes unchanged.

## Two existing tests edited, and why

- `tests/test_preferences.py::test_the_last_chart_loaded_is_the_chart_a_fresh_session_opens_on`
  clicked the bin once and asserted `last_chart` was forgotten. The bin asks
  first now, so the test clicks the confirmation's **Delete** as well. Its
  subject -- what the preferences file does when a record goes -- is
  unchanged, and nothing else in the file moved.
- `tests/test_input_state_2026_09_16.py::test_the_page_functions_are_mains_own_one_guard_line_apart`
  **was already failing on `main`**, before this branch touched anything
  (checked with a pristine `app.py` at `ab497fd`): it compares each page
  function with main's copy after dropping the F05 guard line from ours, and
  since that branch merged, main's copy carries the guard and F17's line
  too. Both sides are now normalised, so the test makes the comparison it
  was written to make and still fails the moment a later branch edits a page
  function.

Full suite: **2479 passed, 1 skipped, 6 xfailed**.

## What was not done

F03 (the method profile in a saved record), F16's Duplicate / Save-as
vocabulary and F18 (the wording of the location and time controls) are
untouched by design; so is recoverable trash for deleted records -- the
review offered "recoverable trash **or** confirmation", and this branch
builds the confirmation.
