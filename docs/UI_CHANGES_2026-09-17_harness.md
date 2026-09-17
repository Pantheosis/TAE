# UI changes 2026-09-17 — the readability harness (branch H)

Branch `readability-h-2026-09-17` off `main` at `93f7bbd`. Branch H of
`UI_READABILITY_PLAN_2026-09-17_rev2.md` §3: tests only. `app.py` and
`engine.py` are byte-identical to `main`; `tests/fixtures/tables.json` is
byte-identical to `main`. Three commits, one per task, in the order below,
and a fourth after the adversarial pass (`H_ADVERSARIAL_REPORT_2026-09-17.md`
on the Desktop) with the three tightenings it asked for, marked below.

## What was asked

**The walker.** `table_inventory(at)` in `tests/conftest.py` keys every
`st.dataframe` on a rendered page by the nearest preceding subheader or
expander label, and skipped only an expander labelled "Sources and editorial
notes". The rule was to become: skip an expander whose label is that OR whose
icon is `:material/menu_book:`, so that a notes expander under any label
(the Chart page's sign-category lookup table sits in one) never becomes the
heading of what follows. The two per-file copies of the walk, in
`test_column_config_2026_09_15.py` and `test_labels_nomenclature_2026_09_16.py`,
were to go, both files importing conftest's. Acceptance: regenerate the
fixture once and the diff is empty.

**Guard tests on text length.** A new `tests/test_text_lengths_2026_09_17.py`
that measures, by AST over `app.py`, every `help=` and `glance=` keyword on
any call and the first positional argument of every `.caption(...)` call;
help and glance at most 300 characters, a caption at most 400; an
`ALLOWED_LONG` tuple frozen in the file holding the first 48 characters of
every current offender; one test that nothing over its ceiling is outside
the tuple, one that every entry still names an offender (so the tuple can
only shrink), and one under `xfail(strict=True)` that the tuple is empty.

**The nothing-lost script.** `tests/tools/prose_preserved.py <base-ref>
[--engine]`, not collected by pytest: every sentence of 25 characters or
more, and every locator token, in the base revision's string constants must
still occur in the working tree's `app.py` + `engine.py` string corpus, both
sides normalised the same way; prints the misses and nothing else.

## What was done

### Commit 1: the walker

Streamlit 1.62.0's `AppTest` builds an expander that carries an icon as a
`Status` node (`type == "status"`) and one without as an `Expander`
(`type == "expander"`); both come from the same `Expandable` proto and both
carry `.label` and `.icon`. Every notes expander in the app carries the book
icon, so the old label-only rule, which looked at `"expander"` nodes alone,
never matched anything: the notes expanders were invisible to it, and the
sign-category table on the Chart page was keyed under the subheader before
it by that accident rather than by rule.

conftest now has `table_nodes(at)`, the one walk, returning `(heading, node)`
pairs; `table_inventory(at)` maps it to `(heading, columns)`; a new
`find_table(at, heading)` returns the first dataframe node under a heading.
The walk reads `"expander"` and `"status"` nodes alike and skips one whose
label is "Sources and editorial notes" or whose icon is `:material/menu_book:`
(`_is_notes_expander`). `.icon` is the raw string as passed to
`st.expander(icon=...)`, not a normalised form; the docstring says so.

The two per-file helpers were not inventories but finders: `_find_table` in
`test_column_config_2026_09_15.py` and `_config` in
`test_labels_nomenclature_2026_09_16.py` each re-implemented the same heading
walk to return the dataframe node under a heading (the second also returned
its parsed `column_config`). Neither differed from conftest's rule beyond
returning the node. Both are deleted; both files import `find_table`, and the
one caller that wanted the config parses it from the node.

**Fixture check.** `UPDATE_TABLE_FIXTURE=1 python -m pytest
tests/test_pages_render.py` once, 67 passed; `git diff --stat
tests/fixtures/tables.json` empty. The sign-category table stays keyed under
the Chart page's last subheader, as before.

**One expander the icon rule does not skip.** The Timing page's "What
Persian Nativities IV does not settle" carries `:material/help:`, so under
the new rule it is a heading. It is the last block on the page before the
notes expander and no dataframe follows it, so the fixture is unchanged; a
later branch that places a dataframe after a help-icon expander, before the
next subheader, will see it keyed under that label.

### Commit 2: the text-length guard

`tests/test_text_lengths_2026_09_17.py`. The scan measures only what the AST
states as text: a string constant; an f-string's constant parts, the
interpolations uncounted; a `+` chain of those; a `.format(...)` call as its
receiver; and, since the adversarial pass, a bare name that `app.py` assigns
exactly once at module level to something the scan can measure, measured as
that value, so a tooltip lifted to a module constant does not leave the
guard. Names that come from `engine.py` through the star import stay
unmeasured by design: the engine's note constants are branch C's business
under plan §1.6, and the test does not read `engine.py` (the two long
captions that print engine notes on the Timing and Reference pages are
therefore invisible to it, as the report says). Anything else measures 0
and is ignored: 24 of the 195 collected strings, down from 26 before the
name resolution, which measures the wheel's dark-theme help at its two
sites (162 characters, under the ceiling) and finds no other app.py
constant at a measured site; the rest are locals, conditionals, joins and
subscripts. The measured text is the constant parts concatenated in order;
the key is its first 48 characters, exact.

On `main` the scan collects 85 `help=`, 35 `glance=` and 75 caption
strings, totalling 35,384, 11,690 and 38,876 characters. **Offenders: 42
help, 16 glance, 32 caption — 90 in all, every key distinct; unchanged by
the name resolution.** (The plan's
own AST count was 56 help calls at 30,100 characters and 75 captions at
39,800; this scan also takes `help=` on `column_config` calls and on
`st.subheader`, hence more help calls.) The file passes on `main`: two
passed, one xfailed.

The module docstring paraphrases the renderer's three-depth comment (a
glance or a help string is one sentence in the tooltip, a caption is
provenance; about 200 characters is the aim, the test's numbers are the
ceiling). Running `python tests/test_text_lengths_2026_09_17.py` prints the
current offenders as kind, ceiling, length, line and key, for regenerating
the tuple by hand; the test is never self-updating.

