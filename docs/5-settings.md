# Settings

The `setup` module contains a `settings` class for changing Immanuel's default settings. Sensible defaults have been set out of the box, such as which chart objects to include, the preferred house system, aspect rules and orbs, dignity scores, Part of Fortune calculation etc. Many of the defaults are set to match those of astro.com but are easily overridden with Immanuel's built-in constants. Once a setting is changed, it will be applied to all subsequent charts until changed again.

## Quick Example

To specify a different house system or MC progression method:

```python
from immanuel import charts
from immanuel.const import calc, chart
from immanuel.setup import settings


settings.house_system = chart.CAMPANUS

native = charts.Subject('2000-01-01 10:00', '32n43', '117w09')
# natal.houses will now use Campanus.
natal = charts.Natal(native)

settings.mc_progression_method = calc.DAILY_HOUSES

# progressed.houses will now use Campanus,
# and its progression method will be Daily Houses.
progressed = charts.Progressed(native, '2025-06-20 17:00')
```

Or, to set them at the same time:

```python
settings.set({
    'house_system': chart.CAMPANUS,
    'mc_progression_method': calc.DAILY_HOUSES,
})
```

## Cascading Settings

Some settings cascade into each other by default - for example, the `aspect_rules` setting (described later) is a dict containing each chart object's rules for which aspects it can initiate and receive. Each of the planets' rules are set to another setting, `planet_aspect_rule`, which is a dict specifying `initiate` and `receive` entries, both of which default to yet another setting, `aspects`, which is simply a list of all aspects being calculated for this chart.

This means that changing the `aspects` setting to your own list will cascade that new list down to `planet_aspect_rule` which in turn will cascade down to the planets in `aspect_rules`.

With all cascading settings, once you change the setting it will be "locked" and no longer inherit anything, but will still cascade downwards to be inherited. For example, changing the `planet_aspect_rule` setting alone will cause it to ignore `aspects` thereafter but it will still cascade down to `aspect_rules`.

Because of the code required under the hood to maintain the real-time nature of these cascading attributes, they are not subscriptable - eg. to change the aspect rules for just the ascendant to allow all aspects, this will silently fail, despite being intuitively correct:

```python
settings.aspect_rules[chart.ASC] = settings.default_aspect_rule
```

You will instead have to assign it as a dict which will automatically be merged into the current settings:

```python
settings.aspect_rules = {
    chart.ASC: settings.default_aspect_rule,
}
```

Now the `chart.ASC` rule is locked in - even changing `default_aspect_rule` will not change this setting - while the other `aspect_rules` entries still inherit their default cascading settings.

Note that if you *manually* merge a dict then this will essentially re-assign the settings to their current value and lock them in, so they will no longer inherit:

```python
# This updates chart.ASC but additionally reads ALL the other aspect_rules
# entries and then writes them back, locking them all in.
settings.aspect_rules |= {
    chart.ASC: settings.default_aspect_rule,
}
```

## Overview

There are many detailed customizations for chart data, especially for aspect rules. This section will provide you with an overview, but taking a look through the defaults in `setup.py` and the const files will give you a more detailed idea.

### `locale`

A string specifying the locale for all output on any subsequently-generated charts or chart subjects. Available options:

* `pt_BR` - Brazilian Portuguese
* `es_ES` - Spanish
* `de_DE` - German

Default: `None` (effectively `en_US`)

### `chart_data`

A dict which specifies what top-level data each chart type should contain. The values here are fairly self-explanatory as the constants line up with the chart class property names described in the [Returned Data](4-data.md) section.

The defaults specify the *maximum* amount of available data for each chart type - the only change you can reasonably make is to remove any properties you do not wish to include. Attempting to add data that does not belong (eg. adding `data.SOLAR_RETURN_DATE` to a natal chart) will not end well.

Defaults:

```python
{
    chart.NATAL: [
        data.NATIVE,
        data.HOUSE_SYSTEM,
        data.SHAPE,
        data.DIURNAL,
        data.MOON_PHASE,
        data.OBJECTS,
        data.HOUSES,
        data.ASPECTS,
        data.WEIGHTINGS,
    ],
    chart.SOLAR_RETURN: [
        data.NATIVE,
        data.SOLAR_RETURN_YEAR,
        data.SOLAR_RETURN_DATE_TIME,
        data.HOUSE_SYSTEM,
        data.SHAPE,
        data.DIURNAL,
        data.MOON_PHASE,
        data.OBJECTS,
        data.HOUSES,
        data.ASPECTS,
        data.WEIGHTINGS,
    ],
    chart.PROGRESSED: [
        data.NATIVE,
        data.PROGRESSION_DATE_TIME,
        data.PROGRESSED_DATE_TIME,
        data.PROGRESSION_METHOD,
        data.HOUSE_SYSTEM,
        data.SHAPE,
        data.DIURNAL,
        data.MOON_PHASE,
        data.OBJECTS,
        data.HOUSES,
        data.ASPECTS,
        data.WEIGHTINGS,
    ],
    chart.COMPOSITE: [
        data.NATIVE,
        data.PARTNER,
        data.HOUSE_SYSTEM,
        data.SHAPE,
        data.DIURNAL,
        data.MOON_PHASE,
        data.OBJECTS,
        data.HOUSES,
        data.ASPECTS,
        data.WEIGHTINGS,
    ],
    chart.TRANSITS: [
        data.NATIVE,
        data.HOUSE_SYSTEM,
        data.SHAPE,
        data.DIURNAL,
        data.MOON_PHASE,
        data.OBJECTS,
        data.HOUSES,
        data.ASPECTS,
        data.WEIGHTINGS,
    ],
}
```

### `angle_precision`

Rounding for formatted angles. This only applies to stringified object output and to the `formatted` key of any angle attributes. Available options:

* `calc.SECOND`
* `calc.MINUTE`
* `calc.DEGREE`

Default: `calc.SECOND`

### `house_system`

Which house system to use. Available options:

* `chart.ALCABITUS`
* `chart.AZIMUTHAL`
* `chart.CAMPANUS`
* `chart.EQUAL`
* `chart.KOCH`
* `chart.MERIDIAN`
* `chart.MORINUS`
* `chart.PLACIDUS`
* `chart.POLICH_PAGE`
* `chart.PORPHYRIUS`
* `chart.REGIOMONTANUS`
* `chart.VEHLOW_EQUAL`
* `chart.WHOLE_SIGN`
* `chart.SUN_ON_FIRST`
* `chart.MOON_ON_FIRST`
* `chart.MERCURY_ON_FIRST`
* `chart.VENUS_ON_FIRST`
* `chart.MARS_ON_FIRST`
* `chart.JUPITER_ON_FIRST`
* `chart.SATURN_ON_FIRST`
* `chart.URANUS_ON_FIRST`
* `chart.NEPTUNE_ON_FIRST`
* `chart.PLUTO_ON_FIRST`

Default: `chart.PLACIDUS`

### `objects`

A list of which chart objects should be included. Default:

```python
[
    chart.ASC, chart.DESC, chart.MC, chart.IC,
    chart.TRUE_NORTH_NODE, chart.TRUE_SOUTH_NODE,
    chart.VERTEX, chart.PART_OF_FORTUNE,
    chart.TRUE_LILITH,
    chart.SUN, chart.MOON, chart.MERCURY, chart.VENUS, chart.MARS,
    chart.JUPITER, chart.SATURN, chart.URANUS, chart.NEPTUNE, chart.PLUTO,
    chart.CHIRON,
]
```

Available options:

Angles:

* `chart.ASC`
* `chart.DESC`
* `chart.MC`
* `chart.IC`
* `chart.ARMC`

Planets:

* `chart.SUN`
* `chart.MOON`
* `chart.MERCURY`
* `chart.VENUS`
* `chart.MARS`
* `chart.JUPITER`
* `chart.SATURN`
* `chart.URANUS`
* `chart.NEPTUNE`
* `chart.PLUTO`

Major asteroids:

* `chart.CHIRON`
* `chart.PHOLUS`
* `chart.CERES`
* `chart.PALLAS`
* `chart.JUNO`
* `chart.VESTA`

Calculated points:

* `chart.NORTH_NODE`
* `chart.SOUTH_NODE`
* `chart.TRUE_NORTH_NODE`
* `chart.TRUE_SOUTH_NODE`
* `chart.VERTEX`
* `chart.LILITH`
* `chart.TRUE_LILITH`
* `chart.INTERPOLATED_LILITH`
* `chart.SYZYGY`
* `chart.PART_OF_FORTUNE`
* `chart.PART_OF_SPIRIT`
* `chart.PART_OF_EROS`

Pre & post-natal eclipses:

* `chart.PRE_NATAL_SOLAR_ECLIPSE`
* `chart.PRE_NATAL_LUNAR_ECLIPSE`
* `chart.POST_NATAL_SOLAR_ECLIPSE`
* `chart.POST_NATAL_LUNAR_ECLIPSE`

