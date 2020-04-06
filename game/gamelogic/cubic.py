import random


class Cubic:
    @classmethod
    def gen_sequence(cls, numcnt, lastnum):
        ret_mas = []
        cube_pts = []
        for a in range(numcnt - 1):
            if len(cube_pts) == 0:
                cube_pts = [x + 1 for x in range(6)]
            ret_mas.append(cube_pts.pop(random.randint(0, len(cube_pts) - 1)))
        ret_mas.append(lastnum)
        return ret_mas