**How a later branch shrinks the list.** When a block's help, glance or
caption is shortened or migrated, the second test fails naming the entry
("remove this entry from ALLOWED_LONG"); the builder deletes that entry in
the same commit. Nothing is ever added. When the last readability branch
(C) migrates the last block, the tuple is empty, the third test would pass,
and `strict=True` fails the suite on the unexpected pass: that builder
removes the `xfail` marker in the same commit, leaving a plain assertion
that the tuple is empty.

Six of the ninety keys begin with a citation form and several with a
quotation fragment, because that is how the offending strings begin and the
key is exact by the plan. They are data, not prose; the file's own docstring
and comments carry neither.

### Commit 3: the nothing-lost script

`tests/tools/prose_preserved.py`. `pytest --collect-only -q tests | grep
tools` is empty (no `__init__.py`, the name does not match `test_*`).

Run from the repository root:

    /home/apothic/almuten_engine/Executable/.venv/bin/python tests/tools/prose_preserved.py main
    /home/apothic/almuten_engine/Executable/.venv/bin/python tests/tools/prose_preserved.py main --engine --summary
    /home/apothic/almuten_engine/Executable/.venv/bin/python tests/tools/prose_preserved.py <branch> --tree <a worktree at main>   # the reverse check: what the branch holds that main does not (nothing added)

