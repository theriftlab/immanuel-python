# Transit Calculation Feature - Product Requirements Document

## Overview

Expand the Immanuel library to provide comprehensive transit calculations with high precision, supporting both mundane transits and personal chart transits. This feature will integrate seamlessly with the existing architecture while adding powerful new capabilities.

## Current State Analysis

### Existing Infrastructure
- **Transits Class**: Already calculates planetary positions for "now" at coordinates
- **Synastry System**: `aspects_to` parameter enables chart-to-chart aspects
- **Aspect Engine**: Robust calculation system in `reports/aspect.py`
- **Ephemeris Tools**: Swiss Ephemeris integration in `tools/ephemeris.py`
- **Settings Framework**: Configurable orbs, aspects, and chart data

### Architecture Strengths
- Modular design with clear separation of concerns
- Consistent Subject/Chart class patterns
- JSON serialization support via ToJSON
- Multi-language localization support
- Comprehensive house system support

## Requirements

### 1. Core Transit Calculation Engine

#### 1.1 TransitCalculator Class
**Purpose**: Core engine for calculating planetary positions across time periods

**Key Features**:
- Calculate transiting planets for any date/time range
- Support both mundane (fixed location) and natal (birth chart) transits
- High-precision event timing (accurate to the second)
- Efficient bulk calculations with caching

**Time Interval Support**:
- String intervals: `'daily'`, `'hourly'`, `'weekly'`, `'monthly'`
- Python timedelta objects: `timedelta(hours=6)`, `timedelta(minutes=30)`
- Custom intervals in seconds: `3600` (1 hour)

#### 1.2 Precision Algorithm Requirements
**Exact Event Timing**: Implement iterative refinement algorithms similar to Newton-Raphson method for square root calculation

**Algorithm Approach**:
1. **Initial Approximation**: Use step-based search to bracket the event
2. **Binary Refinement**: Narrow down the time window using binary search
3. **Iterative Convergence**: Apply Newton's method or similar for final precision
4. **Tolerance**: Achieve precision to ±1 second for all transit events

**Example Implementation Pattern**:
```python
def find_exact_transit_time(planet, target_longitude, start_jd, end_jd, tolerance=1.0/86400):
    """Find exact time when planet reaches target longitude using iterative refinement"""
    # 1. Bracket the event with binary search
    # 2. Use derivative (speed) for Newton-Raphson convergence
    # 3. Iterate until within tolerance (1 second = 1/86400 days)
```

### 2. Transit Event Types

#### 2.1 Aspect Transits
- Exact timing when transiting planets form aspects to natal/mundane points
- Support all configured aspects (conjunction, opposition, square, trine, etc.)
- Calculate applying vs. separating aspects
- Track orb entry/exit times

#### 2.2 Ingress Transits
- Sign ingresses (planet changing zodiac signs)
- House ingresses (planet changing houses)
- Precise timing using iterative algorithms

#### 2.3 Station Transits
- Retrograde stations (planet slowing to retrograde)
- Direct stations (planet resuming direct motion)
- Exact stationary moments with second-level precision

#### 2.4 Eclipse Transits
- Solar eclipses affecting chart points
- Lunar eclipses affecting chart points
- Precise eclipse timing and visibility calculations

### 3. New Chart Classes

#### 3.1 MundaneTransits
**Purpose**: Calculate transits for a fixed geographic location

```python
mundane_transits = MundaneTransits(
    start_date='2024-01-01 00:00:00',
    end_date='2024-12-31 23:59:59',
    latitude=40.7128,
    longitude=-74.0060,
    interval='daily',  # or timedelta(days=1)
    timezone='America/New_York'
)
```

**Features**:
- Calculate planetary positions at regular intervals
- Find ingresses and stations
- Generate aspect grids between transiting planets
- House-based event tracking

#### 3.2 NatalTransits
**Purpose**: Calculate transits to a natal chart

```python
natal = Natal(subject)
natal_transits = NatalTransits(
    natal_chart=natal,
    start_date='2024-01-01',
    end_date='2024-12-31',
    interval=timedelta(hours=4),
    aspects_to_calculate=['conjunction', 'opposition', 'square']
)
```

**Features**:
- Aspects between transiting planets and natal positions
- House transits (planets entering natal houses)
- Return calculations (solar, lunar, planetary returns)
- Progressive vs. exact aspect timing

#### 3.3 TransitSearch
**Purpose**: Find specific transit events within date ranges

```python
search = TransitSearch(
    natal_chart=natal,
    start_date='2024-01-01',
    end_date='2024-12-31'
)

# Find all Jupiter conjunctions to natal Sun
jupiter_sun_conjunctions = search.find_aspects(
    transiting_planet=chart.JUPITER,
    natal_planet=chart.SUN,
    aspect=calc.CONJUNCTION,
    precision='second'  # exact timing to the second
)

# Find Mars retrograde periods
mars_retrogrades = search.find_stations(
    planet=chart.MARS,
    station_type='retrograde'
)
```

