# Transit Intensity Curves Feature - Product Requirements Document

## Overview

This feature adds the ability to generate "intensity curves" for transit aspects, providing time-series data showing how the orb (angular distance from exact) changes over time as planets move through their orbits. This enables visualization of transit strength patterns, including complex retrograde motions.

## Core Concept

An intensity curve tracks the orb value of a specific aspect over time, from when the aspect first comes within the specified orb threshold until it finally moves beyond that threshold. This creates a curve showing:
- How close the aspect gets to being exact (0° orb)
- Whether the aspect is applying (getting closer) or separating (moving away)
- How retrograde motion affects the transit pattern (multiple peaks, extended duration)

## Requirements

### 1. Data Structure

#### IntensityCurve Class
```python
@dataclass
class IntensityCurve:
    """Time-series data for transit aspect intensity over time."""

    # Core identification
    transit_event_id: str  # Links to parent TransitEvent
    transiting_object: int
    target_object: int
    aspect_type: int

    # Time-series data
    samples: List[Dict[str, Any]]  # Time-ordered intensity samples

    # Configuration used for generation
    sampling_config: Dict[str, Any]

    # Derived metadata
    metadata: Dict[str, Any]

    def __json__(self) -> Dict[str, Any]: ...
```

#### Sample Data Point Structure
```python
{
    'julian_date': float,         # Julian date for astronomical calculations
    'datetime': datetime,         # Human-readable datetime object
    'orb_value': float,           # Angular distance from exact (degrees)
    'applying': bool,             # True if getting closer, False if separating
    'retrograde': bool,           # True if transiting planet is retrograde
    'retrograde_session': int,    # 0=direct, 1=first retrograde, 2=second retrograde, etc.
}
```

### 2. Configuration Options

#### Sampling Configuration
- **Interval Options**:
  - String intervals: "hourly", "daily", "weekly"
  - Timedelta objects: `timedelta(hours=6)`, `timedelta(minutes=30)`
  - Dynamic sampling: More frequent near exact, less when distant

- **Orb Thresholds**:
  - `curve_orb`: Maximum orb for including in curve (e.g., 8.0°)
  - `event_orb`: Tighter orb for event detection (e.g., 3.0°)
  - Allows broader curve visualization while maintaining precise event timing

#### Performance Configuration
- **Enable Flag**: `generate_intensity_curves: bool = False`
- **Immediate Generation**: When enabled, curves are generated during transit search
- **Memory Optimization**: Optional data pruning strategies

### 3. Integration Points

#### TransitEvent Enhancement
```python
@dataclass
class TransitEvent:
    # ... existing fields ...

    # New optional field
    intensity_curve: Optional[IntensityCurve] = None
```

#### TransitSearch Integration
```python
class TransitSearch:
    def find_aspects(
        self,
        # ... existing parameters ...

        # New parameters
        generate_curves: bool = False,
        curve_orb: Optional[float] = None,
        curve_sampling: Union[str, timedelta] = "daily",
    ) -> List[TransitEvent]: ...
```

### 4. Retrograde Handling

#### Single Continuous Curve Approach
- Generate one continuous curve covering entire transit period
- Mark retrograde periods with metadata identifiers
- Track direction changes and station dates

#### Retrograde Metadata Structure
```python
{
    'retrograde_sessions': [
        {
            'session_number': int,      # 1, 2, 3, etc.
            'start_jd': float,          # When retrograde began
            'end_jd': float,            # When direct motion resumed
            'station_retrograde_jd': float,  # Station retrograde moment
            'station_direct_jd': float,      # Station direct moment
            'multiple_exactness': bool  # True if aspect goes exact multiple times
        }
    ],
    'peak_intensity': {
        'best_orb': float,
        'julian_date': float,
        'retrograde_session': int   # 0=during direct, 1+=during retrograde session
    }
}
```

### 5. Performance Optimization

