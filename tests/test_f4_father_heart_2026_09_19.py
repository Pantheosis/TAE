"""Adopted G04-A and cross-group heart cases, including downstream values."""
from datetime import datetime
import pytest
from conftest import make_app, assert_no_exception


def chart(engine, **positions):
    c = engine['calculate_traditional_chart'](datetime(1240, 5, 23, 14), 43.7792, 11.2463)
    for p, lon in positions.items():
        c['planetary_data'][p]['longitude'] = lon
    return c


def _testimonies(engine, c, planet):
    p = c['planetary_data']
    ess = engine['evaluate_essential_dignities'](p, c['sect'])
    acc = engine['evaluate_accidental_dignities'](p, c['houses'], c['sect'])
    s = engine['evaluate_strength_of_planets'](p, ess, acc, c['ascendant'], c['sect'], c['houses'])
    w = engine['evaluate_weakness_of_planets'](p, ess, acc, c['ascendant'], c['sect'])
    return [set(t['n'] for r in rows if r['Planet'] == planet for t in r['Testimonies']) for rows in (s, w)]


@pytest.mark.parametrize('delta', [-1.001, -1., -.5, 0., .5, 1., 1.001])
def test_sahl_heart_excludes_rays_on_both_sides(engine, delta):
    c = chart(engine, Sun=0., Mercury=delta % 360)
    s, w = _testimonies(engine, c, 'Mercury')
    assert ('87' in s) == (abs(delta) <= 1.)
    assert ('93' in w) == (abs(delta) > 1.)


@pytest.mark.parametrize('sect', ['Diurnal', 'Nocturnal'])
@pytest.mark.parametrize('delta,substitute', [(-15.001,False),(-15.,False),(-14.999,True),(-1.001,True),(-1.,False),(-.5,False),(0.,False),(.5,False),(1.,False),(1.001,True),(14.999,True),(15.,True),(15.001,False)])
def test_father_selection_boundaries_and_night_order(engine, sect, delta, substitute):
    c = chart(engine, Sun=0., Saturn=delta % 360, Mars=210., Jupiter=310.)
    p = c['planetary_data']; asc = 10.
    expected = 110. if substitute else (asc + (delta if sect == 'Diurnal' else -delta)) % 360
    assert engine['lot_by_id']('father', p, asc, c['houses'], sect) == pytest.approx(expected)
    rows = [r for r in engine['calculate_topical_lots'](p, asc, c['houses'], sect) if r['Topic'] == 'Father']
    ordinary, sahl, hermes = rows
    assert ordinary['Status'] == ('Replaced — reference calculation' if substitute else 'Selected — read and directed')
    assert sahl['Status'] == ('Selected — read and directed' if substitute else
                             'Not applicable — heart exception under the selected reading' if abs(delta) <= 1 else 'Not applicable')
    assert 'Selected — read and directed' != hermes['Status']
    assert 'Hermes' in hermes['Lot']
    assert sahl['Position'] == engine['get_degree_string'](110.)
    assert 'night reversal unstated in Sahl; stated order retained' in sahl['Formula']


def test_prosperity_clean_heart_lord_does_not_open_lot_step(engine):
    from test_prosperity_2026_09_15 import _chart
    c = _chart(engine, 'Diurnal', ('Scorpio',15), lot=True, Sun=('Gemini',10),
               Saturn=('Taurus',20), Mercury=('Gemini',10.5), Moon='Virgo',
               Mars='Capricorn', Venus='Cancer', Jupiter='Pisces')
    rows = engine['evaluate_prosperity'](c)
    lords = next(r for r in rows if r['key'] == 'lords')
    assert 'under the rays (no strength, 2.11, 5)' not in lords['Ground']
    assert rows[0]['key'] == 'high'


