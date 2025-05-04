# Returned Data

Although you have some control over what data is returned for each chart type (more about that in the [Settings](5-settings.md#chart_data) section), here we'll take a look at the default properties returned for our example natal chart.

## JSON Output

The best way to explore a chart's properties is by looking at their JSON output, since this most accurately reflects each property's internal class structure. The following output is available via the `ToJSON` serializer class mentioned in the [Examples](3-examples.md#json) section.

### `natal.native`

#### object

The chart native, based on the date and coordinates you will have passed in when creating the chart.

```json
{
    "date_time": {
        "datetime": "2000-01-01 10:00:00-08:00",
        "timezone": "America/Los_Angeles",
        "ambiguous": false,
        "julian": 2451545.25,
        "deltat": 0.0007387629899254968,
        "sidereal_time": "16:54:13"
    },
    "coordinates": {
        "latitude": {
            "raw": 32.71666666666667,
            "formatted": "32N43.0",
            "direction": "+",
            "degrees": 32,
            "minutes": 43,
            "seconds": 0
        },
        "longitude": {
            "raw": -117.15,
            "formatted": "117W9.0",
            "direction": "-",
            "degrees": 117,
            "minutes": 9,
            "seconds": 0
        }
    }
}
```

The `date_time` structure is consistent for all dates returned by Immanuel's natal charts, and the `latitude` and `longitude` are similarly consistent for all angles returned.

Note that `ambiguous` is set to `true` when a time during the daylight savings switchover is passed without passing `time_is_dst` as discussed in the [Examples](3-examples.md#json) section. For instance, `2023-11-05 01:30` on the USA's West Coast could be either PDT or PST. By specifying `time_is_dst` when constructing the chart's subject, `ambiguous` will be `false`.

### `natal.house_system`

#### string

A string specifying which system was used to generate the houses in this chart. To see how to change the house system, see the [Settings](5-settings.md#house_system) section.

```
"Placidus"
```

### `natal.shape`

#### string

The overall chart shape formed by the planets. To change which chart objects this calculation includes and what orb it uses, see the [Settings](5-settings.md#chart_shape_orb) section.

```
"Bowl"
```

### `natal.diurnal`

#### boolean

Whether this is a daytime chart.

```
true
```

### `natal.moon_phase`

#### object

Contains the eight main moon phases as booleans, and a formatted string of the current phase.

```json
{
    "new_moon": false,
    "waxing_crescent": false,
    "first_quarter": false,
    "waxing_gibbous": false,
    "full_moon": false,
    "disseminating": false,
    "third_quarter": true,
    "balsamic": false,
    "formatted": "Third Quarter"
}
```

### `natal.objects`

#### dict

The core of any chart, the `objects` property is a dict of Python objects representing all of the chart's planets, points, primary angles, asteroids, fixed stars etc. Although the various object types have a slightly different structure, they will largely be like the following example:

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

Some differences between object types include:

* Only planets get dignities & a score.
* Only the traditional seven planets get an `in_sect` boolean.
* Houses, primary angles, and fixed stars do not have `out_of_bounds` or `movement` (retrograde / stationary / direct).
* Houses alone have a `size` measured in degrees.

All angles in chart have the same standard data structure. Certain properties also have a standard "booleans + formatted" structure, like the previous `moon_phases` example, and the `dignities` above.

You might have noticed that chart objects and their types all have a numerical index. More on these later in [the Object Indexing section](#object-indexing), but for now just be aware that Immanuel internally references planets, houses, asteroids etc. by numerical indices, and the `objects` property is keyed by them.

### `natal.houses`

#### dict

A dict of Python objects keyed by index. Each house will look something like this:

```json
{
    "index": 2000001,
    "number": 1,
    "name": "1st House",
    "type": {
        "index": 2000000,
        "name": "House"
    },
    "longitude": {
        "raw": 335.61047303445594,
        "formatted": "335\u00b036'38\"",
        "direction": "+",
        "degrees": 335,
        "minutes": 36,
        "seconds": 38
    },
    "sign_longitude": {
        "raw": 5.610473034455936,
        "formatted": "05\u00b036'38\"",
        "direction": "+",
        "degrees": 5,
        "minutes": 36,
        "seconds": 38
    },
    "sign": {
        "number": 12,
        "name": "Pisces",
        "element": "Water",
        "modality": "Mutable"
    },
    "decan": {
        "number": 1,
        "name": "1st Decan"
    },
    "speed": 516.3767707094903,
    "declination": {
        "raw": -9.453470857404115,
        "formatted": "-09\u00b027'12\"",
        "direction": "-",
        "degrees": 9,
        "minutes": 27,
        "seconds": 12
    },
    "size": 42.38404742743842
}
```

As you can see, this is similar to the Sun's data above, only a little simpler. Again, each house has its own unique numerical index.

### `natal.aspects`

#### dict

A dict keyed by the indices of all chart objects that have aspects. Each entry is a dict of Python objects, keyed by the indices of aspecting chart objects. If this sounds confusing, this is what the JSON structure would look like with all the actual aspect data removed:

```json
{
    "3000001": {
        "4000005": <aspect object>
    },
    "3000003": {
        "6000007": <aspect object>,
        "4000010": <aspect object>,
        "5000001": <aspect object>
    },
    "6000003": {
        "4000004": <aspect object>
    },
    "6000004": {
        "4000004": <aspect object>,
        "4000009": <aspect object>
    },
    "6000009": {
        "4000001": <aspect object>,
        "4000007": <aspect object>
    },
    "6000007": {
        "3000003": <aspect object>,
        "4000010": <aspect object>
    },
    "4000001": {
        "6000009": <aspect object>,
        "4000002": <aspect object>,
        "4000003": <aspect object>,
        "4000007": <aspect object>
    },
    "4000002": {
        "4000001": <aspect object>,
        "4000007": <aspect object>,
        "4000008": <aspect object>
    },
    "4000003": {
        "4000001": <aspect object>,
        "4000005": <aspect object>,
        "4000006": <aspect object>,
        "4000007": <aspect object>
    },
    "4000004": {
        "6000003": <aspect object>,
        "6000004": <aspect object>,
        "4000005": <aspect object>,
        "4000009": <aspect object>,
        "4000010": <aspect object>
    },
    "4000005": {
        "3000001": <aspect object>,
        "4000003": <aspect object>,
        "4000004": <aspect object>,
        "4000006": <aspect object>
    },
    "4000006": {
        "4000003": <aspect object>,
        "4000005": <aspect object>,
        "4000009": <aspect object>
    },
    "4000007": {
        "6000009": <aspect object>,
        "4000001": <aspect object>,
        "4000002": <aspect object>,
        "4000003": <aspect object>,
        "4000008": <aspect object>,
        "4000009": <aspect object>,
        "4000010": <aspect object>,
        "5000001": <aspect object>
    },
    "4000008": {
        "4000002": <aspect object>,
        "4000007": <aspect object>,
        "4000010": <aspect object>,
        "5000001": <aspect object>
    },
    "4000009": {
        "6000004": <aspect object>,
        "4000004": <aspect object>,
        "4000006": <aspect object>,
        "4000007": <aspect object>
    },
    "4000010": {
        "3000003": <aspect object>,
        "6000007": <aspect object>,
        "4000004": <aspect object>,
        "4000007": <aspect object>,
        "4000008": <aspect object>,
        "5000001": <aspect object>
    },
    "5000001": {
        "3000003": <aspect object>,
        "4000007": <aspect object>,
        "4000008": <aspect object>,
        "4000010": <aspect object>
    }
}
```

Each aspect object contains data about the aspect. For example, if we look for the Sun's index `4000001` we see its entry is a dict of four aspects - one of which is to index `4000002`, which is the Moon. Likewise the Moon's entry contains the same aspect to the Sun. Let's manually inspect this aspect object:

```python
print(natal.aspects[4000001][4000002])
```

Will display as:

```
Moon Sun Sextile within -05°42'03" (Separative, Associate)
```

You can of course also serialize this object into JSON for a deeper look:

```python
print(json.dumps(natal.aspects[4000001][4000002], cls=ToJSON, indent=4))
```

Which gives us this data:

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

The active object is the Moon, index `4000002`, while the passive is the Sun, index `4000001`. This is of course to be expected since the Moon consistently travels faster than the sun. The `orb` property is the maximum orb allowed for this aspect as specified in the settings (this particular one defaulting to 6.0°) whereas the `difference` property contains the actual orb of this specific aspect - in this case, -5°42'03".

### `natal.weightings`

#### dict

A dict containing three entries, which are also dicts. Each one contains a breakdown of which chart objects are in various categories based on their sign and house positions in the chart:

* `elements`: which elements the objects belongs to based on their sign.
* `modalities`: which modalities the objects belongs to based on their sign.
* `quadrants`: which objects belong to which four primary quadrants formed by the houses.

Each of the three dicts is keyed by category, and each category contains an array of indices to represent the object within that category. In the case of our natal chart:

```json
{
    "elements": {
        "fire": [
            3000003,
            6000003,
            6000007,
            4000004,
            4000006,
            4000010,
            5000001
        ],
        "earth": [
            3000002,
            6000005,
            6000009,
            4000001,
            4000003,
            4000007
        ],
        "air": [
            3000004,
            6000004,
            4000005,
            4000008,
            4000009
        ],
        "water": [
            3000001,
            4000002
        ]
    },
    "modalities": {
        "cardinal": [
            6000009,
            4000001,
            4000003,
            4000006
        ],
        "fixed": [
            6000003,
            6000004,
            4000002,
            4000005,
            4000007,
            4000008,
            4000009
        ],
        "mutable": [
            3000001,
            3000002,
            3000003,
            3000004,
            6000005,
            6000007,
            4000004,
            4000010,
            5000001
        ]
    },
    "quadrants": {
        "first": [
            3000001,
            4000006,
            4000007
        ],
        "second": [
            3000004,
            6000003
        ],
        "third": [
            3000002,
            6000005,
            6000007,
            4000002,
            4000004,
            4000010,
            5000001
        ],
        "fourth": [
            3000003,
            6000004,
            6000009,
            4000001,
            4000003,
            4000005,
            4000008,
            4000009
        ]
    }
}
```

The human-readable output simply provides a total for each category:

```python
print(natal.weightings['elements'])
```

Will output:

```
Fire: 7, Earth: 6, Air: 5, Water: 2
```

## Boolean + Formatted

When outputting JSON-serialized properties or charts, you will notice that some are returned as simple data and others are returned as an object containing each state as a boolean, plus a human-readable `formatted` property. This distinction was made mainly with front-end development in mind, where a user-facing application powered by Immanuel might need to quickly determine the state of something in order to display some kind of indicator.

For example, if a chart needs to show a full moon symbol when the chart's moon is full, then it can check the `moon_phase.full_moon` property rather than check a returned string for "Full". It can also provide its own mapping to more localized text if needed. Similarly with a chart object's dignity state, if certain dignities need to be quickly determined (eg. exaltation or detriment).

A house system or chart shape, on the other hand, will always simply be information and is very unlikely to be needed as actual data to perform any kind of calculation - they are instead best suited to being passed straight to the user.

## Other Chart Types

So far we have seen what gets returned from a simple natal chart. Other chart types return extra data, but since they are of the same types and formats as what we have already covered, here is a brief overview of what they are.

### Solar Return

| Property | Type | Description |
|---|---|---|
| solar_return_year | int | The year passed to the chart class constructor. |
| solar_return_date_time | object | The calculated solar return date for the passed year. |

### Progressed

| Property | Type | Description |
|---|---|---|
| progression_date_time | object | Reflects the date passed to the chart class constructor to calculate secondary progressions. |
| progressed_date_time | object | The calculated progressed date. |
| progression_method | string | Which of the supported methods was used. |

### Composite

| Property | Type | Description |
|---|---|---|
| partner | object | Based on the partner's `Subject` instance passed to the chart class constructor. |

## Object Indexing

All chart objects have an index. Immanuel maintains internal numerical indices for all the main planets, points, and popular asteroids that it supports out of the box, and provides constants for them in the `const.chart` submodule. As seen above, the `objects`, `aspects` and `weightings` properties of a chart especially rely on object indices to key their values.

Too see an example of using an object's index, we could import our constants and print out the Sun from our natal chart like this:

```python
from immanuel import charts
from immanuel.const import chart


native = charts.Subject('2000-01-01 10:00', '32n43', '117w09')
natal = charts.Natal(native)
# chart.SUN = 4000001
print(natal.objects[chart.SUN])
```

Which will output the Sun's information only:

```
Sun 10°37'26" in Capricorn, 11th House, Direct
```

Or to make the aspect code from earlier a little easier to read:

```python
# chart.SUN = 4000001, chart.MOON = 4000002
print(natal.aspects[chart.SUN][chart.MOON])
```

Which will still happily output:

```
Moon Sun Sextile within -05°42'03" (Separative, Associate)
```

You are free to use the actual numerical index for these objects, but of course `chart.SUN` is easier to work with than  `4000001` if your code ever does need to get this specific.

Immanuel indexes chart objects numerically rather than by name for two main reasons:

* Avoid name conflicts (eg. the four Liliths).
* Allow external objects to be easily added from your own extra ephemeris files by their default index.

To demonstrate, asteroid Lilith is number 1181 as designated by the International Astronomical Union. This is the number of the ephemeris file you would need for Immanuel to include it, and on astro.com this is the number you would type into the "Manual entry" box under "Additional objects" to include the asteroid in your chart.

Once you have the correct ephemeris file and have pointed Immanuel at it, you only need to add the number `1181` to the requested chart objects in Immanuel's settings for the asteroid object to be returned with an index of `1181` in the `objects` property (see the [Settings](5-settings.md#external-objects) section for details on how to do this). Anywhere else this index appears in the chart's data can then be cross-referenced with its entry in `objects` to retrieve Lilith's information.

Fixed stars (which are included without you having to bring your own ephemeris file) are an exception as they are indexed by their name, which will be a string (eg. `Antares`) rather than a number. Any object whose index is a string will be assumed to be a fixed star.

---

1. [Overview](1-overview.md)
2. [Installation](2-installation.md)
3. [Examples](3-examples.md)
4. Returned Data
5. [Settings](5-settings.md)
6. [Submodules](6-submodules.md)
7. [Contributions](7-contributions.md)
