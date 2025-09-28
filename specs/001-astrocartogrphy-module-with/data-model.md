# Data Model: Astrocartography Module

## Core Entities

### AstrocartographyChart
Represents complete astrocartography analysis for a birth chart.

**Fields**:
- `subject`: Subject - Birth chart subject (date, time, location)
- `planetary_lines`: Dict[int, Dict[str, PlanetaryLine]] - Lines by planet ID and line type
- `zenith_points`: Dict[int, ZenithPoint] - Zenith points by planet ID
- `paran_lines`: List[ParanLine] - Calculated paran latitude lines
- `local_space_lines`: Dict[int, LocalSpaceLine] - Local space lines by planet ID
- `aspect_lines`: List[AspectLine] - Optional aspect lines for relocation
- `calculation_metadata`: Dict - Sampling resolution, orb settings, etc.

**Relationships**:
- Extends existing chart architecture (similar to Natal, Transit charts)
- Contains multiple specialized line/point objects
- References original Subject for birth data

**Validation Rules**:
- Subject must have valid date, time, and coordinates
- Planetary lines must include MC, IC, ASC, DESC for each requested planet
- Zenith points must have exact latitude/longitude coordinates
- Calculation metadata must include sampling resolution and orb settings

### PlanetaryLine
Represents a single line type (MC/IC/ASC/DESC) for one planet.

**Fields**:
- `planet_id`: int - Planet identifier (matches Immanuel constants)
- `line_type`: str - Line type: 'MC', 'IC', 'ASC', 'DESC'
- `calculation_method`: str - 'zodiacal' or 'mundo'
- `coordinates`: List[Tuple[float, float]] - (longitude, latitude) pairs
- `sampling_resolution`: float - Degree interval used for sampling
- `orb_influence_km`: float - Orb of influence in kilometers
- `metadata`: Dict - Calculation details, timing, accuracy notes

**Relationships**:
- Belongs to AstrocartographyChart
- References planet via planet_id
- Contains geographic coordinate series

**Validation Rules**:
- Planet ID must be valid Immanuel planet constant
- Line type must be one of: MC, IC, ASC, DESC
- Coordinates must be valid longitude (-180 to 180) and latitude (-90 to 90)
- Sampling resolution must be positive float

### ZenithPoint
Represents exact geographical location where a planet was overhead.

**Fields**:
- `planet_id`: int - Planet identifier
- `latitude`: float - Exact latitude where planet was at zenith
- `longitude`: float - Exact longitude where planet was at zenith
- `calculation_method`: str - 'zodiacal' or 'mundo'
- `precision_estimate`: float - Estimated precision in arc-minutes
- `timestamp_jd`: float - Julian date of birth moment

**Relationships**:
- Belongs to AstrocartographyChart
- One per planet per chart

**Validation Rules**:
- Planet ID must be valid
- Latitude must be between -90 and 90 degrees
- Longitude must be between -180 and 180 degrees
- Precision estimate must be positive

### ParanLine
Represents latitude line where two planets are simultaneously angular.

**Fields**:
- `primary_planet_id`: int - First planet ID
- `secondary_planet_id`: int - Second planet ID
- `primary_angle`: str - Angular position of first planet (MC, IC, ASC, DESC)
- `secondary_angle`: str - Angular position of second planet
- `latitude_coordinates`: List[Tuple[float, float]] - (longitude, latitude) pairs along the paran line
- `orb_tolerance`: float - Orb used for paran calculation

**Relationships**:
- Belongs to AstrocartographyChart
- References two planets and their angular positions

**Validation Rules**:
- Planet IDs must be different and valid
- Angular positions must be valid (MC, IC, ASC, DESC)
- Orb tolerance must be positive
- Coordinates must form a continuous latitude line

### LocalSpaceLine
Represents directional line from birth location toward planetary position.

**Fields**:
- `planet_id`: int - Planet identifier
- `birth_location`: Tuple[float, float] - (longitude, latitude) of birth
- `azimuth_degrees`: float - Compass direction from birth location
- `endpoint_coordinates`: Tuple[float, float] - (longitude, latitude) where line intersects map boundary
- `distance_km`: float - Distance from birth to endpoint
- `planetary_altitude`: float - Planet's altitude at birth moment

**Relationships**:
- Belongs to AstrocartographyChart
- Radiates from birth location

**Validation Rules**:
- Planet ID must be valid
- Azimuth must be between 0 and 360 degrees
- Birth location and endpoint must have valid coordinates
- Distance must be positive

### AspectLine
Represents geographical line where specific aspect between natal and relocated planet positions is exact.

**Fields**:
- `natal_planet_id`: int - Natal planet identifier
- `relocated_planet_id`: int - Relocated (transiting) planet identifier
- `aspect_degrees`: float - Aspect angle (0, 60, 90, 120, 180, etc.)
- `aspect_name`: str - Human-readable aspect name
- `coordinates`: List[Tuple[float, float]] - (longitude, latitude) pairs where aspect is exact
- `orb_applied`: float - Orb used for aspect calculation
- `calculation_date`: datetime - Date for relocated planet position

**Relationships**:
- Belongs to AstrocartographyChart
- References two planets and specific aspect between them

**Validation Rules**:
- Planet IDs must be valid
- Aspect degrees must be positive and typically from standard set
- Coordinates must form continuous line
- Calculation date must be valid

## State Transitions

### AstrocartographyChart Lifecycle
1. **Initialization**: Created with Subject, empty line collections
2. **Calculation**: Populated with planetary lines, zenith points, optional features
3. **Serialization**: Converted to JSON for storage/transmission
4. **Modification**: Can be updated with additional planets or different settings

### Line Calculation States
1. **Pending**: Line calculation not yet started
2. **Processing**: Iterative calculation in progress
3. **Complete**: Successful calculation with coordinates
4. **Failed**: Calculation failed (extreme latitudes, etc.)
5. **Interpolated**: Failed calculation supplemented with interpolated values

## Data Volume Considerations

### Memory Usage
- World map with 0.5-degree resolution: ~720 longitude × 360 latitude = ~260k coordinate pairs
- 10 planets × 4 line types = 40 planetary lines per chart
- Estimated memory: ~10-50 MB per complete world astrocartography chart
- Configurable resolution allows memory/precision trade-offs

### Performance Scaling
- Line calculation complexity: O(resolution × planets × line_types)
- Parallel processing for independent lines reduces wall-clock time
- Caching opportunities for Greenwich Sidereal Time and common calculations
- Target: 10-second maximum for complete world map calculation

## Integration Points

### Existing Immanuel Architecture
- Inherits JSON serialization from existing ToJSON system
- Uses existing Subject class for birth data
- Integrates with existing planet constants and naming systems
- Follows existing chart class patterns for API consistency

### Extension Points
- Additional line types (geodetic, eclipse paths)
- Dynamic astrocartography with progressions/transits
- Synastry astrocartography between two charts
- Custom projection systems for specialized mapping needs