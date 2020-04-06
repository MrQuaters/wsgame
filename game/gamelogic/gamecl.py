from __future__ import annotations

import random
from typing import Optional

from game.gamelogic.gameconstants import CLIENT_POSITIONING, GAME_CONSTANTS, USER_ROLES


def to_fixed(val, cnt):
    return float(("{:." + str(cnt) + "f}").format(val))


class State:
    def __init__(self, x, y, cp):
        self.x: float = to_fixed(x, 3)
        self.y: float = to_fixed(y, 3)
        self.cube_point: int = cp

    def set_x_y(self, x, y):
        self.x = to_fixed(x, 3)
        self.y = to_fixed(y, 3)


class GameClient:
    _uid: int
    _state: State

    def __init__(self, uid: int, turn, fnum):
        self._uid = uid
        self._turn = turn  # game num when he goes
        self._fnum = fnum  # number of point
        self._state = State(
            CLIENT_POSITIONING["CLIENT_DEFAULT_X"]
            + 0.01 * (uid % GAME_CONSTANTS["MAX_PLAYERS_IN_ROOM"]),
            CLIENT_POSITIONING["CLIENT_DEFAULT_Y"],
            -1,
        )
        self.status = GAME_CONSTANTS["PLAYER_CONNECTED"]  # player status
        self.admin = False  # is admin
        self.target = None  # player target
        self.name = None  # player name
        self.set_reg_data = False  # need register
        self.points = 5  # player points
        self.cur_position_num = 0  # cur numeric field position
        self.direction = 1  # direction
        self.resource_pool = []  # pool of cards
        self.resources = []  # resources
        self.open_elevel = False  # did he open elevel
        self.cubic_thrown = False  # did he throw cubic
        self.show_turn = False  # can show turn
        self.penalty = None  # player penalty

    def get_fnum(self):
        return self._fnum

    def get_state(self):
        return self._state

    def get_turn(self):
        return self._turn

    def get_id(self):
        return self._uid

    def get_resource(self):
        return self.resource_pool.pop(random.randint(0, len(self.resource_pool) - 1))


class Admin(GameClient):
    def __init__(self, uid: int, fnum):
        GameClient.__init__(self, uid, -1, fnum)
        self._state = None
        self.admin = True


class Game:
    room: int
    _game_state: int

    def __init__(self, room: int, resources_num: int):
        self._clients = {}
        self._spectrators = {}
        self._turns = [x for x in range(GAME_CONSTANTS["MAX_PLAYERS_IN_ROOM"])]
        self._resources = resources_num
        self._room = room
        self.game_state = GAME_CONSTANTS["GAME_STATE_W8_CLIENTS"]
        self._curr_step = -1
        self._r_step = None

    def start_game(self):
        self._curr_step = GAME_CONSTANTS["MAX_PLAYERS_IN_ROOM"] - 1

    def add_player(self, uid: int, fnum: int, role: int):
        if self._clients.get(uid) is None:
            if role == USER_ROLES["user"]:
                a = self._turns.pop(random.randint(0, len(self._turns) - 1))
                self._clients[uid] = GameClient(uid, a, fnum)
                self._clients[uid].resource_pool = [
                    x + 1 for x in range(self._resources)
                ]
                if self.game_state != GAME_CONSTANTS["GAME_STATE_W8_CLIENTS"]:
                    self._clients[uid].show_turn = True
            elif role == USER_ROLES["admin"]:
                self._clients[uid] = Admin(uid, fnum)
            else:
                self._spectrators[uid] = GAME_CONSTANTS["PLAYER_CONNECTED"]
        else:
            self._clients[uid].status = GAME_CONSTANTS["PLAYER_CONNECTED"]

    def get_player(self, uid: int) -> Optional[GameClient]:
        a = self._clients.get(uid)
        if a is not None:
            a.turn = False
            if a.status != GAME_CONSTANTS["PLAYER_DISCONNECTED"] and a.penalty is None:
                if a.get_turn() == self._curr_step:
                    a.turn = True
        return a

    def disconnect_player(self, uid: int):
        if self._clients.get(uid) is not None:
            self._clients[uid].status = GAME_CONSTANTS["PLAYER_DISCONNECTED"]
        else:
            self._spectrators.pop(uid, None)

    def get_spectrators_and_ids(self):
        return [x for x in self._spectrators] + self.get_active_ids()

    def get_spectrator(self, uid):
        return self._spectrators.get(uid)

    def get_all_ids(self):
        return [a for a in self._clients]

    def get_active_ids(self):
        rm = []
        for a in self._clients:
            if self._clients[a].status == GAME_CONSTANTS["PLAYER_CONNECTED"]:
                rm.append(a)
        return rm

    def get_penalty_ids(self):
        rm = []
        for a in self._clients:
            if self._clients[a].penalty is not None:
                rm.append(a)
        return rm

    def stepping_cli(self) -> Optional[GameClient]:
        if self.game_state == GAME_CONSTANTS["GAME_STATE_W8_CLIENTS"]:
            return None
        for a in self._clients:
            if self._clients[a].get_turn() == self._curr_step:
                return self._clients[a]

    def get_step(self):
        return self._curr_step

    def next_step(self):
        cli = self.get_active_ids()
        ls = self._curr_step
        if len(cli) <= 1:
            return False
        while True:
            self._curr_step = (self._curr_step + 1) % GAME_CONSTANTS[
                "MAX_PLAYERS_IN_ROOM"
            ]
            for a in cli:
                if (
                    self._clients[a].get_turn() == self._curr_step
                    and self._clients[a].penalty is None
                ):
                    return True
            if self._curr_step == ls:
                return False


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


class ComplexData:
    def __init__(self, plr: GameClient, act: [], act_all: []):
        self.player = plr
        self.active_players = act
        self.active_players_spct = act_all


class GameData:
    _data = None

    @classmethod
    def set_new_data(cls, uid: int):
        a = SingletonGame.get_game()
        GameData._data = ComplexData(
            a.get_player(uid), a.get_active_ids(), a.get_spectrators_and_ids()
        )

    @classmethod
    def get_data(cls) -> Optional[ComplexData]:
        return GameData._data

    @classmethod
    def exist(cls):
        if GameData._data.player is None:
            return False
        return True
