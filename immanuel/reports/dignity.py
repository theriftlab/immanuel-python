"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    This module provides simple dignity and mutual reception data.

    Assuming only planets will be passed, these functions will return the main
    essential dignity states of any planet. Mutual receptions are also
    calculated for each diginity.

"""

from immanuel.const import dignities
from immanuel.setup import settings
from immanuel.tools import position


def ruler(object: dict) -> bool:
    """ Returns whether the passed planet is the ruler of its sign. """
    return object['index'] == settings.rulerships[position.sign(object)]


def exalted(object: dict) -> bool:
    """ Returns whether the passed planet is exalted within its sign. """
    return object['index'] == dignities.EXALTATIONS[position.sign(object)]


def triplicity_ruler(object: dict, is_daytime: bool) -> bool:
    """ Returns whether the passed planet is any type of triplicity ruler. """
    triplicities = settings.triplicities[position.sign(object)]

    if settings.include_participatory_triplicities:
        return object['index'] in (triplicities['day' if is_daytime else 'night'], triplicities.get('participatory'))
    else:
        return object['index'] == triplicities['day' if is_daytime else 'night']


def term_ruler(object: dict) -> bool:
    """ Returns whether the passed planet is the term ruler
    within its sign. """
    terms = settings.terms[position.sign(object)]

    if object['index'] not in terms:
        return False

    return terms[object['index']][0] <= position.sign_longitude(object) < terms[object['index']][1]


def face_ruler(object: dict) -> bool:
    """ Returns whether the passed planet is the decan ruler
    within its sign. """
    return object['index'] == dignities.FACE_RULERS[position.sign(object)][position.decan(object)-1]


def mutual_reception_ruler(object: dict, objects: dict) -> bool:
    """ Returns whether the passed planet is in mutual reception
    by rulership. """
    if ruler(object):
        return False

    object_sign = position.sign(object)
    object_sign_rulership = settings.rulerships[object_sign]

    return position.sign(objects[object_sign_rulership]) in _planet_signs(object, settings.rulerships)


def mutual_reception_exalted(object: dict, objects: dict) -> bool:
    """ Returns whether the passed planet is in mutual reception
    by exaltation. """
    if exalted(object):
        return False

    object_sign = position.sign(object)
    object_sign_exaltation = dignities.EXALTATIONS[object_sign]

    if object_sign_exaltation is None:
        return False

    return position.sign(objects[object_sign_exaltation]) in _planet_signs(object, dignities.EXALTATIONS)


def mutual_reception_triplicity_ruler(object: dict, objects: dict, is_daytime: bool) -> bool:
    """ Returns whether the passed planet is in mutual reception
    by any type of triplicity rulership. """
    if triplicity_ruler(object, is_daytime):
        return False

    key = 'day' if is_daytime else 'night'
    object_sign = position.sign(object)
    object_triplicities = settings.triplicities[object_sign]
    day_night_ruler_triplicities = settings.triplicities[position.sign(objects[object_triplicities[key]])]

    if object['index'] == day_night_ruler_triplicities[key]:
        return True

    if not settings.include_participatory_triplicities or 'participatory' not in object_triplicities:
        return False

    participatory_ruler_triplicities = settings.triplicities[position.sign(objects[object_triplicities['participatory']])]

    return object['index'] == participatory_ruler_triplicities['participatory']


def mutual_reception_term_ruler(object: dict, objects: dict) -> bool:
    """ Returns whether the passed planet is in mutual reception
    by term rulership. """
    if term_ruler(object):
        return False

    object_terms = settings.terms[position.sign(object)]

    for index, boundaries in object_terms.items():
        if boundaries[0] <= position.sign_longitude(object) < boundaries[1]:
            break

    term_ruler_terms = settings.terms[position.sign(objects[index])]

    return object['index'] in term_ruler_terms and term_ruler_terms[object['index']][0] <= position.sign_longitude(objects[index]) < term_ruler_terms[object['index']][1]


def mutual_reception_face_ruler(object: dict, objects: dict) -> bool:
    """ Returns whether the passed planet is in mutual reception
    by face rulership. """
    if face_ruler(object):
        return False

    face_ruler_object = dignities.FACE_RULERS[position.sign(object)][position.decan(object)-1]

    return object['index'] == dignities.FACE_RULERS[position.sign(objects[face_ruler_object])][position.decan(objects[face_ruler_object])-1]


def in_rulership_element(object: dict) -> bool:
    """ Returns whether the passed planet is in a sign that shares an element
    with its domicile. """
    if object['index'] not in settings.rulerships.values():
        return False

    return position.element(_planet_signs(object, settings.rulerships)[0]*30-1) == position.element(object)


def detriment(object: dict) -> bool:
    """ Returns whether the passed planet is in detriment within its sign. """
    return position.opposite_sign(object) in _planet_signs(object, settings.rulerships)


def fall(object: dict) -> bool:
    """ Returns whether the passed planet is in fall within its sign. """
    return position.opposite_sign(object) in _planet_signs(object, dignities.EXALTATIONS)


def all(object: dict, objects: dict, is_daytime: bool) -> dict:
    essential_dignities = {
        dignities.RULER: ruler(object),
        dignities.EXALTED: exalted(object),
        dignities.TRIPLICITY_RULER: triplicity_ruler(object, is_daytime),
        dignities.TERM_RULER: term_ruler(object),
        dignities.FACE_RULER: face_ruler(object),
    }

    mutual_reception_dignities = {
        dignities.MUTUAL_RECEPTION_RULER: mutual_reception_ruler(object, objects),
        dignities.MUTUAL_RECEPTION_EXALTED: mutual_reception_exalted(object, objects),
        dignities.MUTUAL_RECEPTION_TRIPLICITY_RULER: mutual_reception_triplicity_ruler(object, objects, is_daytime),
        dignities.MUTUAL_RECEPTION_TERM_RULER: mutual_reception_term_ruler(object, objects),
        dignities.MUTUAL_RECEPTION_FACE_RULER: mutual_reception_face_ruler(object, objects),
    }

    minor_dignities = {
        dignities.IN_RULERSHIP_ELEMENT: in_rulership_element(object),
    }

    debilities = {
        dignities.DETRIMENT: detriment(object),
        dignities.FALL: fall(object),
        dignities.PEREGRINE: not any(essential_dignities.values()),
    }

    if settings.include_mutual_receptions:
        debilities[dignities.PEREGRINE] = debilities[dignities.PEREGRINE] and not any(mutual_reception_dignities.values())

    if debilities[dignities.PEREGRINE]:
        debilities[dignities.PEREGRINE] = not minor_dignities[dignities.IN_RULERSHIP_ELEMENT]

    return essential_dignities | mutual_reception_dignities | minor_dignities | debilities


def score(dignity_state: dict) -> int:
    """ Calculates a planet's dignity score based on settings. """
    return sum([v for k, v in settings.dignity_scores.items() if k in dignity_state and dignity_state[k]])


def _planet_signs(object: dict, table: dict) -> tuple:
    """ Returns the sign(s) a planet belongs to in {sign: planet} dicts. """
    return tuple(k for k, v in table.items() if v == object['index'])
