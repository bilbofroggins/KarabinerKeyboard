from raylib import *
from base_panel import BaseView
from config import Config
from drawing_helper import DrawingHelper
from karabiner_config import KarabinerConfig

class OverridesView(BaseView):
    def __init__(self):
        super().__init__()
        self.karabiner_config = KarabinerConfig()

    def update(self):
        pass

    def draw_overrides(self, start_x, start_y):
        max_from_end = 0
        max_to_end = 0

        row_pixels = start_y
        for override_pair in self.karabiner_config.modification_pairs:
            from_text = str(override_pair.modification_from)

            def clicked():
                override_pair.modification_from.key = 'comma'  # TODO dont hardcode
                KarabinerConfig().write_overrides()

            width = DrawingHelper.clickable_link(from_text, start_x, row_pixels, Config.font_size, BLACK, clicked)

            max_from_end = max(start_x + width + Config.generic_padding, max_from_end)
            row_pixels += Config.font_size

        row_pixels = start_y
        for override_pair in self.karabiner_config.modification_pairs:
            to_text = str(override_pair.modification_to)

            def clicked():
                override_pair.modification_from.key = 'comma'  # TODO dont hardcode
                KarabinerConfig().write_overrides()

            width = DrawingHelper.clickable_link(to_text, max_from_end, row_pixels, Config.font_size, BLACK, clicked)

            max_to_end = max(max_from_end + width + Config.generic_padding, max_to_end)
            row_pixels += Config.font_size

        row_pixels = start_y
        for _ in self.karabiner_config.modification_pairs:
            def clicked():
                override_pair.modification_from.key = 'comma'  # TODO dont hardcode
                KarabinerConfig().write_overrides()

            DrawingHelper.clickable_link("x", max_to_end, row_pixels, Config.font_size, RED, clicked)
            row_pixels += Config.font_size
