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

The wheel is drawn at `width=560` inside
`st.container(horizontal=True, horizontal_alignment="center")`. The wheel's viewBox is
`0 0 1000 1000`, square, so 560 px of width is 560 px of height, and nothing about the picture
changes but its scale: at 400 px the minute figures beside a planet were at the edge of
legibility, and at 560 they are not.

**Not by columns, which was the first attempt and was wrong.** `st.image` draws at the left
edge of whatever holds it, so the obvious centring is a picture in the middle column of
`st.columns([1, 2, 1])` — and that centres it, but it also caps it. A column is a *fraction of
the page*, not a fixed width, and `st.image` shrinks a picture to the width it is given rather
than overflowing it, so the middle of `[1, 2, 1]` drew the wheel at **454 px at a 1400 px
window and 394 px at 1280** — narrower, at the smaller size, than the 400 px the change was
meant to enlarge. Measured in the browser, which is the only place it shows: under `AppTest`
the column split and the container are both simply a block holding the image, and every
structural assertion passed on the capped version.

A horizontal container is a flex row rather than a fraction of the page. Its proto reads
`direction: HORIZONTAL`, `justify: JUSTIFY_CENTER`, `width_config { use_stretch: true }`: the
row is the full width of the main area, its children keep their own widths, and the row centres
them. So the wheel is 560 px at every window width, and centred at every one.

The wide layout is unchanged in substance — `st.image(svg_wide, width='stretch')`, the
positions panel drawn inside the picture, the full page width, scrolling.

### One row of controls, under the wheel

`_layout_control()` keeps everything it did and lays it out differently: the four controls now
sit in `st.container(horizontal=True, vertical_alignment="bottom", gap="medium")` in the order
the ruling gives them — the Wheel layout radio (horizontal, as it always was), the Bounds ring
checkbox, the Dark wheel checkbox, the Download button. The feet are aligned rather than the
tops, so the radio's row of options, the two checkbox rows and the button sit on one line;
aligned at the top they fall at three heights, because a radio carries its label and its
options and a button carries neither. The row is left-aligned and the page's full width, which
is how the row of controls was asked for.

**Again not by columns, and again found only in a browser.** The first version used
`st.columns([2, 1, 1, 1.4], vertical_alignment="bottom")`, and on the owner's screen the four
controls ran straight down the left-hand edge in a single column. Streamlit stacks columns
vertically below about 640 px of page width, and a reader zoomed in, or in a narrow window, is
below that breakpoint — so the "one row" was a row only on a wide enough screen. A horizontal
container is a flex row at every width: `direction: HORIZONTAL`, `align: ALIGN_END`,
`justify: JUSTIFY_START`, `wrap: true`, so the four stay side by side and wrap only when they
genuinely cannot fit, which is the behaviour the ruling describes and `st.columns` does not
give.

**And the radio's label collapsed, so the row is one tier.** With the four side by side the row
still read as two, because a radio prints its label *above* its options and a checkbox prints
its *beside* the box: the radio's options sat a line lower than everything next to them. On the
owner's ruling the Chart page's radio takes `label_visibility="collapsed"` and its tooltip is
dropped — under a wheel, "Square" and "Wide" say what the control does without being told. The
label string itself stays, because Streamlit requires a non-empty one and it remains the
widget's accessible name and the name a test looks it up by. `_reading_radio` gained a
`label_visibility` keyword defaulting to `"visible"` to carry it, so the other eight radios in
the app are untouched — **including the Timing page's copy of this very radio**, which sits in
its own row with a selectbox beside it, where the label is what tells the two apart. That is
the one place the two wheels' shared control now differs, and it differs in its label only:
the widget key is still the same, so the setting still follows the reader between the pages.

The radio's help text is therefore gone from the Chart page altogether. It had said "the wheel
beside the controls and the introduction, the header metrics under it" — a description of a
page that no longer exists — and was reworded to match the new arrangement before the ruling
dropped the tooltip; so no page string on this branch was changed that the owner did not
dictate, the reworded one having been removed rather than kept.

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

### And then the strip broke in two

Eight parts on one line is a long line: it ran past the window and wrapped wherever the width
happened to fall, so the break landed in a different place on every page and at every window
size. On the owner's ruling the strip is two lines, and the break is where the sense already
divides — the first line is **the nativity as it was entered**, the name, the moment, the
standard it is counted in, the place; the second is **what the app reads from it**, the sect,
the lunation, and the two chronocrats. The join is a caption hard break, two spaces and a
newline, which is how the sidebar's own boxes break a caption; nothing else about the parts or
their order changed.

**The second line is bold.** The first line the reader typed and already knows; the second is
four measurements the app made, and above the fold nothing else on any page states them. One
pair of `**` markers wraps the joined line — not each part, which would bold four fragments and
leave the separators between them plain — and a caption renders markdown, as the sidebar's own
boxes rely on.

The strip, on every page, for the harness's chart (line two bold):

    Unsaved chart · 1240-05-23 14:30:00 · LMT +00:44:59 · 43.78, 11.25
    **Diurnal · Conjunctional lunation · Day lord Mercury · Hour lord Moon**

## What the browser showed

The branch could not reach a browser from where it was built: the preview tools resolve
`.claude/launch.json` from the shared checkout at `Executable/`, not from the worktree, and a
worktree-isolated agent may not write to the shared checkout; the launch configuration for port
8516 was written in the worktree's own `.claude/launch.json`, where the tool does not look for
it. QA ran the worktree on 8516 and measured it instead, and the owner looked at the page; that
is how both of the column faults below were found. Neither could have been caught by the
harness: under `AppTest` a column split and a flex container are both simply a block holding
the children, and the widths and the breakpoint that separate them exist only in a browser. The
lesson for the next UI branch is that `st.columns` lays out *proportions of the page*, and that
neither a picture of a fixed width nor a row that must stay a row is a proportion.

