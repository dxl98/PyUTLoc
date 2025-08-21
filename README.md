# PyUTLoc
PyUTLoc is implemented as a modular Python package designed to address the challenges of heterogeneous spatial location transformation through a unified framework. The implementation follows a layered architecture that separates concerns into distinct functional modules while maintaining interoperability between components. 

1. PyPI Installation (Recommended)
Run the following command in the terminal to install the latest stable version:

  pip install Pyutloc==1.0

2. Basic Usage Example
To illustrate PyUTLoc’s workflow, we provide a minimal example of transforming a place name ("Addis Ababa") to a unified DD1 coordinate, then to UTM1 format:

# Step 1: Import core modules
from pyutloc.geocoding import arcgis_geocoding

from pyutloc.annotation import get_coordinate_type

from pyutloc.transformation import DD1toOthers

# Step 2: Geocode place name to DD1
placename = "Addis Ababa"

dd1_coords, crs = arcgis_geocoding(placename)   # Output: (9.01, 38.76), "WGS84"

# Step 3: Annotate coordinate type (verify DD1)
coord_str = f"{dd1_coords[0]} {dd1_coords[1]}"

coord_type = get_coordinate_type(coord_str)   # Output: "DD1"

# Step 4: Convert DD1 to UTM1
dd1_converter = DD1toOthers(dd1_coords[0], dd1_coords[1])

utm1_coords = dd1_converter.dd1_to_utm1()    # Output: "38N 401234 9987654"
