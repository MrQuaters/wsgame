import uvloop
import asyncio
from game.backend import set_out_message_handler
from uvicorn import Server, Config
from game.views import app


if __name__ == "__main__":
    loop = uvloop.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.create_task(set_out_message_handler())  # task for worker listener loop
    config = Config(app=app, host="0.0.0.0", port=8083)
    server = Server(config)
    loop.run_until_complete(server.serve())  # run server loop
