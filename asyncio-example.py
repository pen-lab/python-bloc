import asyncio
import time

class Timer:
    def __init__(self, coro) -> None:
        self.coro = coro
        self.spend = 0


    def __await__(self):
        started = time.monotonic()
        result = yield from self.coro.__await__()
        self.spend = time.monotonic() - started
        return result


async def main():
    t = Timer(asyncio.sleep(1, 'test'))

    res = await t
    print(res)
    print(t.spend)


## Future

import asyncio
from asyncio import Future


async def my_sleep(delay):
    loop = asyncio.get_running_loop()
    future: Future = loop.create_future()
    loop.call_later(delay, future.set_result, True)
    await future


async def main():
    loop = asyncio.get_running_loop()
    print(loop.time())
    await my_sleep(1)
    print(loop.time())


asyncio.run(main())


## Несколько задач

from typing import List
from asyncio import Future, Task


# async def check_user_exists(user_id: int) -> bool:
#     async with aiohttp.ClientSession() as session:
#         url = f'https://example.org/users/{user_id}'
#         async with session.head(url) as resp:
#             print(user_id, resp.status == 200)
#             return resp.status == 200

async def check_user_exists(user_id: int) -> int:
    await asyncio.sleep(12 - user_id)
    print(f'check_user_exists: {user_id}')
    return user_id


async def main():
    future: Future = asyncio.get_running_loop().create_future()
    tasks: List[Task] = []
    executing: int = 0

    def cb(task: Task):
        nonlocal executing
        executing -= 1
        tasks.append(task)
        if executing == 0:
            future.set_result([task.result() for task in tasks])

    for i in range(10):
        task = asyncio.create_task(check_user_exists(i))
        task.add_done_callback(cb)
        executing += 1


    await future
    print(future.result())

asyncio.run(main())

async def sync_main():
    for i in range(10):
        print(await check_user_exists(i))

asyncio.run(sync_main())


async def coros_main():
    coros = (
        check_user_exists(i)
        for i in range(10)
    )
    # return coros

    resutls = await asyncio.gather(*coros) #<coroutine object coros_main at 0x7fc686e6dec0>
    print(resutls)

asyncio.run(coros_main())


## Errors

async def trigger(position):
    await asyncio.sleep(position)
    if position == 3:
        raise RuntimeError('Boom!')

    print(f'{position} is ok')

async def russian_roulette() -> None:
    coros = (trigger(i) for i in range(8))

    try:
        await asyncio.gather(*coros)
        # await asyncio.gather(*coros, return_exceptions=False)
    except RuntimeError as e:
        print(e)

    await asyncio.sleep(10)

asyncio.run(russian_roulette())


## Cancel task

async def coro() -> None:
    try:
        print('start')
        await asyncio.sleep(2)
        print('finished')
    finally:    # выполнится после tack.cancel()
        print('last canceled')


async def cancel(task: Task) -> None:
    await asyncio.sleep(0.5)
    task.cancel()

    print('task.cancel() called')

    try:
        await task
    except asyncio.CancelledError:
        print('task successfully cancelled')


async def main():
    task = asyncio.create_task(coro())

    asyncio.create_task(cancel(task))

    await asyncio.sleep(5)

    assert task.cancelled()

asyncio.run(main())


## Используем asyncio.shield()


async def coro() -> None:
    try:
        print('start')
        await asyncio.sleep(2)
        print('finished')
    finally:    # выполнится после tack.cancel()
        print('last canceled')


async def cancel(task: Task) -> None:
    await asyncio.sleep(0.5)
    task.cancel()

    print('task.cancel() called')

    try:
        await task
    except asyncio.CancelledError:
        print('task successfully cancelled')


async def main():
    task = asyncio.create_task(coro())

    asyncio.create_task(
        cancel(
            asyncio.shield(task)
        )
    )

    await asyncio.sleep(5)
    assert task.cancelled()

asyncio.run(main())


## Ипользуем asyncio.wait_for()

async def eternity() -> None:
    try:
        await asyncio.sleep(3600)
    except asyncio.CancelledError:
        print('i was cancelled')
        raise
    print('finished')


async def main() -> None:
    try:
        await asyncio.wait_for(eternity(), timeout=1.0)
    except asyncio.TimeoutError:
        print('timeout')

asyncio.run(main())


## asyncio.wait


async def check_user_exists(user_id: int) -> int:
    await asyncio.sleep(12 - user_id)
    print(f'check_user_exists: {user_id}')
    return user_id


