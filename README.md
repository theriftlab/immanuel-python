# Immanuel

Immanuel is a Python >= 3.10 package to allow your applications to painlessly produce simple, readable, chart-centred astrology data from [pyswisseph](https://github.com/astrorigin/pyswisseph), with extra calculations modeled on those of [astro.com](https://astro.com) and [Astro Gold](https://www.astrogold.io). Easy-to-use chart classes take date, time, and location data and return an object which can be output as either human-friendly text or easily serialized into JSON.

Full documentation is available [here](https://github.com/theriftlab/immanuel-python/tree/v1.0.12/docs/0-contents.md).

## Quick Start

You can get started generating chart data in minutes. Simply install Immanuel:

```bash
pip install immanuel
```

Now import Immanuel's chart classes and generate a natal chart from a date & coordinates:

```python
from immanuel import charts


natal = charts.Natal(dob='2000-01-01 10:00', lat='32n43', lon='117w09')

for object in natal.objects.values():
    print(object)
```

This will output all the chart objects (planets, points, asteroids etc.) in this format:

```
Sun 10°37'26" in Capricorn, 11th House
Moon 16°19'29" in Scorpio, 8th House
...
```

We can see much more data by serializing the chart's `objects` property to JSON like this:

```python
import json

from immanuel.classes.serialize import ToJSON
from immanuel import charts


natal = charts.Natal(dob='2000-01-01 10:00', lat='32n43', lon='117w09')

print(json.dumps(natal.objects, cls=ToJSON, indent=4))
```

Which will output each of the chart's objects in this format:

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

Note that the entire chart can also be serialized to JSON, eg.:

```python
print(json.dumps(natal, cls=ToJSON, indent=4))
```

## Chart Types

Currently Immanuel supports the following chart types:

* Natal
* Solar return
* Progressed
* Synastry
* Composite

## Returned Chart Data

The various chart types return their own sets of data, but you can expect to receive at least the following in all of them:

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

All properties are available in both human-readable and JSON format as demonstrated above.

## Calculations

Immanuel offers the same three methods for MC progression as astro.com, and will produce the same progressed date, sidereal time, and house positions.

Planetary dignity scores are based on those of Astro Gold, although these are somewhat flexible via the settings.

## Settings

The full documentation covers settings in detail, but much of the output can be customized. The settings module allows you specify what data each chart returns, what planets etc. to include, and to fine-tune many intricate details of the aspect calculations.

## Tests

Tests are available via pytest. If you have cloned the repo, simply run pytest from the root:

```bash
python -m pytest
```

## License

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the [GNU Affero General Public License](LICENSE.md) for more details.

## Credits

Immanuel is forever indebted to the pioneering work of Alois Treindl and Dieter Koch at Astrodienst, and to João Ventura for the incredibly detailed [flatlib](https://github.com/flatangle/flatlib) which first inspired the development of this package.

## Contact

Please post any issues, feature requests, PRs etc. on GitHub. For anything else email robert@theriftlab.com.
