# UI changes 2026-09-15 — navigation to the top, and a chart strip on every page

Branch `top-navigation-2026-09-15` off `main` at `1e97210`. Brief: items 3, 4 and 10 of
`UI_FRAMEWORK_REVIEW_2026-09-15_SECOND_OPINION.md` — one branch, as the order of work in that
document asks (header, navigation, strip, URL together).

## What was asked

**3.** `st.navigation(pages, position="sidebar", expanded=True)` put the page list at the head
of the sidebar, above the nativity form: at 1400×900 the Date field was three-quarters of the
way down the sidebar and Save was below the fold. Move the page list to the top of the window,
keep the three sections, and drop the `st.title` every page repeated under it. Reword only the
page text that says where the page list or the reference pages are.

**4.** The app opens on the last chart used and nothing above the fold named it except the
sidebar's picker and the wheel's hub — and the wheel is on one page of nine. Put one caption
under every page header saying which chart the page is reading: its name, the civil date and
time as entered, the time standard with its resolved offset, the place with its coordinates,
the sect, and the lords of the day and hour.

**10.** `st.Page(page_chart, url_path="chart", ..., default=True)` — `/chart` says "Page not
found" and falls back to root. Establish what Streamlit 1.62 actually does and make the
smallest honest change.

## What was built

**The page list is a header bar.** `st.navigation(pages, position="top").run()`. `expanded=`
went with it: Streamlit reads that argument only when `position="sidebar"`, so leaving it would
have been a line that does nothing. The three sections — Part 1: the nativity, Part 2:
prediction, Reference — are unchanged, and so is every page's order within them. The sidebar
now opens on "Nativity", the saved-chart picker, and the Date field.

**`st.title("Traditional Astrology Engine")` is gone.** The name is the browser tab's
(`st.set_page_config`) and the header bar's; as an `st.title` above each page's `st.header` it
cost a heading's height on every page and told the reader nothing the window did not say. Each
page's `st.header` stays.

**One sentence was reworded**, the third of the Chart page's three `_intro` sentences:

> before: … the judgment is the astrologer's. The reference tables and the sources are at the
> foot of the sidebar.
>
> after: … the judgment is the astrologer's. The reference tables and the sources are at the
> end of the page list above.

Its first clause — "Enter a chart in the sidebar, or load a saved one from the top of it" — is
still true and is untouched: the sidebar is the nativity form, and the picker is its first
control. No other page text names the page list's place. The Reference tables page's caption
("Nothing on this page reads the chart in the sidebar") still describes where the chart is
entered, and stands.

**`_chart_strip()`**, defined beside `_finding()` and `_absent()` and called immediately after
`st.header(...)` on all nine pages — before `_readings_note()` and before each page's own
opening sentence, so it is always the first caption on the page. Seven parts, separated by a
middle dot:

    Test Chart 1240 · 1240-05-23 14:30:00 · LMT +00:44:59 · Florence, Italy 43.78, 11.25 · Diurnal · Day lord Mercury · Hour lord Moon

The name is the `chart_picker` selection when a saved chart is loaded and "Unsaved chart"
otherwise — deliberately not the wheel hub's rule, which falls back to the name typed for
saving and then to "Transits". The date and time are as entered (`date_string`, `input_time`),
not as resolved. The standard is `tz_name` with the offset the sidebar's own box resolved,
condensed: to the second under LMT, where that box prints seconds, and to the minute under a
named zone, where it prints minutes; a manual offset's name *is* its offset ("UTC+05:00") and
is not printed twice. The place is `location_query` with latitude and longitude to two
decimals rather than the sidebar's four. Nothing is escaped — it is a caption, not HTML — and
nothing else is in it.

**The Chart page's URL: the `url_path` argument stays, with a comment.** Read in the installed
package and confirmed under `AppTest`: `Page.url_path` is a property that returns `""` when
`default` is set, and that empty pathname is what `st.navigation` registers and sends to the
frontend, so `/chart` is not a route in Streamlit 1.62 and the browser falls back to root.
There is no way to give the default page a non-root path: `st.navigation` requires exactly one
default page and promotes the first page if none is marked, so "make no page the default"
is not available either. But `Page._script_hash` is `calc_hash` of the **private** `_url_path`,
which keeps the string it was given — `calc_hash("chart")`, which is exactly what the harness
sets as `at._page_hash`. So the argument is the page's identity inside the app even though it
is not its address in the browser; dropping it would rename the page to `page_chart`, break
`make_app(page="chart")` and gain nothing. It stays, and the comment beside it records that the
page is served at the root.

## What the tests showed

`tests/fixtures/tables.json` did **not** change, and neither did `tests/conftest.py`. That was
the expectation and it held: `AppTest` selects a page by hash, not through the navigation
widget, so where the widget is drawn is invisible to the harness; and `table_inventory()` keys
each table to the nearest preceding subheader or expander, which a caption is not.

One existing assertion was updated, `test_reference_page.py`'s pin on the navigation call:
`'st.navigation(pages, position="sidebar", expanded=True)'` → `'st.navigation(pages,
position="top")'`. It is the same pin on the same line, moved with it. Nothing else in the
existing tests changed — no fixture value, no expected row, no count. The strip's own
contribution to the prose counts is nil: `test_prose_counts.py` and `test_prose_tables.py`
count named phrases and table cells, not captions, and every main-area caption assertion in the
suite searches with `any(... for c in at.main.caption)` rather than by position, so a caption
inserted first displaces nothing.

`tests/test_top_navigation_2026_09_15.py` is new, sixteen tests: the navigation call and its
three sections; no `st.title` in the UI half and none rendered on any of the nine pages; for
each of the nine pages a render with no exception, exactly one `st.header`, and a first caption
of seven parts with each part checked (name, date and time, standard, the two-decimal
coordinates, sect, the two lords); the strip naming a saved chart when the picker holds one;
the Findings page at both reading depths; the reworded sentence; and item 10 — the Chart page
resolving by `calc_hash("chart")`, and an unknown page hash falling back to it as the default.

The engine half — everything above `# 4. STREAMLIT UI INTEGRATION` — was diffed against `main`
byte for byte and is identical. `README.md` describes no navigation and was not touched.

Full suite: **2188 passed, 6 xfailed in 94.41 s**, with `-n auto` on the owner's venv. 2172 to
2188 is the sixteen new tests and nothing else.
