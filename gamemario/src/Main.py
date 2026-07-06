import pyglet

import arcade
from Settings import SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE
from menu_view import MenuView
from sound_manager import stop_all_sounds


class GameWindow(arcade.Window):
    def on_close(self):
        stop_all_sounds()
        super().on_close()


def main():
    window = GameWindow(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE, antialiasing=False, vsync=False)
    view = MenuView()
    window.show_view(view)
    arcade.run()


if __name__ == "__main__":
    main()



