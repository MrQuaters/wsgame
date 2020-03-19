import json


class BaseParser:

    def parse_in(self, msg):
       pass

    def parse_out(self, msg):
        pass

    def create_room_name(self, room):
        return "rmn"+str(room)


class Parser(BaseParser):
    def parse_in_dec(self, uid, room, msg):
        a = json.loads(msg)
        a["us_id"] = uid
        a["us_room"] = room
        return self.parse_in(a)

    def parse_in(self, msg):
        b = json.dumps(msg)
        return b

    def parse_out(self, msg):
        return msg


class WorkerParser(BaseParser):
    def parse_in(self, msg):
        a = json.loads(msg)
        return a.pop("action", None), a.pop("us_id", None), a.pop("us_room", None), a