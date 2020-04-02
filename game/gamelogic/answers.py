from .gamecl import Game, GameClient
from .gameconstants import ANSWER_PACKAGE_NAMES, ACTION_LIST
from .parcer import WorkerParser


class Answer:
    def __init__(self, gc: GameClient, action: str = None, wst: str = None):
        self._gdata = {"type": ANSWER_PACKAGE_NAMES["def"]}
        if action is None:
            action = ACTION_LIST["default"]
        self._gdata["action"] = action
        if wst is not None:
            self._gdata["act_val"] = wst
        if gc is None:
            return
        self._gdata["fnum"] = gc.get_fnum()
        t = gc.get_state()
        if t is not None:
            self._gdata["x"] = t.x
            self._gdata["y"] = t.y
            self._gdata["pts"] = gc.points
        self._gdata["name"] = gc.name

    def get_ret_object(self):
        return WorkerParser.parse_out(self._gdata)

    def get_object(self):
        return self._gdata


class FullAnswer:
    def __init__(self, myid: int, game: Game):
        self._gdata = {"users": [], "type": ANSWER_PACKAGE_NAMES["big"]}
        t = game.get_active_ids()
        for a in t:
            cli = game.get_player(a)
            if a == myid:
                self._gdata["myf"] = cli.get_fnum()
                self._gdata["reg"] = cli.set_reg_data
            ans = Answer(cli)
            self._gdata["users"].append(ans.get_object())

        self._gdata["cur_step"] = game.get_step()
        self._gdata["game_state"] = game.game_state

    def get_ret_object(self):
        return WorkerParser.parse_out(self._gdata)


class ErrorActAnswer:
    def __init__(self, error, act_after=None):
        self._gdata = {"error": error, "type": ANSWER_PACKAGE_NAMES["err"]}
        if act_after is not None:
            self._gdata["do_after"] = act_after

    def get_ret_object(self):
        return WorkerParser.parse_out(self._gdata)
