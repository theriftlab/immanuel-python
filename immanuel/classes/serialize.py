"""
    This file is part of immanuel - (C) The Rift Lab
    Author: Robert Davies (robert@theriftlab.com)


    A very basic serializer class to use with the stock json module.

"""

from json import JSONEncoder


class ToJSON(JSONEncoder):
    def default(self, obj) -> dict | str | None:
        if hasattr(obj, 'to_json'):
            return obj.to_json()

        if hasattr(obj, '__dict__'):
            return {k: v for k, v in obj.__dict__.items() if k[0] != '_'}

        if hasattr(obj, '__str__'):
            return str(obj)

        return None
