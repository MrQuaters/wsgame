import redis
from typing import Optional
from .serviceconstants import WORKERS_CHANNEL, SAFE_OFF_WORKERS, REDIS_HOST, REDIS_PORT


class BaseSyncServiceCommunicator:
    def pull_from_work_channel(self, timeout) -> Optional[tuple]:
        pass

    def push_to_client_channel(self, client, msg) -> int:
        pass

    def queue_len(self, client) -> int:
        pass


class SyncServiceCommunicator(BaseSyncServiceCommunicator):
    def __init__(self, channel=None, db: int = 0):
        self._re = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=db,encoding='UTF-8')
        if channel is None:
            self._WORKERS_CHANNEL = WORKERS_CHANNEL
        else:
            self._WORKERS_CHANNEL = channel

    def pull_from_work_channel(self, timeout) -> Optional[tuple]:
        a = self._re.blpop([self._WORKERS_CHANNEL, SAFE_OFF_WORKERS], timeout= timeout)
        if a is not None:
            return (a[0].decode('utf-8'), a[1].decode('utf-8'))

    def push_to_client_channel(self, client, msg) -> int:
        return self._re.rpush(client, msg)

    def queue_len(self, client) -> int:
        return self._re.llen(client)

