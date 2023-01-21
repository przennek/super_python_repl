from dataclasses import dataclass


@dataclass
class Invoices:
    name: str
    type: str
    date: str


def session_state() -> str:
    return "ACTIVE!"
