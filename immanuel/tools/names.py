"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    Utility functions for object name resolution and lookups.

"""

from immanuel.const import names
from immanuel.classes.localize import localize as _


def get_object_name(object_index: int) -> str:
    """Get the proper localized name for an object from the appropriate dictionary.

    Args:
        object_index: The object constant (e.g., chart.SUN, chart.MOON)

    Returns:
        The localized name of the object, or the raw index as string if not found
    """
    # Try each dictionary in order of specificity
    if object_index in names.HOUSES:
        return _(names.HOUSES[object_index])
    elif object_index in names.ANGLES:
        return _(names.ANGLES[object_index])
    elif object_index in names.PLANETS:
        return _(names.PLANETS[object_index])
    elif object_index in names.ASTEROIDS:
        return _(names.ASTEROIDS[object_index])
    elif object_index in names.POINTS:
        return _(names.POINTS[object_index])
    elif object_index in names.ECLIPSES:
        return _(names.ECLIPSES[object_index])
    elif object_index in names.OBJECTS:
        return _(names.OBJECTS[object_index])
    else:
        return str(object_index)  # Fallback to raw index