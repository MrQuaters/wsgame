from typing import NamedTuple
from game.gamelogic.gameconstants import CLIENT_POSITIONING, GAME_CONSTANTS


class State(NamedTuple):
    x: int
    y: int
    cube_point: int


class GameClient:
    _uid: int
    _state: State
    _status: int

    def __init__(self, uid: int):
        self._uid = uid
        self._state = State(
            CLIENT_POSITIONING["CLIENT_DEFAULT_X"] + 0.01 * (uid % GAME_CONSTANTS["MAX_PLAYERS_IN_ROOM"]),
            CLIENT_POSITIONING["CLIENT_DEFAULT_Y"],
            -1
        )
        self._status = -1

    def get_state(self):
        return self._state

    def get_status(self):
        return self._status

    def set_status(self, status):
        self._status = status


class Game:
    _room: int
    _game_state: int
    _current_step: int

    def __init__(self, room: int):
        self._clients = {}
        self._admin = None
        self._room = room

    def add_admin(self, uid):
        self._admin = GameClient(uid)

    def add_player(self, uid: int):
        self._clients[uid] = GameClient(uid)

    def get_player(self, uid: int) -> GameClient:
        return self._clients.get(uid)

