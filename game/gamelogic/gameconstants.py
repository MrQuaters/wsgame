WORKERS_CHANNEL = "workchannel"
CHANNEL_TO_END = "endchannel"

GET_FULL_GAME_STATE = '{"action" : "queue_end"}'
CLIENT_CONNECTED_STR = "connected"
CLIENT_CONNECTED = '{"action" : "' + CLIENT_CONNECTED_STR + '"}'
CLIENT_DISCONNECTED_STR = "disconnected"
CLIENT_DISCONNECTED = '{"action" : "' + CLIENT_DISCONNECTED_STR + '"}'


CLIENT_POSITIONING = {"CLIENT_DEFAULT_X": 0.8, "CLIENT_DEFAULT_Y": 0.16}
GAME_CONSTANTS = {
    "PLAYER_CONNECTED": 0,
    "PLAYER_DISCONNECTED": 1,
    "PLAYER_STOP": 2,
    "PLAYER_BANNED": 3,
    "MAX_PLAYERS_IN_ROOM": 6,
    "GAME_STATE_W8_CLIENTS": -1,
    "GAME_START": 0,
}
PARCER_CONSTANTS = {
    "room": "us_room",
    "action": "action",
    "role": "us_role",
    "fnum": "us_fnum",
    "room_prefix": "rmn",
    "id": "us_id",
}
USER_ROLES = {"user": 0, "admin": 1}
ACTION_LIST = {
    "conn": "connected",
    "dc": "disconnected",
    "default": "default",
    "ping": "PING",
    "pen": "add_penalty",
    "step": "set_step",
}
USER_ACTION_LIST = {"info": "get_info", "reg": "add_name", "move": "new_position"}
ANSWER_PACKAGE_NAMES = {"def": "small_pack", "big": "big_pack", "err": "error_pack"}
ADMIN_ACTION_LIST = {"start": "game_start", "step": "next_step"}
