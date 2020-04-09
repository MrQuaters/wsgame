import game.gamelogic.gameconstants as GC
from game.gamelogic.answers import Answer, FullAnswer, ErrorActAnswer
from game.gamelogic.gamecl import GameData, SingletonGame
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
    if not a.player.turn or not a.player.can_move:
        return [a.player.get_id()], Answer(a.player).get_ret_object()
    if x > 1 or x < 0 or y > 1 or y < 0:
        return [a.player.get_id()], ErrorActAnswer("Wrong Values XY").get_ret_object()
    pos = a.player.get_state()
    if pos is None:
        return IGNORE()
    pos.set_x_y(x, y)
    post = a.player.cur_position_num
    if is_in_field_num(x + 0.036, y + 0.025, post):
        a.player.can_move = False
        if post == 17:
            a.player.penalty = GC.PENALTY_LIST["win"]
        else:
            a.player.open_elevel = True
            DelayedSend.set_send(
                a.active_players_spct,
                Answer(
                    a.player, GC.ACTION_LIST["elvl"], a.player.cur_position_num
                ).get_ret_object(),
            )

        if post == 2 or post == 10 or post == 13 or post == 16 or post == 6:
            a.player.on_pen_field = True

        DelayedSend.set_send(
            [a.player.get_id()],
            Answer(a.player, GC.ACTION_LIST["can_move"], False, True).get_ret_object(),
        )

    return a.active_players_spct, Answer(a.player).get_ret_object()


