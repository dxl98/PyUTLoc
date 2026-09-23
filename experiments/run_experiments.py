"""Reproduce the revised experiments. Never contacts public geocoding services.

Run from any directory with --root pointing to the supplied project directory.
All reference coordinates retain their provenance. Derived format strings are
synthetic representations, not independently surveyed locations.
"""
from pathlib import Path
import argparse,sys,json,hashlib,platform,time,random,zipfile,struct,importlib.util,math,itertools
import numpy as np
import pandas as pd
from scipy.stats import binomtest,wilcoxon
from pyproj import Geod,Transformer,CRS
from pyutloc import normalize,detect,encode,FORMATS
from pyutloc.geocoding import Geocoder,ServiceError

P=argparse.ArgumentParser();P.add_argument('--root',required=True);P.add_argument('--stage',default='all');A=P.parse_args()
ROOT=Path(A.root);C=ROOT/'data/archive';OUT=ROOT/'outputs';OUT.mkdir(parents=True,exist_ok=True)
G=Geod(ellps='WGS84');RNG=np.random.default_rng(20260913)
def holdout():
    p=OUT/'osm_holdout_points.csv'
    return p if p.exists() else ROOT/'data/osm/osm_holdout_points.csv'
def save(rows,name):pd.DataFrame(rows).to_csv(OUT/(name+'.csv'),index=False,encoding='utf-8-sig')
def distance(lat,lon,lat2,lon2):return np.abs(G.inv(lon,lat,lon2,lat2)[2])
def wilson(k,n):
    if not n:return (np.nan,np.nan)
    z=1.95996398454;p=k/n;den=1+z*z/n
    c=(p+z*z/(2*n))/den;h=z*math.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
    return c-h,c+h
def bootstrap_median(x,reps=2000):
    if len(x)<2:return (np.nan,np.nan)
    r=np.random.default_rng(20260913);med=np.median(r.choice(x,(reps,len(x)),replace=True),axis=1)
    return np.quantile(med,[.025,.975])
def manifest(paths,name):
    rows=[]
    for p in paths:
        h=hashlib.sha256()
        with p.open('rb') as f:
            for chunk in iter(lambda:f.read(4*1024**2),b''):h.update(chunk)
        rows.append({'path':str(p.relative_to(ROOT)),'bytes':p.stat().st_size,'sha256':h.hexdigest()})
    (OUT/(name+'.json')).write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')

