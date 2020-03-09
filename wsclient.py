from uvicorn import Server, Config
import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from servicecommunicator import AsyncServiceCommunicator, SafeInit
from helper import ClientHolder
from gamelogic import Parser
import uvloop


app = FastAPI(docs_url=None, redoc_url=None)
re = AsyncServiceCommunicator()
clients = ClientHolder()
loop = uvloop.new_event_loop()
asyncio.set_event_loop(loop)


async def safe_re_init():
    await re.start()


async def worker_sender():
    while True:
        userd = await re.listen_for_clients(clients.get_clients_ids(), 1)
        if userd is not None:
            cli_ws = clients.client_get(userd[0])
            if cli_ws is not None:
                try:
                    await cli_ws.send_text(Parser.parse_input(userd[1]))
                except BaseException:
                    try:
                        clients.task_to_del_client(userd[0])
                        await cli_ws.close()
                    except BaseException:
                        pass

        clients.apply_changes()


async def ping_task(ws: WebSocket):
    while True:
        try:
            await asyncio.wait_for(ws.send_text("PING"), timeout=5)
            await asyncio.sleep(5)

        except BaseException:
            try:
                await ws.close()
            except BaseException:
                pass
            return


@app.get('/')
async def gt():
    return HTMLResponse("ok")


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    id = str(12)
    clients.task_to_add_client(id, websocket)
    loop.create_task(ping_task(websocket))
    while True:
        try:
            data = await websocket.receive_text()

        except BaseException:
            try:
                await websocket.close()
            except BaseException:
                pass
            clients.task_to_del_client(id)
            return




if __name__ == "__main__":
    config = Config(app=app, loop=loop, port=8083, host="127.0.0.1")
    server = Server(config=config)
    sn = SafeInit()
    sn.make_blocking(safe_re_init)
    sn.add_tasks(worker_sender)
    sn.loop_run_until_complete(loop, server.serve)