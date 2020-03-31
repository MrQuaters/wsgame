from .worker import App
import game.gamelogic.gameconstants as GC
from game.gamelogic.gameconstants import ACTION_LIST
from game.gamelogic.answers import Answer
from game.gamelogic.gamecl import GameData, SingletonGame


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


@App.register(GC.USER_ACTION_LIST["info"])
def info(game_obj):
    pass
