"""
This file is part of immanuel - (C) The Rift Lab
Author: Robert Davies (robert@theriftlab.com)


A very basic serializer class to use with the stock json module.

"""

from json import JSONEncoder


class ToJSON(JSONEncoder):
    def default(self, o) -> dict | str | None:
        if hasattr(o, "__json__"):
            return o.__json__()
        if hasattr(o, "__dict__"):
            return {k: v for k, v in o.__dict__.items() if k[0] != "_"}
        if hasattr(o, "__str__"):
            return str(o)
        return None
