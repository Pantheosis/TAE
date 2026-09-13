# Open features — things to build, not doctrinal calls

Started 2026-09-12. Distinct from `13_open_decisions.md`: that file is doctrinal readings
(which citation, which orb, which emendation) each pinned to a source passage and measured
against a chart sample. This file is the other kind of open item — a feature or display the
engine doesn't have yet, where the *doctrine* isn't in question but the *build* is, or where a
concrete implementation detail (a rounding rule, a display convention) is still unresolved.

Numbered `F-N`, appended as they come up, not renumbered.

## Summary table

| # | Feature | Status | Notes |
|---|---|---|---|
| **F-1** | Calendar dates on the Fardar (Firdaria) table | Not built | Structure (lords, years, sub-period order) cross-checked exact against Janus's medieval module across three nativities; the calendar-date conversion itself is unbuilt and its rounding convention unresolved |

## F-1 — Calendar dates on the Fardar table

`pn4_fardar_sequence` / `pn4_fardar_subperiods` (`app.py`) and the Timing page's Fardar table
(`app.py:12726-12738`, the `Lord, Years, From age, To age, Sub-periods, Active` columns) only
carry fractional **ages in years**. There is no code path anywhere that turns a Fardar boundary
into an actual calendar date — Janus's own Firdaria table prints one (day/month/year) for every
major- and sub-period start.

Cross-checked 2026-09-12 against Janus's Firdaria output for three nativities (19 Nov 1982
Petoskey MI; 29 Oct 1990 Pontiac MI; 12 Oct 2030 Alanson MI):

- **The doctrine itself matches exactly**: major-period lords, years (Sun 10, Venus 8, Mercury
  13, Moon 9, Saturn 11, Jupiter 12, Mars 7, Node 3, Node 2 — summing to 75), the sect-based
  starting point (from the Sun by day, the Moon by night, descending the spheres), and the
  cyclic sub-period order within each major period all agree on all three charts.
- **Reconstructing calendar dates independently** (birth moment plus age × a mean-year length;
  also tried real calendar-year anniversaries for the major-period boundaries, sub-divided into
  true-day sevenths) gets close but not exact: against Janus's 51 printed 1982 dates, the best
  variant tried (calendar anniversaries, floor-rounded sevenths) matched 36/51, with every
  remaining difference exactly ±1 day — never more. That pattern points to a rounding/truncation
  convention difference in how a fractional day is floored to a calendar date, not a structural
  error, but the exact convention Janus uses wasn't pinned down.

**To build this**: add a Date column to the Fardar table (both major- and sub-period rows), and
settle (a) the year-length/anniversary convention for turning an age into a date, and (b) the
rounding rule for a fractional day, ideally re-tested against Janus's dates for more than one
chart before calling it matched. ±1 day may simply be an acceptable tolerance to state
explicitly rather than chase further — worth an owner ruling either way.
