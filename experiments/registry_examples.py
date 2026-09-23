"""Generate and validate every example in Supplementary Table S1.

No random sampling or external geocoding is involved. Numerical experiment
results retain their original seeds and are unchanged by these examples.
"""
from pathlib import Path
import argparse,csv,json
from pyutloc import FORMATS,encode,normalize

def examples():
    rows=[]
    for fmt in FORMATS:
        lat,lon=(85.0,20.0) if fmt=='UPS' else (39.9,116.4)
        projected=fmt.startswith(('PMS','PMB','PME'))
        source_crs='EPSG:3857' if projected else 'EPSG:4326'
        text=encode(lat,lon,fmt,target_crs=source_crs if projected else None)
        kwargs={'source_crs':source_crs,'axis_order':'xy' if projected else 'latlon',
                'format_hint':fmt,'utm_convention':'band'}
        result=normalize(text,**kwargs)
        assert result.status=='ok',(fmt,text,result)
        required=source_crs
        if fmt in ['DD1','DDM1','DMS1']:required+='; latlon'
        if projected:required+='; xy' if fmt.startswith('PMS') else '; E/N axes'
        if fmt in ['MGRS','USNG']:required+='; '+fmt+' hint'
        if fmt in ['UTM1','UTM2']:required+='; latitude band'
        if fmt=='UPS':required+='; polar domain'
        rows.append({'label':fmt,'source_latitude':lat,'source_longitude':lon,'example':text,
                     'required_metadata':required,'normalization_arguments':kwargs,
                     'normalized_status':result.status,'decoded_latitude':result.latitude,
                     'decoded_longitude':result.longitude})
    assert len(rows)==55 and len({x['label'] for x in rows})==55
    return rows

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--root',type=Path,required=True);a=p.parse_args()
    out=a.root/'outputs';out.mkdir(parents=True,exist_ok=True);rows=examples()
    (out/'registry_examples.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
    with (out/'registry_examples.csv').open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.DictWriter(f,fieldnames=[k for k in rows[0] if k!='normalization_arguments']);w.writeheader()
        w.writerows({k:v for k,v in r.items() if k!='normalization_arguments'} for r in rows)
    print('Generated and decoded all 55 Supplementary Table S1 examples.')
