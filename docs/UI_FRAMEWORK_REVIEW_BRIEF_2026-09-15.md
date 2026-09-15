# UI framework review brief — 2026-09-15

Two questions from the owner: (1) is Streamlit the right framework for this app, and (2) if so,
what improvements are worth building. Reviewed on `main` at `cfae6df` (the `Executable/`
checkout). `Executable_astra/app.py` differs slightly from it and was not reviewed.

## Verdict

**Stay on Streamlit.** The app is a study companion that is mostly cited tables, prose and a few
drawn wheels. That is the kind of app Streamlit is built for. The measurements below show no speed
problem, and moving to another framework would mean rewriting both the UI and the test harness to
gain interactivity that Streamlit 1.62 now provides.

The one planned piece Streamlit should not carry is the **teaching tool for the three reference
frames** (horizonal, equatorial, ecliptical). Continuous animated 3D is a job for JavaScript
(e.g. three.js), written as its own piece and embedded as a component if wanted.

## How it was checked

- Read the UI half of `app.py` (from `# 4. STREAMLIT UI INTEGRATION`), `desktop_launcher.py`, the
  test harness in `tests/conftest.py`, and `docs/UI_CHANGES_2026-09-10.md`.
- Ran the app headless under `streamlit.testing.v1.AppTest`, profiled one rerun with cProfile, and
  took screenshots of a live server at 1400×900 (Chart, Configurations, Timing, Dignities).
- Environment: a cloud copy on Python 3.14.0rc2 with the pins in `requirements.txt`, not the
  owner's venv (3.14.7). Absolute times will differ; the ratios should hold.

## Findings

### Speed

| Measurement (AppTest, Florence 1240-05-23 14:30 LMT) | Result |
|---|---|
| Rerun, any page | 0.61–0.79 s (Timing is the slowest) |
| Of which: the chart engine and the page code (`app.py` `<module>`) | ~0.18 s under the profiler |
| Of which: parsing and "magic" AST rewriting of the 1 MB script | ~0.45 s |
| Rerun with `runner.magicEnabled = false` | 0.26–0.37 s, same table and markdown counts on all 8 pages |

- The engine is cheap: a full chart with every evaluator and `pn4_timing_bundle` costs about
  0.1 s. Recomputing everything at the top level on each rerun is not a practical problem.
- Most of each test run is Streamlit re-parsing the 16,027-line `app.py` and applying magic.
  The live server keeps the compiled script between clicks, but `AppTest` does not, which is
  why the suite takes about ten minutes.
- An AST scan found **no bare expressions** in `app.py`, so the app does not use magic.

### Layout and interaction

- **The sidebar does two jobs.** It holds the page list and the whole nativity form. At
  1400×900 the Date field starts about ¾ of the way down the window, and Save is off-screen.
- **Every page repeats the h1 "Traditional Astrology Engine"**, about 150 px of vertical space
  the chart itself could use.
- **The wheel is a static SVG** (`st.image`), shown at 400 px in the Square layout with empty
  space beside it. Nothing on it can be clicked. `UI_CHANGES_2026-09-10.md` already notes that
  the tri-wheel is unreadable at 560 px.
- **No table uses `column_config` or row selection** (85 `st.dataframe` calls). Some cells are
  cut off, e.g. Timing → "786 completed civil years (the profec…". Yes/No columns are plain text.
  The strength and weakness headers carry sentence numbers ("78 excellent place").
- **Tabs render every tab on every run.** Timing draws 50 tables across six tabs, and
  Configurations draws 18 across five.
- **Citations sit in expanders** under each table ("Sources and editorial notes"), away from the
  row they explain.
- No theme is configured: `.streamlit/config.toml` only sets `toolbarMode`.

### Alternatives considered

| Option | Gain | Cost |
|---|---|---|
| NiceGUI (event-driven, native window mode) | Finer control, no full reruns | Rewrite about 2,850 UI lines and the AppTest harness behind 2,649 tests |
| Native PySide6 (already bundled on Windows) | Native feel | Tables, markdown and citations are much more work; a full rewrite |
| Web frontend (Tauri / React) with a Python API | Highest ceiling for the UI | Two languages, a new build pipeline, a full rewrite |
| **Streamlit 1.62, used more fully** | **Interactivity via components v2, lazy tabs, dialogs, table selection** | **Incremental; tests stay** |

