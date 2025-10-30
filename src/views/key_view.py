from collections import defaultdict
import random
from functools import lru_cache

import pyray as ray

from src.components.drawing_helper import DrawingHelper
from src.config import config
from src.logic.event_bus import EventBus
from src.logic.global_state import GlobalState
from src.logic.key_mappings import *
from src.logic.layer_colors import layer_color
from src.logic.yaml_config import YAML_Config
import src.panels.global_vars as g


class KeyView():
    _instances = {}

    def __new__(cls, layer, key_index, key_id, current_key, row, col, width_modifier, height=40):
        key = (layer[0], key_index)
        if key in cls._instances:
            # Return existing instance from cache
            return cls._instances[key]
        else:
            # Create a new instance and add it to the cache
            instance = super(KeyView, cls).__new__(cls)
            cls._instances[key] = instance
            return instance

    def __init__(self, layer, key_index, key_id, current_key, row, col, width_modifier, height=40):
        super().__init__()
        if not hasattr(self, '_initialized'):
            self.base_key_width = 50
            self.corner_mod_width = 10
            self.corner_mod_height = 10
            self.key_height = height
            self.key_padding = 5
            self.key_color = ray.LIGHTGRAY
            self.is_hover = False
            self.sim_keys = None

            self.layer = layer
            self.key_id = key_id
            self.current_key = current_key
            self.width = int(self.base_key_width * width_modifier + self.key_padding * (
                    width_modifier - 1))
            self.height = self.key_height
            if self.key_id is not None:
                self.kb_key = rl_to_kb_key_map[self.key_id]

            self.row = row
            self.col = col

            if self.key_id in (ray.KEY_LEFT, ray.KEY_DOWN, ray.KEY_RIGHT):
                self.key_height //= 2
                self.row += self.key_height

            self._initialized = True

    def get_mods(self, override_string):
        shift, ctrl, alt, cmd = 0, 0, 0, 0
        override_chars = override_string.split(' + ')
        for char in override_chars:
            if ('left_shift' in char or 'right_shift' in char) and override_chars[-1] not in shift_mapping:
                shift = 1
            if 'left_control' in char or 'right_control' in char:
                ctrl = 1
            if 'left_alt' in char or 'right_alt' in char:
                alt = 1
            if 'left_command' in char or 'right_command' in char:
                cmd = 1

        return [shift, ctrl, alt, cmd]

    def draw_corner_mods(self, shift, ctrl, alt, cmd):
        if shift:
            ray.draw_rectangle(self.col, self.row, self.corner_mod_width, self.corner_mod_height, ray.BLUE)
            ray.draw_text_ex(g.special_font[0], '⇧', (self.col, self.row),
                             config.corner_font_size, 0, ray.BLACK)
        if ctrl:
            ray.draw_rectangle(self.col, self.row + self.key_height - self.corner_mod_height, self.corner_mod_width, self.corner_mod_height, ray.YELLOW)
            ray.draw_text_ex(g.special_font[0], '⌃', (self.col, self.row + self.key_height - self.corner_mod_height),
                             config.corner_font_size, 0, ray.BLACK)
        if alt:
            ray.draw_rectangle(self.col + self.width - self.corner_mod_width, self.row + self.key_height - self.corner_mod_height, self.corner_mod_width, self.corner_mod_height, ray.GREEN)
            ray.draw_text_ex(g.special_font[0], '⌥', (self.col + self.width - self.corner_mod_width, self.row + self.key_height - self.corner_mod_height),
                             config.corner_font_size, 0, ray.BLACK)
        if cmd:
            ray.draw_rectangle(self.col + self.width - self.corner_mod_width, self.row, self.corner_mod_width, self.corner_mod_height, ray.PURPLE)
            ray.draw_text_ex(g.special_font[0], '⌘', (self.col + self.width - self.corner_mod_width, self.row),
                             config.corner_font_size, 0, ray.BLACK)

    def get_brightness_value(self):
        frame = GlobalState().frame
        speed = 60
        val = 100 * (1 - abs((frame % speed) - (speed / 2)) / (speed / 2)) ** 2
        return val

    def adjust_key_color(self, color, darken=False):
        real_color = color
        if self.current_key[0] is not None:
            current_key_layer = int(self.current_key[0].split(":")[0])
            current_key_chars = self.current_key[0].split(":")[1].split(',')
            if self.layer[0] == current_key_layer and self.kb_key in current_key_chars:
                if darken:
                    real_color = DrawingHelper.darken(color, int(self.get_brightness_value()))
                else:
                    real_color = DrawingHelper.brighten(color, int(self.get_brightness_value()))
        if darken:
            return DrawingHelper.darken(tuple(real_color), 50)
        return real_color

    @lru_cache
    def simultaneous_color(self, key_string):
        random.seed(key_string)

        red = random.randint(100, 255)
        green = random.randint(100, 255)
        blue = random.randint(100, 255)

        return (red, green, blue, 255)

    def update_sim_outline_data(self):
        self.sim_keys = defaultdict(list)
        for key in YAML_Config().all_simultaneous_overrides(self.layer[0]).keys():
            keys = key.split(',')
            for k in keys:
                self.sim_keys[k].append(key)

    def draw_sim_outlines(self):
        if self.kb_key in self.sim_keys:
            start_row, start_col, start_width, start_height = self.row, self.col, self.width, self.height
            for i in range(len(self.sim_keys[self.kb_key])):
                rec = ray.Rectangle(start_col, start_row, start_width, start_height)
                ray.draw_rectangle_lines_ex(rec, 2, self.simultaneous_color(self.sim_keys[self.kb_key][i]))
                start_row -= 2
                start_col -= 2
                start_width += 4
                start_height += 4

    def draw_key(self):
        if self.key_id is None:
            # Fn key & Power key
            return self.col + self.base_key_width + self.key_padding

        override = YAML_Config().key_overriddes(self.layer[0], self.kb_key)
        key_type = YAML_Config().key_type(self.layer[0], self.kb_key)

        key_text = rl_to_display_key_map[self.key_id]

        self.update_sim_outline_data()

        def draw_callback(row, col):
            ray.draw_rectangle(col, row, self.width, self.key_height,
                               self.adjust_key_color(self.key_color, self.kb_key in GlobalState().highlighted_chord_to_show()))
            self.is_hover = False
        def hover_callback(row, col):
            ray.draw_rectangle(col, row, self.width, self.key_height,
                               self.adjust_key_color(self.key_color, True))
            if self.is_hover == False:
                GlobalState().highlighted_keys = []
                GlobalState().highlighted_keys.append([self.kb_key])
                for chord in self.sim_keys[self.kb_key]:
                    GlobalState().highlighted_keys.append(chord.split(','))

                GlobalState().highlighted_frame_start = GlobalState().frame
            self.is_hover = True

        def click_callback():
            GlobalState().input_focus = 'edit_view'
            # Use the currently highlighted chord instead of just the single key
            highlighted_chord = GlobalState().highlighted_chord_to_show()
            if highlighted_chord:
                chord_key = ','.join(highlighted_chord)
            else:
                chord_key = self.kb_key
            self.current_key[0] = str(self.layer[0]) + ":" + chord_key
            EventBus().notify('key_click')

        DrawingHelper.generic_clickable(self.row, self.col, self.width, self.key_height, draw_callback, hover_callback, click_callback)

        if key_type == 'single':
            ray.draw_rectangle(self.col, self.row, self.width, self.key_height, self.adjust_key_color(ray.GOLD, self.kb_key in GlobalState().highlighted_chord_to_show()))
            self.draw_corner_mods(*self.get_mods(override[1]))

            chars = override[1].split(' + ')
            if len(chars) > 1 and ('left_shift' in chars or 'right_shift' in chars):
                if chars[-1] not in modification_keys:
                    key_text = get_shifted_key(rl_to_display_key_map[kb_to_rl_key_map[chars[-1]]])
                else:
                    key_text = ""
            else:
                chars_minus_mods = [char for char in chars if char not in modification_keys]
                if len(chars_minus_mods) > 0:
                    key_text = rl_to_display_key_map[kb_to_rl_key_map[chars_minus_mods[-1]]]
                else:
                    key_text = ""
        elif key_type == 'multi':
            ray.draw_rectangle(self.col, self.row, self.width, self.key_height, self.adjust_key_color(ray.BROWN, self.kb_key in GlobalState().highlighted_chord_to_show()))
            key_text = '...'
        elif key_type == 'osm':
            key_text = 'OSM'
            ray.draw_rectangle(self.col, self.row, self.width, self.key_height, self.adjust_key_color(ray.SKYBLUE, self.kb_key in GlobalState().highlighted_chord_to_show()))
            self.draw_corner_mods(*self.get_mods(override[1]))
        elif key_type == 'shell':
            ray.draw_rectangle(self.col, self.row, self.width, self.key_height, self.adjust_key_color(ray.MAGENTA, self.kb_key in GlobalState().highlighted_chord_to_show()))
            key_text = '>_'
        elif key_type.split('|')[0] == 'layer':
            key_text = key_type.split('|')[1]

            layernum = override[1]
            if isinstance(override[1], str):
                override_string = override[1].split('|')
                if len(override_string) > 1:
                    layernum = override_string[0]
                    key = override_string[1]
                    key_text = key_type.split('|')[1] + "(" + rl_to_display_key_map[kb_to_rl_key_map[key]] + ")"
            color = layer_color(layernum)

            ray.draw_rectangle(self.col, self.row, self.width, self.key_height, self.adjust_key_color(color, self.kb_key in GlobalState().highlighted_chord_to_show()))

        self.draw_sim_outlines()

        font_width = DrawingHelper.measure_unicode_plus_text(key_text, config.font_size)

        text_col = int(self.col + self.width / 2 - font_width / 2)
        text_row = int(self.row + self.key_height / 2 - 10)
        DrawingHelper.draw_unicode_plus_text(key_text, text_row, text_col, config.font_size, config.default_text_color)

        return self.col + self.width + self.key_padding
