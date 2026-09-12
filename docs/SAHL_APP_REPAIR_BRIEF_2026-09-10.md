# Briefing: `app.py` and test repairs from the Sahl Vol. I read-through

Written 2026-09-10 by the session that read the volume. Companion to two documents in
`consolidated_texts/process/`:

- `SAHL_READTHROUGH_FINDINGS_2026-09-10.md` — the evidence.
- `SAHL_REPAIR_BRIEF_2026-09-10.md` — the **corpus** work order, a different job from this one.

**This brief covers `Executable/` — with one deliberate exception, §5, which adds a single entry to
`consolidated_texts/DOCTRINAL_CAVEATS.md` because that file is where adjudicated
do-not-repair items live. Do not apply the corpus repairs from here, and do not let this session
and the corpus session write to the same files.**

---

## 0. Scope, and the good news first

**No engine output is wrong.** All 59 cited loci in Sahl Vol. I were verified sentence by sentence
against the printed page. Every Lot formula, every doctrinal claim, every quotation in a `note=`
field checked out — several verbatim. Two locators are imprecise and neither changes a computation.

So this is not a correctness ticket. It is: **one false statement shown to users**, two locator
fixes, and three places where a test or comment now understates what is known.

## 1. Pin the version. This file moves.

**`app.py` changed five times during the read session** — md5 `78dfb2f9` → `935b9a52` → `ed233fcb`
→ `e6cd3c52` → `3e4c34b6`, and 8,204 → 9,334 lines. Every line number in the findings file is
already stale; the one quoted as `app.py:8864` is now `8982`.

```bash
md5sum Executable/app.py; wc -l Executable/app.py
```

**Anchor every edit on the quoted string, never on a line number**, and re-grep before you start.
If a string below is absent, someone else has already touched it — stop and diff rather than
guessing where it went.

## 2. ★ The one real defect: a false claim rendered to the user

**Where:** the Lots panel `st.markdown(...)` — grep for `Mercury-Venus`, currently ~line 8982.

**The text now reads:**

> "Every formula is taken from the running prose or a footnote, never from one of the summary
> tables, whose glyph columns the OCR mangles -- in Sahl's Fig. 63 (On Nativities; Abu Ma'shar's
> Fig. 63 is a different table), **the row for Ch. 10.2.5 renders as Mercury-Venus** where the body
> text plainly reads "from Saturn to the Moon.""

**It does not.** At corpus blob `b29f7368` the table renders correctly:

```
| 10.1.1, 14-17   | ☿→♂, ASC (R) | Action      |
| 10.2.5, 1-3     | ♄→☽, ASC (R) | Expedition  |
| 10.2.5, 4-14    | ☉→♄, ASC (R) | Father      |
```

`♄→☽` is Saturn-Moon. Further, **all 56 planet-glyph table rows across the seven Sahl files were
swept and not one glyph column is mangled anywhere in the volume** — Fig. 63, Fig. 71, the
ages-of-man table, the fixed-star natures table, the triplicity table, *On Times*' years table and
Ch. 3's connection model. The triplicity and least-years tables were additionally spot-checked
against doctrine and are correct.

Either the table was repaired after that sentence was written, or the sentence was always wrong.
Either way it is false today and users are reading it.

**Fix:** delete the example clause. **Keep the rule** — "take formulas from the running prose or a
footnote, never from a summary table" — which is sound and is how every formula in
`LOT_DEFINITIONS` was in fact sourced. Suggested replacement for the clause:

> "Every formula is taken from the running prose or a footnote, never from one of the summary
> tables, whose glyph columns are the most OCR-fragile part of the corpus."

**Do not** replace it with a different example unless you have verified that example yourself. The
failure mode here is a plausible illustration that nobody re-checked.

## 3. Two locator imprecisions — substance correct, pointer short

Neither changes output. Both are one-token edits.

**A.** Grep `On Nativities Ch. 10.2.7, 22` — a comment above `EGYPTIAN_TERMS`, currently ~line 526.
Change **`10.2.7, 22`** → **`10.2.7, 21-22`**.

Sentence 21 gives the position ("the Sun in Aquarius 16°, and Mercury with him, 5°"); sentence 22
gives the claim the comment relies on ("in his own bound"). The comment cites only 22. The
doctrinal point stands and is worth keeping — it independently confirms Mercury holds Aquarius 0-7,
and fn. 198 on p. 719 ("the first 7° of Capricorn are indeed ruled by Mercury") confirms Capricorn
0-7. Both match `EGYPTIAN_TERMS` as it now stands.

**B.** Grep `On Questions Ch. 6, 2 and 7.7, 91-101` — currently ~line 4410. Change
**`7.7, 91-101`** → **`7.7, 90-101`**. Dykes' Fig. 41 caption gives the range as 90-101.

**While you are in that same string:** it says "(Figures 37-41)". That sweep pulls in **Fig. 38,
which is Critical days**, not an angle reassignment. Either narrow the range to the figures that
actually show the per-topic assignment, or drop the parenthetical. Verify against the corpus before
choosing — I did not confirm which subset is right, only that 38 does not belong.

