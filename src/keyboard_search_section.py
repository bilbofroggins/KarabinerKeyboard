from karabiner_config import KarabinerConfig
from src.modification_change_view import ModificationChangeView

class KeyboardSearchSection():
    def __init__(self):
        self.karabiner_config = KarabinerConfig()
        self.modification_change_view = None

    def draw_overrides(self, row, col):
        # search for relevent modifications based on key presses and set modifications
        self.modification_change_view = ModificationChangeView(self.karabiner_config.modification_pairs)

        # draw
        self.modification_change_view.draw_overrides(col, row)
