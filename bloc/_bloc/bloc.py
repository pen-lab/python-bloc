import dataclasses

from typing import TypeVar
from typing import Generic
from abc import ABC, abstractmethod

import aioreactive as rx
from aioreactive.subject import AsyncMultiSubject as Stream
from aioreactive.combine import pipe

from .transition import Transition
from .bloc_supervisor import bloc_supervisor

E = TypeVar('E')
"""
Docs
"""

S = TypeVar('S')
"""
Docs
"""


@dataclasses.dataclass
class BlocData(Generic[E, S]):
    event: E
    state: S
    

class Bloc(ABC, Generic[E, S]):

    def __init__(self) -> None:
        self._event_subject: Stream[E] = Stream[E]()
        self._state_subject: Stream[BlocData[E, S]] = Stream[BlocData[E, S]]()
        self._state: S = self.initial_state

    @property
    @abstractmethod
    def initial_state(self) -> S:
        ...

    async def dispatch(self, event: E) -> None:
        await self._event_subject.asend(event)

    async def update_state(self, event: E, next_state: S) -> None:
        await self._state_subject.asend(BlocData(event, next_state))

    async def _bind_state_subject(self) -> None:
        async def _map_state_to_transition(bloc_data: BlocData[E, S]) -> None:
            transititon = Transition[E, S](
                current_state=self.state,
                event=bloc_data.event,
                next_state=bloc_data.state
            )

            if bloc_supervisor.delegate is not None:
                await bloc_supervisor.delegate.on_transition(transititon)

            await self.on_transition(transititon)
            self._state = bloc_data.state

        xs: rx.AsyncObservable = pipe(
            self._event_subject,
        )

        await xs.subscribe_async(
            rx.AsyncAnonymousObserver(asend=self.map_event_to_state)
        )

        await self._state_subject.subscribe_async(
            rx.AsyncAnonymousObserver(asend=_map_state_to_transition)
        )

    @abstractmethod
    async def on_transition(self, transition: Transition[E, S]) -> None:
        ...

    @property
    def state(self) -> S:
        return self._state

    # TODO: add current_state
    @abstractmethod
    async def map_event_to_state(self, event: E) -> Stream[S]:
        ...

    async def dispose(self) -> None:
        await self._event_subject.aclose()
        await self._state_subject.aclose()