### 4. Data Structures

#### 4.1 TransitEvent
```python
@dataclass
class TransitEvent:
    event_type: str  # 'aspect', 'ingress', 'station', 'eclipse'
    date_time: datetime
    julian_date: float
    transiting_object: int  # chart constant
    target_object: int | None  # None for ingresses/stations
    aspect_type: int | None  # calc constant for aspects
    orb: float | None
    exact: bool
    longitude: float
    house: int | None

    # Precision metadata
    calculation_method: str
    precision_achieved: float  # in seconds
```

#### 4.2 TransitPeriod
```python
@dataclass
class TransitPeriod:
    start_date: datetime
    end_date: datetime
    events: List[TransitEvent]
    statistics: Dict[str, Any]  # event counts, most active periods, etc.
```

### 5. Precision Requirements

#### 5.1 Event Timing Accuracy
- **Primary Requirement**: All transit events accurate to ±1 second
- **Algorithm**: Iterative refinement using planetary speeds as derivatives
- **Validation**: Compare results against established ephemeris software

#### 5.2 Performance Optimization
- **Bulk Calculations**: Efficient algorithms for date range processing
- **Caching**: Store intermediate calculations for repeated queries
- **Threading**: Support for parallel processing of independent calculations

### 6. Integration with Existing System

#### 6.1 Settings Extension
Add transit-specific settings to existing `settings` class:

```python
# In setup.py BaseSettings.__init__
self.transit_precision_tolerance = 1.0/86400  # 1 second in days
self.transit_default_interval = 'daily'
self.transit_search_step_size = 1.0  # days for initial bracketing
self.transit_max_iterations = 50  # for convergence algorithms
```

#### 6.2 Chart Data Integration
Extend `chart_data` configuration to support transit chart types:

```python
self.chart_data[chart.MUNDANE_TRANSITS] = [
    data.NATIVE,  # Location/time info
    data.TRANSIT_PERIOD,  # Start/end dates
    data.OBJECTS,  # Transiting planets
    data.EVENTS,  # Transit events found
    data.STATISTICS  # Summary data
]
```

#### 6.3 Aspect System Enhancement
Leverage existing `reports/aspect.py` with new functions:
- `transit_aspects()` - aspects between transit and natal positions
- `exact_aspect_time()` - precise timing using iterative algorithms
- `aspect_timeline()` - aspect formation/separation over time

### 7. API Design Examples

#### 7.1 Quick Transit Overview
```python
# Get today's transits to natal chart
natal = Natal(subject)
today_transits = NatalTransits(
    natal_chart=natal,
    start_date=datetime.now(),
    end_date=datetime.now() + timedelta(days=1),
    interval=timedelta(hours=1)
)

# Access current aspects
current_aspects = today_transits.current_aspects
```

#### 7.2 Precise Event Search
```python
# Find exact time of next Jupiter return
search = TransitSearch(natal, datetime.now(), datetime.now() + timedelta(days=4400))
jupiter_return = search.find_planetary_return(chart.JUPITER, precision='second')

# Result: datetime object accurate to the second
print(f"Jupiter return: {jupiter_return}")  # 2025-03-15 14:32:07
```

#### 7.3 Long-term Analysis
```python
# Year-long transit analysis with weekly intervals
yearly_transits = NatalTransits(
    natal_chart=natal,
    start_date='2024-01-01',
    end_date='2024-12-31',
    interval=timedelta(weeks=1)
)

# Export to JSON for external analysis
transit_data = yearly_transits.to_json(indent=2)
```

### 8. Success Metrics

#### 8.1 Precision Benchmarks
- **Timing Accuracy**: 100% of calculated events within ±1 second of reference ephemeris
- **Performance**: Process 1 year of daily transits in <5 seconds
- **Memory Efficiency**: Handle 10+ year calculations without memory issues

#### 8.2 API Usability
- **Consistency**: Follow existing Immanuel patterns 100%
- **Documentation**: Complete docstrings and usage examples
- **Testing**: >95% code coverage with precision validation tests

## Implementation Priority

### Phase 1: Core Precision Engine
1. Implement iterative refinement algorithms
2. Create TransitCalculator base class
3. Add precision validation against reference data

### Phase 2: Basic Transit Classes
1. MundaneTransits implementation
2. NatalTransits implementation
3. TransitEvent data structures

### Phase 3: Advanced Features
1. TransitSearch functionality
2. Eclipse calculations
3. Performance optimizations

### Phase 4: Integration & Polish
1. Settings integration
2. JSON serialization support
3. Documentation and examples

This PRD provides a comprehensive roadmap for adding high-precision transit calculations while maintaining Immanuel's architectural excellence and ease of use.