def geocoding():
    stats=[];details=[];pairs=[];regional=[];sensitivity=[];paths=[]
    for dataset,filename in [('Cities','all_geocoding_detailed_results_500.csv'),('Addresses','all_geocoding_detailed_results_openaddresses_500.csv')]:
        p=C/filename;paths.append(p);d=pd.read_csv(p);errors={};hit={};valids={}
        for col in d.columns:
            if not col.endswith('_lat'):continue
            provider=col[:-4];lat=d[col].to_numpy();lon=d[provider+'_lon'].to_numpy()
            valid=np.isfinite(lat)&np.isfinite(lon)&(np.abs(lat)<=90)&(np.abs(lon)<=180)
            err=np.full(len(d),np.nan);err[valid]=distance(d.latitude.to_numpy()[valid],d.longitude.to_numpy()[valid],lat[valid],lon[valid])
            n=int(valid.sum());lo,hi=wilson(n,len(d));v=err[valid];ci=bootstrap_median(v)
            rows={'dataset':dataset,'provider':provider,'n':len(d),'returned':n,'return_rate':n/len(d),'return_ci_low':lo,'return_ci_high':hi,
                  'mean_m':np.mean(v) if n else np.nan,'median_m':np.median(v) if n else np.nan,'median_ci_low':ci[0],'median_ci_high':ci[1],
                  'p90_m':np.quantile(v,.9) if n else np.nan,'rmse_m':np.sqrt(np.mean(v*v)) if n else np.nan,
                  'max_m':np.max(v) if n else np.nan,'zero_pair_count':int(((lat==0)&(lon==0)).sum())}
            for threshold in [20,100,1000,10000]:rows[f'yield_{threshold}m']=int((err<=threshold).sum())/len(d)
            stats.append(rows);errors[provider]=err;valids[provider]=valid;hit[provider]=err<=(1000 if dataset=='Cities' else 100)
            groups=d['country code'] if dataset=='Cities' else d.city_source
            for group in groups.unique():
                ix=(groups==group).to_numpy();vv=err[ix];good=np.isfinite(vv)
                regional.append({'dataset':dataset,'provider':provider,'group':group,'n':int(ix.sum()),'returned':int(good.sum()),'median_m':float(np.median(vv[good])) if good.any() else np.nan,
                                 'yield_within_threshold':float(np.mean(vv<=(1000 if dataset=='Cities' else 100)))})
            for i in range(len(d)):
                details.append({'dataset':dataset,'row_id':i,'provider':provider,'reference_lat':d.latitude[i],'reference_lon':d.longitude[i],
                    'returned_lat':lat[i],'returned_lon':lon[i],'valid_return':bool(valid[i]),'error_m':err[i]})
            # Unique queries sensitivity does not silently discard hard cases.
            keep=~d.query_string.duplicated();vv=err[keep]
            sensitivity.append({'dataset':dataset,'provider':provider,'n_unique_queries':int(keep.sum()),'return_rate':float(np.isfinite(vv).mean()),'median_m':float(np.nanmedian(vv)) if np.isfinite(vv).any() else np.nan})
        for a,b in itertools.combinations(errors,2):
            both=valids[a]&valids[b];ea=errors[a][both];eb=errors[b][both]
            n10=int((hit[a]&~hit[b]).sum());n01=int((~hit[a]&hit[b]).sum())
            p=binomtest(n10,n10+n01,.5).pvalue if n10+n01 else 1.
            wp=float(wilcoxon(ea-eb,zero_method='wilcox').pvalue) if len(ea)>1 and np.any(ea!=eb) else 1.
            pairs.append({'dataset':dataset,'a':a,'b':b,'paired_returns':int(both.sum()),'median_paired_difference_m':float(np.median(ea-eb)) if len(ea) else np.nan,
                          'mcnemar_p':p,'wilcoxon_p':wp,'a_only_within_threshold':n10,'b_only_within_threshold':n01})
    pairdf=pd.DataFrame(pairs)
    for ds,idx in pairdf.groupby('dataset').groups.items():
        for col in ['mcnemar_p','wilcoxon_p']:
            p=pairdf.loc[idx,col].to_numpy();order=np.argsort(p);adj=np.maximum.accumulate((len(p)-np.arange(len(p)))*p[order]);res=np.empty(len(p));res[order]=np.minimum(adj,1);pairdf.loc[idx,col+'_holm']=res
    save(stats,'geocoding_summary');save(details,'geocoding_recomputed');save(regional,'geocoding_regions');save(sensitivity,'geocoding_unique_query_sensitivity');save(pairdf,'geocoding_paired_tests');manifest(paths,'geocoding_source_manifest')
    # Archived repeated runs: pooled requests and run-level variability, no dates inferred.
    q=pd.read_csv(C/'api_robustness_summary_10_runs.csv')
    rows=[]
    for name,g in q.groupby('API_Name'):
        n=int(g.Total_Requests.sum());k=int(g.Success_Count.sum());lo,hi=wilson(k,n)
        rows.append({'provider':name,'runs':len(g),'requests':n,'success':k,'pooled_return_rate':k/n,'rate_ci_low':lo,'rate_ci_high':hi,
                     'minimum_run_rate':g['Success_Rate(%)'].min()/100,'maximum_run_rate':g['Success_Rate(%)'].max()/100,'mean_logged_latency_s':g['Avg_Response_Time(s)'].mean()})
    save(rows,'api_archived_runs');print('Geocoding reanalysis complete',flush=True)

