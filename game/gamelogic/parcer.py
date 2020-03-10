import json

class BaseParser:

    def parse_in(self, id, room, msg):
       pass

    def parse_out(self, msg):
        pass


class Parser(BaseParser):
    def parse_in(self, uid, room, msg):
        a = json.loads(msg)
        a["us_id"] = uid
        a["us_room"] = room
        b = json.dumps(a)
        return b

    def parse_out(self, msg):
        return msg

