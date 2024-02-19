from raylib import *

from src.config import config
from src.logic.karabiner_config import KarabinerConfig
from src.logic.key_mappings import rl_to_kb_key_map
from src.logic.keyboard_state_controller import *
from src.logic.modification import DELIMITER
from src.components.modification_change_view import ModificationChangeView

class KeyboardSearchSection():
    def __init__(self, keyboard_state_controller):
        self.karabiner_config = KarabinerConfig()
        self.modification_change_view = ModificationChangeView({}, keyboard_state_controller)
        self.keyboard_state_controller = keyboard_state_controller
        self.keyboard_state_controller.register(self)
        self.keyboard_state = STATE_EMPTY
        self.scroll_row_offset = 0
        self.start_row = None

    def change_keyboard_state(self, state):
        self.keyboard_state = state

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

    def draw_overrides(self, row, col):
        self.start_row = row
        self.modification_change_view.update_fn()

        # Search for relevant modifications based on key presses and set modifications
        pairs_to_show = {}
        pressed_keys = set([rl_to_kb_key_map[key] for key in self.keyboard_state_controller.locked_keys])
        if len(pressed_keys):
            for i, modification_pair in self.karabiner_config.modification_pairs.items():
                if pressed_keys <= set(str(modification_pair.modification_from).split(DELIMITER)):
                    pairs_to_show[i] = modification_pair
                    continue
                elif pressed_keys <= set(str(modification_pair.modification_to).split(DELIMITER)):
                    pairs_to_show[i] = modification_pair
                    continue

        self.modification_change_view.modification_pairs = pairs_to_show

        self.scroll_row_offset = self.set_scroll_offset(self.scroll_row_offset + int(GetMouseWheelMove() * config.scroll_speed), len(pairs_to_show) + 1)
        row += self.scroll_row_offset

        # Draw
        row = self.modification_change_view.draw_overrides(row, col)
        if row:
            self.modification_change_view.draw_add_row(row, col)

        DrawRectangle(col, 0, config.window_width - col, self.start_row, config.background_color)
        self.draw_scrollbar(len(pairs_to_show))
