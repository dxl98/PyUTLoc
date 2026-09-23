# PyUTLoc

Validated normalization of heterogeneous coordinate representations with
geocoding integration. PyUTLoc separates the *identification* of a
coordinate format from the *spatial assumptions* required to interpret it,
and connects the validated interpretation to a common WGS84 decimal-degree
record with explicit diagnostics.

- 55 supported notation and unit variants (nine angular, ten grid/encoded,
  36 projected-unit labels) behind one registry
- typed results with `ok` / `invalid` / `ambiguous` / `requires_metadata`
  statuses — no default coordinate for failed input
- optional geocoding adapter with bounded retries, pacing, fallback and
  opt-in caching
- CLI, streaming iterator and a local browser GUI

## Install

Requires Python 3.10 or later.

```powershell
python -m pip install PyUTLoc==2.0.0rc1
```

Or from this source directory:

```powershell
python -m pip install .
python -m pip install ".[geocoding,test]"
```

`requirements-evaluated.txt` records the versions used in the evaluated
environment (Windows 11 / Python 3.12.14). The broader constraints in
`pyproject.toml` are not a claim that every combination was tested.

## Normalize a coordinate

```python
from pyutloc import normalize, encode, detect, normalize_many

r = normalize('N 39°54′0″ E 116°24′0″', source_crs='EPSG:4326')
assert r.status == 'ok'
assert abs(r.latitude - 39.9) < 1e-10
assert abs(r.longitude - 116.4) < 1e-10
print(r.to_dict())

# A signed pair needs both a known CRS and an axis convention.
r = normalize('39.9 116.4', source_crs='EPSG:4326', axis_order='latlon')

# Units do not identify a projection.
r = normalize('111319.49079327357m 0m', source_crs='EPSG:3857')
assert abs(r.longitude - 1) < 1e-10

print(detect('20 30').status)  # ambiguous
print(normalize('91 20', source_crs=4326, axis_order='latlon').status)  # invalid
print(encode(39.9, 116.4, 'DMS3'))
```

The result has named latitude/longitude fields in WGS84 plus status,
detected format, source CRS, reason, optional cell bounds, optional
operation accuracy and provenance. Handle `invalid`, `ambiguous` and
`requires_metadata` explicitly. Missing accuracy is `None`, not zero. No
failed conversion receives a default coordinate.

`normalize_many()` is an iterator over dictionaries with `text` and
per-record metadata. It does not need to load the full input list. The CLI
accepts a single coordinate or a CSV column and emits JSON/JSON Lines:

```powershell
pyutloc "39.9 116.4" --source-crs EPSG:4326 --axis-order latlon
pyutloc --input coordinates.csv --column coordinate --source-crs EPSG:4326 --axis-order latlon --output results.jsonl
python -m pyutloc.gui
```

The GUI listens on `http://127.0.0.1:8766`, processes up to 1,000 rows per
request, and uses no external map service.

## Interpretation rules

- The 55 legacy labels are **notation/unit variants**, not 55 CRSs: nine
  angular, ten special, and 36 projected-unit labels.
- Angular suffixes 1/2/3 mean signed values, trailing hemispheres and
  leading hemispheres. Signed-pair order must be `latlon` or `lonlat`.
- Projected plain pairs require `xy` or `yx`. Unit-bearing projected forms
  use easting then northing. `target_crs` is mandatory when encoding
  projected output.
- `format_hint` resolves known syntax ambiguity, especially MGRS/USNG and
  all-numeric Geohash. It does not infer an unknown datum or serve as a
  general forced-parser mode.
- UTM input requires `utm_convention='band'` or `'hemisphere'`; a letter
  N/S is not guessed. Encoded UTM/UPS currently require an explicit WGS84
  declaration.
- MGRS and USNG share possible syntax. Supply the format convention and
  `source_crs=4326`. A NAD83 USNG declaration is declined by this adapter;
  it is not silently treated as WGS84.
- Full Plus Codes are supported. Short codes need contextual recovery,
  which is outside this adapter.
- Geohash, Plus Codes, GARS, GEOREF and Maidenhead return cell-center
  representatives and cell bounds. MGRS/USNG use the library's
  southwest-corner representative. Coarse cells retain coarse spatial
  information.
