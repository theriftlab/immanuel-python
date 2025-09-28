
# Implementation Plan: Astrocartography Module

**Branch**: `001-astrocartogrphy-module-with` | **Date**: 2025-01-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-astrocartogrphy-module-with/spec.md`

## Execution Flow (/plan command scope)
```
1. Load feature spec from Input path
   → If not found: ERROR "No feature spec at {path}"
2. Fill Technical Context (scan for NEEDS CLARIFICATION)
   → Detect Project Type from file system structure or context (web=frontend+backend, mobile=app+api)
   → Set Structure Decision based on project type
3. Fill the Constitution Check section based on the content of the constitution document.
4. Evaluate Constitution Check section below
   → If violations exist: Document in Complexity Tracking
   → If no justification possible: ERROR "Simplify approach first"
   → Update Progress Tracking: Initial Constitution Check
5. Execute Phase 0 → research.md
   → If NEEDS CLARIFICATION remain: ERROR "Resolve unknowns"
6. Execute Phase 1 → contracts, data-model.md, quickstart.md, agent-specific template file (e.g., `CLAUDE.md` for Claude Code, `.github/copilot-instructions.md` for GitHub Copilot, `GEMINI.md` for Gemini CLI, `QWEN.md` for Qwen Code or `AGENTS.md` for opencode).
7. Re-evaluate Constitution Check section
   → If new violations: Refactor design, return to Phase 1
   → Update Progress Tracking: Post-Design Constitution Check
8. Plan Phase 2 → Describe task generation approach (DO NOT create tasks.md)
9. STOP - Ready for /tasks command
```

**IMPORTANT**: The /plan command STOPS at step 7. Phases 2-4 are executed by other commands:
- Phase 2: /tasks command creates tasks.md
- Phase 3-4: Implementation execution (manual or via tools)

## Summary
Implement astrocartography calculations for the Immanuel library, providing planetary line calculations (MC, IC, Ascendant, Descendant), zenith points, parans, local space lines, and configurable aspect lines. Uses Swiss Ephemeris for astronomical precision with configurable sampling resolution and performance targets under 10 seconds for world maps.

## Technical Context
**Language/Version**: Python 3.10+ (matches existing Immanuel project requirements)
**Primary Dependencies**: pyswisseph (Swiss Ephemeris), existing Immanuel core modules
**Storage**: N/A (computational library, no persistent storage required)
**Testing**: pytest (matches existing project test framework)
**Target Platform**: Cross-platform Python library (Linux, macOS, Windows)
**Project Type**: single (library extension to existing Immanuel project)
**Performance Goals**: Complete world map calculation within 10 seconds for all planetary lines
**Constraints**: 0.5-degree default sampling resolution, 150km default orb influence, interpolation fallback for extreme latitudes
**Scale/Scope**: Library module serving astrological practitioners globally, integrates with existing chart calculation system

## Constitution Check
*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**I. Library-First Architecture**: Is this feature designed as a standalone library component with clear responsibilities?
- [x] Component has single, clear astrological/astronomical purpose (astrocartography calculations)
- [x] Component is independently testable (dedicated test files planned)
- [x] Clear API boundaries defined (charts, tools, classes modules with specific interfaces)

**II. Astronomical Precision**: Does the design leverage Swiss Ephemeris appropriately?
- [x] Uses Swiss Ephemeris for all astronomical calculations (FR-014 mandates Swiss Ephemeris)
- [x] Any custom algorithms documented with precision guarantees (interpolation for extreme latitudes documented)
- [x] Validation plan against established astrological software (performance and accuracy tests planned)

**III. Test-First Development**: Are tests planned before implementation?
- [x] Test scenarios defined for all astrological calculations (performance, edge cases, line generation tests)
- [x] Integration tests planned for ephemeris interactions (astrocartography calculation tests)
- [x] TDD cycle planned (tests first, then implementation per constitution)

**IV. Multilingual Support**: Does the feature include internationalization?
- [x] User-facing text uses locale system (follows existing Immanuel locale patterns)
- [x] Locale mappings planned for new terminology (astrocartography terms will be added to locale system)
- [x] No hard-coded English strings (all user-facing text through locale system)

**V. JSON Serialization**: Are data structures serializable?
- [x] All data structures implement ToJSON compatibility (AstrocartographyChart, PlanetaryLine entities planned with JSON)
- [x] Human-readable output planned alongside JSON (follows existing Immanuel pattern)
- [x] Programmatic interface defined (library functions with clear return types)

## Project Structure

### Documentation (this feature)
```
specs/001-astrocartogrphy-module-with/
├── plan.md              # This file (/plan command output)
├── research.md          # Phase 0 output (/plan command)
├── data-model.md        # Phase 1 output (/plan command)
├── quickstart.md        # Phase 1 output (/plan command)
├── contracts/           # Phase 1 output (/plan command)
└── tasks.md             # Phase 2 output (/tasks command - NOT created by /plan)
```

### Source Code (repository root)
```
immanuel/
├── tools/
│   ├── astrocartography.py    # Core astrocartography calculations
│   └── astrocartography_search.py  # Line search algorithms
├── classes/
│   └── astrocartography_events.py  # Data structures for lines/points
├── const/
│   └── astrocartography.py    # Constants for sampling, orbs, etc.
├── charts.py                  # Extended with astrocartography chart types
└── __init__.py               # Updated exports

