from typing import Any


class GameError(Exception):
    """
    A violation of some game rule.
    """

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message

    def __str__(self) -> str:
        return f"{type(self).__name__}: {self.message}"

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": "violation",
            "message": self.message,
        }
