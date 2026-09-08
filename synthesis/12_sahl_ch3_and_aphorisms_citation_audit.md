# Sahl *Introduction* Ch. 3 and *Fifty Aphorisms* citation audit — every `app.py` claim, checked

Both audits are in this one file (the brief left the choice open): §A is Ch. 3, §B the Aphorisms.
Baseline: `synthesis-completion-2026-09-08` @ `b43bd5a` (main `44cf571` + the Phase 1a commits),
1021 passed / 2 xfailed. Date: 2026-09-08. **`app.py:LINE` numbers are as of `b43bd5a`**; the two
corrections in §5 add one line at `:2192`, so positions after it shift by +1.

## 1. Method

1. Read both texts end to end (`sahl_introduction_ch3.md` 596 lines; `fifty_aphorisms.md` 281
   lines) before opening a citation; the Phase 1 records are `01_sahl_introduction_ch3.md` and
   `01_fifty_aphorisms.md`.
2. **Ch. 3 surface**: every line matching `Ch. 3, N` / `Ch.3, N` / `Introduction Ch.3` that refers
   to Sahl's *Introduction* — **79 lines**. (A bare grep for `Ch. 3` returns 83; four of those are
   *On Nativities* Ch. 3.11 and are excluded. The brief's "42 lines, 30 locators" counts
   differently; the 79 lines are the audit unit.)
3. **Aphorisms surface**: every line containing "Aphorism" — **17 lines**, as the brief says.
4. Same five classes as the earlier audits. Claims on these lines about Book VII or *On Nativities*
   were judged in `10_…` and `11_…`.

## 2. Counts

| Class | Ch. 3 (79 lines) | Aphorisms (17 lines) |
|---|---|---|
| supported | **77** | **17** |
| paraphrase-fair | 2 | 0 |
| paraphrase-misleading | 0 | 0 |
| unsupported | 0 | 0 |
| passage-not-found | 0 | 0 |

**The Aphorisms citations are all supported, and every Ch. 3 locator points at the sentence it
claims.** The two paraphrase-fair rows are a Dykes footnote's paraphrase quoted as if it were ¶76's
own words, and ¶74's own parenthesis described as "a footnote". No locator is wrong; nothing was
found that pins would have caught. The "previously reconciled" judgment held for these two texts.

## 3A. Ch. 3 — the table

Runs of lines sharing one verdict are collapsed. `:N` is `sahl_introduction_ch3.md`. ✓ = wording
matches.

