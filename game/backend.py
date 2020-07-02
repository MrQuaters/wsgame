import asyncio
from game.helper.clientholder import SingletonClientHolder
from game.servicecommunicator.asynccom import AsyncServiceCommunicator
from game.gamelogic.parcer import Parser


async def set_out_message_handler():  # circle that gets data from worker process and send it to cli
    client_holder = SingletonClientHolder.get_client_holder()
    service_communicator = AsyncServiceCommunicator()
    parser = Parser()
    await service_communicator.start()
    while True:
        client_holder.apply_changes()  # apply new cli and del disc cli, bsc prog is async should be done in 1 place
        id_list = client_holder.get_clients_ids()  # get list of ids cli connected
        if len(id_list) == 0:  # if no ids sleep for 1s
            await asyncio.sleep(1)
            continue
        user_data = await service_communicator.listen_for_clients(
            id_list, 1
        )  # w8 for data from worker 1s limit need
        # for new users handle
        if user_data is not None:  # std procedure for sending data to cli
            cli_ws = client_holder.client_get(user_data[0])
            if cli_ws is not None:
                try:
                    await cli_ws.send_text(parser.parse_out(user_data[1]))
                except BaseException:
                    try:
                        await cli_ws.close()
                    except BaseException:
                        pass
