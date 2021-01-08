from typing import TypeVar
from typing import Generic
from abc import ABC, abstractmethod

import aioreactive as rx
from aioreactive.subject import AsyncMultiSubject as Stream
from aioreactive.combine import pipe

from .transition import Transition
from .bloc_supervisor import bloc_supervisor

E = TypeVar('E')
S = TypeVar('S')


class Bloc(ABC, Generic[E, S]):

    def __init__(self) -> None:
        self._event_subject: Stream[E] = Stream[E]()
        self._state_subject: Stream[S] = Stream[S]()
        self._state: S = self.initial_state

    @property
    @abstractmethod
    def initial_state(self) -> S:
        ...

    async def dispatch(self, event: E) -> None:
        await self._event_subject.asend(event)

    async def _bind_state_subject(self) -> None:
        async def _map_state_to_transition(next_state: S) -> None:
            transititon = Transition[E, S](
                current_state=self.state,
                event=None,
                next_state=next_state
            )
            if bloc_supervisor.delegate is not None:
                await bloc_supervisor.delegate.on_transition(transititon)

            await self.on_transition(transititon)
            await self._state_subject.asend(next_state)

        async def update_state(next_state: S):
            self._state = next_state

        xs: rx.AsyncObservable = pipe(
            self._event_subject,
            rx.map_async(self.map_event_to_state),
        )

        await self._state_subject.subscribe_async(
            rx.AsyncAnonymousObserver(asend=update_state)
        )

        await xs.subscribe_async(
            rx.AsyncAnonymousObserver(asend=_map_state_to_transition)
        )

    async def on_transition(self, transition: Transition) -> None:
        print(
            f'Current: {transition.current_state}, '
            f'Next: {transition.next_state}, '
            f'Event: {transition.event}'
        )

    @property
    def state(self) -> S:
        return self._state

    @abstractmethod
    async def map_event_to_state(self, current_state: S, event: E) -> Stream[S]:
        ...

    async def dispose(self) -> None:
        await self._event_subject.aclose()
        await self._state_subject.aclose()



