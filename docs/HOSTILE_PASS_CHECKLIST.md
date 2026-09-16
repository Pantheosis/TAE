# Hostile pass checklist — Traditional Astrology Engine

Run by an agent with NO build context, against the running app (a worktree server on its own
port, `XDG_DATA_HOME` pointed at a scratch copy of `~/.local/share/TraditionalAstrologyEngine/`
so the owner's real charts and preferences are never touched). The job is to falsify, not to
confirm. Every finding becomes a test that stays in `tests/` (model: `tests/test_input_state_2026_09_16.py`).

## 1. Every field, garbage and boundaries
- Date: `not-a-date`, `1240-13-01`, `1582-10-10` (the Julian/Gregorian gap), `0001-01-01`, `9999-12-31`, blank.
- Time: `24:00:00`, seconds edge, blank.
- Time standard: each of the three; manual offset ±14, ±14.25, blank.
- Place: blank; `zzzz-no-such-city`; `New York, NY`; a pasted `lat, lon` with spaces, with a trailing comma, with `91, 0`, `0, 181`, `nan, nan`; the direct-coordinate toggle on and off with a resolved place behind it; polar latitudes 66.6–90 on midsummer and midwinter dates.
- DST: a named zone at a spring-forward gap and an autumn fall-back overlap.
- Timing target: invalid text; an age of 0, 150, negative; a date before the birth date.
- Every checkbox, radio and selectbox on every page toggled once, then the page reloaded: the store keys and the preferences file must hold what a full rerun would produce.

## 2. Lifecycle, across sessions
- Save → fresh session → load: every field, the time standard, the offset, the target, identical.
- Save under an existing name; delete; New; edit a loaded chart; a chart name with quotes, `<`, `&`, a very long name, a name that is only spaces.
- A malformed `saved_charts.json`; an empty file; a file that is a JSON list; a file without write permission; a `preferences.json` with unknown keys, missing keys, wrong types.
- Two browser tabs on one server with different readings: each tab's tables must follow its own readings.

## 3. The same fact in two places
- Strip vs sidebar box vs Chart calculation table: date, time, offset, UT, place.
- Sect, day lord, hour lord, lunation: strip vs Chart vs Victors vs Timing.
- Any "Net", "Verdict", "Lean", count or score: the same number and the same word on every page that shows it; a zero must be named the same way everywhere.
- Every finding's "Not present in this chart" line: is the absence unbounded (true absence) or a finite search (say the horizon)?
- Every approximation, proxy or adopted convention: is it qualified at every place the value appears, not only where it is computed?

## 4. The shell
- With each invalid input above: the header bar, Reference and Sources must render in full; result pages show the recovery panel and name the invalid input; nothing is saved.
- Browser back/forward, reload mid-rerun, a second tab, the 900×600 window, 200% zoom, dark theme.

## 5. Provenance
- Pick five citations at random from five pages and check them against the corpus by chapter and sentence.
- Pick five help texts and check they describe the control that is actually on the page today.
- Every heading that names a source: does the table under it show only that source's rule?

## Reporting
For each finding: the exact input, what the page showed, what the file or store holds, what the right behaviour is, and a one-line reproduction under `AppTest`. Severity by consequence: a misleading stored record is critical; a lost shell or a wrong qualification is high; friction is medium.
