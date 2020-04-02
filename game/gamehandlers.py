from game.gamelogic.gamecl import GameData
from game.gamelogic.gameconstants import GET_FULL_GAME_STATE
from game.gamelogic.parcer import WorkerParser
from game.servicecommunicator.synccom import SyncServiceCommunicator


class ActionHandler:  # main class for worker, using routes to handle actions
    def __init__(self, queue_len: int):
        self._queue_len = queue_len
        self._functions_to_handle = {}  # function dict action : handler_function

    def register_middlepoint(
        self, end_point
    ):  # decorator that used to register conn and disc handlers so
        # u can not use GameData.get_data() in it, bsc game cli is not exist still
        def decorator(f):
            a = self._functions_to_handle.get(end_point)
            if a is not None:
                raise Exception("endpoint has been defined")
            self._functions_to_handle[end_point] = f
            return f

        return decorator

    def register(
        self, end_point
    ):  # normal decorator. cli exist can use GameData.get_data() that returns all about cli
        # that u handle in fucntion
        def decorator(f):
            a = self._functions_to_handle.get(end_point)
            if a is not None:
                raise Exception("endpoint has been defined")
            self._functions_to_handle[end_point] = self._decorate_with_self_data(f)
            return f

        return decorator

    def _decorate_with_self_data(
        self, f
    ):  # decorating func by call set_new_data, puts data about cli in GameData
        def n_func(uid, game_obj):
            GameData.set_new_data(uid)
            if not GameData.exist():
                return WorkerParser.KICK_PLAYER(uid)
            return f(game_obj)

        return n_func

    def run(self, channel, end_loop_channel):  # start handler
        data = SyncServiceCommunicator(
            channel, end_loop_channel
        )  # listening room channel
        data.clear_channel()
        parser = WorkerParser()
        while True:
            channel, msg = data.pull_from_work_channel(0)

            if channel == end_loop_channel:
                return
            try:
                act, uid, obj = parser.parse_in(msg)
            except BaseException:
                continue

            if act is None or uid is None:
                continue

            fun = self._functions_to_handle.get(act, None)
            if fun is None:
                continue

            send_to, msg = fun(int(uid), obj)
            print(send_to, msg)

            for cli in send_to:
                cli = str(cli)
                q_len = data.queue_len(cli)
                if q_len >= self._queue_len:
                    continue
                r = data.push_to_client_channel(cli, msg)
                if r == self._queue_len:
                    data.push_to_client_channel(cli, GET_FULL_GAME_STATE)
