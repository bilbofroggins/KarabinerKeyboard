from raylib import *

from src.components.modification_change_view import ModificationChangeView
from src.config import config
from src.logic.karabiner_config import KarabinerConfig


class OverridesView():
    def __init__(self, keyboard_state_controller):
        self.karabiner_config = KarabinerConfig()
        self.keyboard_state_controller = keyboard_state_controller
        self.modification_change_view = ModificationChangeView({}, keyboard_state_controller)
        self.scroll_row_offset = 0
        self.start_row = 0

    def win_height(self):
        return config.window_height - self.start_row

    def set_scroll_offset(self, proposed_offset, num_rows_in_result):
        content_height = num_rows_in_result * config.font_size

        if content_height <= self.win_height():
            return 0

        max_negative_offset = self.win_height() - content_height

        if proposed_offset < max_negative_offset:
            proposed_offset = max_negative_offset
        if proposed_offset > 0:
            proposed_offset = 0
        return proposed_offset

    def draw_scrollbar(self, num_rows_in_result):
        content_height = num_rows_in_result * config.font_size
        available_height = self.win_height()

        # Only draw the scrollbar if the content exceeds the window height.
        if content_height > available_height:
            scrollbar_height_ratio = available_height / float(content_height)

            min_scrollbar_height = 20
            scrollbar_height = max(available_height * scrollbar_height_ratio,
                                   min_scrollbar_height)

            scroll_progress = abs(self.scroll_row_offset) / float(
                content_height - available_height)
            scrollbar_position = scroll_progress * (available_height - scrollbar_height)

            scrollbar_height = int(scrollbar_height)
            scrollbar_position = int(scrollbar_position)

            scrollbar_width = 10
            scrollbar_column = config.window_width - scrollbar_width - 1

            DrawRectangle(scrollbar_column, self.start_row + scrollbar_position,
                          scrollbar_width, scrollbar_height, VIOLET)


    def draw_overrides(self, start_col, start_row):
        self.modification_change_view.update_fn()
        self.modification_change_view.modification_pairs = self.karabiner_config.modification_pairs

        self.scroll_row_offset = self.set_scroll_offset(self.scroll_row_offset + int(GetMouseWheelMove() * config.scroll_speed), len(self.modification_change_view.modification_pairs))
        start_row += self.scroll_row_offset

        self.modification_change_view.draw_overrides(start_row, start_col)
        self.draw_scrollbar(len(self.karabiner_config.modification_pairs))