"""Compatibility facade for the original DD1 pivot class names.

New code should use typed normalize()/encode() results. Source/target CRS is
required where it cannot be determined by the explicitly declared code system.
"""
from .core import encode,normalize,canonical,FORMATS
class DD1toOthers:
    def __init__(self,lat,lon,*,target_crs=None):self.lat=float(lat);self.lon=float(lon);self.target_crs=target_crs
    def __str__(self):return f'{self.lat} {self.lon}'
    def __getattr__(self,name):
        if name.startswith('dd1_to_') and canonical(name[7:]) in FORMATS:
            return lambda:encode(self.lat,self.lon,canonical(name[7:]),target_crs=self.target_crs)
        raise AttributeError(name)
class OtherstoDD1:
    def __init__(self,lat,lon=None,*,source_crs=None,axis_order='latlon',utm_convention=None):
        self.text=str(lat)+(' '+str(lon) if lon is not None else '');self.kw=dict(source_crs=source_crs,axis_order=axis_order,utm_convention=utm_convention)
    def __getattr__(self,name):
        if name.endswith('_to_dd1') and canonical(name[:-7]) in FORMATS:
            def convert():
                r=normalize(self.text,format_hint=canonical(name[:-7]),**self.kw)
                if r.status!='ok':raise ValueError(r.reason)
                return f'{r.latitude:.8f} {r.longitude:.8f}'
            return convert
        raise AttributeError(name)
SpecialCoordsToDD1=OtherstoDD1
