import importlib.resources as pkg_resources
import logging

import arcade
from arcade import Sprite, SpriteList, Texture
from arcade.experimental.bloom_filter import BloomFilter
from arcade.geometry import is_point_in_box
from arcade.types import Color
import pyglet.media as media

import luxtest.data.music
from luxtest.lib.digiview import DigiView

logger = logging.getLogger("charm")


class RGBMusicMixer:
    def __init__(self, sounds: arcade.Sound, volume = 1.0):
        """Plays exactly three tracks based on color.

        Implements most of the functions of pyglet.media.Player.
        """
        if len(sounds) != 3:
            raise ValueError("RGBMusicMixer requires three sounds!")
        self.tracks: list[media.Player] = [s.play(volume = volume) for s in sounds]
        self.volume = volume
        self.pause()
        self.seek(0)

        self._red = True
        self._green = True
        self._blue = True

    @property
    def red(self) -> bool:
        return self._red

    @red.setter
    def red(self, v: bool):
        self._red = v
        self.r.volume = self.volume if v else 0

    @property
    def green(self) -> bool:
        return self._green

    @green.setter
    def green(self, v: bool):
        self._green = v
        self.g.volume = self.volume if v else 0

    @property
    def blue(self) -> bool:
        return self._blue

    @blue.setter
    def blue(self, v: bool):
        self._blue = v
        self.b.volume = self.volume if v else 0

    @property
    def r(self) -> media.Player:
        return self.tracks[0]

    @r.setter
    def r(self, sound: arcade.Sound):
        self.tracks[0] = sound.play(volume = self.volume if self._red else 0)
        self.tracks[0].seek(self.time)

    @property
    def g(self) -> media.Player:
        return self.tracks[1]

    @g.setter
    def g(self, sound: arcade.Sound):
        self.tracks[1] = sound.play(volume = self.volume if self._green else 0)
        self.tracks[1].seek(self.time)

    @property
    def b(self) -> media.Player:
        return self.tracks[2]

    @b.setter
    def b(self, sound: arcade.Sound):
        self.tracks[2] = sound.play(volume = self.volume if self._blue else 0)
        self.tracks[2].seek(self.time)

    @property
    def color(self) -> Color:
        return Color(255 if self._red else 0, 255 if self._green else 0, 255 if self._blue else 0)

    @color.setter
    def color(self, color: Color):
        self.red = 255 if color.r > 127 else 0
        self.green = 255 if color.g > 127 else 0
        self.blue = 255 if color.b > 127 else 0

    @property
    def time(self) -> float:
        if not self.tracks:
            return 0.0
        return self.tracks[0].time

    @property
    def duration(self) -> float:
        if not self.tracks:
            return 0.0
        return max([t.source.duration if t.source else 0 for t in self.tracks])

    @property
    def playing(self) -> bool:
        if not self.tracks:
            return False
        return self.tracks[0].playing

    def seek(self, time):
        playing = self.playing
        if playing:
            self.pause()
        for t in self.tracks:
            t.seek(time)
        if playing:
            self.play()

    def play(self):
        self.sync()
        for t in self.tracks:
            t.play()

    def pause(self):
        for t in self.tracks:
            t.pause()

    def close(self):
        self.pause()
        for t in self.tracks:
            t.delete()
        self.tracks = []

    @property
    def loaded(self) -> bool:
        return bool(self.tracks)

    def sync(self):
        maxtime = max(t.time for t in self.tracks)
        self.seek(maxtime)


