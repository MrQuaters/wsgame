from .gamecl import Game
from .parcer import WorkerParser


class Answer:
    def __init__(self, fnum: int, action: str):
        self.fnum = fnum
        self.action = action
        self.w_value = None
        self.x = None
        self.y = None

    def set_x_y(self, st):
        if st is not None:
            self.x = st.x
            self.y = st.y

    def get_ret_object(self):
        t = {"fnum": self.fnum, "action": self.action}
        if self.w_value:
            t["w_value"] = self.w_value
        if self.x:
            t["x"] = self.x
            t["y"] = self.y

        return WorkerParser.parse_out(t)


class FullAnswer:
    def __init__(self, myid: int, game: Game):
        self._gdata = {"users": []}
        t = game.get_active_ids()
        for a in t:
            k = {}
            cli = game.get_player(a)
            st = cli.get_state()
            if a == myid:
                self._gdata["myf"] = cli.get_fnum()
                self._gdata["reg"] = cli.set_reg_data
            k["name"] = cli.name
            k["fnum"] = cli.get_fnum()
            if st is not None:
                k["x"] = st.x
                k["y"] = st.y
                k["bl"] = cli.points

            self._gdata["users"].append(k)

        self._gdata["cur_step"] = game.get_step()
        self._gdata["game_state"] = game.game_state

    def get_ret_object(self):
        return WorkerParser.parse_out(self._gdata)


class ErrorActAnswer:
    def __init__(self, error, act_after=None):
        self._gdata = {"error": error, "action": "error"}
        if act_after is not None:
            self._gdata["do_after"] = act_after

    def get_ret_object(self):
        return WorkerParser.parse_out(self._gdata)
