import pyray as ray

from src.components.drawing_helper import DrawingHelper
from src.config import config
from src.logic.yaml_config import YAML_Config
from src.panels.base_panel import BaseView


class ShellSectionView(BaseView):
    def __init__(self, current_key, reset_current_key_callback):
        super().__init__()

    def draw_section(self, row, col):
        ray.draw_rectangle(col, row, 200, int(config.small_font_size), ray.WHITE)
        if (self.input_active):
            ray.draw_rectangle_lines(textbox_start_col, row, textbox_width, int(config.small_font_size*1.4), ray.RED)


    def reset_values(self):
        pass

    def set_values(self, current_key):
        pass