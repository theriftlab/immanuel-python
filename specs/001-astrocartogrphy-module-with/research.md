# Research: Astrocartography Module

## Technical Decisions

### Swiss Ephemeris Integration
**Decision**: Leverage existing pyswisseph integration from Immanuel's ephemeris.py module
**Rationale**:
- Already integrated and tested in the project
- Provides high-precision planetary position calculations required for astrocartography
- Supports both geocentric and topocentric calculations needed for different line types
- Constitutional requirement for astronomical precision

**Alternatives considered**:
- Custom astronomical algorithms: Rejected due to complexity and precision requirements
- Alternative ephemeris libraries: Rejected due to constitutional mandate for Swiss Ephemeris

### Line Calculation Algorithms
**Decision**: Implement iterative geographic sampling with configurable resolution
**Rationale**:
- MC/IC lines: Direct calculation from Right Ascension and Greenwich Sidereal Time
- Ascendant/Descendant lines: Require iterative search using swe.houses_ex for horizon calculations
- Configurable 0.5-degree default sampling provides good balance of precision vs performance
- Meets 10-second performance requirement for world maps

**Alternatives considered**:
- Fixed high-resolution sampling: Rejected due to performance impact
- Mathematical curve fitting: Rejected due to complexity at extreme latitudes

### Data Structure Architecture
**Decision**: Follow existing Immanuel patterns with specialized astrocartography classes
**Rationale**:
- Consistency with existing transit calculations architecture
- JSON serialization using existing ToJSON system
- Clear separation of concerns: calculation logic vs data representation
- Support for both individual line queries and complete chart analysis

**Alternatives considered**:
- Flat coordinate arrays: Rejected due to lack of metadata and type safety
- External data format: Rejected to maintain library cohesion

### Extreme Latitude Handling
**Decision**: Interpolation from nearby stable calculations when direct calculation fails
**Rationale**:
- Maintains continuous line representation even in problematic regions
- Provides graceful degradation rather than hard errors
- Acceptable accuracy loss at extreme latitudes where astrocartography is less commonly used
- Supports global map generation without gaps

**Alternatives considered**:
- Skip problematic regions: Rejected due to incomplete coverage
- Approximation algorithms: More complex to implement and validate
- Error propagation: Would break world map generation workflows

### Performance Optimization
**Decision**: Parallel calculation for independent lines with efficient sampling
**Rationale**:
- MC/IC lines for different planets can be calculated independently
- Ascendant/Descendant calculations can be parallelized by longitude bands
- Configurable sampling resolution allows users to trade precision for speed
- Caching of Greenwich Sidereal Time and common calculations

**Alternatives considered**:
- Sequential calculation: Would not meet 10-second performance target
- Pre-computed lookup tables: Memory intensive and limited flexibility

### Integration with Existing Chart System
**Decision**: Extend charts.py with new AstrocartographyChart class
**Rationale**:
- Follows established pattern from existing chart types
- Reuses existing Subject and coordinate handling
- Maintains API consistency for users familiar with Immanuel
- Enables future synastry astrocartography features

**Alternatives considered**:
- Standalone module: Would duplicate subject handling and coordinate logic
- Functional API only: Less discoverable and harder to extend

## Implementation Strategy

### Phase Approach
1. **Core calculations**: MC/IC lines (simpler, vertical lines)
2. **Complex calculations**: Ascendant/Descendant lines (curved, require iteration)
3. **Advanced features**: Parans, local space lines, aspect lines
4. **Optimization**: Performance tuning and parallel processing
5. **Integration**: Chart class integration and API finalization

### Testing Strategy
- Unit tests for each calculation type with known astronomical positions
- Performance tests to validate 10-second world map requirement
- Edge case tests for polar regions and extreme latitudes
- Integration tests with existing chart system
- Validation against established astrocartography software where possible

### Risk Mitigation
- Early performance validation to catch scalability issues
- Comprehensive edge case testing for extreme latitudes
- Progressive implementation allowing early validation of core concepts
- Fallback strategies documented for calculation failures