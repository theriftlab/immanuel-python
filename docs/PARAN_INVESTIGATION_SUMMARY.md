# Paran Accuracy Investigation Summary

## Investigation Date
2025-10-04

## Problem
During paran accuracy testing, we discovered extreme errors (up to 55°) when verifying that planets are actually at the expected angles (ASC/DESC/MC/IC) at paran intersection locations.

## Root Cause Analysis

### Finding: Pluto's High Ecliptic Latitude

**Planet Ecliptic Latitudes (Birth: 1984-01-03 18:36:00 UTC):**
```
Sun       :  -0.000°
Moon      :  -2.811°
Mercury   :   3.118°
Venus     :   2.092°
Mars      :   1.648°
Jupiter   :   0.319°
Saturn    :   2.281°
Uranus    :   0.055°
Neptune   :   1.162°
Pluto     :  16.725° ⚠️  (5-8x higher than other planets!)
```

### Why This Causes Errors

Traditional astrocartography ASC/DESC calculations use **zodiacal (ecliptic longitude) method**, which:

1. Uses only the planet's ecliptic longitude
2. Assumes planets lie on the ecliptic plane (0° ecliptic latitude)
3. Shows where the planet's **ecliptic longitude** rises/sets, not the planet itself

When Pluto has 16.7° ecliptic latitude:
- At a "Pluto ASC" zodiacal line, Pluto's ecliptic longitude is rising
- But Pluto itself is 16.7° above the ecliptic plane
- This creates a 30-55° angular discrepancy depending on latitude

## Error Distribution

### Top 10 Worst Errors (All Pluto ASC/DESC):
```
1.  55.21° - Pluto ASC  in Jupiter ASC × Pluto ASC   at (124.92°, -58.67°)
2.  55.21° - Pluto DESC in Jupiter DESC × Pluto DESC at (-55.08°, 58.67°)
3.  39.55° - Pluto ASC  in Uranus ASC × Pluto ASC    at (123.63°, -50.57°)
4.  39.36° - Pluto DESC in Uranus DESC × Pluto DESC  at (-56.39°, 50.45°)
5.  34.62° - Pluto DESC in Venus DESC × Pluto DESC   at (-56.91°, 47.15°)
6.  34.58° - Pluto ASC  in Venus ASC × Pluto ASC     at (123.08°, -47.12°)
7.  32.83° - Pluto ASC  in Pluto ASC × Chiron DESC   at (122.87°, -45.76°)
8.  32.80° - Pluto DESC in Pluto DESC × Chiron ASC   at (-57.14°, 45.73°)
9.  14.08° - Pluto ASC  in Saturn ASC × Pluto ASC    at (120.44°, -20.72°)
10. 14.08° - Pluto DESC in Saturn DESC × Pluto DESC  at (-59.56°, 20.72°)
```

### Overall Accuracy (Epsilon=0.5°, Target=0.01°):
```
Total checks: 128
Median error: 1.4°  (most parans are quite accurate!)
Max error: 55.2°    (Pluto outliers)
Pass rate: 3.1%     (with strict 0.01° target)
```

### Non-Pluto Accuracy:
- MC/IC lines: <1° error (excellent - uses RA/Dec, not affected by ecliptic latitude)
- Other planet ASC/DESC: Generally <10° error, often <1°

## Impact Assessment

### Severity by Planet

**Critical (>10° errors):**
- Pluto ASC/DESC: 30-55° errors

**Moderate (5-10° errors):**
- Moon ASC/DESC: 5-10° potential errors (varies with Moon's ecliptic latitude)

**Acceptable (<5° errors):**
- All other planets: 0-3° ecliptic latitude → <5° errors
- MC/IC lines (all planets): <1° error

## Solution: In Mundo Calculations

**In mundo (prime vertical) calculations** use Right Ascension and Declination instead of ecliptic coordinates, providing accurate rising/setting positions.

### Expected Improvements:
- Pluto ASC/DESC: 55° → <1° error
- Moon ASC/DESC: 10° → <1° error
- Other planets: Minimal change (already accurate)

## Documentation Updates

1. ✅ **astrocartography_description.md**: Added "Ecliptic Latitude Limitation" section
2. ✅ **astrocartography.py**: Added docstring warning in `calculate_ascendant_descendant_lines()`
3. ✅ **docs/in_mundo_asc_desc_implementation.md**: Created implementation plan (6-9 day estimate)

## Status

**Current State**: Documented limitation, zodiacal method remains default
**Next Steps**: Implement in mundo ASC/DESC calculations (see implementation plan)
**Backward Compatibility**: Zodiacal method will remain default; in mundo will be opt-in

## References

- Michael Erlewine's work on in mundo astrocartography
- Swiss Ephemeris azalt calculations
- Campanus house system (uses prime vertical)

## Other Discoveries

### Orb Tolerance Not Implemented
During investigation, we discovered that the `orb_tolerance` parameter in paran calculations was never actually implemented. The code only finds exact geometric line intersections. We removed this misleading parameter from the API.

**Changes**:
- Removed `orb_tolerance` from `calculate_all_parans_from_lines()`
- Removed `orb_tolerance` from `calculate_paran_line()`
- Removed `orb_tolerance` from internal intersection methods
- Updated documentation to clarify exact intersection behavior

### Sidereal Time Handling
Confirmed that datetime and sidereal time handling is correct. The Immanuel library properly calculates local sidereal time based on:
1. UTC birth time (JD)
2. Longitude of location

The accuracy issues were solely due to ecliptic latitude, not timing calculations.
