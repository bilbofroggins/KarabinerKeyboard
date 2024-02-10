from karabiner_config import KarabinerConfig
from src.modification_change_view import ModificationChangeView

class OverridesView():
    def __init__(self, keyboard_state_controller):
        self.karabiner_config = KarabinerConfig()
        self.keyboard_state_controller = keyboard_state_controller
        self.modification_change_view = ModificationChangeView(self.karabiner_config.modification_pairs, keyboard_state_controller)
        self.modification_change_view.test = 'abc'

    def draw_overrides(self, start_col, start_row):
        self.modification_change_view.update_fn()
        self.modification_change_view.draw_overrides(start_col, start_row)