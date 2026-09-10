# UI changes 2026-09-10 — chart input, the charts drawn, direction strips

Branch `ui-2026-09-10` off `main` at `05b8746`. Brief:
`consolidated_texts/process/UI_CHART_INPUT_BRIEF.md`; the evaluation that reshaped it, with the
review of PN IV's own figures: `consolidated_texts/process/UI_CHART_INPUT_EVALUATION_2026-09-10.md`.
Commits, each by pathspec: `6b3f664` (input), `976b6a7` (caption + Figure 22 oracle), `6ad3260`
(the pictures), `4c89364` (this note), and the second pass below.

## What was asked

A way to enter a nativity that a person can use, a target for the timing methods settable as an age,
and pictures of what the engine computes and never drew: the revolution of the year, the revolution
of the month, the image of the revolution of I.6, and the four distributions.

## What was built

**Input.** The time standard is saved with a chart and restored on load — the defect that started the
work: the owner's reference nativity (Petoskey 1982, recorded EST) loaded at LMT, forty minutes wrong.
Entries saved before the field existed are flagged on load. A third standard, a manual UTC offset.
The date stays typed (a calendar is the wrong control for 1240) but no longer stops the script when
malformed; the calendar in force is named; time to the second; the resolved offset and UT sit in a box
directly under the standard; one place box that also takes a typed "latitude, longitude". **The target
of the Timing page lives at the top of that page**, as an age (the n-th birthday) or a date, the other
read back beside it, remembered across pages, saved with the chart. Harness keys unchanged.

**Pictures**, all pure functions in the engine half, all downloadable as SVG:

| View (Timing page) | What | Source |
|---|---|---|
| Year | the revolution alone | Figures 4, 26 |
| Year over root | the image of the revolution: root and revolution on one zodiac, the sign of the year shaded, the profection a dashed arc, the distribution a solid arc to the degree reached now with its bound tinted, the terminal point marked, I.6, 6's time lords lettered | I.6, 3–6; Figure 51, fn 33; Figures 5, 27; Figures 2, 65 |
| Month over year and root | a tri-wheel, the sign of the month outlined | IX.3, 4–8; Figures 39, 109, fn 58 |
| Month | the month's revolution alone | IX.3, 2 |
| Profection | the natal wheel with the sign of the year and the sign of the month | Figures 3, 15, 33 |

Plus a **direction strip** above each of the four distribution tables, an **Egyptian-bounds ring** on
every wheel including the Chart page's (a toggle, on by default), and a **Date column** in the four
distribution tables (Figure 22's shape).

## Departures from the brief, measured

1. **Dykes' wheel order is the default, Abu Ma'shar's the alternative.** The brief prescribed the
   revolution inside. Every bi-wheel in the book but Figure 51 puts the nativity inside, and p. 12 says
   why. A control offers both.
2. **The month is a tri-wheel**, not a lone wheel: IX.3, 4–6 and Figures 39/109. The lone wheel is
   still a view.
3. **Typed date, not a picker.** See the evaluation, A.1.
4. **SVG download only.** PNG needs cairosvg (not installed, native cairo, a desktop-build burden).
5. **One wheel block with a view selector**, not three stacked wheels at the top of a twenty-section
   page.
6. **The default point set is Dykes' p. 12 set**; the 35 Lots, 98 rays and 38 twelfth-parts are
   toggles. The inventory table stays the authority and the test holds the picture to it.
7. **The Date column's year is 365.2425 days from the moment in UT**, not 365.25 and not local civil
   time: measured against Figure 22's eight printed dates, only that construction reproduces all eight.

## What the browser showed

At 1280×720 on :8501 (the owner's own server, hot-reloading): the sidebar reads Nativity → Date →
Time → Time standard with its offset box → Birthplace → save; the Timing page opens with the target
control, Age 42 on the 1240 chart gives 1282-05-23 and the revolution of 1282-05-23 17:18 UT; the
wheel block renders with its five views and toggles, the wheel at 560 px square, the Wide layout
stretched, a download button under it; the strips run the page width above their tables. The
pictures themselves were also rasterised and read at 1400 px on the reference nativity: the
bi-wheel's Scorpio stellium in both rings reads, the tri-wheel is legible at that size and not at
560 px (nor is Figure 109 on the page), the bounds ring's lord glyphs read on the natal wheel.

**Lesson for the next session:** a number input in Streamlit applies on Enter or on blur; the
preview browser's Return key did not always land, Tab did. And the preview pane, once hidden, cannot
scroll or screenshot; rasterise the SVG with `rsvg-convert` and read the PNG instead.

## Tests

`tests/test_chart_input.py` (25), `tests/test_revolution_wheels.py` (76), the Figure 22 oracle in
`tests/test_doctrine_fixtures.py`. `tests/fixtures/tables.json`: thirty lines changed, all the same
four tables gaining `Date`; nothing removed. Full suite after the build: 2649 passed, 0 failed, 0 skipped, 10 min 22 s, with the root venv.

## Second pass, same day: chapters

The owner, reading the page: the density is impressive and does not lend itself to easy access; the
strips sit logically beside their tables but are far down; too many radio buttons up top. Built:

- **The Timing page in five tabs**, in the page's own order — *The revolution* (the target stays above
  the tabs, since it governs everything; then the revolution table, the charts drawn, the I.6
  inventory, the I.7 checklist), *Indicators of the year*, *Distributions* (the three strips and their
  tables, III.2), *Days and months* (small days, mighty days, the nine methods, and the seven monthly
  indicators, moved up from below the fardar to sit with the days), *Fardar, ages and reference
  tables*. The selected tab is a reading: it survives navigation (`_timing_tab`), and a click reruns
  the script so the store can follow it. The two closing expanders stay at the foot, outside the tabs.
- **The wheel controls decluttered**: the view is a selectbox, the layout stays a two-way radio, and
  the order, bounds, Lots, rays and twelfth-parts live in an *Options* popover.
- No table renamed; one section moved (the monthly indicators); `tables.json` unchanged — the harness
  walks tab contents, so the fixture sees the same multiset.
