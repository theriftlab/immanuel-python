# Settings

Immanuel has two tiers of settings:

* **Per-chart config** via the `ChartConfig` class. Sensible defaults have been set out of the box, such as which chart objects to include, the preferred house system, aspect rules and orbs, dignity scores, Part of Fortune calculation etc. Many of the defaults are set to match those of astro.com but are easily overridden to your liking. Any of the available locales can be set here too. The `ChartConfig` instance is then passed to a chart instance, which means different charts can use completely different configs.
* **Global per-process settings** live in the `settings` module itself as plain functions. These are per-process rather than per-chart, and currently configure only the ephemeris file paths. These settings will apply to every chart regardless of which `ChartConfig` it was given.

## Quick Example

To specify a different house system and MC progression method:

```python
from immanuel import charts
from immanuel.const import calc, chart
from immanuel.settings import ChartConfig


config = ChartConfig()
config.house_system = chart.CAMPANUS

native = charts.Subject("2000-01-01 10:00", "32n43", "117w09")

# natal.houses will use Campanus.
natal = charts.Natal(native, config=config)

config.mc_progression_method = calc.DAILY_HOUSES

# progressed.houses will also use Campanus,
# and its progression method will be Daily Houses.
progressed = charts.Progressed(native, "2025-06-20 17:00", config=config)
```

Every chart class takes the same optional `config` keyword argument.

## The ChartConfig Class

A `ChartConfig` instance is a simple object with attributes corresponding to the settings documented below. For example:

```python
config = ChartConfig()
config.house_system = chart.WHOLE_SIGN
config.objects.append(chart.CERES)
config.dignity_scores[dignities.EXALTED] = 5
```

### Charts take a snapshot

When a chart is created it deep-copies the config it was given, so later changes to that config will not retroactively change any charts you have already generated:

```python
config = ChartConfig()
config.house_system = chart.PLACIDUS
placidus_natal = charts.Natal(native, config=config)

config.house_system = chart.CAMPANUS
campanus_natal = charts.Natal(native, config=config)

# placidus_natal still uses Placidus.
```

This also means one config can safely be shared between as many charts as you like.

### Copying a config

`ChartConfig.copy()` returns a deep copy of itself, which is handy when you want minor variations without having to repeat yourself:

```python
base = ChartConfig()
base.house_system = chart.KOCH

whole_sign = base.copy()
whole_sign.house_system = chart.WHOLE_SIGN
```

## Cascading Settings

Some settings cascade into each other by default - for example, the `aspect_rules` setting (described later) is a dict containing each chart object's rules for which aspects it can initiate and receive. Each of the planets' rules is inherited from another setting, `planet_aspect_rule`, which is a dict specifying `initiate` and `receive` entries, both of which default to yet another setting, `aspects`, which is simply a list of all aspects being calculated for this chart.

This means changing the `aspects` setting to your own list will cascade that new list down to `planet_aspect_rule`, which in turn will cascade down to the planets in `aspect_rules`:

```python
config = ChartConfig()
config.aspects = [calc.CONJUNCTION, calc.TRINE]

config.planet_aspect_rule["initiate"]    # [0.0, 120.0]
config.aspect_rules[chart.SUN]["initiate"]    # [0.0, 120.0]
```

In-place changes cascade just as well as assignment:

```python
config.aspects.remove(calc.CONJUNCTION)
config.aspect_rules[chart.SUN]["initiate"]    # [120.0]
```

The cascade runs in one direction only, through these chains:

| Setting | Cascades into |
| --- | --- |
| `aspects` | `default_aspect_rule`, `planet_aspect_rule`, `point_aspect_rule`, and therefore `aspect_rules` |
| `planet_aspect_rule` | `aspect_rules` entries for the ten planets |
| `point_aspect_rule` | `aspect_rules` entries for the calculated points and the four main angles |
| `planet_orbs` | `orbs` entries for the ten planets and the four main angles |
| `point_orbs` | `orbs` entries for the calculated points |

### Assigning to a cascading setting

`planet_aspect_rule`, `point_aspect_rule`, `planet_orbs`, and `point_orbs` are *merged* when assigned a new dict, rather than replaced, and it is only the keys you actually pass in the new dict that stop inheriting. Everything else carries on cascading:

