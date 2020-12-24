import time
import asyncio
from asyncio import Future

from typing import Final

from bloc.bloc import Bloc, Event

from rx.core import Observer

l = []

class Increment(Event):
    pass


class Decrement(Event):
    pass


class CounterBloc(Bloc[str]):

    @property
    def initial_state(self) -> str:
        return 'empty'

    async def map_event_to_state(self, event: Event) -> str:

        if isinstance(event, Increment):
            self._state = 'state 1'
            return await asyncio.sleep(5, self._state)
            # await future
            # return self._state
        else:
            self._state = 'state 2'
            return self._state
            # return self._state
        # event.future.set_result(self._state)



class SimpleBlocDelegate(Observer):

    def on_next(self, state: str) -> None:
        print(state)
        l.append(state)
        # print(state)
        # print(asyncio.gather(state))
        # print(asyncio.run(state))


async def main(bloc) -> None:
    # for state in [Increment(), Increment(), Increment(), Decrement()]:
    #     # await asyncio.gather(bloc.dispatch(state))
    #     await bloc.dispatch(state)
    #     # print('ok')

    await asyncio.gather(
        bloc.dispatch(Increment()),
        bloc.dispatch(Increment()),
        bloc.dispatch(Increment()),
        bloc.dispatch(Decrement()),
        bloc.dispatch(Increment())
    )

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    Bloc.observer = SimpleBlocDelegate()
    counter_bloc: Final[CounterBloc] = CounterBloc(
        Increment(),
        loop
    )

    # main()

    # asyncio.run(main(counter_bloc))
    # task = loop.create_task(main(counter_bloc))
    # loop.run_until_complete(task)
    loop.run_until_complete(main(counter_bloc))
    loop.close()

    print(l)
