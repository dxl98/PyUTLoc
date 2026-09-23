"""Compatibility entry point; use detect() to retain ambiguity information."""
from .core import detect
def get_coordinate_type(coordinate,**metadata):
    result=detect(coordinate,**metadata)
    return result.candidates[0] if result.status=='ok' else result.status.upper()
