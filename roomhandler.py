from game.gamelogic.gamecl import SingletonGame
from game.worker import App

if __name__ == "__main__":
    SingletonGame.create_game(18, 14, 25)
    App.run("rmn18", "ermn18")
