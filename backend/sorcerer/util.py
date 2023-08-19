from enum import Enum
from datetime import datetime
from typing import Any


def asdict_factory(data: list[tuple[str, Any]]):
    """
    A customer ``dataclasses.asdict`` factory that can handle enums.
    """

    def convert_value(obj):
        if isinstance(obj, Enum):
            return obj.value
        elif isinstance(obj, datetime):
            return obj.isoformat()
        return obj

    return dict((k, convert_value(v)) for k, v in data)
