from game.gamehandlers import ActionHandler

App = ActionHandler(15)

from game import workerendpoints
from game import adminendpoint

print(workerendpoints.IMPORTED)
print(adminendpoint.IMPORTED)
