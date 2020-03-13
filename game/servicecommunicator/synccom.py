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
    def __init__(self, db: int = 0):
        self._re = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=db,encoding='UTF-8')

    def pull_from_work_channel(self, timeout) -> Optional[tuple]:
        a =  self._re.blpop([WORKERS_CHANNEL, SAFE_OFF_WORKERS], timeout= timeout)
        if a is not None:
            return (a[0].decode('utf-8'), a[1].decode('utf-8'))

    def push_to_client_channel(self, client, msg) -> int:
        return self._re.rpush(client, msg)

    def queue_len(self, client) -> int:
        return self._re.llen(client)


class SingletonServiceCommunicator:
    __instanced = None
    __db = None

    @classmethod
    def get_communicator(cls, db: int = 0) -> SyncServiceCommunicator:
        if SingletonServiceCommunicator.__instanced is None or db != SingletonServiceCommunicator.__db:
            SingletonServiceCommunicator.__instanced = SyncServiceCommunicator(db)
        return SingletonServiceCommunicator.__instanced
