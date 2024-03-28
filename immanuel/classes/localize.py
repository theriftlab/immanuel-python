"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    Set up translations.

"""

import gettext, locale, os
from pathlib import Path

from immanuel.setup import settings


class Localize:
    translation = None

    def get_translation() -> gettext.NullTranslations:
        if Localize.translation is None:
            localedir = (Path(__file__).parent.parent.parent / 'locales').absolute()
            languages = [settings.locale]

            Localize.translation = gettext.translation('immanuel', localedir=localedir, languages=languages, fallback=True)

            if os.path.exists(localedir / settings.locale):
                locale.setlocale(locale.LC_TIME, '' if settings.locale is None else settings.locale)

        return Localize.translation

def _(input: str) -> str:
    if settings.locale is None:
        return input

    return Localize.get_translation().gettext(input)
