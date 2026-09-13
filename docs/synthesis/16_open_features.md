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
| **F-2** | Small days (IX.7, 29-31): direct against houses, Lots, and the Nodes, not just the seven planets | Not built | Janus's own "Solar Return Distribution" hits house cusps, Part of Fortune, the Nodes and the Midheaven as well as the planets; IX.7, 31 licenses the extension ("everything of the planets, Lots, and houses") but only the planets' bodies and rays are wired in |
| **F-3** | Small days: fixed 59'08"/day rate vs. the Sun's real (varying) daily motion | Already decided 2026-09-10 (fixed rate) — flagged here as newly re-tested | A second Janus cross-check (Pontiac 1990) shows the same aspect sequence as ours but a day-offset that grows through the year (3 days by mid-November, 5+ by month's end) — consistent with Janus using the Sun's true motion rather than the flat average. Not a bug: the owner already chose the fixed rate over IX.7, 32's "exact" alternative. Recorded here so the choice is visible next to the evidence, not to reopen it |
| **F-4** | "Directing by Triplicities" — a standalone whole-life table of the three triplicity lords in succession | **Built 2026-09-13** (branch `triplicity-life-lords-2026-09-13`) | Keyed to the **sect light**, not the Ascendant: the life-division is stated by Sahl, *On Nativities* 2.11, 1-4 (Theophilus; fn 148: *Carmen* I.24), 2.13, 39 and 2.17, 5, all for the luminary's triplicity; nothing in hand divides the life by the Ascendant's (those are the upbringing lords, 1.29). No years shown (owner's ruling); the Ascendant rows built as a labelled off-by-default comparison (owner's ruling). `triplicity_lords_of_life()`, Timing page, before the *fardar* |

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

## F-2 — Small days: extend the target points beyond the seven planets

`pn4_small_days()` (`app.py:8545`) directs the revolution's Ascendant through the Egyptian
bounds, hitting only what `pn4_bodies_and_rays()` (`app.py:8328`) supplies as meeting points —
the seven planets' bodies and rays. Compared 2026-09-12 against Janus's "Solar Return
Distribution" for the same nativity (29 Oct 1990, Pontiac MI): Janus's list also has the
directed Ascendant conjuncting house cusps ("2nd HC", "3rd HC", ...), Part of Fortune, the
Moon's Nodes, and the Midheaven along the way, none of which our version can ever report since
they aren't in the event list it searches.

IX.7, 31 licenses exactly this: "you work like that with everything of the planets, Lots, and
houses, of whatever you want the direction of" — already the citation `_pn4_distribute()`'s own
docstring uses to justify directing points other than the Ascendant. The gap is on the *event*
side, not the *distributed point* side: bodies-and-rays needs to also carry Lots, house cusps,
and the Nodes as things the direction can meet, at least for this method.

**To build this**: extend `pn4_bodies_and_rays()` (or add a sibling event list `pn4_small_days`
merges in) to include the Lots already computed for the chart, the house cusps, the Nodes, and
the Midheaven/Ascendant themselves as body-only meeting points (rays to houses and Lots may or
may not be intended — Janus's sample only shows conjunctions to non-planet points, never
squares/trines/etc. to them, which is worth confirming against more examples before deciding
whether to add rays to them too).

## F-3 — Small days: the fixed 59'08"/day rate vs. the Sun's real motion

Already ruled on (`app.py:8521-8531`, 2026-09-10): Abu Ma'shar names two readings of IX.7, 29's
directing rate — the flat 59'08"/day average (360° in ~365.28 days) and "the exact
[form]... like the direction of the Sun every day" (IX.7, 32), i.e. the Sun's true, varying
daily motion. The owner chose the fixed rate.

Re-tested 2026-09-12 against the same Pontiac 1990 Janus data used for F-2: our engine and
Janus produce the *same sequence* of aspect hits (Venus square, Sun square, Mercury square,
Jupiter opposition, Mars trine, in that order) but Janus's dates arrive earlier, by a gap that
grows through the run — about 3 days by mid-November, 5+ by early December. That is the
signature of the Sun's real motion (faster than 59'08" in the weeks either side of perihelion,
which October-November is approaching) rather than a bug: it is consistent with Janus
implementing IX.7, 32's "exact" alternative instead of the fixed rate.

