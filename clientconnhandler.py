from game.wsclient import WsClientHandler
from game.servicecommunicator.asynccom import AsyncServiceCommunicator
from game.gamelogic.parcer import Parser
from game.helper.clientholder import ClientHolder
import uvloop
import asyncio


if __name__ == "__main__":
    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)
    a = WsClientHandler(
        "127.0.0.1", 8083, ClientHolder(), AsyncServiceCommunicator(), loop, Parser(), docs_url=None, redoc_url=None
    )
    a.run()
