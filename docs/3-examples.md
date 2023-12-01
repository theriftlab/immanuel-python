# Examples

All the chart data generation happens in the chart classes in Immanuel's `charts` module. Once imported, data for any given chart can be generated with one line of code by passing the relevant dates and coordinates.

The constructors take date/times in standard timezone-naive ISO format (YYYY-MM-DD HH:MM:SS), and coordinates in either standard text format (as in the following examples) or decimal.

Some times can be ambiguous, for example 1:30am on a night when switching to daylight savings. This time could be in either timezone. To specify which one, you can pass in an additional `is_dst` boolean to tell Immanuel whether or not the `dob` time belongs in the daylight savings zone. For partner charts, there will be an additional `partner_is_dst` for the `partner_dob`.

To generate one of each type of supported chart, you could do the following:

```python
from immanuel import charts


natal = charts.Natal(dob='2000-01-01 10:00', lat='32n43', lon='117w09')
# or...
natal = charts.Natal(dob='2000-01-01 10:00', lat=32.71667, lon=-117.15)
# and if you were born in DST during a switchover...
natal = charts.Natal(dob='2023-11-05 01:30', lat=32.71667, lon=-117.15, is_dst=True)

solar_return = charts.SolarReturn(dob='2000-01-01 10:00', lat='32n43', lon='117w09', year=2025)

progressed = charts.Progressed(dob='2000-01-01 10:00', lat='32n43', lon='117w09', pdt='2025-06-20 17:00')

synastry = charts.Synastry(dob='2000-01-01 10:00', lat='32n43', lon='117w09', partner_dob='2001-02-03 15:45', partner_lat='38n35', partner_lon='121w30')

composite = charts.Composite(dob='2000-01-01 10:00', lat='32n43', lon='117w09', partner_dob='2001-02-03 15:45', partner_lat='38n35', partner_lon='121w30')
```

## Human-Readable

You can simply print out a chart's property to see human-readable data, eg.:

```python
print(f'Daytime: {natal.diurnal}')
print(f'Moon phase: {natal.moon_phase}\n')

for object in natal.objects.values():
    print(object)

print('\n')

for index, aspects in natal.aspects.items():
    print(f'Aspects for {natal.objects[index].name}:')

    for aspect in aspects.values():
        print(f' - {aspect}')
```

The (abridged) output will look something like this:

```
Daytime: True
Moon phase: Third Quarter

Sun 10°37'26" in Capricorn, 11th House
Moon 16°19'29" in Scorpio, 8th House
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
print(natal.coordinates)
print(natal.coordinates.latitude)
print(natal.coordinates.latitude.raw)
```

Will look like this:

```
32N43.0, 117W9.0
32N43.0
32.71666666666667
```

## JSON

A property's structure is easier to visualise by serializing it with the bundled `ToJSON` class. In the above `coordinates` case:

```python
import json

from immanuel import charts
from immanuel.classes.serialize import ToJSON


natal = charts.Natal(dob='2000-01-01 10:00', lat='32n43', lon='117w09')
print(json.dumps(natal.coordinates, cls=ToJSON, indent=4))
```

This will output the following JSON:

```json
{
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
```

All chart properties, and the chart itself, can be serialized to JSON:

```python
# Just the coordinates
print(json.dumps(natal.coordinates, cls=ToJSON, indent=4))
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
5. [Calculations](5-calculations.md)
6. [Settings](6-settings.md)
7. [Submodules](7-submodules.md)
