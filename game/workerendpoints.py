from .worker import App
import game.gamelogic.gameconstants as GC
from game.gamelogic.gamecl import GameData, SingletonGame
from .gamelogic.parcer import WorkerParser

ACTION_LIST = {
    'conn': 'connected',
    'dc': 'disconnected',
    'move': 'new_position'
}


class Answer:
    def __init__(self,fnum: int, action: str):
        self.fnum = fnum
        self.action = action
        self.w_value = None
        self.x = None
        self.y = None

    def get_ret_object(self):
        t = {
            "fnum": self.fnum,
            "action": self.action,
        }
        if self.w_value:
            t["w_value"] = self.w_value
        if self.x:
            t["x"] = self.x
            t["y"] = self.y

        return WorkerParser.parse_out(t)


@App.register_middlepoint(GC.CLIENT_CONNECTED_STR)  # conn handler
def conn(uid: int, game_obj):
    game = SingletonGame.get_game()
    role = int(game_obj[GC.PARCER_CONSTANTS["role"]])
    fnum = int(game_obj[GC.PARCER_CONSTANTS["fnum"]])
    if role == GC.USER_ROLES["admin"]:
        game.add_admin(uid)
    else:
        game.add_player(uid, fnum)

    a = Answer(fnum, ACTION_LIST['conn'])
    if role != GC.USER_ROLES["admin"]:
        pl = game.get_player(uid)
        st = pl.get_state()
        a.x = st.x
        a.y = st.y

    return game.get_active_ids(), a.get_ret_object()


@App.register_middlepoint(GC.CLIENT_DISCONNECTED_STR)  # disc handler
def disc(uid: int, game_obj):
    game = SingletonGame.get_game()
    pl = game.get_player(uid)
    game.disconnect_player(uid)
    a = Answer(pl.get_fnum(), ACTION_LIST["dc"])
    return game.get_active_ids(), a.get_ret_object()
