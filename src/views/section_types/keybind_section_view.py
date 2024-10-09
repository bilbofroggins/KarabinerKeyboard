import pyray as ray

from src.components.drawing_helper import DrawingHelper
from src.config import config
from src.logic.yaml_config import YAML_Config
from src.panels.base_panel import BaseView


class KeybindSectionView(BaseView):
    def __init__(self, current_key, reset_current_key_callback):
        super().__init__()

    def draw_section(self, row, col):
        ray.draw_rectangle(100, 100, 200, 200, ray.BLUE)

    def reset_values(self):
        pass

    def set_values(self, current_key):
        pass