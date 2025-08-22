# PyUTLoc Usage Guide

## 1. PyPI Installation

Run the following command in your terminal to install the latest stable version:

```bash
pip install PyUTLoc
```

## 2. Basic Usage Example

The following example demonstrates how to use PyUTLoc to transform a place name ("Addis Ababa") into a unified DD1 coordinate, and then convert it to UTM1 format:

### Step 1: Import Core Modules

```python
from pyutloc.geocoding import arcgis_geocoding
from pyutloc.annotation import get_coordinate_type
from pyutloc.transformation import DD1toOthers
```

### Step 2: Geocode Place Name to DD1 Coordinates

```python
placename = "Addis Ababa"
dd1_coords, crs = arcgis_geocoding(placename)  # Output: (9.01, 38.76), "WGS84"
```

### Step 3: Annotate Coordinate Type (Verify DD1)

```python
coord_str = f"{dd1_coords[0]} {dd1_coords[1]}"
coord_type = get_coordinate_type(coord_str)  # Output: "DD1"
```

### Step 4: Convert DD1 to UTM1

```python
dd1_converter = DD1toOthers(dd1_coords[0], dd1_coords[1])
utm1_coords = dd1_converter.dd1_to_utm1()  # Output: "38N 401234 9987654"
```
