"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    This module calculates aspects between chart items based on the options
    specified in the options module.

    This relies on the item data returned by the eph module.

"""

import swisseph as swe

from immanuel.const import calc
from immanuel.setup import options
from immanuel.tools import position


def between(item1: dict, item2: dict, check_aspects: tuple) -> dict:
    """ Returns any aspect between the two passed items. """
    active, passive = (item1, item2) if abs(item1['speed']) > abs(item2['speed']) else (item2, item1)

    for aspect in check_aspects:
        # Check aspect rules
        active_aspect_rule = options.aspect_rules[active['index']] if active['index'] in options.aspect_rules else options.default_aspect_rule
        passive_aspect_rule = options.aspect_rules[passive['index']] if passive['index'] in options.aspect_rules else options.default_aspect_rule

        if aspect not in active_aspect_rule['initiate'] or aspect not in passive_aspect_rule['receive']:
            return None

        # Get orbs
        active_orb = options.orbs[active['index']][aspect] if active['index'] in options.orbs else options.default_orb
        passive_orb = options.orbs[passive['index']][aspect] if passive['index'] in options.orbs else options.default_orb
        orb = (active_orb + passive_orb) / 2 if options.orb_calculation == calc.MEAN else max(active_orb, passive_orb)

        # Look for an aspect
        distance = swe.difdeg2n(passive['lon'], active['lon'])

        if aspect-orb <= abs(distance) <= aspect+orb:
            # Work out aspect information
            aspect_orb = abs(distance) - aspect
            exact_lon = swe.degnorm(passive['lon'] + (aspect if distance < 0 else -aspect))
            associate = position.sign(exact_lon) == position.sign(active['lon'])
            exact = exact_lon-options.exact_orb <= active['lon'] <= exact_lon+options.exact_orb
            applicative = not exact and ((aspect_orb < 0 if distance < 0 else aspect_orb > 0) or active['speed'] < -calc.STATION_SPEED)

            return {
                'active': active['index'],
                'passive': passive['index'],
                'aspect': aspect,
                'distance': distance,
                'orb': aspect_orb,
                'movement': calc.EXACT if exact else calc.APPLICATIVE if applicative else calc.SEPARATIVE,
                'condition': calc.ASSOCIATE if associate else calc.DISSOCIATE,
            }

    return None


def for_item(item: dict, items: dict, exclude_same: bool = True, check_aspects: tuple = options.aspects) -> dict:
    """ Returns all chart items aspecting the passed chart item. If two
    separate sets of items are being compared (eg. synastry) then
    exclude_self can be set to False to find aspects between the same
    item in both charts. """
    aspects = {}

    for index, check_item in items.items():
        if exclude_same and index == item['index']:
            continue

        aspect = between(item, check_item, check_aspects)

        if aspect is not None:
            aspects[check_item['index']] = aspect

    return aspects


def all(items: dict, exclude_same: bool = True, check_aspects: tuple = options.aspects) -> dict:
    """ Returns all aspects between the passed chart items. """
    aspects = {}

    for index, item in items.items():
        item_aspects = for_item(item, items, exclude_same, check_aspects)

        if item_aspects:
            aspects[index] = item_aspects

    return aspects


def by_type(items: dict, exclude_same: bool = True, check_aspects: tuple = options.aspects) -> dict:
    """ Returns all aspects between the passed chart items keyed by
    aspect type. """
    aspects = {}

    for item in items.values():
        item_aspects = for_item(item, items, exclude_same, check_aspects)

        if item_aspects:
            for item_aspect in item_aspects.values():
                if item_aspect['aspect'] not in aspects:
                    aspects[item_aspect['aspect']] = []

                if item_aspect not in aspects[item_aspect['aspect']]:
                    aspects[item_aspect['aspect']].append(item_aspect)

    return aspects