The base corpus is `git show <base-ref>:app.py` (and `engine.py` with
`--engine`); the branch corpus is the working tree's `app.py` and `engine.py`,
always both. Each side: every string constant the AST holds, plain constants
and the constant parts of f-strings, minus docstrings. Normalisation:
whitespace runs to one space, `**` removed, a leading `> ` stripped from each
line, surrounding whitespace stripped. Sentences from the base only: two
consecutive newlines in the raw string are a boundary; then a split after
sentence-ending punctuation (with any closing quotes or brackets) followed
by whitespace and an upper-case letter, digit, opening quote or opening
bracket; sentences under 25 characters dropped. A chapter abbreviation
followed by a number splits by that rule too (59 such fragments on `main`),
which costs nothing in coverage since both fragments are checked, only that
a miss may print a fragment. Locators are the citation forms the three
citation-scan tests recognise, their patterns copied into the script with a
comment naming the source files; every token matched in the base corpus
must be a substring of the branch corpus. Output: `SENTENCE: ...` or
`LOCATOR: ...` per miss, nothing on success; exit 1 on any miss. After
those, since the adversarial pass, an informational `LOCATOR-COUNT: <token>
base <n> -> branch <m>` line for every locator token that occurs fewer times
in the branch corpus than in the base corpus but still occurs (occurrences
counted over the normalised string corpus, not sites; a token gone
altogether is a `LOCATOR:` miss and is not repeated). It never sets the exit
status. It exists because the presence check is satisfied by any one copy of
a duplicated locator: the same chapter-and-sentence range stands in several
labels and notes, and a copy mistyped to another valid number passed the
script and the citation-scan tests alike. `--summary` prints base
sentences, base locators, misses and count drops to stderr.

Self-check on this branch: `main` gives 1,262 sentences and 114 locators
from `app.py`, 3,448 and 193 with `--engine`, zero misses, exit 0. Two
non-committed edits, each reverted with `git checkout -- app.py`: deleting
one caption sentence on the Chart page reported exactly that sentence and
exited 1; altering the range in a short source label (under 25 characters,
so no sentence covers it) reported exactly that locator token, the two
copies of the token in `engine.py` being a docstring and a comment, which
the extraction rightly ignores. After the tightening: `main` still prints
nothing (every count equal on an unchanged tree, exit 0); shortening one of
the two copies of a duplicated third-chapter range in a short finding label
printed exactly one `LOCATOR-COUNT` line, `base 2 -> branch 1`, and exited
0 (non-committed, reverted). That label's sentence check was silent, since
the sentence rule splits after the chapter abbreviation and leaves the
changed range in a fragment under 25 characters: the count line is what
sees a mistyped copy in a short label.

**How misses are classified on N, A, B and C.** Every `SENTENCE:` or
`LOCATOR:` line the script prints is listed in that branch's docs note under
exactly one of six headings: the five in plan §3, *consolidated duplicate of
<sentence>*, *copy correction 9a/9b*, *cross-reference reworded (N)*, *ALL
CAPS to bold (test_prose_counts edited)*, *heading shortened*, and a sixth,
*rebuilt into the table <heading> from <sentence>*, for a sentence whose
substance now stands as a row of a comparison table: the per-table
source-sentence list that plan rule 1.4 already requires is that list, under
the table's heading, and the sentence named there is the one the row was
built from. A miss that fits none is a loss and blocks the branch.

Two things the script's matching implies for a builder. A sentence moved
verbatim into a Markdown table cell is silent, because the match is
substring; only a rewritten row is a miss, and it goes under the sixth
heading. A sentence split across two string constants joined by `+`, or
given an f-string interpolation mid-sentence, reads as a miss, because the
branch corpus joins constants with newlines: migrated prose stays in
adjacent string literals, which is `app.py`'s style everywhere.

A `LOCATOR-COUNT` line is classified under *consolidated duplicate* when
the surviving copy is the same locator in the same sentence as the one that
went; otherwise it is checked by eye against the source before the branch is
called done. It never blocks on its own.

## What the tests showed

Full suite with `-n auto`: **3352 passed, 1 skipped, 1 xfailed** (the
allowlist-is-empty test); the walker's own callers
(`test_pages_render`, `test_column_config_2026_09_15`,
`test_labels_nomenclature_2026_09_16`, `test_saved_readings_export_2026_09_16`,
`test_configurations_tabs`, `test_prosperity_2026_09_15`) all pass on the
new walk. `pytest-xdist==3.8.0` is pinned in `requirements.txt` but was not
installed in the project venv; it was installed at that pin so `-n auto`
runs as the plan and CI expect.
