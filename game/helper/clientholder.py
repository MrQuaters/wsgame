from typing import Optional, List
from fastapi import WebSocket


class BaseClientHolder:
    def get_clients_ids(self) -> []:
        pass

    def task_to_add_client(self, cli, data) -> None:
        pass

    def task_to_del_client(self, cli) -> None:
        pass

    def apply_changes(self) -> None:
        pass

    def client_get(self, cid):
        pass


class ClientHolder(BaseClientHolder):
    def __init__(self):
        self._clients = {}
        self._clients_ids = []
        self._clients_to_del = []
        self._clients_to_add = {}
        self._changed = False

    def get_clients_ids(self) -> List:
        return self._clients_ids[:]

    def task_to_add_client(self, cli, data) -> None:
        self._clients_to_add[cli] = data
        self._changed = True

    def task_to_del_client(self, cli) -> None:
        self._clients_to_del.append(cli)
        self._changed = True

    def apply_changes(self) -> None:
        if not self._changed:
            return

        for cli, val in self._clients_to_add.items():
            self._clients[cli] = val
        self._clients_to_add.clear()
        for cli in self._clients_to_del:
            self._clients.pop(cli, None)
        self._clients_to_del.clear()
        self._clients_ids.clear()
        for key in self._clients:
            self._clients_ids.append(key)

        self._changed = False

    def client_get(self, cid) -> Optional[WebSocket]:
        return self._clients.get(cid)


class SingletonClientHolder:
    __isinstance = None

    @classmethod
    def get_client_holder(cls) -> ClientHolder:
        if SingletonClientHolder.__isinstance is None:
            SingletonClientHolder.__isinstance = ClientHolder()
        return SingletonClientHolder.__isinstance
