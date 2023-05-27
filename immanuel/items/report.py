"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    Inspects element and quadrant weighting from a dict of chart items
    provided by the eph module.

"""

from immanuel.const import chart
from immanuel.tools import position


def elements(items: dict) -> dict:
    """ Returns data on the amount of chart items
    belonging to each element. """
    weightings = {
        chart.FIRE: [],
        chart.EARTH: [],
        chart.AIR: [],
        chart.WATER: [],
    }

    for item in items.values():
        weightings[position.element(item['lon'])].append(item['index'])

    return weightings


def modalities(items: dict) -> dict:
    """ Returns data on the amount of chart items
    belonging to each modality. """
    weightings = {
        chart.CARDINAL: [],
        chart.FIXED: [],
        chart.MUTABLE: [],
    }

    for item in items.values():
        weightings[position.modality(item['lon'])].append(item['index'])

    return weightings


def quadrants(items: dict, houses: dict) -> dict:
    """ Returns data on the amount of chart items
    belonging to each of the chart's house quadrants. """
    weightings = {
        1: [],
        2: [],
        3: [],
        4: [],
    }

    for item in items.values():
        house = position.house(item['lon'], houses)
        quadrant = int((house['number']-1) / 3) + 1
        weightings[quadrant].append(item['index'])

    return weightings
