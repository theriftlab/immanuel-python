from immanuel import options
from immanuel.const import dignities
from immanuel.tools import position


SIGN_RULER = 0
EXALTATION = 1
HOUSE_RULER = 2


# TODO: peregrine? withotu calling a bunch of functions already called????????????
def mutual_reception(items: dict, type: int) -> int:
    """ Returns the planet which is in mutual reception with
    the passed planet. """

    """ TODO: Massively tidy this shit up.
        for name, planet in self.planets.items():
            planet_sign_rulers = const.ESSENTIAL_DIGNITIES[planet.sign][const.DOMICILE]
            sign_exaltations = const.ESSENTIAL_DIGNITIES[planet.sign][const.EXALTED]
            # By sign ruler
            for planet_sign_ruler_name in planet_sign_rulers:
                if planet_sign_ruler_name == name:
                    continue
                planet_sign_ruler = self.planets[planet_sign_ruler_name]
                if name in const.ESSENTIAL_DIGNITIES[planet_sign_ruler.sign][const.DOMICILE]:
                    planet.mutual_reception = planet_sign_ruler_name
                    planet_sign_ruler.mutual_reception = name
            # By sign exaltation
            for sign_exaltation_name in sign_exaltations:
                if sign_exaltation_name == name:
                    continue
                sign_exaltation = self.planets[sign_exaltation_name]
                if name in const.ESSENTIAL_DIGNITIES[sign_exaltation.sign][const.EXALTED]:
                    planet.mutual_reception_exaltion = sign_exaltation_name
                    sign_exaltation.mutual_reception_exaltion = name

        # By house ruler
        for house_number, house in self.houses.items():
            house_rulers = const.ESSENTIAL_DIGNITIES[house.sign][const.DOMICILE]

            for house_ruler_name in house_rulers:
                planet = self.planets[house_ruler_name]
                if planet.house == house_number:
                    continue

                planet_house_rulers = const.ESSENTIAL_DIGNITIES[self.houses[planet.house].sign][const.DOMICILE]

                for planet_house_ruler_name in planet_house_rulers:
                    planet2 = self.planets[planet_house_ruler_name]
                    if planet2.house == house_number:
                        planet.mutual_reception_house = planet2.house
                        planet2.mutual_reception_house = planet.house

    """
    return None


def domiciled(index: int, lon: float) -> bool:
    """ Returns whether the passed planet is domiciled within its sign. """
    return index == options.rulerships[position.sign(lon)]


def detriment(index: int, lon: float) -> bool:
    """ Returns whether the passed planet is in detriment within its sign. """
    return position.opposite_sign(lon) == list(options.rulerships.values()).index(index) + 1


def exalted(index: int, lon: float) -> bool:
    """ Returns whether the passed planet is exalted within its sign. """
    return index == dignities.EXALTATIONS[position.sign(lon)]


def fall(index: int, lon: float) -> bool:
    """ Returns whether the passed planet is in fall within its sign. """
    return position.opposite_sign(lon) == list(dignities.EXALTATIONS.values()).index(index) + 1


def term_ruler(index: int, lon: float) -> bool:
    """ Returns whether the passed planet is the term ruler
    within its sign. """
    planet_sign, planet_sign_lon = position.signlon(lon)

    if index not in options.terms[planet_sign]:
        return False

    return options.terms[planet_sign][index][0] <= planet_sign_lon < options.terms[planet_sign][index][1]


def triplicity_ruler(index: int, lon: float) -> bool:
    """ Returns whether the passed planet is a triplicity ruler
    within its sign. """
    return index in options.triplicities[position.sign(lon)].values()


def face_ruler(index: int, lon: float) -> bool:
    """ Returns whether the passed planet is the decan ruler
    within its sign. """
    return dignities.FACE_RULERS[position.sign(lon)][position.decan(lon)-1] == index
