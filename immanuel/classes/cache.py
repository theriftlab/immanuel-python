"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    Basic wrapper for the functools @cache decorator. This way we can keep
    track of which functions are being cached and can easily clear them.

"""

import functools
from typing import Callable


class FunctionCache:
    registry = []

    def clear_all() -> None:
        for cached_func in FunctionCache.registry:
            cached_func.cache_clear()


def cache(func: Callable) -> Callable:
    cached_func = functools.cache(func)
    FunctionCache.registry.append(cached_func)
    return cached_func
