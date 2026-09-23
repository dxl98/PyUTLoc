GeoNames inputs are external downloads from
<https://download.geonames.org/export/dump/> (CC BY 4.0). This folder
stores only the manifests documenting which files were used, their sizes
and SHA-256 checksums; `cities15000.txt` and the per-country dumps are
recreated by placing the extracted files under
`data/geonames/<region>/<country>/<CC>.txt` (see `benchmark_sources.csv`
for the exact layout). The gazetteer stage expects
`data/geonames/cities15000/cities15000.txt`.
