# Briefing: build "Directing by Triplicities" (life governed by the three triplicity lords)

Written 2026-09-13, from a session that cross-checked several predictive techniques against
Janus's medieval module and found this one is a real, sourced gap (`docs/synthesis/16_open_features.md`
F-4). This brief hands the research done so far to a fresh session to finish the research and
build it. **Read all of this before writing code — the citation this technique actually rests on
is not settled, and guessing wrong here means shipping a table under the wrong authority.**

---

## 0. What's being asked for

Janus's medieval module prints, for every nativity, a short table headed "Directing by
Triplicities":

```
Age    Ruler
00-30  Venus
30-60  Moon
60-90  Mars
```

(from the natal chart of 29 Oct 1990 13:02 EST, Pontiac, Michigan, 42n38'20 83w17'28 — this
project's own test nativity used throughout the Janus cross-checks this session). Three planets,
in order, each ruling a roughly-30-year stretch of life. This is a real classical technique —
**the three lords of a triplicity governing the native's life in succession** — not something
Janus invented. The question is which primary-source passage grounds it, and this project has
a citation-precision standard (every Lot, dignity, and technique in `app.py` traces to a quoted
passage) that a plausible-looking guess does not satisfy.

## 1. What's already found, and already partially built

**PN IV, Book VI, Chapter VI.2, ¶4-5** (Abū Ma'shar; corpus file
`pn4/pn4_complete/persian_nativities_iv.md`, around p. 430-431) states:

> "**4** For the knowledge of the condition of assets, the Lot of Fortune of the root, and the
> Lot of assets, and the house of assets, are turned and directed — and along with that you look
> at every one of the lords of the triplicities of the luminary which had the shift in the root,
> [to see] what its condition was at that time, and what its condition is in the revolution of
> that year, and especially the lord of the triplicity which indicated his condition at that time
> of his lifespan."
>
> fn. 13: "That is, the triplicity lords of the sect light." fn. 14: "For example, if the native
> was older, one would use the second triplicity lord (or for many Persian- and Arabic-language
> astrologers, the third one)."
>
> "**5** ... then along with that you look at the triplicity lords of the sign in which Mars was
> at the root, [to see] what its condition was at that time and what its condition was in the
> revolution of that year (and the first lord of its triplicity indicates the older ones of the
> siblings, and the second lord of its triplicity indicates the middle ones of the siblings, and
> the third lord of its triplicity indicates the condition of the younger ones of the siblings)."

This is already read, adjudicated, and half-built. The adjudication record
(`process/adjudication/LANE_3A_PN4_READINGS.md`, card **PN4R-4f-6**, 2026-09-10, confidence
**high**) ruled: *"These are stated rules with a stated procedure (which planets, in which order,
judged in root and revolution), not delineation... The omission is a gap, not a refusal."*
[pn4_turning_triplicity_lords()](app.py:10076) implements the IDENTIFICATION of the three lords
(in Dorothean day/night/participating order, reordered by sect) for both VI.2,4 (assets, keyed to
the **sect light**'s sign) and VI.2,5 (siblings, keyed to **Mars's** sign) — but only as rows
beside the "turning" (solar-revolution) technique, each showing the lord's condition in the root
and in the revolution. Its own docstring says: *"fn 14's age mapping is the editor's and is not
applied (order PN4R-4f-6, 2026-09-11)."* That is: Abū Ma'shar's text names the three lords and
says one of them "indicated his condition at that time of his lifespan" — but gives no numbers.
fn. 14 is Dykes' own editorial gloss ("if older, use the second or third"), not Abū Ma'shar's
stated text, and a prior decision on this branch explicitly chose not to build a numeric
age-cutoff on the strength of an editor's aside.

**So the three-lords-in-order machinery already exists and is already sourced.** What Janus adds
— and what this project doesn't have — is (a) a **standalone, whole-life table** (not tucked
inside the yearly "turning" report, and not requiring a solar revolution to compute at all) and
(b) **actual age boundaries** dividing life into three governed stretches.

## 2. The open problem: this project's citation likely does NOT match Janus's data

Before writing a line of code, check this, because it changes which passage you cite.

VI.2,4's triplicity lords are keyed to **the sect light's sign** (Sun by day, Moon by night).
The Pontiac 1990 nativity is **Diurnal**, and its **Sun is at 06° Scorpio** — a **water** sign.
Sahl's own triplicity table (`sahl_introduction_zodiac_chapters.md`, Figure 4; the same table
Abū Ma'shar gives) has water's day/night/participating lords as **Venus / Mars / Moon**. In sect
order for a diurnal chart (day, night, participating) that's **Venus, Mars, Moon** — NOT the
Venus, Moon, Mars that Janus prints.

