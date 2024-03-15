import pyray as ray

from src.config import config
from src.logic.key_mappings import *
from src.logic.keyboard_state_controller import *
from src.panels.global_vars import special_font


class KeyboardView(BaseView):
    def __init__(self, keyboard_state_controller):
        super().__init__()
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
        self.keyboard_state_controller = keyboard_state_controller
        self.keyboard_state_controller.register(self)
        self.keyboard_state = STATE_EMPTY
        self.pressed_key_color = {
            STATE_EMPTY: ray.ORANGE,
            STATE_IS_PRESSING: ray.ORANGE,
            STATE_LOCKED: ray.YELLOW,
            STATE_OVERRIDING: self.key_color,
            STATE_BUNDLE_SEARCH: ray.YELLOW,
        }

    def change_keyboard_state(self, state):
        self.keyboard_state = state

    def draw_keyboard(self, start_x, start_y):
        y = start_y
        for keyboard_row in self.key_positions:
            x = start_x
            for key_id, width in keyboard_row:
                key_width = int(self.base_key_width * width + self.key_padding * (width - 1))
                key_text = rl_to_display_key_map[key_id] if key_id is not None else ""

                if key_id in (ray.KEY_LEFT, ray.KEY_DOWN, ray.KEY_RIGHT):
                    self.key_height //= 2
                    y += self.key_height

                if key_id in self.keyboard_state_controller.locked_keys and self.keyboard_state != STATE_OVERRIDING:
                    ray.draw_rectangle(x, y, key_width, self.key_height, self.pressed_key_color[self.keyboard_state])
                else:
                    ray.draw_rectangle(x, y, key_width, self.key_height, self.key_color)

                if key_id in special_chars:
                    font_width = ray.measure_text_ex(special_font[0], key_text, config.font_size, 0).x
                else:
                    font_width = ray.measure_text(key_text, config.font_size)

                text_x = int(x + key_width / 2 - font_width / 2)
                text_y = int(y + self.key_height / 2 - 10)

                if key_id in special_chars:
                    kb_begin_text = rl_to_kb_key_map[key_id][:5]
                    if kb_begin_text == 'left_' and key_id != ray.KEY_LEFT:
                        char_color = config.left_mod_kb_color
                    elif kb_begin_text == 'right' and key_id != ray.KEY_RIGHT:
                        char_color = config.right_mod_kb_color
                    else:
                        char_color = config.default_text_color
                    ray.draw_text_ex(special_font[0], key_text, (text_x, text_y), config.font_size, 0, char_color)
                else:
                    ray.draw_text(key_text, text_x, text_y, config.font_size, config.default_text_color)

                if key_id in (ray.KEY_LEFT, ray.KEY_DOWN, ray.KEY_RIGHT):
                    y -= self.key_height
                    self.key_height *= 2

                x += key_width + self.key_padding
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

        if ray.KEY_UP in self.keyboard_state_controller.locked_keys and self.keyboard_state != STATE_OVERRIDING:
            ray.draw_rectangle(up_key_x, up_key_y, up_key_width, self.key_height // 2, self.pressed_key_color[self.keyboard_state])
        else:
            ray.draw_rectangle(up_key_x, up_key_y, up_key_width, self.key_height // 2, self.key_color)

        key_text = rl_to_display_key_map[ray.KEY_UP]
        font_width = ray.measure_text_ex(special_font[0], key_text, config.font_size, 0).x

        up_text_x = int(up_key_x + up_key_width / 2 - font_width / 2)
        up_text_y = int(up_key_y + self.key_height / 4 - 10)
        ray.draw_text_ex(special_font[0], key_text, (up_text_x, up_text_y), config.font_size, 0, config.default_text_color)
