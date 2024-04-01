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


class Localize:
    lcid = None
    translation = None

    def set_locale(lcid: str) -> None:
        FunctionCache.clear_all()

        localedir = f'{os.path.dirname(__file__)}{os.sep}..{os.sep}..{os.sep}locales'
        languages = (lcid, lcid[:2])
        translation = gettext.translation('immanuel', localedir=localedir, languages=languages, fallback=True)

        if isinstance(translation, gettext.GNUTranslations):
            Localize.lcid = lcid
            Localize.translation = translation
            locale.setlocale(locale.LC_TIME, lcid)
        else:
            Localize.reset()

    def reset() -> None:
        Localize.lcid = None
        Localize.translation = None
        locale.setlocale(locale.LC_TIME, 'en_US')


def _(input: str) -> str:
    if Localize.translation is None:
        return input

    return Localize.translation.gettext(input)
