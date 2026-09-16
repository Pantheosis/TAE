# Traditional Astrology Engine

A study companion for traditional natal astrology: cast a chart, then check, table by table,
what the texts say about it. The rules it applies come from the course's two books in Benjamin
Dykes's translations — Sahl b. Bishr, *The Astrology of Sahl b. Bishr*, vol. I, and Abū Ma'shar,
*On the Revolutions of the Years of Nativities* (*Persian Nativities* IV) — with his *Great
Introduction to the Science of the Judgments of the Stars* as the supplement, and a handful of
witness texts (Rhetorius, Firmicus, Dykes's *Introductions*, the other *Persian Nativities*
volumes, Valens, Morin) where the course texts leave a question open; every one of them, with
what it supplies and how it is cited, is in [docs/REFERENCES.md](docs/REFERENCES.md). Every rule a
page applies names the sentence it comes from; where a text leaves something open, the page
says so and shows the reading it made. The judgment of the chart is the astrologer's.

## Download

Portable builds for Windows and macOS are on the
[Releases](https://github.com/Pantheosis/TAE/releases) page: unzip, run
`TraditionalAstrologyEngine`. No install, no internet — place lookup uses a bundled atlas and
the planets run on the built-in Moshier ephemeris. Saved charts live in your user data folder
and survive updates.

## What it computes

**Part 1 — the nativity**

- **Chart** — the wheel (square, or wide with a positions panel; SVG download), positions,
  the Alchabitius divisions beside the whole-sign places, solar phase, Sahl's sign categories,
  the special degrees, the prenatal lunation, sect, the lords of the day and hour.
- **Dignities and places** — the essential dignities at each planet's own degree, sect and
  domain, planets in the places and the lords of the places with their delineations.
- **Findings** — the delineations read off the cast chart: the fetus's stay, the Moon on the
  third day, Sahl's seven classes of fortune and livelihood, and, under the fuller reading
  depth, Mars by sect, the Moon's phases, Mercury's phase, Rhetorius's afflictions, Morin's
  aspect rules and the places harming the eyesight. Each cites its sentence; none is scored.
- **Configurations** — Sahl's connections, receptions and their refusals, the handing-over,
  prevented connections, strength and weakness, the corruption of the Moon; Abū Ma'shar's
  planetary conditions (Gr. Intr. VII) beside them, and the forward-looking conditions
  (revoking, resistance, escape) simulated against the ephemeris.
- **Lots** — the classical Lots and Sahl's topical Lots, each with its formula and its
  source; where Sahl gives a Lot twice with different formulas, both are shown.
- **Lunation and victors** — the prenatal syzygy, its lords and its governor (Sahl 1.7), the
  victor of the chart.

**Part 2 — prediction** (Abū Ma'shar, *PN* IV, with the releaser and house-master from Sahl)

- **Timing** — the revolution of the year and of the month with their wheels; profections;
  the distributions from the Ascendant and the meridian through the bounds; the lord of the
  year and the governor with their testimonies; the releaser, the house-master and its years;
  the fardārs, the ages, the days and hours; what the book does not settle, listed rather than
  filled in.

**Reference** — the dignity tables, the bounds, the planetary years, the ages; and *Sources
and readings*, which lists every doctrinal switch in force and the readings the app makes.

## Running from source

```bash
pip install -r requirements.txt
streamlit run app.py
```

Python 3.14 is what the pins were resolved on and what the tests and the desktop build use.
The tests (`python -m pytest -q`, about ten minutes) pin every rule to a fixture drawn from
the texts' own worked figures, with a near-miss beside each.

## Building the desktop app

To build the portable app yourself, see [`docs/BUILD_NOTES.md`](docs/BUILD_NOTES.md)
(PyInstaller, one folder per platform).

## Repository

| Path | What |
|---|---|
| `engine.py` | the engine: the chart, the dignities, the evaluators, the lots, the timing, and the pictures drawn from them |
| `app.py` | the Streamlit pages, after the marker `# 4. STREAMLIT UI INTEGRATION`; it takes the engine whole and is the file to run |
| `tests/` | the suite; `tests/fixtures/tables.json` pins which tables each page renders |
| `ephe/` | the Swiss Ephemeris fixed-star catalogue the app ships (AGPL-3.0; see its README) |
| `atlas.db` | the offline place lookup |
| `desktop_launcher.py`, `build.spec` | the desktop wrapper and the PyInstaller build |
| `docs/` | build and release notes, the build logs and audits, and `synthesis/`, the working notes the rules were adjudicated from |

The texts themselves are not in this repository: they are copyrighted translations and are
worked from privately. The pages cite them by volume, chapter and sentence so that anyone
with the books can check every rule.

## Licence

AGPL-3.0 — see [`LICENSE`](LICENSE). The fixed-star catalogue in `ephe/` is Swiss Ephemeris
data redistributed under the same licence. `glyph_font.py` embeds a 26-glyph subset of Google's
Noto Sans Symbols and Noto Sans Symbols 2 (SIL Open Font License 1.1) as base64 WOFF2, so every
picture the app draws carries its own zodiac and planet glyphs regardless of what is installed
on the viewing machine — see [`fonts/OFL.txt`](fonts/OFL.txt) for the licence notice and
`docs/UI_CHANGES_2026-09-15_symbol_font.md` for what the subset does and does not cover.
