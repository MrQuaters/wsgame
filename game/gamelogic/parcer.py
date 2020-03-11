import json

class BaseParser:

    def parse_in(self, msg):
       pass

    def parse_out(self, msg):
        pass


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