```python
config = ChartConfig()
config.planet_aspect_rule = {"initiate": [calc.SQUARE]}

# "initiate" is now locked to your list...
config.planet_aspect_rule["initiate"]    # [90.0]

# ...but "receive" still follows the aspects setting.
config.aspects = [calc.SEXTILE]
config.planet_aspect_rule["receive"]    # [60.0]
```

Assigning to `aspects` replaces its contents in place, so it stays connected to everything downstream. Reassigning it as often as you like will not break the cascade.

### Fallbacks

Not every chart object appears in `aspect_rules` and `orbs` by default - asteroids (including Chiron), eclipses, fixed stars, the ARMC, and any external objects you add are all absent. Aspect calculation falls back in this order:

| Failure | Fallback |
| --- | --- |
| Object has no `aspect_rules` entry | `default_aspect_rule` |
| Object has no per-aspect `orbs` map | `planet_orbs` |
| Object's per-aspect orb map is missing an aspect | `default_orb` |

## Chart Settings

These are all attributes of the `ChartConfig` class. Taking a look through the defaults in `settings.py` and the `const` files will give you a more detailed idea.

### `locale`

A chart's output can be translated by setting `locale` on its `ChartConfig`:

```python
from immanuel import charts
from immanuel.const import chart
from immanuel.settings import ChartConfig


config = ChartConfig()
config.locale = "pt_BR"

native = charts.Subject("2000-01-01 10:00", "32n43", "117w09")
natal = charts.Natal(native, config=config)

print(natal.objects[chart.SUN])
# Sol 10°37'26" em Capricórnio, Casa 11
```

Available locales:

* `pt_BR` - Brazilian Portuguese
* `es_ES` - Spanish
* `de_DE` - German

If the full locale has no translation file, Immanuel falls back to the parent language (eg. `pt_BR` falls back to `pt`), and if that fails too it silently reverts to untranslated English rather than raising an error. Passing `None` returns output to untranslated English.

### `chart_data`

A dict which specifies what top-level data each chart type should contain. The values are constants from `const.data` and line up with the chart class property names described in the [Returned Data](4-data.md) section.

The defaults specify the *maximum* amount of available data for each chart type - the only change you can reasonably make is to remove any properties you do not wish to include. Adding data that does not belong to a chart type (eg. adding `data.SOLAR_RETURN_YEAR` to a natal chart) is harmless but has no effect, as the chart classes simply ignore anything they have no method for.

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

To trim a chart down to just its objects, for example:

```python
config = ChartConfig()
config.chart_data[chart.NATAL] = [data.NATIVE, data.OBJECTS]
```

The chart's `type` property is always present and is not affected by this setting.

### `angle_precision`

Rounding for formatted angles. This only applies to stringified object output and to the `formatted` key of any angle attributes - the `raw` value is always the full-precision float. Available options:

| Option | Example output |
| --- | --- |
| `calc.SECOND` | `Sun 10°37'26" in Capricorn, 11th House` |
| `calc.MINUTE` | `Sun 10°37' in Capricorn, 11th House` |
| `calc.DEGREE` | `Sun 11° in Capricorn, 11th House` |

Default: `calc.SECOND`

### `output_typical_object_motion`

A boolean determining whether the stringified output of a chart object should always state its motion (retrograde, direct etc.) even when that motion is typical for the object. With the default `False`, a retrograde Saturn is printed as `Saturn 10°23'27" in Taurus, 2nd House, Retrograde` while a direct Sun is simply `Sun 10°37'26" in Capricorn, 11th House`. Set it to `True` and the Sun becomes `Sun 10°37'26" in Capricorn, 11th House, Direct`.

This only affects the human-readable string - the `movement` property is returned either way.

Default: `False`

### `default_latitude`

The latitude to use for a `Transits` chart when none is passed to its constructor.

Default: `51.4779` (the GMT prime meridian in Greenwich, UK)

### `default_longitude`

The longitude to use for a `Transits` chart when none is passed to its constructor.

Default: `-0.0015`

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

