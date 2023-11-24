# Immanuel

Immanuel is a Python >= 3.10 package for painlessly producing simple, readable, chart-centred astrology data from [pyswisseph](https://github.com/astrorigin/pyswisseph) with extra calculations modelled on those of astro.com and Astro Gold. Simple chart classes take date, time, and location data and return an object which can be output as either human-friendly text or easily serialised into JSON.

## Installation

```bash
pip install immanuel
```

**NOTE:** The package requirements have locked in version 5.2.0 of `timezonefinder` - version >= 6.0.0 requires a C compiler present on installation in order to run with any degree of efficiency. Without one it will revert to a pure-Python library which is painfully slow by comparison. Version 5.2.0 will run much faster if a C compiler is not available, but it is unclear how big an impact on accuracy this will have.

## Chart Types

Currently Immanuel supports the following chart types:

* Natal
* Solar return
* Progressed
* Synastry
* Composite

## Examples

Chart class constructors take dates in standard timezone-naive ISO format (YYYY-MM-DD HH:MM:SS), and coordinates in either standard text format (as in the following examples) or decimal. To generate data for the available charts, you would use something like this:

```python
from immanuel import charts


natal = charts.Natal(dob='2000-01-01 10:00', lat='32n43', lon='117w09')

solar_return = charts.SolarReturn(dob='2000-01-01 10:00', lat='32n43', lon='117w09', year=2025)

progressed = charts.Progressed(dob='2000-01-01 10:00', lat='32n43', lon='117w09', pd='2025-06-20 17:00')

synastry = charts.Synastry(dob='2000-01-01 10:00', lat='32n43', lon='117w09', partner_dob='2001-02-03 15:45', partner_lat='38n35', partner_lon='121w30')

composite = charts.Composite(dob='2000-01-01 10:00', lat='32n43', lon='117w09', partner_dob='2001-02-03 15:45', partner_lat='38n35', partner_lon='121w30')
```

## Returned Chart Data

The various chart types return their own sets of data, but for a basic natal chart you can expect to receive the following:

* Chart date
* Chart coordinates
* House system
* Chart shape type (eg. bowl, splash etc.)
* Whether the chart is diurnal (ie. daytime)
* Moon phase
* All chart objects (eg. planets, asteroids, primary angles etc.) and their positions & dignities if applicable
* Houses
* Aspects
* Weightings (ie. which objects are in which elements / modalities etc.)

The data is available in both human-readable and JSON format. To see an example of both, first we set up with a natal chart:

```python
import json

from immanuel import charts
from immanuel.const import chart
from immanuel.classes.serialize import ToJSON


natal = charts.Natal(dob='2000-01-01 10:00', lat='32n43', lon='117w09')
```

Now we can see the human-readable output of the Sun like this:

```python
print(natal.objects[chart.SUN])
```

Which will output the following string:

```
Sun 10°37'26" in Capricorn, 11th House
```

We can get much more data from the JSON output like this:

```python
print(json.dumps(natal.objects[chart.SUN], cls=ToJSON, indent=4))
```

Which will output the following:

```json
{
    "index": 4000001,
    "name": "Sun",
    "type": {
        "index": 4000000,
        "name": "Planet"
    },
    "latitude": {
        "raw": 0.0002259471008556382,
        "formatted": "00\u00b000'01\"",
        "direction": "+",
        "degrees": 0,
        "minutes": 0,
        "seconds": 1
    },
    "longitude": {
        "raw": 280.6237802656368,
        "formatted": "280\u00b037'26\"",
        "direction": "+",
        "degrees": 280,
        "minutes": 37,
        "seconds": 26
    },
    "sign_longitude": {
        "raw": 10.62378026563681,
        "formatted": "10\u00b037'26\"",
        "direction": "+",
        "degrees": 10,
        "minutes": 37,
        "seconds": 26
    },
    "sign": {
        "number": 10,
        "name": "Capricorn"
    },
    "house": {
        "index": 2000011,
        "number": 11,
        "name": "11th House"
    },
    "distance": 0.9833259257690341,
    "speed": 1.0194579691359147,
    "movement": {
        "direct": true,
        "stationary": false,
        "retrograde": false,
        "formatted": "Direct"
    },
    "declination": {
        "raw": -23.01236501586868,
        "formatted": "-23\u00b000'45\"",
        "direction": "-",
        "degrees": 23,
        "minutes": 0,
        "seconds": 45
    },
    "out_of_bounds": false,
    "dignities": {
        "ruler": false,
        "exalted": false,
        "triplicity_ruler": false,
        "term_ruler": false,
        "face_ruler": false,
        "mutual_reception_ruler": false,
        "mutual_reception_exalted": false,
        "mutual_reception_triplicity_ruler": true,
        "mutual_reception_term_ruler": false,
        "mutual_reception_face_ruler": false,
        "detriment": false,
        "fall": false,
        "peregrine": false,
        "formatted": [
            "Triplicity Ruler by mutual reception"
        ]
    },
    "score": 3
}
```

Note that the entire chart object can be serialized to JSON, not just its properties, eg.:

```python
print(json.dumps(natal, cls=ToJSON, indent=4))
```

Each returned chart object has its own numerical index - for example, the Sun has an index of `4000001`. For common objects, the `chart` module contains constants (in this case `chart.SUN`). It is useful to index chart objects numerically rather than by name so that extra objects may be easily added from ephemeris files by their index. Asteroid Lilith has an index of `1181` in the ephemeris, so if this is added to the requested chart objects then it will be returned with this index. Anywhere else this index appears in the data can then be cross-referenced with its entry in the `objects` property to retrieve its information.

A good example of this is in the `aspects` property. All aspects will reference objects by their index. To see aspect data between the Sun and Moon, we could do this:

```python
print(json.dumps(natal.aspects[chart.SUN][chart.MOON], cls=ToJSON, indent=4))
```

Which would give us this data:

```json
{
    "active": 4000002,
    "passive": 4000001,
    "type": "Sextile",
    "aspect": 60.0,
    "orb": 6.0,
    "distance": {
        "raw": 54.29916852653977,
        "formatted": "54\u00b017'57\"",
        "direction": "+",
        "degrees": 54,
        "minutes": 17,
        "seconds": 57
    },
    "difference": {
        "raw": -5.700831473460227,
        "formatted": "-05\u00b042'03\"",
        "direction": "-",
        "degrees": 5,
        "minutes": 42,
        "seconds": 3
    },
    "movement": {
        "applicative": false,
        "exact": false,
        "separative": true,
        "formatted": "Separative"
    },
    "condition": {
        "associate": true,
        "dissociate": false,
        "formatted": "Associate"
    }
}
```

The active object is the Moon, index `4000002`, while the passive is the Sun, index `4000001` (this is of course to be expected since the Moon consistently travels faster than the sun). The `orb` property is the maximum orb allowed for this aspect as specified in the settings (this particular one defaulting to 6.0°) whereas the `difference` property contains the actual orb of this specific aspect - in this case, -5°42'03".

## Calculations

Calculations for the secondary progressions are based on those of astro.com. The same 3 methods for MC progression are available and will produce the same progressed date, sidereal time, and house positions as astro.com:

* **Daily Houses** - equivalent to astro.com's `ARMC 361°/prog.day`
* **Naibod** (default) - equivalent to astro.com's `ARMC 1 Naibod/prog.day`
* **Solar Arc** - equivalent to astro.com's `MC from solar arc`

Planetary dignity scores are based on those of Astro Gold, although these are somewhat flexible via the settings.

## Settings

The `setup` module contains sensible defaults for chart calculations such as which chart objects to include, the preferred house system, aspect rules and orbs, dignity scores, Part of Fortune calculation etc. Many of the defaults are set to match those of astro.com but are easily overridden using Immanuel's built-in constants. For example, to specify a house system or MC progression method:

```python
from immanuel.const import calc, chart
from immanuel.setup import settings


settings.house_system = chart.CAMPANUS

natal = charts.Natal(dob='2000-01-01 10:00', lat='32n43', lon='117w09')

settings.mc_progression_method = calc.DAILY_HOUSES

progressed = charts.Progressed(dob='2000-01-01 10:00', lat='32n43', lon='117w09', pd='2025-06-20 17:00')
```

There are many detailed customisations for chart data, especially for aspect rules, and a look through the defaults in `setup.py` will give you a good idea of what is available to customise and how.

## Extra Objects

Fixed stars are included in Immanuel's data, but to include extra objects such as asteroids, you will need to download the relevant ephemeris file(s) and tell Immanuel where to find them with the `setup` module, then add it to the settings for returned objects. For example, to include asteroid Lilith (`1181`), download its ephemeris file `se01181s.se1` (currently available [here](https://www.dropbox.com/scl/fo/y3naz62gy6f6qfrhquu7u/h/all_ast/ast1?dl=0)) and use the `add_filepath()` function, then add `1181` to the `settings.objects` list:

```python
import json

from immanuel import charts, setup
from immanuel.classes.serialize import ToJSON
from immanuel.setup import settings


setup.add_filepath('my/directory/path')
settings.objects.append(1181)

natal = charts.Natal(dob='2000-01-01 10:00', lat='32n43', lon='117w09')
print(json.dumps(natal.objects[1181], cls=ToJSON, indent=4))
```

This will return a standard asteroid object:

```json
{
    "index": 1181,
    "name": "Lilith",
    "type": {
        "index": 5000000,
        "name": "Asteroid"
    },
    "latitude": {
        "raw": 4.818541410009123,
        "formatted": "04\u00b049'07\"",
        "direction": "+",
        "degrees": 4,
        "minutes": 49,
        "seconds": 7
    },
    "longitude": {
        "raw": 348.27965784580425,
        "formatted": "348\u00b016'47\"",
        "direction": "+",
        "degrees": 348,
        "minutes": 16,
        "seconds": 47
    },
    "sign_longitude": {
        "raw": 18.279657845804252,
        "formatted": "18\u00b016'47\"",
        "direction": "+",
        "degrees": 18,
        "minutes": 16,
        "seconds": 47
    },
    "sign": {
        "number": 12,
        "name": "Pisces"
    },
    "house": {
        "index": 2000001,
        "number": 1,
        "name": "1st House"
    },
    "distance": 2.4219215373717056,
    "speed": 0.4102596602496747,
    "movement": {
        "direct": true,
        "stationary": false,
        "retrograde": false,
        "formatted": "Direct"
    },
    "declination": {
        "raw": -0.19720685380581718,
        "formatted": "-00\u00b011'50\"",
        "direction": "-",
        "degrees": 0,
        "minutes": 11,
        "seconds": 50
    },
    "out_of_bounds": false
}
```

Fixed stars are already included, and you can pass the name as a string:

```python
from immanuel.setup import settings


settings.objects.append('Antares')
```

## Object Indexing

To recap: *all* chart objects have an index.

* Immanuel maintains internal numerical indices for the main planets, points, and some popular asteroids (you can see which ones specifically in `const.chart`). You are free to use the actual numerical index for these objects, but of course `chart.SUN` is easier to work with than  `4000001`.
* Asteroids from external ephemeris files are indexed by their number, eg. `1181` for Lilith.
* Fixed stars are indexed by their name, which will be a string eg. 'Antares'.

## Useful Submodules

The chart classes are built on various submodules which are used to collect chart-centred data. These submodules are also sufficiently independent and developer-friendly to produce any custom data that might be required outside of purely generating charts. Although a deep dive into each submodule is beyond the scope of this readme, here is a quick overview:

### tools

The `tools` submodules contain functions to extract and standardise useful data from swisseph and perform common calculations on it such as progressions, transits, midpoints etc. There are also functions for date conversion and formatting data. All modules here are agnostic of any settings in the `setup` module.

### objects

The `objects` submodules contain functions for extrapolating chart-specific data from pure ephemeris data based on the settings in the `setup` module. These include calculating aspects, dignity scores, chart shapes etc.

## Tests

Tests are available via Pytest. Simply run this from the root:

```bash
python -m pytest
```

## License

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public License for more details.

## Credits

Immanuel is forever indebted to the pioneering work of Alois Treindl and Dieter Koch at Astrodienst, and to João Ventura for the incredibly detailed [flatlib](https://github.com/flatangle/flatlib) which first inspired the development of this package.
