# Tasks: Astrocartography Module

**Input**: Design documents from `/specs/001-astrocartogrphy-module-with/`
**Prerequisites**: plan.md (required), research.md, data-model.md, contracts/

## Execution Flow (main)
```
1. Load plan.md from feature directory
   → If not found: ERROR "No implementation plan found"
   → Extract: tech stack, libraries, structure
2. Load optional design documents:
   → data-model.md: Extract entities → model tasks
   → contracts/: Each file → contract test task
   → research.md: Extract decisions → setup tasks
3. Generate tasks by category:
   → Setup: project init, dependencies, linting
   → Tests: contract tests, integration tests
   → Core: models, services, CLI commands
   → Integration: DB, middleware, logging
   → Polish: unit tests, performance, docs
4. Apply task rules:
   → Different files = mark [P] for parallel
   → Same file = sequential (no [P])
   → Tests before implementation (TDD)
5. Number tasks sequentially (T001, T002...)
6. Generate dependency graph
7. Create parallel execution examples
8. Validate task completeness:
   → All contracts have tests?
   → All entities have models?
   → All endpoints implemented?
9. Return: SUCCESS (tasks ready for execution)
```

## Format: `[ID] [P?] Description`
- **[P]**: Can run in parallel (different files, no dependencies)
- Include exact file paths in descriptions

