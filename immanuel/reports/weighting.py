"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    Inspects element and quadrant weighting from a dict of chart objects
    provided by the ephemeris module.

"""

from immanuel.const import chart
from immanuel.tools import position


def elements(objects: dict) -> dict:
    """ Returns data on the amount of chart objects
    belonging to each element. """
    weightings = {
        chart.FIRE: [],
        chart.EARTH: [],
        chart.AIR: [],
        chart.WATER: [],
    }

    for object in objects.values():
        weightings[position.element(object)].append(object['index'])

    return weightings


def modalities(objects: dict) -> dict:
    """ Returns data on the amount of chart objects
    belonging to each modality. """
    weightings = {
        chart.CARDINAL: [],
        chart.FIXED: [],
        chart.MUTABLE: [],
    }

    for object in objects.values():
        weightings[position.modality(object)].append(object['index'])

    return weightings


def quadrants(objects: dict, houses: dict) -> dict:
    """ Returns data on the amount of chart objects
    belonging to each of the chart's house quadrants. """
    weightings = {
        1: [],
        2: [],
        3: [],
        4: [],
    }

    for object in objects.values():
        house = position.house(object, houses)
        quadrant = int((house['number']-1) / 3) + 1
        weightings[quadrant].append(object['index'])

    return weightings
