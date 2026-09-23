"""Refactored annotation / DD1 pivot design from the supplied 2026 notebooks.

The registry keeps the 55 historical labels. They are notation/unit variants,
not independent coordinate reference systems. USGN is a legacy spelling of USNG.
No routine infers a geodetic datum from coordinate text.
"""
from dataclasses import dataclass, field, asdict
from functools import lru_cache
import math, re, unicodedata
from typing import Iterable
from pyproj import CRS as _CRS, Transformer
from pyproj.exceptions import CRSError

@lru_cache(maxsize=128)
def CRS(value):
    return _CRS(value)

UNITS = {'m':1., 'cm':.01, 'dm':.1, 'ft':.3048, 'in':.0254,
         'km':1000., 'mi':1609.344, 'mm':.001, 'nmi':1852.,
         'pt':.0254/72, 'usft':1200/3937, 'yd':.9144}
UNIT_LIST=list(UNITS)
FORMATS = ['DD1','DD2','DD3','DDM1','DDM2','DDM3','DMS1','DMS2','DMS3',
           'GARS','GEOREF','MGRS','USNG','UTM1','UTM2','UPS','PLUS_CODES','GEOHASH','MAIDENHEAD']
FORMATS += [f'{p}{i}' for p in ['PMS','PMB','PME'] for i in range(1,13)]
NUM=r'[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?'
UN=r'(?:usft|ftUS|nmi|cm|dm|km|mm|ft|in|mi|pt|yd|m)'
DEG=rf'{NUM}\s*°?'
DM=rf'[+-]?\d+\s*°\s*(?:\d+(?:\.\d*)?|\.\d+)\s*\x27'
DMS=rf'[+-]?\d+\s*°\s*\d+\s*\x27\s*(?:\d+(?:\.\d*)?|\.\d+)\s*"'
SEP=r'(?:\s*[,;]\s*|\s+)'
ANGLE_PATTERNS=[]
for family,body in [('DMS',DMS),('DDM',DM),('DD',DEG)]:
    ANGLE_PATTERNS += [(family+'1',re.compile(rf'^({body}){SEP}({body})$')),
        (family+'2',re.compile(rf'^({body}\s*[NS])\s*[,;]?\s*({body}\s*[EW])$',re.I)),
        (family+'3',re.compile(rf'^([NS]\s*{body})\s*[,;]?\s*([EW]\s*{body})$',re.I))]
PROJECTED=[('PMS',re.compile(rf'^({NUM})\s*({UN}){SEP}({NUM})\s*({UN})$')),
 ('PMB',re.compile(rf'^({NUM})\s*({UN})\s*([EW]){SEP}({NUM})\s*({UN})\s*([NS])$',re.I)),
 ('PME',re.compile(rf'^([EW])\s*({NUM})\s*({UN}){SEP}([NS])\s*({NUM})\s*({UN})$',re.I))]
@dataclass(frozen=True)
class Detection:
    status: str
    candidates: tuple[str,...]=()
    reason: str=''
    normalized_text: str=''

@dataclass
class Result:
    status: str
    format: str|None=None
    latitude: float|None=None
    longitude: float|None=None
    source_crs: str|None=None
    target_crs: str='EPSG:4326'
    reason: str=''
    cell_bounds: tuple|None=None  # south, west, north, east in degrees
    operation_accuracy_m: float|None=None
    provenance: dict=field(default_factory=dict)
    def to_dict(self): return asdict(self)

def canonical(fmt):
    f=str(fmt).upper().replace(' ','_')
    return {'USGN':'USNG','PLUS_CODE':'PLUS_CODES','MAIDENHEAD_GRID':'MAIDENHEAD'}.get(f,f)

def clean(text):
    if not isinstance(text,str): raise ValueError('coordinate must be a string')
    if len(text)>4096: raise ValueError('coordinate exceeds 4096 characters')
    return unicodedata.normalize('NFKC',text).translate(str.maketrans({'−':'-','′':"'",'″':'"','’':"'",'“':'"','”':'"'})).strip().replace("''",'"')

