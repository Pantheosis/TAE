# Phase 0 — corpus inventory (2026-09-07)

Corpus: `/home/apothic/Desktop/Fifty Aphorism OCR Project/consolidated_texts/`.
Last code reconciliation: `AUDIT_2026-09-06_SOURCE_CONFORMANCE.md`, which names its sources as
`sahl_introduction_ch3.md`, `abu_mashar_book_vii.md`, `on_nativities.md`, `fifty_aphorisms.md`,
`images/`. Everything else in the table below has arrived since, and has never been read
against `app.py`.

## Two pagination systems

`abu_mashar_book_vii.md` pp. 407–498 are **Abū Ma'shar's *Great Introduction*** pagination — a
different printed volume from Sahl's *Volume I*. They overlap numerically with Sahl's
*On Nativities* (pp. 255–749) by coincidence. **Figure numbers collide the same way**: Sahl
Vol. I runs Figures 1–71; Abū Ma'shar's volume has its own Figure 61 and Figures 90, 98–146.
"Figure 61" is ambiguous without naming the volume (Sahl Fig. 61 = "Frequency of illness,"
Sahl p. 574, in `on_nativities.md`; Abū Ma'shar Fig. 61 = the degrees of brightness, V.20, GI p. 306 [corrected 2026-09-08; an earlier draft here said "the aspect-conditions table"],
in `abu_mashar_book_vii.md`). Paragraph numbers restart per chapter in every work.

## The table

| File | Printed pages | Sections present | Figures | New / newly legible |
|---|---|---|---|---|
| `sahl_editors_introduction.md` | Sahl 1–39 (39 markers) | 14 headings; Dykes's editorial preamble, sources, manuscript sigla | Sahl 1–2 | **New to reconciliation.** Not doctrine, but carries the sigla and the "not always mutually compatible" warnings that later phases will need to read footnotes. |
| `sahl_frontmatter_reference.md` | — (front matter) | Printed contents + the full **list of Figures 1–71 with page numbers** | names all 71 | **New.** The authoritative figure→page index for Sahl Vol. I; settles the Figure-61 collision above. |
| `sahl_introduction_zodiac_chapters.md` | Sahl 41–51 (11) | *Introduction* Ch. 1 (categories of the signs), Ch. 2 (essences of the twelve houses) | Sahl 3–8 | **New whole chapters.** `app.py` cites "Introduction Ch.2" 6× and "Ch.3" 39×, but Ch. 1 not at all. Figs. 5–7 are the 8-place vs 7-place good-places systems; Fig. 3 crooked/straight signs; Fig. 4 triplicity lords. |
| `sahl_introduction_ch3.md` | Sahl 53–75 (23) | Ch. 3 complete (¶1–132) + a standalone Ch. V.20 supplement | Sahl 9–29; cross-refs Abū Ma'shar 60–61 | Previously reconciled. Change since 09-06: the bad p. 75 image sliver was removed (p. 75 confirmed prose-only); fn. 110 now points at Abū Ma'shar's Fig. 61 instead of nothing. |
| `fifty_aphorisms.md` | Sahl 76–88 (unmarked in file) | All 50 aphorisms, ¶1–107 continuous | Sahl 30–31 | Previously reconciled. Change since 09-06: Aphorism 45's policy decided (implement the editor's **ascensional**-degree correction, not the printed zodiacal wording); fn. 61 Arabic resolved. |
| `sahl_on_questions.md` | Sahl 89–193 (105) | 18 chapters (one per house 1–12, with Ch. 7 split into 7.1–7.7, then books/messengers, reports, retaliation, multiple options, hunting, meals); ¶ restart per chapter, ~1,160 numbered sentences total | Sahl 32–43 | **New whole work.** Zero citations in `app.py`. Figs. 33–34 are a *worked question chart, MS values vs modern calculation* — a directly testable fixture. |
| `sahl_on_choices.md` | Sahl 194–231 (38) | 13 chapters by house + general principles + sign natures | none | **New whole work.** Zero citations in `app.py`. |
| `sahl_on_times.md` | Sahl 232–254 (23) | 11 chapters: aphorisms of times, extracting the indicator of time, then per-house timing, wars, travels, Māshā'allāh on reports and the Sultan | Sahl 44–47 | **New whole work.** Zero citations in `app.py`. **Timing-adjacent — see the scope note below.** Figs. 46–47 (time units by sign/planet; planetary years) verified cell-by-cell against source photos 2026-09-07. |
| `on_nativities.md` | Sahl 255–749 (495, no gaps) | 17 books / 135 subchapters | Sahl 48–71 | Previously reconciled (85 `app.py` mentions). Change since 09-06: four Arabic "reading X for X" collapses resolved by photo (pp. 360, 507, 687, 705). Figs. 64–70 are seven worked *spear-bearing* charts (pp. 717–723) — testable fixtures. |
| `abu_mashar_book_vii.md` | **Abū Ma'shar GI** 407–498 (92) | **All nine chapters VII.1–VII.9**, plus TOC and fns. 1–329 | AM 61, 90, 98–146 | Previously reconciled through VII.6. **VII.7–VII.9 (pp. 485–498) added 2026-09-07** — genuinely new doctrine, and `app.py:4150`'s coverage entry ("The chapter begins on a page not photographed") is now false. VII.7 = Ptolemy's ascensional ray-casting; VII.8 = *fardārs* and planetary years (**timing — deferred**); VII.9 = planetary natures. Fig. 146 (planetary years) was corrupt and is now fixed; the TOC and fns. 1–2 were dropped by a merge bug and have been restored. |
| `sahl_appendix_a_sixty_six_sections.md` | Sahl 750–758 (9) | 66 numbered sections | none | **New.** Zero citations in `app.py`. S53 carries a `<missing>` lacuna — excluded from synthesis. |
| `sahl_appendix_b_lord_of_ascendant.md` | Sahl 759–765 (7) | Connections of the lord of the Ascendant, ¶1–72 | none | **New.** Zero citations in `app.py`. Five `<missing>`/`[uncertain]` marks (¶12, 20, 43, 45, 48); no source photos exist for this file at all. |
| `sahl_glossary.md` | Sahl 771–797 (27) | ~220 term entries | none | **New.** `app.py`'s 4 "Glossary" references are all to the *TNAC Course Glossary*, a different document; Sahl's own glossary has never been read against the code. |

