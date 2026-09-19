import ast

import pytest

from conftest import assert_no_exception, engine_source, make_app, ui_source


RESULT_FIELDS = {'Hayz', 'ContraryDomain', 'PlanetSect', 'Net'}


def _function(tree, name):
    matches = [node for node in ast.walk(tree)
               if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == name]
    assert len(matches) == 1, name
    return matches[0]


def _assignment(function, name):
    values = []
    for node in ast.walk(function):
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(isinstance(target, ast.Name) and target.id == name for target in targets):
                values.append(node.value)
    assert len(values) == 1, name
    return values[0]


def _field_read(node):
    if isinstance(node, ast.Subscript) and isinstance(node.slice, ast.Constant):
        return node.slice.value if node.slice.value in RESULT_FIELDS else None
    if (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
            and node.func.attr == 'get' and node.args
            and isinstance(node.args[0], ast.Constant)
            and node.args[0].value in RESULT_FIELDS):
        return node.args[0].value
    return None


def _direct_result_truth_reads(node):
    """Result fields used as truth values, allowing explicit comparisons and guards."""
    field = _field_read(node)
    if field:
        return [field]
    if isinstance(node, ast.BoolOp):
        return [field for value in node.values for field in _direct_result_truth_reads(value)]
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
        return _direct_result_truth_reads(node.operand)
    if isinstance(node, ast.NamedExpr):
        return _direct_result_truth_reads(node.value)
    # Comparisons (`is True`, `is None`, membership) and predicate calls
    # (`isinstance`, `is_unresolved`) produce their own booleans.
    return []


def _names(node):
    return {item.id for item in ast.walk(node) if isinstance(item, ast.Name)}


def _has_isinstance_of_net(node, *, negated):
    calls = [item for item in ast.walk(node)
             if isinstance(item, ast.Call) and isinstance(item.func, ast.Name)
             and item.func.id == 'isinstance' and len(item.args) == 2]
    assert calls
    assert any(
        any(_field_read(part) == 'Net' for part in ast.walk(call.args[0]))
        and any(isinstance(part, ast.Name) and part.id == 'UnresolvedResult'
                for part in ast.walk(call.args[1]))
        for call in calls
    )
    has_not = any(isinstance(item, ast.UnaryOp) and isinstance(item.op, ast.Not)
                  for item in ast.walk(node))
    assert has_not is negated


def test_indeterminate_result_is_immutable_named_and_never_boolean(engine):
    result = engine['UnresolvedResult'](
        reason='the source leaves two readings open',
        source='Example 1.2, 3',
        alternatives=(('first reading', 12), ('second reading', 15)),
    )
    assert result.status == 'unresolved'
    assert result.reason == 'the source leaves two readings open'
    assert result.source == 'Example 1.2, 3'
    assert result.alternatives == (('first reading', 12), ('second reading', 15))
    with pytest.raises(TypeError, match='has no truth value'):
        bool(result)
    with pytest.raises(Exception):
        result.reason = 'changed'


def test_indeterminate_statuses_remain_distinct(engine):
    cls = engine['UnresolvedResult']
    assert {cls('r', 's', status=status).status for status in engine['INDETERMINATE_STATUSES']} == {
        'unavailable', 'unresolved', 'unassigned', 'not decided'}
    with pytest.raises(ValueError):
        cls('r', 's', status='false')


def test_three_valued_conjunction_and_disjunction_settle_only_when_known(engine):
    unknown = engine['UnresolvedResult']('open', 'Example 1')
    assert engine['doctrinal_and'](unknown, False) is False
    assert engine['doctrinal_and'](True, unknown) is unknown
    assert engine['doctrinal_or'](unknown, True) is True
    assert engine['doctrinal_or'](False, unknown) is unknown
    with pytest.raises(TypeError):
        engine['doctrinal_and'](1, True)
    with pytest.raises(TypeError):
        engine['doctrinal_or']('', False)


def test_prosperity_conflict_uses_the_shared_result(engine):
    source = open(engine['__file__'], encoding='utf-8').read()
    assert "class_field = UnresolvedResult(" in source
    assert "key, class_field = 'unresolved', 'unresolved'" not in source


def test_selected_unresolved_prosperity_detail_is_rendered_without_truth_testing():
    at = make_app(date='1240-05-23', page='findings').run()
    box = [node for node in at.main.selectbox
           if node.key == 'sahl_indications_of_fortune_and_livelihood_detail'][0]
    assert 'Unresolved — ' in box.options[0]
    box.select(box.options[0])
    at.run()
    assert_no_exception(at, 'selected unresolved prosperity detail')
    rendered = [node.value for node in at.main.markdown if node.value.startswith('**Class.**')]
    assert rendered and rendered[0].startswith('**Class.** Unresolved — ')


