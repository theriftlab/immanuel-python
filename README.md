# <p align="center"><img src="https://github.com/theriftlab/immanuel-python/assets/370745/b834a4b1-9558-410f-8cbd-94018a9e2f1d"></p>

<p align="center">
    <img src="https://img.shields.io/pypi/v/immanuel">
    <img src="https://img.shields.io/python/required-version-toml?tomlFilePath=https://raw.githubusercontent.com/theriftlab/immanuel-python/master/pyproject.toml">
    <img src="https://img.shields.io/github/issues/theriftlab/immanuel-python">
    <img src="https://img.shields.io/pepy/dt/immanuel">
</p>

Immanuel is a Python >= 3.10 package to painlessly provide your application with simple yet detailed chart-centric astrology data for planets, points, signs, houses, aspects, weightings, etc. all based on the [Swiss Ephemeris](https://github.com/astrorigin/pyswisseph). Extra calculations, notably secondary progressions and dignity scores, are modeled on those of [astro.com](https://astro.com) and [Astro Gold](https://www.astrogold.io).

Data for natal charts, solar returns, progressions, and composites are available, as well as the ability to point the aspects from any one chart instance to the planets in another, creating a flexible method to build synastries.

Simply pass in a date and coordinates to one of the available chart classes, and the returned instance will contain all data necessary to construct a full astrological chart. A serializer is bundled to easily output all data as JSON, or it can simply be printed out as human-readable text.

## Translations

Immanuel's output is currently available in the following locales / languages:

* **en_US:** (default) US English
* **pt_BR:** Brazilian Portuguese
* **es_ES:** Spanish

See [here](https://github.com/theriftlab/immanuel-python/tree/v1.4.2/docs/5-settings.md#locale) for details on how to switch. The documentation itself is not currently available in other translations. To contribute in-software translations, see [here](https://github.com/theriftlab/immanuel-python/tree/v1.4.2/docs/7-contributions.md).

## Documentation

Full documentation is available [here](https://github.com/theriftlab/immanuel-python/tree/v1.4.2/docs/0-contents.md), or follow the Quick Start below to see how to quickly generate a natal chart.

## Quick Start

You can get started with full natal chart data in minutes. Simply install Immanuel:

```bash
pip install immanuel
```

Once you've imported Immanuel's chart classes into your application, you will need to hand them a person or event. This is made easy with the Subject class, which takes a date and geographical coordinates. The date can be an ISO-formatted string or a Python datetime instance, and coordinates can be strings or decimals.

```python
from immanuel import charts


native = charts.Subject(
        date_time='2000-01-01 10:00',
        latitude='32n43',
        longitude='117w09',
    )

# or, alternatively...

from datetime import datetime

native = charts.Subject(
        date_time=datetime(2000, 1, 1, 10, 0, 0),
        latitude=32.71667,
        longitude=-117.15,
    )

# and then...

natal = charts.Natal(native)

for object in natal.objects.values():
    print(object)
```

This will output all the chart objects (planets, points, asteroids etc.) in this format:

```
Sun 10°37'26" in Capricorn, 11th House
Moon 16°19'29" in Scorpio, 8th House
Mercury 02°16'43" in Capricorn, 10th House
Venus 01°52'05" in Sagittarius, 9th House
Mars 28°09'26" in Aquarius, 12th House
Jupiter 25°15'48" in Aries, 2nd House
Saturn 10°23'27" in Taurus, 2nd House, Retrograde
Uranus 14°49'19" in Aquarius, 12th House
Neptune 03°12'07" in Aquarius, 12th House
Pluto 11°27'49" in Sagittarius, 9th House
...
```

Add asteroid Ceres into the mix:

```python
from immanuel import charts
from immanuel.const import chart
from immanuel.setup import settings


native = charts.Subject(
        date_time='2000-01-01 10:00',
        latitude='32n43',
        longitude='117w09'
    )

settings.objects.append(chart.CERES)
natal = charts.Natal(native)

for object in natal.objects.values():
    print(object)
```

Now you will see this appended to the list:

```
Ceres 04°30'28" in Libra, 7th House
```

More on the settings & constants in the full documentation - for now, we can see much more data by serializing the chart's `objects` property to JSON like this:

```python
import json

from immanuel.classes.serialize import ToJSON
from immanuel import charts


native = charts.Subject(
        date_time='2000-01-01 10:00',
        latitude='32n43',
        longitude='117w09'
    )

natal = charts.Natal(native)

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
        "name": "Capricorn",
        "element": "Earth",
        "modality": "Cardinal"
    },
    "decan": {
        "number": 2,
        "name": "2nd Decan"
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
    "in_sect": true,
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
* Composite
* Transits

Synastry is also available with an extra step - all chart classes allow an instance of another chart class to be passed as an argument, which will then calculate the main chart's aspects in relation to the passed chart. This way synastry (and transit) charts can be generated with great flexibility.

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

The full documentation covers settings in detail, but much of the output can be customized. The settings class allows you to specify and personalize:

* Locale / language
* The house system to use
* What data each chart returns
* What planets, points, asteroid etc. to include
* Details of the aspect calculations
* Which dignities to use and their scores
* The progression method to use for secondary progressions
* ...and much more.

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

A big thank-you goes to Nathan Octavio who suggested translations, and who translated Immanuel into both Brazilian Portuguese and Spanish.

## Contact

Please post any issues, feature requests, PRs etc. on GitHub. For anything else email robert@theriftlab.com.
