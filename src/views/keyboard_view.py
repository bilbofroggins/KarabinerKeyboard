import pyray as ray

from src.config import config
from src.devices.keyboard_controller import KeyboardController
from src.logic.event_bus import EventBus
from src.logic.global_state import GlobalState
from src.logic.key_mappings import *
import src.panels.global_vars as g
from src.panels.base_panel import BaseView
from src.views.key_view import KeyView


class KeyboardView(BaseView):
    def __init__(self, layer, current_key):
        super().__init__()
        self.layer = layer
        self.current_key = current_key
        # Define the Mac keyboard layout
        self.key_positions = [
            [(ray.KEY_ESCAPE, 1.5), (ray.KEY_F1, 1), (ray.KEY_F2, 1), (ray.KEY_F3, 1), (ray.KEY_F4, 1),
             (ray.KEY_F5, 1), (ray.KEY_F6, 1), (ray.KEY_F7, 1), (ray.KEY_F8, 1), (ray.KEY_F9, 1),
             (ray.KEY_F10, 1), (ray.KEY_F11, 1), (ray.KEY_F12, 1), (None, 1)],
            [(ray.KEY_GRAVE, 1), (ray.KEY_ONE, 1), (ray.KEY_TWO, 1), (ray.KEY_THREE, 1), (ray.KEY_FOUR, 1),
             (ray.KEY_FIVE, 1), (ray.KEY_SIX, 1), (ray.KEY_SEVEN, 1), (ray.KEY_EIGHT, 1), (ray.KEY_NINE, 1),
             (ray.KEY_ZERO, 1), (ray.KEY_MINUS, 1), (ray.KEY_EQUAL, 1), (ray.KEY_BACKSPACE, 1.5)],
            [(ray.KEY_TAB, 1.5), (ray.KEY_Q, 1), (ray.KEY_W, 1), (ray.KEY_E, 1), (ray.KEY_R, 1), (ray.KEY_T, 1),
             (ray.KEY_Y, 1), (ray.KEY_U, 1), (ray.KEY_I, 1), (ray.KEY_O, 1), (ray.KEY_P, 1),
             (ray.KEY_LEFT_BRACKET, 1), (ray.KEY_RIGHT_BRACKET, 1), (ray.KEY_BACKSLASH, 1)],
            [(ray.KEY_CAPS_LOCK, 1.75), (ray.KEY_A, 1), (ray.KEY_S, 1), (ray.KEY_D, 1), (ray.KEY_F, 1),
             (ray.KEY_G, 1), (ray.KEY_H, 1), (ray.KEY_J, 1), (ray.KEY_K, 1), (ray.KEY_L, 1),
             (ray.KEY_SEMICOLON, 1), (ray.KEY_APOSTROPHE, 1), (ray.KEY_ENTER, 1.75)],
            [(ray.KEY_LEFT_SHIFT, 2.25), (ray.KEY_Z, 1), (ray.KEY_X, 1), (ray.KEY_C, 1), (ray.KEY_V, 1),
             (ray.KEY_B, 1), (ray.KEY_N, 1), (ray.KEY_M, 1), (ray.KEY_COMMA, 1), (ray.KEY_PERIOD, 1),
             (ray.KEY_SLASH, 1), (ray.KEY_RIGHT_SHIFT, 2.25)],
            [(None, 1), (ray.KEY_LEFT_CONTROL, 1), (ray.KEY_LEFT_ALT, 1), (ray.KEY_LEFT_SUPER, 1.25),
             (ray.KEY_SPACE, 5), (ray.KEY_RIGHT_SUPER, 1.25), (ray.KEY_RIGHT_ALT, 1), (ray.KEY_LEFT, 1),
             (ray.KEY_DOWN, 1), (ray.KEY_RIGHT, 1)]
        ]
        self.base_key_width = 50
        self.key_height = 40
        self.key_padding = 5
        self.key_color = ray.LIGHTGRAY
        self.search_keys = set()

    def draw_keyboard(self, start_x, start_y):
        if GlobalState().input_focus == 'keyboard' and len(KeyboardController.added_keys()):
            GlobalState().input_focus = 'edit_view'
            self.current_key[0] = str(self.layer[0]) + ':' + rl_to_kb_key_map[next(iter(KeyboardController.pressed_keys))]
            EventBus().notify('key_click')

        y = start_y
        for keyboard_row in self.key_positions:
            x = start_x
            for key_id, width in keyboard_row:
                x = KeyView(self.layer, self.current_key, key_id, y, x, width).draw_key()
            y += self.key_height + self.key_padding

        # Calculate the total width of keys before the 'left' key in the last row
        total_width_before_left = sum(
            self.base_key_width * size + self.key_padding * (size - 1) for key, size in
            self.key_positions[-1][:8]) + self.key_padding * 8 - (self.key_padding//4)

        # Calculate the total height of rows above the last row
        total_height_above_last_row = sum(
            self.key_height + self.key_padding for _ in range(len(self.key_positions[:-1])))

        # Position for the 'up' arrow key
        up_key_x = int(start_x + total_width_before_left)
        up_key_y = int(start_y + total_height_above_last_row)

        # Draw the 'up' arrow key
        up_key_width = int(self.base_key_width)

        ray.draw_rectangle(up_key_x, up_key_y, up_key_width, self.key_height // 2, self.key_color)

        key_text = rl_to_display_key_map[ray.KEY_UP]
        font_width = ray.measure_text_ex(g.special_font[0], key_text, config.font_size, 0).x

        up_text_x = int(up_key_x + up_key_width / 2 - font_width / 2)
        up_text_y = int(up_key_y + self.key_height / 4 - 10)
        ray.draw_text_ex(g.special_font[0], key_text, (up_text_x, up_text_y), config.font_size, 0, config.default_text_color)

        return y