def osm_points():
    rows=[];sources=[];r=random.Random(20260913)
    for p in sorted((ROOT/'data/osm').rglob('*.zip')):
        with zipfile.ZipFile(p) as z:
            names=[n for n in z.namelist() if n.endswith('gis_osm_pois_free_1.shp')]
            if not names:continue
            sample=[];count=0
            with z.open(names[0]) as f:
                f.read(100)
                while h:=f.read(8):
                    rec,n=struct.unpack('>ii',h);b=f.read(n*2)
                    if len(b)>=20 and struct.unpack('<i',b[:4])[0]==1:
                        lon,lat=struct.unpack('<dd',b[4:20]);count+=1
                        if not -90<=lat<=90 or not -180<=lon<=180:continue
                        item=(rec,lat,lon)
                        if len(sample)<100:sample.append(item)
                        else:
                            j=r.randrange(count)
                            if j<100:sample[j]=item
            source=str(p.relative_to(ROOT));sources.append({'source':source,'point_records':count,'sampled':len(sample),'shp_member':names[0]})
            for rec,lat,lon in sample:rows.append({'source':source,'record':rec,'lat':lat,'lon':lon})
    save(rows,'osm_holdout_points');save(sources,'osm_sources');print('OSM holdout points',len(rows),flush=True)
    return pd.DataFrame(rows)

def coordinate():
    spec=importlib.util.spec_from_file_location('legacy_annotation',C/'annotation_v3.py');legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy)
    p=holdout()
    if not p.exists():p=osm_points();p.to_csv(OUT/'osm_holdout_points.csv',index=False)
    # Test domain: OSM source points plus independent boundary controls.
    points=[(str(i),row.lat,row.lon,'OSM') for i,row in p.iterrows()]
    boundary=[(-.00001,-.00001),(-.999999999,179.999999),(.999999999,-179.999999),(89.999,10),(-89.999,-170),(84,0),(-80,0),(0,180),(0,-180),(60,6),(78,20)]
    for i,(lat,lon) in enumerate(boundary):points.append((f'E{i}',lat,lon,'boundary'))
    results=[]
    for i,lat,lon,source in points:
        for fmt in FORMATS:
            row={'point_id':i,'source':source,'format':fmt,'lat':lat,'lon':lon}
            try:text=encode(lat,lon,fmt,target_crs=3857)
            except Exception as e:row.update(status='outside_encoder_domain',reason=str(e));results.append(row);continue
            meta={'source_crs':3857 if fmt.startswith('PM') else 4326,'axis_order':'latlon','utm_convention':'band'}
            d=detect(text,source_crs=meta['source_crs'],axis_order='latlon')
            # MGRS/USNG shared syntax is counted as candidate-set correctness.
            hint=fmt if fmt in ('MGRS','USNG') else None
            v=normalize(text,format_hint=hint,**meta)
            old=legacy.get_coordinate_type(text);old={'USGN':'USNG','Geohash':'GEOHASH','Plus Codes':'PLUS_CODES','Maidenhead Grid':'MAIDENHEAD'}.get(old,old)
            row.update(text=text,status=v.status,predicted=';'.join(d.candidates),candidate_correct=fmt in d.candidates,legacy_label=old,
                legacy_correct=old==fmt or (old in ('USNG','MGRS') and fmt in ('USNG','MGRS')),reason=v.reason)
            if v.status=='ok':
                row['error_m']=float(distance(lat,lon,v.latitude,v.longitude))
                row['decoded_lat']=v.latitude;row['decoded_lon']=v.longitude
                if v.cell_bounds:
                    s,w,n,e=v.cell_bounds
                    row['cell_contains_source']=s-1e-10<=lat<=n+1e-10 and any(w-1e-10<=ll<=e+1e-10 for ll in (lon,lon-360,lon+360))
            results.append(row)
    save(results,'coordinate_holdout_details');d=pd.DataFrame(results);stats=[]
    for (source,fmt),g in d.groupby(['source','format']):
        a=g[g.status!='outside_encoder_domain'];v=a[a.status=='ok'];x=v.error_m.dropna()
        stats.append({'source':source,'format':fmt,'attempted':len(g),'domain_excluded':len(g)-len(a),'valid_inputs':len(a),'decoded':len(v),
            'candidate_accuracy':a.candidate_correct.mean(),'legacy_accuracy':a.legacy_correct.mean(),'mean_m':x.mean(),'median_m':x.median(),'p90_m':x.quantile(.9),'max_m':x.max(),
            'cell_containment':v.cell_contains_source.dropna().mean() if 'cell_contains_source' in v else np.nan})
    save(stats,'coordinate_holdout_summary')
    # Re-evaluate frozen legacy corpus, never regenerate it in place.
    d=pd.read_csv(C/'synthetic_heterogeneous_coordinates_1100_perfect.csv');rr=[]
    for col in d.columns[3:]:
        fmt='DD1' if col=='Format_00_DD1_String' else col.replace('dd1_to_','').upper();fmt='USNG' if fmt=='USGN' else fmt
        for i,s in enumerate(d[col]):
            if not isinstance(s,str) or s.startswith('Error:'):continue
            v=normalize(s,source_crs=3857 if fmt.startswith('PM') else 4326,axis_order='latlon',format_hint=fmt if fmt in ('MGRS','USNG') else None,utm_convention='band')
            rr.append({'point_id':i,'format':fmt,'status':v.status,'reason':v.reason,'error_m':float(distance(d.Original_lat_float[i],d.Original_lon_float[i],v.latitude,v.longitude)) if v.status=='ok' else np.nan})
    save(rr,'legacy_corpus_reanalysis');print('Coordinate evaluation complete',len(results),flush=True)

