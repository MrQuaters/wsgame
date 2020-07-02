from .gamecl import Game, GameClient, PlayerState
from .cubic import Cubic
from .gameconstants import ANSWER_PACKAGE_NAMES, ACTION_LIST, GAME_CONSTANTS
from .parcer import WorkerParser


class Answer:
    def __init__(self, gc: GameClient, action: str = None, wst=None, lowpack=False):
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
        if t is not None and lowpack == False:
            self._gdata["x"] = t.x
            self._gdata["y"] = t.y
            self._gdata["pts"] = gc.points
            self._gdata["pen"] = gc.penalty
            self._gdata["name"] = gc.name

    def get_ret_object(self):
        return WorkerParser.parse_out(self._gdata)

    def get_object(self):
        return self._gdata


class CliRetPosAnswer:
    def __init__(self, cli: GameClient):
        self._vals = []
        self._pub_vals = []
        self._cli = cli
        if cli.open_elevel:
            self._pub_vals.append(("elvl", abs(cli.cur_position_num), True))
        if cli.rune is not None:
            self._pub_vals.append(("elvl", abs(cli.rune), True))
        if cli.open_resource:
            self._pub_vals.append(("resource", cli.resources, True))
        if cli.cubic_thrown:
            rp = Cubic.gen_sequence(0, cli.get_state().cube_point)
            self._pub_vals.append(("cubic", rp, True))
        if cli.yncubic_thrown:
            rp = Cubic.gen_sequence(0, cli.get_state().yncube_point)
            self._pub_vals.append(("yncubic", rp, True))
        if cli.player_state == PlayerState.set_yncubic_state():
            self._vals.append(("can_throw_yn", True, True))
        elif cli.player_state == PlayerState.set_moving_state():
            self._vals.append(("can_move", True, True))
        elif cli.player_state == PlayerState.set_numcubic_state():
            self._vals.append(("can_throw_num", True, True))
        if (
            cli.player_state == PlayerState.set_thinking_state()
            and cli.can_take_resource
        ):
            self._vals.append(("can_take_resource", True, True))

    def get_my_ret_obj(self):
        ro = []
        for a in self._vals:
            ro.append(Answer(self._cli, ACTION_LIST[a[0]], a[1], a[2]).get_ret_object())
        return ro

    def get_my_obj(self):
        ro = []
        for a in self._vals:
            ro.append(Answer(self._cli, ACTION_LIST[a[0]], a[1], a[2]).get_object())
        return ro

    def get_pub_ret_obj(self):
        ro = []
        for a in self._pub_vals:
            ro.append(Answer(self._cli, ACTION_LIST[a[0]], a[1], a[2]).get_ret_object())
        return ro

    def get_pub_obj(self):
        ro = []
        for a in self._pub_vals:
            ro.append(Answer(self._cli, ACTION_LIST[a[0]], a[1], a[2]).get_object())
        return ro


class FullAnswer:  # contains all info about game, described by lot of small_packs
    def __init__(self, myid: int, game: Game):
        self._gdata = {"users": [], "type": ANSWER_PACKAGE_NAMES["big"]}
        t = game.get_active_ids()
        for a in t:
            cli = game.get_player(a)
            if a == myid:
                self._gdata["myf"] = cli.get_fnum()
                self._gdata["reg"] = cli.set_reg_data
                if (
                    game.game_state == GAME_CONSTANTS["GAME_STATE_W8_CLIENTS"]
                    and not cli.admin
                ):
                    self._gdata["users"].append(
                        Answer(
                            cli, ACTION_LIST["can_throw_num"], True, lowpack=True
                        ).get_object()
                    )

            self._gdata["users"].append(Answer(cli, ACTION_LIST["conn"]).get_object())

        elevel = None
        resource = None

        cli = game.stepping_cli()
        if cli is not None:
            self._gdata["users"].append(Answer(cli, ACTION_LIST["step"]).get_object())
            self._gdata["users"] += CliRetPosAnswer(cli).get_pub_obj()
            if cli.get_id() == myid:
                self._gdata["users"] += CliRetPosAnswer(cli).get_my_obj()
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


def print_step_set(gm: Game, prefix: str = None, postfix: str = None):
    tr = {}
    rt_string = ""
    if prefix is not None:
        rt_string += prefix
    rt_string += "Ходит(число на кубике): Имя" + "\n"
    cli_pull = []
    clients = gm.get_active_ids()
    for a in clients:
        cli = gm.get_player(a)
        if cli.admin:
            continue
        cli_pull.append([cli.get_turn(), cli.show_turn, cli.name])
    if len(cli_pull) != 0:
        cli_pull.sort(key=lambda pl: pl[0])
    i = 1
    for a in cli_pull:
        if not a[1]:
            ct = "-"
            if gm.game_state == GAME_CONSTANTS["GAME_STATE_W8_CLIENTS"]:
                continue
        else:
            ct = a[0] + 1
        rt_string += str(i) + "(" + str(ct) + "): "
        if a[2] is not None:
            rt_string += a[2]
        rt_string += "\n"
        i += 1

    if postfix is not None:
        rt_string += postfix

    tr["err"] = rt_string
    return tr
