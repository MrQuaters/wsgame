from __future__ import annotations
import aioredis
import asyncio
from .serviceconstants import WORKERS_CHANNEL, SAFE_OFF_WORKERS, REDIS_ADDRESS

from typing import Optional


class BaseAsyncServiceCommunicator:
    async def listen_for_clients(self, cli, timeout) -> Optional[tuple]:
        pass

    async def push_in_work_channel(self, msg) -> None:
        pass

    async def pull_from_work_channel(self, timeout) -> Optional[tuple]:
        pass


class AsyncServiceCommunicator(BaseAsyncServiceCommunicator):
    def __init__(self):
        self.iscon = False

    async def start(self):
        if not self.iscon:
            self.re = await aioredis.create_redis(REDIS_ADDRESS, encoding="UTF-8", db=0)
            self.iscon = True

    async def listen_for_clients(self, cli, timeout) -> Optional[tuple]:
        return await self.re.blpop(*cli, timeout=timeout)

    async def push_in_work_channel(self, msg) -> None:
        await self.re.rpush(WORKERS_CHANNEL, msg)

    async def pull_from_work_channel(self, timeout) -> Optional[tuple]:
        return await self.re.blpop([WORKERS_CHANNEL, SAFE_OFF_WORKERS], timeout=timeout)

    async def push_in_channel(self, ch, msg) -> None:
        await self.re.rpush(ch, msg)


class SingletonAsyncServerCommunicator:
    __instanced = None

    @classmethod
    async def get_communicator(cls) -> AsyncServiceCommunicator:
        if SingletonAsyncServerCommunicator.__instanced is None:
            SingletonAsyncServerCommunicator.__instanced = AsyncServiceCommunicator()
            await SingletonAsyncServerCommunicator.__instanced.start()
        else:
            while not SingletonAsyncServerCommunicator.__instanced.iscon:
                await asyncio.sleep(0.1)

        return SingletonAsyncServerCommunicator.__instanced


class CallFunc:
    def __init__(self, fun, *args, **kwargs):
        self.fun = fun
        self.args = args
        self.kwargs = kwargs


class SafeInit:
    def __init__(self):
        self._bmas = []
        self._task = []
        self._ruc = None

    def make_blocking(self, func, *args, **kwargs):
        self._bmas.append(CallFunc(func, *args, **kwargs))

    def add_tasks(self, func, *args, **kwargs):
        self._task.append(CallFunc(func, *args, **kwargs))

    async def _runblock(self, loop):
        for fun in self._bmas:
            await fun.fun(*(fun.args), **(fun.kwargs))
        for fun in self._task:
            loop.create_task(fun.fun(*(fun.args), **(fun.kwargs)))

        self._bmas.clear()
        self._task.clear()

        if self._ruc is not None:
            return await self._ruc.fun(*(self._ruc.args), **(self._ruc.kwargs))

    def loop_run_until_complete(self, loop, func, *args, **kwargs):
        self._ruc = CallFunc(func, *args, *kwargs)
        loop.run_until_complete(self._runblock(loop))

    def loop_run_forever(self, loop):
        loop.create_task(self._runblock(loop))
        loop.run_forever()
