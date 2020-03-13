from fastapi.responses import HTMLResponse
from fastapi import FastAPI, WebSocket
from game.helper.clientholder import SingletonClientHolder
from game.servicecommunicator.asynccom import SingletonAsyncServerCommunicator
from game.gamelogic.parcer import Parser
from game.gamelogic.gameconstants import CLIENT_CONNECTED, CLIENT_DISCONNECTED
import asyncio


app = FastAPI(redoc_url=None, docs_url=None)

@app.get('/')
async def gt():
    return HTMLResponse("ok")


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


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    hid = websocket.headers.get("ID_FROM_COOKIE")
    hroom = websocket.headers.get("ROOM_FROM_COOKIE")
    if hid is None or hroom is None:
        try:
            await websocket.close()
        except BaseException:
            pass
        return

    uid = str(hid)
    uroom = str(hroom)
    client_holder = SingletonClientHolder.get_client_holder()
    client_holder.task_to_add_client(uid, websocket)
    work_channel = await SingletonAsyncServerCommunicator.get_communicator()
    loop = asyncio.get_event_loop()
    loop.create_task(ping_task(websocket))
    parser = Parser()
    try:
        await work_channel.push_in_work_channel(parser.parse_in_dec(uid, uroom, CLIENT_CONNECTED))
        while True:
            data = await websocket.receive_text()
            await work_channel.push_in_work_channel(parser.parse_in_dec(uid, uroom, data))

    except BaseException:
        client_holder.task_to_del_client(uid)
        await work_channel.push_in_work_channel(parser.parse_in_dec(uid, uroom, CLIENT_DISCONNECTED))
        try:
            await websocket.close()
        except BaseException:
            pass
        return
