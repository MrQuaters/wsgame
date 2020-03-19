from game.servicecommunicator.synccom import SyncServiceCommunicator
from game.servicecommunicator.serviceconstants import SAFE_OFF_WORKERS
from game.gamelogic.gameconstants import GET_FULL_GAME_STATE
from game.gamelogic.parcer import WorkerParser


class ActionHandler:
    def __init__(self, queue_len: int):
        self._queue_len = queue_len
        self._functions_to_handle = {}

    def register(self, end_point):
        def decorator(f):
            a = self._functions_to_handle.get(end_point)
            if a is not None:
                raise Exception('endpoint has been defined')
            self._functions_to_handle[end_point] = self._decorate_with_self_data(f)
            return f
        return decorator

    def _decorate_with_self_data(self, f):
        def n_func(uid, room, game_obj):
            GameData.set_new_data(uid, room)
            return f(game_obj)
        return n_func

    def run(self, channel):
        data = SyncServiceCommunicator(channel)
        parser = WorkerParser()
        while True:
            channel, msg = data.pull_from_work_channel(0)

            if channel == SAFE_OFF_WORKERS:
                return
            try:
                act, uid, room, obj = parser.parse_in(msg)
            except BaseException:
                continue

            if act is None or uid is None or room in None:
                continue

            fun = self._functions_to_handle.get(act, None)
            if fun is None:
                continue

            send_to, msg = fun(uid, room, obj)

            for cli in send_to:
                q_len = data.queue_len(cli)
                if q_len >= self._queue_len:
                    continue
                r = data.push_to_client_channel(cli, msg)
                if r == self._queue_len:
                    data.push_to_client_channel(cli, GET_FULL_GAME_STATE)
