<!--
Sync Impact Report:
Version change: template → 1.0.0
Added sections: All core principles and governance
Templates requiring updates:
✅ .specify/templates/plan-template.md (Constitution Check section updated with specific principle gates)
✅ .specify/templates/spec-template.md (no constitution references - no changes needed)
✅ .specify/templates/tasks-template.md (no constitution references - no changes needed)
✅ .specify/templates/agent-file-template.md (no constitution references - no changes needed)
✅ All template files synchronized with constitution v1.0.0
No follow-up TODOs - all placeholders filled and dependencies updated
-->

# Immanuel Constitution

## Core Principles

### I. Library-First Architecture
Every feature MUST start as a standalone library component with clear responsibilities.
Libraries MUST be self-contained, independently testable, and documented with clear APIs.
No organizational-only libraries - each component must serve a specific astronomical or
astrological calculation purpose.

**Rationale**: Maintains modularity and enables reliable composition of astrological
calculations while ensuring each component can be tested and understood in isolation.

### II. Astronomical Precision
All calculations MUST leverage Swiss Ephemeris for maximum precision and astronomical
accuracy. Custom algorithms are forbidden unless Swiss Ephemeris lacks the required
functionality, and then MUST be documented with precision guarantees and validation
against established astronomical sources.

**Rationale**: Astrological applications require high precision astronomical data.
Swiss Ephemeris is the gold standard for accuracy and ensures compatibility with
professional astrological software.

### III. Test-First Development (NON-NEGOTIABLE)
TDD MUST be strictly enforced: Tests written → User approved → Tests fail → Then implement.
Red-Green-Refactor cycle is mandatory. Integration tests MUST cover all astrological
calculation accuracy, especially for new chart types, aspect calculations, and
ephemeris interactions.

**Rationale**: Astrological calculations are complex and precision-critical. Testing
first ensures accuracy and prevents regression in astronomical computations that
users depend on for astrological analysis.

### IV. Multilingual Support
All user-facing text MUST support internationalization through the locale system.
New features MUST include locale mappings. Breaking changes to locale keys require
migration documentation.

**Rationale**: Astrology is a global practice with practitioners speaking many languages.
Maintaining translation support ensures accessibility across cultures and regions.

### V. JSON Serialization & CLI Interface
Every astrological data structure MUST be JSON serializable using the ToJSON system.
All library functionality MUST be accessible via programmatic interface. Human-readable
text output MUST be provided alongside JSON for debugging and user interfaces.

**Rationale**: Enables integration with web applications, mobile apps, and other tools
while maintaining both machine-readable and human-readable outputs for flexibility.

## Quality Standards

All changes MUST maintain backward compatibility unless increment major version.
Performance MUST be maintained - calculation-heavy operations like transit searches
MUST complete within reasonable timeframes (< 10s for yearly transit searches).
Code coverage MUST exceed 90% for all astrological calculation modules.

## Development Workflow

Feature development MUST follow the specification → planning → implementation workflow.
All calculations MUST be validated against known astrological software outputs
(astro.com, Astro Gold) for consistency. Breaking changes require documentation of
migration path and version bump rationale.

## Governance

This constitution supersedes all other development practices and coding conventions.
All pull requests MUST verify compliance with these principles before merge.
Complexity that violates these principles MUST be justified in feature documentation
or the approach must be simplified to comply.

Amendments require documentation of impact, approval from maintainers, and migration
plan for affected components. Version increments follow semantic versioning:
- MAJOR: Breaking API changes or calculation methodology changes
- MINOR: New astrological features or calculation types
- PATCH: Bug fixes, performance improvements, documentation

**Version**: 1.0.0 | **Ratified**: 2025-01-28 | **Last Amended**: 2025-01-28