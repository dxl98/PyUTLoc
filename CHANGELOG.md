# 2.0.0rc1 — validated normalization release candidate

- Retain the annotation/geocoding/transformation architecture and 55 historical labels.
- Introduce typed diagnostics, explicit CRS/axis metadata and known ambiguity handling.
- Correct exact length units, signed angular values near zero, rounding carries and grid boundaries.
- Cache compiled patterns, CRS objects and transformations; expose streaming input processing.
- Add configurable geocoding pacing, bounded retries, fallback and optional permitted caching.
- Add CLI, local GUI and compatibility facades.
- Supply regression tests, independent numerical constructions, controlled faults, archived-provider reanalysis and fresh-process performance scripts.
- Publish the release candidate to PyPI and this repository.

Behavior changes: invalid or unresolved input is no longer converted to a default coordinate. A source CRS cannot be inferred from unit symbols or a familiar string. Encoded-grid adapters have documented domain/datum requirements.
