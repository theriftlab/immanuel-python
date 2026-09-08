# Installation

Immanuel requires Python >= 3.10 and can be installed with pip:

```bash
pip install immanuel
```

Note that the package requirements have currently locked in the outdated version 5.2.0 of `timezonefinder` due to various performance issues with later, more accurate, versions. While 5.2.0 will have outdated boundary data and less accurate lookup algorithms, it is the most consistent performance-wise across most use cases. The [Examples](3-examples.md) section covers how to pass in your own timezone strings or UTC offsets to bypass Immanuel's own `timezonefinder`-powered lookups with your own.

---

1. [Overview](1-overview.md)
2. Installation
3. [Examples](3-examples.md)
4. [Returned Data](4-data.md)
5. [Settings](5-settings.md)
6. [Submodules](6-submodules.md)
7. [Contributions](7-contributions.md)