def robustness():
    spec=importlib.util.spec_from_file_location('legacy_annotation',C/'annotation_v3.py');legacy=importlib.util.module_from_spec(spec);spec.loader.exec_module(legacy)
    rows=[]
    # This generator is independent of pyutloc.encode and fixed before evaluation.
    r=np.random.default_rng(20260913)
    for i in range(2000):
        lat,lon=r.uniform(-79,79),r.uniform(-179,179)
        forms={'plain':f'{lat:.8f} {lon:.8f}','comma':f'{lat:.8f}, {lon:.8f}',
            'unicode':f'{abs(lat):.8f}° {"N" if lat>=0 else "S"}\u00a0{abs(lon):.8f}° {"E" if lon>=0 else "W"}',
            'lowercase':f'{"n" if lat>=0 else "s"}{abs(lat):.8f} {"e" if lon>=0 else "w"}{abs(lon):.8f}',
            'latitude_overflow':f'{91+abs(lat):.8f} {lon:.8f}',
            'minutes_overflow':f'10° {60+i%10}\' 20° 5\'',
            'hemisphere_conflict':f'-{abs(lat):.8f}N {abs(lon):.8f}E',
            'trailing_text':f'{lat:.8f} {lon:.8f} nonsense'}
        for kind,text in forms.items():
            valid=kind in ['plain','comma','unicode','lowercase'];v=normalize(text,source_crs=4326,axis_order='latlon');old=legacy.get_coordinate_type(text)
            rows.append({'id':i,'kind':kind,'expected_valid':valid,'status':v.status,'accepted':v.status=='ok','legacy_accepted':old!='UNKNOWN',
                'correct_policy':(v.status=='ok')==valid,'error_m':float(distance(lat,lon,v.latitude,v.longitude)) if v.status=='ok' and valid else np.nan})
    save(rows,'robustness_details');d=pd.DataFrame(rows);save(d.groupby('kind').agg(n=('id','size'),acceptance=('accepted','mean'),legacy_acceptance=('legacy_accepted','mean'),policy_accuracy=('correct_policy','mean'),max_error_m=('error_m','max')).reset_index(),'robustness_summary')
    print('Robustness evaluation complete',flush=True)

def faults():
    rows=[]
    for scenario in ['healthy','timeout_first','rate_limit_first','permanent_failure','malformed_response','all_unavailable']:
        for retries,cache_on,fallback in [(0,False,False),(2,False,True),(2,True,True)]:
            now=[0.];counts={};requests=[0]
            def first(q):
                requests[0]+=1;counts[q]=counts.get(q,0)+1
                if scenario=='timeout_first' and counts[q]==1:raise TimeoutError()
                if scenario=='rate_limit_first' and counts[q]==1:raise ServiceError('429',retryable=True,retry_after=3)
                if scenario in ['permanent_failure','all_unavailable']:raise ServiceError('unavailable')
                if scenario=='malformed_response':return (200.,400.,'EPSG:4326')
                return (10.,20.,'EPSG:4326')
            def second(q):
                requests[0]+=1
                if scenario=='all_unavailable':raise ServiceError('unavailable')
                return (10.,20.,'EPSG:4326')
            providers={'primary':first};providers.update({'fallback':second} if fallback else {})
            g=Geocoder(providers,max_retries=retries,cache={} if cache_on else None,min_intervals={'primary':1,'fallback':1},clock=lambda:now[0],sleep=lambda x:now.__setitem__(0,now[0]+x))
            results=[g.geocode(f'fixture {i%500}') for i in range(1000)]
            rows.append({'scenario':scenario,'retries':retries,'cache':cache_on,'fallback':fallback,'queries':len(results),'success':sum(v.status=='ok' for v in results),
                'requests':requests[0],'cache_hits':sum(v.cache_hit for v in results),'virtual_wait_seconds':now[0]})
    save(rows,'fault_injection');print('Controlled fault injection complete',flush=True)