@pytest.mark.parametrize('sect', ['Diurnal','Nocturnal'])
@pytest.mark.parametrize('target_year', [1245,1260])
def test_father_bundle_uses_selected_degree_for_harmers_and_direction(engine,sect,target_year):
    c = chart(engine, Sun=100., Saturn=110., Mars=210., Jupiter=310.)
    p = c['planetary_data']; c['sect'] = sect
    expected = (c['ascendant'] + 100.) % 360
    b = engine['pn4_timing_bundle'](c,43.7792,11.2463,datetime(1240,5,23).date(),
                                  datetime(target_year,5,24).date(), engine['PN4_MONTHLY_TURN_OPTIONS'][0])
    f = b['father_lot']
    assert f['lot'] == pytest.approx(expected)
    assert f['second'] == ('Sun' if sect=='Diurnal' else 'Saturn')
    assert f['harmers'] == engine['sahl_father_lot_harmers'](sect,p,expected,100.)
    assert f['from_lot'] == engine['sahl_house_master_direction'](p,None,c['obliquity'],43.7792,
        origin_jd=c['julian_day'],start_lon=expected,sun_target=False,target_planets=(('Mars','Saturn','Mercury') if sect=='Diurnal' else ('Mars','Mercury')))
    assert f['selection']['formula_id'] == 'father_burnt'


@pytest.mark.parametrize('sun,delta', [(0.,0.),(0.,16/60),(0.,16/60+.00001),(0.,20/60),(359.75,.5),(.25,-.5),(0.,1.),(0.,1.00001)])
def test_named_source_heart_and_accidental_convention(engine, sun, delta):
    c=chart(engine,Sun=sun,Mercury=(sun+delta)%360)
    p=c['planetary_data'];lon=p['Mercury']['longitude']
    assert (engine['solar_phase']('Mercury',lon,sun,source='Sahl')[0]=='Cazimi') == (abs(delta)<=1)
    assert (engine['solar_phase']('Mercury',lon,sun)[0]=='Cazimi') == (abs(delta)<=16/60)
    acc=engine['evaluate_accidental_dignities'](p,c['houses'],c['sect'])
    assert acc['Mercury']['Cazimi'] == (abs(delta)<=16/60)
    assert not engine['in_solar_heart']('Sun',sun,sun,source='Sahl')


@pytest.mark.parametrize('delta,retrograde,expected',[(.5,False,False),(.5,True,True),(1.001,False,True)])
def test_returning_ray_exception_retains_retrograde(engine, monkeypatch, delta, retrograde, expected):
    c=chart(engine,Sun=100.,Saturn=100.+delta,Mercury=95.)
    p=c['planetary_data'];acc=engine['evaluate_accidental_dignities'](p,c['houses'],c['sect'])
    acc['Saturn']['Retrograde']=retrograde
    # Isolate the accepted connection; F4 changes the receiver's solar qualification only.
    monkeypatch.setitem(engine,'_pairwise_configurations',lambda _: [{'aspect_name':'Conjunction','motion':'Applying','applicant':'Mercury','receiver':'Saturn'}])
    monkeypatch.setitem(engine,'_is_connected',lambda _:True)
    rows=engine['evaluate_returning'](p,acc,c['ascendant'])
    assert any(r['Manner']=='I (65)' for r in rows)==expected


def test_sahl_years_ranking_revolution_and_jn_source_separation(engine):
    c=chart(engine,Sun=100.,Mercury=100.5)
    p=c['planetary_data'];ess=engine['evaluate_essential_dignities'](p,c['sect'])
    years=engine['sahl_house_master_years']('Mercury',p,c['houses'],c['sect'],ess)
    assert years['facts']['under the rays'] is False
    assert engine['_jn_solar_facts']('Mercury',p,years['facts'])['under the rays'] is True
    rank=engine['_sahl_rank_house_master']({'both_at_once':False, 'looking':[], 'sharer_1_20_6':('house','Mercury')},p,c['houses'])
    assert rank[0]['Under the rays']=='Cazimi'
    rows=engine['sahl_house_master_in_revolution']('Mercury',c,c)
    assert next(r['Reads'] for r in rows if r['Fact']=='Burned at the revolution').startswith('Cazimi')


