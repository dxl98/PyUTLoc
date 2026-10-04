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

PyPI page: <https://pypi.org/project/PyUTLoc/>. See `CHANGELOG.md` and `LICENSE`.
