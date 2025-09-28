"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    Data structures for astrocartography calculations.
    These classes define the structure of astrocartography data including
    planetary lines, zenith points, parans, local space lines, and aspect lines.

"""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from immanuel.const import astrocartography


@dataclass
class PlanetaryLine:
    """Represents a single line type (MC/IC/ASC/DESC) for one planet."""

    # Core identification
    planet_id: int
    line_type: str  # 'MC', 'IC', 'ASC', 'DESC'
    calculation_method: str  # 'zodiacal' or 'mundo'

    # Geographic data
    coordinates: List[Tuple[float, float]]  # (longitude, latitude) pairs

    # Calculation parameters
    sampling_resolution: float  # Degree interval used for sampling
    orb_influence_km: float  # Orb of influence in kilometers

    # Metadata
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        """Validate fields after initialization."""
        if self.metadata is None:
            self.metadata = {}

        # Validate line type
        if self.line_type not in astrocartography.LINE_TYPES:
            raise ValueError(f"Invalid line_type: {self.line_type}. Must be one of {astrocartography.LINE_TYPES}")

        # Validate calculation method
        if self.calculation_method not in astrocartography.CALCULATION_METHODS:
            raise ValueError(f"Invalid calculation_method: {self.calculation_method}. Must be one of {astrocartography.CALCULATION_METHODS}")

        # Validate sampling resolution
        if not (astrocartography.MIN_SAMPLING_RESOLUTION <= self.sampling_resolution <= astrocartography.MAX_SAMPLING_RESOLUTION):
            raise ValueError(f"Sampling resolution {self.sampling_resolution} out of valid range {astrocartography.MIN_SAMPLING_RESOLUTION}-{astrocartography.MAX_SAMPLING_RESOLUTION}")

        # Validate orb influence
        if not (astrocartography.MIN_ORB_INFLUENCE_KM <= self.orb_influence_km <= astrocartography.MAX_ORB_INFLUENCE_KM):
            raise ValueError(f"Orb influence {self.orb_influence_km} out of valid range {astrocartography.MIN_ORB_INFLUENCE_KM}-{astrocartography.MAX_ORB_INFLUENCE_KM}")

        # Validate coordinates
        for longitude, latitude in self.coordinates:
            if not (astrocartography.MIN_LONGITUDE <= longitude <= astrocartography.MAX_LONGITUDE):
                raise ValueError(f"Invalid longitude: {longitude}")
            if not (astrocartography.MIN_LATITUDE <= latitude <= astrocartography.MAX_LATITUDE):
                raise ValueError(f"Invalid latitude: {latitude}")

    def __json__(self) -> Dict[str, Any]:
        """JSON serialization method for ToJSON encoder."""
        return {
            'planet_id': self.planet_id,
            'line_type': self.line_type,
            'calculation_method': self.calculation_method,
            'coordinates': self.coordinates,
            'sampling_resolution': self.sampling_resolution,
            'orb_influence_km': self.orb_influence_km,
            'metadata': self.metadata
        }

    def __str__(self) -> str:
        """Human-readable string representation."""
        coord_count = len(self.coordinates)
        return f"PlanetaryLine(planet_id={self.planet_id}, line_type={self.line_type}, coordinates={coord_count} points)"


@dataclass
class ZenithPoint:
    """Represents exact geographical location where a planet was overhead."""

    # Core identification
    planet_id: int

    # Geographic coordinates
    latitude: float  # Exact latitude where planet was at zenith
    longitude: float  # Exact longitude where planet was at zenith

    # Calculation details
    calculation_method: str  # 'zodiacal' or 'mundo'
    precision_estimate: float  # Estimated precision in arc-minutes
    timestamp_jd: float  # Julian date of birth moment

    # Metadata
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        """Validate fields after initialization."""
        if self.metadata is None:
            self.metadata = {}

        # Validate coordinates
        if not (astrocartography.MIN_LATITUDE <= self.latitude <= astrocartography.MAX_LATITUDE):
            raise ValueError(f"Invalid latitude: {self.latitude}")
        if not (astrocartography.MIN_LONGITUDE <= self.longitude <= astrocartography.MAX_LONGITUDE):
            raise ValueError(f"Invalid longitude: {self.longitude}")

        # Validate calculation method
        if self.calculation_method not in astrocartography.CALCULATION_METHODS:
            raise ValueError(f"Invalid calculation_method: {self.calculation_method}")

        # Validate precision estimate
        if self.precision_estimate <= 0:
            raise ValueError(f"Precision estimate must be positive: {self.precision_estimate}")

    def __json__(self) -> Dict[str, Any]:
        """JSON serialization method for ToJSON encoder."""
        return {
            'planet_id': self.planet_id,
            'latitude': round(self.latitude, astrocartography.COORDINATE_PRECISION),
            'longitude': round(self.longitude, astrocartography.COORDINATE_PRECISION),
            'calculation_method': self.calculation_method,
            'precision_estimate': round(self.precision_estimate, astrocartography.ANGLE_PRECISION),
            'timestamp_jd': round(self.timestamp_jd, astrocartography.TIME_PRECISION),
            'metadata': self.metadata
        }

    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"ZenithPoint(planet_id={self.planet_id}, lat={self.latitude:.3f}, lon={self.longitude:.3f})"


@dataclass
class ParanLine:
    """Represents latitude line where two planets are simultaneously angular."""

    # Planet identification
    primary_planet_id: int
    secondary_planet_id: int

    # Angular positions
    primary_angle: str  # 'MC', 'IC', 'ASC', 'DESC'
    secondary_angle: str  # 'MC', 'IC', 'ASC', 'DESC'

    # Geographic data
    latitude_coordinates: List[Tuple[float, float]]  # (longitude, latitude) pairs along the paran line

    # Calculation parameters
    orb_tolerance: float  # Orb used for paran calculation

    # Metadata
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        """Validate fields after initialization."""
        if self.metadata is None:
            self.metadata = {}

        # Validate planet IDs are different
        if self.primary_planet_id == self.secondary_planet_id:
            raise ValueError("Primary and secondary planet IDs must be different")

        # Validate angular positions
        for angle in [self.primary_angle, self.secondary_angle]:
            if angle not in astrocartography.LINE_TYPES:
                raise ValueError(f"Invalid angle: {angle}. Must be one of {astrocartography.LINE_TYPES}")

        # Validate orb tolerance
        if self.orb_tolerance <= 0:
            raise ValueError(f"Orb tolerance must be positive: {self.orb_tolerance}")

        # Validate coordinates
        for longitude, latitude in self.latitude_coordinates:
            if not (astrocartography.MIN_LONGITUDE <= longitude <= astrocartography.MAX_LONGITUDE):
                raise ValueError(f"Invalid longitude: {longitude}")
            if not (astrocartography.MIN_LATITUDE <= latitude <= astrocartography.MAX_LATITUDE):
                raise ValueError(f"Invalid latitude: {latitude}")

    def __json__(self) -> Dict[str, Any]:
        """JSON serialization method for ToJSON encoder."""
        return {
            'primary_planet_id': self.primary_planet_id,
            'secondary_planet_id': self.secondary_planet_id,
            'primary_angle': self.primary_angle,
            'secondary_angle': self.secondary_angle,
            'latitude_coordinates': self.latitude_coordinates,
            'orb_tolerance': self.orb_tolerance,
            'metadata': self.metadata
        }

    def __str__(self) -> str:
        """Human-readable string representation."""
        coord_count = len(self.latitude_coordinates)
        return f"ParanLine({self.primary_planet_id}_{self.primary_angle} + {self.secondary_planet_id}_{self.secondary_angle}, {coord_count} points)"


@dataclass
class LocalSpaceLine:
    """Represents directional line from birth location toward planetary position."""

    # Core identification
    planet_id: int

    # Geographic data
    birth_location: Tuple[float, float]  # (longitude, latitude) of birth
    endpoint_coordinates: Tuple[float, float]  # (longitude, latitude) where line intersects map boundary

    # Directional data
    azimuth_degrees: float  # Compass direction from birth location (0-360)
    distance_km: float  # Distance from birth to endpoint
    planetary_altitude: float  # Planet's altitude at birth moment in degrees

    # Metadata
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        """Validate fields after initialization."""
        if self.metadata is None:
            self.metadata = {}

        # Validate azimuth
        if not (0.0 <= self.azimuth_degrees < 360.0):
            raise ValueError(f"Azimuth must be between 0 and 360 degrees: {self.azimuth_degrees}")

        # Validate distance
        if self.distance_km <= 0:
            raise ValueError(f"Distance must be positive: {self.distance_km}")

        # Validate birth location coordinates
        birth_lon, birth_lat = self.birth_location
        if not (astrocartography.MIN_LONGITUDE <= birth_lon <= astrocartography.MAX_LONGITUDE):
            raise ValueError(f"Invalid birth longitude: {birth_lon}")
        if not (astrocartography.MIN_LATITUDE <= birth_lat <= astrocartography.MAX_LATITUDE):
            raise ValueError(f"Invalid birth latitude: {birth_lat}")

        # Validate endpoint coordinates
        end_lon, end_lat = self.endpoint_coordinates
        if not (astrocartography.MIN_LONGITUDE <= end_lon <= astrocartography.MAX_LONGITUDE):
            raise ValueError(f"Invalid endpoint longitude: {end_lon}")
        if not (astrocartography.MIN_LATITUDE <= end_lat <= astrocartography.MAX_LATITUDE):
            raise ValueError(f"Invalid endpoint latitude: {end_lat}")

        # Validate planetary altitude (can be negative for below horizon)
        if not (-90.0 <= self.planetary_altitude <= 90.0):
            raise ValueError(f"Planetary altitude must be between -90 and 90 degrees: {self.planetary_altitude}")

    def __json__(self) -> Dict[str, Any]:
        """JSON serialization method for ToJSON encoder."""
        return {
            'planet_id': self.planet_id,
            'birth_location': [round(coord, astrocartography.COORDINATE_PRECISION) for coord in self.birth_location],
            'endpoint_coordinates': [round(coord, astrocartography.COORDINATE_PRECISION) for coord in self.endpoint_coordinates],
            'azimuth_degrees': round(self.azimuth_degrees, astrocartography.ANGLE_PRECISION),
            'distance_km': round(self.distance_km, 2),
            'planetary_altitude': round(self.planetary_altitude, astrocartography.ANGLE_PRECISION),
            'metadata': self.metadata
        }

    def __str__(self) -> str:
        """Human-readable string representation."""
        return f"LocalSpaceLine(planet_id={self.planet_id}, azimuth={self.azimuth_degrees:.1f}°, distance={self.distance_km:.1f}km)"


@dataclass
class AspectLine:
    """Represents geographical line where specific aspect between natal and relocated planet positions is exact."""

    # Planet identification
    natal_planet_id: int
    relocated_planet_id: int

    # Aspect details
    aspect_degrees: float  # Aspect angle (0, 60, 90, 120, 180, etc.)
    aspect_name: str  # Human-readable aspect name
    orb_applied: float  # Orb used for aspect calculation

    # Time reference
    calculation_date: datetime  # Date for relocated planet position

    # Geographic data
    coordinates: List[Tuple[float, float]]  # (longitude, latitude) pairs where aspect is exact

    # Metadata
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        """Validate fields after initialization."""
        if self.metadata is None:
            self.metadata = {}

        # Validate aspect degrees
        if self.aspect_degrees < 0 or self.aspect_degrees >= 360:
            raise ValueError(f"Aspect degrees must be between 0 and 360: {self.aspect_degrees}")

        # Validate orb
        if self.orb_applied <= 0:
            raise ValueError(f"Orb must be positive: {self.orb_applied}")

        # Validate coordinates
        for longitude, latitude in self.coordinates:
            if not (astrocartography.MIN_LONGITUDE <= longitude <= astrocartography.MAX_LONGITUDE):
                raise ValueError(f"Invalid longitude: {longitude}")
            if not (astrocartography.MIN_LATITUDE <= latitude <= astrocartography.MAX_LATITUDE):
                raise ValueError(f"Invalid latitude: {latitude}")

        # Validate calculation date
        if not isinstance(self.calculation_date, datetime):
            raise ValueError("Calculation date must be a datetime object")

    def __json__(self) -> Dict[str, Any]:
        """JSON serialization method for ToJSON encoder."""
        return {
            'natal_planet_id': self.natal_planet_id,
            'relocated_planet_id': self.relocated_planet_id,
            'aspect_degrees': self.aspect_degrees,
            'aspect_name': self.aspect_name,
            'orb_applied': self.orb_applied,
            'calculation_date': self.calculation_date.isoformat(),
            'coordinates': self.coordinates,
            'metadata': self.metadata
        }

    def __str__(self) -> str:
        """Human-readable string representation."""
        coord_count = len(self.coordinates)
        return f"AspectLine({self.natal_planet_id} {self.aspect_name} {self.relocated_planet_id}, {coord_count} points)"