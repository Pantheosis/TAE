"""F10 G11: lunar orientality alternatives and Mercury's actual-giver gate."""

import sys

from conftest import assert_no_exception, make_app
from test_doctrine_fixtures import _sahl_chart


def _moon_years(engine, sun_lon, *, speed=13.0):
    # Virgo rising; the Moon at 15 Cancer is in her domicile and in the
    # eleventh division. Sun 15 Taurus/15 Virgo gives a 60/300 difference.
    data, cusps = _sahl_chart(165.0, Moon=105.0, Sun=sun_lon)
    data['Moon']['speed_in_lon'] = speed
    essential = engine['evaluate_essential_dignities'](data, 'Nocturnal')
    return (data, cusps, essential,
            engine['sahl_house_master_years']('Moon', data, cusps, 'Nocturnal', essential),
            engine['jn_years_fallback']('Moon', data, cusps, 'Nocturnal', essential))


def _numbers(result):
    return [(name, value.sentence, value.number, value.unit) for name, value in result.alternatives]


def test_both_solar_sides_leave_lunar_orientality_unknown(engine):
    results = []
    for sun_lon in (45.0, 165.0):
        _data, _cusps, _essential, sahl, combined = _moon_years(engine, sun_lon)
        assert isinstance(sahl['result'], engine['UnresolvedResult'])
        assert _numbers(sahl['result']) == [
            ('if the Moon is eastern', '1.20, 10', 108, 'years'),
            ('if the Moon is not eastern', None, None, None),
        ]
        assert _numbers(combined['result']) == [
            ('if the Moon is eastern', '1.20, 10', 108, 'years'),
            ('if the Moon is not eastern', 'JN Ch. 3, succedent', 25, 'years'),
        ]
        results.append(combined['result'])
    assert results[0] == results[1]


def test_conditional_years_keep_inverse_top_level_evidence_and_concrete_routes(engine):
    _data, _cusps, _essential, sahl, combined = _moon_years(engine, 45.0)
    east, west = sahl['facts']['eastern'], sahl['facts']['westernizing']
    assert east.alternatives == (('if the Moon is eastern', True), ('if the Moon is not eastern', False))
    assert west.alternatives == (('if the Moon is eastern', False), ('if the Moon is not eastern', True))
    for field in ('class', 'count', 'unit', 'place', 'steps', 'jn', 'umar', 'table_note'):
        assert isinstance(combined[field], engine['UnresolvedResult']), field
    assert isinstance(combined['facts']['eastern'], engine['UnresolvedResult'])
    assert isinstance(combined['facts']['westernizing'], engine['UnresolvedResult'])
    east_route, west_route = [route for _label, route in combined['alternative_routes']]
    assert (east_route['route'], east_route['facts']['eastern'], east_route['facts']['westernizing']) == (
        'Sahl 1.20', True, False)
    assert (west_route['route'], west_route['facts']['eastern'], west_route['facts']['westernizing']) == (
        'JN Ch. 3 after Sahl 1.20 is silent', False, True)


def test_jn_ladder_alone_keeps_66_and_a_half_against_25(engine):
    facts = {'share': True, 'eastern': None, 'westernizing': None,
             'retrograde': False, 'under the rays': False, 'fall': False}
    result = engine['jn_years_ladder']('Moon', 11, facts)
    assert _numbers(result['result']) == [
        ('if the Moon is eastern', 'JN Ch. 3, succedent', 66.5, 'years'),
        ('if the Moon is not eastern', 'JN Ch. 3, succedent', 25, 'years'),
    ]