@App.register(GC.USER_ACTION_LIST["cubic"])
def cubic(game_obj):
    a = GameData.get_data()
    if a.player.admin:
        return (
            [a.player.get_id()],
            ErrorActAnswer("AdminCannotThrowCubic").get_ret_object(),
        )
    t = 0
    send_to = []
    if a.player.turn:  # player can move
        if a.player.cubic_thrown or a.player.on_pen_field:
            return (
                [a.player.get_id()],
                ErrorActAnswer("CubicAlreadyThrown").get_ret_object(),
            )
        a.player.cubic_thrown = True
        t = random.randint(1, 6)
        a.player.get_state().cube_point = t
        a.player.cur_position_num += t
        if a.player.cur_position_num > GC.GAME_CONSTANTS["FIELD_LAST_NUM"]:
            a.player.cur_position_num = GC.GAME_CONSTANTS["FIELD_LAST_NUM"] + 1
        a.player.can_move = True
        DelayedSend.set_send(
            [a.player.get_id()],
            Answer(a.player, GC.ACTION_LIST["can_move"], True, True).get_ret_object(),
        )
        if a.player.points > 0:
            DelayedSend.set_send(
                [a.player.get_id()],
                Answer(
                    a.player, GC.ACTION_LIST["can_take_resource"], True, True
                ).get_ret_object(),
            )
            send_to = a.active_players_spct

    else:
        if a.player.show_turn:
            DelayedSend.set_send(
                [a.player.get_id()],
                Answer(
                    a.player, GC.ACTION_LIST["can_throw_num"], False, True
                ).get_ret_object(),
            )
            return (
                [a.player.get_id()],
                Answer(
                    a.player,
                    GC.ACTION_LIST["cubic"],
                    Cubic.gen_sequence(0, a.player.get_turn() + 1),
                ).get_ret_object(),
            )
        a.player.show_turn = True
        t = a.player.get_turn() + 1
        send_to = [a.player.get_id()]

    sec = Cubic.gen_sequence(random.randint(8, 15), t)
    DelayedSend.set_send(
        send_to, Answer(a.player, GC.ACTION_LIST["cubic"], sec).get_ret_object()
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
    if not a.player.cubic_thrown:
        return [a.player.get_id()], ErrorActAnswer("CubicNotThrown").get_ret_object()
    if a.player.points <= 0:
        DelayedSend.set_send(
            [a.player.get_id()],
            Answer(
                a.player, GC.ACTION_LIST["can_take_resource"], False, True
            ).get_ret_object(),
        )
        return [a.player.get_id()], ErrorActAnswer("YouHaveNoPoints").get_ret_object()
    a.player.points -= 1
    rs = a.player.get_resource()
    a.player.resources.append(rs)
    return (
        a.active_players_spct,
        Answer(a.player, GC.ACTION_LIST["resource"], rs).get_ret_object(),
    )


@App.register(GC.USER_ACTION_LIST["ycubic"])
def ycubic(game_obj):
    a = GameData.get_data()
    if not a.player.turn:
        return IGNORE()
    if (
        not a.player.on_pen_field
        or not a.player.can_throw_yn
        or a.player.yncubic_thrown
    ):
        return ([a.player.get_id()], ErrorActAnswer("CantThrowYCubic").get_ret_object())
    a.player.yncubic_thrown = True
    DelayedSend.set_send(
        [a.player.get_id()],
        Answer(a.player, GC.ACTION_LIST["can_throw_yn"], False, True).get_ret_object(),
    )
    t = random.randint(1, 6)
    DelayedSend.set_send(
        a.active_players_spct,
        Answer(
            a.player,
            GC.ACTION_LIST["yncubic"],
            Cubic.gen_sequence(random.randint(4, 8), t),
        ).get_ret_object(),
    )
    t = t % 2
    a.player.can_move = True

    if t == 0:
        a.player.cur_position_num = 0
        return (
            [a.player.get_id()],
            Answer(a.player, GC.ACTION_LIST["can_move"], True, True).get_ret_object(),
        )

    if a.player.yn_time is None:
        a.player.cur_position_num = -1 * a.player.cur_position_num
        a.player.yn_time = True
        return (
            [a.player.get_id()],
            Answer(a.player, GC.ACTION_LIST["can_move"], True, True).get_ret_object(),
        )

    a.player.cur_position_num = abs(a.player.cur_position_num)
    a.player.on_pen_field = False
    a.player.yn_time = None
    a.player.can_move = False
    return (
        [a.player.get_id()],
        Answer(a.player, GC.ACTION_LIST["can_throw_num"], True, True).get_ret_object(),
    )


@App.register(GC.ADMIN_ACTION_LIST["start"])
def game_start(game_obj):
    a = GameData.get_data()
    if not a.player.admin:
        return IGNORE()
    game = SingletonGame.get_game()
    if game.game_state != GC.GAME_CONSTANTS["GAME_STATE_W8_CLIENTS"]:
        return [a.player.get_id()], ErrorActAnswer("GameStarted").get_ret_object()
    game.game_state = GC.GAME_CONSTANTS["GAME_START"]
    clients = game.get_all_ids()
    for c in clients:
        game.get_player(c).show_turn = True
    game.start_game()
    ns = game.next_step()
    if not ns:
        return [a.player.get_id()], ErrorActAnswer("NoPlayers").get_ret_object()
    cli = game.stepping_cli()
    cli.cubic_thrown = False
    DelayedSend.set_send(
        [cli.get_id()],
        Answer(cli, GC.ACTION_LIST["can_throw_num"], True, True).get_ret_object(),
    )
    return a.active_players_spct, Answer(cli, GC.ACTION_LIST["step"]).get_ret_object()


@App.register(GC.ADMIN_ACTION_LIST["step"])
def next_step(game_obj):
    a = GameData.get_data()
    if not a.player.admin:
        return IGNORE()
    game = SingletonGame.get_game()
    if game.game_state == GC.GAME_CONSTANTS["GAME_STATE_W8_CLIENTS"]:
        return [a.player.get_id()], ErrorActAnswer("GameNotStarted").get_ret_object()
    ns = game.next_step()
    if not ns:
        return [a.player.get_id()], ErrorActAnswer("NoPlayers").get_ret_object()

    cli = game.stepping_cli()
    cli.resources.clear()
    cli.open_elevel = False
    cli.cubic_thrown = False
    cli.yncubic_thrown = False
    if not cli.on_pen_field:
        DelayedSend.set_send(
            [cli.get_id()],
            Answer(cli, GC.ACTION_LIST["can_throw_num"], True, True).get_ret_object(),
        )
    return a.active_players_spct, Answer(cli, GC.ACTION_LIST["step"]).get_ret_object()


@App.register(GC.ADMIN_ACTION_LIST["allow_yn"])
def allow_yn(game_obj):
    a = GameData.get_data()
    if not a.player.admin:
        return IGNORE()
    game = SingletonGame.get_game()
    cli = game.stepping_cli()
    if cli is None:
        return (
            [a.player.get_id()],
            ErrorActAnswer("NoActiveCliOrGameNotStarted").get_ret_object(),
        )
    if not cli.on_pen_field:
        return [a.player.get_id()], ErrorActAnswer("CliNotOnPenField").get_ret_object()
    cli.can_throw_yn = True
    DelayedSend.set_send([a.player.get_id()], ErrorActAnswer("Done").get_ret_object())
    return (
        [cli.get_id()],
        Answer(cli, GC.ACTION_LIST["can_throw_yn"], True, True).get_ret_object(),
    )