The `*_ON_FIRST` systems are equal-house systems with the first house cusp on the chosen planet. The main angles and the vertex are still calculated by Placidus in this case, so the Ascendant won't line up with the first house cusp.

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
config.objects.append("Antares")
```

Extra objects from external ephemeris files can also be added to this list by their number. See the [External Objects](#external-objects) section below for details how.

Anything else will raise a `ValueError` when the chart is generated.

### `chart_shape_objects`

A list of which chart objects should be included in the calculations for determining a chart's shape. Default:

```python
[
    chart.SUN, chart.MOON, chart.MERCURY, chart.VENUS, chart.MARS,
    chart.JUPITER, chart.SATURN, chart.URANUS, chart.NEPTUNE, chart.PLUTO,
]
```

All chart objects in the previous section are available here too.

### `chart_shape_orb`

The orb used when checking various gap sizes between objects to calculate the chart shape.

Default: `5.0` degrees

### `aspects`

A list of which aspects to calculate and include in the chart. This setting cascades into the aspect rules described below, and has the final say over which aspects are actually calculated, regardless of what is included in the rules. Default:

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

You may add your own aspects here - simply `append()` a `float` value that defines the aspect's angle. Then, in order for the chart to generate successfully, you will need to supply a string for the new aspect's name under `aspect_names`.

### `aspect_names`

The names of any custom aspects you might have added, keyed byt the aspect's angle `float`:

```python
from immanuel import charts
from immanuel.const import chart
from immanuel.settings import ChartConfig


new_aspect = 54.3   # add a weird aspect

config = ChartConfig()
config.aspects.append(new_aspect)
config.aspect_names[new_aspect] = "Wrongle"

native = charts.Subject("2000-01-01 10:00", "32n43", "117w09")
natal = charts.Natal(native, config=config)

for aspect in natal.aspects[chart.MOON].values():
    print(aspect)