def test_independently_false_and_convergent_routes_resolve_normally(engine):
    # Retrograde and under the rays settle Sahl 1.20, 23b in the eleventh
    # before easternness can establish the enhanced grant.
    _data, _cusps, _essential, sahl, combined = _moon_years(engine, 100.0, speed=-0.1)
    assert (sahl['grade'], sahl['sentence']) == ('months', '1.20, 23')
    assert combined is None

    # Enough independent demotions put both JN assignments at its days floor.
    facts = {'share': False, 'eastern': None, 'westernizing': None,
             'retrograde': True, 'under the rays': True, 'fall': False}
    common = engine['jn_years_ladder']('Moon', 11, facts)
    assert isinstance(common['result'], engine['YearsOutcome'])
    assert (common['class'], common['count'], common['unit']) == ('days', 25, 'days')


def _mercury_rows(engine, jupiter, *, mars=90.0):
    # Saturn 0 Aries is house-master; Mercury 0 Gemini sextiles Saturn.
    # Jupiter at 0 Libra opposes Saturn but trines Mercury; at 0 Aquarius
    # it sextiles Saturn and trines Mercury.
    data, _ = _sahl_chart(15.0, Saturn=0.0, Mercury=60.0, Jupiter=jupiter,
                          Venus=90.0, Mars=mars, Sun=120.0, Moon=240.0)
    return {row['planet']: row for row in engine['evaluate_jn_years_additions']('Saturn', data)}


def test_explicitly_zero_benefic_does_not_qualify_mercury(engine):
    rows = _mercury_rows(engine, 180.0)
    assert rows['Jupiter']['effect'] == 'nothing'
    mercury = rows['Mercury']
    assert isinstance(mercury['effect'], engine['UnresolvedResult'])
    assert mercury['effect'].status == 'not decided'
    assert 'no benefic companion actually adds' in mercury['effect'].reason


def test_actual_benefic_addition_and_missing_grade_allow_mercurys_20(engine):
    rows = _mercury_rows(engine, 300.0)
    jupiter, mercury = rows['Jupiter'], rows['Mercury']
    assert jupiter['effect'] == 'adds'
    assert [unit for _text, _number, unit in jupiter['grades']] == ['years', 'months', 'days or hours']
    assert mercury['effect'] == 'adds' and mercury['lesser_years'] == 20


def test_sub_year_contribution_is_positive_and_unknown_contribution_propagates(engine):
    month_only = {'effect': 'adds', 'grades': (('confirmed middling', 12, 'months'),)}
    assert engine['_jn_positive_contribution'](month_only) is True
    assert engine['mercury_jn_addition_gate'](True, [True]) is True

    unknown = engine['UnresolvedResult'](
        'the companion contribution is unresolved', "Abu 'Ali, Judgments of Nativities Ch. 4")
    assert engine['mercury_jn_addition_gate'](True, [unknown]) == unknown
    # An independently failed Mercury aspect settles the conjunction false.
    assert engine['mercury_jn_addition_gate'](False, [unknown]) is False


def test_mixed_company_remains_unresolved(engine):
    rows = _mercury_rows(engine, 300.0, mars=180.0)
    mercury = rows['Mercury']
    assert isinstance(mercury['effect'], engine['UnresolvedResult'])
    assert mercury['effect'].status == 'unresolved' and 'mixed benefic and malefic company' in mercury['effect'].reason


def test_releaser_table_and_selected_detail_render_typed_results():
    at = make_app(date='1240-02-02', page='releaser')
    at.session_state['_reading_depth'] = 'Course text and supplement'
    at.run()
    assert_no_exception(at, 'conditional years initial render')
    text = ' '.join(node.value for node in at.main.markdown)
    assert 'The supplied passages do not define the Moon’s orientality' in text
    assert 'the greater years, 108 (Moon)' in text and 'the lesser years, 25 (Moon)' in text

    detail = next(box for box in at.selectbox if box.label == 'Read details for'
                  and 'Mercury' in box.options)
    detail.select('Mercury').run()
    assert_no_exception(at, 'Mercury selected detail')
    detail_text = ' '.join(node.value for node in at.main.markdown)
    assert 'UnresolvedResult(' not in detail_text
    assert "Under the adopted reading of ‘which add,’ Mercury’s +20 requires" in detail_text