## Recommendations, in priority order

### 1. Turn off magic (one line)

```toml
[runner]
magicEnabled = false
```

Add this to `.streamlit/config.toml`. It should roughly halve the test suite. **Check:** run the
full suite (it includes the `tables.json` inventory) and record the new runtime.

### 2. Render only the open tab

`st.tabs(labels, key=..., on_change="rerun")`, then render a tab's content only when its `.open`
property is true. Start with Timing, then Configurations. **Watch:** the table-inventory tests
render one page at a time, so they need to open each tab (or the harness needs to set each tab's
state) to keep counting every table.

### 3. A chart strip and a nativity dialog

- Replace the repeated `st.title` with a one-line summary shown on every page, for example:
  `1240-05-23 14:30 LMT · Florence 43.78, 11.25 · Diurnal · ☿ day / ☽ hour`.
- Put an **Edit nativity** button in the strip that opens `st.dialog` with the date, time, time
  standard, place and save controls. The sidebar is left with the page list and the saved-chart
  picker.
- **Constraint:** keep the session keys the harness and `_restore_chart` rely on unchanged:
  `date_input_key`, `time_input_key`, `time_standard_key`, `utc_offset_key`, `manual_coords_key`,
  `manual_lat_key`, `manual_lon_key`, `location_input_key`, `chart_picker`.
- **Watch:** the engine currently reads these widgets at the top level before any page runs.
  Values must still resolve from `session_state` when the dialog is closed.

### 4. Tables with `column_config`

- `CheckboxColumn` for Yes/No, e.g. Connected, Received.
- Short strength and weakness headers, with the sentence number and citation in the column's `help`.
- Set widths on text-heavy Value columns (Timing → The revolution of the year) so nothing is cut off.
- Consider planet glyphs beside the names, watching the emoji-variation-selector rule already
  learned (`_VS`).

### 5. "Why this fired" row detail

Use `st.dataframe(..., on_select="rerun", selection_mode="single-row")` on the finding tables.
Selecting a row opens a panel or dialog with the rule's sentence, its source, and the chart values
that satisfied it. This places the app's principle that every rule names its sentence at the row
where it is used.

### 6. A clickable wheel (the headline feature)

Wrap the SVG from `generate_hybrid_svg` in an `st.components.v2.component` (inline HTML, CSS and
JS with no build step; the JS sends events back to Python).

- **Click a planet:** a side panel lists its essential and accidental dignity, its connections and
  receptions, the lots it rules, and its places, each with a citation.
- **Hover a sign:** show its bounds and triplicity lords.
- **Keep** `generate_hybrid_svg` a pure function and keep the SVG download. The component only
  adds `data-*` attributes and listeners.
- **Security:** the component runs trusted code only. Escape any chart name or place label placed
  in its HTML.
- This is also the groundwork for embedding the reference-frames sky tool later.

### 7. Move the engine out of `app.py`

Move everything above the UI marker into a module (e.g. `engine.py`, or a package) that `app.py`
imports.

- Each test run then parses only the UI.
- `conftest.py` can import the engine directly instead of cutting the file at the marker.
- **PyInstaller:** the module must be included in `build.spec`.
- Splitting the pages into separate files can follow later.

### 8. A theme

Set `[theme]` in `config.toml`, e.g. a serif body font to suit a scholarly companion. Worth
testing: bundle a symbol font (served through `server.enableStaticServing`) for the astrological
glyphs. It might fix the emoji-rendering problem at its source rather than only through variation
selectors. **Constraint:** the app is offline, so fonts must be bundled, not loaded from Google
Fonts.

## Suggested order of work

One branch each, with the full suite after each:

1 → 2 → 3 → 4 → 5 → 6, with 7 and 8 whenever convenient.

Items 1, 2 and 4 are small. Items 3 and 6 need checking in a live browser as they are built. For
the preview-pane quirks, see `UI_CHANGES_2026-09-10.md` ("Lesson for the next session").
