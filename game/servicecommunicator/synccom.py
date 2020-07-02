from typing import Optional

import redis

from .serviceconstants import WORKERS_CHANNEL, SAFE_OFF_WORKERS, REDIS_HOST, REDIS_PORT


class BaseSyncServiceCommunicator:
    def pull_from_work_channel(self, timeout) -> Optional[tuple]:
        pass

    def push_to_client_channel(self, client, msg) -> int:
        pass

    def queue_len(self, client) -> int:
        pass


class SyncServiceCommunicator(BaseSyncServiceCommunicator):
    def __init__(self, channel=None, endchannel=None, db: int = 0):
        self._re = redis.Redis(
            host=REDIS_HOST, port=REDIS_PORT, db=db, encoding="UTF-8"
        )
        if channel is None:
            self._WORKERS_CHANNEL = WORKERS_CHANNEL
        else:
            self._WORKERS_CHANNEL = channel
        if endchannel is None:
            self._SAFE_OFF_WORKERS = SAFE_OFF_WORKERS
        else:
            self._SAFE_OFF_WORKERS = endchannel

    def pull_from_work_channel(self, timeout) -> Optional[tuple]:
        a = self._re.blpop(
            [self._WORKERS_CHANNEL, self._SAFE_OFF_WORKERS], timeout=timeout
        )
        if a is not None:
            return (a[0].decode("utf-8"), a[1].decode("utf-8"))

    def push_to_client_channel(self, client, msg) -> int:
        return self._re.rpush(client, msg)

    def set_expire_chan(self, key, time) -> None:
        return self._re.expire(key, time)

    def queue_len(self, client) -> int:
        return self._re.llen(client)

    def clear_cli_channel(self, cli):
        self._re.delete(cli)

    def clear_channel(self):
        self._re.delete(self._WORKERS_CHANNEL, self._SAFE_OFF_WORKERS)
