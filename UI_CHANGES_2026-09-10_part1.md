# UI changes 2026-09-10, second brief — the Part 1 pages, the gate, persistence

Branch `ui-part1-2026-09-10` off `main` at `3ab68eb`, built in a **git worktree**
(`Executable_ui/`) because a second session was building the releaser and house-master,
uncommitted, in the shared `Executable/` tree at the same time. Review that decided the work:
`consolidated_texts/process/UI_REVIEW_2026-09-10.md`; the owner accepted all five of its decisions
(retire the gate, tag now, depth control on the Sources page, auto-load the last chart, a Reference
tables page). Commits by pathspec, after rebasing onto `e07344d` (the other session's releaser and house-master):
`fc04ac3` (preferences), `a546df1` (sections, gate, Reference tables), `4719606` (Configurations
chapters and the reading depth), `22e4216` (the tab fix), `74f5b68` and `8b9a05d` (the citation
convention), and this note.

## What was asked

The "Show material through" gate hid the Lesson 5 warm-up material (the planets and their places,
which is the Dignities page) from a student who applied it strictly, and it forgot itself every
session. Review the rest of the UI and recommend.

## What was built

1. **Preferences across runs.** Every doctrinal reading and display choice lives in
   `preferences.json` beside the saved charts (same per-user directory the packaged build uses),
   written through `_persist()` and read once per session into the store keys nothing has seeded.
   The **last chart loaded is the chart a fresh session opens on**; deleting it forgets it. The
   Sources page, now **Sources and readings**, lists every reading, its value, the course default
   and where it is set, with a **reset** button; a Part 1 page whose reading is off its default says
   so in one line under its header. Harness: `ALMUTEN_NO_PREFERENCES=1` so tests neither read a real
   file nor leak into each other; the preferences tests lift it against a tmp path.
2. **Navigation in three sections, nothing hidden.** Part 1: the nativity · Part 2: prediction ·
   Reference. The gate is gone; the lesson captions under each page header stay.
3. **Reference tables** — the app's Handy Tables, one static page reading no chart: dignities by
   sign (with the standard exaltation degrees, printed only here), the Egyptian bounds, the orders
   of the dignities and the good places (moved from a Chart page expander), the planetary years
   with the fardar period (display only, registered with the D-3 control), the Ages of Man.
4. **Configurations in four chapters** — Aspects and connections · Handing over and reception ·
   Prevented connections · Strength and weakness — with the connection rule and the fitting
   infortune above them. The three-way view control is gone.
5. **The reading depth** (Sources page, persisted): *Course text* keeps Abu Ma'shar's tables in a
   fifth chapter of their own and the Dignities page's supplementary expanders closed; *Course text
   and supplement* lays his tables beside Sahl's on the same topic, each group in his own bordered
   block so the author separation stands, and opens those expanders.

## Departures from the review, measured

- **The depth does less than the review imagined, and that is right.** On inspection the
  supplement is already folded structurally almost everywhere (expanders, the Configurations tab),
  so the depth's real work is the interleaving on Configurations and the expanders on Dignities.
  The Rhetorius/PN4 readings are course material (the Reference Guide cites them for the warm-ups)
  and stay open under either depth.
- **The Chart page keeps one table from its old expander** — the sign categories of *this chart's*
  points read the chart and belong with it; only the two static tables moved. The expander is
  renamed to say what it now holds.
- **Timing's own reference tab stays.** The directing units and ladder are Part 2 material and were
  not duplicated onto the Reference page.

## Fixture and harness

`tables.json` changed three times, each read line by line: the Sources page gains *Readings in
force*; the Chart page loses the two static tables (they were keyed under the preceding subheader)
and the Reference page gains six; the three Configurations view slots collapse into one whose
content equals the old *Both* slot on every chart (checked by a script before committing). The
matrix now runs the switch cross-product once and every single-switch alternative under both
depths. `reference_planetary_years_rows` was added to `D3_GRANT_READERS` and `D3_FARDAR_READERS`
with its reason.

## What the browser showed

On the worktree's own server (:8511, launch config `almuten-ui-worktree`): the sidebar opens with the
three sections and no gate; Configurations shows the five chapters under *Course text* and four
under *Course text and supplement*, switched live from the Sources page and back; the Reference page
prints the dignities table with the exaltation degrees and the faces; Sources shows the readings
table with no row differing. After the live switch the real `preferences.json` existed with the
depth in it — the first time this app has remembered anything between runs.

**Lesson recorded in memory:** check `git diff HEAD --stat` before the first edit in the shared
tree; another session's uncommitted work was interleaved in `app.py`, and the fixture regeneration
picked up its tables. My step-A edits were kept as reversible anchor-based operations, lifted out of
the shared file exactly, and re-applied in the worktree. Note that the shared tree's
`tests/fixtures/tables.json` and `tests/conftest.py` were restored to `HEAD` in the process; the
other session will need to regenerate the fixture when its tables are final.

## Same day, later: two things the owner noticed

**The second-click bug.** Every Timing chapter took two clicks: the tab control's `default` was
read from the store key, which `_persist` updates only after the widget renders, so on the rerun a
click causes the widget already held the new tab while the default still said the old one, and the
frontend snapped back. Both tab controls (Timing, Configurations) now read the widget key first
through `_reading()`, like every other reading. Verified live: one click selects. A test seeds
widget = new, store = old and holds the clicked tab.

**The citation convention.** Most citations were written before Persian Nativities IV joined the
corpus, when "Abu Ma'shar VII.6" could only mean the Great Introduction. Both of his volumes have a
Book VII, so the author's name alone confounds — the citation test itself could not tell them
apart. Rule now: **a locator names its volume, never the author alone** — `Gr. Intr. VII.6, 27`,
`PN IV IX.1, 26-34`; Sahl's works were already named; the author's name stays in prose. The Timing
page keeps its stated page-wide rule (bare Book.chapter for PN IV). Applied by a deterministic,
idempotent script (`cite_ops.py` in the session scratchpad; the rule is recorded in memory), 63
lines; two option values renamed with a preferences migration; two table headings renamed and the
fixture follows; the Sources page states the convention. **Recommended follow-up, not done:** tag
the Timing page's PN IV locators too, now that Sahl's *On Nativities* material has joined that page
(the releaser and house-master) — a separate pass over the other session's region once it is quiet.

**The shared-tree incident.** My branch switches in `Executable/` (creating the branch there, then
checking main back out) flipped the other session's working tree twice mid-suite and, when I
restored `tables.json` to HEAD to lift my edits out, reverted its fixture. Everything of mine now
lives in the worktree; the branch was rebased cleanly onto `e07344d`; the convention script found
no author-only locators in the other session's text. Lesson recorded in memory.
