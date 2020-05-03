from game.gamelogic.gamecl import SingletonGame
from game.worker import App
from game.gamelogic.parcer import BaseParser
import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", type=int, required=True)
    arg = parser.parse_args()
    t = arg.r
    SingletonGame.create_game(t, 14, 25)
    App.run(BaseParser().create_room_name(t), "e" + BaseParser().create_room_name(t))
