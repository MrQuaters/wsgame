import game.gamelogic.gameconstants as GC
from game.gamelogic.answers import Answer, FullAnswer, ErrorActAnswer, print_step_set
from game.gamelogic.gamecl import GameData, SingletonGame, PlayerState
from game.gamehandlers import DelayedSend
from game.gamelogic.positioning import is_in_field_num
from game.gamelogic.gameconstants import ACTION_LIST
from game.gamelogic.cubic import Cubic
import random
from .worker import App

IMPORTED = "IMOPRTED"


def IGNORE():
    return [], " "


@App.register_middlepoint(GC.CLIENT_CONNECTED_STR)  # conn handler
def conn(uid: int, game_obj):
    game = SingletonGame.get_game()
    role = int(game_obj[GC.PARCER_CONSTANTS["role"]])
    fnum = int(game_obj[GC.PARCER_CONSTANTS["fnum"]])
    game.add_player(uid, fnum, role)
    return (
        game.get_spectrators_and_ids(),
        Answer(game.get_player(uid), ACTION_LIST["conn"]).get_ret_object(),
    )


@App.register_middlepoint(GC.CLIENT_DISCONNECTED_STR)  # disc handler
def disc(uid: int, game_obj):
    game = SingletonGame.get_game()
    pl = game.get_player(uid)
    game.disconnect_player(uid)
    if pl is None:
        return IGNORE()
    return (
        game.get_spectrators_and_ids(),
        Answer(pl, GC.ACTION_LIST["dc"]).get_ret_object(),
    )


@App.register_middlepoint(GC.USER_ACTION_LIST["info"])  # info call msg
def info(uid, game_obj):
    game = SingletonGame.get_game()
    a = game.get_player(uid)
    if a is not None:
        return [uid], FullAnswer(uid, game).get_ret_object()
    else:
        sp = game.get_spectrator(uid)
        if sp is None:
            return IGNORE()
        return [uid], FullAnswer(None, game).get_ret_object()


@App.register_middlepoint(GC.USER_ACTION_LIST["card_data"])
def get_card_data(uid, game_obj):
    game = SingletonGame.get_game()
    pl_fnum = game_obj.get("fnm", None)
    if pl_fnum is None:
        return IGNORE()
    player = game.get_player_fnum(pl_fnum)
    if player is None:
        return IGNORE()
    if player.penalty is not None:
        return IGNORE()
    answ = {}
    if player.open_elevel:
        answ["elvl"] = abs(player.cur_position_num)
    if player.rune is not None:
        answ["rune"] = player.rune
    if player.resources is not None:
        answ["res"] = [player.resources]
    if len(answ) == 0:
        answ["err"] = "Пусто"
    return (
        [uid],
        Answer(None, GC.ACTION_LIST["card_data"], answ, lowpack=True).get_ret_object(),
    )


@App.register_middlepoint(GC.USER_ACTION_LIST["target_data"])
def target_data(uid, game_obj):
    game = SingletonGame.get_game()
    pl_fnum = game_obj.get("fnm", None)
    if pl_fnum is None:
        return IGNORE()
    player = game.get_player_fnum(pl_fnum)
    if player is None:
        return IGNORE()
    answ = {}
    if player.target is None:
        answ["err"] = "Пусто"
    else:
        answ["err"] = player.target
    return (
        [uid],
        Answer(None, GC.ACTION_LIST["card_data"], answ, lowpack=True).get_ret_object(),
    )


@App.register_middlepoint(GC.USER_ACTION_LIST["steps"])
def steps(uid, game_obj):
    game = SingletonGame.get_game()
    t = print_step_set(game)

    return (
        [uid],
        Answer(None, GC.ACTION_LIST["card_data"], t, lowpack=True).get_ret_object(),
    )


@App.register(GC.USER_ACTION_LIST["reg"])  # add name n target
def reg(game_obj):
    name = game_obj.get("name")
    target = game_obj.get("target")
    if name is None or target is None:
        return IGNORE()
    a = GameData.get_data()
    if a.player.set_reg_data:
        return (
            [a.player.get_id()],
            ErrorActAnswer("U had already set name").get_ret_object(),
        )
    a.player.target = str(target)
    a.player.name = str(name)
    a.player.set_reg_data = True
    return a.active_players_spct, Answer(a.player).get_ret_object()


