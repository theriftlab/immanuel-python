# <p align="center"><img src="https://github.com/theriftlab/immanuel-python/assets/370745/b834a4b1-9558-410f-8cbd-94018a9e2f1d"></p>

<p align="center">
    <a href="https://github.com/Essk/ai-contribution-level">
        <img src="https://raw.githubusercontent.com/Essk/ai-contribution-level/main/badges/level-1.svg" alt="AI Contribution: Level 1 - Research Only">
    </a>
</p>

<p align="center">
    <img src="https://img.shields.io/pypi/v/immanuel">
    <img src="https://img.shields.io/python/required-version-toml?tomlFilePath=https://raw.githubusercontent.com/theriftlab/immanuel-python/master/pyproject.toml">
    <img src="https://img.shields.io/github/issues/theriftlab/immanuel-python">
    <img src="https://img.shields.io/pepy/dt/immanuel">
</p>

#### NOTE: This README and the documentation are for the `master` branch which is often in flux. Please check the docs for your installed release version to ensure they match the code.

Immanuel is a Python >= 3.10 package with a focus on speed, simplicity, and precision. Its classes generate chart-centric astrology data - planets, points, signs, houses, aspects, weightings, and more - based on the [Swiss Ephemeris](https://github.com/sailorfe/pysweph), with progressions and dignity scores modeled on [astro.com](https://astro.com) and [Astro Gold](https://www.astrogold.io). This makes it a breeze to generate natal, solar return, progressed, and composite charts, plus create cross-chart aspects for flexible synastries.

## Quick Start

Full documentation is available [here](/docs/0-contents.md), but you can get started with full natal chart data in minutes. Simply install Immanuel:

```bash
pip install immanuel
```

Once you've imported Immanuel's chart classes, you will need to hand them a `Subject`, which takes a date and geographical coordinates. The date can be an ISO-formatted string or a Python `datetime` instance, and coordinates can be strings or floats.

```python
from immanuel import charts


native = charts.Subject(
        date_time="2000-01-01 10:00",
        latitude="32n43",
        longitude="117w09",
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

# Sun 10°37'26" in Capricorn, 11th House
# Moon 16°19'29" in Scorpio, 8th House
# Mercury 02°16'43" in Capricorn, 10th House
# Venus 01°52'05" in Sagittarius, 9th House
# Mars 28°09'26" in Aquarius, 12th House
# Jupiter 25°15'48" in Aries, 2nd House
# Saturn 10°23'27" in Taurus, 2nd House, Retrograde
# Uranus 14°49'19" in Aquarius, 12th House
# Neptune 03°12'07" in Aquarius, 12th House
# Pluto 11°27'49" in Sagittarius, 9th House
# ...etc.
```

Add asteroid Ceres into the mix via the Config class:

```python
from immanuel import charts
from immanuel.const import chart


config = charts.Config()
config.objects.append(chart.CERES)

native = charts.Subject(
        date_time="2000-01-01 10:00",
        latitude="32n43",
        longitude="117w09"
    )

natal = charts.Natal(native, config=config)

for object in natal.objects.values():
    print(object)

# This now appears:
# Ceres 04°30'28" in Libra, 7th House
```

We can see much more data by serializing the chart's properties (or even the whole chart itself) to JSON. See  like this:

```python
import json

from immanuel import charts
from immanuel.const import chart


native = charts.Subject(
        date_time="2000-01-01 10:00",
        latitude="32n43",
        longitude="117w09"
    )

natal = charts.Natal(native)

print(json.dumps(natal.objects[chart.SUN], cls=charts.ToJSON, indent=4))
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
        "raw": 0.00022547880358658867,
        "formatted": "00\u00b000'01\"",
        "direction": "+",
        "degrees": 0,
        "minutes": 0,
        "seconds": 1
    },
    "longitude": {
        "raw": 280.62378011422516,
        "formatted": "280\u00b037'26\"",
        "direction": "+",
        "degrees": 280,
        "minutes": 37,
        "seconds": 26
    },
    "sign_longitude": {
        "raw": 10.623780114225156,
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
    "distance": 0.9833259252292994,
    "speed": 1.0194579732387614,
    "movement": {
        "direct": true,
        "stationary": false,
        "retrograde": false,
        "typical": true,
        "formatted": "Direct"
    },
    "declination": {
        "raw": -23.012365494740244,
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

## Tests

Tests are available via pytest. If you have cloned the repo, simply run pytest from the root:

```bash
python -m pytest
```

## Translations

Immanuel's output is currently available in the following locales / languages:

* **en_US:** (default) US English
* **pt_BR:** Brazilian Portuguese
* **es_ES:** Spanish
* **de_DE:** German

See [here](/docs/5-settings.md#chart-settings) for details on how to switch. The documentation itself is not currently available in other translations. To contribute in-software translations, see [here](/docs/7-contributions.md).

## AI Transparency

Immanuel is a passion project, and as such all of the code in this package - including the tests - is 100% hand-rolled by a human. AI is used to assist in planning, checking, and auditing the codebase and documentation, and Claude Code has write permission for the documentation only, in order to provide suggested updates and examples to help keep them in line with code changes.

## License

This program is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the [GNU Affero General Public License](LICENSE.md) for more details.

## Credits

* [@aloistr](https://github.com/aloistr) / Alois Treindl and Dieter Koch at Astrodienst for the mighty [Swiss Ephemeris](https://github.com/aloistr/swisseph)
* [@astrorigin](https://github.com/astrorigin) / Stanislas Marquis for the OG Python port [pyswisseph](https://github.com/astrorigin/pyswisseph)
* [@sailorfe](https://github.com/sailorfe) for its subsqeuent rescue and revival at [pysweph](https://github.com/sailorfe/pysweph)
* [@flatangle](https://github.com/flatangle) / João Ventura for the incredibly detailed [flatlib](https://github.com/flatangle/flatlib) which first inspired the development of this package
* [@nodbr](https://github.com/nodbr) / Nathan Octavio who suggested translations, and who translated Immanuel into both Brazilian Portuguese and Spanish
* [@cosmosandapi](https://github.com/cosmosandapi) who provided the German translation

## Contact

Please post any issues, feature requests, PRs etc. on GitHub.