- Exact length units include international foot, US survey foot and
  typographic point. Their definitions are distinct. Default projected
  encoding retains nine decimal places in the requested unit.
- `normalize()` always returns WGS84. `encode()` takes WGS84
  latitude/longitude and writes a requested supported representation.
  Neither operation recovers a missing coordinate epoch or unknown source
  datum.

## Optional geocoding

Configure a provider explicitly. The adapter contract is
`callable(query) -> (latitude, longitude, declared_crs)` or `None`. The
common wrapper currently accepts EPSG:4326 results. It does not resolve
textual aliases itself.

```python
from pyutloc.geocoding import Geocoder, geopy_adapter

# locator is a geopy service object configured by the caller with its
# endpoint, timeout and credentials. Do not put credentials in scripts.
def configured_client(locator):
    return Geocoder(
        {'selected_provider': geopy_adapter(locator, crs='EPSG:4326')},
        min_intervals={'selected_provider': 1.0},
        max_retries=2,
        cache=None,
    )
```

The interval above is an example, not universal permission to call a
service. Apply the actual endpoint's policy, quotas, retention rights and
fees. Caching is opt-in and has a TTL. Query context and provider order
participate in the cache identity. The client provides a trace, bounded
retries and fallback; it does not guarantee uptime or geocoding accuracy.
The bundled experiments make **no public geocoding calls**.

## Reproduce the experiments

From the repository root, with the dependencies installed:

```powershell
python -m pytest tests -q
python experiments/run_experiments.py --root .
python experiments/independent_checks.py --root .
python experiments/benchmark.py --root .
python experiments/registry_examples.py --root .
```

The root can be any directory preserving this layout:

```text
data/
  archive/     archived provider-result CSVs, the frozen legacy corpus,
               and annotation_v3.py (the legacy parsing baseline)
  osm/         sampled OSM holdout points and source manifests
  geonames/    source manifests for the GeoNames inputs
  environment.json   evaluated environment and dependency record
outputs/       derived results are written here
```

The first script supports `--stage geocoding`, `coordinate`,
`robustness`, `faults`, `gazetteer` or `downstream`. The coordinate and
downstream stages reuse the sampled points in
`data/osm/osm_holdout_points.csv`; the remaining OSM extracts and the
GeoNames dumps they were sampled from are external downloads (see
`data/README.md` for sources, checksums and licences) and are not
redistributed here. The scale benchmark takes several minutes and records
three fresh-process runs per condition.

`registry_examples.py` generates the 55 registry examples and validates
each using its recorded CRS, axis, and format arguments. It writes
`registry_examples.csv` and `registry_examples.json` to `outputs/`
without random sampling.

Evaluation boundaries:

- OSM positions are real data; the heterogeneous strings are generated
  test representations.
- 30,000 independent numerical cases use 10,000 source positions and
  three separate constructions, not 30,000 independent locations.
- Geocoding CSVs are archived snapshots without sufficient timestamps and
  raw responses for historical replay. They do not establish current
  service availability.
- The fault test uses a virtual clock; its waiting times are not measured
  network latency.
- The downstream fixture starts from known identical entities. It
  demonstrates ingestion and coordinate linkage, not improved general
  entity resolution or AI prediction.
- Absolute benchmark RSS includes runtime and preloaded data. CSV fields
  ending `_mb` contain MiB (bytes / 2^20).

See the accompanying manuscript and its Supplementary Materials for full
metrics, denominators and limitations. Source records retain their
GeoNames, OpenStreetMap and OpenAddresses attribution and licence
conditions; this repository does not redistribute their complete raw
archives.

## Compatibility and development

`pyutloc.annotation.get_coordinate_type`,
`pyutloc.transformation.DD1toOthers`, `OtherstoDD1` and
`SpecialCoordsToDD1` preserve familiar entry points. Their strict metadata
requirements are intentional; this is not a drop-in replacement for
undocumented CRS assumptions. The historical `USGN` spelling is accepted
as a USNG alias. New code should prefer the typed result API.

PyPI page: <https://pypi.org/project/PyUTLoc/>. See `CHANGELOG.md` and
`LICENSE`.
