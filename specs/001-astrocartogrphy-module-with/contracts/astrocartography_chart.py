"""
Contract: AstrocartographyChart Class API

This contract defines the public interface for the AstrocartographyChart class
that extends the existing Immanuel chart system.
"""

from typing import Dict, List, Optional, Tuple, Union
from datetime import datetime
from immanuel.charts import Subject


class AstrocartographyChart:
    """
    Astrocartography chart providing planetary line calculations and zenith points.

    Extends existing Immanuel chart architecture to provide geographical
    planetary influence mapping.
    """

    def __init__(
        self,
        subject: Subject,
        planets: Optional[List[int]] = None,
        line_types: Optional[List[str]] = None,
        calculation_method: str = 'zodiacal',
        sampling_resolution: float = 0.5,
        orb_influence_km: float = 150.0,
        include_parans: bool = False,
        include_local_space: bool = False,
        aspect_lines_config: Optional[Dict] = None
    ):
        """
        Initialize astrocartography chart for given subject.

        Args:
            subject: Birth chart subject (date, time, location)
            planets: List of planet IDs to calculate (default: all major planets)
            line_types: List of line types ['MC', 'IC', 'ASC', 'DESC'] (default: all)
            calculation_method: 'zodiacal' or 'mundo' calculation approach
            sampling_resolution: Degree interval for line sampling (default: 0.5)
            orb_influence_km: Orb of influence in kilometers (default: 150)
            include_parans: Whether to calculate paran lines
            include_local_space: Whether to calculate local space lines
            aspect_lines_config: Configuration for aspect lines (optional)

        Raises:
            ValueError: If subject data is invalid or parameters out of range
            CalculationError: If initial astronomical calculations fail
        """
        pass

    @property
    def planetary_lines(self) -> Dict[int, Dict[str, 'PlanetaryLine']]:
        """
        Get all planetary lines organized by planet ID and line type.

        Returns:
            Dictionary mapping planet_id -> {line_type: PlanetaryLine}
            Example: {chart.SUN: {'MC': PlanetaryLine(...), 'IC': PlanetaryLine(...)}}
        """
        pass

    @property
    def zenith_points(self) -> Dict[int, 'ZenithPoint']:
        """
        Get zenith points for all calculated planets.

        Returns:
            Dictionary mapping planet_id -> ZenithPoint
        """
        pass

    @property
    def paran_lines(self) -> List['ParanLine']:
        """
        Get calculated paran lines (if enabled).

        Returns:
            List of ParanLine objects showing simultaneous planetary angularity
        """
        pass

    @property
    def local_space_lines(self) -> Dict[int, 'LocalSpaceLine']:
        """
        Get local space lines (if enabled).

        Returns:
            Dictionary mapping planet_id -> LocalSpaceLine
        """
        pass

    @property
    def aspect_lines(self) -> List['AspectLine']:
        """
        Get aspect lines (if configured).

        Returns:
            List of AspectLine objects for relocation aspects
        """
        pass

    def get_lines_for_planet(self, planet_id: int) -> Dict[str, 'PlanetaryLine']:
        """
        Get all line types for a specific planet.

        Args:
            planet_id: Planet identifier constant

        Returns:
            Dictionary mapping line_type -> PlanetaryLine

        Raises:
            KeyError: If planet not calculated for this chart
        """
        pass

    def get_lines_by_type(self, line_type: str) -> Dict[int, 'PlanetaryLine']:
        """
        Get lines of specific type for all planets.

        Args:
            line_type: Line type ('MC', 'IC', 'ASC', 'DESC')

        Returns:
            Dictionary mapping planet_id -> PlanetaryLine

        Raises:
            ValueError: If line_type is invalid
        """
        pass

    def get_influences_at_location(
        self,
        longitude: float,
        latitude: float
    ) -> Dict[str, List[Dict]]:
        """
        Get planetary influences at a specific geographical location.

        Args:
            longitude: Location longitude (-180 to 180)
            latitude: Location latitude (-90 to 90)

        Returns:
            Dictionary with keys: 'active_lines', 'nearby_lines', 'zenith_distances'
            Each containing relevant planetary influence data

        Raises:
            ValueError: If coordinates are out of valid range
        """
        pass

    def calculate_travel_recommendations(
        self,
        target_influences: List[str],
        max_distance_km: Optional[float] = None
    ) -> List[Dict]:
        """
        Find locations with desired planetary influences.

        Args:
            target_influences: List of desired influences (e.g., ['Sun_MC', 'Venus_ASC'])
            max_distance_km: Maximum distance from birth location (optional)

        Returns:
            List of location recommendations with influence details
        """
        pass

    def export_coordinates(
        self,
        format: str = 'geojson',
        include_orbs: bool = True
    ) -> Union[Dict, str]:
        """
        Export line coordinates for mapping applications.

        Args:
            format: Export format ('geojson', 'kml', 'csv')
            include_orbs: Whether to include orb influence zones

        Returns:
            Formatted coordinate data suitable for mapping tools

        Raises:
            ValueError: If format is unsupported
        """
        pass

    def __json__(self) -> Dict:
        """
        Serialize chart to JSON-compatible dictionary.

        Returns:
            Dictionary containing all chart data with nested line/point objects
        """
        pass

    def __str__(self) -> str:
        """
        Human-readable representation of astrocartography chart.

        Returns:
            Formatted string showing key chart information and line counts
        """
        pass