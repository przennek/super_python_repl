from dataclasses import dataclass


@dataclass
class Invoice:
    name: str
    type: str
    date: str


def session_state() -> str:
    return "ACTIVE!"

