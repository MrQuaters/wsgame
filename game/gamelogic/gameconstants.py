WORKERS_CHANNEL = "workchannel"
CHANNEL_TO_END = "endchannel"

GET_FULL_GAME_STATE = '{"action" : "queue_end"}'
CLIENT_CONNECTED_STR = "connected"
CLIENT_CONNECTED = '{"action" : "' + CLIENT_CONNECTED_STR + '"}'
CLIENT_DISCONNECTED_STR = "disconnected"
CLIENT_DISCONNECTED = '{"action" : "' + CLIENT_DISCONNECTED_STR + '"}'


CLIENT_POSITIONING = {
    "CLIENT_DEFAULT_X": 0.8,
    "CLIENT_DEFAULT_Y": 0.16,
    "CLIENT_WIN_POS_X": 0.45,
    "CLIENT_WIN_POS_Y": 0.49,
}
GAME_CONSTANTS = {
    "PLAYER_CONNECTED": 0,
    "PLAYER_DISCONNECTED": 1,
    "PLAYER_STOP": 2,
    "PLAYER_BANNED": 3,
    "MAX_PLAYERS_IN_ROOM": 6,
    "GAME_STATE_W8_CLIENTS": -1,
    "GAME_START": 0,
    "FIELD_LAST_NUM": 16,
}
PARCER_CONSTANTS = {
    "room": "us_room",
    "action": "action",
    "role": "us_role",
    "fnum": "us_fnum",
    "room_prefix": "rmn",
    "id": "us_id",
}
USER_ROLES = {"user": 0, "admin": 1, "spec": 2}
ACTION_LIST = {
    "conn": "connected",
    "dc": "disconnected",
    "default": "default",
    "ping": "PING",
    "pen": "add_penalty",
    "step": "set_step",
    "cubic": "show_cubic",
    "yncubic": "show_ycubic",
    "elvl": "get_elevel",
    "resource": "get_resource",
    "can_throw_num": "set_numcubic",
    "can_move": "set_move_handle",
    "can_take_resource": "set_resource_take",
    "can_throw_yn": "set_yncubic",
    "card_data": "ret_card_data",
    "target_data": "ret_card_data",
    "rem_pen": "pentalty_remove",
}
USER_ACTION_LIST = {
    "info": "get_info",
    "reg": "add_name",
    "move": "new_position",
    "cubic": "throw_cubic",
    "elvl": "get_elevel",
    "resource": "get_resource",
    "ycubic": "throw_ycubic",
    "card_data": "get_card_data",
    "target_data": "get_player_target",
}
ANSWER_PACKAGE_NAMES = {"def": "small_pack", "big": "big_pack", "err": "error_pack"}
ADMIN_ACTION_LIST = {
    "start": "game_start",
    "step": "next_step",
    "allow_yn": "allow_yn",
    "ban_unban": "ban_unban",
}
PENALTY_LIST = {"win": "game_win", "stop": "player_stop"}