tests/
├── test_astrocartography.py  # Core calculation tests
├── test_astrocartography_lines.py  # Line generation tests
├── test_astrocartography_performance.py  # Performance validation
└── test_astrocartography_edge_cases.py  # Extreme latitude handling
```

**Structure Decision**: Single project library extension following existing Immanuel patterns. Astrocartography functionality integrates into existing modules (tools/, classes/, const/) with new dedicated files, maintaining consistency with transit calculations architecture.

## Phase 0: Outline & Research
1. **Extract unknowns from Technical Context** above:
   - For each NEEDS CLARIFICATION → research task
   - For each dependency → best practices task
   - For each integration → patterns task

2. **Generate and dispatch research agents**:
   ```
   For each unknown in Technical Context:
     Task: "Research {unknown} for {feature context}"
   For each technology choice:
     Task: "Find best practices for {tech} in {domain}"
   ```

3. **Consolidate findings** in `research.md` using format:
   - Decision: [what was chosen]
   - Rationale: [why chosen]
   - Alternatives considered: [what else evaluated]

**Output**: research.md with all NEEDS CLARIFICATION resolved

## Phase 1: Design & Contracts
*Prerequisites: research.md complete*

1. **Extract entities from feature spec** → `data-model.md`:
   - Entity name, fields, relationships
   - Validation rules from requirements
   - State transitions if applicable

2. **Generate API contracts** from functional requirements:
   - For each user action → endpoint
   - Use standard REST/GraphQL patterns
   - Output OpenAPI/GraphQL schema to `/contracts/`

3. **Generate contract tests** from contracts:
   - One test file per endpoint
   - Assert request/response schemas
   - Tests must fail (no implementation yet)

4. **Extract test scenarios** from user stories:
   - Each story → integration test scenario
   - Quickstart test = story validation steps

5. **Update agent file incrementally** (O(1) operation):
   - Run `.specify/scripts/bash/update-agent-context.sh claude`
     **IMPORTANT**: Execute it exactly as specified above. Do not add or remove any arguments.
   - If exists: Add only NEW tech from current plan
   - Preserve manual additions between markers
   - Update recent changes (keep last 3)
   - Keep under 150 lines for token efficiency
   - Output to repository root

**Output**: data-model.md, /contracts/*, failing tests, quickstart.md, agent-specific file

## Phase 2: Task Planning Approach
*This section describes what the /tasks command will do - DO NOT execute during /plan*

**Task Generation Strategy**:
- Load `.specify/templates/tasks-template.md` as base
- Generate tasks from Phase 1 design docs (contracts, data model, quickstart)
- Contract tests: AstrocartographyChart API contract → test suite [P]
- Contract tests: AstrocartographyCalculator API contract → test suite [P]
- Data model entities: Each entity class creation → task [P]
- Integration tests: Each quickstart scenario → validation test
- Implementation tasks: Core calculator, chart class, line generation algorithms
- Performance tests: 10-second world map validation, extreme latitude handling

**Ordering Strategy**:
- Setup: Project constants, ephemeris integration configuration
- TDD order: Contract tests → Entity tests → Integration tests → Implementation
- Core dependencies: AstrocartographyCalculator before AstrocartographyChart
- Line calculation: MC/IC (simple) before ASC/DESC (complex) before advanced features
- Mark [P] for parallel execution: different entity files, independent test suites
- Performance validation as final gate before completion

**Key Task Categories**:
1. **Setup Tasks**: Constants, configuration, ephemeris integration
2. **Test Tasks [TDD]**: Contract tests for APIs, entity validation tests
3. **Core Implementation**: Calculator engine, line generation algorithms
4. **Chart Integration**: AstrocartographyChart class, existing chart system integration
5. **Advanced Features**: Parans, local space, aspect lines (if time permits)
6. **Validation**: Performance tests, extreme latitude tests, quickstart validation

**Estimated Output**: 30-35 numbered, ordered tasks in tasks.md

**IMPORTANT**: This phase is executed by the /tasks command, NOT by /plan

## Phase 3+: Future Implementation
*These phases are beyond the scope of the /plan command*

**Phase 3**: Task execution (/tasks command creates tasks.md)  
**Phase 4**: Implementation (execute tasks.md following constitutional principles)  
**Phase 5**: Validation (run tests, execute quickstart.md, performance validation)

## Complexity Tracking
*Fill ONLY if Constitution Check has violations that must be justified*

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |


## Progress Tracking
*This checklist is updated during execution flow*

**Phase Status**:
- [x] Phase 0: Research complete (/plan command)
- [x] Phase 1: Design complete (/plan command)
- [x] Phase 2: Task planning complete (/plan command - describe approach only)
- [ ] Phase 3: Tasks generated (/tasks command)
- [ ] Phase 4: Implementation complete
- [ ] Phase 5: Validation passed

**Gate Status**:
- [x] Initial Constitution Check: PASS
- [x] Post-Design Constitution Check: PASS
- [x] All NEEDS CLARIFICATION resolved
- [x] Complexity deviations documented (none - all principles satisfied)

---
*Based on Constitution v1.0.0 - See `.specify/memory/constitution.md`*
