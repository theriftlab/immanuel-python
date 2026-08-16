"""
This file is part of immanuel - (C) The Rift Lab
Author: Robert Davies (robert@theriftlab.com)


Sets up translations and provides our own localize() function. This will
look for a translation file for the full locale and fall back to the parent
locale, for example pt_BR then pt.

Weekday and month names are translated from dicts in const.dates,
so localizing the datetime format depends only on the translation files
rather than OS-level locales.

"""

import gettext
import os

from immanuel.classes.types import Stringable
from immanuel.const import genders

MAPPINGS = {}


class Localize:
    lcid = None
    translation = None
    localedir = f"{os.path.dirname(__file__)}{os.sep}..{os.sep}locales"

    @staticmethod
    def set_locale(lcid: str) -> None:
        languages = (lcid, lcid[:2])
        translation = gettext.translation(
            "immanuel", localedir=Localize.localedir, languages=languages, fallback=True
        )
        if isinstance(translation, gettext.GNUTranslations):
            Localize.lcid = lcid
            Localize.translation = translation
            mappings_path = (
                f"{Localize.localedir}{os.sep}{Localize.lcid}{os.sep}mappings.py"
            )
            if os.path.isfile(mappings_path):
                with open(mappings_path, "r") as mappings:
                    exec(mappings.read(), MAPPINGS)
        else:
            Localize.reset()

    @staticmethod
    def reset() -> None:
        Localize.lcid = None
        Localize.translation = None
        MAPPINGS.clear()


def localize(input: str | Stringable, context: str | None = None) -> str:
    input = str(input)
    if Localize.translation is None:
        return input
    if context is None:
        return Localize.translation.gettext(input)
    else:
        contextualized = Localize.translation.pgettext(context, input)
        return (
            contextualized
            if contextualized != input
            else Localize.translation.gettext(input)
        )


def gender(index: int | float) -> str | None:
    if Localize.translation is None:
        return None
    return (
        MAPPINGS["GENDERS"][index]
        if index in MAPPINGS["GENDERS"]
        else genders.AMBIGUOUS
    )
