import importlib.resources as pkg_resources

import arcade
from arcade import Window

import luxtest.data.fonts
from luxtest.views.mainmenu import MenuView

FPS_CAP = 240


with pkg_resources.path(luxtest.data.fonts, "gohu.ttf") as p:
    arcade.text.load_font(str(p))


class LuxTest(Window):
    def __init__(self):
        super().__init__(1280, 720, update_rate = 1 / FPS_CAP, title = "Lux Test")

        self.show_view(MenuView())


def main():
    LuxTest().run()


if __name__ == "__main__":
    main()
