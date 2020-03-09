class ClientHolder:
    def __init__(self):
        self._clients = {}
        self._clients_ids = []
        self._clients_to_del = []
        self._clients_to_add = {}
        self._changed = False

    def get_clients_ids(self) -> []:
        return self._clients_ids[:]

    def task_to_add_client(self, cli, data):
        self._clients_to_add[cli] = data
        self._changed = True

    def task_to_del_client(self, cli):
        self._clients_to_del.append(cli)
        self._changed = True

    def apply_changes(self):
        if not self._changed:
            return

        for cli in self._clients_to_del:
            self._clients.pop(cli, None)
        self._clients_to_del.clear()
        for cli, val in self._clients_to_add:
            self._clients[cli] = val
        self._clients_to_add.clear()
        self._clients_ids = self._clients.keys()
        self._changed = False