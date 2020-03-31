from __future__ import annotations
from typing import NamedTuple, Optional
import random
from game.gamelogic.gameconstants import CLIENT_POSITIONING, GAME_CONSTANTS, USER_ROLES


class State(NamedTuple):
    x: int
    y: int
    cube_point: int


class GameClient:
    _uid: int
    _state: State

    def __init__(self, uid: int, turn, fnum):
        self._uid = uid
        self._turn = turn
        self._fnum = fnum
        self._state = State(
            CLIENT_POSITIONING["CLIENT_DEFAULT_X"]
            + 0.01 * (uid % GAME_CONSTANTS["MAX_PLAYERS_IN_ROOM"]),
            CLIENT_POSITIONING["CLIENT_DEFAULT_Y"],
            -1,
        )
        self.status = GAME_CONSTANTS["PLAYER_CONNECTED"]
        self.exp = None
        self.admin = False

    def get_fnum(self):
        return self._fnum

    def get_state(self):
        return self._state

    def get_turn(self):
        return self._turn


class Admin(GameClient):
    def __init__(self, uid: int, fnum):
        GameClient.__init__(self, uid, -1, fnum)
        self._state = None
        self.admin = True


class Game:
    room: int
    _game_state: int

    def __init__(self, room: int, resources_num: int, target_num: int):
        self._clients = {}
        self._turns = [x for x in range(GAME_CONSTANTS["MAX_PLAYERS_IN_ROOM"])]
        self._resources = [x for x in range(resources_num)]
        self._targets = [x for x in range(target_num)]
        self._room = room
        self.game_state = GAME_CONSTANTS["GAME_STATE_W8_CLIENTS"]
        self._curr_step = -1
        self._r_step = -1

    def add_player(self, uid: int, fnum: int, role: int):
        if self._clients.get(uid) is None:
            if role == USER_ROLES["user"]:
                a = self._turns.pop(random.randint(0, len(self._turns) - 1))
                self._clients[uid] = GameClient(uid, a, fnum)
            else:
                self._clients[uid] = Admin(uid, fnum)
        else:
            self._clients[uid].status = GAME_CONSTANTS["PLAYER_CONNECTED"]

    def get_player(self, uid: int) -> Optional[GameClient]:
        a = self._clients.get(uid)
        if a is not None:
            a.turn = False
            if (
                a.status != GAME_CONSTANTS["PLAYER_DISCONNECTED"]
                and a.exp != GAME_CONSTANTS["PLAYER_BANNED"]
                and a.exp != GAME_CONSTANTS["PLAYER_STOP"]
            ):

                if a.get_turn() == self._curr_step:
                    a.turn = True
        return a

    def disconnect_player(self, uid: int):
        if self._clients.get(uid) is not None:
            self._clients[uid].status = GAME_CONSTANTS["PLAYER_DISCONNECTED"]

    def get_active_ids(self):
        rm = []
        for a in self._clients:
            if self._clients[a].status == GAME_CONSTANTS["PLAYER_CONNECTED"]:
                rm.append(a)
        return rm


class SingletonGame:
    _game = None

    @classmethod
    def create_game(cls, *args, **kwargs) -> Game:
        SingletonGame._game = Game(*args, **kwargs)
        return SingletonGame.get_game()

    @classmethod
    def get_game(cls) -> Game:
        if SingletonGame._game is None:
            raise Exception("GAME NOT CREATED")
        return SingletonGame._game


class GameData:
    _data = None

    @classmethod
    def set_new_data(cls, uid: int):
        a = SingletonGame.get_game()
        if a is not None:
            t = GameData()
            t.player = a.get_player(uid)
            t.active_players = a.get_active_ids()
            GameData._data = t
        else:
            GameData._data = None

    @classmethod
    def get_data(cls) -> Optional[GameData]:
        return GameData._data