@App.register(GC.USER_ACTION_LIST["move"])  # user move point
def move(game_obj):
    x = game_obj.get("x")
    y = game_obj.get("y")
    if x is None or y is None:
        return IGNORE()
    try:
        x = float(x)
        y = float(y)
    except BaseException:
        return IGNORE()

    a = GameData.get_data()
    if not a.player.turn or a.player.player_state != PlayerState.set_moving_state():
        return [a.player.get_id()], Answer(a.player).get_ret_object()
    if x > 1 or x < 0 or y > 1 or y < 0:
        return [a.player.get_id()], ErrorActAnswer("Wrong Values XY").get_ret_object()
    pos = a.player.get_state()
    if pos is None:
        return IGNORE()
    pos.set_x_y(x, y)
    post = a.player.cur_position_num
    if is_in_field_num(x + 0.036, y, post):
        a.player.player_state = PlayerState.set_thinking_state()
        if post == 17:
            a.player.penalty = GC.PENALTY_LIST["win"]
        elif post == 0:
            a.player.penalty = GC.PENALTY_LIST["stop"]
            a.player.cubic_thrown = False
            a.player.rune = None
            a.player.open_elevel = False
            a.player.resources = None
            a.player.open_resource = False

        elif post == -2 or post == -10 or post == -13 or post == -16 or post == -6:
            rn = a.player.get_rune()
            a.player.rune = rn
            DelayedSend.set_send(
                a.active_players_spct,
                Answer(a.player, GC.ACTION_LIST["elvl"], rn).get_ret_object(),
            )

        else:
            a.player.open_elevel = True
            DelayedSend.set_send(
                a.active_players_spct,
                Answer(a.player, GC.ACTION_LIST["elvl"], post).get_ret_object(),
            )

        DelayedSend.set_send(
            [a.player.get_id()],
            Answer(a.player, GC.ACTION_LIST["can_move"], False, True).get_ret_object(),
        )

    return a.active_players_spct, Answer(a.player).get_ret_object()


@App.register(GC.USER_ACTION_LIST["my_turn"])
def my_turn(game_obj):
    a = GameData.get_data()
    if a.player.admin:
        return (
            [a.player.get_id()],
            ErrorActAnswer("AdminCannotThrowCubic").get_ret_object(),
        )
    t = a.player.get_turn() + 1
    if a.player.show_turn:
        sec = Cubic.gen_sequence(0, t)
        DelayedSend.set_send(
            [a.player.get_id()],
            Answer(a.player, GC.ACTION_LIST["cubic"], sec, True).get_ret_object(),
        )
    else:
        sec = Cubic.gen_sequence(random.randint(8, 15), t)
        DelayedSend.set_send(
            [a.player.get_id()],
            Answer(a.player, GC.ACTION_LIST["cubic"], sec, True).get_ret_object(),
        )
    return (
        [a.player.get_id()],
        Answer(a.player, GC.ACTION_LIST["can_throw_num"], False, True).get_ret_object(),
    )


@App.register(GC.USER_ACTION_LIST["cubic"])
def cubic(game_obj):
    a = GameData.get_data()
    if a.player.admin:
        return (
            [a.player.get_id()],
            ErrorActAnswer("AdminCannotThrowCubic").get_ret_object(),
        )

    if not a.player.turn or a.player.player_state != PlayerState.set_numcubic_state():
        return IGNORE()
    t = 0
    a.player.cubic_thrown = True
    t = random.randint(1, 6)
    a.player.get_state().cube_point = t
    a.player.cur_position_num += t
    if a.player.cur_position_num > GC.GAME_CONSTANTS["FIELD_LAST_NUM"]:
        a.player.cur_position_num = GC.GAME_CONSTANTS["FIELD_LAST_NUM"] + 1
    a.player.player_state = PlayerState.set_moving_state()
    sec = Cubic.gen_sequence(random.randint(8, 15), t)
    DelayedSend.set_send(
        a.active_players_spct,
        Answer(a.player, GC.ACTION_LIST["cubic"], sec).get_ret_object(),
    )
    return (
        [a.player.get_id()],
        Answer(a.player, GC.ACTION_LIST["can_throw_num"], False, True).get_ret_object(),
    )


