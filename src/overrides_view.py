from karabiner_config import KarabinerConfig
from src.modification_change_view import ModificationChangeView

class OverridesView():
    def __init__(self):
        self.karabiner_config = KarabinerConfig()
        self.modification_change_view = ModificationChangeView(self.karabiner_config.modification_pairs)

    def draw_overrides(self, start_col, start_row):
        self.modification_change_view.draw_overrides(start_col, start_row)