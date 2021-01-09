import asyncio
from abc import ABC

from typing import AsyncGenerator


from bloc import (
    BlocSupervisor,
    BlocDelegate,
    Transition,
    Bloc
)



class Event(ABC):
    def __repr__(self): return self.__class__.__name__


class Increment(Event):
    pass


class Decrement(Event):
    pass


class CounterBloc(Bloc[Event, int]):

    @property
    def initial_state(self) -> int: return 10

    async def map_event_to_state(self, event: Event) -> AsyncGenerator[int, None]:

        if isinstance(event, Increment):
            await asyncio.sleep(5)
            yield self.state + 1
        else:
            yield self.state - 1

    async def on_transition(self, transition: Transition[Event, int]) -> None:
        print(f'{transition}')


class SimpleBlocDelegate(BlocDelegate):

    async def on_transition(self, transition: Transition) -> None:
        print(f'{transition}')


async def main(bloc: Bloc) -> None:
    await bloc._bind_state_subject()

    await asyncio.gather(
        bloc.dispatch(Increment()),
        bloc.dispatch(Decrement()),
        bloc.dispatch(Increment())
    )


if __name__ == '__main__':
    BlocSupervisor().delegate = SimpleBlocDelegate()
    counter_bloc = CounterBloc()

    asyncio.run(main(counter_bloc))
