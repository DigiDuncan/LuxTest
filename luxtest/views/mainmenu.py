import logging

from arcade import key

from luxtest.lib.dev_menu import DevMenu
from luxtest.lib.digiview import DigiView
from luxtest.views.musicmixer import MusicMixerView

logger = logging.getLogger("charm")


class MenuView(DigiView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.menu = DevMenu({
            "Music Mixer": MusicMixerView(back = self)
        })

    def on_key_press(self, symbol: int, modifiers: int):
        match symbol:
            case key.UP:
                self.menu.selected -= 1
            case key.DOWN:
                self.menu.selected += 1
            case key.ENTER:
                self.window.show_view(self.menu.current_view)

    def on_draw(self):
        self.clear()
        self.menu.draw()