def gazetteer():
    cols=['id','name','ascii','alternate','lat','lon','feature_class','feature_code','country','cc2','admin1','admin2','admin3','admin4','population','elevation','dem','timezone','modified']
    p=ROOT/'data/geonames/cities15000/cities15000.txt';d=pd.read_csv(p,sep='\t',names=cols,keep_default_na=False)
    d['key']=d.ascii.str.casefold();groups=d.groupby('key');rr=[]
    for key,g in groups:
        if len(g)<2:continue
        global_top=g.sort_values(['population','id'],ascending=[False,True]).iloc[0]
        for _,row in g.iterrows():
            c=g[g.country==row.country];top=c.sort_values(['population','id'],ascending=[False,True]).iloc[0]
            rr.append({'id':row.id,'name':row['name'],'country':row.country,'global_candidates':len(g),'country_candidates':len(c),
                'population_only_correct':global_top.id==row.id,'country_context_correct':top.id==row.id,'unique_after_country':len(c)==1})
    save(rr,'gazetteer_ambiguity');manifest([p],'gazetteer_source_manifest');print('Homonym context study',len(rr),flush=True)

def downstream():
    from scipy.spatial import cKDTree
    p=pd.read_csv(holdout());p=p.drop_duplicates(['lat','lon']).reset_index(drop=True)
    ref=np.deg2rad(p[['lat','lon']].to_numpy());xyz=np.c_[np.cos(ref[:,0])*np.cos(ref[:,1]),np.cos(ref[:,0])*np.sin(ref[:,1]),np.sin(ref[:,0])];tree=cKDTree(xyz)
    formats=['DD1','DD2','DD3','DMS2','UTM1','GEOHASH','PLUS_CODES','PMS1'];rows=[];triples=[]
    for i,row in p.iterrows():
        fmt=formats[i%len(formats)];text=encode(row.lat,row.lon,fmt,target_crs=3857)
        v=normalize(text,source_crs=3857 if fmt=='PMS1' else 4326,axis_order='latlon',utm_convention='band')
        # Numeric-only baseline accepts exactly two float fields and range-valid lat/lon.
        try:
            a,b=map(float,text.replace('°','').split());base=abs(a)<=90 and abs(b)<=180
        except:base=False
        recovered=False
        if v.status=='ok':
            a,b=np.deg2rad([v.latitude,v.longitude]);q=[np.cos(a)*np.cos(b),np.cos(a)*np.sin(b),np.sin(a)];_,j=tree.query(q)
            recovered=int(j)==i and distance(row.lat,row.lon,v.latitude,v.longitude)<=100
            triples.append(f'<urn:osm-record:{i}> <http://www.opengis.net/ont/geosparql#asWKT> "<http://www.opengis.net/def/crs/OGC/1.3/CRS84> POINT({v.longitude:.8f} {v.latitude:.8f})"^^<http://www.opengis.net/ont/geosparql#wktLiteral> .')
        rows.append({'id':i,'format':fmt,'baseline_ingested':base,'normalized':v.status=='ok','correct_nearest_link_within100m':recovered})
    save(rows,'downstream_linkage');(OUT/'normalized_spatial_literals.nt').write_text('\n'.join(triples),encoding='utf8')
    print('Downstream integration fixture complete',len(rows),flush=True)

if A.stage in ('all','geocoding'):geocoding()
if A.stage in ('all','coordinate'):coordinate()
if A.stage in ('all','robustness'):robustness()
if A.stage in ('all','faults'):faults()
if A.stage in ('all','gazetteer'):gazetteer()
if A.stage in ('all','downstream'):downstream()
