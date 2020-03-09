import redis
from gamelogic import Game
from gamelogic import gameconstants

MAX_QUEUE_LENGTH = 4

re = redis.Redis(host="localhost", port=6379, db=0)
game = Game()

while True:
    ch, msg = re.blpop(
        [gameconstants.WORKERS_CHANNEL, gameconstants.CHANNEL_TO_END], timeout=0
    )

    nmsg = msg.decode("UTF-8")
    ch = ch.decode("UTF-8")

    if ch == gameconstants.CHANNEL_TO_END:
        break

    sendto, nmsg = game.gameLogic(nmsg)
    msg = nmsg.encode("utf-8")

    for address in sendto:
        ln = re.llen(address)
        if ln < MAX_QUEUE_LENGTH:
            re.rpush(address, msg)
        elif ln == MAX_QUEUE_LENGTH:
            re.rpush(address, gameconstants.GET_FULL_GAME_STATE)
        else:
            pass
