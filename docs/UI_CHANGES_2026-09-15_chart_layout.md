# UI changes 2026-09-15 — the wheel at centre stage on the Chart page

Branch `chart-centre-stage-2026-09-15` off `main` at `a7b5ce3`. The Chart page's own layout:
the wheel, its controls, the introduction, and the header metrics row that stood under them.

## What was asked

The owner's ruling. **The wheel takes centre stage on the Chart page**: the wheel centred, the
controls in one row beneath it, the three introductory paragraphs beneath those, then the rest
of the page as it was. **The header metrics row goes**, and its lunation joins the chart strip.
**The three paragraphs are reworded**, and the wording given is the text, verbatim.

Behind it, the shape the page had grown into. The wheel sat in the left half of a `[1, 1]`
split at 400 px, with the four controls and the three sentences stacked in the right half, and
under both a row of four `st.metric`s — the prenatal lunation, the sect, the lord of the day,
the lord of the hour. Three of those four had been in the chart strip since the strip was
built, so the metrics row was mostly a second printing of the line directly above it; and the
wheel, which is what the page is for, had half the page and a quarter of its width.

## What was built

### The square layout

The wheel is drawn in the middle column of `st.columns([1, 2, 1])` at `width=560`. `st.image`
draws at the left edge of whatever holds it, so a centred picture needs a container narrower
than the page and centred in it; `[1, 2, 1]` is the narrowest of those that leaves 560 px of
room at the window widths the app is read at. The wheel's viewBox is `0 0 1000 1000`, square,
so 560 px of width is 560 px of height, and nothing about the picture changes but its scale:
at 400 px the minute figures beside a planet were at the edge of legibility, and at 560 they
are not.

The wide layout is unchanged in substance — `st.image(svg_wide, width='stretch')`, the
positions panel drawn inside the picture, the full page width, scrolling.

### One row of controls, under the wheel

`_layout_control()` keeps everything it did and lays it out differently: the four controls now
sit in `st.columns([2, 1, 1, 1.4], vertical_alignment="bottom")` in the order the ruling gives
them — the Wheel layout radio (horizontal, as it always was), the Bounds ring checkbox, the
Dark wheel checkbox, the Download button. The feet are aligned rather than the tops, so the
radio's row of options, the two checkbox rows and the button sit on one line; aligned at the
top they fall at three heights, because a radio carries its label and its options and a button
carries neither.

The radio's help text said "the wheel beside the controls and the introduction, the header
metrics under it", which describes a page that no longer exists; it now says "the wheel
centred, with the controls and the introduction beneath it". That is the only page string
changed that the owner did not dictate, and it is changed because it had become false.

`_layout_control()` is called once, after the wheel, for both layouts — it used to be called
above the wide wheel and beside the square one. **The read-before-draw stays**: the layout is
still taken from `st.session_state.get("wheel_layout", ...get("_wheel_layout", ...))` before
the control renders. It was done that way so the control could sit beside the wheel; it is
needed now because the control sits *under* the wheel, and the page must know which of the two
wheels to draw before the radio that chooses it has rendered. The widget key holds the new
value from the start of the rerun a click causes, so a click on Wide draws the wide wheel on
that same rerun.

The circumpolar warning — the Lord of the Hour that is not a temporal hour — is unchanged to
the word and sits directly under the controls row, which is where it landed when the metrics
row it used to follow was removed.

### The three sentences

Three `st.caption` calls, full width, one sentence each, in both layouts. Wide used to join
them with hard breaks into one caption and Square printed them separately; the two now read
alike. The asterisk italics are Streamlit markdown in a caption, exactly as the old tuple wrote
them. The text, verbatim as ruled:

> A TNAC study companion: cast the chart by hand, then check it here, table by table, against
> what the texts say.

> The texts are *The Astrology of Sahl b. Bishr*, vol. I, and Abu Ma'shar's *On the Revolutions
> of the Years of Nativities* (*Persian Nativities* IV), in Benjamin Dykes's translations, with
> his *Great Introduction* as the supplement. Every rule applied on a page names its sentence.

> Enter or load a nativity in the sidebar. Part 1 sets out what the chart contains, Part 2 what
> the year holds; the reference tables and the sources close the page list. The judgment is the
> astrologer's.

Then `Calculation` and the whole of the rest of the page, untouched.

### The metrics row, and where its lunation went

The `hdr1..hdr4` `st.columns([1.5, 1, 1, 1])` block, its four `st.metric` calls and the caption
under the first are gone. The Chart page renders no metric at all now.

Sect, the lord of the day and the lord of the hour were already in the chart strip. The
prenatal lunation was not, and it is the one thing the row said that the strip did not, so the
strip gained one part after the sect: the first word of `event_label` and the word "lunation".
The label is `Conjunctional (New Moon)` or `Preventional (Full Moon)`, and the first word is
the whole of the answer; the degree the syzygy falls in and the house it falls in — which the
old caption printed under the metric — stay on the Lunation and victors page, whose syzygy
table gives them in full with the rest of that doctrine.

