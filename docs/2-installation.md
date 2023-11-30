# Installation

Immanuel requires Python >= 3.10 and can be installed with pip:

```bash
pip install immanuel
```

Note that the package requirements have currently locked in version 5.2.0 of `timezonefinder` due to version >= 6.0.0 requiring a C compiler to be present on installation in order to run with any degree of efficiency. Without one it will revert to a pure-Python library which is painfully slow by comparison. Version 5.2.0 will run much faster if a C compiler is not available, but it is unclear how big an impact on accuracy this will have.

---

1. [Overview](1-overview.md)
2. Installation
3. [Examples](3-examples.md)
4. [Returned Data](4-data.md)
5. [Calculations](5-calculations.md)
6. [Settings](6-settings.md)
7. [Submodules](7-submodules.md)
