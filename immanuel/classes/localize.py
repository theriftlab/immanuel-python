"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    Sets up translations and provides our own _() function. This will look for
    a translation file for the full locale and fall back to the parent locale,
    for example pt_BR then pt. If a file is found, then the full locale string
    (eg. pt_BR) will be passed to locale.setlocale() for localizing datetimes.

"""

import gettext, locale, os

from immanuel.classes.cache import FunctionCache
from immanuel.const import genders


MAPPINGS = {}


class Localize:
    lcid = None
    translation = None
    localedir = f'{os.path.dirname(__file__)}{os.sep}..{os.sep}locales'

    def set_locale(lcid: str) -> None:
        FunctionCache.clear_all()

        languages = (lcid, lcid[:2])
        translation = gettext.translation('immanuel', localedir=Localize.localedir, languages=languages, fallback=True)

        if isinstance(translation, gettext.GNUTranslations):
            Localize.lcid = lcid
            Localize.translation = translation
            locale.setlocale(locale.LC_TIME, lcid)

            mappings_path = f'{Localize.localedir}{os.sep}{Localize.lcid}{os.sep}mappings.py'

            if os.path.isfile(mappings_path):
                with open(mappings_path, 'r') as mappings:
                    exec(mappings.read(), MAPPINGS)
        else:
            Localize.reset()

    def reset() -> None:
        FunctionCache.clear_all()
        Localize.lcid = None
        Localize.translation = None
        locale.setlocale(locale.LC_TIME, 'en_US')
        MAPPINGS = {}


def _(input: str, context: str = None) -> str:
    if Localize.translation is None:
        return input

    if context is None:
        return Localize.translation.gettext(input)
    else:
        contextualized = Localize.translation.pgettext(context, input)
        return contextualized if contextualized != input else Localize.translation.gettext(input)


def gender(index: int|float) -> str:
    if Localize.translation is None:
        return None

    return MAPPINGS['GENDERS'][index] if index in MAPPINGS['GENDERS'] else genders.AMBIGUOUS
