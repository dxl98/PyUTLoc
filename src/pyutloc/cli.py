import argparse,csv,json,sys
from .core import normalize
def main():
    p=argparse.ArgumentParser(description='Normalize coordinates with explicit CRS and axis metadata')
    p.add_argument('text',nargs='?');p.add_argument('--source-crs');p.add_argument('--axis-order',choices=['latlon','lonlat','xy','yx'])
    p.add_argument('--format-hint');p.add_argument('--utm-convention',choices=['band','hemisphere'])
    p.add_argument('--input');p.add_argument('--output');p.add_argument('--column',default='coordinate')
    a=p.parse_args();kw={k:getattr(a,k) for k in ['source_crs','axis_order','format_hint','utm_convention']}
    if a.input:
        out=open(a.output,'w',encoding='utf8',newline='') if a.output else sys.stdout
        with open(a.input,encoding='utf-8-sig',newline='') as f:
            for row in csv.DictReader(f):out.write(json.dumps({'input':row[a.column],**normalize(row[a.column],**kw).to_dict()},ensure_ascii=False)+'\n')
        if a.output:out.close()
    elif a.text: print(json.dumps(normalize(a.text,**kw).to_dict(),ensure_ascii=False,indent=2))
    else:p.error('provide coordinate text or --input')
if __name__=='__main__':main()
