import math
import pytest
from pyutloc import normalize,detect,encode,FORMATS,UNITS
from pyutloc.geocoding import Geocoder,ServiceError
K={'source_crs':'EPSG:4326','axis_order':'latlon'}
@pytest.mark.parametrize('text,expected',[
 ('-0° 30\' 0" 0° 15\' 0"',(-.5,.25)),
 ('S 0° 30′ 0″ W 0° 15′ 0″',(-.5,-.25)),
 ('34° 7.2\' S 118° 25.8\' E',(-34.12,118.43)),
 ('90° 0\' 0" N 180° 0\' 0" E',(90,180)),
 ('−0.5°, 1.25°',(-.5,1.25)),
 ('1e-2 -2e-2',(.01,-.02)),
])
def test_independent_angles(text,expected):
    r=normalize(text,**K);assert r.status=='ok',r;assert (r.latitude,r.longitude)==pytest.approx(expected)
@pytest.mark.parametrize('text',['91 0','0 181','1° 60\' 0° 0\'','1° 0\' 60" 0° 0\' 0"','NaN 3','inf 0','-10N 20E','10E 20N','1234','1 2 trailing'])
def test_invalid(text):assert normalize(text,**K).status!='ok'
def test_ambiguous():
    assert detect('20 30').status=='ambiguous'
    assert normalize('20° 30°',source_crs=4326).status=='requires_metadata'
    assert normalize('123.0m 456.0m').status=='requires_metadata'
    assert detect('18SUJ2348306479').candidates==('MGRS','USNG')
def test_utm_oracle():
    r=normalize('33U 308124.3678624593 6098907.825129169',source_crs=4326,utm_convention='band')
    assert r.status=='ok';assert (r.latitude,r.longitude)==pytest.approx((55,12),abs=1e-8)
    assert normalize('33U 308124 6098907',source_crs=4326).status=='requires_metadata'
    assert normalize('61N 500000 5000000',source_crs=4326,utm_convention='band').status=='invalid'
def test_crs_and_units():
    r=normalize('111319.49079327357m 0m',source_crs=3857)
    assert r.status=='ok';assert r.longitude==pytest.approx(1,abs=1e-10)
    assert UNITS['pt']==pytest.approx(.0254/72)
    assert UNITS['usft']==pytest.approx(1200/3937)
    assert UNITS['mi']==1609.344
@pytest.mark.parametrize('fmt',FORMATS)
def test_representative_roundtrip(fmt):
    lat,lon=(87.2,120.3) if fmt=='UPS' else (-.51,-70.21)
    s=encode(lat,lon,fmt,target_crs=3857)
    r=normalize(s,source_crs=3857 if fmt.startswith('PM') else 4326,axis_order='latlon',format_hint=fmt,utm_convention='band')
    assert r.status=='ok',(fmt,s,r)
    # Cell systems intentionally lose precision; this is a coarse smoke bound.
    assert abs(r.latitude-lat)<.1 and abs(r.longitude-lon)<.1
def test_dms_carry_and_sign():
    s=encode(-.99999999999,1.99999999999,'DMS1')
    assert '60' not in s
    r=normalize(s,**K);assert r.latitude==pytest.approx(-1)
def test_grid_rejects_wrong_datum():
    assert normalize('18SUJ2348306479',source_crs=4269,format_hint='USNG').status=='invalid'
def test_geocoder_retry_cache_context():
    now=[0.];n=[0]
    def fail(q):n[0]+=1;raise ServiceError('rate limit',retryable=True,retry_after=2)
    def good(q):return (10.,20.,'EPSG:4326')
    g=Geocoder({'a':fail,'b':good},cache={},clock=lambda:now[0],sleep=lambda x:now.__setitem__(0,now[0]+x))
    a=g.geocode('Paris',context='France');b=g.geocode('Paris',context='France');c=g.geocode('Paris',context='Texas')
    assert a.status=='ok' and a.attempts==4 and n[0]==6
    assert b.cache_hit and not c.cache_hit

@pytest.mark.parametrize("lat,lon", [(22.593047,114.249914),(-0.00001,-0.00001),(-1.0000001,179.999999),(90,180),(-90,-180)])
def test_maidenhead_boundary_containment(lat,lon):
    for precision in (2,3,4):
        v=normalize(encode(lat,lon,'MAIDENHEAD',precision=precision))
        assert v.status=='ok'
        s,w,n,e=v.cell_bounds
        assert s-1e-10<=lat<=n+1e-10
        assert any(w-1e-10<=ll<=e+1e-10 for ll in (lon,lon-360,lon+360))

def test_invalid_crs_is_diagnostic():
    assert normalize('20 30', source_crs='nonsense', axis_order='latlon').status=='invalid'

def test_malformed_provider_response_and_declared_crs():
    from pyutloc.geocoding import geopy_adapter
    g=Geocoder({'malformed':lambda q:(None,20,'EPSG:4326'),
                'valid':lambda q:(10.,20.,'EPSG:4326')})
    r=g.geocode('fixture')
    assert r.status=='ok' and r.provider=='valid'
    assert r.trace[0]['status']=='malformed_response'
    class Locator:
        def geocode(self,q,exactly_one=True):
            return type('Place',(),{'latitude':10.,'longitude':20.})()
    a=geopy_adapter(Locator(),crs='EPSG:4269')
    assert Geocoder({'other_datum':a}).geocode('fixture').status=='failed'

def test_compatibility_facades_keep_metadata_explicit():
    from pyutloc.transformation import DD1toOthers,OtherstoDD1
    text=DD1toOthers(39.9,116.4).dd1_to_dms3()
    assert OtherstoDD1(text,source_crs=4326).dms3_to_dd1()=='39.90000000 116.40000000'
    with pytest.raises(ValueError):OtherstoDD1(text).dms3_to_dd1()