def angle(s, limit):
    direction=re.search(r'[NSEW]\s*$',s,re.I) or re.match(r'\s*[NSEW]',s,re.I)
    ch=direction.group().strip().upper() if direction else ''
    vals=re.findall(NUM,re.sub(r'^[NSEW]|[NSEW]$','',s.strip(),flags=re.I))
    if not vals or len(vals)>3: raise ValueError('invalid angular components')
    v=[float(x) for x in vals]
    if len(v)>1 and not 0<=v[1]<60: raise ValueError('minutes outside [0,60)')
    if len(v)>2 and not 0<=v[2]<60: raise ValueError('seconds outside [0,60)')
    sign=-1 if vals[0].startswith('-') else 1
    if ch:
        if limit==90 and ch not in 'NS' or limit==180 and ch not in 'EW': raise ValueError('axis hemisphere mismatch')
        if vals[0].startswith('-') or vals[0].startswith('+'): raise ValueError('signed number combined with hemisphere')
        sign=-1 if ch in 'SW' else 1
    value=sign*(abs(v[0])+(v[1]/60 if len(v)>1 else 0)+(v[2]/3600 if len(v)>2 else 0))
    if not math.isfinite(value) or abs(value)>limit: raise ValueError('angle outside valid range')
    return value

def _projected(s):
    for p,rx in PROJECTED:
        m=rx.fullmatch(s)
        if not m: continue
        a=m.groups()
        if p=='PMS': x,u,y,v=a; ex=ny=''
        elif p=='PMB': x,u,ex,y,v,ny=a
        else: ex,x,u,ny,y,v=a
        u='usft' if u.lower() in ['ftus','usft'] else u.lower()
        v='usft' if v.lower() in ['ftus','usft'] else v.lower()
        if u!=v: raise ValueError('mixed axis units require separate fields')
        if ex and (x.startswith(('-', '+')) or y.startswith(('-', '+'))): raise ValueError('signed projected number combined with direction')
        xx=float(x)*UNITS[u]*(-1 if ex.upper()=='W' else 1)
        yy=float(y)*UNITS[v]*(-1 if ny.upper()=='S' else 1)
        if not math.isfinite(xx+yy): raise ValueError('nonfinite coordinate')
        return p+str(UNIT_LIST.index(u)+1),xx,yy
    return None

def detect(text, *, source_crs=None, axis_order=None, format_hint=None):
    try:
        s=clean(text)
        hint=canonical(format_hint) if format_hint else None
        p=_projected(s)
        if p: return Detection('ok',(p[0],),'explicit unit; source CRS still required',s)
        for f,rx in ANGLE_PATTERNS:
            m=rx.fullmatch(s)
            if m:
                if f=='DD1' and '°' not in s and not source_crs and not hint:
                    return Detection('ambiguous',('DD1','PROJECTED'),'bare numeric pair requires CRS and axis order',s)
                if f=='DD1' and source_crs and CRS(source_crs).is_projected:
                    return Detection('ok',('PROJECTED',),'CRS axis units',s)
                a,b=m.groups()
                limits=(180,90) if axis_order=='lonlat' and f.endswith('1') else (90,180)
                angle(a,limits[0]);angle(b,limits[1])
                return Detection('ok',(f,),'validated angular components',s)
        compact=s.replace(' ','')
        candidates=[]
        if re.fullmatch(r'(?:\d{1,2}[C-HJ-NP-X]|[ABYZ])[A-HJ-NP-Z]{2}(?:\d{2}){0,5}',compact,re.I):
            candidates+=['MGRS','USNG']
        elif re.fullmatch(r'\d{1,2}[C-HJ-NP-X]\s+\d+(?:\.\d+)?\s+\d+(?:\.\d+)?',s): candidates=['UTM1']
        elif re.fullmatch(r'\d{1,2}[C-HJ-NP-X]\d{6}\d{1,7}(?:\.\d+)?',s): candidates=['UTM2']
        elif re.fullmatch(r'(?:00\s+)?[NS]\s+\d+(?:\.\d+)?\s+\d+(?:\.\d+)?',s): candidates=['UPS']
        elif re.fullmatch(r'\d{3}[A-HJ-NP-Z]{2}[1-4]?[1-9]?',s): candidates=['GARS']
        elif re.fullmatch(r'[A-HJ-NP-Z]{4}(?:\d{2}){0,6}',s): candidates=['GEOREF']
        elif re.fullmatch(r'[2-9CFGHJMPQRVWX0]{2,8}\+[2-9CFGHJMPQRVWX]{0,7}',s,re.I): candidates=['PLUS_CODES']
        elif re.fullmatch(r'[A-Ra-r]{2}\d{2}(?:[A-Xa-x]{2}(?:\d{2})?)?',s): candidates=['MAIDENHEAD']
        elif re.fullmatch(r'[0-9bcdefghjkmnpqrstuvwxyz]{4,12}',s): candidates=['GEOHASH','SCALAR'] if s.isdigit() else ['GEOHASH']
        if hint and hint in candidates: return Detection('ok',(hint,),'format supplied',s)
        if len(candidates)>1: return Detection('ambiguous',tuple(candidates),'multiple interpretations; supply format convention and datum',s)
        if candidates: return Detection('ok',tuple(candidates),'syntax candidate; decoder validation required',s)
        return Detection('invalid',(),'unsupported or malformed coordinate',s)
    except (ValueError,OverflowError,TypeError,CRSError) as e:
        return Detection('invalid',(),str(e),'')

