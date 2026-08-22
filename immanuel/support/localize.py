"""
This file is part of immanuel - (C) The Rift Lab
Author: Robert Davies (robert@theriftlab.com)


Sets up translations and provides our own localize() function. This will
look for a translation file for the full locale and fall back to the parent
locale, for example pt_BR then pt.

Weekday and month names are translated from dicts in const.names,
so localizing the datetime format depends only on the translation files
rather than OS-level locales.

"""

import gettext
import importlib
import os
from typing import Protocol

_TRANSLATIONS = {}

_CONTEXTS = {}

_LOCALEDIR = f"{os.path.dirname(__file__)}{os.sep}..{os.sep}locales"


class Stringable(Protocol):
    """This allows us to translate any object that implements __str__()
    in our localize() as if it were a string."""

    def __str__(self) -> str: ...


def load_locale(lcid: str) -> bool:
    """If available, loads the translation and contexts for the given locale
    into our module's dict cache. Returns True if the locale was successfully
    loaded, False otherwise."""
    if lcid in _TRANSLATIONS:
        return True
    translation = gettext.translation(
        "immanuel",
        localedir=_LOCALEDIR,
        languages=(lcid, lcid[:2]),
        fallback=True,
    )
    if isinstance(translation, gettext.GNUTranslations):
        _TRANSLATIONS[lcid] = translation
        try:
            _CONTEXTS[lcid] = importlib.import_module(
                f"immanuel.locales.{lcid}.contexts"
            ).CONTEXTS
        except ModuleNotFoundError:
            pass  # we can still translate without contexts
        return True
    return False


def localize(
    input: str | Stringable, lcid: str | None, context: str | tuple | None = None
) -> str:
    """Localizes a string or Stringable object to the given locale, if
    available, and auto-loads the locale if not already loaded. The context
    can be either a plain string, or a (type, key) tuple if the context depends
    on a key-value pair like the gender list."""
    input = str(input)
    if lcid is None or (lcid not in _TRANSLATIONS and not load_locale(lcid)):
        return input
    translation = _TRANSLATIONS[lcid]
    if context is None:
        return translation.gettext(input)
    if isinstance(context, tuple):
        context_type, context_key = context
        contexts = _CONTEXTS[lcid].get(context_type)
        if contexts is not None and context_key in contexts:
            context = contexts[context_key]
        else:
            return translation.gettext(input)
    contextualized = translation.pgettext(context, input)
    return contextualized if contextualized != input else translation.gettext(input)
