from typing import Final
from typing import TypeVar

import dataclasses

import asyncio
from asyncio import Future
import rx
from rx import Observable
import rx.operators as ops
from rx.subject import Subject
from rx.scheduler.eventloop import AsyncIOScheduler


@dataclasses.dataclass
class EchoItem:
    future: Future
    data: Final[str]


def tcp_server(sink: Subject, loop) -> Observable:
    def on_subscribe(observer, scheduler):
        async def handle_echo(reader, writer):
            print("new client connected")
            while True:
                data = await reader.readline()
                data = data.decode("utf-8")
                if not data:
                    break

                future = Future()

                observer.on_next(
                    EchoItem(
                        future=future,
                        data=data
                    )
                )
                await future

                writer.write(future.result().encode("utf-8"))

            print("Close the client socket")
            writer.close()

        def on_next(echo_item: EchoItem):
            echo_item.future.set_result(echo_item.data)

        print("starting server")
        server = asyncio.start_server(handle_echo, '127.0.0.1', 8888, loop=loop)
        loop.create_task(server)

        sink.subscribe(
            on_next=on_next,
            on_error=observer.on_error,
            on_completed=observer.on_completed
        )

    return rx.create(on_subscribe)


async def print_(echo_item: EchoItem) -> EchoItem:
    print(echo_item.data)
    return echo_item


Sink = TypeVar('sink')

loop = asyncio.get_event_loop()
proxy: Sink = Subject()
source: Observable = tcp_server(proxy, loop)
aio_scheduler = AsyncIOScheduler(loop=loop)

source.subscribe(proxy, scheduler=aio_scheduler)

# source.pipe(
#     # ops.map(lambda echo_item: echo_item.data = (data="echo: {}".format(i.data))),
#     ops.map(lambda echo_item: EchoItem(data="echo: {}".format(echo_item.data))),
#     # ops.map(print_),
#     ops.delay(5.0)
# ).subscribe(proxy, scheduler=aio_scheduler)

loop.run_forever()

loop.run_forever()
print("done")
loop.close()
