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

    def __str__(self):
        return f'{self.current_state=}, {self.event=}, {self.next_state=}'