The nativity's **Ascendant**, though, is at **21° Capricorn** — an **earth** sign. Earth's lords
are day **Venus**, night **Moon**, participating **Mars** (Sahl Fig. 4: *"the lords of this
triplicity are by day Venus, by night the Moon, and their partner... is Mars"*). In diurnal sect
order that's **Venus, Moon, Mars** — an exact match to Janus's table.

**So Janus's "Directing by Triplicities" almost certainly keys off the Ascendant's triplicity,
not the sect light's.** That is a different point than VI.2,4 names. Two live possibilities:

1. There's a separate passage — somewhere in Sahl's *On Nativities* (the house-master material,
   which leans on the Ascendant's triplicity lord constantly — see
   `on_nativities.md` around the house-master years section already cross-referenced from this
   codebase), Dorotheus, or elsewhere in PN IV — that states this life-division using the
   Ascendant specifically. This has **not yet been searched for** by this session; do that first.
2. Janus is applying VI.2,4's mechanism generically to "the most relevant chart point" and picked
   the Ascendant for its own reasons (a common substitution in general astrological software,
   since the Ascendant is often used as a stand-in ruler of "the life" broadly) rather than
   because a specific text says so. If a search turns up nothing else, this should be documented
   as an unsourced (or Janus-convention-only) reading, built if at all as a clearly-labeled
   variant — the same way this codebase already labels `death_ws` as "not prescribed in any
   supplied passage" rather than passing it off as textual.

**Do not default to "Ascendant" just because it fits the one data point above.** One nativity is
not proof; find or rule out a real citation before committing to a point.

## 3. What to actually build, and how to scope the doctrinal parts

Two genuinely separate deliverables here — keep them separate in the code and in commit messages:

**(a) A standalone whole-life table, using the identification machinery that already exists.**
This part is low-risk and already has a "high confidence, GAP" ruling behind it (§1). Given
whichever point (§2) turns out to be correct, get its sign, look up `TRIPLICITY[SIGN_ELEMENT[sign]]`,
and order the three lords by sect (day, night, participating for a diurnal chart; night, day,
participating for nocturnal — see `pn4_turning_triplicity_lords`'s own ordering, which already
gets this right and should be reused or factored out rather than re-derived).

**(b) Age boundaries for each lord's stretch of rule.** This is the part with no numbers in the
primary text (§1). Do not silently pick 0-30/30-60/60-90 (or anything else) and ship it as if it
were stated. Options, in order of how defensible they are without more research:
   - Show the three lords with **no numeric ages at all** — "younger / middle / older," exactly
     as fn. 14 and VI.2,5 phrase it, with no claim about *which* years those are. This is the
     safest reading of what's actually stated.
   - If further corpus research (§2) turns up an actual numbered scheme (e.g. tied to the
     lords'/planets' own "years" — this codebase already has a lesser/middle/greater-years
     apparatus for the house-master; check whether anything analogous is stated for this
     technique specifically), use that, cited precisely.
   - Only use a flat 30-year split (matching Janus) if you find it's what Janus's own
     documentation claims to implement, or if the owner rules that a labelled, admittedly
     non-primary-source convenience reading is acceptable — the same way this project sometimes
     offers a variant row explicitly marked as not stated by any source. **This is an owner
     decision, not a default** — flag it rather than deciding it, matching this project's
     practice of rulings before doctrinal merges (see `docs/synthesis/13_open_decisions.md` for
     the shape those rulings take).

## 4. Where things live

- **Read first:** `pn4/pn4_complete/persian_nativities_iv.md` (VI.2, 4-5 and surrounding ¶s, in
  the corpus repo — private, never push changes there from this branch) — also skim VI.2's
  opening (¶1-3) for context on "turning" vs "direction" in case it bears on the age question.
  Also search `on_nativities.md` and `sahl_introduction_zodiac_chapters.md` for anything keying a
  life-division to the Ascendant's triplicity specifically (§2).
- **Existing code to reuse:** [pn4_turning_triplicity_lords()](app.py:10076) (the lord-ordering
  logic), `TRIPLICITY` / `SIGN_ELEMENT` (the triplicity table itself), `chart_data['sect']`
  (day/night ordering).
- **Existing test to extend:** `tests/test_doctrine_fixtures.py`,
  `test_turning_triplicity_lords_for_assets_and_siblings` (search `PN4R-4f-6`) — add a sibling
  test for the new standalone table rather than overloading this one, and follow its fixture
  style (`_two_charts`, explicit longitudes, asserting on lord order and source string).
- **UI:** `pn4_turning_triplicity_lords`'s output currently feeds `turning_triplicity_rows` inside
  `pn4_timing_bundle` (~app.py:12883), rendered on the Timing page beside the yearly "turning"
  material. A standalone whole-life table doesn't need a solar revolution at all — it belongs
  wherever this project already puts other whole-life, natal-only tables (the Fardar table and
  the bound distribution are the nearest analogues; see how each gets its own `st.subheader` with
  a `help=` citation string, e.g. around app.py:14870).
- **Tracking:** `docs/synthesis/16_open_features.md` has (or should have, if not added yet) an
  F-4 entry pointing at this brief — update its status when this ships.

## 5. Test data for cross-checking

Once built, sanity-check against the one real data point already in hand:

**29 Oct 1990, 13:02:00 EST (+5h to UT), Pontiac, Michigan, 42n38'20 N / 83w17'28 W.** Diurnal.
Sun 06° Scorpio, Ascendant 21° Capricorn. Janus's Firdaria/medieval-module report (if built on
the Ascendant's triplicity, per §2) should reproduce **Venus / Moon / Mars** in that order — but
confirm the *reason*, not just the sequence, before calling it matched: getting Venus-Moon-Mars
out of an accidentally-transcribed rule is not the same as getting it from the right one.

## 6. What not to do

- Don't touch `pn4_turning_triplicity_lords` or its existing test in ways that change its current
  VI.2,4/VI.2,5 behavior (sect-light for assets, Mars's sign for siblings) — that function is
  correctly scoped and already has a citation-checked adjudication behind it. Build the new
  standalone table alongside it, sharing the ordering logic, not by repurposing it.
- Don't invent age numbers and cite VI.2,4 for them — the text doesn't have numbers, and saying it
  does is exactly the kind of false-citation defect this project's own repair briefs (see
  `docs/SAHL_APP_REPAIR_BRIEF_2026-09-10.md` §2 for the standard of care expected) exist to catch.
- Don't assume the Ascendant reading from §2 is confirmed — it's one data point away from settled.
