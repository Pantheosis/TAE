"""Ceilings on the length of the app's tooltip and caption text, with a
frozen allowlist that can only shrink.

The renderer's own comment sets out three depths for one finding: the
GLANCE is what the thing is, said in a sentence in the heading's tooltip;
the CHECK is the citation, a visible caption; the AUDIT is the quotations
and measurements, in an expander under the table. A tooltip cannot be
scrolled, selected or searched, so a glance or a help string is a
sentence, and a caption is provenance, not an essay. The renderer's
comment names about 200 characters as the aim for a tooltip; the numbers
here are ceilings, not the aim: help and glance at 300, caption at 400.

The scan is by AST over app.py, so it sees only what the source states
as text: a string constant; an f-string's constant parts (the
interpolations count for nothing); a ``+`` chain of those; a
``.format(...)`` call measured as its receiver; a bare name, when app.py
assigns it exactly once at module level to something the scan can
measure, measured as that value, so a tooltip lifted to a module constant
does not leave the guard. Names app.py takes from engine.py through its
star import stay unmeasured by design: the engine's note constants are
the last readability branch's (C) business, and this test does not read
engine.py. Anything else measures 0 and is ignored, so a caption built at
run time from a local is not this test's business. The measured text is
the constant parts concatenated in order.

ALLOWED_LONG freezes the first 48 characters of every string over its
ceiling as the app stood when the tuple was generated. Three tests: no
string over its ceiling whose key is not in the tuple; every entry in
the tuple still names an offender, so a builder who shortens a text must
delete its entry and the list can only shrink; and the tuple is empty,
expected to fail until the last readability branch (C) empties it, when
that test's xfail marker is removed. To regenerate the tuple after a
migration run this module as a script:

    python tests/test_text_lengths_2026_09_17.py

which prints the current offenders, one per line, as kind, ceiling,
length and key; the test is never self-updating.
"""
import ast

import pytest

from conftest import APP_PATH

CEILINGS = {"help": 300, "glance": 300, "caption": 400}
KEY_LENGTH = 48

# The first 48 characters of every string over its ceiling, exact, one
# entry per offender, grouped by kind and in source order at generation.
# A later branch that shortens or migrates a text deletes its entry here;
# nothing is ever added.
ALLOWED_LONG = (
    # help
    'LMT (local mean time) for charts before standard',
    'Masha\'allah: "look at the position of the govern',
    '31: "if the nativity was by day, the infortunes ',
    'IX.7, 29: "you look at the degree of the Ascenda',
    'IX.7, 23: "you look in the revolution of the yea',
    '"The days and hours have nine indicators" (IX.7,',
    'IX.1, 35-39. Five are "rooted" -- turned from th',
    "IX.1, 26-34: Abu Ma'shar turns the monthly indic",
    'Sahl, On Nativities 2.11, 1-2 (Theophilus; fn 14',
    'Some software divides the life by the lords of t',
    'IV.1, 2-4: the years are Sun 10, Venus 8, Mercur',
    'A planet may distribute or manage more than once',
    "I.8, 10-26 and Figure 53 (PN IV): Ptolemy's seve",
    'Two rows: the lord of the year by annual profect',
    'The lesser, middle, greater and mighty years and',
    # glance
    # caption
    'The releaser and the house-master PN IV leaves t',
    '**** turned a year a sign from its natal sign (w',
    'Readings: "the degree of burning" is the Sun\'s n',
    'Zodiacal, by the sentence: 59\' 08" a day round t',
    'The rate. IX.7, 25 prints "12 days, <4 hours>, 1',
    'A "day" is a whole 24-hour period from the birth',
    'The three cases do not stand alike. The **Ascend',
    "The three lords of the sect light's triplicity (",
    '**All three grades are shown and none is chosen.',
)


def _module_constants(tree):
    """name -> value expression, for every name app.py assigns exactly
    once at module level with a single plain target."""
    counts, values = {}, {}
    for node in tree.body:
        if (isinstance(node, ast.Assign) and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)):
            name = node.targets[0].id
            counts[name] = counts.get(name, 0) + 1
            values[name] = node.value
    return {name: values[name] for name, n in counts.items() if n == 1}


def _constant_parts(node, constants=None):
    """The string constants an expression states, in order; [] where the
    AST cannot see text. `constants` is the module-level table a bare
    name is resolved through, one hop only."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]
    if isinstance(node, ast.JoinedStr):
        return [v.value for v in node.values
                if isinstance(v, ast.Constant) and isinstance(v.value, str)]
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        return _constant_parts(node.left, constants) + _constant_parts(node.right, constants)
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and node.func.attr == "format"):
        return _constant_parts(node.func.value, constants)
    if isinstance(node, ast.Name) and constants and node.id in constants:
        return _constant_parts(constants[node.id])
    return []


def measured_texts(source=None):
    """Every (kind, line, text) the scan measures: kind is "help" or
    "glance" for those keyword arguments on any call, "caption" for the
    first positional argument of any ``.caption(...)`` call, whatever the
    receiver; a bare name resolved through the module-level constants."""
    tree = ast.parse(APP_PATH.read_text() if source is None else source)
    constants = _module_constants(tree)
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        for kw in node.keywords:
            if kw.arg in ("help", "glance"):
                found.append((kw.arg, node.lineno, "".join(_constant_parts(kw.value, constants))))
        if (isinstance(node.func, ast.Attribute) and node.func.attr == "caption"
                and node.args):
            found.append(("caption", node.lineno,
                          "".join(_constant_parts(node.args[0], constants))))
    return sorted(found, key=lambda t: t[1])


def offenders(source=None):
    return [(kind, line, text) for kind, line, text in measured_texts(source)
            if len(text) > CEILINGS[kind]]


def key_of(text):
    return text[:KEY_LENGTH]


def _describe(kind, line, text):
    return f"{kind:7} ceiling {CEILINGS[kind]:3}  length {len(text):5}  line {line:5}  {key_of(text)!r}"


def print_offenders():
    """For regenerating ALLOWED_LONG by hand: the current offenders, one
    per line."""
    for kind, line, text in offenders():
        print(_describe(kind, line, text))


def test_no_text_over_its_ceiling_outside_the_allowlist():
    violators = [(kind, line, text) for kind, line, text in offenders()
                 if key_of(text) not in ALLOWED_LONG]
    assert not violators, (
        "text over its ceiling and not in ALLOWED_LONG -- shorten it, or move the "
        "surplus to the notes expander:\n  "
        + "\n  ".join(_describe(*v) for v in violators))


def test_every_allowlist_entry_still_names_an_offender():
    current = {key_of(text) for _kind, _line, text in offenders()}
    stale = [entry for entry in ALLOWED_LONG if entry not in current]
    assert not stale, (
        "no current text over its ceiling starts with this key; remove this entry "
        "from ALLOWED_LONG:\n  " + "\n  ".join(repr(s) for s in stale))


@pytest.mark.xfail(strict=True, reason=(
    "ALLOWED_LONG holds every text over its ceiling until the readability branches "
    "migrate them; this flips to passing when the last of them (C) empties the tuple, "
    "and that builder removes this marker"))
def test_the_allowlist_is_empty():
    assert ALLOWED_LONG == ()


if __name__ == "__main__":
    print_offenders()
