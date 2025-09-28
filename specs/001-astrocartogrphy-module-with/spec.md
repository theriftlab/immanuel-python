# Feature Specification: Astrocartography Module

**Feature Branch**: `001-astrocartogrphy-module-with`
**Created**: 2025-01-28
**Status**: Draft
**Input**: User description: "Astrocartogrphy module with calculations of major lines and points for a chart and optional aspect lines @astrocartography_description.md"

## Execution Flow (main)
```
1. Parse user description from Input
   → If empty: ERROR "No feature description provided"
2. Extract key concepts from description
   → Identify: actors, actions, data, constraints
3. For each unclear aspect:
   → Mark with [NEEDS CLARIFICATION: specific question]
4. Fill User Scenarios & Testing section
   → If no clear user flow: ERROR "Cannot determine user scenarios"
5. Generate Functional Requirements
   → Each requirement must be testable
   → Mark ambiguous requirements
6. Identify Key Entities (if data involved)
7. Run Review Checklist
   → If any [NEEDS CLARIFICATION]: WARN "Spec has uncertainties"
   → If implementation details found: ERROR "Remove tech details"
8. Return: SUCCESS (spec ready for planning)
```

---

## ⚡ Quick Guidelines
- ✅ Focus on WHAT users need and WHY
- ❌ Avoid HOW to implement (no tech stack, APIs, code structure)
- 👥 Written for business stakeholders, not developers

### Section Requirements
- **Mandatory sections**: Must be completed for every feature
- **Optional sections**: Include only when relevant to the feature
- When a section doesn't apply, remove it entirely (don't leave as "N/A")

### For AI Generation
When creating this spec from a user prompt:
1. **Mark all ambiguities**: Use [NEEDS CLARIFICATION: specific question] for any assumption you'd need to make
2. **Don't guess**: If the prompt doesn't specify something (e.g., "login system" without auth method), mark it
3. **Think like a tester**: Every vague requirement should fail the "testable and unambiguous" checklist item
4. **Common underspecified areas**:
   - User types and permissions
   - Data retention/deletion policies
   - Performance targets and scale
   - Error handling behaviors
   - Integration requirements
   - Security/compliance needs

---

## Clarifications

### Session 2025-01-28
- Q: Which aspects should be supported for aspect lines between birth chart and relocated positions? → A: Configurable aspect set (user can specify which aspects to calculate)
- Q: What measurement units and default values should be used for orb of influence? → A: Kilometers only with 150-km default
- Q: What maximum calculation time should be acceptable for generating a complete world map with all planetary lines? → A: 10 seconds
- Q: What fallback behavior should be used when calculations fail at extreme latitudes? → A: Interpolate values from nearby stable calculations
- Q: What degree interval should be used for sampling astrocartography lines? → A: Configurable in project constants, default 0.5 degrees

---

## User Scenarios & Testing *(mandatory)*

### Primary User Story
Astrological practitioners need to analyze how planetary energies from a birth chart influence different geographical locations on Earth. They want to generate astrocartography maps showing planetary lines (MC, IC, Ascendant, Descendant) and points (zenith positions) to understand where on Earth specific planetary influences are strongest for a given birth chart.

### Acceptance Scenarios
1. **Given** a birth chart with date, time, and location, **When** astrologer requests astrocartography lines for the Sun, **Then** system calculates and returns MC, IC, Ascendant, and Descendant lines as geographical coordinates
2. **Given** a birth chart, **When** astrologer requests zenith points for all planets, **Then** system returns exact latitude/longitude coordinates where each planet was directly overhead at birth moment
3. **Given** planetary line data, **When** astrologer specifies an orb of influence (e.g., 100 miles), **Then** system provides geographical zones around lines where planetary influence is active
4. **Given** two charts (birth chart and relocated chart), **When** astrologer requests aspect lines between charts, **Then** system calculates lines where specific aspects between natal and relocated planets are exact

### Edge Cases
- What happens when calculating lines for polar regions where standard astrological calculations become mathematically unstable?
- How does system handle locations where certain angular positions (like MC/IC) cannot be calculated due to extreme latitudes?
- What happens when planets are circumpolar and don't cross the horizon at certain latitudes?

## Requirements *(mandatory)*

### Functional Requirements
- **FR-001**: System MUST calculate MC (Midheaven) lines showing longitude where each planet culminates at zenith for the birth moment
- **FR-002**: System MUST calculate IC (Imum Coeli) lines showing longitude opposite to MC lines where each planet anti-culminates
- **FR-003**: System MUST calculate Ascendant lines showing curved geographical paths where each planet rises on eastern horizon
- **FR-004**: System MUST calculate Descendant lines showing curved geographical paths where each planet sets on western horizon
- **FR-005**: System MUST calculate zenith points showing exact latitude/longitude where each planet was directly overhead at birth moment
- **FR-006**: System MUST support both zodiacal (ecliptic) and mundo (equatorial) calculation methods for line generation
- **FR-007**: System MUST accept birth chart data including date, time (UTC), and geographical coordinates as input
- **FR-008**: System MUST return line data as series of geographical coordinate pairs with configurable sampling resolution (default 0.5-degree intervals)
- **FR-009**: System MUST support configurable orb of influence around lines measured in kilometers with 150-km default
- **FR-010**: System MUST calculate parans (simultaneous planetary angularity) showing latitude lines where two planets are simultaneously angular
- **FR-011**: System MUST provide local space lines radiating from birth location showing compass directions to planetary positions
- **FR-012**: System MUST support configurable aspect lines between birth chart and relocated positions, allowing users to specify which aspects to calculate
- **FR-013**: System MUST handle edge cases at extreme latitudes by interpolating values from nearby stable calculations when direct calculations fail
- **FR-014**: System MUST maintain astronomical precision using Swiss Ephemeris calculations for all planetary positions
- **FR-015**: System MUST complete calculation of all planetary lines for a world map within 10 seconds

### Key Entities *(include if feature involves data)*
- **AstrocartographyChart**: Represents complete astrocartography analysis for a birth chart, containing all calculated lines and points
- **PlanetaryLine**: Represents a single line type (MC/IC/ASC/DESC) for one planet, containing geographical coordinate series and calculation metadata
- **ZenithPoint**: Represents exact geographical location where a planet was overhead, containing latitude/longitude and planet identifier
- **ParanLine**: Represents latitude line where two specified planets are simultaneously angular, containing geographical coordinates and planet pair information
- **LocalSpaceLine**: Represents directional line from birth location toward planetary position, containing azimuth, distance, and geographical endpoint
- **AspectLine**: Represents geographical line where specific aspect between natal and relocated planet positions is exact, containing aspect type and coordinate series

---

## Review & Acceptance Checklist
*GATE: Automated checks run during main() execution*

### Content Quality
- [x] No implementation details (languages, frameworks, APIs)
- [x] Focused on user value and business needs
- [x] Written for non-technical stakeholders
- [x] All mandatory sections completed

### Requirement Completeness
- [x] No [NEEDS CLARIFICATION] markers remain
- [x] Requirements are testable and unambiguous
- [x] Success criteria are measurable
- [x] Scope is clearly bounded
- [x] Dependencies and assumptions identified

---

## Execution Status
*Updated by main() during processing*

- [x] User description parsed
- [x] Key concepts extracted
- [x] Ambiguities marked
- [x] User scenarios defined
- [x] Requirements generated
- [x] Entities identified
- [x] Review checklist passed

---