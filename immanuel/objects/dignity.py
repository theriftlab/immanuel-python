"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    This module provides simple dignity and mutual reception data.

    Assuming only planets will be passed, these functions will return the main
    essential dignity states of any planet. Various mutual receptions are also
    calculated.

"""

from immanuel.const import dignities
from immanuel.setup import settings
from immanuel.tools import position


def mutual_reception_rulership(object: dict, objects: dict) -> bool:
    """ Whether the passed planet is in mutual reception by rulership. """
    if ruler(object):
        return False

    object_sign = position.sign(object['lon'])
    object_rulership_signs = _planet_signs(object, settings.rulerships)
    object_sign_rulership = settings.rulerships[object_sign]

    return position.sign(objects[object_sign_rulership]['lon']) in object_rulership_signs


def mutual_reception_exaltaion(object: dict, objects: dict) -> bool:
    """ Whether the passed planet is in mutual reception by exaltation. """
    if exalted(object):
        return False

    object_sign = position.sign(object['lon'])
    object_exaltation_signs = _planet_signs(object, dignities.EXALTATIONS)
    object_sign_exaltation = dignities.EXALTATIONS[object_sign]

    if object_sign_exaltation is None:
        return False

    return position.sign(objects[object_sign_exaltation]['lon']) in object_exaltation_signs


def mutual_reception_house(object: dict, objects: dict, houses: dict) -> bool:
    """ Whether the passed planet is in mutual reception by
    house-sign rulership. """
    house = houses[position.house(object['lon'], houses)['index']]
    house_sign = position.sign(house['lon'])
    house_sign_ruler = objects[settings.rulerships[house_sign]]
    house_sign_ruler_house = houses[position.house(house_sign_ruler['lon'], houses)['index']]
    house_sign_ruler_house_sign = position.sign(house_sign_ruler_house['lon'])

    return object['index'] == settings.rulerships[house_sign_ruler_house_sign]


def ruler(object: dict) -> bool:
    """ Returns whether the passed planet is the ruler of its sign. """
    return object['index'] == settings.rulerships[position.sign(object['lon'])]


def exalted(object: dict) -> bool:
    """ Returns whether the passed planet is exalted within its sign. """
    return object['index'] == dignities.EXALTATIONS[position.sign(object['lon'])]


def detriment(object: dict) -> bool:
    """ Returns whether the passed planet is in detriment within its sign. """
    return position.opposite_sign(object['lon']) in _planet_signs(object, settings.rulerships)


def fall(object: dict) -> bool:
    """ Returns whether the passed planet is in fall within its sign. """
    return position.opposite_sign(object['lon']) in _planet_signs(object, dignities.EXALTATIONS)


def term_ruler(object: dict) -> bool:
    """ Returns whether the passed planet is the term ruler
    within its sign. """
    planet_sign, planet_sign_lon = position.signlon(object['lon'])

    if object['index'] not in settings.terms[planet_sign]:
        return False

    return settings.terms[planet_sign][object['index']][0] <= planet_sign_lon < settings.terms[planet_sign][object['index']][1]


def triplicity_ruler_day(object: dict, is_daytime: bool) -> bool:
    """ Returns whether the passed planet is a daytime triplicity ruler
    within its sign. """
    return object['index'] == settings.triplicities[position.sign(object['lon'])]['day'] and is_daytime


def triplicity_ruler_night(object: dict, is_daytime: bool) -> bool:
    """ Returns whether the passed planet is a nighttime triplicity ruler
    within its sign. """
    return object['index'] == settings.triplicities[position.sign(object['lon'])]['night'] and not is_daytime


def triplicity_ruler_participatory(object: dict) -> bool:
    """ Returns whether the passed planet is a participatory triplicity ruler
    within its sign, if the selected triplicities contain one. """
    triplicities = settings.triplicities[position.sign(object['lon'])]
    return 'participatory' in triplicities and object['index'] == triplicities['participatory']


def face_ruler(object: dict) -> bool:
    """ Returns whether the passed planet is the decan ruler
    within its sign. """
    return object['index'] == dignities.FACE_RULERS[position.sign(object['lon'])][position.decan(object['lon'])-1]


def all(object: dict, **kwargs) -> dict:
    """ Returns a dictionary of all dignity states based on passed
    arguments. 'objects', 'houses' and 'is_daytime' are optional and any
    dignities based on these will not be calculated if missing. """
    objects = kwargs.get('objects', None)
    houses = kwargs.get('houses', None)
    is_daytime = kwargs.get('is_daytime', None)

    dignity_state = {
        dignities.RULER: ruler(object) if dignities.RULER in settings.dignity_scores else None,
        dignities.EXALTED: exalted(object) if dignities.EXALTED in settings.dignity_scores else None,
        dignities.TERM_RULER: term_ruler(object) if dignities.TERM_RULER in settings.dignity_scores else None,
        dignities.FACE_RULER: face_ruler(object) if dignities.FACE_RULER in settings.dignity_scores else None,
    }

    if is_daytime is not None:
        dignity_state |= {
            dignities.TRIPLICITY_RULER_DAY: triplicity_ruler_day(object, is_daytime) if dignities.TRIPLICITY_RULER_DAY in settings.dignity_scores else None,
            dignities.TRIPLICITY_RULER_NIGHT: triplicity_ruler_night(object, is_daytime) if dignities.TRIPLICITY_RULER_NIGHT in settings.dignity_scores else None,
            dignities.TRIPLICITY_RULER_PARTICIPATORY: triplicity_ruler_participatory(object) if dignities.TRIPLICITY_RULER_PARTICIPATORY in settings.dignity_scores else None,
        }

    if settings.peregrine == dignities.IGNORE_MUTUAL_RECEPTIONS:
        peregrine = len([v for v in dignity_state.values() if v]) == 0

    if objects is not None:
        dignity_state |= {
            dignities.MUTUAL_RECEPTION_RULERSHIP: mutual_reception_rulership(object, objects) if dignities.MUTUAL_RECEPTION_RULERSHIP in settings.dignity_scores else None,
            dignities.MUTUAL_RECEPTION_EXALTATION: mutual_reception_exaltaion(object, objects) if dignities.MUTUAL_RECEPTION_EXALTATION in settings.dignity_scores else None,
            dignities.MUTUAL_RECEPTION_HOUSE: mutual_reception_house(object, objects, houses) if houses is not None and dignities.MUTUAL_RECEPTION_HOUSE in settings.dignity_scores else None,
        }

    if settings.peregrine == dignities.INCLUDE_MUTUAL_RECEPTIONS:
        peregrine = len([v for v in dignity_state.values() if v]) == 0

    dignity_state |= {
        dignities.DETRIMENT: detriment(object) if dignities.DETRIMENT in settings.dignity_scores else None,
        dignities.FALL: fall(object) if dignities.FALL in settings.dignity_scores else None,
        dignities.PEREGRINE: peregrine if dignities.PEREGRINE in settings.dignity_scores else None,
    }

    return {k: v for k, v in dignity_state.items() if v is not None}


def score(object: dict, **kwargs) -> int:
    """ Calculates the planet's dignity score based on settings. """
    dignity_state = all(object, **kwargs)
    return sum([v for k, v in settings.dignity_scores.items() if k in dignity_state and dignity_state[k]])


def _planet_signs(object: dict, table: dict) -> tuple:
    """ Returns the sign(s) a planet belongs to in {sign: planet} dicts. """
    return tuple(k for k, v in table.items() if v == object['index'])
