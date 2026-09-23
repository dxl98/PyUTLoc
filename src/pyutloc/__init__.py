"""PyUTLoc: explicit metadata, validated notation, reproducible normalization."""
from .core import Detection, Result, detect, normalize, encode, normalize_many, FORMATS, UNITS
__version__ = "2.0.0rc1"
__all__ = ["Detection", "Result", "detect", "normalize", "encode", "normalize_many", "FORMATS", "UNITS"]
