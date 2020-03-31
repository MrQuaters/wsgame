from game.worker import App
from game.gamelogic.gamecl import SingletonGame


if __name__ == "__main__":
    SingletonGame.create_game(18, 32, 50)
    App.run("rmn18", "ermn18")
