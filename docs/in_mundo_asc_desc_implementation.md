# In Mundo ASC/DESC Line Implementation Plan

## Problem Statement

Current zodiacal ASC/DESC line calculations use ecliptic longitude only, causing significant errors for planets with high ecliptic latitude:

- **Pluto**: 16.7° ecliptic latitude → 30-55° errors on ASC/DESC lines
- **Moon**: Up to 5° ecliptic latitude → 5-10° errors
- **Other planets**: 0-3° ecliptic latitude → <5° errors

At a "Pluto ASC" zodiacal line, Pluto's **ecliptic longitude** is rising, not Pluto itself.

## Solution: In Mundo (Prime Vertical) Calculations

In mundo calculations use **Right Ascension (RA)** and **Declination (Dec)** instead of ecliptic coordinates, providing accurate rising/setting positions that account for the planet's true 3D position.

## Implementation Approach

### Phase 1: Research & Design

1. **Study astronomical formulas** for in mundo calculations:
   - Rising/setting conditions using RA/Dec
   - Prime vertical crossing calculations
   - Altitude/azimuth to RA/Dec conversions

2. **Research existing implementations**:
   - Check if Swiss Ephemeris has built-in in mundo functions
   - Review astrology literature on in mundo vs. zodiacal methods
   - Study Solar Fire or other professional software approaches

3. **Design API**:
   ```python
   # Proposed API
   calculator = AstrocartographyCalculator(
       julian_date=jd,
       calculation_method='in_mundo'  # or 'zodiacal' (default)
   )

   # Or separate methods
   asc_desc_lines_zodiacal = calculator.calculate_ascendant_descendant_lines(
       planet_id=chart.PLUTO,
       method='zodiacal'
   )

   asc_desc_lines_mundo = calculator.calculate_ascendant_descendant_lines(
       planet_id=chart.PLUTO,
       method='in_mundo'
   )
   ```

### Phase 2: Core Algorithm Implementation

#### In Mundo ASC Line Calculation

For a planet to be rising (on the Ascendant) in mundo:

1. **Planet must cross the eastern horizon**
   - Altitude = 0°
   - Azimuth ≈ 90° (east)

2. **Calculate for each longitude**:
   ```python
   def calculate_in_mundo_asc_line(planet_ra, planet_dec, longitude_range):
       """
       Calculate in mundo ASC line using RA/Dec.

       For each longitude:
       1. Calculate Local Sidereal Time (LST)
       2. Calculate Hour Angle (HA) = LST - RA
       3. Solve for latitude where planet is on horizon:
          sin(altitude) = sin(lat) * sin(dec) + cos(lat) * cos(dec) * cos(HA)
          For rising: altitude = 0
          0 = sin(lat) * sin(dec) + cos(lat) * cos(dec) * cos(HA)
          tan(lat) = -cos(dec) * cos(HA) / sin(dec)
       """
   ```

3. **Handle edge cases**:
   - Circumpolar planets (never rise/set at extreme latitudes)
   - Planets near celestial poles

#### In Mundo DESC Line Calculation

Similar to ASC but for setting (western horizon):
- Altitude = 0°
- Azimuth ≈ 270° (west)
- Hour Angle = RA - LST + 180°

### Phase 3: Integration

1. **Add method parameter** to existing functions:
   ```python
   def calculate_ascendant_descendant_lines(
       self,
       planet_id: int,
       latitude_range: Tuple[float, float] = (-60, 60),
       method: str = 'zodiacal'  # 'zodiacal' or 'in_mundo'
   ) -> Tuple[List[Tuple[float, float]], List[Tuple[float, float]]]:
   ```

2. **Update line generation** to support both methods:
   - Keep zodiacal as default (backward compatibility)
   - Add in_mundo as opt-in for accuracy

3. **Update paran calculations** to handle mixed methods:
   - Allow parans between zodiacal and in mundo lines
   - Document differences in paran meanings

### Phase 4: Testing & Validation

1. **Create test cases**:
   - Pluto ASC/DESC lines (biggest difference)
   - Moon ASC/DESC lines (moderate difference)
   - Sun ASC/DESC lines (minimal difference, should match zodiacal)

2. **Accuracy verification**:
   - Cast charts at in mundo line locations
   - Verify planet is actually rising/setting (altitude ≈ 0°)
   - Compare with zodiacal line locations

3. **Performance testing**:
   - Benchmark in mundo vs. zodiacal calculation speed
   - Optimize if needed

### Phase 5: Documentation

1. **Update API documentation**:
   - Explain zodiacal vs. in mundo differences
   - Provide usage examples
   - Document when to use each method

2. **Add visual comparisons**:
   - Generate maps showing zodiacal vs. in mundo lines
   - Highlight Pluto line differences

3. **Update astrocartography_description.md**:
   - Add detailed in mundo explanation
   - Include mathematical formulas
   - Reference implementation

## Expected Results

### Accuracy Improvements

**Pluto ASC/DESC Lines**:
- Zodiacal method: 30-55° errors
- In mundo method: <1° errors (expected)

**Moon ASC/DESC Lines**:
- Zodiacal method: 5-10° errors
- In mundo method: <1° errors (expected)

**Other Planets**:
- Both methods should be similar (<5° difference)

### Performance Impact

- In mundo calculations may be slightly slower due to:
  - Trigonometric calculations for horizon crossings
  - Iterative solving for latitude
- Expected: 10-30% slower than zodiacal method
- Still fast enough for real-time use

## Implementation Phases

### Phase 1: Foundation (1-2 days)
- Research formulas
- Design API
- Create test framework

### Phase 2: Core Implementation (2-3 days)
- Implement in mundo ASC calculation
- Implement in mundo DESC calculation
- Handle edge cases

### Phase 3: Integration (1 day)
- Add method parameter
- Update line generation
- Ensure backward compatibility

### Phase 4: Testing (1-2 days)
- Create test cases
- Verify accuracy
- Performance testing

### Phase 5: Documentation (1 day)
- Update docs
- Create examples
- Generate comparison visualizations

**Total estimated time**: 6-9 days

## References

- Campanus system (prime vertical house system)
- Regiomontanus calculations
- Swiss Ephemeris documentation on azalt calculations
- Michael Erlewine's work on in mundo astrocartography

## Open Questions

1. Should in mundo be the default for Pluto/Moon?
2. How to handle parans between zodiacal and in mundo lines?
3. Should we support other house systems (Campanus, Regiomontanus) for ASC/DESC?
4. Performance optimization strategies if calculations are too slow?
