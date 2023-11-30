# Submodules

Immanuel's chart classes are built upon several smaller submodules which you will find in the `tools` and `reports` directories. Those under `tools` are fairly universal and are completely agnostic of Immanuel's settings. Those under `reports` generally build on the data pulled from the `tools` modules, and require access to the settings to perform their calculations.

These submodules represent Immanuel's backbone and therefore contain far too much functionality to document here, but you are of course free to browse the code and use them yourself if desired.

## tools

| Module | Purpose |
| --- | --- |
| calculate | Simple calculations based on ephemeris data, such as moon phase, Part of Fortune position, year length for progressions, etc. |
| convert | Converting between string, tuple, and decimal formats for common data such as coordinates and angles. |
| date | Timezone management based on geographical coordinates, and easy conversion between Gregorian and Julian dates between timezones. |
| ephemeris | The main interface with the `swisseph` module. This essentially pulls house, angle, fixed star and other object data and standardises it for use in chart calculations. It also calculates pre- and post-natal lunar and solar eclipses, and pulls other important data for Immanuel's inner workings, such as obliquity and Delta-T. |
| find | Given a date, this provides searches for the previous or next of a given aspect between two chart objects. It also provides the dates of the previous or next lunar or solar eclipse. |
| forecast | Calculates solar return and secondary progression dates. |
| midpoint | Calculates composite chart objects and houses. |
| position | Returns info on a chart object's sign, house, decan, etc. |

## reports

| Module | Purpose |
| --- | --- |
| aspect | Calculates all aspects between a chart's objects, based on the settings. |
| dignity | Calculates a chart object's dignity state, and assigns it an Astro Gold-style score based on the settings. |
| pattern | Currently just finds which pattern a chart's objects make. |
| weighting | Provides breakdowns of a chart's objects between element, modality, and house quadrants. |

---

1. [Overview](1-overview.md)
2. [Installation](2-installation.md)
3. [Examples](3-examples.md)
4. [Returned Data](4-data.md)
5. [Calculations](5-calculations.md)
6. [Settings](6-settings.md)
7. Submodules
