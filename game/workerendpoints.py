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
    if player.open_elevel or player.on_pen_field:
        answ["elvl"] = abs(player.cur_position_num)
    if player.on_pen_field and player.rune is not None:
        answ["rune"] = player.rune
    if player.resources:
        answ["res"] = player.resources
    if len(answ) == 0:
        answ["err"] = "Пусто"
    return (
        [uid],
        Answer(
            player, GC.ACTION_LIST["card_data"], answ, lowpack=True
        ).get_ret_object(),
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
        Answer(
            player, GC.ACTION_LIST["card_data"], answ, lowpack=True
        ).get_ret_object(),
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
    if not a.player.turn or not a.player.can_move:
        return [a.player.get_id()], Answer(a.player).get_ret_object()
    if x > 1 or x < 0 or y > 1 or y < 0:
        return [a.player.get_id()], ErrorActAnswer("Wrong Values XY").get_ret_object()
    pos = a.player.get_state()
    if pos is None:
        return IGNORE()
    pos.set_x_y(x, y)
    post = a.player.cur_position_num
    print(post)
    if is_in_field_num(x + 0.036, y, post):
        a.player.can_move = False
        if post == 17:
            a.player.penalty = GC.PENALTY_LIST["win"]
        elif post == 0:
            a.player.penalty = GC.PENALTY_LIST["stop"]
            a.player.on_pen_field = False
            a.player.back_flag = False
            a.player.cubic_thrown = False
            a.player.rune = None

        elif post == 2 or post == 10 or post == 13 or post == 16 or post == 6:
            if a.player.back_flag:
                a.player.on_pen_field = False
                a.player.back_flag = False
                a.player.cubic_thrown = False
                a.player.rune = None
                DelayedSend.set_send(
                    [a.player.get_id()],
                    Answer(
                        a.player, GC.ACTION_LIST["can_throw_num"], True, True
                    ).get_ret_object(),
                )

            else:
                a.player.on_pen_field = True
                a.player.open_elevel = True
                DelayedSend.set_send(
                    a.active_players_spct,
                    Answer(a.player, GC.ACTION_LIST["elvl"], post).get_ret_object(),
                )

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
        or a.player.can_move
    ):
        return ([a.player.get_id()], ErrorActAnswer("CantThrowYCubic").get_ret_object())
    a.player.yncubic_thrown = True
    a.player.can_throw_yn = False
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
    a.player.can_move = True
    if t == 0:
        a.player.cur_position_num = 0
        a.player.yn_time = None
        a.player.back_flag = False
    else:
        if a.player.yn_time is None:
            a.player.cur_position_num = -1 * a.player.cur_position_num
            a.player.yn_time = True
        else:
            a.player.cur_position_num = abs(a.player.cur_position_num)
            a.player.yn_time = None
            a.player.back_flag = True
    return (
        [a.player.get_id()],
        Answer(a.player, GC.ACTION_LIST["can_move"], True, True).get_ret_object(),
    )


@App.register(GC.ADMIN_ACTION_LIST["start"])
def game_start(game_obj):
    a = GameData.get_data()
    if not a.player.admin:
        return IGNORE()
    game = SingletonGame.get_game()
    if game.game_state != GC.GAME_CONSTANTS["GAME_STATE_W8_CLIENTS"]:
        return [a.player.get_id()], ErrorActAnswer("GameStarted").get_ret_object()
    clients = game.get_all_ids()
    game.game_state = GC.GAME_CONSTANTS["GAME_START"]
    for c in clients:
        game.get_player(c).show_turn = True
    game.start_game()
    ns = game.next_step()
    if not ns:
        game.game_state = GC.GAME_CONSTANTS["GAME_STATE_W8_CLIENTS"]
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
    if cli.penalty is not None:
        return [a.player.get_id()], ErrorActAnswer("CliHavePenalty").get_ret_object()
    if cli.can_move:
        return [a.player.get_id()], ErrorActAnswer("PlayerStillMoving").get_ret_object()
    cli.can_throw_yn = True
    DelayedSend.set_send([a.player.get_id()], ErrorActAnswer("Done").get_ret_object())
    return (
        [cli.get_id()],
        Answer(cli, GC.ACTION_LIST["can_throw_yn"], True, True).get_ret_object(),
    )


@App.register(GC.ADMIN_ACTION_LIST["ban_unban"])
def bun_unban(game_obj):
    a = GameData.get_data()
    if not a.player.admin:
        return IGNORE()
    fnm = game_obj.get("fnm", None)
    if fnm is None:
        return IGNORE()
    game = SingletonGame.get_game()
    cli = game.get_player_fnum(fnm)
    if cli is None:
        return IGNORE()
    if cli.penalty is None:
        cli.penalty = GC.PENALTY_LIST["stop"]
    elif cli.penalty == GC.PENALTY_LIST["win"]:
        return IGNORE()
    else:
        cli.penalty = None
    if cli.penalty is None:
        return (
            game.get_spectrators_and_ids(),
            Answer(cli, GC.ACTION_LIST["rem_pen"]).get_ret_object(),
        )
    else:
        return (game.get_spectrators_and_ids(), Answer(cli).get_ret_object())
