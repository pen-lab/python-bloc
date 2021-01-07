import dataclasses
from typing import Generic
from typing import TypeVar

E = TypeVar('E')
S = TypeVar('S')


@dataclasses.dataclass
class Transition(Generic[E, S]):
    current_state: S
    event: E
    next_state: S