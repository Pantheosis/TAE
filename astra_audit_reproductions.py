# Astra's reproduction harness, extracted verbatim from ASTRA_ENGINE_AUDIT_2026-09-11.md (appendix).
# Usage: python astra_audit_reproductions.py <directory containing Executable/app.py>
# On main 96fd547 (2026-09-11): 23 FAIL, 4 PASS -- see ASTRA_ENGINE_AUDIT_TRIAGE_2026-09-11.md.
from pathlib import Path
from datetime import datetime, date, timedelta
from unittest.mock import patch
import os, sys, math, tempfile

os.environ['ALMUTEN_NO_PREFERENCES'] = '1'
os.environ['XDG_DATA_HOME'] = tempfile.mkdtemp(prefix='astrology-audit-')
import swisseph as swe

base = Path(sys.argv[1]).resolve()
app = base / 'Executable/app.py'
source = app.read_text()
e = {'__name__': 'audit_engine', '__file__': str(app)}
exec(compile(source.split('# 4. STREAMLIT UI INTEGRATION')[0], str(app), 'exec'), e)
failed = 0

def check(name, ok, detail):
    global failed
    failed += not ok
    print(('PASS ' if ok else 'FAIL ') + name + ': ' + str(detail))

def P(lon, speed=1.0, lat=0.0):
    return dict(longitude=float(lon), latitude=float(lat), distance=1.0,
                speed_in_lon=float(speed), speed_in_lat=0.0, speed_in_dist=0.0)

def fixture(**overrides):
    p = {n:P(l,v) for n,l,v in [
        ('Sun',280,1), ('Moon',160,13), ('Mercury',270,1.2),
        ('Venus',300,1.1), ('Mars',210,.5), ('Jupiter',90,.08),
        ('Saturn',330,.03), ('North Node',200,-.05)]}
    p.update(overrides)
    return p

# F01. These deliberately reproduce the current input adapter.
check('F01 Julian validation', e['parse_iso_date']('1300-02-29') is not None,
      e['parse_iso_date']('1300-02-29'))
j = swe.julday(1300,2,29,12,swe.JUL_CAL)
try:
    got = e['pn4_datetime_from_jd'](j)
    check('F01 Julian reverse conversion', (got.year,got.month,got.day)==(1300,2,29), got)
except ValueError as exc:
    check('F01 Julian reverse conversion', False, repr(exc))
local = datetime(1300,3,1,0,30)
current_adapter_ut = local - timedelta(hours=2)
actual = e['calculate_traditional_chart'](current_adapter_ut,0,30)['julian_day']
expected = swe.julday(1300,3,1,0.5,swe.JUL_CAL)-2/24
check('F01 current offset adapter', abs(actual-expected)<1e-8, (actual,expected))

# F02/F03/F11. Target dates use the application's documented noon convention.
c = e['calculate_traditional_chart'](datetime(2000,1,1,12),0,0)
b = e['pn4_timing_bundle'](c,0,0,date(2000,1,1),date(2001,7,1),'forward')
check('F02 fardar', b['fardar']['sub_lord']=='Venus', b['fardar'])
b = e['pn4_timing_bundle'](c,0,0,date(2000,1,1),date(2012,10,21),'forward')
check('F02 distribution', b['current']['distributor']=='Saturn', b['current'])
c3 = e['calculate_traditional_chart'](datetime(2000,1,1,23),43.7792,11.2463)
b3 = e['pn4_timing_bundle'](c3,43.7792,11.2463,date(2000,1,1),date(2003,1,1),'forward')
check('F03 containing return', b3['jd_sr']<=2452641.0 and b3['month']==12,
      (b3['jd_sr'],b3['month'],b3['day_of_year']))
b1 = e['pn4_timing_bundle'](c,0,0,date(2000,1,1),date(2001,1,1),'forward')
# Use age 1 to isolate the presentation defect from the fractional-age defect.
oa = e['_oblique_ascension'](c['ascendant'],c['obliquity'],0)
endpoint = e['_lon_with_oblique_ascension'](oa+1,c['obliquity'],0)
check('F11 active degree', b1['year_rows'][1]['Active point']==e['get_degree_string'](endpoint),
      (b1['year_rows'][1]['Active point'],endpoint))

# F04. Independent Cartesian rotation and zenith dot product.
c4 = e['calculate_traditional_chart'](datetime(2000,1,1,1,40),51.5,0)
p = c4['planetary_data']; jup = p['Jupiter']
lam, beta, eps, theta, phi = map(math.radians,
    [jup['longitude'],jup['latitude'],c4['obliquity'],c4['armc'],51.5])
x = math.cos(beta)*math.cos(lam)
y = math.cos(beta)*math.sin(lam)*math.cos(eps)-math.sin(beta)*math.sin(eps)
z = math.cos(beta)*math.sin(lam)*math.sin(eps)+math.sin(beta)*math.cos(eps)
sinalt = math.sin(phi)*z+math.cos(phi)*(math.cos(theta)*x+math.sin(theta)*y)
acc = e['evaluate_accidental_dignities'](p,c4['houses'],c4['sect'])
assert sinalt<0 and c4['sect']=='Nocturnal' and 0<jup['longitude']<30
check('F04 Jupiter hayz', acc['Jupiter']['Hayz'] is True,
      {'Hayz':acc['Jupiter']['Hayz'],'altitude':math.degrees(math.asin(sinalt))})

