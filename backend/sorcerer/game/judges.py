from abc import ABC
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Judge(ABC):
    judge_id: str = field(init=False)


def get_judge_types() -> list[type[Judge]]:
    return [
        Moira,
    ]


class Moira(Judge):
    judge_id: str = "judge_moira"
