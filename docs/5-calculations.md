# Calculations

## Secondary Progressions

Immanuel calculates progressions in the same way as [astro.com](https://astro.com). The natal date is progressed by the same formula and the same three MC progression methods are available to calculate houses:

| Method | Astro.com Equivalent |
| --- | --- |
| Daily Houses | ARMC 361°/prog.day |
| Naibod | ARMC 1 Naibod/prog.day |
| Solar Arc | MC from solar arc |

See the [Settings](6-settings.md#mc_progression_method) section to see how to pick a method, otherwise Immanuel will default to Naibod.

## Composites

Composite charts are calculated by midpoint. There are two options for calculating the houses - Immanuel defaults to taking midpoints for all house cusps (as does astro.com), but it is also possible to generate a new set of houses from the composite MC.

Similarly, the composite Part of Fortune can either be calculated by midpoint (the default) or it can generate a new Part of Fortune from the composite Sun, Moon, and Ascendant.

See the [Settings](6-settings.md#composite_pars_fortuna) section to see how to change these defaults.

## Synastry

As mentioned in the [Returned Data](4-data.md) section, a synastry chart will have two sets of aspects - one for the main chart's objects that have aspects to the partner chart's objects, and vice versa. Since there are two charts, it is entirely possible for a chart object to seemingly aspect itself since, for example, the main chart's Sun might aspect the partner chart's Sun.

Just bear in mind that every top-level object keyed in the `aspects` property belongs to the main chart, and each entry will be a dict of the partner chart's objects that aspect it - and vice versa for `partner_aspects`.

## Dignity Scores

The planets all feature diginity scores based on [Astro Gold's scoring system](https://www.astrogold.io/AG-MacOS-Help/essential_dignities.html). Dignities and their scores can all be customised quite heavily via Immanuel's [settings](6-settings.md#rulerships), however; various rulership, triplicity, and term tables are available, and the actual scores and some of the dignity calculations can also be modified.
