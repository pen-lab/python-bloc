import asyncio
from abc import ABC


from bloc import (
    BlocSupervisor,
    BlocDelegate,
    Transition,
    Stream,
    Bloc
)
from bloc._bloc.bloc import E, S


class Event(ABC):
    def __repr__(self): return self.__class__.__name__


class Increment(Event):
    pass


class Decrement(Event):
    pass


class CounterBloc(Bloc[Event, int]):

    @property
    def initial_state(self) -> int: return 10

    async def map_event_to_state(self, event: Event):

        if isinstance(event, Increment):
            await asyncio.sleep(5)
            await self.update_state(event, self.state + 1)
        else:
            await self.update_state(event, self.state - 1)

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
