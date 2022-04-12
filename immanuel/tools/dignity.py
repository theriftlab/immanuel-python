"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    This module provides simple dignity and mutual reception data.

    Assuming only planets will be passed, these functions will return the main
    essential dignity states of any planet. Various mutual receptions are also
    calculated.

"""

from immanuel import options
from immanuel.const import chart, dignities
from immanuel.tools import position


def mutual_reception_rulership(item: dict, items: dict) -> bool:
    """ Whether the passed planet is in mutual reception by rulership. """
    if ruler(item):
        return False

    item_sign = position.sign(item['lon'])
    item_rulership_signs = _planet_signs(item, options.rulerships)
    item_sign_rulership = options.rulerships[item_sign]

    return position.sign(items[item_sign_rulership]['lon']) in item_rulership_signs


def mutual_reception_exaltaion(item: dict, items: dict) -> bool:
    """ Whether the passed planet is in mutual reception by exaltation. """
    if exalted(item):
        return False

    item_sign = position.sign(item['lon'])
    item_exaltation_signs = _planet_signs(item, dignities.EXALTATIONS)
    item_sign_exaltation = dignities.EXALTATIONS[item_sign]

    if item_sign_exaltation is None:
        return False

    return position.sign(items[item_sign_exaltation]['lon']) in item_exaltation_signs


def mutual_reception_house(item: dict, items: dict, houses: dict) -> bool:
    """ Whether the passed planet is in mutual reception by
    house-sign rulership. """
    house = houses[position.house(item['lon'], houses)]
    house_sign = position.sign(house['lon'])
    house_sign_ruler = items[options.rulerships[house_sign]]
    house_sign_ruler_house = houses[position.house(house_sign_ruler['lon'], houses)]
    house_sign_ruler_house_sign = position.sign(house_sign_ruler_house['lon'])

    return item['index'] == options.rulerships[house_sign_ruler_house_sign]


def ruler(item: dict) -> bool:
    """ Returns whether the passed planet is the ruler of its sign. """
    return item['index'] == options.rulerships[position.sign(item['lon'])]


def exalted(item: dict) -> bool:
    """ Returns whether the passed planet is exalted within its sign. """
    return item['index'] == dignities.EXALTATIONS[position.sign(item['lon'])]


def detriment(item: dict) -> bool:
    """ Returns whether the passed planet is in detriment within its sign. """
    return position.opposite_sign(item['lon']) in _planet_signs(item, options.rulerships)


def fall(item: dict) -> bool:
    """ Returns whether the passed planet is in fall within its sign. """
    return position.opposite_sign(item['lon']) in _planet_signs(item, dignities.EXALTATIONS)


def term_ruler(item: dict) -> bool:
    """ Returns whether the passed planet is the term ruler
    within its sign. """
    planet_sign, planet_sign_lon = position.signlon(item['lon'])

    if item['index'] not in options.terms[planet_sign]:
        return False

    return options.terms[planet_sign][item['index']][0] <= planet_sign_lon < options.terms[planet_sign][item['index']][1]


def triplicity_ruler_day(item: dict, is_daytime: bool) -> bool:
    """ Returns whether the passed planet is a daytime triplicity ruler
    within its sign. """
    return item['index'] == options.triplicities[position.sign(item['lon'])]['day'] and is_daytime


def triplicity_ruler_night(item: dict, is_daytime: bool) -> bool:
    """ Returns whether the passed planet is a nighttime triplicity ruler
    within its sign. """
    return item['index'] == options.triplicities[position.sign(item['lon'])]['night'] and not is_daytime


def triplicity_ruler_participatory(item: dict) -> bool:
    """ Returns whether the passed planet is a participatory triplicity ruler
    within its sign, if the selected triplicities contain one. """
    triplicities = options.triplicities[position.sign(item['lon'])]
    return 'participatory' in triplicities and item['index'] == triplicities['participatory']


def face_ruler(item: dict) -> bool:
    """ Returns whether the passed planet is the decan ruler
    within its sign. """
    return item['index'] == dignities.FACE_RULERS[position.sign(item['lon'])][position.decan(item['lon'])-1]


def all(item: dict, **kwargs) -> dict:
    """ Returns a dictionary of all dignity states based on passed
    arguments. 'items', 'houses' and 'is_daytime' are optional and any
    dignities based on these will not be calculated if missing. """
    items = kwargs.get('items', None)
    houses = kwargs.get('houses', None)
    is_daytime = kwargs.get('is_daytime', None)

    dignity_state = {}

    if dignities.RULER in options.dignity_scores:
        dignity_state[dignities.RULER] = ruler(item)

    if dignities.EXALTED in options.dignity_scores:
        dignity_state[dignities.RULER] = exalted(item)

    if dignities.TERM_RULER in options.dignity_scores:
        dignity_state[dignities.TERM_RULER] = term_ruler(item)

    if dignities.FACE_RULER in options.dignity_scores:
        dignity_state[dignities.FACE_RULER] = face_ruler(item)

    if is_daytime is not None:
        if dignities.TRIPLICITY_RULER_DAY in options.dignity_scores:
            dignity_state[dignities.TRIPLICITY_RULER_DAY] = triplicity_ruler_day(item, is_daytime)

        if dignities.TRIPLICITY_RULER_NIGHT in options.dignity_scores:
            dignity_state[dignities.TRIPLICITY_RULER_NIGHT] = triplicity_ruler_night(item, is_daytime)

        if dignities.TRIPLICITY_RULER_PARTICIPATORY in options.dignity_scores:
            dignity_state[dignities.TRIPLICITY_RULER_PARTICIPATORY] = triplicity_ruler_participatory(item)

    if options.peregrine == dignities.IGNORE_MUTUAL_RECEPTIONS:
        peregrine = len([v for v in dignity_state.values() if v]) == 0

    if items is not None:
        if dignities.MUTUAL_RECEPTION_RULERSHIP in options.dignity_scores:
            dignity_state[dignities.MUTUAL_RECEPTION_RULERSHIP] = mutual_reception_rulership(item, items)

        if dignities.MUTUAL_RECEPTION_EXALTATION in options.dignity_scores:
            dignity_state[dignities.MUTUAL_RECEPTION_EXALTATION] = mutual_reception_exaltaion(item, items)

        if houses is not None and dignities.MUTUAL_RECEPTION_HOUSE in options.dignity_scores:
            dignity_state[dignities.MUTUAL_RECEPTION_HOUSE] = mutual_reception_house(item, items, houses)

    if options.peregrine == dignities.INCLUDE_MUTUAL_RECEPTIONS:
        peregrine = len([v for v in dignity_state.values() if v]) == 0

    if dignities.DETRIMENT in options.dignity_scores:
        dignity_state[dignities.DETRIMENT] = detriment(item)

    if dignities.FALL in options.dignity_scores:
        dignity_state[dignities.FALL] = fall(item)

    if dignities.PEREGRINE in options.dignity_scores:
        dignity_state[dignities.PEREGRINE] = peregrine

    return dignity_state


def score(item: dict, **kwargs) -> int:
    """ Calculates the planet's dignity score based on options. """
    dignity_state = all(item, **kwargs)
    return sum([v for k, v in options.dignity_scores.items() if k in dignity_state and dignity_state[k]])


def _planet_signs(item: dict, table: dict) -> int:
    """ Returns the sign(s) a planet belongs to in {sign: planet} dicts. """
    return tuple(k for k, v in table.items() if v == item['index'])