The strip, on every page, for the harness's chart:

    Unsaved chart · 1240-05-23 14:30:00 · LMT +00:44:59 · 43.78, 11.25 · Diurnal ·
    Conjunctional lunation · Day lord Mercury · Hour lord Mars

## What the browser showed

**Nothing: the live check could not be run, and this is the one thing the brief asked for that
is not here.** The preview tools resolve `.claude/launch.json` from the shared checkout at
`Executable/`, not from the worktree, and a worktree-isolated agent may not write to the shared
checkout; a launch configuration for port 8516 was written in the worktree's own
`.claude/launch.json`, where the tool does not look for it, and starting the server any other
way is not available either. Nothing was measured in a browser, so **no wheel-foot-against-fold
numbers were taken at 1400×900 or at 1280×720**, and the one open question — how far the
560 px wheel's foot falls below the fold at 1280×720 — is unanswered. Running the app on 8516
from this worktree and reading `img.getBoundingClientRect().bottom` against
`window.innerHeight` on the Chart page is what would close it.

What could be checked without a browser was checked.

**The picture at its new size.** The square wheel was rendered from this branch's engine for the
harness's chart and rasterised with `rsvg-convert` at 560 px. It is 560×560: the viewBox is
`0 0 1000 1000` and `st.image(width=560)` scales a square to a square, so the wheel occupies
exactly 560 px of page height, 160 px more than it did. At that size the sign glyphs, the
degree and minute figures beside each planet, the Alchabitius cusp numbers and the retrograde
marks are all legible, which at 400 px the minutes were not.

**The arrangement, from the rendered page.** `AppTest` renders the real element tree, and the
Chart page's children come out in the ruled order: the header, the strip caption, a block of
three columns whose middle one holds the image and whose outer two are empty, a block of four
columns holding the radio, the two checkboxes and the download button in that order, then the
three captions, then the `Calculation` subheader. No metric anywhere on the page, at either
layout and at either reading depth. The circumpolar caption is absent on the Florence default
chart and appears directly under the controls row, above the three sentences, for a chart cast
at 78.2°N.

## What the tests showed

`tests/fixtures/tables.json` did not change, and neither did `tests/conftest.py`: no table was
added, removed or renamed, and no heading moved.

**Two existing test files changed, three assertions in them.**

| test | before | after |
|---|---|---|
| `test_top_navigation_2026_09_15.py::test_every_page_opens_with_its_header_and_then_the_chart_strip` | `len(parts) == 7`; `name, when, standard, place, sect, day, hour = parts` | `len(parts) == 8`; `name, when, standard, place, sect, lunation, day, hour = parts`, with `lunation in ("Conjunctional lunation", "Preventional lunation")` asserted after the sect |
| `test_top_navigation_2026_09_15.py::test_the_chart_pages_intro_no_longer_sends_the_reader_down_the_sidebar` | `"The reference tables and the sources are at the end of the page list above." in src` and `"Enter a chart in the sidebar, or load a saved one from the top of it." in src` | `"the reference tables and the sources close the page" in src` and `"Enter or load a nativity in the sidebar." in src` — the same two facts (the reference pages close the list; the sidebar takes the nativity) asserted against the owner's new wording |
| `test_wheel.py::test_chart_page_names_the_wheel_and_offers_both_layouts` | `"st.image(svg_code, width=400)" in src` | `"st.image(svg_code, width=560)" in src` |

Nothing was weakened: the strip test gained a part rather than losing one, and the two prose
assertions pin the new sentences as tightly as they pinned the old.

**One new file, twenty-six tests.** `tests/test_chart_layout_2026_09_15.py`, which reads the
rendered page's element order rather than only its source, so the arrangement itself is pinned
and not merely the calls that produce it:

- the Chart page renders **no** `st.metric`, at both layouts and both reading depths (four
  cases), and the four old metric labels and the `hdr1, hdr2, hdr3, hdr4` split are gone from
  the UI half;
- the strip has eight parts on every one of the nine pages, with `Conjunctional lunation` sixth
  and after the sect (nine cases), and the strip takes the first word of `event_label`;
- the square wheel stands in the middle column of a three-column block whose outer columns are
  empty, at 560 px; the wide wheel is still an image at the page's full width;
- the four controls stand in one row of four columns, Radio, Checkbox, Checkbox,
  DownloadButton in that order, at both layouts, aligned on their feet;
- the layout is read before the control is drawn and the wheel is drawn between the two;
- the three captions follow the controls in order and are the owner's three sentences to the
  character, at both layouts, with `Calculation` next after them; both layouts print the same
  three and no joined one; the four italicised titles carry their asterisks;
- the circumpolar caption is absent on the default chart and, for a circumpolar chart, is the
  first thing under the controls row and above the three sentences.

Full suite: **2239 passed, 6 xfailed in 96.69s**, with `-n auto` on the owner's venv. 2213 to
2239 is those twenty-six and nothing else.

The engine half of `app.py` — everything above `# 4. STREAMLIT UI INTEGRATION` — is
byte-identical to `main` at `a7b5ce3`, compared directly rather than by reading the diff.