# F05/F06. Patch only the external ephemeris within this isolated process.
def linear_ephemeris(p):
    ids = {e['PLANET_SWE_IDS'][n]:v for n,v in p.items()}
    def calc(t, who, *args):
        v = ids[who]
        return ((v['longitude']+t*v['speed_in_lon'])%360,0,1,
                v['speed_in_lon'],0,0),260
    return calc

p = {'Moon':P(1,13),'Mars':P(29,.5),'Saturn':P(40,.03)}
with patch.object(swe,'calc_ut',linear_ephemeris(p)):
    sim = e['_simulate_forward_uncached'](p,0,horizon_days=6,step_days=.1)
    rows = e['evaluate_escape'](p,sim)
    bad = [r for r in rows if r['Planet']=='Moon' and r['Escaped']=='Mars'
           and r['Connected Instead With']=='Saturn']
    check('F05 synthetic escape', not bad, bad)

p = {'Moon':P(29.636,13),'Sun':P(89.948,1)}
with patch.object(swe,'calc_ut',linear_ephemeris(p)):
    sim = e['_simulate_forward_uncached'](p,0,horizon_days=1,step_days=.25)
    exit_day = sim['events']['Moon']['sign_exits'][0]
    contact = e['_perfection_day'](sim,'Moon','Sun',60,before_day=exit_day)
    check('F06 contact before exit', contact is not None, (exit_day,contact))

# F05, real ephemeris corroboration. No location is needed for conjunction order.
p = {}
for name in ['Sun','Moon','Mercury','Venus','Mars','Jupiter','Saturn']:
    xx, _ = swe.calc_ut(2451587.0,e['PLANET_SWE_IDS'][name])
    p[name] = dict(zip(['longitude','latitude','distance','speed_in_lon',
                        'speed_in_lat','speed_in_dist'],xx))
sim = e['_simulate_forward_uncached'](p,2451587.0,horizon_days=100,step_days=1)
bad = [r for r in e['evaluate_escape'](p,sim) if r['Planet']=='Mars'
       and r['Escaped']=='Jupiter' and r['Connected Instead With']=='Moon']
check('F05 real escape', not bad,
      (bad,e['_body_union_day'](sim,'Mars','Jupiter'),e['_body_union_day'](sim,'Mars','Moon',after_day=39.6)))

# F07. Both longitude and reported speed describe the same quadratic.
def retro_ephemeris(t, who, *args):
    return (29.99+.12*t-.12*t*t,0,1,.12-.24*t,0,0),260
with patch.object(swe,'calc_ut',retro_ephemeris):
    sim = e['_simulate_forward_uncached']({'Mercury':P(29.99,.12)},0,
                                          horizon_days=1,step_days=1)
    crossings = sim['events']['Mercury']['sign_exits']
    check('F07 two sign crossings', len(crossings)==2, sim['events']['Mercury'])

# F08. Check the departing-receiver branch under the current Sahl policy.
for tag,p,expected_word in [
    ('missing',fixture(Moon=P(190.5,13),Venus=P(190,1)),'venus'),
    ('reversed',fixture(Moon=P(95.5,13),Saturn=P(95,.03),Jupiter=P(120,.08)),'saturn')]:
    ess = e['evaluate_essential_dignities'](p,'Diurnal')
    acc = e['evaluate_accidental_dignities'](p,tuple(range(0,360,30)),'Diurnal')
    rows = e['evaluate_weakness_of_planets'](p,ess,acc,0,'Diurnal')
    labels = next(r['Labels'] for r in rows if r['Planet']=='Moon')
    hit = any(x.startswith('Separating from') and expected_word in x.lower() for x in labels)
    check('F08 '+tag, hit if tag=='missing' else not hit, labels)

# F09. Eighteen arcseconds post-exact, avoiding the exact-one-minute float.
r = e['_pairwise_configurations']({'Moon':P(10.005,13),'Saturn':P(10,.03)})[0]
check('F09 separated', not e['_is_connected_abu_mashar'](r),
      (r['motion'],e['_is_connected_abu_mashar'](r)))

# F10. Opening eastern thresholds. Western controls must stay inclusive.
for name,lon,want in [('Saturn',94,'Under the rays'),('Saturn',85,None),
                      ('Mars',90,'Under the rays'),('Mars',82,None),
                      ('Mercury',93,'Under the rays'),('Mercury',88,None)]:
    got = e['solar_phase'](name,lon,100)[0]
    check('F10 '+name+' '+str(lon), got==want, (got,want))
check('western control', e['solar_phase']('Saturn',106,100)[0]=='Burned',
      e['solar_phase']('Saturn',106,100))

# F12/F13. Exact advertised endpoint and an entered sexagesimal minute.
r = e['pn4_fardar_at_age'](4.0,'Diurnal')
r2 = e['pn4_fardar_at_age'](r['sub_to'],'Diurnal')
check('F12 subperiod endpoint', r2['sub_lord']=='Moon', r2)
check('F13 minute round trip', e['get_degree_string'](30+1/60)=="00° Tau 01'",
      e['get_degree_string'](30+1/60))

# Selected non-defect/source-policy controls.
check('twelfth-part source formula', e['pn4_twelfth_part'](35.25)==93,
      e['pn4_twelfth_part'](35.25))
check('source wells count', sum(map(len,e['WELLED_DEGREES'].values()))==64,
      sum(map(len,e['WELLED_DEGREES'].values())))
check('25 thirds equal one symbolic hour',
      e['pn4_arc_to_time'](25/216000)['hours']==1,
      e['pn4_arc_to_time'](25/216000))
print('Failing expectation count:',failed)
