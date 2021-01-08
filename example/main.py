import asyncio
from abc import ABC

from typing import Final

from bloc.bloc import Bloc

from aioreactive.subject import AsyncMultiSubject as Stream


l = []

class Event(ABC):
    pass


class Increment(Event):
    pass


class Decrement(Event):
    pass


class CounterBloc(Bloc[Event, str]):

    @property
    def initial_state(self) -> str:
        return 'empty'

    async def map_event_to_state(self, event: Event) -> Stream[str]:

        if isinstance(event, Increment):
            await asyncio.sleep(5)
            return 'state 1'
        else:
            return 'state 2'


async def main(bloc) -> None:
    await bloc._bind_state_subject()
    await bloc.dispatch(Increment())
    await bloc.dispatch(Decrement())
    await bloc.dispatch(Increment())
    # await asyncio.gather(
    #     bloc.dispatch(Increment()),
    #     bloc.dispatch(Increment()),
    #     bloc.dispatch(Increment()),
    #     bloc.dispatch(Decrement()),
    #     bloc.dispatch(Increment())
    # )

if __name__ == '__main__':

    counter_bloc = CounterBloc(Increment())

    asyncio.run(main(counter_bloc))

    print(l)
