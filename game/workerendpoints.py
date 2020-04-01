import game.gamelogic.gameconstants as GC
from game.gamelogic.answers import Answer, FullAnswer, ErrorActAnswer
from game.gamelogic.gamecl import GameData, SingletonGame
from game.gamelogic.gameconstants import ACTION_LIST
from .worker import App

IGNORE = ([], " ")


@App.register_middlepoint(GC.CLIENT_CONNECTED_STR)  # conn handler
def conn(uid: int, game_obj):
    game = SingletonGame.get_game()
    role = int(game_obj[GC.PARCER_CONSTANTS["role"]])
    fnum = int(game_obj[GC.PARCER_CONSTANTS["fnum"]])
    game.add_player(uid, fnum, role)
    a = Answer(fnum, ACTION_LIST["conn"])
    a.set_x_y(game.get_player(uid).get_state())
    return game.get_active_ids(), a.get_ret_object()


@App.register_middlepoint(GC.CLIENT_DISCONNECTED_STR)  # disc handler
def disc(uid: int, game_obj):
    game = SingletonGame.get_game()
    pl = game.get_player(uid)
    if pl is None:
        conn(uid, game_obj)
        pl = game.get_player(uid)

    game.disconnect_player(uid)
    a = Answer(pl.get_fnum(), ACTION_LIST["dc"])
    return game.get_active_ids(), a.get_ret_object()


@App.register(GC.USER_ACTION_LIST["info"])  # info call msg
def info(game_obj):
    a = GameData.get_data()
    e = a.player.get_id()
    return [e], FullAnswer(e, SingletonGame.get_game()).get_ret_object()


@App.register(GC.USER_ACTION_LIST["reg"])
def reg(game_obj):
    name = game_obj.get("name")
    target = game_obj.get("target")
    if name is None or target is None:
        return IGNORE
    a = GameData.get_data()
    if a.player.set_reg_data:
        return (
            [a.player.get_id()],
            ErrorActAnswer("U had already set name").get_ret_object(),
        )
    a.player.target = str(target)
    a.player.name = str(name)
    a.player.set_reg_data = True
    answ = Answer(a.player.get_fnum(), ACTION_LIST["reg"])
    answ.w_value = name
    return a.active_players, answ.get_ret_object()


@App.register(GC.USER_ACTION_LIST["move"])
def move(game_obj):
    x = game_obj.get("x")
    y = game_obj.get("y")
    if x is None or y is None:
        return IGNORE
    try:
        x = round(float(x), 2)
        y = float(float(y), 2)
    except BaseException:
        return IGNORE

    a = GameData.get_data()
    if not a.player.turn:
        return (
            [a.player.get_id()],
            ErrorActAnswer("Not your turn to move").get_ret_object(),
        )
    pos = a.player.get_state()
    if pos is None:
        return IGNORE

    pos.x = x
    pos.y = y
    answ = Answer(a.player.get_fnum(), ACTION_LIST["move"])
    answ.set_x_y(pos)
    return a.active_players, answ.get_ret_object()
