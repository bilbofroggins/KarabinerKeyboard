import pyray as ray

from src.components.drawing_helper import DrawingHelper
from src.config import config
from src.panels.base_panel import BaseView
from src.panels.click_handler import ClickHandler


class ListPanel(BaseView):
    def __init__(self):
        super().__init__()
        self.options = ["Keyboard", "Overrides", "Help"]
        self.selected_option = "Keyboard"
        self.panel_width = self.calculate_max_width()

    def calculate_max_width(self):
        max_width = 0
        for option in self.options:
            text_width = ray.measure_text(option, config.font_size)
            if text_width > max_width:
                max_width = text_width
        return max_width + config.generic_padding

    def draw(self):
        ray.draw_rectangle(0, 0, self.panel_width, config.window_height, config.lime_color)

        for i, option in enumerate(self.options):
            def click_callback(opt):
                self.base_message("close_ask_window")
                self.selected_option = opt
            def draw_callback(row, col):
                ray.draw_text(option, col, row, config.font_size, config.default_text_color)
            def hover_callback(row, col):
                ray.draw_text(option, col, row, config.font_size, DrawingHelper.brighten(config.default_text_color))


            if option == self.selected_option:
                ray.draw_text(option, config.list_padding, config.list_padding + i * config.font_size, config.font_size, config.active_tab_color)
            else:
                DrawingHelper.generic_clickable(
                    config.list_padding + i * config.font_size, config.list_padding,
                    self.panel_width, config.font_size,
                    draw_callback, hover_callback, click_callback, [option]
                )