@pytest.mark.parametrize('delta,under',[(.5,False),(1.,False),(1.001,True),(13.,True),(15.,True),(15.001,False)])
def test_moon_releaser_fixed_radius_and_heart(engine, delta, under):
    c=chart(engine,Sun=100.,Moon=100.+delta);p=c['planetary_data']
    result=engine['_sahl_examine_candidate']('Moon',p['Moon']['longitude'],p,c['houses'],c['sect'],engine['SAHL_RELEASER_NIGHT_PLACES'],self_planet='Moon')
    assert result['under_1_19_6'] is under


def test_moon_corruption_burning_remains_independent(engine):
    c=chart(engine,Sun=100.,Moon=100.5)
    rows=engine['evaluate_corruption_of_the_moon'](c['planetary_data'],c['ascendant'],c['sect'])
    assert '103' in str(rows)
    strength,weakness=_testimonies(engine,c,'Moon')
    assert '87' in strength and '93' not in weakness


def test_unavailable_substitute_does_not_fall_back(engine):
    c=chart(engine,Sun=100.,Saturn=110.)
    del c['planetary_data']['Jupiter']
    result=engine['father_lot_selection'](c['planetary_data'],c['ascendant'],c['houses'],c['sect'])
    assert isinstance(result,engine['UnresolvedResult']) and result.status=='unavailable'
    assert engine['lot_by_id']('father',c['planetary_data'],c['ascendant'],c['houses'],c['sect']) is None


def test_operational_lot_inventory_excludes_comparison_degrees(engine):
    c=chart(engine,Sun=100.,Saturn=110.,Mars=210.,Jupiter=310.)
    c['ascendant']=10.;c['sect']='Diurnal'
    # Ordinary=20 Aries, selected=110 Cancer, Hermes=220 Scorpio.
    assert 'Lot of the father' not in engine['_pn4_lots_in_sign'](c,'Aries')
    assert engine['_pn4_lots_in_sign'](c,'Cancer').count('Lot of the father')==1
    all_names=[n for sign in engine['SIGN_ORDER'] for n in engine['_pn4_lots_in_sign'](c,sign)]
    assert not any('Saturn under the rays' in n for n in all_names)


@pytest.mark.parametrize('page',['chart','dignities','findings','configurations','lots','victors','timing','releaser','days','fardar','reference','sources'])
def test_synthetic_chart_pages_have_readable_cells(monkeypatch,page):
    at=make_app(date='1240-05-23',page=page)
    at.session_state['_target_date']='2026-09-17'
    at.session_state['_reading_depth']='Course text and supplement'
    import engine as module
    original=module.calculate_traditional_chart_jd
    def synthetic(*args,**kwargs):
        c=original(*args,**kwargs);p=c['planetary_data'];sun=p['Sun']['longitude']
        for name,delta in [('Mercury',.5),('Saturn',10.),('Mars',110.),('Jupiter',210.)]:
            p[name]['longitude']=(sun+delta)%360
        return c
    monkeypatch.setattr(module,'calculate_traditional_chart_jd',synthetic)
    at.run();assert_no_exception(at)
    frames=[el.value for el in at.main.dataframe]+[el.value for el in at.main.table]
    for frame in frames:
        exported=frame.to_csv(index=False)
        assert 'UnresolvedResult(' not in exported and 'YearsOutcome(' not in exported
    import json
    analysis=at.session_state['_analysis_export']
    exported=json.dumps(analysis)
    assert 'UnresolvedResult(' not in exported and 'YearsOutcome(' not in exported
    text='\n'.join(node.value for node in at.main.markdown)
    if page=='lots':
        father=next(f for f in frames if 'Status' in f.columns and 'Position' in f.columns)
        father=father[father['Topic']=='Father']
        assert father.iloc[0]['Status']=='Replaced — reference calculation'
        assert father.iloc[1]['Status']=='Selected — read and directed'
        exported_rows=analysis['results']['Lots']['Topical Lots (Sahl, On Nativities)'][0]['rows']
        for row in father.to_dict('records'):
            saved=next(r for r in exported_rows if r['Lot']==row['Lot'])
            assert all(saved[key]==value for key,value in row.items())
        assert module.FATHER_SUBSTITUTION_TEXT in text
    if page=='releaser':
        assert 'Ascendant + (Jupiter - Mars)' in text
        assert module.FATHER_SUBSTITUTION_TEXT in text


