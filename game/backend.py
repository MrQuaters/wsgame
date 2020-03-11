import asyncio
from game.helper.clientholder import SingletonClientHolder
from game.servicecommunicator.asynccom import AsyncServiceCommunicator
from game.gamelogic.parcer import Parser


async def set_out_message_handler():
    client_holder = SingletonClientHolder.get_client_holder()
    service_communicator = AsyncServiceCommunicator()
    parser = Parser()
    await service_communicator.start()
    while True:
        client_holder.apply_changes()
        id_list = client_holder.get_clients_ids()
        if len(id_list) == 0:
            await asyncio.sleep(1)
            continue
        user_data = await service_communicator.listen_for_clients(id_list, 1)
        if user_data is not None:
            cli_ws = client_holder.client_get(user_data[0])
            if cli_ws is not None:
                try:
                    await cli_ws.send_text(parser.parse_out(user_data[1]))
                except BaseException:
                    client_holder.task_to_del_client(user_data[0])
                    try:
                        await cli_ws.close()
                    except BaseException:
                        pass
