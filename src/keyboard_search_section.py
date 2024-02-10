from karabiner_config import KarabinerConfig
from src.key_mappings import rl_to_kb_key_map
from src.keyboard_controller import KeyboardController
from src.modification_change_view import ModificationChangeView

class KeyboardSearchSection():
    def __init__(self):
        self.karabiner_config = KarabinerConfig()
        self.modification_change_view = ModificationChangeView({})

    def draw_overrides(self, row, col):
        # search for relevent modifications based on key presses and set modifications
        pairs_to_show = {}
        pressed_keys = set([rl_to_kb_key_map[key] for key in KeyboardController.pressed_keys])
        for i, modification_pair in self.karabiner_config.modification_pairs.items():
            if pressed_keys <= set(str(modification_pair.modification_from).split('+')):
                pairs_to_show[i] = modification_pair
                continue
            elif pressed_keys <= set(str(modification_pair.modification_to).split('+')):
                pairs_to_show[i] = modification_pair
                continue

        self.modification_change_view.modification_pairs = pairs_to_show

        # draw
        self.modification_change_view.draw_overrides(col, row)