Fixed stars:

All fixed stars are available out of the box - simply add the name as a string to this list, eg.:

```python
settings.objects.append('Antares')
```

Extra objects from external ephemeris files can also be added to this list by their number. See the [External Objects](#external-objects) section below for details how.

### `chart_shape_objects`

A list of which chart objects should be included in the calculations for determining a chart's shape. Default:

```python
[
    chart.SUN, chart.MOON, chart.MERCURY, chart.VENUS, chart.MARS,
    chart.JUPITER, chart.SATURN, chart.URANUS, chart.NEPTUNE, chart.PLUTO,
]
```

All chart objects in the previous section are available here too.

### `aspects`

A list of which aspects to calculate. This setting will cascade into the other settings described below that rely on it. Default:

```python
[
    calc.CONJUNCTION, calc.OPPOSITION, calc.SQUARE, calc.TRINE, calc.SEXTILE,
    calc.QUINCUNX,
]
```

Available options:

| Option | Angle |
| --- | --- |
| `calc.CONJUNCTION` | 0.0° |
| `calc.OPPOSITION` | 180.0° |
| `calc.SQUARE` | 90.0° |
| `calc.TRINE` | 120.0° |
| `calc.SEXTILE` | 60.0° |
| `calc.SEPTILE` | 51.43° |
| `calc.SEMISQUARE` | 45.0° |
| `calc.SESQUISQUARE` | 135.0° |
| `calc.SEMISEXTILE` | 30.0° |
| `calc.QUINCUNX` | 150.0° |
| `calc.QUINTILE` | 72.0° |
| `calc.BIQUINTILE` | 144.0° |

### `default_aspect_rule`

A dict which specifies a chart object's default aspect behavior. If a chart object does not have specific rules assigned to it (described below) then Immanuel will fall back to this setting. It has two entries:

| Key | Value |
| --- | --- |
| `initiate` | List of aspects a chart object can create when it is the active body. |
| `receive` | List of aspects a chart object can receive when it is the passive body. |

Default:

```python
{
    'initiate': self.aspects,
    'receive': self.aspects,
}
```

That is, both of these default to the list of all the aspects being calculated for this chart, and will by default inherit any changes made to it.

### `planet_aspect_rule`

A dict of aspect rules, as above, which will be applied to planets only. Default:

```python
{
    'initiate': self.aspects,
    'receive': self.aspects,
}
```

As above, this will by default inherit any changes made to `aspects`.

### `point_aspect_rule`

A dict of aspect rules, as above, which will be applied to calculated points only - you can see which ones under the next heading. Default:

```python
{
    'initiate': (calc.CONJUNCTION,),
    'receive': self.aspects,
}
```

Similar to above, `receive` will by default inherit any changes made to `aspects`.

### `aspect_rules`

A dict of aspect rule dicts like those above, keyed by chart object index. This sets which specific chart objects have which rules, and any object not found in this dict will default to the `default_aspect_rule` rules described above.

By default this inherits any changes made to the above planet and point rules.

Default:

```python
{
    chart.ASC: self.point_aspect_rule,
    chart.DESC: self.point_aspect_rule,
    chart.MC: self.point_aspect_rule,
    chart.IC: self.point_aspect_rule,

    chart.SUN: self.planet_aspect_rule,
    chart.MOON: self.planet_aspect_rule,
    chart.MERCURY: self.planet_aspect_rule,
    chart.VENUS: self.planet_aspect_rule,
    chart.MARS: self.planet_aspect_rule,
    chart.JUPITER: self.planet_aspect_rule,
    chart.SATURN: self.planet_aspect_rule,
    chart.URANUS: self.planet_aspect_rule,
    chart.NEPTUNE: self.planet_aspect_rule,
    chart.PLUTO: self.planet_aspect_rule,

    chart.NORTH_NODE: self.point_aspect_rule,
    chart.SOUTH_NODE: self.point_aspect_rule,
    chart.TRUE_NORTH_NODE: self.point_aspect_rule,
    chart.TRUE_SOUTH_NODE: self.point_aspect_rule,
    chart.SYZYGY: self.point_aspect_rule,
    chart.PART_OF_FORTUNE: self.point_aspect_rule,
    chart.PART_OF_SPIRIT: self.point_aspect_rule,
    chart.PART_OF_EROS: self.point_aspect_rule,
    chart.VERTEX: self.point_aspect_rule,
    chart.LILITH: self.point_aspect_rule,
    chart.TRUE_LILITH: self.point_aspect_rule,
    chart.INTERPOLATED_LILITH: self.point_aspect_rule,
}
```

### `default_orb`

A numeric value of the default orb to fall back on when one hasn't been specified for the objects and aspect in question. Default `1.0` degree.

### `exact_orb`

A numeric value of the orb within which an aspect can be considered "exact". Default `0.3` degrees.

### `orb_calculation`

How an aspect's orb is calculated when two objects have different orbs for this aspect.

| Option | Description |
| --- | --- |
| `calc.MEAN` | Takes the average of both orbs. |
| `calc.MAX` | Takes the maximum orb. |

Default: `calc.MEAN`

### `planet_orbs`

A dict which specifies orbs for each aspect type, which will be applied to planets only. This will cascade down into the `orbs` setting described below. Default:

```python
{
    calc.CONJUNCTION: 10.0,
    calc.OPPOSITION: 10.0,
    calc.SQUARE: 10.0,
    calc.TRINE: 10.0,
    calc.SEXTILE: 6.0,
    calc.SEPTILE: 3.0,
    calc.SEMISQUARE: 3.0,
    calc.SESQUISQUARE: 3.0,
    calc.SEMISEXTILE: 3.0,
    calc.QUINCUNX: 3.0,
    calc.QUINTILE: 2.0,
    calc.BIQUINTILE: 2.0,
}
```

### `point_orbs`

A dict which specifies orbs for each aspect type, which will be applied to calculated points only. This will cascade down into the `orbs` setting described below. Default:

```python
{
    calc.CONJUNCTION: 0.0,
    calc.OPPOSITION: 0.0,
    calc.SQUARE: 0.0,
    calc.TRINE: 0.0,
    calc.SEXTILE: 0.0,
    calc.SEPTILE: 0.0,
    calc.SEMISQUARE: 0.0,
    calc.SESQUISQUARE: 0.0,
    calc.SEMISEXTILE: 0.0,
    calc.QUINCUNX: 0.0,
    calc.QUINTILE: 0.0,
    calc.BIQUINTILE: 0.0,
}
```

### `orbs`

A dict of orb dicts like those above, keyed by chart object index. This sets which specific chart objects have which orbs for each aspect, and any object not found in this dict will default to the `default_orb` value described above.

By default this inherits any changes made to the above planet and point orbs.

Default:

```python
{
    chart.ASC: self.planet_orbs,
    chart.DESC: self.planet_orbs,
    chart.MC: self.planet_orbs,
    chart.IC: self.planet_orbs,

    chart.SUN: self.planet_orbs,
    chart.MOON: self.planet_orbs,
    chart.MERCURY: self.planet_orbs,
    chart.VENUS: self.planet_orbs,
    chart.MARS: self.planet_orbs,
    chart.JUPITER: self.planet_orbs,
    chart.SATURN: self.planet_orbs,
    chart.URANUS: self.planet_orbs,
    chart.NEPTUNE: self.planet_orbs,
    chart.PLUTO: self.planet_orbs,

    chart.NORTH_NODE: self.point_orbs,
    chart.SOUTH_NODE: self.point_orbs,
    chart.TRUE_NORTH_NODE: self.point_orbs,
    chart.TRUE_SOUTH_NODE: self.point_orbs,
    chart.SYZYGY: self.point_orbs,
    chart.PART_OF_FORTUNE: self.point_orbs,
    chart.PART_OF_SPIRIT: self.point_orbs,
    chart.PART_OF_EROS: self.point_orbs,
    chart.VERTEX: self.point_orbs,
    chart.LILITH: self.point_orbs,
    chart.TRUE_LILITH: self.point_orbs,
    chart.INTERPOLATED_LILITH: self.point_orbs,
}
```

### `chart_shape_orb`

The orb used when checking various gap sizes between planets to calculate the chart shape. Default `5` degrees.

### `mc_progression_method`

Which of the three available methods to use to progress the MC in a progressed chart.

| Method | Astro.com Equivalent | Description |
| --- | --- | --- |
| `calc.NAIBOD` | ARMC 1 Naibod/prog.day | Advances the ARMC by the Sun's mean daily motion multiplied by the number of days between the natal and progressed date. |
| `calc.SOLAR_ARC` | MC from solar arc | ARMC is calculated by advancing the MC by the same distance the Sun has traveled between the natal and progressed date. |
| `calc.DAILY_HOUSES` | ARMC 361°/prog.day | Calculates where the ARMC would be on the progressed date. |

Default `calc.NAIBOD`.

### `part_formula`

Which formula to use when calculating the Part of Fortune / Spirit / Eros.

| Option | Description |
| --- | --- |
| `calc.DAY_FORMULA` | Always use the day formula `asc + moon - sun` |
| `calc.NIGHT_FORMULA` | Always use the night formula `asc + sun - moon` |
| `calc.DAY_NIGHT_FORMULA` | Use whichever of the above is appropriate for the current chart's time of day. |

Default `calc.DAY_NIGHT_FORMULA`.

### `rulerships`

Rules for the planets' rulerships. You can see these in the `const.dignities` submodule.

| Option | Description |
| --- | --- |
| `dignities.MODERN_RULERSHIPS` | Modern rulerships which include all ten planets. |
| `dignities.TRADITIONAL_RULERSHIPS` | Traditional rulerships which only include the first seven planets. |

Default `dignities.MODERN_RULERSHIPS`.

### `triplicities`

Rules for the planets' triplicity rulerships. You can see these in the `const.dignities` submodule.

| Option | Description |
| --- | --- |
| `dignities.PTOLEMAIC_TRIPLICITIES` | Ptolemy's second-century table of triplicity rulers, where each sign has day, night, and participatory rulers. |
| `dignities.LILLEAN_TRIPLICITIES` | William Lilly's 17th-century simplification where each sign only has a day and a night ruler. |
| `dignities.DOROTHEAN_TRIPLICITIES` | Dorotheus's first-century table, which also has day, night, and participatory rulers, only slightly different from Ptolemy's. |

Default `dignities.PTOLEMAIC_TRIPLICITIES`.

### `terms`

Rules for the planets' term rulerships. You can see these in the `const.dignities` submodule.

| Option | Description |
| --- | --- |
| `dignities.PTOLEMAIC_TERMS` | Ptolemy's terms as described by William Lilly. |
| `dignities.EGYPTIAN_TERMS` | Egyptian terms as described in Ptolemy's Tetrabiblos. |

Default `dignities.EGYPTIAN_TERMS`.

### `include_participatory_triplicities`

A boolean to determine whether a participatory ruler counts as a triplicity ruler, or whether to only count day and night rulers. This will affect a planet's dignity state and score.

Default `False`

### `include_mutual_receptions`

A boolean to determine whether a planet being in any of the various mutual receptions will cancel its peregrine state. This will affect a planet's dignity state and score.

Default `True`

### `dignity_scores`

A dict of dignities and the scores associated with them. These are based on [Astro Gold's scoring system](https://www.astrogold.io/AG-MacOS-Help/essential_dignities.html).

Default:

```python
{
    dignities.RULER: 5,
    dignities.EXALTED: 4,
    dignities.TRIPLICITY_RULER: 3,
    dignities.TERM_RULER: 2,
    dignities.FACE_RULER: 1,
    dignities.MUTUAL_RECEPTION_RULER: 5,
    dignities.MUTUAL_RECEPTION_EXALTED: 4,
    dignities.MUTUAL_RECEPTION_TRIPLICITY_RULER: 3,
    dignities.MUTUAL_RECEPTION_TERM_RULER: 2,
    dignities.MUTUAL_RECEPTION_FACE_RULER: 1,
    dignities.DETRIMENT: -5,
    dignities.FALL: -4,
    dignities.PEREGRINE: -5,
}
```

## External Objects

As well as the readily-available chart objects listed above in the `objects` setting, it is possible to point Immanuel to any outside ephemeris files you might want to include, and add those extra objects to your chart.

For example, to include asteroid Lilith (`1181`), download its ephemeris file `se01181s.se1` (currently available [here](https://www.dropbox.com/scl/fo/y3naz62gy6f6qfrhquu7u/h/all_ast/ast1?dl=0)). Then you can use the `add_filepath()` function to point to its location, and add `1181` to the `settings.objects` list:

```python
import json

from immanuel import charts
from immanuel.classes.serialize import ToJSON
from immanuel.setup import settings


settings.add_filepath('my/directory/path')
settings.objects.append(1181)

native = charts.Subject('2000-01-01 10:00', '32n43', '117w09')
natal = charts.Natal(native)
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

Congratulations - you have imported an external object into your chart.

If you want Immanuel to only use your own ephemeris files for everything, passing `True` as a second parameter to `add_filepath()` will set the passed path as the only path rather than adding it to the default one.

---

1. [Overview](1-overview.md)
2. [Installation](2-installation.md)
3. [Examples](3-examples.md)
4. [Returned Data](4-data.md)
5. Settings
6. [Submodules](6-submodules.md)
7. [Contributions](7-contributions.md)
