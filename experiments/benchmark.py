"""Measured CPU/wall time and RSS. No random replacement of measurements.

Each (mode,size,repetition) runs in a fresh child process. CSV input/output is
excluded from measured compute time. Loading input is included in absolute RSS.
Memory is sampled every 5 ms; short-lived peaks may be missed.
"""
from pathlib import Path
import argparse,sys,os,json,time,threading,subprocess,platform,csv,hashlib
import numpy as np
import pandas as pd
import psutil
from pyproj import Transformer,Geod
from pyutloc import normalize,detect,encode
P=argparse.ArgumentParser();P.add_argument('--root',required=True);P.add_argument('--worker');P.add_argument('--n',type=int);P.add_argument('--repeat',type=int,default=0);A=P.parse_args()
ROOT=Path(A.root);OUT=ROOT/'outputs';NP=OUT/'benchmark_points.npy'
def prepare():
    if NP.exists():return
    rng=np.random.default_rng(20260914);samples=[];inventory=[]
    for p in sorted((ROOT/'data/geonames').glob('*/*/*.txt')):
        if p.stem!=p.parent.name or p.name=='readme.txt':continue
        chunks=[];total=0
        for c in pd.read_csv(p,sep='\t',header=None,usecols=[0,4,5],chunksize=200000):
            a=c.to_numpy();a=a[np.isfinite(a[:,1])&np.isfinite(a[:,2])&(np.abs(a[:,1])<80)&(np.abs(a[:,2])<=180)];total+=len(a)
            chunks.append(a)
        d=np.concatenate(chunks);take=min(len(d),150000);d=d[rng.choice(len(d),take,replace=False)]
        samples.append(d[:,1:3]);inventory.append({'source':str(p.relative_to(ROOT)),'eligible_records':total,'sampled':take,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()})
    a=np.concatenate(samples);rng.shuffle(a)
    if len(a)<1000000:raise ValueError(f'Only {len(a)} source rows available, do not oversample silently')
    np.save(NP,a[:1000000]);pd.DataFrame(inventory).to_csv(OUT/'benchmark_sources.csv',index=False)
    print('Prepared one million source records',flush=True)
def worker():
    import importlib.util
    a=np.load(NP,mmap_mode='r')[:A.n];lat=np.asarray(a[:,0]);lon=np.asarray(a[:,1]);tr=Transformer.from_crs(4326,3857,always_xy=True)
    formats=['DD1','DD2','DD3','DMS2','GEOHASH','PMS1']
    records=[]
    if A.worker in ['mixed_normalize','legacy_detect','new_detect']:
        for i,(la,lo) in enumerate(a):
            f=formats[i%6];records.append((encode(la,lo,f,target_crs=3857),3857 if f=='PMS1' else 4326))
    if A.worker=='legacy_detect':
        spec=importlib.util.spec_from_file_location('legacy',ROOT/'data/archive/annotation_v3.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
    proc=psutil.Process();base=proc.memory_info().rss;peak=[base];stop=threading.Event()
    def poll():
        while not stop.wait(.005):peak[0]=max(peak[0],proc.memory_info().rss)
    t=threading.Thread(target=poll,daemon=True);t.start();start=time.perf_counter();cpu=time.process_time();good=0;checksum=0.
    if A.worker=='pyproj_vector':
        x,y=tr.transform(lon,lat,errcheck=True);good=int((np.isfinite(x)&np.isfinite(y)).sum());checksum=float(np.sum(x)+np.sum(y))
    elif A.worker=='pyproj_scalar':
        for la,lo in a:
            x,y=tr.transform(lo,la,errcheck=True);good+=math_isfinite(x+y);checksum+=x+y
    elif A.worker=='mixed_normalize':
        for text,crs in records:
            r=normalize(text,source_crs=crs,axis_order='latlon');good+=r.status=='ok'
            if r.status=='ok':checksum+=r.latitude+r.longitude
    elif A.worker=='legacy_detect':
        for text,crs in records:good+=m.get_coordinate_type(text)!='UNKNOWN'
    elif A.worker=='new_detect':
        for text,crs in records:good+=detect(text,source_crs=crs,axis_order='latlon').status=='ok'
    elapsed=time.perf_counter()-start;cput=time.process_time()-cpu;peak[0]=max(peak[0],proc.memory_info().rss);stop.set();t.join()
    row={'mode':A.worker,'n':A.n,'repeat':A.repeat,'elapsed_s':elapsed,'cpu_s':cput,'throughput_per_s':A.n/elapsed,'accepted':good,
          'accept_rate':good/A.n,'rss_baseline_mb':base/1024**2,'rss_peak_mb':peak[0]/1024**2,'rss_increment_mb':(peak[0]-base)/1024**2,'checksum':checksum}
    print(json.dumps(row))
def math_isfinite(x):return int(np.isfinite(x))
if A.worker:worker()
else:
    prepare();rows=[]
    env={'python':sys.version,'platform':platform.platform(),'cpu':platform.processor(),'logical_cores':psutil.cpu_count(),'ram_gb':psutil.virtual_memory().total/1024**3,'seed':20260914,
         'timing_excludes':'input generation, disk IO, package imports','rss_includes':'runtime and loaded inputs','memory_sampling_s':.005,'repeats':3}
    import importlib.metadata as im
    env['versions']={x:im.version(x) for x in ['numpy','pandas','pyproj','pygeodesy','mgrs','utm','openlocationcode','geohash2','maidenhead','psutil','scipy']}
    (OUT/'environment.json').write_text(json.dumps(env,indent=2),encoding='utf8')
    for mode in ['legacy_detect','new_detect','mixed_normalize','pyproj_scalar','pyproj_vector']:
        for n in [10000,100000,1000000]:
            for repeat in range(3):
                cmd=[sys.executable,__file__,'--root',str(ROOT),'--worker',mode,'--n',str(n),'--repeat',str(repeat)]
                p=subprocess.run(cmd,capture_output=True,text=True,encoding='utf8',check=True);row=json.loads(p.stdout.strip().splitlines()[-1]);rows.append(row)
                pd.DataFrame(rows).to_csv(OUT/'performance_runs.csv',index=False)
                print(mode,n,repeat,round(row['elapsed_s'],3),row['accepted'],flush=True)
    d=pd.DataFrame(rows);s=d.groupby(['mode','n']).agg(elapsed_mean_s=('elapsed_s','mean'),elapsed_sd_s=('elapsed_s','std'),throughput_mean=('throughput_per_s','mean'),rss_peak_mean_mb=('rss_peak_mb','mean'),rss_increment_mean_mb=('rss_increment_mb','mean'),accepted_mean=('accepted','mean')).reset_index()
    s['elapsed_ci_halfwidth_s']=4.3026527299*s.elapsed_sd_s/np.sqrt(3);s.to_csv(OUT/'performance_summary.csv',index=False)
