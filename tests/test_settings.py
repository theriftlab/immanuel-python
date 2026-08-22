"""
This file is part of immanuel - (C) The Rift Lab
Author: Robert Davies (robert@theriftlab.com)


Tests for the settings module. These come in two parts - first the per-chart
settings via the ChartConfig class, and second the global, per-process settings via
the module's functions.

"""

import os

import pytest
import swisseph as swe
from pytest import fixture

from immanuel import charts, settings
from immanuel.const import calc, chart
from immanuel.settings import ChartConfig


@fixture
def native():
    return charts.Subject("2000-01-01 10:00", "32N43.0", "117W9.0")


def teardown_function():
    settings.reset_swe_filepath()


def test_config_attributes():
    config = ChartConfig()
    config.house_system = chart.POLICH_PAGE
    assert config.house_system == chart.POLICH_PAGE
    # Cascading setting
    assert calc.CONJUNCTION in config.aspects
    assert calc.CONJUNCTION in config.aspect_rules[chart.SUN]["initiate"]
    config.aspects.remove(calc.CONJUNCTION)
    assert calc.CONJUNCTION not in config.aspects
    assert calc.CONJUNCTION not in config.aspect_rules[chart.SUN]["initiate"]


def test_config_is_respected(native):
    config = ChartConfig()
    config.house_system = chart.PLACIDUS
    natal = charts.Natal(native, config=config)
    assert natal.houses[chart.HOUSE2].sign.number == 1
    assert natal.houses[chart.HOUSE2].sign_longitude.formatted == "17°59'40\""
    assert natal.houses[chart.HOUSE3].sign.number == 2
    assert natal.houses[chart.HOUSE3].sign_longitude.formatted == "19°56'55\""
    config.house_system = chart.CAMPANUS
    natal = charts.Natal(native, config=config)
    assert natal.houses[chart.HOUSE2].sign.number == 1
    assert natal.houses[chart.HOUSE2].sign_longitude.formatted == "25°02'32\""
    assert natal.houses[chart.HOUSE3].sign.number == 2
    assert natal.houses[chart.HOUSE3].sign_longitude.formatted == "25°34'25\""
    # Ensure Sun can initiate all aspects
    config.planet_aspect_rule = {
        "initiate": config.aspects,
    }
    natal = charts.Natal(native, config=config)
    assert len(natal.aspects[chart.SUN]) > 0
    # Ensure Sun can initiate no aspects
    config.aspect_rules = {
        chart.SUN: {
            "initiate": [],
            "receive": [],
        }
    }
    natal = charts.Natal(native, config=config)
    assert chart.SUN not in natal.aspects


def test_add_filepath(native):
    settings.add_swe_filepath(os.path.dirname(__file__))
    config = ChartConfig()
    config.objects.append(1181)
    natal = charts.Natal(native, config=config)
    assert 1181 in natal.objects
    settings.add_swe_filepath("", True)
    with pytest.raises(swe.Error):
        charts.Natal(native)


def test_reset(native):
    settings.add_swe_filepath(os.path.dirname(__file__))
    config = ChartConfig()
    config.objects.append(1181)
    natal = charts.Natal(native, config=config)
    assert 1181 in natal.objects
    settings.reset_swe_filepath()
    with pytest.raises(swe.Error):
        charts.Natal(native, config=config)