class MusicMixerView(DigiView):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        sounds: list[arcade.Sound] = []
        for s in ["stem_1.mp3", "stem_2.mp3", "stem_3.mp3"]:
            with pkg_resources.path(luxtest.data.music, s) as p:
                sounds.append(arcade.load_sound(p))
        self.rgbmusic = RGBMusicMixer(sounds)

        self.red = (0, 0, 0, 0)
        self.green = (0, 0, 0, 0)
        self.blue = (0, 0, 0, 0)
        self.square = (0, 0, 0, 0)
        self.color_square = (0, 0, 0, 0)

        self.tex = Texture.create_empty("rgbmusic", (1280, 720))
        self.sprite = Sprite(self.tex, center_x = self.window.width // 2, center_y = self.window.height // 2)
        self.sprite_list = SpriteList()
        self.sprite_list.append(self.sprite)

        self.bloom_level = 5.0
        self.bloom_filter = BloomFilter(1280, 720, 5.0)

        self.calc_pos()

    def on_show_view(self):
        self.rgbmusic.play()
        self.bloom_level = 5.0
        self.bloom_filter = BloomFilter(1280, 720, 5.0)

    def on_hide_view(self):
        self.rgbmusic.pause()
        self.rgbmusic.seek(0)

    def on_mouse_press(self, x: int, y: int, button: int, modifiers: int):
        if button == arcade.MOUSE_BUTTON_LEFT:
            if is_point_in_box((self.red[0], self.red[2]), (x, y), (self.red[1], self.red[3])):
                self.rgbmusic.red = not self.rgbmusic.red
            elif is_point_in_box((self.green[0], self.green[2]), (x, y), (self.green[1], self.green[3])):
                self.rgbmusic.green = not self.rgbmusic.green
            elif is_point_in_box((self.blue[0], self.blue[2]), (x, y), (self.blue[1], self.blue[3])):
                self.rgbmusic.blue = not self.rgbmusic.blue

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.UP:
            self.bloom_level += 1.0
            self.bloom_filter = BloomFilter(1280, 720, self.bloom_level)
        elif symbol == arcade.key.DOWN:
            self.bloom_level -= 1.0
            self.bloom_filter = BloomFilter(1280, 720, self.bloom_level)
        return super().on_key_press(symbol, modifiers)

    def calc_pos(self):
        ww, wh = arcade.get_window().size
        wcw = ww / 2

        one_third_h = wh / 3
        two_thirds_h = one_third_h * 2
        one_sixth_h = one_third_h / 2
        one_ninth_h = one_third_h / 3

        square_left = wcw - one_sixth_h
        square_center_x = wcw

        red_top = two_thirds_h
        red_bottom = green_top = red_top - one_ninth_h
        green_bottom = blue_top = green_top - one_ninth_h
        blue_bottom = blue_top - one_ninth_h

        ww, wh = arcade.get_window().size
        wcw = ww / 2

        one_third_h = wh / 3
        two_thirds_h = one_third_h * 2
        one_sixth_h = one_third_h / 2

        square_left = wcw - one_sixth_h
        square_center_x = wcw
        square_right = wcw + one_sixth_h
        square_top = two_thirds_h
        square_bottom = one_third_h

        self.red = (square_left, square_center_x, red_bottom, red_top)
        self.green = (square_left, square_center_x, green_bottom, green_top)
        self.blue = (square_left, square_center_x, blue_bottom, blue_top)
        self.square = (square_left, square_right, square_bottom, square_top)
        self.color_square = (square_center_x, square_right, square_bottom, square_top)

    def on_draw(self):
        with arcade.get_window().ctx.default_atlas.render_into(self.tex) as fbo:
            fbo.clear()

            # Outline
            arcade.draw_lrbt_rectangle_outline(*self.square, arcade.color.GRAY, 5)

            # Lights
            if self.rgbmusic.red:
                arcade.draw_lrbt_rectangle_filled(*self.red, arcade.color.RED)
            if self.rgbmusic.green:
                arcade.draw_lrbt_rectangle_filled(*self.green, arcade.color.GREEN)
            if self.rgbmusic.blue:
                arcade.draw_lrbt_rectangle_filled(*self.blue, arcade.color.BLUE)

            # Color
            if self.rgbmusic.color != Color(0, 0, 0):
                arcade.draw_lrbt_rectangle_filled(*self.color_square, self.rgbmusic.color)

        # BLOOM
        self.bloom_filter.use()
        self.bloom_filter.clear()
        self.sprite_list.draw()

        self.window.use()
        self.clear()
        self.bloom_filter.draw()
        # Draw the original on top of the bloom because it looks better
        self.sprite_list.draw()
        return super().on_draw()
