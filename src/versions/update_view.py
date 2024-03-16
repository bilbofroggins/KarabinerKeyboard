import sys
import threading

import pyray as ray

from src.components.drawing_helper import DrawingHelper
from src.config import config
from src.versions.updates import check_up_to_date, background_updates


class UpdateView():
    def __init__(self):
        super().__init__()
        self.text1 = "New version available"
        self.text2 = "Download & Install"
        width = ray.measure_text(self.text1, config.font_size)
        self.is_updated = True
        self.text_width = max(width, ray.measure_text(self.text2, config.font_size))
        self.is_quitting = False
        self.quitting_done_flag = [False]
        threading.Thread(target=self.check_updates, daemon=True).start()

    def check_updates(self):
        self.is_updated, self.latest_version = check_up_to_date()

    def update_app(self, new_version):
        threading.Thread(target=background_updates, args=(new_version, self.quitting_done_flag,)).start()
        self.is_quitting = True

    def draw_updates(self, start_row, start_col, max_row, max_col):
        if self.quitting_done_flag[0] == True:
            sys.exit(0)
        elif self.is_quitting:
            ray.draw_rectangle(start_col, start_row, max_col, max_row, config.background_color)
            ray.draw_text("Restarting...",
                     start_col, start_row, config.font_size * 4, config.default_text_color)
            return

        max_row -= config.generic_padding
        max_col -= config.generic_padding

        if not self.is_updated:
            box_start_row = max_row - config.font_size*2 - config.generic_padding*3
            box_start_col = max_col - self.text_width - config.generic_padding*2

            ray.draw_rectangle(box_start_col, box_start_row, max_col - box_start_col, max_row - box_start_row, ray.BLUE)
            ray.draw_text(self.text1, box_start_col + config.generic_padding, box_start_row + config.generic_padding, config.font_size, config.default_text_color)
            DrawingHelper.clickable_link(self.text2, box_start_row + config.generic_padding*2 + config.font_size, box_start_col + config.generic_padding, config.font_size, config.default_text_color, self.update_app, [self.latest_version])
