import random


class PlayingCubic:
    def __init__(self):
        self.top = 2
        self.bot = 5
        self.front = 1
        self.beh = 6
        self.left = 3
        self.right = 4

    @classmethod
    def to_pos(self, pos):
        r = random.randint(0, 1)
        if pos == 1:
            return [0, 0]
        if pos == 2:
            if r % 2 == 0:
                return [3, 0]
            else:
                return [-1, 0]
        if pos == 3:
            return [0, 1]
        if pos == 4:
            return [0, -1]
        if pos == 5:
            if r % 2 == 0:
                return [-3, 0]
            else:
                return [1, 0]
        if pos == 6:
            if r % 2 == 0:
                return [-2, 0]
            else:
                return [2, 0]


class Cubic:
    @classmethod
    def gen_sequence(cls, numcnt, lastnum):
        ret_mas = []
        c = random.randint(0, 1)
        g = random.randint(0, 1)
        rx = 0
        ry = 0
        for a in range(numcnt):
            o = random.randint(0, 1)
            rt = (-2 * c + 1) * o
            if rt == 0:
                o = 1
            else:
                o = random.randint(0, 1)
            rg = (-2 * g + 1) * o
            ret_mas.append([rt, rg])
            rx += rt
            ry += rg

        rx = abs(rx) % 4
        ry = abs(ry) % 4
        if rx > 0:
            rx = 4 - rx
        if ry > 0:
            ry = 4 - ry

        while rx > 0 or ry > 0:
            rk = [0, 0]
            if rx > 0:
                rk[0] = -2 * c + 1
                rx -= 1
            if ry > 0:
                rk[1] = -2 * g + 1
                ry -= 1
            ret_mas.append(rk)

        g = PlayingCubic.to_pos(lastnum)
        kx = 1
        ky = 1
        if g[0] < 0:
            kx = -1
        if g[1] < 0:
            ky = -1
        for a in range(len(ret_mas)):
            if ret_mas[a][0] == 0 and abs(g[0]) > 0:
                g[0] -= kx
                ret_mas[a][0] = kx

            if ret_mas[a][1] == 0 and abs(g[1]) > 0:
                g[1] -= ky
                ret_mas[a][1] = ky

        if abs(g[0]) > 0 or abs(g[1]) > 0:
            ret_mas.append(g)

        return ret_mas
