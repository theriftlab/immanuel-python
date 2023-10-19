"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    This module calculates aspects between chart objects based on
    the settings provided by the setup module.

    The functions also rely on the object data returned by the
    ephemeris module.

"""

import swisseph as swe

from immanuel.const import calc
from immanuel.setup import settings
from immanuel.tools import position


def between(object1: dict, object2: dict) -> dict:
    """ Returns any aspect between the two passed objects. """
    active, passive = (object1, object2) if abs(object1['speed']) > abs(object2['speed']) else (object2, object1)

    for aspect in settings.aspects:
        # Check aspect rules
        active_aspect_rule = settings.aspect_rules[active['index']] if active['index'] in settings.aspect_rules else settings.default_aspect_rule
        passive_aspect_rule = settings.aspect_rules[passive['index']] if passive['index'] in settings.aspect_rules else settings.default_aspect_rule

        if aspect not in active_aspect_rule['initiate'] or aspect not in passive_aspect_rule['receive']:
            return None

        # Get orbs
        active_orb = settings.orbs[active['index']][aspect] if active['index'] in settings.orbs else settings.default_orb
        passive_orb = settings.orbs[passive['index']][aspect] if passive['index'] in settings.orbs else settings.default_orb
        orb = ((active_orb + passive_orb) / 2) if settings.orb_calculation == calc.MEAN else max(active_orb, passive_orb)

        # Look for an aspect
        distance = swe.difdeg2n(passive['lon'], active['lon'])

        if aspect-orb <= abs(distance) <= aspect+orb:
            # Work out aspect information
            aspect_orb = abs(distance) - aspect
            exact_lon = swe.degnorm(passive['lon'] + (aspect if distance < 0 else -aspect))
            associate = position.sign(exact_lon) == position.sign(active)
            exact = exact_lon-settings.exact_orb <= active['lon'] <= exact_lon+settings.exact_orb
            applicative = not exact and ((aspect_orb < 0 if distance < 0 else aspect_orb > 0) or active['speed'] < -calc.STATION_SPEED)

            return {
                'active': active['index'],
                'passive': passive['index'],
                'aspect': aspect,
                'orb': orb,
                'distance': distance,
                'difference': aspect_orb,
                'movement': calc.EXACT if exact else calc.APPLICATIVE if applicative else calc.SEPARATIVE,
                'condition': calc.ASSOCIATE if associate else calc.DISSOCIATE,
            }

    return None


def for_object(object: dict, objects: dict, exclude_same: bool = True) -> dict:
    """ Returns all chart objects aspecting the passed chart object. If two
    separate sets of objects are being compared (eg. synastry) then
    exclude_self can be set to False to find aspects between the same
    object in both charts. """
    aspects = {}

    for index, check_object in objects.items():
        if exclude_same and index == object['index']:
            continue

        aspect = between(object, check_object)

        if aspect is not None:
            aspects[check_object['index']] = aspect

    return aspects


def all(objects: dict, exclude_same: bool = True) -> dict:
    """ Returns all aspects between the passed chart objects. """
    aspects = {}

    for index, object in objects.items():
        object_aspects = for_object(object, objects, exclude_same)

        if object_aspects:
            aspects[index] = object_aspects

    return aspects


def by_type(objects: dict, exclude_same: bool = True) -> dict:
    """ Returns all aspects between the passed chart objects keyed by
    aspect type. """
    aspects = {}

    for object in objects.values():
        object_aspects = for_object(object, objects, exclude_same)

        if object_aspects:
            for object_aspect in object_aspects.values():
                if object_aspect['aspect'] not in aspects:
                    aspects[object_aspect['aspect']] = []

                if object_aspect not in aspects[object_aspect['aspect']]:
                    aspects[object_aspect['aspect']].append(object_aspect)

    return aspects


def synastry(objects1: dict, objects2: dict, exclude_same: bool = False) -> dict:
    """ Returns all aspects between the two sets of passed chart objects. """
    aspects = {}

    for index, object in objects1.items():
        object_aspects = for_object(object, objects2, exclude_same)

        if object_aspects:
            aspects[index] = object_aspects

    return aspects
