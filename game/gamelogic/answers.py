from .gamecl import Game, GameClient
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
            if cli.open_elevel and cli.cur_position_num > 0:
                elevel = cli.cur_position_num

            if len(cli.resources) > 0:
                resource = cli.resources[len(cli.resources) - 1]
            if cli.cubic_thrown:
                self._gdata["users"].append(
                    Answer(
                        cli,
                        ACTION_LIST["cubic"],
                        Cubic.gen_sequence(0, cli.get_state().cube_point),
                        lowpack=True,
                    ).get_object()
                )

            if cli.yncubic_thrown:
                self._gdata["users"].append(
                    Answer(
                        cli,
                        ACTION_LIST["yncubic"],
                        Cubic.gen_sequence(0, cli.get_state().yncube_point),
                        lowpack=True,
                    ).get_object()
                )

            if cli.rune is not None:
                self._gdata["users"].append(
                    Answer(
                        cli, ACTION_LIST["elvl"], cli.rune, lowpack=True
                    ).get_object()
                )

            if cli.on_pen_field and cli.can_throw_yn and cli.get_id() == myid:
                self._gdata["users"].append(
                    Answer(
                        cli, ACTION_LIST["can_throw_yn"], True, lowpack=True
                    ).get_object()
                )

            if not cli.on_pen_field and not cli.cubic_thrown and cli.get_id() == myid:
                self._gdata["users"].append(
                    Answer(
                        cli, ACTION_LIST["can_throw_num"], True, lowpack=True
                    ).get_object()
                )

            if cli.can_move and cli.get_id() == myid:
                self._gdata["users"].append(
                    Answer(
                        cli, ACTION_LIST["can_move"], True, lowpack=True
                    ).get_object()
                )

            if cli.get_id() == myid:
                self._gdata["users"].append(
                    Answer(
                        cli, ACTION_LIST["can_take_resource"], True, lowpack=True
                    ).get_ret_object()
                )

        if elevel is not None and cli.rune is None:
            self._gdata["users"].append(
                Answer(cli, ACTION_LIST["elvl"], elevel, lowpack=True).get_object()
            )
        if resource is not None:
            self._gdata["users"].append(
                Answer(
                    cli, ACTION_LIST["resource"], resource, lowpack=True
                ).get_object()
            )
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


def print_step_set(gm: Game):
    tr = {}
    rt_string = "Ходит(число на кубике): Имя" + "\n"
    cli_pull = []
    clients = gm.get_active_ids()
    for a in clients:
        cli = gm.get_player(a)
        if cli.admin:
            continue
        cli_pull.append([cli.get_turn(), cli.show_turn, cli.name])
    if len(cli_pull) == 0:
        return None
    cli_pull.sort(key=lambda pl: pl[0])
    i = 1
    for a in cli_pull:
        rt_string += str(i)
        ct = a[0] + 1
        if not a[1]:
            ct = "-"
        rt_string += "(" + str(ct) + "): "
        if a[2] is not None:
            rt_string += a[2]
        rt_string += "\n"
        i += 1
    tr["err"] = rt_string
    return tr
