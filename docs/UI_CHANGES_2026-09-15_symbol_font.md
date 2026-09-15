# UI changes 2026-09-15 — the embedded symbol font

Branch `symbol-font-2026-09-15` off `main` at `0a67dae`. Item 13 of
`UI_FRAMEWORK_REVIEW_2026-09-15_SECOND_OPINION.md` (brief #8's second half),
ruled on 2026-09-15: a symbol-font subset embedded in every SVG the app
draws, and nothing else — no general-use font, no
`server.enableStaticServing`, no launcher change.

## What was asked

The four renderers (`generate_hybrid_svg`, `generate_multiwheel_svg`,
`generate_distribution_strip_svg`, `generate_hit_strip_svg`) name three
system fonts in `_WHEEL_FONT` (Noto Sans Symbols, Segoe UI Symbol, DejaVu
Sans) and hope one is installed. An SVG shown through `st.image` or opened
as a download cannot load a web font at all, so the astrological glyphs
depend on what each viewing machine happens to have. The ruling: subset the
exact glyphs the renderers use out of the two Noto Sans Symbols files on
this machine, embed the subset as base64 WOFF2 inside every SVG via a
`<style>` element right after the opening `<svg>` tag, and put the embedded
family first in `_WHEEL_FONT`'s stack so the system names stay as
fallbacks for whatever the embedded subset does not cover. Nothing else
changes: not the picture's geometry, not page text, not `tables.json`.

## The character list — confirmed by scanning, not by the brief's own count

The brief that authorised this build supplied a candidate list of 32
characters (31 symbols, plus U+FE0E) and asked for it to be confirmed by
scanning the four renderers and the three glyph tables (`SIGN_GLYPHS`,
`POINT_GLYPHS`, `_ASPECT_GLYPH`) rather than trusted. The scan (every
non-ASCII character across `engine.py` lines 594–1450, the four renderers
and every private helper they call) found a **different** list:

- The candidate list's right arrow (U+2192) is written nowhere in the four
  renderers. It is a table cell on the aspects page — `f"{applicant} →
  {receiver}"`, an `st.dataframe` string near line 3013, not SVG — and is
  out of this branch's scope under "no page text changes at all."
- Three characters the candidate list omitted ARE written into SVG text by
  the renderers: the degree sign U+00B0 (`f'{d:02d}°'`, at every planet's
  degree label and the hub's latitude/longitude line), the middle dot
  U+00B7 (the hub's "Whole sign · Alchabitius" and, in the wide layout,
  "Lord of the day · Lord of the hour") and the en dash U+2013 (the wide
  positions panel's motion cell when a point carries no speed data).

The confirmed list is **33 symbols plus U+FE0E** (`_VS`, the
text-presentation selector already on every glyph — kept exactly as it is;
this branch does not touch it):

    ° · – … ′ ℞ ⊗ □ △ ☉ ☊ ☋ ☌ ☍ ☽ ☿
    ♀ ♂ ♃ ♄ ♈ ♉ ♊ ♋ ♌ ♍ ♎ ♏ ♐ ♑ ♒ ♓ ⚹

## Coverage per source font, checked with fontTools

The two files named in the brief, as shipped by Arch Linux's `noto-fonts`
package (version `1:2026.09.01-1`, `pacman -Qi` licence `OFL-1.1-no-RFN`):

| file | family | version |
|---|---|---|
| `/usr/share/fonts/noto/NotoSansSymbols-Regular.ttf` | Noto Sans Symbols | Version 2.003; ttfautohint (v1.8.4.7-5d5b) |
| `/usr/share/fonts/noto/NotoSansSymbols2-Regular.ttf` | Noto Sans Symbols 2 | Version 2.008 |

Checked per character with `uvx --from fonttools python`, `TTFont.getBestCmap()`,
cross-checked against the union of every `cmap` subtable in each font (a
"symbol" TTF can carry a Symbol-platform (3,0) table instead of a Unicode
one — both fonts here carry ordinary Unicode (0,3)/(0,4)/(3,1)/(3,10)
tables, so the two methods agree):

| | in Symbols | in Symbols 2 | in neither |
|---|---|---|---|
| ☊ ☋ ☌ ☍ ☽ ☿ ♀ ♂ ♃ ♄ (10) | yes | no | |
| the 12 signs | yes | no | |
| ⚹ (sextile) | yes | no | |
| ☉ (Sun), □ (square), △ (trine) | no | yes | |
| ⊗ (Lot of Fortune, U+2297) | no | no | **yes** |
| ° · – … ′ ℞ (6 marks) | no | no | **yes** |

23 code points live only in Symbols, 3 only in Symbols 2 — disjoint sets,
which is why this is **two embedded faces**, exactly the contingency the
brief named ("if some glyphs live only in Symbols2, two faces"). **26 of
the 33 confirmed code points are covered between the two files. 7 are not,
in EITHER file**, and this is not a subsetting choice: `pyftsubset
--unicodes=U+2297` on either source produces a font with zero glyphs for
it, because the character is not there. Of the 7:

- **⊗, the Lot of Fortune's own glyph in `POINT_GLYPHS`**, is the one
  genuine gap in the glyph-table completeness this branch otherwise
  guarantees. It keeps depending on the system fallback stack — exactly
  its behaviour before this branch, no better and no worse.
- The other six (° · – … ′ ℞) are not glyph-table entries — they are
  literals the renderers write directly — and are common Latin-1/General
  Punctuation/Letterlike-Symbol characters present in nearly every
  installed sans-serif font, so the practical risk they carry is far
  smaller than the dingbats this branch was built to fix.

`glyph_font.py`'s own docstring carries this finding in full, and
`glyph_font.COVERED` / `glyph_font.KNOWN_UNCOVERED` name the 26 and the 1
exactly; `tests/test_symbol_font_2026_09_15.py` fails loudly if a NEW,
undocumented gap ever appears in the three glyph tables.

## The command

```
uvx --from 'fonttools[woff]' pyftsubset /usr/share/fonts/noto/NotoSansSymbols-Regular.ttf \
    --output-file=TAE-Symbols-Regular.woff2 \
    --unicodes=U+260A,U+260B,U+260C,U+260D,U+263D,U+263F,U+2640,U+2642,U+2643,U+2644,\
U+2648,U+2649,U+264A,U+264B,U+264C,U+264D,U+264E,U+264F,U+2650,U+2651,U+2652,U+2653,U+26B9 \
    --flavor=woff2 --no-hinting --desubroutinize --layout-features=

uvx --from 'fonttools[woff]' pyftsubset /usr/share/fonts/noto/NotoSansSymbols2-Regular.ttf \
    --output-file=TAE-Symbols2-Regular.woff2 \
    --unicodes=U+2609,U+25A1,U+25B3 \
    --flavor=woff2 --no-hinting --desubroutinize --layout-features=
```

`fontTools` is not a runtime dependency of this app (`requirements.txt`
unchanged) — both runs were one-off, through `uvx`, on this machine only;
only the two resulting base64 WOFF2 blobs are committed, in `glyph_font.py`.
Verified after subsetting (`fonttools[woff]` again, for the brotli WOFF2
decoder): each output's cmap is exactly its intended code points, no more,
no fewer. `--layout-features=` (empty) drops every GSUB/GPOS table
subsetting would otherwise keep — neither font carries one for these code
points, but the flag makes the omission a decision.

## Sizes

| | bytes | base64 |
|---|---:|---:|
| `TAE-Symbols-Regular.woff2` (23 glyphs) | 2,800 | 3,736 chars |
| `TAE-Symbols2-Regular.woff2` (3 glyphs) | 708 | 944 chars |
| **total embedded per SVG** | 3,508 | 4,680 chars |

The `<style>` element itself (both `@font-face` rules, `unicode-range`
descriptors, the base64) is 5,046 characters — 5,076 bytes land in every
SVG once written out, measured on the default chart:

| picture | before | after | delta |
|---|---:|---:|---:|
| natal wheel, bounds ring | 71,803 | 76,879 | +5,076 |
| revolution wheel (one ring) | 66,825 | 71,901 | +5,076 |

The delta is identical to the byte because the `<style>` payload's size
does not depend on the chart — it is the same block, verbatim, in all four
renderers.

## What `rsvg-convert` showed

`rsvg-convert 2.62.3` (cairo 1.18.4, pango 1.58.2, harfbuzz 14.4.0) rendered
both the natal wheel and a revolution wheel from their raw SVG text with
**every glyph correct** — the twelve signs, the seven planets, the nodes,
retrograde marks, degree signs, and the Lot of Fortune (⊗, via the fallback
stack, since it is the one documented gap). A 2000×2000 render of the natal
wheel, cropped to the Gemini/Taurus sign band, shows crisp glyphs at high
zoom with no tofu and no substitution artifacts. **librsvg does honour an
embedded data-URI WOFF2 font declared in the SVG's own `<style>` element**
— this is not a browser-only effect.

## What the browser showed

Server on port 8521 (`streamlit run app.py --server.port 8521`),
`preview_start(url=...)` reaching it directly with no `.claude/launch.json`
needed. Chart page at 1400×900, chart "Jason Armfield" (the last-loaded
chart, unchanged).

- **The Chart page's inline wheel** (the `st.components.v2` mount from item
  11) carries the SVG inside a shadow root, and that shadow root holds
  *two* `<style>` elements: the component's own CSS (2,633 characters, no
  `@font-face`) and a second one, 5,046 characters, beginning
  `@font-face{font-family:'TAE Symbols';...}` — exactly `font_face_css()`'s
  output. **`document.fonts.check("16px 'TAE Symbols'")` returns `true`,
  but this is not reliable evidence**: iterating `document.fonts` directly
  (`for (const f of document.fonts)`) lists only Streamlit's own top-level
  faces (KaTeX, Source Sans/Serif/Code Pro, Material Symbols) and never
  `'TAE Symbols'` at all, even after `await document.fonts.ready`. This
  browser's engine does not promote a shadow-root-scoped `@font-face` into
  the document's `FontFaceSet`, so `check()` is answering "no matching
  face is registered, therefore nothing blocks it" rather than "this face
  is loaded and in use" — a genuine quirk, not a rendering problem: the
  wheel's sign ring, inspected by eye (zoomed screenshot, and again in the
  component's own full-viewport expand overlay), shows the correct glyphs
  regardless. The reliable check here is the pixels, not the API.
- **The Timing page's wheel** is still an `<img src="data:image/svg+xml;base64,...">`
  (eight such images on that page — the multiwheel picture and the six
  direction strips, each confirmed by reading `img.src` directly), exactly
  as before item 11. Its sign ring, compared by eye with the Chart page's,
  shows the same glyphs at the same fidelity; the data-URI image path
  cannot be inspected the way the shadow root's raw markup can, only seen.
- **Standalone download.** The mounted component's own SVG markup was read
  out of its shadow root (`shadowRoot.querySelector('svg').outerHTML`,
  79,285 characters, confirmed to contain `@font-face` and `'TAE Symbols'`)
  and reloaded in an isolated `<iframe>` on a `data:image/svg+xml;base64,`
  URL — the same self-contained form a downloaded `.svg` file opened
  directly in a browser tab would take, with no parent stylesheet, no
  shadow root, no Streamlit CSS reachable. It rendered identically: full
  wheel, every glyph in place. This is the proof the brief's own "why"
  asked for — an SVG opened as a bare file, offline, still carries its
  glyphs.
- **Preferences.** `~/.local/share/TraditionalAstrologyEngine/preferences.json`
  hash before: `3739a413d161c09ddf83827a821a3fdb` (`_launches: 5`); after:
  `f443f346d1fb11d189b90dc948cbd5f8` (`_launches: 6`). The only change is
  the launch counter a session start always increments (item 9's own
  `_launches` preference, unrelated to this branch); `_wheel_dark`,
  `_wheel_layout`, `_timing_wheel_view` and every other stored preference
  are unchanged — nothing this branch's own browsing touched was written
  back.

## The licence

Both source files' own `name` table (ID 13, identical in both) declares:
"This Font Software is licensed under the SIL Open Font License, Version
1.1. This license is available with a FAQ at: https://scripts.sil.org/OFL"
(ID 0: "Copyright 2022 The Noto Project Authors
(https://github.com/notofonts/symbols)"). The full OFL 1.1 legal text was
sought on this machine and **not found** where the brief expected it:
`pacman -Qi noto-fonts` reports `Licenses: OFL-1.1-no-RFN`, but
`/usr/share/licenses/noto-fonts/LICENSE` — the file that package actually
ships — is the Apache License, Version 2.0, verbatim. A packaging mismatch,
not a statement about the font's own licence. `fonts/OFL.txt` in this
repository carries the font's own name-table attestation, verbatim, and
says plainly that the full SIL OFL 1.1 text
(https://scripts.sil.org/OFL) still needs to be added to complete the
notice — the brief's own fallback ("or say it must be added"), used
because retyping the legal text from memory into a licence file is worse
than admitting it is not yet there. `README.md`'s Licence section names the
embedded subset and points at both `fonts/OFL.txt` and this document.

## What changed, and what did not

Engine diff, confirmed by an AST comparison against `main`'s
`engine.py`: one new import (`from glyph_font import font_face_css`),
`_WHEEL_FONT`'s literal (the family prepended to the existing stack), and
the four renderer functions — `generate_hybrid_svg`,
`generate_multiwheel_svg`, `generate_distribution_strip_svg`,
`generate_hit_strip_svg` — each gaining one list element,
`f'<style>{font_face_css()}</style>'`, right after the opening `<svg>` tag.
No other top-level function or assignment differs. `tests/fixtures/tables.json`
is untouched (no page text, no table, no heading moved).

**The proof that nothing else moved**: a normalisation — strip the
`<style>...</style>` block, then strip `'TAE Symbols', ` from the
`font-family` stack — asserted byte-equal against `main`'s output for the
default chart on all four renderers, in
`tests/test_symbol_font_2026_09_15.py`. `tests/test_clickable_wheel_2026_09_15.py`'s
own "normalised SVG equals main's" proof (item 11) needed the same
treatment, applied to BOTH sides rather than one: `main` at this
repository's current HEAD already carries the `<g>` wrappers that proof
was first written against (item 11 is merged), so a fresh checkout of
`main` today, with no branch open at all, already fails that assertion as
originally written — checked directly, by reverting `engine.py` to HEAD in
this worktree and rerunning. That is a pre-existing condition, unrelated to
this branch, surfaced by comparing against an updated `main`; making the
comparison symmetric restores its actual intent (nothing but known,
accounted-for markup differs) without weakening or re-litigating what item
11 already settled.

`build.spec` bundles `glyph_font.py` as data beside `engine.py`, for the
same reason `engine.py` itself is bundled as data rather than analysed:
nothing imports it at PyInstaller build time, and Streamlit puts the
script's own directory on `sys.path` before running it. `desktop_launcher.py`
is untouched.

10 new tests (`tests/test_symbol_font_2026_09_15.py`), one existing test
file's normalisation adjusted (`test_clickable_wheel_2026_09_15.py`, one
assertion, symmetric now rather than one-sided), full suite:
**2358 passed, 1 skipped (fontTools/brotli are not in the app's venv,
by design — the skip is the coverage-decoding test, already checked
separately through `uvx`), 6 xfailed.**
