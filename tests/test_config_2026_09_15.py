"""Executable/.streamlit/config.toml, and the AST fact behind it.

The app had no config file in Executable/, so the live server showed the
Deploy button and every AppTest render paid for the magic rewrite it never
used -- the script has no bare expression statement anywhere (checked here
by AST, not by eye), so turning magic off changes nothing on a page. The
config file and tests/conftest.py's own `runner.magicEnabled` setting (set
before the first AppTest is built, so the suite does not depend on the
working directory) both carry the same fact.
"""
import ast

import tomllib

from conftest import APP_PATH, EXECUTABLE_DIR, ui_source

CONFIG_PATH = EXECUTABLE_DIR / ".streamlit" / "config.toml"


def test_config_file_exists_with_magic_off_and_minimal_toolbar():
    assert CONFIG_PATH.exists(), f"{CONFIG_PATH} is missing"
    config = tomllib.loads(CONFIG_PATH.read_text())
    assert config["runner"]["magicEnabled"] is False
    assert config["client"]["toolbarMode"] == "minimal"
    # No [theme] section: the app follows the viewer's own theme, and the
    # pictures carry their own palette control (2026-09-15 second opinion,
    # item 6).
    assert "theme" not in config


def _is_bare_expression(node):
    """An ast.Expr whose value is not a call, an await, a yield, or a
    string constant (the docstring case) -- the shape magic would print."""
    value = node.value
    if isinstance(value, (ast.Call, ast.Await, ast.Yield, ast.YieldFrom)):
        return False
    if isinstance(value, ast.Constant) and isinstance(value.value, str):
        return False
    return True


def test_no_bare_expression_statements_anywhere_in_the_app():
    """Magic rewrites a bare expression statement into st.write(...); the
    app has none, at either half, so magicEnabled=false changes nothing a
    page shows. The count is reported so a future one is caught at review,
    not by a page silently gaining a new line."""
    tree = ast.parse(APP_PATH.read_text())
    bare = [node for node in ast.walk(tree)
            if isinstance(node, ast.Expr) and _is_bare_expression(node)]
    assert len(bare) == 0, (
        f"{len(bare)} bare expression statement(s) found (expected 0), at lines "
        f"{[n.lineno for n in bare]} -- magicEnabled=false would then change what a page shows")


def test_ui_source_still_has_no_bare_expressions_either():
    """The same fact, read off the UI half alone by source text rather than
    the whole file's AST, so a UI-only regression is caught even if the
    engine half is checked separately elsewhere."""
    tree = ast.parse(ui_source())
    bare = [node for node in ast.walk(tree)
            if isinstance(node, ast.Expr) and _is_bare_expression(node)]
    assert len(bare) == 0, [n.lineno for n in bare]