@App.register(GC.USER_ACTION_LIST["resource"])
def get_resource(game_obj):
    a = GameData.get_data()
    if not a.player.turn:
        return IGNORE()
    if (
        a.player.points <= 0
        or a.player.open_resource
        or a.player.player_state != PlayerState.set_thinking_state()
        or not a.player.can_take_resource
    ):
        return [a.player.get_id()], ErrorActAnswer("YouHaveNoPoints").get_ret_object()
    DelayedSend.set_send(
        [a.player.get_id()],
        Answer(
            a.player, GC.ACTION_LIST["can_take_resource"], False, True
        ).get_ret_object(),
    )
    a.player.points -= 1
    a.player.open_resource = True
    a.player.can_take_resource = False
    rs = a.player.get_resource()
    a.player.resources = rs
    return (
        a.active_players_spct,
        Answer(a.player, GC.ACTION_LIST["resource"], rs).get_ret_object(),
    )


@App.register(GC.USER_ACTION_LIST["ycubic"])
def ycubic(game_obj):
    a = GameData.get_data()
    if not a.player.turn:
        return IGNORE()
    if not a.player.player_state == PlayerState.set_yncubic_state():
        return ([a.player.get_id()], ErrorActAnswer("CantThrowYCubic").get_ret_object())
    a.player.yncubic_thrown = True
    DelayedSend.set_send(
        [a.player.get_id()],
        Answer(a.player, GC.ACTION_LIST["can_throw_yn"], False, True).get_ret_object(),
    )
    t = random.randint(1, 6)
    a.player.get_state().yncube_point = t
    DelayedSend.set_send(
        a.active_players_spct,
        Answer(
            a.player,
            GC.ACTION_LIST["yncubic"],
            Cubic.gen_sequence(random.randint(12, 17), t),
        ).get_ret_object(),
    )
    t = t % 2
    post = a.player.cur_position_num
    a.player.open_resource = False
    a.player.resources = None
    if t != 0:
        a.player.rune = None
        a.player.open_elevel = False

    if post == 2 or post == 10 or post == 13 or post == 16 or post == 6:
        if t == 0:
            a.player.cur_position_num = -1 * a.player.cur_position_num
            a.player.player_state = PlayerState.set_moving_state()
        else:
            a.player.player_state = PlayerState.set_numcubic_state()
    elif post == -2 or post == -10 or post == -13 or post == -16 or post == -6:
        if t == 0:
            a.player.cur_position_num = 0
            a.player.player_state = PlayerState.set_moving_state()
        else:
            a.player.open_elevel = True
            a.player.cur_position_num = -1 * a.player.cur_position_num
            a.player.player_state = PlayerState.set_numcubic_state()
    else:
        if t == 0:
            a.player.player_state = PlayerState.set_thinking_state()
        else:
            a.player.player_state = PlayerState.set_numcubic_state()

    return IGNORE()


@App.register(GC.USER_ACTION_LIST["anim_end"])
def anim_end(game_obj):
    a = GameData.get_data()
    if not a.player.turn:
        if not a.player.show_turn:
            a.player.show_turn = True
        return IGNORE()
    if a.player.player_state == PlayerState.set_moving_state():
        return (
            [a.player.get_id()],
            Answer(a.player, GC.ACTION_LIST["can_move"], True, True).get_ret_object(),
        )
    if a.player.player_state == PlayerState.set_numcubic_state():
        DelayedSend.set_send(
            a.active_players_spct,
            Answer(
                a.player, GC.ACTION_LIST["clr_trgr_res"], True, True
            ).get_ret_object(),
        )
        return (
            [a.player.get_id()],
            Answer(
                a.player, GC.ACTION_LIST["can_throw_num"], True, True
            ).get_ret_object(),
        )

    return IGNORE()
