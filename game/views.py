import asyncio

from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import subprocess
import os
import json

from game.gamelogic.answers import Answer
from game.gamelogic.gameconstants import (
    CLIENT_CONNECTED,
    CLIENT_DISCONNECTED,
    ACTION_LIST,
)
from game.gamelogic.gameconstants import SERVER_COMMUNICATING_CONSTANTS as SCC
from game.gamelogic.parcer import Parser
from game.helper.clientholder import SingletonClientHolder
from game.servicecommunicator.asynccom import (
    SingletonAsyncServerCommunicator,
    AsyncServiceCommunicator,
)

app = FastAPI(redoc_url=None, docs_url=None)

sp = {}


@app.get("/ping")
async def png(room: int, admin: str):
    retv = {
        SCC["CHECK_IN_DICT"]: False,
        SCC["PING_GOOD"]: False,
        SCC["POLL_CODE"]: False,
    }
    prc = sp.get(room, None)
    if prc is not None:
        retv[SCC["CHECK_IN_DICT"]] = True
        d = prc.poll()
        if d is None:
            retv[SCC["POLL_CODE"]] = True
        else:
            retv[SCC["POLL_CODE"]] = d
    com = AsyncServiceCommunicator()
    await com.start()
    ps = Parser()
    cmd = {"action": SCC["PING_COMMAND"], SCC["W8ANSWERIN"]: admin + str(room) + "ping"}
    await com.push_in_channel("e" + ps.create_room_name(room), ps.parse_in(cmd))
    await com.set_expires_channel("e" + ps.create_room_name(room), 5)
    msg = await com.listen_for_clients([admin + str(room) + "ping"], 8)
    if msg is not None:
        retv[SCC["PING_GOOD"]] = True
    return HTMLResponse(json.dumps(retv))


@app.get("/close")
async def cls(room: int, admin: str):
    log = {}
    com = AsyncServiceCommunicator()
    await com.start()
    ps = Parser()
    cmd = {"action": SCC["SERV_STOP"], SCC["W8ANSWERIN"]: admin + str(room) + "close"}
    await com.push_in_channel("e" + ps.create_room_name(room), ps.parse_in(cmd))
    await com.set_expires_channel("e" + ps.create_room_name(room), 5)
    msg = await com.listen_for_clients([admin + str(room) + "close"], 8)
    prc = sp.pop(room, None)
    if prc is None:
        log["err"] = "NoServinlocal"
        if msg is None:
            log["CRITICAL"] = "CAN NOT STOP ROOM"
            return HTMLResponse(json.dumps(log))
    else:
        g = prc.poll()
        if g is None:
            log["err1"] = "DOING SIGKILL"
            prc.kill()
        else:
            log["OK"] = "CLOSED OK"
    return HTMLResponse(json.dumps(log))


@app.get("/open")
async def gt(room: int):
    cd = os.getcwd()
    args = ["python", cd + "/roomhandler.py", "-r", str(room)]
    sp[room] = subprocess.Popen(
        args,
        stderr=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stdin=subprocess.DEVNULL,
    )
    print("starting room" + str(room))
    return HTMLResponse("ok")


async def ping_task(ws: WebSocket):  # ping task to find crit disconected clients
    while True:
        try:
            await asyncio.wait_for(
                ws.send_text(Answer(None, ACTION_LIST["ping"]).get_ret_object()),
                timeout=5,
            )
            await asyncio.sleep(30)

        except BaseException:
            try:
                await ws.close()
            except BaseException:
                pass
            return


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):  # endpoint wor websocket
    await websocket.accept()
    hid = websocket.headers.get(
        "ID_FROM_COOKIE"
    )  # headers defined in nginx config, putted by nginx in auth req
    hroom = websocket.headers.get("ROOM_FROM_COOKIE")
    role = websocket.headers.get("ROLE_FROM_COOKIE")
    fnum = websocket.headers.get("FNUM_FROM_COOKIE")
    if (
        hid is None or hroom is None or role is None or fnum is None
    ):  # if no headers - bad req
        try:
            await websocket.close()
        except BaseException:
            pass
        return

    uid = str(hid)
    uroom = str(hroom)
    role = str(role)
    fnum = str(fnum)
    client_holder = (
        SingletonClientHolder.get_client_holder()
    )  # get client holder abstraction. Needed for info about
    # connected clients
    client_holder.task_to_add_client(uid, websocket)
    work_channel = (
        await SingletonAsyncServerCommunicator.get_communicator()
    )  # with this abstraction we can send data
    # to worker process that will handle game room
    loop = asyncio.get_event_loop()
    loop.create_task(ping_task(websocket))  # creating detached ping task
    parser = Parser()
    try:  # push data to worker process about new cli
        await work_channel.push_in_channel(
            parser.create_room_name(uroom),
            parser.parse_in_dec(uid, uroom, role, fnum, CLIENT_CONNECTED),
        )
        while True:  # inf circle, get data from ws
            data = await websocket.receive_text()
            await work_channel.push_in_channel(  # add std headers to data and push one to worker channel
                parser.create_room_name(uroom),
                parser.parse_in_dec(uid, uroom, role, fnum, data),
            )

    except BaseException:  # if cli disconected or some trouble with broker, safe close client and exit from circle
        client_holder.task_to_del_client(uid)
        await work_channel.push_in_channel(
            parser.create_room_name(uroom),
            parser.parse_in_dec(uid, uroom, role, fnum, CLIENT_DISCONNECTED),
        )
        try:
            await websocket.close()
        except BaseException:
            pass
        return
