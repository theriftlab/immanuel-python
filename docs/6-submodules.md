# Submodules

Immanuel's chart classes are built upon several smaller submodules which you will find in the `tools` and `reports` directories. Those under `tools` are fairly universal and are completely agnostic of Immanuel's settings. Those under `reports` generally build on the data pulled from the `tools` modules, and require access to the settings to perform their calculations.

These submodules represent Immanuel's backbone and therefore contain far too much functionality to document here, but you are of course free to browse the code and use them yourself if desired.

## tools

| Module | Purpose |
| --- | --- |
| condition | Calculates position & motion conditions of a chart object (sect, retrograde, out of bounds, etc.), the moon's phase, and daytime status. |
| convert | Conversion between string, tuple, and decimal formats for common data such as coordinates and angles. |
| date | Timezone management based on geographical coordinates, and easy conversion between Gregorian and Julian dates across timezones. Also provides supporting functions including Delta-T and sidereal time. |
| ephemeris | The main source of standardized chart object data used to build charts. Under the hood this is mostly a dispatcher to the more granular and technical functions of the `sweph` module. |
| forecast | Calculates solar return and secondary progression dates. |
| midpoint | Calculates composite chart objects and houses by the midpoint method. |
| orbit | Orbital mechanics for chart objects, as well as the properties of Earth's own orbit. |
| part | Calculates the longitudes of the Parts of Fortune, Spirit, and Eros. |
| position | Returns info on a chart object's position in the chart - sign, house, decan, etc. |
| sweph | The direct interface with the external `pysweph` module, standardizing its house, angle, fixed star and other chart object data for the other `tools` modules to build on. Most of its functions can work with either a Julian date or an ARMC. This is the main ephemeris engine at the core of Immanuel. |
| transit | Searches for the previous or next of a given aspect between two chart objects, as well as the previous or next lunar or solar eclipse, new or full moon, and sign ingress / egress. |

## reports

| Module | Purpose |
| --- | --- |
| aspect | Calculates all aspects between a chart's objects, based on the settings. |
| dignity | Calculates a chart object's dignity state, and assigns it an Astro Gold-style score based on the settings. |
| pattern | Finds which pattern a chart's objects make. |
| weighting | Provides breakdowns of a chart's objects between element, modality, and house quadrants. |

---

1. [Overview](1-overview.md)
2. [Installation](2-installation.md)
3. [Examples](3-examples.md)
4. [Returned Data](4-data.md)
5. [Settings](5-settings.md)
6. Submodules
7. [Contributions](7-contributions.md)
