from asyncio import Future

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
    def initial_state(self) -> T:
        return None

    def __init__(self, start_event, loop) -> None:
        aio_scheduler = AsyncIOScheduler(loop)
        self._event_subject.pipe(
             map(self.map_event_to_state)
        ).subscribe(self.observer, scheduler=aio_scheduler)

        # self.dispatch(start_event)

    async def dispatch(self, event: Event) -> None:
        future = Future()
        event.future = future
        self._event_subject.on_next(event)
        await future

    @property
    def state(self) -> T:
        return self._state

    @abstractmethod
    def map_event_to_state(self, event) -> str:
        ...

    def dispose(self) -> None:
        self._event_subject.dispose()
