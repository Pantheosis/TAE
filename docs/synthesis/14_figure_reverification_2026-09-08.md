# Photo re-verification of the twelve code-read OCR tables — 2026-09-08

Brief: of the 25 figures transcribed into markdown tables in `consolidated_texts/`, 14 are cited by
`app.py`; Fig. 62 (wells) and Fig. 146 (planetary years) were already photo-verified. The other twelve
were each transcribed **from the page photograph first**, with neither the corpus file nor `app.py`
open, and only then diffed three ways (photo / corpus / code). Two OCR captures of one page were never
compared to each other; only page images count.

Branch `figure-reverification-2026-09-08` off `main` 6044bab. The corpus directory is not under git,
so its edits are recorded here and in `consolidated_texts/DOCTRINAL_CAVEATS.md`; the repo commits carry
this record and the two `app.py` comment fixes.

## Verdicts

| # | Figure | Vol. | Page | Photograph(s) | Three-way result | Verdict |
|---|--------|------|------|---------------|------------------|---------|
| 1 | 24 Planetary strengths & weaknesses | Sahl | 69 | `aspect_conditions_rotated/IMG_20260903_040025_248.jpg` | 16 data rows, every cell = corpus. Sentence numbers 78–88 in the strength column are eleven distinct numbers, as `evaluate_strength_of_planets` claims. Fn. 109 on the page reads "my own suggested **contraries**"; corpus had "contrasts" (line at the bottom edge of the frame). | **corpus corrected** (footnote word only; table confirmed) |
| 2 | 60 Four categories of brightness | AM | 305 | `mashar_book_v_rotated/p305.jpg`; `aspect_conditions_rotated/IMG_20260902_232835_592.jpg` | Both photographs: a 4-row key (B/K/E/D). The brief's "21 rows" is not what the corpus holds either — the corpus key is 4 rows; no row-count finding. Letters and English = corpus and = `BRIGHTNESS_DEGREES` categories. Arabic column: page prints نيّرة \ مضيئة, قتّمة, خالية \ فارغة, مظلمة; corpus had invented full vowelling and مَضِيَّة without the hamza. | **corpus corrected** (Arabic column; key confirmed) |
| 3 | 61 Degrees of brightness (V.20) | AM | 306 | `mashar_book_v_rotated/p306_v2.jpg`; `aspect_conditions_rotated/IMG_20260902_233834.jpg` | 77 bands over 12 signs; both photographs agree with each other, with the corpus and with `BRIGHTNESS_DEGREES` in every band (checked by script against the transcription). Each row sums to 30, ranges contiguous 0–29. | **confirmed on all three** |
| 4 | 63 Increasing in good fortune (V.22) | AM | 309 | `mashar_book_v_rotated/p309.jpg` | ♉ 15/27/30, ♌ 3/5, ♏ 7, ♒ 20 = corpus = `GOOD_FORTUNE_DEGREES`. | **confirmed on all three** |
| 5 | 64 Elevation and power (V.22) | AM | 309 | same photograph | 28 ordinal rows incl. the three ranges (♋ 1st–3rd, 14th–15th; ♑ 12th–14th; ♒ 16th–17th) = corpus = `ELEVATION_DEGREES` (31 degrees). | **confirmed on all three** |
| 6 | 59 Male and female degrees (V.19) | AM | 304 | `mashar_book_v_rotated/p304.jpg` (table does not spill to p. 303) | 12 sign rows, every count and range = corpus; each row sums to 30; ♊ and ♍ begin in the Fem. column on the page and in the corpus. Page prints ♓ "23°-27°59" without the minute mark; corpus regularises to 59' — left. Code cites but does not read it (D-19). | **confirmed** (photo = corpus; code reads nothing) |
| 7 | 105 Bodies or orbs of planets | AM | 424 | `mashar_ch_vii_additions_rotated/IMG_20260904_104743_267.jpg`; `aspect_conditions_rotated/IMG_20260902_233802_467.jpg` | ☉15 ☽12 ♄♃9 ♂8 ☿♀7 on both photographs, in the prose VII.3, 7–11, in the corpus and in `PLANETARY_ORBS`. | **confirmed on all three** |
| 8 | 18 Five kinds of non-reception | Sahl | 62 | `aspect_conditions_rotated/IMG_20260903_040427.jpg` | 5 rows, sentence numbers 58 / 59-60 / 61 / 62 / 62, descriptions and ☽→♄ models = corpus = the Kind I–V docstring of `evaluate_non_reception`. | **confirmed on all three** |
| 9 | 71 Māshā'allāh's Lot of enemies | Sahl | 747 | `on_nativities_rotated/IMG_20260904_041543_555.jpg` (**brief's locator was wrong**: `…041220_792` is p. 734, `…041533_677` is p. 746) | M ☿→⊗ Necessity; E ☿→☽ Slaves; Vat. Pal. Lat. 1892 f. 103r Lord 12th→12th Enemies (Hermes) = corpus = the three `LOT_DEFINITIONS` rows (`enemies_necessity`, `enemies_slaves`, `enemies_hermes`). | **confirmed on all three** |
| 10 | 59 Fixed stars harming eyes | Sahl | 550 | `on_nativities_rotated/IMG_20260904_031250_001.jpg` | All Bayer letters are the page's Greek (α-β-γ, λ, β, δ, π, γ², η, ε κ, ζ) — except Lesath, which the page prints **υ Sco.** and the corpus had as `$\nu$`. Not read by code. | **corpus corrected** (ν → υ) |
| 11 | 62 Sahl's use of al-Andarzaghar, Ch. 8 | Sahl | 637 | `on_nativities_rotated/IMG_20260904_033827_845.jpg` (**brief's locator was wrong**: `…015409_781` is p. 339, `…015558_455` is p. 345) | 15 rows (items 1–14 and the unnumbered Head and Tail), every topic and passage reference = corpus. Not read by code. | **confirmed** |
| 12 | 63 Lots of action or work | Sahl | 709 | `on_nativities_rotated/IMG_20260904_040509_857.jpg` | Three rows ☿→♂ (R), ♄→☽ (R), ☉→♄ (R) with names = corpus. Code: `work_action` and `work_authority` reverse at night as the (R) says; `work_expedition` does **not**, by the recorded reason (Sahl's own "by day and night", 10.2.5, 1) with a second row `work_expedition_paul` giving the reversed reading. A documented departure, not a discrepancy. | **confirmed** |

No photograph was unusable; none of the twelve had to be skipped. No code value disagrees with any
photograph, so nothing was escalated.

Structural checks on the fresh transcriptions: twelve glyphs in zodiac order wherever a table is by sign
(Figs. 59, 61, 64 AM); no two-column row with an empty half (the empty Masc. cells of ♊/♍ in AM Fig. 59
are the page's own layout, not a gap); no two adjacent rows byte-identical (Fig. 18's two "62" rows and
Fig. 24's three "(82)" rows differ in their text); degree limits strictly increasing and closing at 29°59'
in every sign row of Figs. 59 and 61.

## Corpus edits (untracked directory; applied in place)

Value corrections — one edit:
- `on_nativities.md:7646` — `$\nu$ Sco., Lesath` → `$\upsilon$ Sco., Lesath` (Sahl Fig. 59).
- `abu_mashar_book_vii.md:2256–2260` — Fig. 60 Arabic column as printed: `نيّرة / مضيئة`, `قتّمة`,
  `خالية / فارغة`, `مظلمة` (the corpus's `/` kept for the page's mirrored slash).
- `sahl_introduction_ch3.md:411` — fn. 109 "contrasts" → "contraries".

Caption labelling — a separate edit, tables untouched: `on_nativities.md` captions of Figures 59, 60,
61, 62, 63 and 64 now read "Figure NN (Sahl): …", matching the "(Abū Ma'shar)" convention on the
other side of each collision. The book's own list of figures in `sahl_frontmatter_reference.md` is left
as the page prints it.

> **Superseded later the same day.** The label was moved from the author axis to the volume axis and
> extended to the whole corpus: all 128 captions in `consolidated_texts/` now read `(Sahl I)` or
> `(Gr. Intr.)`, and PN IV's 141 read `(PN IV)`. "(Abū Ma'shar)" could not stand, because *Persian
> Nativities IV* is his as well — it does not separate *Gr. Intr.* Fig. 98 from PN IV Fig. 98, which is
> the collision this file was written about. See `consolidated_texts/DOCTRINAL_CAVEATS.md`.

Record: a dated paragraph appended to `consolidated_texts/DOCTRINAL_CAVEATS.md`.

## Fixture discipline

Predicted `tests/fixtures/tables.json` diff: **none** — no value in `app.py` changed; the only `app.py`
edit is the comment above `WELLED_DEGREES`. Actual: `tests/test_pages_render.py` passes against the
existing fixture, so the diff is empty, as predicted.

## `app.py` comment fixes (one commit)

`app.py:4409–4416`: the wells comment now says the 2026-09-08 correction was made against the owner's
photographs of V.21 (p. 308), not "the corpus capture", records the third confirmation against Fig. 62's
own page image (62 cells), and names the volume for "Fig. 98" — Abū Ma'shar's Fig. 98 is "Speed relative
to apogee", Persian Nativities IV's Fig. 98 is the wells table itself (PN IV p. 547).

## Locator corrections for the next pass

| Page | Wrong file in the brief | Actual page of that file | Correct file |
|------|-------------------------|--------------------------|--------------|
| Sahl 747 | `IMG_20260904_041220_792.jpg` / `…041533_677.jpg` | 734 / 746 | `on_nativities_rotated/IMG_20260904_041543_555.jpg` |
| Sahl 637 | `IMG_20260904_015409_781.jpg` / `…015558_455.jpg` | 339 / 345 | `on_nativities_rotated/IMG_20260904_033827_845.jpg` |

Found by grepping `on_nativities_pages/*.md` for the figure caption, as the brief's method prescribes.
