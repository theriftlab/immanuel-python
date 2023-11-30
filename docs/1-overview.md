# Overview

## Why Immanuel?

> Now is heaven the readier to favour those who search out its secrets.

*- Marcus Manilius*

Immanuel is an ancient name that means *God is with us*. Since astrology was once revered as a study of the gods in their realm to make sense of their whims and seemingly-erratic movements, it seems an appropriate name for a package which aims to translate complex astronomical data into simple astrology chart data.

## What problem does it solve?

Immanuel sets out to make it a breeze to generate simple, chart-centred data based on the Swiss Ephemeris from within your Python application. While [pyswisseph](https://github.com/astrorigin/pyswisseph) does an excellent job of providing detailed astronomical and house data, there are many steps to translating this into meaningful chart data. This is where Immanuel comes in.

Not only are the basics covered (planets and houses, which signs and houses the planets are in, etc.) but more complex calculations such as aspects, composites and secondary progressions are also taken care of, with many options to customise them.

Since there are seemingly infinite ways to interpret astronomical data into astrological, Immanuel seeks to align much of its output with that of [astro.com](https://astro.com) as this is arguably the most popular free go-to for many amateur and even professional astrologers.

Although Immanuel generates human-friendly output, all of its data is JSON-serializable and highly configurable, making it ideal for powering APIs.

## What's with all the objects?

Some confusion might arise with the word "object" - since an astrological chart can contain much more than just planets, anything that can appear within the chart and make aspects is referred to as a "chart object". However, since Python is indeed an object-oriented language, the code itself generates Python objects. The documentation therefore makes an effort to spell out "chart object" vs "Python object" to avoid confusion (and to avoid trying to explain why you'll have a chart object full of chart objects which are object objects).

---

1. Overview
2. [Installation](2-installation.md)
3. [Examples](3-examples.md)
4. [Returned Data](4-data.md)
5. [Calculations](5-calculations.md)
6. [Settings](6-settings.md)
7. [Submodules](7-submodules.md)