| `app.py` | Claims | Text | Class |
|---|---|---|---|
| 756–757 | Ch. 3, 87 "with him in one degree" | ¶87 `:330` ✓ | supported |
| 1011–1013, 1370–1371 | Fig. 105's orbs "identical to Sahl's 'light' figures (Ch. 3, 12–18)" | ¶13–17 `:34`: 15 (half of 30) / 12 / 9 / 8 / 7 ✓ | supported |
| 1050–1052 | "light"/"heavy" as nouns at 6–8, 22, 67 | ✓ | supported |
| 1171–1174, 7169 | ¶6 quoted; ¶67 quoted | `:20`, `:258` ✓ verbatim | supported |
| 1239–1246, 1629–1631, 1839–1845, 7396–7399 | ¶20–21 quoted; fn. 58 "not see … still connected" | `:38–54`, fn. 58 `:60` ✓ | supported |
| 1317–1318 | ¶23 looking sign-to-sign, connecting degree-to-degree | ✓ | supported |
| 1324–1326, 2016–2017, 7396–7397 | Ch. 3, 6–21 / 13–19: the applying planet's own light governs | ¶19 ✓ | supported |
| 1486–1487, 1627, 1643–1644, 1680–1681, 7172 | transfer Ch. 3, 24–27; ¶24 quoted | `:58` ✓ | supported |
| 1715, 7174 | collection Ch. 3, 28–30 | ✓ | supported |
| 1758–1760, 1822–1823, 7227–7228, 7295 | banished, ¶64 quoted | `:230` ✓ | supported |
| 2024–2032, 2055–2057, 2085, 2124, 7201, 7211–7212, 7223–7224 | blocking: intervention 35–37, nullification 38–48, cutting 31–34 and 44–48 | ✓ (fn. 64 names) | supported |
| 2156–2161 | Fig. 14 has the Moon 13° from her opposition to Saturn, outside her 12° light (13–17), still called a connection about to be cut — "an inconsistency in the source" | ¶42–43: Moon 10° Scorpio, Saturn 23° Taurus ✓; ¶14 12° ✓; ¶43 *"cutting the aspect"* ✓ | supported |
| 2191 | handing over Ch. 3, 70–76, three grades | ✓ (fn. 90) | supported |
| **2192–2193** | *Management (76, "any application or connection hands over management")* | ¶76 `:280` reads *"in signs other than these two, she only hands over management."* The quoted words are **fn. 90's** (`:286`): *"In 76, Sahl says that any application or connection hands over management"* | paraphrase-fair — wording corrected |
| 2194–2196 | power 70–72 from own house, exaltation or triplicity | ¶70 ✓ | supported |
| **2196–2198** | *Nature (73–74, confirmed by the worked example's own footnote — "that is, in reception")* | the words are ¶74's **own parenthesis** `:280`, not a footnote | paraphrase-fair — wording corrected |
| 2379–2380, 2691–2697 | ¶44 precedence; fn. 68 quoted | `:124`, `:134` ✓ verbatim | supported |
| 2440–2452, 4281, 7189–7190 | returning 65–69, two manners; ¶65 quoted | `:240–258` ✓ | supported |
| 2494–2497 | ¶117 quoted (to say it is *not* the passage) | `:467` ✓ | supported |
| 2710–2716 | Fig. 12's numbers: Virgo rising, Mercury 10 Cancer, Jupiter 15 Pisces, Mars 13 Aries, ~3° from the square | ¶33 `:96–106` ✓ | supported |
| 2977–2992, 7185 | reception 49–55: one direction; ¶52 quoted; "perfect … truthful intention" (49); triplicity "below this reception" (50); bound only with triplicity, Māshā'allāh (54–55), confirmed by VII.5 fn. 207; face never appears; ¶56 and fn. 75 quoted; ¶57 quoted | `:158–176` ✓ all; fn. 207 `abu_mashar_book_vii.md:1545` ✓ | supported |
| 3417–3440, 7186–7188 | non-reception 58–62, Fig. 18, Kinds I–V; ¶60's five examples; ¶61's parenthetical "house or exaltation" | `:178–212` ✓ (Fig. 18 in the OCR as a table) | supported |
| 4297–4298, 4470–4472, 5555, 6990–6999 | Sahl's "advancing" = Ch. 3, 4 (stake or succedent); Fig. 9 shades | `:12–18` ✓ | supported |
| 4527–4528 | ¶108 last degrees = infortunes' bounds | `:429` ✓ | supported |
| 4681–4683, 4737–4739, 5762–5763, 7176–7177 | enclosure 119–123, Fig. 25; 7° grade | `:495` ✓ | supported |
| 4761–4762 | ¶110 "end of Libra and the beginning of Scorpio", fn. 120's 19♎–3♏ | `:433`, `:469` ✓ | supported |
| 4783–4784, 4791–4793, 7237–7240 | strength 78–88 eleven; ¶78 "of the places which look at the Ascendant"; fn. 95 on 83 quoted | `:294–332`; fn. 95 `:318` ✓ verbatim | supported |
| 5003–5005, 7241–7244 | weakness 91–100 ten; the list at 7244 | `:338–364` ✓ (with the Node "if it does not have latitude") | supported |
| 5123–5124 | 12° orb for the Node from Ch. 3, 107 | ¶107 `:427` *"less than 12° between them"* ✓ | supported |
| 5139–5141, 5298–5300, 5781–5783, 5857–5859, 5964–5975, 7245–7246, 7288 | Moon's ten 103–112; ¶112 quoted; the four Abū Ma'shar items absent from Sahl; Sahl's own fall / fallen planet / wildness absent from Abū Ma'shar | `:419–461` ✓ | supported |
| 5594–5598 | emptiness Ch. 3, 63, Fig. 19; "confirmed as his own addition by Dykes' footnote on 63" | fn. 85 `:244` *"In Abū Ma'shar's Gr. Intr. this is sharpened so that she does not complete a connection with any planet while in her current sign"* ✓ | supported |
| 7077 | "Sect: Sahl, The Introduction Ch.3, 85" | ¶85 (glow: masculine by day, feminine by night; fn. 97 calls the gender wording an error) — fair as a sect label | supported |
| 7166, 7171, 7180, 7223, 7232 | group headings Ch. 3, 6–21 / 24–30 and 119–123 / 49–76 / 31–48 / 77–112 | ✓ | supported |
| 7182 | handing over: Power when the giver is in own house, exaltation or triplicity; Nature when the receiver is the ruler | ¶70, ¶73 ✓ | supported |

## 3B. Aphorisms — the table

| `app.py` | Claims | Text (`fifty_aphorisms.md`) | Class |
|---|---|---|---|
| 756–757 | #40, 79 "with him in one degree" | `:211` ✓ | supported |
| 935–937 | #48, 99–102 quoted | `:260` ✓ verbatim | supported |
| 1189–1191 | note on #19: "it would only be possible for Saturn to be the one handing over if he is retrograde" | fn. 24 `:115` ✓ verbatim | supported |
| 3497–3498, 4829–4831, 5560–5562, 7234, 7240, 7424 | #44, 87–89 / 88 quoted | `:230–252` ✓ | supported |
| 3509–3511 | *Nativities* 1.22, 9's footnote cross-references #44 | fn. 176 there ✓ | supported |
| 3514–3516 | #44, 88 states the rule for the stakes | ✓ | supported |
| 3529–3531 | fn. on #44: "as measured in diurnal motion, hence Sahl's reference to the 'rear' of the stake" | fn. 56 `:262` ✓ verbatim | supported |
| 3539–3540 | #44, 88 about the stakes | ✓ | supported |
| 4311–4313 | #45 "misstated there per Dykes' note 57" | fn. 57 `:264` ✓ | supported |
| 4352–4354, 7023 | #44, 87 quoted | `:230` ✓ | supported |
| 4360–4362, 7023 | #15, 31–33 quoted | `:77` ✓ verbatim | supported |

## 4. What could not be verified

- Nothing in either text was unverifiable: both files are short, fully paginated by the printed
  contents, and every cited sentence exists. The only figures relied on (Figs. 12, 14, 18, 24) have
  their data in the prose or in OCR tables.
- The `:1011` claim that Sahl's lights are "identical" to Fig. 105 is verified on the numbers; the
  Sun's is stated as a 30° body (¶13) with 15° each side, which is the same fact.

## 5. Corrections applied (wording only, line count unchanged)

| Line | Before | After |
|---|---|---|
| 2192–2193 | `Management (76, "any application or connection hands over management")` | `Management (76, "in signs other than these two, she only hands over management"; fn. 90: "any application or connection hands over management")` |
| 2197 | `confirmed by the worked example's own footnote -- "that is, in reception"` | `confirmed by the worked example's own parenthesis at 74 -- "that is, in reception"` |

**What moves for users:** nothing; both are docstrings.

## 6. The pins — `tests/test_sahl_citations.py`

- **Ch. 3 paragraph range**: every `Ch. 3, N` / `Ch.3, N` / `Introduction Ch.3, N` (and each end of
  `N-M`) satisfies `2 ≤ N ≤ 132`; the corpus-present test re-derives the maximum from the file.
  Coverage: every Ch. 3 paragraph citation in `app.py`. It would catch a citation to a
  non-existent sentence; it cannot tell ¶65 from ¶66.
- **Aphorism number and sentence**: every `Aphorism(s) #N` has `1 ≤ N ≤ 50`, and every `#N, S`
  (and range) has `S` inside aphorism N's own sentence span, vendored from the *"The Nth:"* markers
  (50 spans, 2–107). The corpus-present test re-derives the spans from the file. Coverage: every
  Aphorism citation in `app.py`. This is the strongest pin of the three passes, because the
  aphorism boundaries make a sentence number checkable against a *topic*, not just a maximum —
  `#44, 90` would fail.

Both pass on the baseline (there was nothing to catch) and after the two wording changes.
