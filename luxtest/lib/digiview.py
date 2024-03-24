from __future__ import annotations

from arcade import View, Window
import arcade


class DigiView(View):
    def __init__(self, window: Window | None = None, back: DigiView = None):
        super().__init__(window)
        self.back = back

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.BACKSPACE:
            self.window.show_view(self.back)
        return super().on_key_press(symbol, modifiers)
