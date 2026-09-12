# Abū Ma'shar Book VII citation audit — every `app.py` claim about VII.1–6, checked against the text

Baseline: `main` @ `44cf571`, 1018 passed / 2 xfailed. Branch `synthesis-completion-2026-09-08`.
Date: 2026-09-08. Phase 1a of the completion brief.

**`app.py:LINE` numbers are the baseline's (44cf571).** The corrections in §5 add three lines
(two at `:851`, one at `:4263`), so post-fix positions from `:851` on shift by up to +3.

## 1. Method

1. Read VII.1–6 end to end (`abu_mashar_book_vii.md:1–1809`, four slices) before opening any
   citation; the Phase 1 record is `01_abu_mashar_vii_1_to_6.md`. VII.7 was re-read for the one
   coverage entry that quotes it (`:4283–4291`); VII.8–9 are covered by the earlier artifact.
2. Listed every line of `app.py` containing `VII.`: **200 lines**. From them the extractor in
   `tests/test_abu_mashar_citations.py` pulls **115 distinct chapter-paragraph tokens**
   (`VII.N, P`, `VII.N, P-Q`, `VII.N, P and Q`); the brief's "89 distinct locators" counts
   differently and is not reconciled — the 200 lines are the audit unit.
3. Each line was compared with the cited sentence(s), with the same five classes as the *On
   Nativities* audit (`10_…` §1). Lines that cite Book VII only as a label ("the VII.6 table") are
   **supported** when the label is true of the chapter.
4. Claims a line makes about *other* sources (Sahl Ch. 3, the Aphorisms, al-Bīrūnī) are not judged
   here; §4 lists them for Phases 1b–1c.

## 2. Counts

| Class | Lines |
|---|---|
| supported | **193** |
| paraphrase-fair | 2 |
| paraphrase-misleading | 2 |
| unsupported | 0 |
| passage-not-found | 3 |
| **Total** | **200** |

**Not "all supported", but close: 193 of 200 are clean as written.** No computed value was wrong at
any site. The three passage-not-found rows are two copies of one wrong paragraph number
(`VII.5, 120` for the Resistance sentence at ¶118) and one wrong chapter (`VII.3, 19-20` for
VII.6, 19–20). The two misleading rows are a footnote attributed to the wrong paragraph with its
content over-stated (`:851`) and a wrong page-recovery claim (`:4263`).

**Decay check.** The brief expected citations written against the pre-repair file to have decayed.
None did: every quotation checked matches the current OCR word for word, including the passages on
the recovered pages (VII.4, 97–109 on pp. 440–442; VII.5, 32–52 on pp. 452–454; VII.5, 134–142 on
p. 477). The `:4263` page claim is the only candidate for decay (see its row) and is classified as
an error rather than decay because pp. 450–451 were never among the recovered pages.

## 3. The table

Runs of lines that share one verdict are collapsed. `:N` in the Text column is
`abu_mashar_book_vii.md`. ✓ = wording matches.

