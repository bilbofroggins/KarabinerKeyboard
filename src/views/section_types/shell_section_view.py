import pyray as ray

from src.components.drawing_helper import DrawingHelper
from src.config import config
from src.logic.yaml_config import YAML_Config
from src.panels.base_panel import BaseView


class ShellSectionView(BaseView):
    def __init__(self, current_key, reset_current_key_callback):
        super().__init__()

    def submit(self):
        pass

    def draw_section(self, row, col):
        ray.draw_text("Implementation coming soon", col, row, config.font_size, ray.DARKBLUE)

    def reset_values(self):
        pass

    def set_values(self, current_key):
        pass