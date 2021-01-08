from abc import ABC, abstractmethod
from .transition import Transition


class BlocDelegate(ABC):

    @abstractmethod
    async def on_transition(self, transition: Transition) -> None:
        ...
