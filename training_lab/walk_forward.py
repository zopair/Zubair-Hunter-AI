"""Chronological walk-forward splitter with purge/embargo."""
from dataclasses import dataclass

@dataclass
class Split:
    train: tuple[int,int]
    validation: tuple[int,int]
    test: tuple[int,int]


def split(n: int, train=0.60, validation=0.20, purge=100, embargo=100) -> Split:
    a = int(n * train); b = int(n * (train + validation))
    return Split((0, max(0, a-purge)), (a+embargo, max(a+embargo, b-purge)), (b+embargo, n))
