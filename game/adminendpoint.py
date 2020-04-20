import game.gamelogic.gameconstants as GC
from game.gamelogic.answers import (
    Answer,
    CliRetPosAnswer,
    ErrorActAnswer,
    print_step_set,
)
from game.gamelogic.gamecl import GameData, SingletonGame, PlayerState
from game.gamehandlers import DelayedSend
from .worker import App


IMPORTED = "ADMINIMPORT"


def IGNORE():
    return [], " "


@App.register(GC.ADMIN_ACTION_LIST["start"])
def game_start(game_obj):
    a = GameData.get_data()
    if not a.player.admin:
        return IGNORE()
    game = SingletonGame.get_game()
    if game.game_state != GC.GAME_CONSTANTS["GAME_STATE_W8_CLIENTS"]:
        return [a.player.get_id()], ErrorActAnswer("GameStarted").get_ret_object()
    clients = game.get_all_ids()
    game.game_state = GC.GAME_CONSTANTS["GAME_START"]
    game.start_game()
    ns = game.next_step()
    if not ns:
        game.game_state = GC.GAME_CONSTANTS["GAME_STATE_W8_CLIENTS"]
        return [a.player.get_id()], ErrorActAnswer("NoPlayers").get_ret_object()
    cli = game.stepping_cli()
    for c in clients:
        r = game.get_player(c)
        r.show_turn = True
        DelayedSend.set_send(
            [r.get_id()], Answer(r, GC.ACTION_LIST["get_info"], True).get_ret_object()
        )

    DelayedSend.set_send(
        a.active_players_spct,
        Answer(
            cli,
            GC.ACTION_LIST["card_data"],
            print_step_set(game, "ИГРА НАЧАЛАСЬ! Порядок ходов:\n"),
            lowpack=True,
        ).get_ret_object(),
    )

    return [a.player.get_id()], ErrorActAnswer("GameSTARTED").get_ret_object()


@App.register(GC.ADMIN_ACTION_LIST["step"])
def next_step(game_obj):
    a = GameData.get_data()
    if not a.player.admin:
        return IGNORE()
    game = SingletonGame.get_game()
    if game.game_state == GC.GAME_CONSTANTS["GAME_STATE_W8_CLIENTS"]:
        return [a.player.get_id()], ErrorActAnswer("GameNotStarted").get_ret_object()
    ns = game.next_step()
    if not ns:
        return [a.player.get_id()], ErrorActAnswer("NoPlayers").get_ret_object()

    cli = game.stepping_cli()
    cli.cubic_thrown = False
    cli.yncubic_thrown = False
    cl_data = CliRetPosAnswer(cli)
    for cr in cl_data.get_my_ret_obj():
        DelayedSend.set_send([cli.get_id()], cr)
    for cr in cl_data.get_pub_ret_obj():
        DelayedSend.set_send(a.active_players_spct, cr)
    return a.active_players_spct, Answer(cli, GC.ACTION_LIST["step"]).get_ret_object()


@App.register(GC.ADMIN_ACTION_LIST["allow_yn"])
def allow_yn(game_obj):
    a = GameData.get_data()
    if not a.player.admin:
        return IGNORE()
    game = SingletonGame.get_game()
    cli = game.stepping_cli()
    if cli is None:
        return (
            [a.player.get_id()],
            ErrorActAnswer("NoActiveCliOrGameNotStarted").get_ret_object(),
        )
    if cli.penalty is not None:
        return [a.player.get_id()], ErrorActAnswer("CliHavePenalty").get_ret_object()
    if cli.player_state != PlayerState.set_thinking_state():
        return [a.player.get_id()], ErrorActAnswer("PlayerStillMoving").get_ret_object()
    cli.player_state = PlayerState.set_yncubic_state()
    return (
        [cli.get_id()],
        Answer(cli, GC.ACTION_LIST["can_throw_yn"], True, True).get_ret_object(),
    )


@App.register(GC.ADMIN_ACTION_LIST["ban_unban"])
def bun_unban(game_obj):
    a = GameData.get_data()
    if not a.player.admin:
        return IGNORE()
    fnm = game_obj.get("fnm", None)
    if fnm is None:
        return IGNORE()
    game = SingletonGame.get_game()
    cli = game.get_player_fnum(fnm)
    if cli is None:
        return IGNORE()
    if cli.penalty is None:
        cli.penalty = GC.PENALTY_LIST["stop"]
    elif cli.penalty == GC.PENALTY_LIST["win"]:
        return IGNORE()
    else:
        cli.penalty = None
    if cli.penalty is None:
        return (
            game.get_spectrators_and_ids(),
            Answer(cli, GC.ACTION_LIST["rem_pen"]).get_ret_object(),
        )
    else:
        return (game.get_spectrators_and_ids(), Answer(cli).get_ret_object())


@App.register(GC.ADMIN_ACTION_LIST["session"])
def session(game_obj):
    a = GameData.get_data()
    if not a.player.admin:
        return IGNORE()
    game = SingletonGame.get_game()
    cli = game.stepping_cli()
    if cli is None or cli.player_state != PlayerState.set_thinking_state():
        return (
            [a.player.get_id()],
            ErrorActAnswer("NoActiveCliOrGameNotStarted").get_ret_object(),
        )
    if cli.points < 3:
        return ([a.player.get_id()], ErrorActAnswer("NotEnoughPoints").get_ret_object())
    cli.points -= 3
    return a.active_players_spct, Answer(cli).get_ret_object()


@App.register(GC.ADMIN_ACTION_LIST["allow_res"])
def allow_res(game_obj):
    a = GameData.get_data()
    if not a.player.admin:
        return IGNORE()
    game = SingletonGame.get_game()
    cli = game.stepping_cli()
    if cli is None or cli.player_state != PlayerState.set_thinking_state():
        return (
            [a.player.get_id()],
            ErrorActAnswer("NoActiveCliOrGameNotStarted").get_ret_object(),
        )
    if cli.points < 1:
        return ([a.player.get_id()], ErrorActAnswer("NotEnoughPoints").get_ret_object())
    cli.can_take_resource = True
    return (
        [cli.get_id()],
        Answer(cli, GC.ACTION_LIST["can_take_resource"], True, True).get_ret_object(),
    )
