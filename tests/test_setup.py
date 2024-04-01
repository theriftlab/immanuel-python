"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    Tests for the settings class. This class is designed to act like a module
    containing global variables, but due to some settings cascading into each
    other it requires slightly more complex machinery under the hood.

"""

import os

import swisseph as swe
import pytest
from pytest import fixture

from immanuel import charts
from immanuel.classes.cache import FunctionCache
from immanuel.const import calc, chart
from immanuel.setup import settings


@fixture
def native():
    return charts.Subject('2000-01-01 10:00', '32N43.0', '117W9.0')


def teardown_function():
    settings.reset()
    FunctionCache.clear_all()


def test_attributes():
    settings.house_system = chart.POLICH_PAGE
    assert settings.house_system == chart.POLICH_PAGE

    # Cascading setting
    assert calc.CONJUNCTION in settings.aspects
    assert calc.CONJUNCTION in settings.aspect_rules[chart.SUN]['initiate']

    settings.aspects.remove(calc.CONJUNCTION)

    assert calc.CONJUNCTION not in settings.aspects
    assert calc.CONJUNCTION not in settings.aspect_rules[chart.SUN]['initiate']


def test_set():
    settings.set({
        'house_system': chart.CAMPANUS,
        'planet_aspect_rule': {
            'initiate': [calc.CONJUNCTION,],
        }
    })

    assert settings.house_system == chart.CAMPANUS
    assert settings.planet_aspect_rule['initiate'] == [calc.CONJUNCTION,]
    assert settings.aspect_rules[chart.SUN]['initiate'] == [calc.CONJUNCTION,]


def test_settings_are_respected(native):
    settings.house_system = chart.PLACIDUS
    natal = charts.Natal(native)
    assert natal.houses[chart.HOUSE2].sign.number == 1
    assert natal.houses[chart.HOUSE2].sign_longitude.formatted == '17°59\'40"'
    assert natal.houses[chart.HOUSE3].sign.number == 2
    assert natal.houses[chart.HOUSE3].sign_longitude.formatted == '19°56\'55"'

    settings.house_system = chart.CAMPANUS
    natal = charts.Natal(native)
    assert natal.houses[chart.HOUSE2].sign.number == 1
    assert natal.houses[chart.HOUSE2].sign_longitude.formatted == '25°02\'32"'
    assert natal.houses[chart.HOUSE3].sign.number == 2
    assert natal.houses[chart.HOUSE3].sign_longitude.formatted == '25°34\'25"'

    # Ensure Sun can initiate all aspects
    settings.planet_aspect_rule = {
        'initiate': settings.aspects,
    }

    natal = charts.Natal(native)
    assert len(natal.aspects[chart.SUN]) > 0

    # Ensure Sun can initiate no aspects
    settings.aspect_rules = {
        chart.SUN: {
            'initiate': [],
            'receive': [],
        }
    }

    natal = charts.Natal(native)
    assert chart.SUN not in natal.aspects


def test_add_filepath(native):
    settings.add_filepath(os.path.dirname(__file__))
    settings.objects.append(1181)
    natal = charts.Natal(native)
    assert 1181 in natal.objects

    settings.add_filepath('', True)
    FunctionCache.clear_all()

    with pytest.raises(swe.Error):
        charts.Natal(native)

    settings.add_filepath(f'{os.path.dirname(__file__)}{os.sep}..{os.sep}resources{os.sep}ephemeris')