@pytest.mark.parametrize('delta,classes',[(13.,['high','low to high']),(.5,['high','high'])])
def test_prosperity_moon_switch_changes_outer_rays_but_not_heart(engine,delta,classes):
    from test_prosperity_2026_09_15 import _chart
    c=_chart(engine,'Nocturnal','Taurus',Sun=('Taurus',10),Moon=('Taurus',10+delta),Venus='Pisces',Mars='Libra',Saturn='Gemini',Jupiter='Sagittarius',Mercury='Gemini')
    old=engine['reading']('MOON_RAYS_ORB')
    try:
        got=[]
        for radius in (12.,15.):
            engine['set_readings'](MOON_RAYS_ORB=radius)
            got.append(engine['evaluate_prosperity'](c)[0]['key'])
        assert got==classes
    finally:
        engine['set_readings'](MOON_RAYS_ORB=old)


@pytest.mark.parametrize('sect,rank',[('Diurnal','second'),('Nocturnal','first')])
@pytest.mark.parametrize('other',['none','falling','malefic'])
def test_prosperity_heart_lord_other_afflictions_still_open_lot_step(engine,sect,rank,other):
    from test_prosperity_2026_09_15 import _chart
    # Air triplicity: Saturn/Mercury by day, Mercury/Saturn by night.
    asc='Aries' if other=='falling' else 'Scorpio'
    c=_chart(engine,sect,asc,lot=False,Sun=('Gemini',10),Mercury=('Gemini',10.5),
             Saturn=('Taurus',20),Moon='Libra',Mars='Virgo' if other=='malefic' else 'Capricorn',Venus='Cancer',Jupiter='Pisces')
    rows=engine['evaluate_prosperity'](c);ground=rows[0]['Ground']
    assert 'Mercury under the rays' not in ground
    if other=='none':assert 'the Lot step (2.3, 6)' not in ground
    else:assert 'the Lot step (2.3, 6)' in ground and 'Mercury' in ground


def test_prosperity_partner_in_heart_has_strength(engine):
    from test_prosperity_2026_09_15 import _chart
    c=_chart(engine,'Diurnal','Aries',Sun=('Aries',10),Saturn=('Aries',10.5),Jupiter='Sagittarius',Mercury='Gemini',Venus='Taurus',Mars='Virgo',Moon='Aquarius')
    rows=engine['evaluate_prosperity'](c)
    partner=next(r for r in rows if r['key']=='third')
    assert 'under the rays' not in partner['Ground']
    assert 'supports' in partner['Ground']



def test_life_lords_disclose_both_solar_sources_in_actual_cells_and_export(monkeypatch):
    at=make_app(date='1240-05-23',page='fardar')
    import engine as module
    original=module.calculate_traditional_chart_jd
    def chart_with_heart_mercury(*args,**kwargs):
        c=original(*args,**kwargs);c['sect']='Diurnal'
        c['planetary_data']['Sun']['longitude']=60.
        c['planetary_data']['Mercury']['longitude']=60.5
        return c
    monkeypatch.setattr(module,'calculate_traditional_chart_jd',chart_with_heart_mercury)
    at.run();assert_no_exception(at)
    table=next(node.value for node in at.main.dataframe if 'Time of life' in node.value.columns)
    row=table[table['Lord']=='Mercury'].iloc[0]
    assert "Abu Ma'shar (heart through 16′):" in row['Root condition']
    assert 'burned' in row['Root condition']
    assert 'Sahl (heart through 1°): in the heart' in row['Root condition']
    analysis=at.session_state['_analysis_export']
    exported=[r for tables in analysis['results'].values() for entries in tables.values()
              for entry in entries for r in entry['rows'] if r.get('Lord')=='Mercury' and 'Time of life' in r]
    assert exported and all(r['Root condition']==row['Root condition'] for r in exported)
