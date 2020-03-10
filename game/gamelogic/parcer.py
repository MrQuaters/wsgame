import json

class BaseParser:

    def parse_in(self, id, room, msg):
       pass

    def parse_out(self, msg):
        pass


class Parser(BaseParser):
    def parse_in(self, id, room, msg):
        a = json.loads(msg)
        a["us_id"] = id
        a["us_room"] = room
        print(a)
        b = json.dumps(a)
        print(b)
        return b

    def parse_out(self, msg):
        return msg

