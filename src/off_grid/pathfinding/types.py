# Source: https://www.redblobgames.com/pathfinding/a-star/implementation.html
from typing import Protocol, TypeVar

T = TypeVar("T")


class Graph(Protocol[T]):
    def neighbors(self, id: T) -> list[T]:
        ...


class WeightedGraph(Protocol[T]):
    def neighbors(self, id: T) -> list[T]:
        ...

    def cost(self, from_id: T, to_id: T) -> float:
        ...


Number = int | float
Location = tuple[Number, Number]
