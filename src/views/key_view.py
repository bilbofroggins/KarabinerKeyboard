import math

import pyray as ray

from src.components.drawing_helper import DrawingHelper
from src.config import config
from src.logic.event_bus import EventBus
from src.logic.global_state import GlobalState
from src.logic.key_mappings import *
from src.logic.layer_colors import layer_color
from src.logic.yaml_config import YAML_Config
from src.panels.base_panel import BaseView
import src.panels.global_vars as g


class KeyView(BaseView):
    def __init__(self, layer, current_key, key_id, row, col, width, ):
        super().__init__()
        self.base_key_width = 50
        self.corner_mod_width = 10
        self.corner_mod_height = 10
        self.key_height = 40
        self.key_padding = 5
        self.key_color = ray.LIGHTGRAY

        self.layer = layer
        self.current_key = current_key
        self.key_id = key_id
        self.row = row
        self.col = col
        self.width = int(self.base_key_width * width + self.key_padding * (width - 1))
        self.height = self.key_height
        if self.key_id is not None:
            self.kb_key = rl_to_kb_key_map[self.key_id]

        if self.key_id in (ray.KEY_LEFT, ray.KEY_DOWN, ray.KEY_RIGHT):
            self.key_height //= 2
            self.row += self.key_height

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

    def adjust_key_color(self, color):
        real_color = color
        if self.current_key[0] is not None:
            current_key_layer = int(self.current_key[0].split(":")[0])
            current_key_char = self.current_key[0].split(":")[1]
            if self.layer[0] == current_key_layer and self.kb_key == current_key_char:
                real_color = DrawingHelper.brighten(color, int(self.get_brightness_value()))
        return real_color

    def draw_key(self):
        if self.key_id is None:
            # Fn key & Power key
            self.col += self.base_key_width + self.key_padding
            return self.col

        override = YAML_Config().key_overriddes(self.layer[0], self.kb_key)
        key_type = YAML_Config().key_type(self.layer[0], self.kb_key)

        key_text = rl_to_display_key_map[self.key_id]

        def click_callback():
            GlobalState().input_focus = 'edit_view'
            self.current_key[0] = str(self.layer[0]) + ":" + self.kb_key
            EventBus().notify('key_click')

        DrawingHelper.generic_clickable(self.row, self.col, self.width, self.key_height, lambda x,y: None, lambda x,y: None, click_callback)
        ray.draw_rectangle(self.col, self.row, self.width, self.key_height,
                           self.adjust_key_color(self.key_color))

        if key_type == 'single':
            ray.draw_rectangle(self.col, self.row, self.width, self.key_height, self.adjust_key_color(ray.DARKBROWN))
            self.draw_corner_mods(*self.get_mods(override[1]))

            chars = override[1].split(' + ')
            if len(chars) > 1 and ('left_shift' in chars or 'right_shift' in chars):
                key_text = get_shifted_key(chars[-1])
            else:
                key_text = rl_to_display_key_map[kb_to_rl_key_map[chars[-1]]]
        elif key_type == 'multi':
            ray.draw_rectangle(self.col, self.row, self.width, self.key_height, self.adjust_key_color(ray.MAROON))
            key_text = '...'
        elif key_type == 'osm':
            key_text = 'OSM'
            ray.draw_rectangle(self.col, self.row, self.width, self.key_height, self.adjust_key_color(ray.SKYBLUE))
            self.draw_corner_mods(*self.get_mods(override[1]))
        elif key_type == 'shell':
            ray.draw_rectangle(self.col, self.row, self.width, self.key_height, self.adjust_key_color(ray.MAGENTA))
            key_text = '>_'
        elif key_type.split('|')[0] == 'layer':
            key_text = key_type.split('|')[1]
            color = layer_color(override[1])
            ray.draw_rectangle(self.col, self.row, self.width, self.key_height, self.adjust_key_color(color))

        sim_keys = []
        for key in YAML_Config().all_simultaneous_overrides(self.layer[0]).keys():
            sim_keys += key.split(',')
        if self.kb_key in sim_keys:
            ray.draw_rectangle_lines(self.col, self.row, self.width, self.key_height, ray.RED)


        if self.key_id in special_chars and key_type in ('', 'single'):
            font_width = ray.measure_text_ex(g.special_font[0], key_text,
                                             config.font_size, 0).x
        else:
            font_width = ray.measure_text(key_text, config.font_size)

        text_col = int(self.col + self.width / 2 - font_width / 2)
        text_row = int(self.row + self.key_height / 2 - 10)

        if self.key_id in special_chars and key_type in ('', 'single'):
            kb_begin_text = rl_to_kb_key_map[self.key_id][:5]
            if kb_begin_text == 'left_' and self.key_id != ray.KEY_LEFT:
                char_color = config.left_mod_kb_color
            elif kb_begin_text == 'right' and self.key_id != ray.KEY_RIGHT:
                char_color = config.right_mod_kb_color
            else:
                char_color = config.default_text_color
            ray.draw_text_ex(g.special_font[0], key_text, (text_col, text_row),
                             config.font_size, 0, char_color)
        else:
            ray.draw_text(key_text, text_col, text_row, config.font_size,
                          config.default_text_color)


        self.col += self.width + self.key_padding
        return self.col