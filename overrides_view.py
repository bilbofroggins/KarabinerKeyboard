from raylib import *
from base_panel import BaseView
from config import Config
from karabiner_config import KarabinerConfig

class OverridesView(BaseView):
    def __init__(self):
        super().__init__()
        self.karabiner_config = KarabinerConfig()
        self.is_hovering_mouse = False

    def update(self):
        pass

    def is_mouse_over_text(self, mouse_x, mouse_y, x, y, width, height):
        return x <= mouse_x <= x + width and y <= mouse_y <= y + height

    def draw_overrides(self, start_x, start_y):
        mouse_position = GetMousePosition()
        max_from_end = 0
        max_to_end = 0

        row_pixels = start_y
        for override_pair in self.karabiner_config.modification_pairs:
            from_text = str(override_pair.modification_from).encode('utf-8')
            DrawText(from_text, start_x, row_pixels, Config.font_size, BLACK)
            from_width = MeasureText(from_text, Config.font_size)

            # Make it clickable
            if self.is_mouse_over_text(mouse_position.x, mouse_position.y, start_x, row_pixels, from_width, Config.font_size):
                self.is_hovering_mouse = True
                DrawLine(start_x, row_pixels + Config.font_size, start_x + from_width,
                         row_pixels + Config.font_size, BLACK)
                if IsMouseButtonPressed(MOUSE_BUTTON_LEFT):
                    override_pair.modification_from.key = 'comma' # TODO dont hardcode
                    KarabinerConfig().write_overrides()

            max_from_end = max(start_x + from_width + Config.generic_padding, max_from_end)
            row_pixels += Config.font_size

        row_pixels = start_y
        for override_pair in self.karabiner_config.modification_pairs:
            to_text = str(override_pair.modification_to).encode('utf-8')
            DrawText(to_text, max_from_end, row_pixels, Config.font_size, BLACK)
            to_width = MeasureText(to_text, Config.font_size)

            # Make it clickable
            if self.is_mouse_over_text(mouse_position.x, mouse_position.y, max_from_end, row_pixels, to_width, Config.font_size):
                self.is_hovering_mouse = True
                DrawLine(max_from_end, row_pixels + Config.font_size, max_from_end + to_width,
                         row_pixels + Config.font_size, BLACK)
                if IsMouseButtonPressed(MOUSE_BUTTON_LEFT):
                    print("to clicked!")

            max_to_end = max(max_from_end + to_width + Config.generic_padding, max_to_end)
            row_pixels += Config.font_size

        row_pixels = start_y
        for _ in self.karabiner_config.modification_pairs:
            DrawText("x".encode('utf-8'), max_to_end, row_pixels, Config.font_size, RED)
            row_pixels += Config.font_size

            # Make it clickable
            if self.is_mouse_over_text(mouse_position.x, mouse_position.y,
                                       max_to_end, row_pixels,
                                       Config.font_size, Config.font_size):
                self.is_hovering_mouse = True
                if IsMouseButtonPressed(MOUSE_BUTTON_LEFT):
                    print("X clicked!")

        if self.is_hovering_mouse:
            SetMouseCursor(MOUSE_CURSOR_POINTING_HAND)
            self.is_hovering_mouse = False
        else:
            SetMouseCursor(MOUSE_CURSOR_DEFAULT)