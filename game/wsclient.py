from uvicorn import Server, Config
import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
from game.servicecommunicator.asynccom import BaseAsyncServiceCommunicator, SafeInit
from game.helper.clientholder import BaseClientHolder
from game.gamelogic.parcer import BaseParser


class WsClientHandler:
    def __init__(
            self, host: str, port: int, client_holder: BaseClientHolder,
            asy_com: BaseAsyncServiceCommunicator, mloop,  msg_parser: BaseParser, **fastapi_config
    ):
        self._clients = client_holder
        self._re = asy_com
        self._si = SafeInit()
        self._app = FastAPI(**fastapi_config)
        self._host = host
        self._port = port
        self._parser = msg_parser
        self._loop = mloop
        start_func = getattr(self._clients, "start", None)
        if callable(start_func):
            self._si.make_blocking(self._clients.start)
        start_func = getattr(self._re, "start", None)
        if callable(start_func):
            self._si.make_blocking(self._re.start)
        self._conf = Config(app=self._app, loop=self._loop, port=self._port, host=self._host)
        self._server = Server(self._conf)
        self._set_income_message_handler()
        self._si.add_tasks(self._set_out_message_handler)

    def run(self):
        self._si.loop_run_until_complete(self._loop, self._server.serve)

    def _set_income_message_handler(self):
        @self._app.get('/')
        async def gt():
            return HTMLResponse("ok")

        @self._app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            hid = websocket.headers.get("ID_FROM_COOKIE")
            hroom = websocket.headers.get("ROOM_FROM_COOKIE")
            if hid is None or hroom is None:
                await websocket.close()
                return
            uid = str(hid)
            uroom = str(hroom)
            self._clients.task_to_add_client(uid, websocket)
            self._loop.create_task(self._ping_task(websocket))
            while True:
                try:
                    data = await websocket.receive_text()
                    await self._re.push_in_work_channel(self._parser.parse_in(uid, uroom, data))
                except BaseException:
                    self._clients.task_to_del_client(id)
                    try:
                        await websocket.close()
                    except BaseException:
                        pass
                    return

    async def _set_out_message_handler(self):
        while True:
            self._clients.apply_changes()
            idlist = self._clients.get_clients_ids()
            if len(idlist) == 0:
                await asyncio.sleep(1)
                continue

            userd = await self._re.listen_for_clients(idlist, 1)
            if userd is not None:
                cli_ws = self._clients.client_get(userd[0])
                if cli_ws is not None:
                    try:
                        await cli_ws.send_text(self._parser.parse_out(userd[1]))
                    except BaseException:
                        self._clients.task_to_del_client(userd[0])
                        try:
                            await cli_ws.close()
                        except BaseException:
                            pass

    async def _ping_task(self, ws: WebSocket):
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