Not proposing to change the default — the fixed rate is the owner's standing choice, and the
docstring's reasoning for it stands. Logged here so the size and direction of the divergence is
on record, in case it ever bears on whether to offer the exact form as a labelled alternative
reading alongside the fixed one (as several other switches in this file already do).

## F-4 — "Directing by Triplicities": a standalone whole-life table

Janus prints a short table dividing life into three stretches, each ruled by one of a
triplicity's three lords in succession (Pontiac 1990: Venus 0-30, Moon 30-60, Mars 60-90). This
is a real technique, not a Janus invention — PN IV VI.2, 4-5 (Abū Ma'shar) names the three lords
of a triplicity and says one of them "indicated his condition at that time of his lifespan," and
`pn4_turning_triplicity_lords()` (`app.py:10076`) already identifies those three lords, correctly
ordered by sect — but only as rows beside the yearly "turning" (solar-revolution) report, keyed
to the sect light's sign (VI.2, 4, for assets) or Mars's sign (VI.2, 5, for siblings).

Checked 2026-09-13: Janus's data matches **neither** of those points for this nativity. The sect
light (Sun, Diurnal, in Scorpio/water) would give Venus-Mars-Moon; Janus prints Venus-Moon-Mars.
That sequence instead matches the **Ascendant's** triplicity (Capricorn/earth: day Venus, night
Moon, participating Mars) — a point VI.2,4 doesn't name at all. So building this as a simple
extension of VI.2,4 would cite the wrong passage. There's also no numeric age boundary anywhere
in the stated text — fn. 14's "if older, use the second or third lord" is Dykes' own editorial
gloss, and a prior decision (PN4R-4f-6, 2026-09-11) already declined to build a hard age-cutoff
from it.

Full research brief, with the citations, the Ascendant discrepancy, and what still needs
resolving before this can be built without mis-citing it: `docs/TRIPLICITY_LORDS_OF_LIFE_BRIEF_2026-09-13.md`.

**Resolved 2026-09-13.** The corpus was searched for a life-division keyed to the Ascendant's
triplicity and none exists: the Ascendant's triplicity lords are the *upbringing* lords
throughout (Sahl, *On Nativities* 1.29, 2-8; Appendix A §8-9 with fn 7; *Great Introduction*
"upbringing and survival"). The life-division itself IS stated, four times, always for the
**luminary's** triplicity:

- Sahl 2.11, 1-4 (Theophilus; fn 148: *cf. Carmen* I.24, 1-8): "If you found both of the two
  lords of the triplicity of the luminary to be strong, they indicate high rank from the
  beginning of his life to its end. And if one of the two was strong and the other weak, his
  benefit will be in the time of the strong one of them ... and the partnering lord of the
  triplicity supports them both."
- Sahl 2.13, 39 (Māshā'allāh): "the first lord of the triplicity indicates the end of the
  father's life, and the beginning of the native's life."
- Sahl 2.17, 5: "if the third lord of the triplicity was in the house of marriage, he will gain
  good fortune at the end of his lifespan."
- PN IV VI.2, 4 (already built beside the turning): "the lord of the triplicity which indicated
  his condition at that time of his lifespan."

None gives a number of years. (Sahl 2.7, 3's "thirty years" for Saturn as sect-light triplicity
overlord is Saturn's greater years, not a life-third — a false friend.) So Janus's
Venus-Moon-Mars for Pontiac 1990 is an unsourced substitution of the Ascendant for the luminary,
and its 0-30/30-60/60-90 is stated nowhere.

Owner's rulings (2026-09-13): (1) no years on the table, no 30-year option; (2) the Ascendant
rows built as a labelled comparison, off by default. Built: `_triplicity_lords_in_sect_order()`
factored out of `pn4_turning_triplicity_lords()` (whose VI.2, 4-5 behaviour and test are
unchanged); `triplicity_lords_of_life(chart_data, point)` with `LIFE_LORDS_SOURCE`,
`LIFE_LORDS_ASCENDANT_SOURCE`, `LIFE_LORDS_TIMES`; carried in `pn4_timing_bundle` as
`life_lords_rows` / `life_lords_ascendant_rows`; rendered on the Timing page's last tab before
the *fardar*, with a checkbox for the Ascendant rows. Tests: three `test_triplicity_lords_of_life_*`
in `tests/test_doctrine_fixtures.py`, the last on the Pontiac 1990 chart (sect light
Venus-Mars-Moon; Ascendant Venus-Moon-Mars).
