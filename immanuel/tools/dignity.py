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

    return position.sign(items[chart.PLANETS][item_sign_rulership]['lon']) in item_rulership_signs


def mutual_reception_exaltaion(item: dict, items: dict) -> bool:
    """ Whether the passed planet is in mutual reception by exaltation. """
    if exalted(item):
        return False

    item_sign = position.sign(item['lon'])
    item_exaltation_signs = _planet_signs(item, dignities.EXALTATIONS)
    item_sign_exaltation = dignities.EXALTATIONS[item_sign]

    return position.sign(items[chart.PLANETS][item_sign_exaltation]['lon']) in item_exaltation_signs


def mutual_reception_house(item: dict, items: dict, houses: dict) -> bool:
    """ Whether the passed planet is in mutual reception by
    house-sign rulership. """
    house = houses[position.house(item['lon'], houses)]
    house_sign = position.sign(house['lon'])
    house_sign_ruler = items[chart.PLANETS][options.rulerships[house_sign]]
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


def _planet_signs(item: dict, table: dict) -> int:
    """ Returns the sign(s) a planet belongs to in {sign: planet} dicts. """
    return tuple(k for k, v in table.items() if v == item['index'])
