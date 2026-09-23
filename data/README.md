# Data

Core raw inputs and provenance records used by the experiments in
`experiments/`. Derived per-record and statistical outputs are not stored
in this repository; they are regenerated into `outputs/` by the scripts.

| Item | Contents | Origin / licence |
|---|---|---|
| `archive/annotation_v3.py` | legacy annotation routine used as the parsing baseline | this project |
| `archive/all_geocoding_detailed_results_500.csv` | archived geocoding returns, 500 GeoNames city queries | collected benchmark snapshot; see `geonames/geocoding_source_manifest.json` |
| `archive/all_geocoding_detailed_results_openaddresses_500.csv` | archived geocoding returns, 500 OpenAddresses address queries (San Francisco, Hong Kong) | collected benchmark snapshot; OpenAddresses data are ODbL |
| `archive/api_robustness_summary_10_runs.csv` | archived repeated-run summaries per provider | collected benchmark snapshot |
| `archive/synthetic_heterogeneous_coordinates_1100_perfect.csv` | frozen legacy heterogeneous-coordinate corpus | this project |
| `osm/osm_holdout_points.csv` | 2,100 sampled OpenStreetMap point records (100 per regional extract) | sampled from Geofabrik-style regional shapefiles; OSM data are ODbL |
| `osm/osm_sources.csv`, `osm/osm_source_manifest.json`, `osm/osm_crs_audit.json` | source file inventory, sizes, SHA-256 checksums and CRS audit | this project |
| `geonames/gazetteer_source_manifest.json` | checksum of the GeoNames cities15000 dump | GeoNames data are CC BY 4.0 |
| `geonames/benchmark_sources.csv` | per-country dump inventory for the scale benchmark | GeoNames CC BY 4.0 |
| `geonames/geocoding_source_manifest.json` | checksums of the archived provider CSVs | this project |
| `environment.json` | evaluated environment, dependency versions and benchmark settings | this project |

External downloads (not redistributed):

- GeoNames `cities15000.zip` and per-country dumps:
  <https://download.geonames.org/export/dump/>
- OpenStreetMap regional shapefiles (`.shp.zip`, POI layer):
  <https://download.geosm.org/> (or the equivalent Geofabrik regional
  extracts); the manifests record the exact files, sizes and checksums
  that were used.

Check the licence and attribution conditions of each source before
redistributing anything derived from them.
