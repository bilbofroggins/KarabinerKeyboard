from raylib import *

from src.config import config
from src.panels.base_panel import BaseView
from src.panels.click_handler import ClickHandler


class ListPanel(BaseView):
    def __init__(self):
        super().__init__()
        self.options = [b"Keyboard", b"Overrides", b"Help"]
        self.selected_option = b"Keyboard"
        self.panel_width = self.calculate_max_width()

    def calculate_max_width(self):
        max_width = 0
        for option in self.options:
            text_width = MeasureText(option, config.font_size)
            if text_width > max_width:
                max_width = text_width
        return max_width + config.generic_padding  # Add some padding

    def update(self):
        def callback(opt):
            self.base_message("close_ask_window")
            self.selected_option = opt

        mouse_position = GetMousePosition()
        # Check if a list item is clicked
        for i, option in enumerate(self.options):
            if mouse_position.x <= self.panel_width:
                if i * config.font_size + config.list_padding <= mouse_position.y <= (i+1) * config.font_size + config.list_padding:
                    ClickHandler.append(callback, [option])

    def draw(self):
        DrawRectangle(0, 0, self.panel_width, config.window_height, GREEN)

        for i, option in enumerate(self.options):
            if option == self.selected_option:
                DrawText(option, config.list_padding, config.list_padding + i * config.font_size, config.font_size, RED)
            else:
                DrawText(option, config.list_padding, config.list_padding + i * config.font_size, config.font_size, config.default_text_color)
