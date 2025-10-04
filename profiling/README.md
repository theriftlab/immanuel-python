# Profiling & Benchmarking

This directory contains performance testing, profiling, and validation scripts for the astrocartography module.

## Files

### Paran Calculation Tests
- **test_parans.py** - Comprehensive paran accuracy testing and Douglas-Peucker precision benchmarks
  - Tests exact geometric line intersection for parans
  - Benchmarks different simplification tolerances
  - Validates accuracy by casting charts at paran locations
  - Documents ecliptic latitude limitations (especially for Pluto)

### Aspect Calculation Tests
- **test_astrocartography_aspects.py** - Aspect line calculation validation and performance testing
  - Tests aspect line accuracy (sextile, square, trine)
  - Compares fast binary search vs slow methods
  - Full chart performance benchmarks
  - MC/IC and ASC/DESC aspect validation

- **test_asc_desc_aspects.py** - ASC/DESC aspect line testing
- **asc_desc_aspect_testbed.py** - ASC/DESC aspect calculation testbed
- **verify_aspect_coordinates.py** - Coordinate verification for aspect lines
- **simple_aspect_test.py** - Simple aspect calculation tests

## Key Findings

### Paran Accuracy
- **Median error: ~1.4°** for most parans (zodiacal method)
- **Pluto ASC/DESC errors: 30-55°** due to 16.7° ecliptic latitude
- Solution: In mundo calculations (see `docs/in_mundo_asc_desc_implementation.md`)

### Douglas-Peucker Optimization
- **Epsilon 0.5°-1.0°**: 95-120x speedup with identical results
- **Epsilon >10°**: Too imprecise, finds different parans

### Performance
- **MC/IC lines**: ~0.2ms each (simple longitude calculation)
- **ASC/DESC lines**: Fast ternary search
- **Aspect lines**: Binary search for MC/IC, ternary search for ASC/DESC

## Usage

```bash
# Run paran accuracy tests
python profiling/test_parans.py

# Run aspect validation tests
python profiling/test_astrocartography_aspects.py

# Run full performance benchmarks
python profiling/test_astrocartography_aspects.py --all
```

## Documentation

See main documentation for implementation details:
- `docs/in_mundo_asc_desc_implementation.md` - In mundo calculation plan
- `docs/PARAN_INVESTIGATION_SUMMARY.md` - Detailed accuracy investigation
- `astrocartography_description.md` - Ecliptic latitude limitations
