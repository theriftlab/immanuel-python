# Quickstart: Astrocartography Module

## Basic Usage

### Generate a Complete Astrocartography Chart

```python
from immanuel import charts
from immanuel.const import chart

# Create subject for birth data
subject = charts.Subject(
    date_time='1990-01-01 12:00:00',
    latitude='40.7128',  # New York
    longitude='-74.0060'
)

# Generate astrocartography chart
astro_chart = charts.AstrocartographyChart(subject)

# Access planetary lines
sun_lines = astro_chart.get_lines_for_planet(chart.SUN)
print(f"Sun MC Line: {len(sun_lines['MC'].coordinates)} coordinates")
print(f"Sun Zenith Point: {astro_chart.zenith_points[chart.SUN]}")

# Get all MC lines for comparison
mc_lines = astro_chart.get_lines_by_type('MC')
for planet_id, line in mc_lines.items():
    print(f"Planet {planet_id} MC line longitude: {line.coordinates[0][0]}")
```

### Analyze Specific Location

```python
# Check planetary influences at a specific location
location_influences = astro_chart.get_influences_at_location(
    longitude=-118.2437,  # Los Angeles
    latitude=34.0522
)

print("Active Lines:", location_influences['active_lines'])
print("Nearby Lines:", location_influences['nearby_lines'])
print("Zenith Distances:", location_influences['zenith_distances'])
```

### Customized Chart Configuration

```python
from immanuel.const import chart

# Create chart with specific configuration
custom_chart = charts.AstrocartographyChart(
    subject=subject,
    planets=[chart.SUN, chart.MOON, chart.VENUS, chart.MARS],
    line_types=['MC', 'IC'],  # Only vertical lines
    sampling_resolution=1.0,   # Lower resolution for faster calculation
    orb_influence_km=100.0,    # Smaller orb
    include_parans=True,       # Include paran calculations
    include_local_space=True   # Include local space lines
)

# Access advanced features
parans = custom_chart.paran_lines
print(f"Found {len(parans)} paran lines")

local_space = custom_chart.local_space_lines
for planet_id, line in local_space.items():
    print(f"Planet {planet_id} azimuth: {line.azimuth_degrees}°")
```

### Travel Recommendations

```python
# Find locations with desired planetary influences
recommendations = astro_chart.calculate_travel_recommendations(
    target_influences=['Sun_MC', 'Venus_ASC'],
    max_distance_km=5000  # Within 5000km of birth location
)

for rec in recommendations[:5]:  # Top 5 recommendations
    print(f"Location: {rec['coordinates']}")
    print(f"Influences: {rec['active_influences']}")
    print(f"Distance: {rec['distance_km']}km")
    print("---")
```

### Export for Mapping

```python
# Export coordinates for use with mapping software
geojson_data = astro_chart.export_coordinates(
    format='geojson',
    include_orbs=True
)

# Save to file for use with mapping applications
import json
with open('astrocartography_map.geojson', 'w') as f:
    json.dump(geojson_data, f, indent=2)

# Also available in other formats
kml_data = astro_chart.export_coordinates(format='kml')
csv_data = astro_chart.export_coordinates(format='csv')
```

### JSON Serialization

```python
import json
from immanuel.classes.serialize import ToJSON

# Serialize entire chart to JSON
chart_json = json.dumps(astro_chart, cls=ToJSON, indent=2)

# Save for later use
with open('my_astrocartography.json', 'w') as f:
    f.write(chart_json)

# Human-readable representation
print(astro_chart)  # Shows summary of chart with line counts
```

## Advanced Features

### Aspect Lines (Relocation Astrology)

```python
from datetime import datetime

# Configure aspect lines for relocation analysis
aspect_config = {
    'aspects': [0, 60, 90, 120, 180],  # Conjunction, sextile, square, trine, opposition
    'relocated_date': datetime(2025, 6, 21),  # Summer solstice
    'orb_tolerance': 1.0
}

relocation_chart = charts.AstrocartographyChart(
    subject=subject,
    aspect_lines_config=aspect_config
)

# Analyze aspect lines
aspect_lines = relocation_chart.aspect_lines
for line in aspect_lines:
    print(f"{line.aspect_name} between natal {line.natal_planet_id} and relocated {line.relocated_planet_id}")
    print(f"Exact at {len(line.coordinates)} locations")
```

### Performance Monitoring

```python
import time

start_time = time.time()

# Generate high-resolution world map
high_res_chart = charts.AstrocartographyChart(
    subject=subject,
    sampling_resolution=0.25,  # Higher resolution
    planets=list(range(4000001, 4000011))  # All major planets
)

calculation_time = time.time() - start_time
print(f"Calculation completed in {calculation_time:.2f} seconds")

# Should be under 10 seconds per constitutional requirement
assert calculation_time < 10.0, "Performance requirement not met"
```

### Error Handling

```python
try:
    # Chart with extreme coordinates
    extreme_subject = charts.Subject(
        date_time='1990-01-01 12:00:00',
        latitude='89.5',   # Near North Pole
        longitude='0.0'
    )

    extreme_chart = charts.AstrocartographyChart(extreme_subject)

    # Check for interpolated values due to extreme latitude
    for planet_id, lines in extreme_chart.planetary_lines.items():
        for line_type, line in lines.items():
            if 'interpolated' in line.metadata:
                print(f"Warning: {line_type} line for planet {planet_id} uses interpolated values")

except Exception as e:
    print(f"Calculation error: {e}")
```

## Integration with Existing Charts

```python
# Use with existing natal chart
natal_chart = charts.Natal(subject)

# Create astrocartography analysis for the same subject
astro_chart = charts.AstrocartographyChart(subject)

# Compare planetary positions
for planet_id in [chart.SUN, chart.MOON, chart.MERCURY]:
    natal_planet = natal_chart.objects[planet_id]
    zenith_point = astro_chart.zenith_points[planet_id]

    print(f"Planet {planet_id}:")
    print(f"  Natal position: {natal_planet.sign_longitude.formatted}")
    print(f"  Zenith location: {zenith_point.latitude:.2f}°, {zenith_point.longitude:.2f}°")
```

## Validation and Testing

```python
# Validate chart calculation
def validate_astrocartography_chart(chart):
    """Basic validation of astrocartography chart completeness."""

    # Check that all requested planets have lines
    assert len(chart.planetary_lines) > 0, "No planetary lines calculated"

    # Check that all line types are present
    for planet_id, lines in chart.planetary_lines.items():
        assert 'MC' in lines, f"Missing MC line for planet {planet_id}"
        assert 'IC' in lines, f"Missing IC line for planet {planet_id}"

        # Verify coordinate validity
        for line_type, line in lines.items():
            assert len(line.coordinates) > 0, f"Empty coordinates for {line_type} line"
            for lon, lat in line.coordinates:
                assert -180 <= lon <= 180, f"Invalid longitude: {lon}"
                assert -90 <= lat <= 90, f"Invalid latitude: {lat}"

    # Check zenith points
    assert len(chart.zenith_points) > 0, "No zenith points calculated"

    print("Chart validation passed!")

# Run validation
validate_astrocartography_chart(astro_chart)
```

This quickstart guide demonstrates the core functionality of the astrocartography module and provides examples for common use cases, advanced features, and integration patterns.