| `app.py` | Claims | Text | Class |
|---|---|---|---|
| 117 | ephemeris ids defined "with the VII.6 material" | label | supported |
| 134–137 | VII.1 = conditions in themselves; VII.6, 22 and 38 distinguish "rising up in the north" from "northern" and "going down in the south" from "southern" | ¶22 `:1636`, ¶38 `:1682` ✓ | supported |
| 642–643, 650 | Abū Ma'shar's domain = VII.1, 37 / VII.6, 13, sign gender fixed to the planet's own | ✓ | supported |
| 670–671 | VII.6 station tests are 24 and 32 | ¶24 second station (strength), ¶32 first station (weakness) ✓ | supported |
| 683–684 | seventeen conditions (6–34), sixteen (35–57), sixteen (58–74) | ¶6, ¶35, ¶58 ✓ | supported |
| 695, 697 | ♄♃ burned 6, rays 15; ♂ 10, 18 (VII.2, 11–13) | ¶11, ¶13 ✓ | supported |
| 699–706 | ♀☿ 7 / 12 east / 15 west (VII.2, 40, 48, 51–52); ¶37 and ¶40 quoted; ¶44's 6 flagged | ¶37 `:281` ✓ verbatim; ¶40 ✓; ¶44 + fn. 43 ✓ | supported |
| 707–708 | Moon 6 / 12 (VII.2, 60–61, 72–74) | ✓ | supported |
| 717–719 | fifteenth condition "in the degrees of setting" 22→15 (VII.2, 30–31) | ✓ (Mars 18→15) | supported |
| 734, 6959, 7431 | Moon 12 (VII.2, 61, 72–73) | ✓ | supported |
| 740–743 | VII.2, 30 quoted; 31 "degrees of setting" to 15 | `:255–257` ✓ verbatim | supported |
| 748–753, 7251–7254, 7425–7428 | VII.6, 27/45 read by hemisphere (VII.2, 2) or the bands VII.2, 14–21 / 29–31 name | ✓ | supported |
| 754–756, 7124 | in the heart 16′ from a ≈32′ disc (VII.2, 7–9); "Dykes notes that al-Bīrūnī has 16′ as well" | ¶7–8 ✓; the al-Bīrūnī remark is Dykes's comment on *Nativities* 1.22 (`on_nativities.md:1085`), accurate | supported |
| 763, 963 | solar phase per VII.2 | label | supported |
| 848–850 | VII.1, 37 quoted, "again at VII.6, 13" | `:137–155` ✓ verbatim | supported |
| **851** | *"Al-Qabisi I.78 has the same (Dykes' note on VII.6, 13)"* | The al-Qabīsī note is **fn. 222 on VII.6, 10** (*halb*), and what it attributes to al-Qabīsī is *"a sect-related rejoicing condition: that diurnal planets are above the earth in the day but below it by night"* — the hemisphere half only, no sign gender. The note on ¶13 (fn. 223) says only *"See also VII.1, 37-39."* | **paraphrase-misleading** — corrected |
| 858–864 | VII.6, 13 has no Mars exception; fn. 24 on VII.1, 37 quoted | ¶13 ✓; fn. 24 `:149` ✓ | supported |
| 902–906, 5530–5534 | VII.6, 36 quoted; VII.1, 39 the milder single-failure case | ¶36 `:1666` ✓; ¶39 ✓ | supported |
| 915–919, 5499–5501 | VII.1, 29 quoted; 30–31 except the inferiors (Sun's motion that day) | `:113–127` ✓ verbatim | supported |
| 934–937 | stations = seventh and eleventh conditions (VII.2, 23, 27); VII.6 weakness 32 / strength 24 | ✓ | supported |
| 1009–1011 | Fig. 105 orbs | `:428–434` ✓ (the "identical to Sahl Ch. 3, 12–18" half → Phase 1b) | supported |
| 1098–1103, 1370–1373, 7166 (first clause), 7403 | VII.3, 6–11; VII.4, 5–8; VII.4, 7 Saturn/Moon 12 vs "a little under 9" | ¶7 `:458` ✓ | supported |
| 1119–1121, 1178–1180, 1611–1613, 7166 | VII.5, 24 quoted | `:990` ✓ verbatim | supported |
| 1126–1127, 1185–1187, 7166 | note on VII.5, 130: Saturn "could never be received … unless by retrogradation" | fn. 206 `:1543` ✓ | supported |
| **1181–1182** | *"His Cutting the Light turns on it -- 'the light one IN MORE DEGREES goes retrograde and connects with the heavy one through its retrogradation' (VII.5, 120)"* | ¶120 is *"CUTTING OF LIGHT is of three types."* The quoted words are **¶118, Resistance** (`:1423–1429`). Cutting #1 (¶121) does involve a retrograde entrant, but the sentence quoted is not from it | **passage-not-found** — corrected |
| 1183–1185 | Fig. 138's Resistance has Venus retrograde connecting with the lighter Mercury | fn. 196 ✓ | supported |
| 1416–1420 | assembly same-sign (VII.4, 3), power from 15° | ¶3 ✓ | supported |
| 1421–1425 | VII.5, 27 quoted; "per the note there" aspect rays have no orbs | ¶27 `:1010` ✓ verbatim; the note is **fn. 146 on ¶28**, not on 27 | paraphrase-fair (adjacent note) |
| 1427–1431, 1532–1534, 1636–1637, 2405, 7409 | VII.4, 13 and VII.5, 14 quoted; no out-of-sign connection | ¶13 `:486` ✓; ¶14 `:954` ✓ | supported |
| 1465–1475 | VII.5, 34 (1′); VII.6, 4 and 57 quoted; VII.5, 17 and 35 quoted | `:1066`, `:1586`, `:1738`, `:958`, `:1066` ✓ | supported |
| 1508, 1519–1523, 1563, 1589 | VII.3–4; VII.4, 5–8 grading by bodies and shared bound | ¶5–8 ✓ | supported |
| 1578–1580, 7166 | VII.5, 4 quoted, Fig. 111 | `:891–893` ✓ | supported |
| 1642–1644, 7169 | two transfer types are Abū Ma'shar's (VII.5, 83–85, Fig. 126) | ✓ | supported |
| 1714 | VII.5, 86, Fig. 127 | ✓ | supported |
| 1767, 1814–1816, 7290 | wildness = no planet looks (VII.5, 79–82, Fig. 125); fn. 166 gloss | ✓ | supported |
| 1847–1849, 1906, 3212–3214, 7286 | natural connections VII.5, 53–77; ¶53 quoted; pairs at 56 and 67–75; 134 is acceptance | ✓ | supported |
| 1964–1966, 7293 | reflection VII.5, 87–89, Figs. 128–129; 89 = transfer for an aversion pair | ✓ | supported |
| 1996–1998 | VII.5, 3 quoted | ✓ | supported |
| 2014–2016 | flat 12° (VII.5, 27) | ✓ | supported |
| 2023–2032, 2085–2087, 2124–2126, 7199, 7221 | Blocking I = VII.5, 91–92 fn. 172 (Sahl's Intervention); II = 93–94 fn. 174 (Nullification); ¶91, ¶93 quoted | `:1272`, `:1276`, `:1284`, `:1292` ✓ | supported |
| 2046–2048, 2134–2136 | VII.5, 94 exception quoted | `:1290` ✓ | supported |
| 2104–2105 | VII.5, 10 "direct in motion" | ✓ | supported |
| 2199–2201, 4275 | two natures VII.5, 97–100, not in Sahl | ¶97–100 ✓ (Sahl half → 1b) | supported |
| 2244–2246 | VII.5's motion-dependent conditions | ✓ | supported |
| 2378–2380 | VII.5, 121 and its note read the verb as "conjoins" by degree | fn. 198 `:1461` ✓ | supported |
| 2489–2491 | VII.5, 117 quoted | `:1393` ✓ verbatim | supported |
| 2537, 7214 | VII.5, 118 Fig. 138; 117–119 | ✓ | supported |
| 2615–2617 | VII.5, 119 quoted | ✓ | supported |
| 2717–2721, 2747, 7207–7209, 7223 | cutting VII.5, 120–125; I–II (121–124) Abū Ma'shar's own; III (125) | ✓ | supported |
| 2905–2907 | VII.5, 127 quoted | `:1502–1508` ✓ | supported |
| 2943–2945, 7295 | favor: a planet in Fall or a Well "pulled out by a connecting dispositor" | ¶126: also *"friendly towards it"* and *"the one handing over or the one accepting has testimony in its own sign"* — wider than dispositor | paraphrase-fair |
| 3017–3019, 5317–5318, 7182 | reception VII.5, 129–133; grades 136–142; 137 "detestable"; 139 Mercury from Virgo; 140 middling incl. house; 141 strong | `:1541`, `:1557–1579` ✓ | supported |
| 4261–4262 | VII.5, 29–31: priority by claims, bound lord breaks ties | ¶29–31 ✓ | supported |
| **4263** | *"Recovered with p. 452"* | ¶29 is on **p. 450** (`:1030`, after the marker at `:1020`) and ¶30–31 on **p. 451**; the p. 452 recovery begins mid-¶32. Only the p. 440/442/452/453/477 pages were ever recovered | **paraphrase-misleading** — corrected |
| 4264–4267 | latitude VII.5, 38–52, three kinds, recovered with pp. 452–453 | ✓ (¶38–39 p. 452, ¶40–49 p. 453, ¶50–52 p. 454) | supported |
| 4268–4274 | natural pairs from 56 and 67–75; three omitted per notes 163–164 | ✓ | supported |
| 4277 | returning tree VII.5, 104–116 | ✓ | supported |
| 4279–4280 | VII.6, 13 and 36 male/female degrees; "No table for them in this corpus" | grep of all 15 files: only these two mentions, no table ✓ | supported |
| 4281 | VII.6, 52 own Dragons | ✓ | supported |
| 4283–4291 | VII.7 complete at 1–22 (pp. 485–487): hours 4–13, ray from right and oblique ascensions corrected by the hours 14–19, ¶22 opposition quoted | re-read `:1810–1855`: pp. 485–487 ✓; ¶4–13 ✓; ¶14–19 ✓; ¶22 ✓ verbatim | supported |
| 4292–4296, 4463–4471, 4500 | VII.3, 2 / VI.26, 3 quadrants; VII.3, 2–5 quoted | `:418–424` ✓; fn. 52 ✓ | supported |
| 4297–4299 | VII.5, 32–33 by ray across a boundary; Fig. 121: Moon 29°59′ Aquarius, Saturn's trine at 1° Pisces | ¶32–33 ✓; fn. 149 describes the figure without degrees — **the degrees are in the image only, not verified** | supported (figure not checked) |
| 4389 | supporting data from VII.3–4 and V.20 | label | supported |
| **4419–4421** | *"Great Introduction VII.3, 19-20: for the five non-luminaries, the domicile in which their nature is 'moderated'"* | VII.3 has 11 sentences. The passage is **VII.6, 19–20** (`:1618–1620`) | **passage-not-found** — corrected |
| 4438–4440 | VII.6, 28 names the quadrants, defined at IV.8, 16 | fn. 228 ✓ | supported |
| 4503 | VII.6, 23 apogee | ✓ | supported |
| 4517, 4525, 4531–4532 | VII.6, 12 received; 72 end of signs = infortunes' bounds; 48 quoted | ✓ | supported |
| 4542–4543, 4553, 4690, 4736–4738, 5757–5762, 5775 | enclosure VII.6, 56–62; 58 "by its body or rays"; 5 and 62 fortunes | ✓ | supported |
| 4760 | VII.6, 40 harsh band 19♎–3♏ | ✓ | supported |
| 4809, 5007 | labels | — | supported |
| 5133–5135, 5247, 5377, 5497, 5669, 5777, 5818, 7249, 7260 | the four groups 1–20 / 21–29 / 30–46 / 47–62 and the Moon 63–74 | ✓ | supported |
| 5182–5185, 5654–5659 | 46's "beginning of easternization" = VII.2, 40–41's 12°; ¶40 quoted | ✓ | supported |
| 5248–5249 | VII.6, 2 quoted | ✓ | supported |
| 5286–5300 | VII.1, 19–21 light = falling from apogee; 23–25 number, fn. 14 "no direct astrological import"; VII.2, 62–71 glow; VII.1, 22 "the one agreed upon" | ✓ all four | supported |
| 5378–5381 | VII.6, 22; VII.1, 34–35 maximum 90° past the Head | ✓ | supported |
| 5398–5413 | VII.6, 25 "going out of the rays"; VII.2, 12 quoted; 32 denies the greater years on the setting side; VII.6, 34 | `:201`, `:259`, `:1662` ✓ | supported |
| 5445–5457 | VII.6, 27 quoted with the sextile clause; fn. 227 → VII.2, 17–18; VII.2, 2; 14; VII.6, 34; bands | ✓ | supported |
| 5597–5599 | VII.5, 78, Fig. 124 | ✓ ("Dykes' footnote on 63" is Sahl Ch. 3 → 1b) | supported |
| 5670–5671, 5755 | VII.6, 48 quoted; nodes 52–55 | ✓ | supported |
| 5786–5789, 6306–6309, 7086, 7272, 7280 | VII.6 never totals, weights or tie-breaks | true on the full read | supported |
| 5839–5842 | VII.6, 68 twelfth-part; VII.4, 2 twelfth-parts among assembly partners | ✓ | supported |
| 5851–5862, 5962–5966 | eleven corruptions VII.6, 63–74, one per paragraph | ✓ | supported |
| 7056, 7074, 7127 | VII.1, 37–39 / VII.6, 13 | ✓ | supported |
| 7118–7124 | solar phase per VII.2; 16′ (7–9) | ✓ | supported |
| **7166** (second VII.5 citation) | *"VII.5, 120 ('the light one IN MORE DEGREES goes retrograde and connects with the heavy one')"* | ¶118 (Resistance), as at `:1182` | **passage-not-found** — corrected |
| 7407 | assembly within 15° in one sign (VII.4, 3), aspects within 12° (VII.5, 27) | ✓ | supported |

## 4. What could not be verified here, and what is deferred to 1b–1c

- **Figure 121's degrees** (`:4298`): the OCR has the caption and fn. 149 only; the 29°59′ / 1°
  Pisces are in the image, not opened.
- **al-Bīrūnī** (`:686`, `:755`, `:7119`): outside the corpus; taken from Dykes's comment on
  *Nativities* 1.22.
- **Claims about Sahl made on VII-citing lines**, to be judged in Phase 1b: Fig. 105 "identical to
  Sahl's light figures (Ch. 3, 12–18)" (`:1010`, `:1370`); "two natures … doesn't appear anywhere
  in Sahl" (`:2200`); "Dykes' footnote on 63" (`:5598`); Sahl's ten Moon defects vs the eleven
  (`:5858`); Sahl Ch. 3, 87 "one degree" for the heart (`:756`).
- **Claims about the Aphorisms** on the same lines, Phase 1c: #40, 79 (`:757`); #48, 99–102
  (`:934`); the note at `:1187`.
- **IV.8, 16** (the male quadrants) and **V.21** (the wells): outside the corpus; the citations say
  so.

## 5. Corrections applied (citation text only)

| Line | Before | After |
|---|---|---|
| 850–851 | `Al-Qabisi I.78 has the same (Dykes' note on VII.6, 13).` | `Al-Qabisi I.78 has the hemisphere-by-sect half only (Dykes' note 222 on VII.6, 10, glossing halb; the note on 13 itself just points back to VII.1, 37-39).` |
| 1180, 1182 | `His Cutting the Light turns on it -- "…" (VII.5, 120)` | `His Resistance turns on it -- "…" (VII.5, 118)` |
| 4263 | `Recovered with p. 452; computable, not yet built.` | `Sentences 29-31 are on pp. 450-451; 32-39 came with the p. 452 recovery. Computable, not yet built.` |
| 4419 | `Great Introduction VII.3, 19-20:` | `Great Introduction VII.6, 19-20:` |
| 7166 | `VII.5, 120 ("the light one IN MORE DEGREES …")` | `VII.5, 118 ("the light one IN MORE DEGREES …")` |

**What moves for users:** one displayed note on the Aspects table (row 7166, a paragraph number).
No number changes.

## 6. The pins — `tests/test_abu_mashar_citations.py`

Two mechanical holds, both of which the OCR supports for every citation:

1. **Chapter existence**: every `VII.N` in `app.py` names one of VII.1–VII.9.
2. **Paragraph range**: every `VII.N, P` (and each end of `P-Q`, and each of `P and Q`, `P, Q`)
   satisfies `P ≤ max(N)`, with the maxima vendored from the file — 39 / 75 / 11 / 109 / 142 / 74 /
   22 / 8 / 37. With the corpus on disk, a third test re-derives the maxima from the headings and
   sentence numbers and fails if the vendored list drifts.

On the baseline the range pin fails on exactly `VII.3, 19-20` (max 11), and passes after the
correction. It cannot catch `120` for `118` — both are inside VII.5 — which is the class only a
re-read finds. The brief asked whether VII's OCR would carry the paragraph pin: it does, because
VII's sentence numbers are clean and its footnotes are numbered continuously (no per-chapter
restart to confuse a "44"), unlike *On Nativities*. The maxima were derived by script and each one
checked against the reading.
