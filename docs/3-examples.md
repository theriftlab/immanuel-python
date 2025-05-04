# Examples

All the chart data generation happens in the chart classes in Immanuel's `charts` module. To start, you will need to create a chart subject via the Subject class - this essentially just encapsulates a date/time and coordinates.

The Subject class constructor takes a date/time either as a standard ISO format string (YYYY-MM-DD HH:MM:SS) or a native `datetime` object. Coordinates can be in either standard text format, decimal, or even a list / tuple of `[direction, degrees, minutes, seconds]`. All of these will yield the same result:

```python
from immanuel import charts


native = charts.Subject('2000-01-01 10:00', '32n43', '117w09')
native = charts.Subject('2000-01-01 10:00:00', "32°43'", "-117°09'")
native = charts.Subject(datetime.fromisoformat('2000-01-01 10:00:00'), '32.71667n', '117.15w')
native = charts.Subject(datetime(2000, 1, 1, 10, 0, 0), 32.71667, -117.15)
native = charts.Subject(datetime(year=2000, month=1, day=1, hour=10), ('+', 32, 43, 0), ['-', 117, 9, 0])
# Or if you prefer named arguments...
native = charts.Subject(
        date_time='2023-11-05 01:30',
        latitude='32n43',
        longitude='117w09',
        time_is_dst=True,
    )
```

The optional `time_is_dst` parameter is a boolean to clarify ambiguous times - for example 1:30am on a night when switching to US daylight savings could be in either the standard or the DST timezone. To specify which one, pass either `True` or `False` to this argument. For all other non-ambiguous times, `time_is_dst` can safely be omitted.

You may provide a string argument to the optional `timezone` parameter if you'd like to bypass the coordinate lookup. This will speed up chart generation and could potentially be more accurate if your own timezone data is more up to date than Immanuel's offline lookup.

There is also an optional `timezone_offset` parameter. This is a float which explicitly sets the UTC offset in hours for the location specified by the passed coordinates. While Immanuel will do its best to look up the correct timezone for the coordinates, it might not always be accurate, especially when boundaries or offsets have changed since the given birth date. This parameter can safely be ignored for most use cases.

To generate one of each type of supported chart, you could do the following:

```python
from immanuel import charts


native = charts.Subject('2000-01-01 10:00', '32n43', '117w09')
partner = charts.Subject('2001-06-21 18:30', '51n28.69', '0e0.1')

natal = charts.Natal(native)
solar_return = charts.SolarReturn(native, 2025)
progressed = charts.Progressed(native, '2025-06-20 17:00')
composite = charts.Composite(native, partner)
transits = charts.Transits('32n43', '117w09')
```

For the Transits chart, the time is always assumed to be the present. Coordinates are optional, and when omitted they will default to the location of the GMT prime meridian in Greenwich. Coordinates are only needed to calculate the houses and house-based chart objects (Part of Fortune, Vertex, etc.), so if you do not require these in your transits you can safely omit the coordinates and simply call `chart.Transits()`.

Synastry charts are not explicitly available as a distinct class, but since a synastry chart is essentially two charts layered on top of each other with aspects between them, you can use the `aspects_to` parameter - available in each chart class - to create a synastry. This takes another chart class instance as an argument, and builds the aspects of the containing instance to point to the planets/objects in the passed instance. For example:

```python
from immanuel import charts


native = charts.Subject('2000-01-01 10:00', '32n43', '117w09')
partner = charts.Subject('2001-06-21 18:30', '51n28.69', '0e0.1')

partner_chart = charts.Natal(partner)
native_chart = charts.Natal(native, aspects_to=partner_chart)
```

Now `native_chart`'s planets/objects will aspect `partner_chart`'s planets/objects instead of its own. This makes things very flexible - a synastry chart can be created as above, with two natal charts, or a natal+transits chart can be created by passing a transits chart into a natal chart. It might also be useful to pass transits into a progressed or composite chart. You could even pass a composite chart into another composite chart to view synastry aspects between them.

All chart instances additionally feature a `house_for()` method which takes a chart object as a parameter. This simply returns the index of the current chart's house where the passed chart object would appear. This can be useful in conjunction with the above functionality to see which houses a transiting planet is in, or which houses in your chart a partner's planets appear.

Similarly, the `Transits` chart class features an additional `houses_for_aspected` boolean parameter. This will give the transits chart the same houses as the `aspected_to` chart for easy transit tracking.

## Human-Readable

You can simply print out a chart's property to see human-readable data, eg.:

```python
print(f'Daytime: {natal.diurnal}')
print(f'Moon phase: {natal.moon_phase}\n')

for object in natal.objects.values():
    print(object)

print()

for index, aspects in natal.aspects.items():
    print(f'Aspects for {natal.objects[index].name}:')

    for aspect in aspects.values():
        print(f' - {aspect}')
```

The (abridged) output will look something like this:

```
Daytime: True
Moon phase: Third Quarter

Sun 10°37'26" in Capricorn, 11th House, Direct
Moon 16°19'29" in Scorpio, 8th House, Direct
... etc.

Aspects for Sun:
 - Sun Part of Fortune Conjunction within 00°41'15" (Applicative, Associate)
 - Moon Sun Sextile within -05°42'03" (Separative, Associate)
 - Mercury Sun Conjunction within 08°20'43" (Applicative, Associate)
 - Sun Saturn Trine within -00°13'59" (Exact, Associate)
Aspects for Moon:
 - Moon Sun Sextile within -05°42'03" (Separative, Associate)
 - Moon Saturn Opposition within -05°56'02" (Separative, Associate)
 - Moon Uranus Square within -01°30'10" (Separative, Associate)
... etc.
```

Many of the properties are nested, eg.:

```python
print(natal.native)
print(natal.native.coordinates)
print(natal.native.coordinates.latitude)
print(natal.native.coordinates.latitude.raw)
```

Will look like this:

```
Sat Jan 01 2000 10:00:00 AM America/Los_Angeles at 32N43.0, 117W9.0
32N43.0, 117W9.0
32N43.0
32.71666666666667
```

## JSON

A chart property's structure is easier to visualize by serializing it with the bundled `ToJSON` class. In the above `native` case:

```python
import json

from immanuel import charts
from immanuel.classes.serialize import ToJSON


native = charts.Subject('2000-01-01 10:00', '32n43', '117w09')
natal = charts.Natal(native)
print(json.dumps(natal.native, cls=ToJSON, indent=4))
```

This will output the following JSON:

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

All chart properties, and the chart itself, can be serialized to JSON:

```python
# Just the chart native
print(json.dumps(natal.native, cls=ToJSON, indent=4))
# Just the planets etc.
print(json.dumps(natal.objects, cls=ToJSON, indent=4))
# The whole chart
print(json.dumps(natal, cls=ToJSON, indent=4))
```

This makes Immanuel ideal for powering APIs and other applications. For a deeper dive into the actual data returned, see the next section.

---

1. [Overview](1-overview.md)
2. [Installation](2-installation.md)
3. Examples
4. [Returned Data](4-data.md)
5. [Settings](5-settings.md)
6. [Submodules](6-submodules.md)
7. [Contributions](7-contributions.md)
