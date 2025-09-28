"""
Astrocartography constants for line calculations and configuration.

This module provides constants for astrocartography calculations including
sampling resolution, orb distances, line types, and calculation methods.
"""

# Line types
LINE_MC = 'MC'
LINE_IC = 'IC'
LINE_ASCENDANT = 'ASC'
LINE_DESCENDANT = 'DESC'

LINE_TYPES = [LINE_MC, LINE_IC, LINE_ASCENDANT, LINE_DESCENDANT]

# Calculation methods
METHOD_ZODIACAL = 'zodiacal'
METHOD_MUNDO = 'mundo'

CALCULATION_METHODS = [METHOD_ZODIACAL, METHOD_MUNDO]

# Compatibility aliases
CALCULATION_METHOD_ZODIACAL = METHOD_ZODIACAL
CALCULATION_METHOD_MUNDO = METHOD_MUNDO

# Default configuration values
DEFAULT_SAMPLING_RESOLUTION = 0.5  # degrees
DEFAULT_ORB_INFLUENCE_KM = 150.0    # kilometers
DEFAULT_CALCULATION_METHOD = METHOD_ZODIACAL

# Performance targets
MAX_WORLD_MAP_CALCULATION_TIME = 10.0  # seconds

# Sampling configuration
MIN_SAMPLING_RESOLUTION = 0.1   # degrees (finest detail)
MAX_SAMPLING_RESOLUTION = 5.0   # degrees (coarsest detail)

# Orb configuration
MIN_ORB_INFLUENCE_KM = 50.0     # kilometers
MAX_ORB_INFLUENCE_KM = 500.0    # kilometers

# Geographic constraints
MIN_LATITUDE = -90.0    # degrees
MAX_LATITUDE = 90.0     # degrees
MIN_LONGITUDE = -180.0  # degrees
MAX_LONGITUDE = 180.0   # degrees

# Extreme latitude thresholds for interpolation
EXTREME_LATITUDE_THRESHOLD = 80.0  # degrees (above/below this requires interpolation)
INTERPOLATION_THRESHOLD = 85.0     # degrees (above/below this always requires interpolation)

# Advanced feature types
FEATURE_PARANS = 'parans'
FEATURE_LOCAL_SPACE = 'local_space'
FEATURE_ASPECT_LINES = 'aspect_lines'

ADVANCED_FEATURES = [FEATURE_PARANS, FEATURE_LOCAL_SPACE, FEATURE_ASPECT_LINES]

# Aspect types for aspect lines (configurable set)
ASPECT_CONJUNCTION = 0
ASPECT_SEXTILE = 60
ASPECT_SQUARE = 90
ASPECT_TRINE = 120
ASPECT_OPPOSITION = 180

# Minor aspects
ASPECT_SEMI_SEXTILE = 30
ASPECT_SEMI_SQUARE = 45
ASPECT_SESQUARE = 135
ASPECT_QUINCUNX = 150

MAJOR_ASPECTS = [ASPECT_CONJUNCTION, ASPECT_SEXTILE, ASPECT_SQUARE, ASPECT_TRINE, ASPECT_OPPOSITION]
MINOR_ASPECTS = [ASPECT_SEMI_SEXTILE, ASPECT_SEMI_SQUARE, ASPECT_SESQUARE, ASPECT_QUINCUNX]
ALL_ASPECTS = MAJOR_ASPECTS + MINOR_ASPECTS

# Export formats
EXPORT_GEOJSON = 'geojson'
EXPORT_KML = 'kml'
EXPORT_CSV = 'csv'

EXPORT_FORMATS = [EXPORT_GEOJSON, EXPORT_KML, EXPORT_CSV]

# Calculation precision
COORDINATE_PRECISION = 6  # decimal places for lat/lon coordinates
ANGLE_PRECISION = 4       # decimal places for astronomical angles
TIME_PRECISION = 2        # decimal places for time calculations

# Error handling
ERROR_CALCULATION_FAILED = 'calculation_failed'
ERROR_EXTREME_LATITUDE = 'extreme_latitude'
ERROR_INVALID_PLANET = 'invalid_planet'
ERROR_INVALID_COORDINATES = 'invalid_coordinates'
ERROR_PERFORMANCE_EXCEEDED = 'performance_exceeded'

ERROR_TYPES = [
    ERROR_CALCULATION_FAILED,
    ERROR_EXTREME_LATITUDE,
    ERROR_INVALID_PLANET,
    ERROR_INVALID_COORDINATES,
    ERROR_PERFORMANCE_EXCEEDED
]