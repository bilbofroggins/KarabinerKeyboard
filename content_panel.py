from raylib import *
from base_panel import BaseView
from config import Config
from key_mappings import *
from keyboard_view import KeyboardView
from overrides_view import OverridesView


class ContentPanel(BaseView):
    def __init__(self, list_panel):
        super().__init__()
        self.list_panel = list_panel
        self.background_color = GRAY
        self.keyboard_view = KeyboardView()
        self.overrides_view = OverridesView()

    def draw(self):
        left_panel_width = self.list_panel.panel_width

        # Draw the background for the content panel
        DrawRectangle(left_panel_width, 0, Config.window_width - left_panel_width, Config.window_height,
                      self.background_color)

        if self.list_panel.selected_option:
            if self.list_panel.selected_option.decode('utf-8') == "Keyboard":
                # Draw keyboard with some padding
                self.keyboard_view.draw_keyboard(left_panel_width + 20, 20)

                # Draw two lines of text at the bottom
                bottom_text_y = 360  # Adjusted Y position of the bottom text section
                DrawText(b"Line 1 of bottom text", left_panel_width + 20, bottom_text_y, 20,
                         BLACK)
                DrawText(b"Line 2 of bottom text", left_panel_width + 20, bottom_text_y + 30,
                         20, BLACK)
            elif self.list_panel.selected_option.decode('utf-8') == "Overrides":
                self.overrides_view.draw_overrides(left_panel_width + 20, 20)