async def main():

    tasks = [
        asyncio.create_task(check_user_exists(i))
        for i in range(10)
    ]

    # Задачи выполненные за 6 мс
    # done, pending = await asyncio.wait(tasks, timeout=6)

    # До первой выполненной задачи
    done, pending = await asyncio.wait(
        tasks,
        return_when=asyncio.FIRST_COMPLETED
    )

    print(done, pending)

asyncio.run(main())

## asyncio.as_complated - в порядке выполнения


async def delayed_result(delay):
    if delay == 2:
        return 2
    return await asyncio.sleep(10 - delay, delay)


async def main():
    tasks = [
        delayed_result(i)
        for i in range(10)
    ]

    for earliest in asyncio.as_completed(tasks):
        result = await earliest
        print(result)

asyncio.run(main())

## Все задачи запущенные в цикле


async def check_user_exists(user_id: int) -> int:
    await asyncio.sleep(12 - user_id)
    print(f'check_user_exists: {user_id}')
    return user_id


async def main():
    coros = (
        check_user_exists(i)
        for i in range(10)
    )

    asyncio.gather(*coros)
    await asyncio.sleep(2)
    tasks = asyncio.all_tasks()

    print(type(tasks))
    print(tasks)

asyncio.run(main())


## Policy

# asyncio.WindowsProactorEventLoopPolicy
# asyncio.ProactorEventLoop
# asyncio.SelectorEventLoop

import asyncio

asyncio.set_event_loop_policy(
    asyncio.WindowsProactorEventLoopPolicy()
)

# github: uvloop

#_run_once()

import selectors # посмотреть

## Запуск блокируемого кода

from concurrent import futures

def blocking_io():
    with open('/dev/urandom', 'rb') as f:
        return f.read(100)


def cpu_bound():
    return sum(i * i for i in range(10 ** 7))


async def main():
    loop = asyncio.get_running_loop()

    resutl = await loop.run_in_executor(None, blocking_io)
    print('default thread pool', resutl)


    with futures.ThreadPoolExecutor() as pool:
        resutl = await loop.run_in_executor(pool, blocking_io)
        print('default thread pool', resutl)



    with futures.ProcessPoolExecutor() as pool:
        resutl = await loop.run_in_executor(pool, blocking_io)
        print('default process pool', resutl)

asyncio.run(main())


## async with


class TransactionCtx:
    def __init__(self, conn):
        self.conn = conn

    async def __aenter__(self):
        await self.conn.execute('Begin')
        print('entering context')
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        command = 'ROLLBACK' if exc_val else 'COMMIT'
        await self.conn.execute(command)
        print('exiting context')


class Connect:
    def __init__(self, delay: int):
        self.delay = delay

    def raise_err(self):
        raise RuntimeError

    async def execute(self, command):
        await asyncio.sleep(self.delay)
        print(f'conn: {command}')


async def main():

    async def trans(conn):
        async with TransactionCtx(conn) as transaction:
            await asyncio.sleep(2)
            conn.raise_err()
            print('transaction')

    async def raise_err(conn: Connect):
        await asyncio.sleep(2)
        print('ok')
        # conn.raise_err()

    conn = Connect(4)

    await asyncio.gather(
        trans(conn),
        raise_err(conn)
    )
    print('completed')

asyncio.run(main())


## Асинхронный итератор


class Ticker:
    def __init__(self, delay, to):
        self.delay = delay
        self.i = 0
        self.to = to

    def __aiter__(self):
        return self

    async def __anext__(self):
        i = self.i
        if i >= self.to:
            raise StopAsyncIteration
        self.i += 1

        if i:
            await asyncio.sleep(self.delay)

        return i


async def main():

    async def ticker_1():
        async for i in Ticker(2, 3):
            print(f'Ticker 1: {i}')

    async def ticker_2():
        async for i in Ticker(4, 2):
            print(f'Ticker 2: {i}')

    await asyncio.gather(
        ticker_1(),
        ticker_2()
    )
    print('completed')

asyncio.run(main())


## Асинхронный генератор


async def ticker(delay, to):
    for i in range(to):
        yield i
        await asyncio.sleep(delay)

async def main():

    async def ticker_1():
        async for i in ticker(2, 3):
            print(f'Ticker 1: {i}')

    async def ticker_2():
        async for i in ticker(4, 2):
            print(f'Ticker 2: {i}')

    await asyncio.gather(
        ticker_1(),
        ticker_2()
    )
    print('completed')

asyncio.run(main())


## comprehensions


async def ticker(delay, to):
    for i in range(to):
        yield i
        await asyncio.sleep(delay)

async def main():
    resutls = [
        (i, j)
        async for i in ticker(1, 5)
        async for j in ticker(1, 5)
        if not i % 2 and j % 2
    ]

    print(resutls)

asyncio.run(main())