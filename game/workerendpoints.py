import game.gamelogic.gameconstants as GC
from game.gamelogic.answers import Answer, FullAnswer, ErrorActAnswer
from game.gamelogic.gamecl import GameData, SingletonGame
from game.gamelogic.gameconstants import ACTION_LIST
from .worker import App


def IGNORE():
    return [], " "


@App.register_middlepoint(GC.CLIENT_CONNECTED_STR)  # conn handler
def conn(uid: int, game_obj):
    game = SingletonGame.get_game()
    role = int(game_obj[GC.PARCER_CONSTANTS["role"]])
    fnum = int(game_obj[GC.PARCER_CONSTANTS["fnum"]])
    game.add_player(uid, fnum, role)
    return (
        game.get_active_ids(),
        Answer(game.get_player(uid), ACTION_LIST["conn"]).get_ret_object(),
    )


@App.register_middlepoint(GC.CLIENT_DISCONNECTED_STR)  # disc handler
def disc(uid: int, game_obj):
    game = SingletonGame.get_game()
    pl = game.get_player(uid)
    if pl is None:
        return IGNORE()
    game.disconnect_player(uid)
    return game.get_active_ids(), Answer(pl, ACTION_LIST["dc"]).get_ret_object()


@App.register(GC.USER_ACTION_LIST["info"])  # info call msg
def info(game_obj):
    a = GameData.get_data()
    e = a.player.get_id()
    return [e], FullAnswer(e, SingletonGame.get_game()).get_ret_object()


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
    return a.active_players, Answer(a.player).get_ret_object()


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
    if not a.player.turn:
        return (
            [a.player.get_id()],
            ErrorActAnswer("Not your turn to move").get_ret_object(),
        )
    if x > 1 or x < 0 or y > 1 or y < 0:
        return ([a.player.get_id()], ErrorActAnswer("Wrong Values XY").get_ret_object())
    pos = a.player.get_state()
    if pos is None:
        return IGNORE()

    pos.set_x_y(x, y)
    return a.active_players, Answer(a.player).get_ret_object()


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
    return a.active_players, Answer(cli, GC.ACTION_LIST["step"]).get_ret_object()


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
    return a.active_players, Answer(cli, GC.ACTION_LIST["step"]).get_ret_object()
