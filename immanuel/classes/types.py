"""
This file is part of immanuel - (C) The Rift Lab
Author: Robert Davies (robert@theriftlab.com)


Defines custom types used throughout Immanuel.

"""

from typing import Protocol


class Stringable(Protocol):
    def __str__(self) -> str: ...
