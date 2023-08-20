from abc import ABC, abstractmethod
from typing import Any


class ToDict(ABC):
    @abstractmethod
    def to_dict(self) -> dict[str, Any]:
        raise NotImplementedError()