#### Smart Sampling Strategy
1. **Distance-based Frequency**:
   - Within 1°: Sample every hour
   - 1-3°: Sample every 6 hours
   - 3-5°: Sample daily
   - 5°+ (up to curve_orb): Sample weekly

2. **Event-driven Sampling**:
   - Always sample at aspect exact moments
   - Always sample at station dates
   - Always sample at orb threshold crossings

#### Memory Management
- **Immediate Generation**: Curves generated during transit search when enabled
- **Optional Pruning**: Post-processing step using topological persistence
- **Efficient Storage**: Store only essential data points for visualization

### 6. API Design

#### Basic Usage
```python
# Enable curves during search
search = TransitSearch(natal_chart=chart, start_date=start, end_date=end)
aspects = search.find_aspects(
    transiting_planet=chart.SATURN,
    natal_planet=chart.SUN,
    aspect=calc.CONJUNCTION,
    generate_curves=True,
    curve_orb=8.0,
    curve_sampling="daily"
)

# Access curve data
for aspect in aspects:
    if aspect.intensity_curve:
        samples = aspect.intensity_curve.samples
        # Plot or analyze curve data
```

#### Accessing Generated Curves
```python
# Curves are already generated if enabled during search
for aspect in aspects:
    if aspect.intensity_curve:
        # Access curve samples for plotting
        times = [sample['datetime'] for sample in aspect.intensity_curve.samples]
        orbs = [sample['orb_value'] for sample in aspect.intensity_curve.samples]

        # Or use julian dates for calculations
        jd_times = [sample['julian_date'] for sample in aspect.intensity_curve.samples]
```

#### Post-processing Options
```python
# Optional: Prune curve data using topological persistence
from immanuel.tools.curve_processing import prune_curve_data

pruned_curve = prune_curve_data(
    intensity_curve,
    persistence_threshold=0.5  # Keep only significant features
)
```

### 7. Implementation Scope

#### Phase 1: Core Implementation
- [x] Basic IntensityCurve data structure
- [x] Integration with TransitEvent class
- [x] Smart sampling algorithm
- [x] Retrograde period detection
- [x] JSON serialization support

#### Phase 2: Performance Optimization
- [x] Lazy loading implementation
- [x] Memory-efficient storage
- [x] Configurable sampling strategies

#### Phase 3: Advanced Features
- [ ] Topological persistence pruning (optional)
- [ ] Visualization helper utilities
- [ ] Export formats for common plotting libraries

### 8. Technical Considerations

#### Coordinate System Consistency
- Use same geocentric coordinates as transit calculations
- Handle longitude wraparound (359° ↔ 1°) correctly
- Maintain precision consistency with existing transit system

#### Error Handling
- Graceful degradation when curve generation fails
- Clear error messages for invalid configurations
- Fallback to basic transit events if curve generation disabled

#### Testing Requirements
- Unit tests for curve generation algorithms
- Integration tests with retrograde scenarios
- Performance tests with large time ranges
- Visualization output validation

### 9. Success Criteria

1. **Accuracy**: Intensity curves accurately reflect orbital mechanics
2. **Performance**: Curve generation adds <30% overhead to transit calculations
3. **Usability**: Simple API for basic use cases, flexible for advanced needs
4. **Compatibility**: Zero breaking changes to existing transit functionality
5. **Visualization Ready**: Output format suitable for common plotting libraries

## Timeline

- **Week 1**: Core data structures and basic sampling algorithm
- **Week 2**: Retrograde handling and smart sampling optimization
- **Week 3**: Integration with existing transit system and testing
- **Week 4**: Performance optimization and documentation

## Dependencies

- Existing transit calculation system (TransitCalculator, TransitSearch)
- Swiss Ephemeris for planetary position data
- Current JSON serialization framework
- Existing test infrastructure

## Future Enhancements

- Machine learning for optimal sampling point selection
- Real-time streaming of intensity data for current transits
- Integration with web-based visualization frameworks
- Statistical analysis tools for pattern recognition in transit intensities