## Path Conventions
- **Single project**: Immanuel library structure at repository root
- **immanuel/**: Main library code (tools/, classes/, const/, charts.py)
- **tests/**: Test files matching immanuel/ structure
- Paths follow existing Immanuel project conventions

## Phase 3.1: Setup
- [x] T001 Create astrocartography constants in immanuel/const/astrocartography.py
- [x] T002 [P] Add astrocartography imports to immanuel/__init__.py
- [x] T003 [P] Configure pytest for astrocartography test coverage

## Phase 3.2: Tests First (TDD) ⚠️ MUST COMPLETE BEFORE 3.3
**CRITICAL: These tests MUST be written and MUST FAIL before ANY implementation**
- [ ] T004 [P] Contract test AstrocartographyChart class API in tests/test_astrocartography_chart_contract.py
- [ ] T005 [P] Contract test AstrocartographyCalculator class API in tests/test_astrocartography_calculator_contract.py
- [ ] T006 [P] Integration test basic chart generation in tests/test_astrocartography_integration.py
- [ ] T007 [P] Integration test planetary line calculations in tests/test_astrocartography_lines.py
- [ ] T008 [P] Integration test zenith point calculations in tests/test_astrocartography_zenith.py
- [ ] T009 [P] Performance test 10-second world map requirement in tests/test_astrocartography_performance.py
- [ ] T010 [P] Edge case test extreme latitude handling in tests/test_astrocartography_edge_cases.py

## Phase 3.3: Core Implementation (ONLY after tests are failing)
- [ ] T011 [P] PlanetaryLine entity class in immanuel/classes/astrocartography_entities.py
- [ ] T012 [P] ZenithPoint entity class in immanuel/classes/astrocartography_entities.py
- [ ] T013 [P] ParanLine entity class in immanuel/classes/astrocartography_entities.py
- [ ] T014 [P] LocalSpaceLine entity class in immanuel/classes/astrocartography_entities.py
- [ ] T015 [P] AspectLine entity class in immanuel/classes/astrocartography_entities.py
- [ ] T016 AstrocartographyCalculator core engine in immanuel/tools/astrocartography.py
- [ ] T017 MC/IC line calculation methods in immanuel/tools/astrocartography.py
- [ ] T018 Ascendant/Descendant line calculation methods in immanuel/tools/astrocartography.py
- [ ] T019 Zenith point calculation methods in immanuel/tools/astrocartography.py
- [ ] T019a Mundo (equatorial) calculation method implementation in immanuel/tools/astrocartography.py
- [ ] T020 Extreme latitude interpolation methods in immanuel/tools/astrocartography.py
- [ ] T021 AstrocartographyChart class in immanuel/charts.py
- [ ] T022 Chart initialization and validation logic in immanuel/charts.py
- [ ] T023 Planetary line access methods in immanuel/charts.py
- [ ] T024 Location influence analysis methods in immanuel/charts.py
- [ ] T025 Coordinate export functionality in immanuel/charts.py

## Phase 3.4: Advanced Features
- [ ] T026 [P] Paran line calculation in immanuel/tools/astrocartography_search.py
- [ ] T027 [P] Local space line calculation in immanuel/tools/astrocartography_search.py
- [ ] T028 [P] Aspect line calculation in immanuel/tools/astrocartography_search.py
- [ ] T029 Travel recommendation algorithm in immanuel/tools/astrocartography_search.py
- [ ] T030 Coordinate export formats (GeoJSON, KML, CSV) in immanuel/tools/astrocartography_search.py

## Phase 3.5: Integration & JSON Serialization
- [ ] T031 JSON serialization for all astrocartography entities using ToJSON
- [ ] T032 Human-readable string representations (__str__ methods)
- [ ] T033 Locale support for astrocartography terminology in immanuel/const/names.py
- [ ] T034 Integration with existing chart class hierarchy
- [ ] T035 Swiss Ephemeris error handling and fallback strategies

## Phase 3.6: Polish & Validation
- [ ] T036 [P] Unit tests for PlanetaryLine entity in tests/test_astrocartography_entities.py
- [ ] T037 [P] Unit tests for calculation accuracy validation in tests/test_astrocartography_accuracy.py
- [ ] T038 [P] Performance optimization and caching in immanuel/tools/astrocartography.py
- [ ] T039 [P] Documentation strings for all public methods
- [ ] T040 [P] Quickstart validation - run all examples from quickstart.md
- [ ] T041 Integration test with existing natal chart workflow
- [ ] T042 Memory usage optimization for large coordinate sets

## Dependencies
**Setup Dependencies**:
- T001 blocks T002, T003
- T002, T003 can run in parallel after T001

**Test Dependencies (TDD Critical)**:
- T004-T010 must complete and FAIL before any T011+ implementation
- T004-T010 can all run in parallel (different test files)

**Core Implementation Dependencies**:
- T011-T015 (entities) must run sequentially (same file, different classes)
- T016 (calculator) blocks T017-T020 (calculation methods)
- T019a depends on T016 (calculator core)
- T021 (chart class) blocks T022-T025 (chart methods)
- T021 depends on T011-T015 (entities) and T016 (calculator)

**Advanced Features Dependencies**:
- T026-T030 depend on T016 (calculator core)
- T026-T028 can run in parallel (different calculation types)

**Integration Dependencies**:
- T031-T035 depend on all core implementation (T011-T025)
- T031, T032 can run in parallel (different concerns)

**Polish Dependencies**:
- T036-T042 depend on complete implementation
- T036, T037, T039, T040 can run in parallel (different test files)

## Parallel Example
```
# Launch contract tests together (T004-T010):
Task: "Write contract test for AstrocartographyChart class API in tests/test_astrocartography_chart_contract.py"
Task: "Write contract test for AstrocartographyCalculator class API in tests/test_astrocartography_calculator_contract.py"
Task: "Write integration test for basic chart generation in tests/test_astrocartography_integration.py"
Task: "Write performance test for 10-second world map requirement in tests/test_astrocartography_performance.py"
```

## Notes
- [P] tasks = different files, no dependencies
- Verify tests fail before implementing
- Commit after each task
- Maintain 10-second performance target throughout implementation
- Follow TDD cycle: Red-Green-Refactor for each component
- All coordinate calculations must use Swiss Ephemeris for precision
- Implement interpolation fallback for extreme latitudes per constitutional requirements

## Task Generation Rules
*Applied during main() execution*

1. **From Contracts**:
   - astrocartography_chart.py → T004 contract test [P]
   - astrocartography_calculator.py → T005 contract test [P]

2. **From Data Model**:
   - AstrocartographyChart → T021 chart class
   - PlanetaryLine → T011 entity class [P]
   - ZenithPoint → T012 entity class [P]
   - ParanLine → T013 entity class [P]
   - LocalSpaceLine → T014 entity class [P]
   - AspectLine → T015 entity class [P]

3. **From Quickstart Scenarios**:
   - Basic usage → T006 integration test [P]
   - Location analysis → T007 line calculation test [P]
   - Performance monitoring → T009 performance test [P]
   - Extreme coordinates → T010 edge case test [P]

4. **Ordering**:
   - Setup (T001-T003) → Tests (T004-T010) → Entities (T011-T015) → Calculator (T016-T020) → Chart (T021-T025) → Advanced (T026-T030) → Integration (T031-T035) → Polish (T036-T042)

## Validation Checklist
*GATE: Checked by main() before returning*

- [x] All contracts have corresponding tests (T004, T005)
- [x] All entities have creation tasks (T011-T015)
- [x] All tests come before implementation (T004-T010 before T011+)
- [x] Parallel tasks truly independent ([P] marked appropriately)
- [x] Each task specifies exact file path
- [x] No task modifies same file as another [P] task
- [x] Performance requirements addressed (T009, T038)
- [x] Constitutional requirements covered (TDD, Swiss Ephemeris, JSON serialization, internationalization)