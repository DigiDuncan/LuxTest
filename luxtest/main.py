import importlib.resources as pkg_resources

import arcade
from arcade import Window
from arcade import key

import luxtest.data.fonts
from luxtest.lib.dev_menu import DevMenu
from luxtest.views.musicmixer import MusicMixerView

FPS_CAP = 240


with pkg_resources.path(luxtest.data.fonts, "gohu.ttf") as p:
    arcade.text.load_font(str(p))


class LuxTest(Window):
    def __init__(self):
        super().__init__(1280, 720, update_rate = 1 / FPS_CAP, title = "Lux Test")

        self.menu = DevMenu({
            "Music Mixer": MusicMixerView
        })

    def on_key_press(self, symbol: int, modifiers: int):
        match symbol:
            case key.UP:
                self.menu.selected -= 1
            case key.DOWN:
                self.menu.selected += 1
            case key.ENTER:
                self.show_view(self.menu.current_view())

    def on_draw(self):
        self.menu.draw()


def main():
    LuxTest().run()


if __name__ == "__main__":
    main()
