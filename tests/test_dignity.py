"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    Due to the huge amount of variables involved in testing different
    rulerships, terms, and triplicities as well as testing every planet
    in each of them, this is a fairly basic set of tests using the default
    test DOB with a select few planets, and checked against Astro Gold on iOS.

"""

import copy
from datetime import datetime

from pytest import fixture

from immanuel.const import chart, dignities
from immanuel.reports import dignity
from immanuel.setup import settings
from immanuel.tools import convert, date, ephemeris


@fixture
def coords():
    # San Diego coords as used by Astro Gold
    return [convert.string_to_dec(v) for v in ('32°42\'55"', '-117°09\'23"')]

@fixture
def jd(coords):
    return date.to_jd(date.localize(datetime.fromisoformat('2000-01-01 10:00'), *coords))

@fixture
def objects(jd):
    objects = (chart.SUN, chart.MOON, chart.MERCURY, chart.VENUS, chart.MARS, chart.JUPITER, chart.SATURN, chart.URANUS, chart.NEPTUNE, chart.PLUTO)
    return ephemeris.objects(objects, jd)

@fixture
def is_daytime(jd, coords):
    return ephemeris.is_daytime(jd, *coords)


def teardown_function():
    settings.include_participatory_triplicities = False
    settings.include_mutual_receptions = True


def test_ruler(objects):
    # Uranus is ruler of its sign
    assert dignity.ruler(objects[chart.SUN]) == False
    assert dignity.ruler(objects[chart.URANUS]) == True


def test_exalted(objects):
    # Nothing is exalted so we fudge the data
    sun = objects[chart.SUN].copy()
    assert dignity.exalted(sun) == False
    sun['lon'] = 0                          # Force it into Aries
    assert dignity.exalted(sun) == True


def test_triplicity_ruler(objects, is_daytime):
    # Nothing is triplicity ruler without participatory so we fudge the data
    sun = objects[chart.SUN].copy()
    assert dignity.triplicity_ruler(sun, is_daytime) == False
    sun['lon'] = 0                          # Force it into Aries
    assert dignity.triplicity_ruler(sun, is_daytime) == True

    # Saturn should be triplicity ruler with participatory included
    settings.include_participatory_triplicities = True
    assert dignity.triplicity_ruler(objects[chart.SATURN], is_daytime) == True


def test_term_ruler(objects):
    # Mercury is a term ruler
    assert dignity.term_ruler(objects[chart.SUN]) == False
    assert dignity.term_ruler(objects[chart.MERCURY]) == True


def test_face_ruler(objects):
    # Nothing is face ruler so we fudge the data
    sun = objects[chart.SUN].copy()
    assert dignity.face_ruler(sun) == False
    sun['lon'] = 10                         # Force it into 10° Aries
    assert dignity.face_ruler(sun) == True


def test_mutual_reception_ruler(objects):
    # Nothing is ruler by mutual reception so we fudge the data
    test_objects = copy.deepcopy(objects)
    sun = test_objects[chart.SUN]
    moon = test_objects[chart.MOON]
    assert dignity.mutual_reception_ruler(sun, test_objects) == False
    assert dignity.mutual_reception_ruler(moon, test_objects) == False
    sun['lon'] = 90                         # Force Sun into Cancer
    moon['lon'] = 120                       # Force Moon into Leo
    assert dignity.mutual_reception_ruler(sun, test_objects) == True
    assert dignity.mutual_reception_ruler(moon, test_objects) == True


def test_mutual_reception_exalted(objects):
    # Nothing is exalted by mutual reception so we fudge the data
    test_objects = copy.deepcopy(objects)
    sun = test_objects[chart.SUN]
    moon = test_objects[chart.MOON]
    assert dignity.mutual_reception_exalted(sun, test_objects) == False
    assert dignity.mutual_reception_exalted(moon, test_objects) == False
    sun['lon'] = 30                         # Force Sun into Taurus
    moon['lon'] = 0                         # Force Moon into Aries
    assert dignity.mutual_reception_exalted(sun, test_objects) == True
    assert dignity.mutual_reception_exalted(moon, test_objects) == True


def test_mutual_reception_triplicity_ruler(objects, is_daytime):
    # Sun & Venus are triplicity rulers by mutual reception
    assert dignity.mutual_reception_triplicity_ruler(objects[chart.SUN], objects, is_daytime) == True
    assert dignity.mutual_reception_triplicity_ruler(objects[chart.VENUS], objects, is_daytime) == True
    assert dignity.mutual_reception_triplicity_ruler(objects[chart.MOON], objects, is_daytime) == False


def test_mutual_reception_term_ruler(objects):
    # Nothing is term ruler by mutual reception so we fudge the data
    test_objects = copy.deepcopy(objects)
    mars = test_objects[chart.MARS]
    venus = test_objects[chart.VENUS]
    assert dignity.mutual_reception_term_ruler(mars, test_objects) == False
    assert dignity.mutual_reception_term_ruler(venus, test_objects) == False
    mars['lon'] = 6                         # Force Mars into 6° Aries
    venus['lon'] = 57                       # Force venus into 27° Taurus
    assert dignity.mutual_reception_term_ruler(mars, test_objects) == True
    assert dignity.mutual_reception_term_ruler(venus, test_objects) == True


def test_mutual_reception_face_ruler(objects):
    # Nothing is face ruler by mutual reception so we fudge the data
    test_objects = copy.deepcopy(objects)
    sun = test_objects[chart.SUN]
    moon = test_objects[chart.MOON]
    assert dignity.mutual_reception_face_ruler(sun, test_objects) == False
    assert dignity.mutual_reception_face_ruler(moon, test_objects) == False
    sun['lon'] = 40                         # Force Sun into 10° Taurus
    moon['lon'] = 10                        # Force Moon into 10° Aries
    assert dignity.mutual_reception_face_ruler(sun, test_objects) == True
    assert dignity.mutual_reception_face_ruler(moon, test_objects) == True


def test_in_rulership_element(objects):
    # Moon is in a Water sign, Sun is in an Earth sign
    assert dignity.in_rulership_element(objects[chart.SUN]) == False
    assert dignity.in_rulership_element(objects[chart.MOON]) == True


def test_detriment(objects):
    # Nothing is in detriment so we fudge the data
    sun = objects[chart.SUN].copy()
    assert dignity.detriment(sun) == False
    sun['lon'] = 300                        # Force it into Aquarius
    assert dignity.detriment(sun) == True


def test_fall(objects):
    # Moon is in fall in Scorpio
    assert dignity.fall(objects[chart.SUN]) == False
    assert dignity.fall(objects[chart.MOON]) == True


def test_all(objects, is_daytime):
    all = {}

    for object in objects.values():
        all[object['index']] = dignity.all(object, objects, is_daytime)

    assert all[chart.SUN][dignities.MUTUAL_RECEPTION_TRIPLICITY_RULER] == True
    assert all[chart.SUN][dignities.PEREGRINE] == False
    assert all[chart.MOON][dignities.IN_RULERSHIP_ELEMENT] == True
    assert all[chart.MOON][dignities.FALL] == True
    assert all[chart.MERCURY][dignities.TERM_RULER] == True
    assert all[chart.VENUS][dignities.MUTUAL_RECEPTION_TRIPLICITY_RULER] == True
    assert all[chart.VENUS][dignities.PEREGRINE] == False
    assert all[chart.MARS][dignities.PEREGRINE] == True
    assert all[chart.JUPITER][dignities.IN_RULERSHIP_ELEMENT] == True
    assert all[chart.SATURN][dignities.IN_RULERSHIP_ELEMENT] == True
    assert all[chart.URANUS][dignities.RULER] == True
    assert all[chart.URANUS][dignities.IN_RULERSHIP_ELEMENT] == True
    assert all[chart.NEPTUNE][dignities.FALL] == True
    assert all[chart.NEPTUNE][dignities.PEREGRINE] == True
    assert all[chart.PLUTO][dignities.PEREGRINE] == True

    settings.include_mutual_receptions = False

    for object in objects.values():
        all[object['index']] = dignity.all(object, objects, is_daytime)

    assert all[chart.SUN][dignities.MUTUAL_RECEPTION_TRIPLICITY_RULER] == True
    assert all[chart.SUN][dignities.PEREGRINE] == True
    assert all[chart.MOON][dignities.IN_RULERSHIP_ELEMENT] == True
    assert all[chart.MOON][dignities.FALL] == True
    assert all[chart.MERCURY][dignities.TERM_RULER] == True
    assert all[chart.VENUS][dignities.MUTUAL_RECEPTION_TRIPLICITY_RULER] == True
    assert all[chart.VENUS][dignities.PEREGRINE] == True
    assert all[chart.MARS][dignities.PEREGRINE] == True
    assert all[chart.JUPITER][dignities.IN_RULERSHIP_ELEMENT] == True
    assert all[chart.SATURN][dignities.IN_RULERSHIP_ELEMENT] == True
    assert all[chart.URANUS][dignities.RULER] == True
    assert all[chart.URANUS][dignities.IN_RULERSHIP_ELEMENT] == True
    assert all[chart.NEPTUNE][dignities.FALL] == True
    assert all[chart.NEPTUNE][dignities.PEREGRINE] == True
    assert all[chart.PLUTO][dignities.PEREGRINE] == True


def test_score(objects, is_daytime):
    # Astro Gold only calculates scores for the main 7 planets
    scores = {}

    for object in objects.values():
        scores[object['index']] = dignity.score(dignity.all(object, objects, is_daytime))

    assert scores[chart.SUN] == 3
    assert scores[chart.MOON] == -4
    assert scores[chart.MERCURY] == 2
    assert scores[chart.VENUS] == 3
    assert scores[chart.MARS] == -5
    assert scores[chart.JUPITER] == 0
    assert scores[chart.SATURN] == 0

    settings.include_mutual_receptions = False

    for object in objects.values():
        scores[object['index']] = dignity.score(dignity.all(object, objects, is_daytime))

    assert scores[chart.SUN] == -2
    assert scores[chart.MOON] == -4
    assert scores[chart.MERCURY] == 2
    assert scores[chart.VENUS] == -2
    assert scores[chart.MARS] == -5
    assert scores[chart.JUPITER] == 0
    assert scores[chart.SATURN] == 0