# Moon Part of Fortune Wrongle within 00°41'12" (Applicative, Associate)
# ...
```

### `default_aspect_rule`

A dict which specifies a chart object's default aspect behavior. If a chart object has no entry in `aspect_rules` (described below) then Immanuel falls back to this setting. It has two entries:

| Key | Value |
| --- | --- |
| `initiate` | List of aspects a chart object can create when it is the active body. |
| `receive` | List of aspects a chart object can receive when it is the passive body. |

Default:

```python
{
    "initiate": self.aspects,
    "receive": self.aspects,
}
```

That is, both of these default to the list of all the aspects being calculated for this chart, and will inherit any changes made to it. Note that unlike the two rules below, assigning to this setting replaces it outright rather than merging.

### `planet_aspect_rule`

A dict of aspect rules, as above, which is inherited by the planets' entries in `aspect_rules`. Default:

```python
{
    "initiate": self.aspects,
    "receive": self.aspects,
}
```

### `point_aspect_rule`

A dict of aspect rules, as above, which is inherited by the calculated points' and main angles' entries in `aspect_rules`. Default:

```python
{
    "initiate": [calc.CONJUNCTION],
    "receive": self.aspects,
}
```

That is, points and angles can only initiate a conjunction by default, but can receive anything.

### `aspect_rules`

A dict of aspect rule dicts like those above, keyed by chart object index. This sets which specific chart objects have which rules. Any object without an entry here - asteroids, eclipses, fixed stars, external objects - falls back to `default_aspect_rule`.

By default the planets' entries inherit from `planet_aspect_rule`, while the points' and angles' entries inherit from `point_aspect_rule`.

Default:

```python
{
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

    chart.ASC: self.point_aspect_rule,
    chart.DESC: self.point_aspect_rule,
    chart.MC: self.point_aspect_rule,
    chart.IC: self.point_aspect_rule,

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

Remember to assign per-key rather than replacing the whole dict - see [Cascading Settings](#cascading-settings) above.

### `default_orb`

A numeric value of the default orb to fall back on when an object's orb mapping is empty.

Default: `1.0` degree

### `exact_orb`

A numeric value of the orb within which an aspect can be considered "exact".

Default: `0.3` degrees

### `orb_calculation`

How an aspect's orb is calculated when two objects have different orbs for this aspect.

| Option | Description |
| --- | --- |
| `calc.MEAN` | Takes the average of both orbs. |
| `calc.MAX` | Takes the maximum orb. |

Default: `calc.MEAN`

### `planet_orbs`

A dict which specifies orbs for each aspect type, inherited by the planets' and main angles' entries in `orbs`. Default:

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

This is also the fallback for any object with no entry in `orbs` at all.

### `point_orbs`

A dict which specifies orbs for each aspect type, inherited by the calculated points' entries in `orbs`. Default:

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

A dict of orb dicts like those above, keyed by chart object index. This sets which specific chart objects have which orbs for each aspect.

Note that the four main angles take their orbs from `planet_orbs` even though they take their aspect rules from `point_aspect_rule`.

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

### `mc_progression_method`

Which of the three available methods to use to progress the MC in a progressed chart.

| Method | Astro.com Equivalent | Description |
| --- | --- | --- |
| `calc.NAIBOD` | ARMC 1 Naibod/prog.day | Advances the ARMC by the Sun's mean daily motion multiplied by the number of days between the natal and progressed date. |
| `calc.SOLAR_ARC` | MC from solar arc | ARMC is calculated by advancing the MC by the same distance the Sun has traveled between the natal and progressed date. |
| `calc.DAILY_HOUSES` | ARMC 361°/prog.day | Calculates where the ARMC would be on the progressed date. |

Default: `calc.NAIBOD`

### `part_formula`

Which formula to use when calculating the Part of Fortune / Spirit / Eros.

| Option | Description |
| --- | --- |
| `calc.DAY_FORMULA` | Always use the day formula `asc + moon - sun` |
| `calc.NIGHT_FORMULA` | Always use the night formula `asc + sun - moon` |
| `calc.DAY_NIGHT_FORMULA` | Use whichever of the above is appropriate for the current chart's time of day. |

Default: `calc.DAY_NIGHT_FORMULA`

### `rulerships`

Rules for the planets' rulerships. You can see these in the `const.dignities` submodule.

| Option | Description |
| --- | --- |
| `dignities.MODERN_RULERSHIPS` | Modern rulerships which include all ten planets. |
| `dignities.TRADITIONAL_RULERSHIPS` | Traditional rulerships which only include the first seven planets. |

Default: `dignities.MODERN_RULERSHIPS`

### `triplicities`

Rules for the planets' triplicity rulerships. You can see these in the `const.dignities` submodule.

| Option | Description |
| --- | --- |
| `dignities.PTOLEMAIC_TRIPLICITIES` | Ptolemy's second-century table of triplicity rulers, where each sign has day, night, and participatory rulers. |
| `dignities.LILLEAN_TRIPLICITIES` | William Lilly's 17th-century simplification where each sign only has a day and a night ruler. |
| `dignities.DOROTHEAN_TRIPLICITIES` | Dorotheus's first-century table, which also has day, night, and participatory rulers, only slightly different from Ptolemy's. |

Default: `dignities.PTOLEMAIC_TRIPLICITIES`

### `terms`

Rules for the planets' term rulerships. You can see these in the `const.dignities` submodule.

| Option | Description |
| --- | --- |
| `dignities.PTOLEMAIC_TERMS` | Ptolemy's terms as described by William Lilly. |
| `dignities.EGYPTIAN_TERMS` | Egyptian terms as described in Ptolemy's Tetrabiblos. |

Default: `dignities.EGYPTIAN_TERMS`

### `include_participatory_triplicities`

A boolean to determine whether a participatory ruler counts as a triplicity ruler, or whether to only count day and night rulers. This will affect a planet's dignity state and score.

Default: `False`

### `include_mutual_receptions`

A boolean to determine whether a planet being in any of the various mutual receptions will cancel its peregrine state. This will affect a planet's dignity state and score.

Default: `True`

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

Only the dignities listed here contribute to a planet's score, so removing an entry here is equivalent to that dignity state contributing zero to the score.

One further dignity is calculated but deliberately left unscored: `dignities.IN_RULERSHIP_ELEMENT`, which is true when a planet occupies an element it rules. By default this only serves to cancel an otherwise peregrine planet, but adding it to this dict will give it a score of its own:

```python
config.dignity_scores[dignities.IN_RULERSHIP_ELEMENT] = 2
```

## Global Settings

The remaining settings take the form of functions in the `settings` module rather than attributes of `ChartConfig`. They apply per-process, to every chart, regardless of the config the chart instance was given.

### `add_swe_filepath()`

Adds the passed file path to the list of directories to search for ephemeris files. If `True` is passed as the 2nd argument, the passed path will replace the default one.

| Argument | Type | Purpose |
| --- | --- | ---|
| path | `str` | Absolute file path to a directory containing Swiss Ephemeris files. |
| default | `bool` | Whether this path should be the default, replacing the location of Immanuel's bundled files. Defaults to `False`, which simply appends the new path to Immanuel's own. |

The next section contains an example of how to use this to get extra, non-bundled chart objects into your charts.

### `reset_swe_filepath()`

Simply resets the ephemeris search path back to the bundled default.


## External Objects

As well as the readily-available chart objects listed above in the `objects` setting, it is possible to point Immanuel to any outside ephemeris files you might want to include, and add those extra objects to your chart.

Details on where to find the various ephemeris files can be found on [the Swiss Ephemeris GitHub repo](https://github.com/aloistr/swisseph).

For example, to include asteroid Lilith (`1181`), download its ephemeris file `se01181s.se1` (currently available [here](https://www.dropbox.com/scl/fo/y3naz62gy6f6qfrhquu7u/h/all_ast/ast1?rlkey=ejltdhb262zglm7eo6yfj2940&dl=0)). Then you can use the `add_filepath()` function to point to its location, and add `1181` to your config's `objects` list:

```python
import json

from immanuel import charts, settings
from immanuel.settings import ChartConfig


settings.add_filepath("my/directory/path")

config = ChartConfig()
config.objects.append(1181)

native = charts.Subject("2000-01-01 10:00", "32n43", "117w09")
natal = charts.Natal(native, config=config)
print(json.dumps(natal.objects[1181], cls=charts.ToJSON, indent=4))
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
        "raw": 4.8185412257115665,
        "formatted": "04\u00b049'07\"",
        "direction": "+",
        "degrees": 4,
        "minutes": 49,
        "seconds": 7
    },
    "longitude": {
        "raw": 348.27965783420325,
        "formatted": "348\u00b016'47\"",
        "direction": "+",
        "degrees": 348,
        "minutes": 16,
        "seconds": 47
    },
    "sign_longitude": {
        "raw": 18.27965783420325,
        "formatted": "18\u00b016'47\"",
        "direction": "+",
        "degrees": 18,
        "minutes": 16,
        "seconds": 47
    },
    "sign": {
        "number": 12,
        "name": "Pisces",
        "element": "Water",
        "modality": "Mutable"
    },
    "decan": {
        "number": 2,
        "name": "2nd Decan"
    },
    "house": {
        "index": 2000001,
        "number": 1,
        "name": "1st House"
    },
    "distance": 2.4219215340974056,
    "speed": 0.41025966444735706,
    "movement": {
        "direct": true,
        "stationary": false,
        "retrograde": false,
        "typical": true,
        "formatted": "Direct"
    },
    "declination": {
        "raw": -0.1972070280539613,
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

If a requested object's file cannot be found, the underlying Swiss Ephemeris will raise a `swisseph.Error` naming the missing file and the paths it searched.

`add_filepath()` appends to the existing paths by default. Passing `True` as a second argument will instead set the passed path as the *only* path, replacing the bundled default:

```python
settings.add_filepath("my/directory/path", True)
```

Since external objects have no entries in the `aspect_rules` and `orbs` settings, they will use `default_aspect_rule` and `planet_orbs` when aspects are calculated. Add entries for their index if you want to treat them differently:

```python
config.orbs[1181] = config.point_orbs
```

---

1. [Overview](1-overview.md)
2. [Installation](2-installation.md)
3. [Examples](3-examples.md)
4. [Returned Data](4-data.md)
5. Settings
6. [Submodules](6-submodules.md)
7. [Contributions](7-contributions.md)