@lru_cache(maxsize=128)
def transformer(src,dst):
    return Transformer.from_crs(src,dst,always_xy=True,allow_ballpark=False,only_best=True)

def _reproject(x,y,src):
    t=transformer(str(src),'EPSG:4326')
    lon,lat=t.transform(x,y,errcheck=True)
    # Only clamp floating-point endpoint drift, never an out-of-domain input.
    if 180<abs(lon)<=180+1e-10: lon=math.copysign(180,lon)
    if 90<abs(lat)<=90+1e-10: lat=math.copysign(90,lat)
    if not math.isfinite(lat+lon) or abs(lat)>90 or abs(lon)>180: raise ValueError('invalid transformed result')
    return lat,lon,(t.accuracy if t.accuracy>=0 else None)

def normalize(text, *, source_crs=None, axis_order=None, format_hint=None, utm_convention=None):
    d=detect(text,source_crs=source_crs,axis_order=axis_order,format_hint=format_hint)
    if d.status!='ok': return Result(d.status,reason=d.reason,provenance={'candidates':d.candidates})
    f=d.candidates[0];s=d.normalized_text
    r=Result('ok',format=f,source_crs=str(source_crs) if source_crs else None,
             provenance={'input':text,'axis_order':axis_order,'utm_convention':utm_convention})
    try:
        if f.startswith(('PMS','PMB','PME')) or f=='PROJECTED':
            if not source_crs: return Result('requires_metadata',f,reason='source CRS is required')
            crs=CRS(source_crs)
            if not crs.is_projected: raise ValueError('projected notation requires a projected CRS')
            if f=='PROJECTED':
                if axis_order not in ('xy','yx'): return Result('requires_metadata',f,reason='xy or yx order is required')
                vals=re.findall(NUM,s);x,y=map(float,vals)
                if axis_order=='yx': x,y=y,x
            else:
                _,x,y=_projected(s)
                # text numbers are converted to metres, then to CRS-native units
                x/=crs.axis_info[0].unit_conversion_factor;y/=crs.axis_info[1].unit_conversion_factor
            r.latitude,r.longitude,r.operation_accuracy_m=_reproject(x,y,source_crs)
        elif f.startswith(('DD','DMS')):
            if not source_crs: return Result('requires_metadata',f,reason='source geodetic CRS is required')
            if not CRS(source_crs).is_geographic: raise ValueError('angular notation requires geographic CRS')
            m=next(rx.fullmatch(s) for ff,rx in ANGLE_PATTERNS if ff==f)
            a,b=m.groups()
            if f.endswith('1'):
                if axis_order not in ('latlon','lonlat'): return Result('requires_metadata',f,reason='latlon or lonlat order is required')
                if axis_order=='lonlat': b,a=a,b
            lat,lon=angle(a,90),angle(b,180)
            r.latitude,r.longitude,r.operation_accuracy_m=_reproject(lon,lat,source_crs)
        elif f in ('UTM1','UTM2'):
            if utm_convention not in ('band','hemisphere'): return Result('requires_metadata',f,reason='UTM band or hemisphere convention is required')
            if source_crs is None: return Result('requires_metadata',f,reason='WGS84 datum declaration is required for UTM')
            if CRS(source_crs)!=CRS(4326): raise ValueError('encoded UTM adapter currently requires WGS84; use projected coordinates for other datums')
            if f=='UTM1': m=re.fullmatch(r'(\d{1,2})([C-HJ-NP-X])\s+(\d+(?:\.\d+)?)\s+(\d+(?:\.\d+)?)',s)
            else: m=re.fullmatch(r'(\d{1,2})([C-HJ-NP-X])(\d{6})(\d{1,7}(?:\.\d+)?)',s)
            z,band,x,y=m.groups();z=int(z);x=float(x);y=float(y)
            if not 1<=z<=60 or not 100000<=x<1000000 or not 0<=y<=10000000: raise ValueError('UTM zone/easting/northing outside range')
            if utm_convention=='hemisphere' and band not in 'NS': raise ValueError('hemisphere convention requires N or S')
            north=(band=='N') if utm_convention=='hemisphere' else band>='N'
            lat,lon,acc=_reproject(x,y,32600+z if north else 32700+z)
            if not -80.00001<=lat<=84.00001: raise ValueError('UTM outside its latitude domain')
            if utm_convention=='band':
                lo=-80+8*'CDEFGHJKLMNPQRSTUVWX'.index(band);hi=84 if band=='X' else lo+8
                if not lo-1e-4<=lat<=hi+1e-4: raise ValueError('UTM latitude inconsistent with band')
            r.latitude,r.longitude,r.operation_accuracy_m=lat,lon,acc
        elif f=='UPS':
            if source_crs is None: return Result('requires_metadata',f,reason='WGS84 datum declaration is required for UPS')
            if CRS(source_crs)!=CRS(4326): raise ValueError('UPS adapter requires WGS84')
            a=s.split();a=a[1:] if a[0]=='00' else a
            pole,x,y=a;lat,lon,acc=_reproject(float(x),float(y),32661 if pole=='N' else 32761)
            if (pole=='N' and lat<84-1e-5) or (pole=='S' and lat>-80+1e-5): raise ValueError('UPS outside polar domain')
            r.latitude,r.longitude,r.operation_accuracy_m=lat,lon,acc
        elif f in ('MGRS','USNG'):
            if source_crs is None: return Result('requires_metadata',f,reason='grid datum declaration required')
            if CRS(source_crs)!=CRS(4326): raise ValueError('MGRS/USNG adapter supports WGS84 only; NAD83 must not be assumed equivalent')
            import mgrs
            r.latitude,r.longitude=mgrs.MGRS().toLatLon(s.replace(' ',''))
            r.provenance['representative']='southwest cell corner returned by mgrs'
        elif f=='GEOHASH':
            import geohash2
            lat,lon,dy,dx=geohash2.decode_exactly(s)
            r.latitude,r.longitude=lat,lon;r.cell_bounds=(lat-dy,lon-dx,lat+dy,lon+dx)
        elif f=='PLUS_CODES':
            from openlocationcode import openlocationcode as olc
            if not olc.isFull(s): raise ValueError('short Plus Code requires a reference location')
            c=olc.decode(s);r.latitude,r.longitude=c.latitudeCenter,c.longitudeCenter
            r.cell_bounds=(c.latitudeLo,c.longitudeLo,c.latitudeHi,c.longitudeHi)
        elif f=='MAIDENHEAD':
            import maidenhead
            lat,lon=maidenhead.to_location(s,center=True);south,west=maidenhead.to_location(s,center=False)
            r.latitude,r.longitude=lat,lon;r.cell_bounds=(south,west,2*lat-south,2*lon-west)
        elif f in ('GARS','GEOREF'):
            from pygeodesy import gars,wgrs
            v=(gars.decode3(s) if f=='GARS' else wgrs.decode3(s))
            r.latitude,r.longitude=float(v.lat),float(v.lon)
            if f=='GARS': step={5:.5,6:.25,7:1/12}[len(s)]
            else: step=15 if len(s)==2 else 1 if len(s)==4 else (1/60)*10**(2-(len(s)-4)//2)
            r.cell_bounds=(r.latitude-step/2,r.longitude-step/2,r.latitude+step/2,r.longitude+step/2)
        else: raise ValueError('unsupported adapter')
        if not math.isfinite(r.latitude+r.longitude) or abs(r.latitude)>90 or abs(r.longitude)>180: raise ValueError('invalid decoded coordinates')
        if f in ('GEOHASH','PLUS_CODES','MAIDENHEAD','GARS','GEOREF'): r.source_crs='EPSG:4326'
        return r
    except Exception as e:
        return Result('invalid',f,source_crs=r.source_crs,reason=f'{type(e).__name__}: {e}',provenance=r.provenance)

def _angular(value,family,mode,positive,negative,precision):
    neg=math.copysign(1,value)<0;v=abs(value)
    if family=='DD': body=f'{v:.{precision}f}°'
    elif family=='DDM':
        ticks=round(v*60*10**precision);deg,ticks=divmod(ticks,60*10**precision)
        body=f"{deg}° {ticks/10**precision:.{precision}f}'"
    else:
        ticks=round(v*3600*10**precision);deg,ticks=divmod(ticks,3600*10**precision);mins,ticks=divmod(ticks,60*10**precision)
        body=f'''{deg}° {mins}' {ticks/10**precision:.{precision}f}"'''
    if mode==1: return ('-' if neg else '')+body
    return body+(' '+negative if neg else ' '+positive) if mode==2 else (negative if neg else positive)+' '+body

def encode(latitude,longitude,fmt,*,target_crs=None,precision=None):
    lat=float(latitude);lon=float(longitude);f=canonical(fmt)
    if not math.isfinite(lat+lon) or abs(lat)>90 or abs(lon)>180: raise ValueError('invalid WGS84 coordinate')
    if f not in FORMATS: raise ValueError('unsupported format')
    if f in ('GARS','GEOREF','MAIDENHEAD','GEOHASH','PLUS_CODES') and lon==180:
        lon=-180.  # equivalent meridian, required by half-open grid domains
    if f.startswith(('DD','DMS')):
        family=f[:-1];mode=int(f[-1]);p=precision if precision is not None else {'DD':8,'DDM':6,'DMS':4}[family]
        return _angular(lat,family,mode,'N','S',p)+' '+_angular(lon,family,mode,'E','W',p)
    if f.startswith(('PMS','PMB','PME')):
        if target_crs is None: raise ValueError('target CRS required for projected output')
        crs=CRS(target_crs)
        if not crs.is_projected: raise ValueError('target must be projected')
        if crs==CRS(3857) and abs(lat)>85.0511287798066: raise ValueError('outside Web Mercator map domain')
        x,y=transformer('EPSG:4326',str(target_crs)).transform(lon,lat,errcheck=True)
        u=UNIT_LIST[int(f[3:])-1];x*=crs.axis_info[0].unit_conversion_factor/UNITS[u];y*=crs.axis_info[1].unit_conversion_factor/UNITS[u]
        p=9 if precision is None else precision
        if f[:3]=='PMS': return f'{x:.{p}f}{u} {y:.{p}f}{u}'
        ex='E' if x>=0 else 'W';ny='N' if y>=0 else 'S'
        if f[:3]=='PMB': return f'{abs(x):.{p}f}{u} {ex} {abs(y):.{p}f}{u} {ny}'
        return f'{ex} {abs(x):.{p}f}{u} {ny} {abs(y):.{p}f}{u}'
    if f in ('UTM1','UTM2'):
        import utm
        if not -80<=lat<=84: raise ValueError('UTM valid only within [-80,84]')
        x,y,z,b=utm.from_latlon(lat,lon)
        # projection supplied by pyproj for stable numerical evaluation
        x,y=transformer('EPSG:4326',str(32600+z if lat>=0 else 32700+z)).transform(lon,lat,errcheck=True)
        return f'{z}{b} {x:.6f} {y:.6f}' if f=='UTM1' else f'{z}{b}{x:06.0f}{y:014.6f}'
    if f=='UPS':
        if -80<lat<84: raise ValueError('UPS requires polar latitude')
        x,y=transformer('EPSG:4326',str(32661 if lat>=0 else 32761)).transform(lon,lat,errcheck=True)
        return f"00 {'N' if lat>=0 else 'S'} {x:.6f} {y:.6f}"
    if f in ('MGRS','USNG'):
        import mgrs
        return mgrs.MGRS().toMGRS(lat,lon,MGRSPrecision=5 if precision is None else precision)
    if f=='GEOHASH':
        import geohash2
        return geohash2.encode(lat,lon,precision=12 if precision is None else precision)
    if f=='PLUS_CODES':
        from openlocationcode import openlocationcode as olc
        return olc.encode(lat,lon,10 if precision is None else precision)
    if f=='MAIDENHEAD':
        # Truncate into the containing cell; rounding may cross a cell boundary.
        p=3 if precision is None else precision
        if p not in (2,3,4): raise ValueError('Maidenhead precision must be 2, 3 or 4 pairs')
        radices=[18,10,24,10][:p]; total=math.prod(radices)
        ix=min(total-1,math.floor((lon+180)/360*total))
        iy=min(total-1,math.floor((lat+90)/180*total))
        pairs=[]
        for i in range(p-1,-1,-1):
            ix,x=divmod(ix,radices[i]);iy,y=divmod(iy,radices[i])
            base=ord('a') if i==2 else ord('A')
            pairs.append(str(x)+str(y) if i%2 else chr(base+x)+chr(base+y))
        return ''.join(reversed(pairs))
    from pygeodesy import gars,wgrs
    return gars.encode(lat,lon,precision=2 if precision is None else precision) if f=='GARS' else wgrs.encode(lat,lon,precision=6 if precision is None else precision)

def normalize_many(records:Iterable[dict]):
    """Streaming results. Input records contain text and explicit optional metadata."""
    for record in records:
        row=dict(record);text=row.pop('text');yield normalize(text,**row)
