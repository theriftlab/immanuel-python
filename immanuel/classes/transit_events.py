"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    Data structures for transit events and calculations.
    These classes define the structure of transit data returned
    by transit calculations.

"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

from immanuel.const import transits


@dataclass
class IntensityCurve:
    """Time-series data for transit aspect intensity over time."""

    # Core identification
    transit_event_id: str
    transiting_object: int
    target_object: int
    aspect_type: int

    # Time-series data
    samples: List[Dict[str, Any]]

    # Configuration used for generation
    sampling_config: Dict[str, Any]

    # Derived metadata
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.sampling_config is None:
            self.sampling_config = {}

    def __json__(self) -> Dict[str, Any]:
        """JSON serialization method for ToJSON encoder."""
        return {
            'transit_event_id': self.transit_event_id,
            'transiting_object': self.transiting_object,
            'target_object': self.target_object,
            'aspect_type': self.aspect_type,
            'samples': [self._serialize_sample(sample) for sample in self.samples],
            'sampling_config': self.sampling_config,
            'metadata': self.metadata
        }

    def _serialize_sample(self, sample: Dict[str, Any]) -> Dict[str, Any]:
        """Serialize a single sample point for JSON output."""
        serialized = sample.copy()
        # Convert datetime to ISO format
        if 'datetime' in serialized and isinstance(serialized['datetime'], datetime):
            serialized['datetime'] = serialized['datetime'].isoformat()
        return serialized

    def get_peak_intensity(self) -> Optional[Dict[str, Any]]:
        """Get the sample point with the smallest orb (closest to exact)."""
        if not self.samples:
            return None
        return min(self.samples, key=lambda s: s['orb_value'])

    def get_samples_by_retrograde_session(self, session: int) -> List[Dict[str, Any]]:
        """Get all samples from a specific retrograde session."""
        return [s for s in self.samples if s.get('retrograde_session', 0) == session]

    def get_applying_samples(self) -> List[Dict[str, Any]]:
        """Get all samples where the aspect is applying."""
        return [s for s in self.samples if s.get('applying', False)]

    def get_separating_samples(self) -> List[Dict[str, Any]]:
        """Get all samples where the aspect is separating."""
        return [s for s in self.samples if not s.get('applying', True)]


@dataclass
class TransitEvent:
    """Represents a single transit event with precise timing and metadata."""

    event_type: str  # transits.EVENT_* constant
    date_time: datetime
    julian_date: float
    transiting_object: int  # chart constant (e.g., chart.SUN)
    target_object: Optional[int] = None  # None for ingresses/stations
    aspect_type: Optional[int] = None  # calc constant for aspects
    orb: Optional[float] = None
    exact: bool = False
    longitude: float = 0.0
    house: Optional[int] = None

    # Precision metadata
    calculation_method: str = "swisseph"
    precision_achieved: str = transits.PRECISION_SECOND

    # Additional event-specific data
    metadata: Dict[str, Any] = None

    # Intensity curve data (optional)
    intensity_curve: Optional[IntensityCurve] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}

    def __json__(self) -> Dict[str, Any]:
        """JSON serialization method for ToJSON encoder."""
        return {
            'event_type': self.event_type,
            'date_time': self.date_time.isoformat() if self.date_time else None,
            'julian_date': self.julian_date,
            'transiting_object': self.transiting_object,
            'target_object': self.target_object,
            'aspect_type': self.aspect_type,
            'orb': self.orb,
            'exact': self.exact,
            'longitude': self.longitude,
            'house': self.house,
            'calculation_method': self.calculation_method,
            'precision_achieved': self.precision_achieved,
            'metadata': self.metadata,
            'intensity_curve': self.intensity_curve.__json__() if self.intensity_curve else None
        }


