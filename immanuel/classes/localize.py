"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    Sets up translations and provides our own _() function. This will look for
    a translation file for the full locale and fall back to the parent locale,
    for example pt_BR then pt. If a file is found, then the full locale string
    (eg. pt_BR) will be passed to locale.setlocale() for localizing datetimes.

"""

import gettext, locale
from pathlib import Path

from immanuel.setup import settings


class Localize:
    translation = None

    def get_translation() -> gettext.NullTranslations | gettext.GNUTranslations:
        if Localize.translation is None:
            localedir = (Path(__file__).parent.parent.parent / 'locales').absolute()
            languages = [settings.locale, settings.locale[:2]]

            Localize.translation = gettext.translation('immanuel', localedir=localedir, languages=languages, fallback=True)

            if isinstance(Localize.translation, gettext.GNUTranslations):
                locale.setlocale(locale.LC_TIME, settings.locale)

        return Localize.translation

def _(input: str) -> str:
    if settings.locale is None:
        return input

    return Localize.get_translation().gettext(input)