## 4. `tests/test_nativities_citations.py` — its docstring is now out of date

The docstring says:

> "Paragraph numbers cannot be pinned mechanically from the OCR (bold markers, LaTeX degree signs
> and footnote superscripts make "44" ambiguous), so this test holds only what it can hold
> everywhere: the chapter number."

**That is no longer true, and the read exists partly to retire it.** Findings §1c: **154 of 187
citations carry a sentence number** and the corpus numbers its sentences. What defeats a naive
regex is that sentences run *inline* within a paragraph, so line-leading matching finds about half
— which is a matching problem, not an impossibility. The fixed clause scanner in
`consolidated_texts/process/resolve_sahl_citations.py` now resolves **219 citations → 59 loci**,
naming sentences for 40 of them.

Two things follow, in order of value:

**A. Update the docstring regardless.** Leaving a claim of impossibility in place is how a
limitation becomes folklore — this project has already been bitten by a docstring that promised
"only exact, one-for-one accounting" while double-counting.

**B. Consider strengthening the test itself.** Every one of the 59 loci is now sentence-verified in
findings §2a-§2f, so a `(chapter, sentence)` existence check is buildable. **This is a judgment
call and I am not directing it** — it needs the corpus on disk or a much larger vendored fixture,
and the current test deliberately runs in CI without the corpus. If you do build it, note the
anchoring rule the read established: **bold `**N**` and plain `N` sentence markers alternate by
page inside a single chapter in every Sahl file**, so matching on either form alone is unsafe
everywhere. Accept both.

## 5. `consolidated_texts/DOCTRINAL_CAVEATS.md` — one entry to add

*(The only file outside `Executable/` in this brief. It is here rather than in the corpus brief
because it is an adjudication record, not a transcription change — nothing in the corpus text moves.)*

**p. 726 fn 231** is cited by `app.py` for the eastern-quarter advancing criterion at
On Nativities 10.3. The English is unaffected and the citation is sound, **but the footnote's
Arabic is wrong in the printed book**: it calls `إدبار` (*retreating*) one of "the two words used
for advancing". The owner's closeup confirms the page reads `إدبار` — so this is Dykes' error, the
corpus is faithful, and **it must not be repaired**.

Add it under the existing heading **"Arabic contrast lost in transcription — \"reading X for X\"
notes"**, which is exactly this class. A future reader who notices the contradiction should find it
already adjudicated rather than "fixing" the corpus.

The file's four headings are: *Calculation-sensitive*, *Reversed or missing source material*,
*Arabic contrast lost in transcription*, *Corpus completeness*.

## 6. What is explicitly NOT an engine change

Listed so nobody goes looking for downstream effects that do not exist.

- **The 23 corpus repairs** in the companion brief are all in Dykes' apparatus — footnote glosses
  and one dropped footnote line — not in doctrine. None alters a formula, a table or a delineation.
- **The p. 747 restored line** returns a *fourth* witness to the Lot of enemies (Saturn-Mars,
  Valens's Lot of accusation). Dykes explicitly declines to vouch for its manuscript. `app.py`
  correctly carries the three witnesses from his Fig. 71 and **should not gain a fourth.**
- **The p. 601 and p. 526 corpus defects** sit in engine-cited chapters (7.1, 5.3) but are a
  mis-tagged sentence number and a lost sentence number. Text is intact; no cited claim moves.
- **`resolve_sahl_citations.py` was already fixed** during the read and its output regenerated into
  `SAHL_EXPOSURE_WORKLIST.md`. Nothing to do, but note the worklist says 57 loci where the true
  count is **59**: two chapters (Nat 1.34 at p. 358, Nat 9.3 at p. 663) are cited across a prose
  bridge and print under `PROXIMITY` rather than being counted, because attributing them
  automatically would be inference. They were confirmed real citations by eye. If you regenerate,
  do not "fix" the resolver to count them — the conservatism is deliberate.

## 7. When you are done

1. `grep` each edited string to confirm the old form is gone and appears nowhere else.
2. Run the suite. Nothing here should move a test; if one moves, you have changed behaviour and
   should stop.
3. **Do not commit.** If asked, `git commit -F <msgfile> -- <paths>` and **never `git add`** — that
   form commits the named paths only and ignores the index, so it cannot sweep a peer's staged
   work. A new file needs `git add -N <path>` first. Check what the commit **contained**, not what
   it was meant to contain. Never `git add -A` in a shared tree.
4. Write your own status file. Findings and repair-status live in different documents; two writers
   on one document collided twice in the *Gr. Intr.* work.

---

## The reason §2 matters more than its size

It is one clause in one tooltip, and it would be easy to leave. But it is a **claim about the
corpus's reliability, shown to the user, that is false** — and it is false in the specific direction
that makes the apparatus look less trustworthy than it is. The volume's glyph tables are clean; the
place this corpus actually fails is single Arabic words inside footnotes, where a misread letter and
a dropped shadda produce **a well-formed Arabic string that no sweep can catch** (findings §2f).

A user told the tables are mangled will distrust the right thing for the wrong reason, and the real
failure mode stays invisible.
