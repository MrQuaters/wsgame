from .parcer import WorkerParser


class Answer:
    def __init__(self, fnum: int, action: str):
        self.fnum = fnum
        self.action = action
        self.w_value = None
        self.x = None
        self.y = None

    def set_x_y(self, st):
        if st is not None:
            self.x = st.x
            self.y = st.y

    def get_ret_object(self):
        t = {"fnum": self.fnum, "action": self.action}
        if self.w_value:
            t["w_value"] = self.w_value
        if self.x:
            t["x"] = self.x
            t["y"] = self.y

        return WorkerParser.parse_out(t)