**The wheel, first arrangement, `st.columns([1, 2, 1])`:** the image 454 px wide at 1400×900,
its foot at 696 px of 900; 394 px wide at 1280×720, foot at 658 px of 720. Centred to within
5 px, no metric on the page, the strip correct — and the wheel *smaller* than the 400 px it
replaced at the smaller window, because a column is a fraction of the page and `st.image`
shrinks to the width it is given. Rejected on the measurement.

**The controls, first arrangement, `st.columns([2, 1, 1, 1.4])`:** on the owner's screen the
four ran vertically down the left-hand edge. Streamlit stacks columns below about 640 px of
page width, so the row was a row only above that breakpoint and a zoomed or narrow window fell
under it.

**Both, second arrangement, the horizontal containers:** to be re-measured. Expected for the
wheel, and accepted by the owner in advance: about 560 px wide at both sizes, the foot near
800 px of 900 at 1400×900 — inside the fold — and about 100 px below the fold at 1280×720,
where the reader scrolls to the controls anyway. Expected for the controls: one row at any
width, wrapping only when the four genuinely cannot fit.

What could be checked without a browser was checked.

**The picture at its new size.** The square wheel was rendered from this branch's engine for the
harness's chart and rasterised with `rsvg-convert` at 560 px. It is 560×560: the viewBox is
`0 0 1000 1000` and `st.image(width=560)` scales a square to a square, so the wheel occupies
exactly 560 px of page height, 160 px more than it did. At that size the sign glyphs, the
degree and minute figures beside each planet, the Alchabitius cusp numbers and the retrograde
marks are all legible, which at 400 px the minutes were not.

**The arrangement, from the rendered page.** `AppTest` renders the real element tree, and the
Chart page's children come out in the ruled order: the header, the strip caption, a centred
flex row holding the image, a bottom-aligned flex row holding the radio, the two checkboxes and
the download button in that order, then the
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
| `test_top_navigation_2026_09_15.py::test_every_page_opens_with_its_header_and_then_the_chart_strip` | `len(parts) == 7`; `name, when, standard, place, sect, day, hour = parts` | the strip split on the hard break first and then on the dots: two lines, four parts each — `name, when, standard, place = entered` and `sect, lunation, day, hour = read` — with `lunation in ("Conjunctional lunation", "Preventional lunation")` asserted after the sect |
| `test_top_navigation_2026_09_15.py::test_the_chart_pages_intro_no_longer_sends_the_reader_down_the_sidebar` | `"The reference tables and the sources are at the end of the page list above." in src` and `"Enter a chart in the sidebar, or load a saved one from the top of it." in src` | `"the reference tables and the sources close the page" in src` and `"Enter or load a nativity in the sidebar." in src` — the same two facts (the reference pages close the list; the sidebar takes the nativity) asserted against the owner's new wording |
| `test_wheel.py::test_chart_page_names_the_wheel_and_offers_both_layouts` | `"st.image(svg_code, width=400)" in src` | `"st.image(svg_code, width=560)" in src` |

Nothing was weakened: the strip test gained a part rather than losing one, and the two prose
assertions pin the new sentences as tightly as they pinned the old.

**One new file, thirty tests.** `tests/test_chart_layout_2026_09_15.py`, which reads the
rendered page's element order rather than only its source, so the arrangement itself is pinned
and not merely the calls that produce it:

- the Chart page renders **no** `st.metric`, at both layouts and both reading depths (four
  cases), and the four old metric labels and the `hdr1, hdr2, hdr3, hdr4` split are gone from
  the UI half;
- the strip is two lines of four parts on every one of the nine pages, with
  `Conjunctional lunation` second on the second line and after the sect (nine cases), and the
  strip takes the first word of `event_label`;
- the strip's two lines are exactly right for the harness's chart, the second bold with one
  pair of markers round the whole line (`read.count("*") == 4`) and the first with none;
- the Chart page's layout radio reports `label_visibility` COLLAPSED and no help, and still
  answers to the label "Wheel layout" so a lookup by name finds it; the Timing page's copy of
  the same radio is asserted **not** collapsed; and `_reading_radio` is asserted to take the
  keyword and to default it to `"visible"`;
- the square wheel is the one child of a full-width flex row whose proto reads
  `direction: HORIZONTAL` and `justify: JUSTIFY_CENTER`, at 560 px, and `st.columns([1, 2, 1])`
  is asserted **absent** so the cap cannot come back; the wide wheel is still an image at the
  page's full width;
- the four controls are the four children of one flex row — `direction: HORIZONTAL`,
  `align: ALIGN_END`, `justify: JUSTIFY_START`, `wrap: true`, full width — as Radio, Checkbox,
  Checkbox, DownloadButton in that order, at both layouts, with the column split that collapsed
  asserted absent;
- the layout is read before the control is drawn and the wheel is drawn between the two;
- the three captions follow the controls in order and are the owner's three sentences to the
  character, at both layouts, with `Calculation` next after them; both layouts print the same
  three and no joined one; the four italicised titles carry their asterisks;
- the circumpolar caption is absent on the default chart and, for a circumpolar chart, is the
  first thing under the controls row and above the three sentences.

Full suite: **2243 passed, 6 xfailed in 96.56s**, with `-n auto` on the owner's venv. 2213 to
2243 is those thirty and nothing else.

The engine half of `app.py` — everything above `# 4. STREAMLIT UI INTEGRATION` — is
byte-identical to `main` at `a7b5ce3`, compared directly rather than by reading the diff.