**Decided exclusions** (per `CORPUS_MANIFEST.md`, not gaps): Sahl p. 40 (probable divider),
Appendix C pp. 766–770, Bibliography p. 798+.

## Scope note — *On the Revolutions of the Years of Nativities*

**The consolidated corpus does not contain it.** Timing and prediction stay deferred; this pass
proceeds.

Acquisition has, however, started and is visible in the OCR project:
`/home/apothic/Downloads/Persian Nativities IV On the Revolutions of the Years of Nativities
(Benjamin N. Dykes).pdf` (33 MB), 60 raw photos under
`persian_nativities_iv/front_matter_editors_introductions_raw/` (front matter and editors'
introductions only), and a marker test run (`run_marker_pn4_test.py`, pages 19–24) whose output
`pn4_test_output/.../*.md` is **0 bytes** — the run produced nothing. So: no clean OCR, no
chapter text, nothing to synthesize.

One caution for later phases: Sahl's *On Times* is now in the corpus and is a timing work in its
own right (indicator of time, per-house timing, planetary years). It is Sahl's, not Abū Ma'shar's
*Revolutions*, so it does not lift the deferral — but Phase 1 will surface timing doctrine, and a
decision will be needed on whether Sahl-only timing counts as in scope.

## Delta summary

Nine of the thirteen files are new to code reconciliation, roughly **+1.0 MB against the ~1.5 MB
previously read** — three complete works (*On Questions*, *On Choices*, *On Times*), two
appendices, Sahl's own glossary, *Introduction* Ch. 1–2, the editor's introduction, and the
front-matter figure index; plus Abū Ma'shar VII.7–VII.9 inside an already-known file.

**This is not a small delta.** Phases 1–3 should be scoped accordingly.
