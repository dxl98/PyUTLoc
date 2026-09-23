"""Explicit service adapters with request pacing, bounded retries and provenance.

Cache use is opt-in and must be permitted by the selected provider. This module
does not claim to improve a provider's geocoding or resolve textual ambiguity.
"""
from dataclasses import dataclass, asdict
import time, math, hashlib, json
from datetime import datetime, timezone
from typing import Callable

class ServiceError(Exception):
    def __init__(self,message,*,retryable=False,retry_after=0):
        super().__init__(message);self.retryable=retryable;self.retry_after=retry_after

@dataclass
class GeocodeResult:
    status:str
    provider:str|None=None
    latitude:float|None=None
    longitude:float|None=None
    crs:str|None=None
    attempts:int=0
    cache_hit:bool=False
    retrieved_at:str|None=None
    reason:str=''
    trace:list|None=None
    def to_dict(self): return asdict(self)

class Geocoder:
    def __init__(self,providers:dict[str,Callable],*,min_intervals=None,max_retries=2,
                 cache=None,cache_ttl=86400,sleep=time.sleep,clock=time.monotonic):
        self.providers=dict(providers);self.min_intervals=min_intervals or {}
        self.max_retries=max_retries;self.cache=cache;self.cache_ttl=cache_ttl
        self.sleep=sleep;self.clock=clock;self.last={}
    def geocode(self,query,*,context=None):
        # Context is part of both the query and the cache identity.
        text=', '.join(str(x).strip() for x in [query,context] if x)
        key=hashlib.sha256(json.dumps([list(self.providers),text],ensure_ascii=False).encode()).hexdigest()
        now=self.clock()
        if self.cache is not None and key in self.cache:
            stamp,value=self.cache[key]
            if now-stamp<self.cache_ttl:
                return GeocodeResult(**{**value,'attempts':0,'cache_hit':True,'trace':[]})
        trace=[];attempts=0
        for name,provider in self.providers.items():
            for retry in range(self.max_retries+1):
                delay=self.min_intervals.get(name,0)-(self.clock()-self.last.get(name,float('-inf')))
                if delay>0:self.sleep(delay)
                self.last[name]=self.clock();attempts+=1
                try:
                    value=provider(text)
                    if value is None:
                        trace.append({'provider':name,'status':'no_match'});break
                    lat,lon,crs=value
                    if crs!='EPSG:4326':
                        trace.append({'provider':name,'status':'unsupported_crs','crs':crs});break
                    if not math.isfinite(lat+lon) or abs(lat)>90 or abs(lon)>180:raise ServiceError('invalid response coordinate')
                    trace.append({'provider':name,'status':'ok'})
                    r=GeocodeResult('ok',name,lat,lon,crs,attempts,False,
                        datetime.now(timezone.utc).isoformat(),trace=trace)
                    if self.cache is not None:self.cache[key]=(self.clock(),r.to_dict())
                    return r
                except ServiceError as e:
                    trace.append({'provider':name,'status':'retryable_error' if e.retryable else 'permanent_error'})
                    if not e.retryable or retry==self.max_retries:break
                    self.sleep(max(e.retry_after,2**retry))
                except (TimeoutError,ConnectionError):
                    trace.append({'provider':name,'status':'network_error'})
                    if retry==self.max_retries:break
                    self.sleep(2**retry)
                except (TypeError,ValueError):
                    trace.append({'provider':name,'status':'malformed_response'});break
        return GeocodeResult('failed',attempts=attempts,reason='no valid provider result',trace=trace)

def geopy_adapter(service, *, crs):
    """Wrap an explicitly configured geopy locator; caller declares WGS84 service."""
    def call(query):
        from geopy.exc import GeocoderTimedOut,GeocoderUnavailable,GeocoderQuotaExceeded,GeocoderServiceError
        try:
            v=service.geocode(query,exactly_one=True)
            return None if v is None else (float(v.latitude),float(v.longitude),crs)
        except (GeocoderTimedOut,GeocoderUnavailable,GeocoderQuotaExceeded) as e:
            raise ServiceError(type(e).__name__,retryable=True) from e
        except GeocoderServiceError as e:raise ServiceError(type(e).__name__) from e
    return call