def test_result_fields_are_not_coerced_in_boolean_conditions():
    offenders = []
    for filename, source in (('engine.py', engine_source()), ('app.py', ui_source())):
        tree = ast.parse(source)
        tests = []
        for node in ast.walk(tree):
            if isinstance(node, (ast.If, ast.IfExp, ast.While)):
                tests.append(node.test)
            elif isinstance(node, (ast.ListComp, ast.SetComp, ast.DictComp, ast.GeneratorExp)):
                tests.extend(condition for generator in node.generators for condition in generator.ifs)
        for test in tests:
            fields = _direct_result_truth_reads(test)
            if fields:
                offenders.append((filename, test.lineno, fields, ast.unparse(test)))
    assert offenders == []


def test_known_aggregators_partition_unresolved_results_before_counts_and_ranks():
    engine_tree = ast.parse(engine_source())
    strength = _function(engine_tree, 'evaluate_strength_of_planets')
    count_values = [value
                    for node in ast.walk(strength) if isinstance(node, ast.Dict)
                    for key, value in zip(node.keys, node.values)
                    if isinstance(key, ast.Constant) and key.value == 'Count']
    assert len(count_values) == 1
    assert (isinstance(count_values[0], ast.Call)
            and isinstance(count_values[0].func, ast.Name)
            and count_values[0].func.id == 'len'
            and len(count_values[0].args) == 1
            and isinstance(count_values[0].args[0], ast.Name)
            and count_values[0].args[0].id == 'labels')

    unresolved_count = _assignment(strength, 'unresolved_count')
    assert isinstance(unresolved_count, ast.Call)
    assert isinstance(unresolved_count.func, ast.Name) and unresolved_count.func.id == 'sum'
    assert {'testimonies', 'UnresolvedResult'} <= _names(unresolved_count)

    condition = _function(engine_tree, 'evaluate_abu_mashar_condition')
    net_known = _assignment(condition, 'net_known')
    assert {'positive_votes', 'negative_votes'} <= _names(net_known)
    assert not {name for name in _names(net_known) if name.startswith('unresolved')}

    houses = _function(engine_tree, 'evaluate_planets_in_houses')
    net_guard = next(
        node for node in ast.walk(houses)
        if isinstance(node, ast.If)
        and any(isinstance(part, ast.Name) and part.id == 'net'
                for part in ast.walk(node.test))
        and any(isinstance(part, ast.Name) and part.id == 'UnresolvedResult'
                for part in ast.walk(node.test))
    )
    assert len(net_guard.orelse) == 1 and isinstance(net_guard.orelse[0], ast.If)
    assert any(isinstance(part, ast.Call) and isinstance(part.func, ast.Name)
               and part.func.id == 'abs' and 'net' in _names(part)
               for part in ast.walk(net_guard.orelse[0].test))

    ui_tree = ast.parse(ui_source())
    for function_name, resolved_name, unresolved_name in (
        ('page_dignities', 'resolved_dignity', 'unresolved_dignity'),
        ('abu_condition', 'resolved_condition', 'unresolved_condition'),
    ):
        function = _function(ui_tree, function_name)
        resolved = _assignment(function, resolved_name)
        unresolved = _assignment(function, unresolved_name)
        assert isinstance(resolved, ast.Call) and isinstance(resolved.func, ast.Name)
        assert resolved.func.id == 'sorted'
        _has_isinstance_of_net(resolved, negated=True)
        _has_isinstance_of_net(unresolved, negated=False)


def test_dignities_readings_tables_render_an_unassigned_mercury_without_a_repr_leak(monkeypatch):
    """The blind check of 2026-09-18 found the Dignities page's "Rhetorius / PN IV
    readings" table printing the UnresolvedResult repr in Mercury's Net cell when
    his sect is unassigned (exact conjunction with the Sun). The chart is the
    ephemeris chart with Mercury moved onto the Sun's degree, the checker's own
    recipe; every frame the page draws must pass through the display boundary."""
    at = make_app(date='1240-05-23', page='dignities')   # make_app syncs (reloads) the engine: patch after it
    import engine
    original = engine.calculate_traditional_chart_jd

    def mercury_on_the_sun(*args, **kwargs):
        chart = original(*args, **kwargs)
        chart['planetary_data']['Mercury']['longitude'] = chart['planetary_data']['Sun']['longitude']
        return chart
    monkeypatch.setattr(engine, 'calculate_traditional_chart_jd', mercury_on_the_sun)
    at.run()
    assert_no_exception(at)
    frames = [el.value for el in at.main.dataframe] + [el.value for el in at.main.table]
    assert frames, "the Dignities page drew no frames"
    cells = [cell for frame in frames for cell in frame.astype(str).values.ravel()]
    leaks = [cell for cell in cells if 'UnresolvedResult(' in cell or 'YearsOutcome(' in cell]
    assert not leaks, leaks[:3]
    texts = cells + [node.value for node in at.main.markdown]
    assert any('unassigned' in t.lower() or 'unresolved' in t.lower() for t in texts), \
        "the unassigned Mercury never reached the page"
