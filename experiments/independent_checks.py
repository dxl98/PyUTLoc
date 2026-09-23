"""Independent formulas and a second UTM implementation; no PyUTLoc encoder."""
from pathlib import Path
import argparse,math,json
import numpy as np,pandas as pd
import utm
from pyproj import Geod
from pyutloc import normalize
P=argparse.ArgumentParser();P.add_argument('--root',required=True);A=P.parse_args();O=Path(A.root)/'outputs';r=np.random.default_rng(20260915);G=Geod(ellps='WGS84');rows=[]
for i in range(10000):
    lat,lon=r.uniform(-79,83),r.uniform(-179.999,179.999)
    # Independent, conventional DMS expression with four fractional second digits.
    def dms(v,p,n):
        x=abs(v);deg=int(x);m=int((x-deg)*60);sec=((x-deg)*60-m)*60
        return f'''{deg}°{m}'{sec:.4f}"{p if v>=0 else n}'''
    x=6378137*math.radians(lon);y=6378137*math.log(math.tan(math.pi/4+math.radians(lat)/2))
    e,n,z,b=utm.from_latlon(lat,lon)
    cases=[('DMS_formula',dms(lat,'N','S')+' '+dms(lon,'E','W'),4326),('Mercator_formula',f'{x:.9f}m {y:.9f}m',3857),('UTM_independent_library',f'{z}{b} {e:.6f} {n:.6f}',4326)]
    for kind,text,crs in cases:
        v=normalize(text,source_crs=crs,axis_order='latlon',utm_convention='band')
        err=abs(G.inv(lon,lat,v.longitude,v.latitude)[2]) if v.status=='ok' else np.nan
        rows.append({'point_id':i,'kind':kind,'status':v.status,'error_m':err})
d=pd.DataFrame(rows);d.to_csv(O/'independent_details.csv',index=False)
s=d.groupby('kind').agg(n=('point_id','size'),successful=('error_m','count'),median_m=('error_m','median'),mean_m=('error_m','mean'),max_m=('error_m','max')).reset_index();s.to_csv(O/'independent_summary.csv',index=False);print(s.to_string(index=False))
