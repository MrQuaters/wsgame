import json
from .gameconstants import PARCER_CONSTANTS


class BaseParser:
    def parse_in(self, msg):
        pass

    def parse_out(self, msg):
        pass

    def create_room_name(self, room):
        return PARCER_CONSTANTS["room_prefix"] + str(room)


class Parser(BaseParser):
    def parse_in_dec(self, uid, room, role, fnum, msg):
        a = json.loads(msg)
        a[PARCER_CONSTANTS["id"]] = uid
        a[PARCER_CONSTANTS["room"]] = room
        a[PARCER_CONSTANTS["role"]] = role
        a[PARCER_CONSTANTS["fnum"]] = fnum
        return self.parse_in(a)

    def parse_in(self, msg):
        b = json.dumps(msg)
        return b

    def parse_out(self, msg):
        return msg


class WorkerParser(BaseParser):
    def parse_in(self, msg):
        a = json.loads(msg)
        return (
            a.pop(PARCER_CONSTANTS["action"], None),
            a.pop(PARCER_CONSTANTS["id"], None),
            a,
        )

    @classmethod
    def parse_out(cls, msg):
        return json.dumps(msg)
