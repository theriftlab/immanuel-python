"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    Set up translations.

"""

import gettext
from pathlib import Path

from immanuel.setup import settings


class Localize:
    translation = None

    def get_translation() -> gettext.NullTranslations:
        if Localize.translation is None:
            localedir = (Path(__file__).parent.parent.parent / 'locales').absolute()
            languages = [settings.language]
            Localize.translation = gettext.translation('immanuel', localedir=localedir, languages=languages, fallback=True)

        return Localize.translation

def _(input: str) -> str:
    return Localize.get_translation().gettext(input)