@dataclass
class TransitPeriod:
    """Represents a period of time with associated transit events and statistics."""

    start_date: datetime
    end_date: datetime
    events: List[TransitEvent]
    interval: Union[str, object]  # timedelta or string

    # Statistics
    statistics: Dict[str, Any] = None

    def __post_init__(self):
        if self.statistics is None:
            self.statistics = {}

    def __json__(self) -> Dict[str, Any]:
        """JSON serialization method for ToJSON encoder."""
        return {
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'events': [event.__json__() for event in self.events],
            'interval': str(self.interval),  # Convert timedelta to string
            'statistics': self.statistics
        }

    def add_event(self, event: TransitEvent) -> None:
        """Add a transit event to this period."""
        self.events.append(event)
        self._update_statistics()

    def _update_statistics(self) -> None:
        """Update statistics based on current events."""
        if not self.events:
            return

        # Count events by type
        event_counts = {}
        for event in self.events:
            event_type = event.event_type
            event_counts[event_type] = event_counts.get(event_type, 0) + 1

        # Count events by transiting object
        object_counts = {}
        for event in self.events:
            obj = event.transiting_object
            object_counts[obj] = object_counts.get(obj, 0) + 1

        self.statistics.update({
            'total_events': len(self.events),
            'event_type_counts': event_counts,
            'object_counts': object_counts,
            'first_event': min(self.events, key=lambda e: e.julian_date).date_time,
            'last_event': max(self.events, key=lambda e: e.julian_date).date_time,
        })

    def get_events_by_type(self, event_type: str) -> List[TransitEvent]:
        """Get all events of a specific type."""
        return [e for e in self.events if e.event_type == event_type]

    def get_events_for_object(self, object_index: int) -> List[TransitEvent]:
        """Get all events for a specific transiting object."""
        return [e for e in self.events if e.transiting_object == object_index]


@dataclass
class StationEvent(TransitEvent):
    """Specialized transit event for planetary stations."""

    station_type: str = transits.STATION_RETROGRADE  # or STATION_DIRECT
    speed_before: float = 0.0
    speed_after: float = 0.0

    def __post_init__(self):
        super().__post_init__()
        self.event_type = transits.EVENT_STATION
        self.metadata.update({
            'station_type': self.station_type,
            'speed_before': self.speed_before,
            'speed_after': self.speed_after,
        })


@dataclass
class IngressEvent(TransitEvent):
    """Specialized transit event for sign or house ingresses."""

    from_position: Union[int, str] = None  # previous sign/house
    to_position: Union[int, str] = None    # new sign/house

    def __post_init__(self):
        super().__post_init__()
        # event_type is already set from parent class
        self.metadata.update({
            'from_position': self.from_position,
            'to_position': self.to_position,
        })


@dataclass
class AspectEvent(TransitEvent):
    """Specialized transit event for aspects between transiting and natal/fixed objects."""

    orb_difference: float = 0.0  # How close to exact
    applying: bool = True        # True if applying, False if separating

    def __post_init__(self):
        super().__post_init__()
        self.event_type = transits.EVENT_ASPECT
        self.metadata.update({
            'orb_difference': self.orb_difference,
            'applying': self.applying,
        })


@dataclass
class EclipseEvent(TransitEvent):
    """Specialized transit event for eclipses affecting chart points."""

    eclipse_type: str = "total"  # total, partial, annular, etc.
    visibility_info: Dict[str, Any] = None
    magnitude: float = 0.0

    def __post_init__(self):
        super().__post_init__()
        self.event_type = transits.EVENT_ECLIPSE
        if self.visibility_info is None:
            self.visibility_info = {}
        self.metadata.update({
            'eclipse_type': self.eclipse_type,
            'magnitude': self.magnitude,
            'visibility_info': self.visibility_info,
        })


# Factory function to create appropriate event type
def create_transit_event(event_type: str, **kwargs) -> TransitEvent:
    """Factory function to create the appropriate transit event subclass."""

    event_classes = {
        transits.EVENT_ASPECT: AspectEvent,
        transits.EVENT_STATION: StationEvent,
        transits.EVENT_INGRESS_SIGN: IngressEvent,
        transits.EVENT_INGRESS_HOUSE: IngressEvent,
        transits.EVENT_ECLIPSE: EclipseEvent,
        transits.EVENT_PLANETARY_RETURN: AspectEvent,  # Special case of aspect
    }

    event_class = event_classes.get(event_type, TransitEvent)

    # Ensure event_type is passed to all subclasses
    kwargs['event_type'] = event_type

    return event_class(**kwargs)