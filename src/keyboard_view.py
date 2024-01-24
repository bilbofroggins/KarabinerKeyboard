from raylib import *
from base_panel import BaseView
from config import Config
from key_mappings import *

class KeyboardView(BaseView):
    def __init__(self):
        super().__init__()
        # Define the Mac keyboard layout
        self.key_positions = [
            [(KEY_ESCAPE, 1.5), (KEY_F1, 1), (KEY_F2, 1), (KEY_F3, 1), (KEY_F4, 1),
             (KEY_F5, 1), (KEY_F6, 1), (KEY_F7, 1), (KEY_F8, 1), (KEY_F9, 1),
             (KEY_F10, 1), (KEY_F11, 1), (KEY_F12, 1), (None, 1)],
            [(KEY_GRAVE, 1), (KEY_ONE, 1), (KEY_TWO, 1), (KEY_THREE, 1), (KEY_FOUR, 1),
             (KEY_FIVE, 1), (KEY_SIX, 1), (KEY_SEVEN, 1), (KEY_EIGHT, 1), (KEY_NINE, 1),
             (KEY_ZERO, 1), (KEY_MINUS, 1), (KEY_EQUAL, 1), (KEY_BACKSPACE, 1.5)],
            [(KEY_TAB, 1.5), (KEY_Q, 1), (KEY_W, 1), (KEY_E, 1), (KEY_R, 1), (KEY_T, 1),
             (KEY_Y, 1), (KEY_U, 1), (KEY_I, 1), (KEY_O, 1), (KEY_P, 1),
             (KEY_LEFT_BRACKET, 1), (KEY_RIGHT_BRACKET, 1), (KEY_BACKSLASH, 1)],
            [(KEY_CAPS_LOCK, 1.75), (KEY_A, 1), (KEY_S, 1), (KEY_D, 1), (KEY_F, 1),
             (KEY_G, 1), (KEY_H, 1), (KEY_J, 1), (KEY_K, 1), (KEY_L, 1),
             (KEY_SEMICOLON, 1), (KEY_APOSTROPHE, 1), (KEY_ENTER, 1.75)],
            [(KEY_LEFT_SHIFT, 2.25), (KEY_Z, 1), (KEY_X, 1), (KEY_C, 1), (KEY_V, 1),
             (KEY_B, 1), (KEY_N, 1), (KEY_M, 1), (KEY_COMMA, 1), (KEY_PERIOD, 1),
             (KEY_SLASH, 1), (KEY_RIGHT_SHIFT, 2.25)],
            [(None, 1), (KEY_LEFT_CONTROL, 1), (KEY_LEFT_ALT, 1), (KEY_LEFT_SUPER, 1.25),
             (KEY_SPACE, 5), (KEY_RIGHT_SUPER, 1.25), (KEY_RIGHT_ALT, 1), (KEY_LEFT, 1),
             (KEY_DOWN, 1), (KEY_RIGHT, 1)]
        ]
        self.base_key_width = 50
        self.key_height = 40
        self.key_padding = 5
        self.key_color = LIGHTGRAY
        self.pressed_keys = set()

    def update(self):
        # Check for all key presses since the last frame
        pressed_key = GetKeyPressed()
        while pressed_key != 0:  # Loop until the queue is empty
            self.pressed_keys.add(pressed_key)
            pressed_key = GetKeyPressed()

        to_remove = []
        for key in self.pressed_keys:
            if IsKeyUp(key):
                to_remove.append(key)
        for key in to_remove:
            self.pressed_keys.remove(key)

    def draw_keyboard(self, start_x, start_y):
        y = start_y
        for keyboard_row in self.key_positions:
            x = start_x
            for key_id, width in keyboard_row:
                key_width = int(self.base_key_width * width + self.key_padding * (width - 1))
                key_str = rl_to_kb_key_map[key_id] if key_id is not None else ''
                key_text = key_str.encode('utf-8')

                if key_text in (b'left_arrow', b'down_arrow', b'right_arrow'):
                    self.key_height //= 2
                    y += self.key_height

                if key_id in self.pressed_keys:
                    DrawRectangle(x, y, key_width, self.key_height, YELLOW)
                else:
                    DrawRectangle(x, y, key_width, self.key_height, self.key_color)
                text_x = int(x + key_width / 2 - MeasureText(key_text, Config.font_size) / 2)
                text_y = int(y + self.key_height / 2 - 10)
                DrawText(key_text, text_x, text_y, Config.font_size, BLACK)

                if key_text in (b'left_arrow', b'down_arrow', b'right_arrow'):
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
        if KEY_UP in self.pressed_keys:
            DrawRectangle(up_key_x, up_key_y, up_key_width, self.key_height // 2, YELLOW)
        else:
            DrawRectangle(up_key_x, up_key_y, up_key_width, self.key_height // 2, self.key_color)
        up_text_x = int(up_key_x + up_key_width / 2 - MeasureText(b'up_arrow', Config.font_size) / 2)
        up_text_y = int(up_key_y + self.key_height / 4 - 10)
        DrawText(b'up_arrow', up_text_x, up_text_y, Config.font_size, BLACK)

