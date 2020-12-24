from asyncio import Future, sleep

from typing import Final
from typing import Any
from typing import TypeVar
from typing import Generic
from abc import ABC, abstractmethod

from rx.subject import Subject
from rx.operators import map
from rx.core import Observer
from rx.scheduler.eventloop import AsyncIOScheduler


T = TypeVar('T')


class Event:
    future: Future


class Bloc(ABC, Generic[T]):

    _event_subject: Final[Subject] = Subject()

    _state: T = None

    observer: Final[Observer]

    @property
    @abstractmethod
    def initial_state(self) -> T:
        ...

    def __init__(self, start_event, loop) -> None:
        aio_scheduler = AsyncIOScheduler(loop)
        # self._event_subject.pipe(
        #      map(self.map_event_to_state)
        # ).subscribe(self.observer, scheduler=aio_scheduler)
        #
        self._event_subject.subscribe(self.observer, scheduler=aio_scheduler)

        # self.dispatch(start_event)

    async def dispatch(self, event: Event) -> None:
        # await sleep(5)

        # future = Future()
        # event.future = future
        state = await self.map_event_to_state(event)
        self._event_subject.on_next(state)
        # await future

    @property
    def state(self) -> T:
        return self._state

    @abstractmethod
    async def map_event_to_state(self, event: Event) -> T:
        ...

    def dispose(self) -> None:
        self._event_subject.dispose()
