from __future__ import annotations
import aioredis
from game import servicecommunicator
from typing import Optional


class BaseAsyncServiceCommunicator:
    async def listen_for_clients(self, cli, timeout) -> Optional[tuple]:
        pass

    async def push_in_work_channel(self, msg) -> None:
        pass

    async def pull_from_work_channel(self, timeout) -> Optional[tuple]:
        pass


class AsyncServiceCommunicator(BaseAsyncServiceCommunicator):
    async def start(self):
        self.re = await aioredis.create_redis(servicecommunicator.REDIS_ADDRESS, encoding='UTF-8', db=0)
        self.iscon = True

    async def listen_for_clients(self, cli, timeout) -> Optional[tuple]:
        return await self.re.blpop(*cli, timeout=timeout)

    async def push_in_work_channel(self, msg) -> None:
        await self.re.rpush(servicecommunicator.WORKERS_CHANNEL, msg)

    async def pull_from_work_channel(self, timeout) -> Optional[tuple]:
        t = await self.re.blpop(servicecommunicator.WORKERS_CHANNEL, timeout=timeout)
        if t is not None:
            t[0] = t[0].decode('UTF-8')
            t[1] = t[1].decode('UTF-8')
        return t


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
