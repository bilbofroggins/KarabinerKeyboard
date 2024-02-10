from karabiner_config import KarabinerConfig
from src.key_mappings import rl_to_kb_key_map
from src.keyboard_state_controller import *
from src.modification import DELIMITER
from src.modification_change_view import ModificationChangeView

class KeyboardSearchSection():
    def __init__(self, keyboard_state_controller):
        self.karabiner_config = KarabinerConfig()
        self.modification_change_view = ModificationChangeView({}, keyboard_state_controller)
        self.keyboard_state_controller = keyboard_state_controller
        self.keyboard_state_controller.register(self)
        self.keyboard_state = STATE_EMPTY

    def change_keyboard_state(self, state):
        self.keyboard_state = state

    def draw_overrides(self, search_keys, row, col):
        self.modification_change_view.update_fn()

        # Search for relevant modifications based on key presses and set modifications
        pairs_to_show = {}
        pressed_keys = set([rl_to_kb_key_map[key] for key in search_keys])
        for i, modification_pair in self.karabiner_config.modification_pairs.items():
            if pressed_keys <= set(str(modification_pair.modification_from).split(DELIMITER)):
                pairs_to_show[i] = modification_pair
                continue
            elif pressed_keys <= set(str(modification_pair.modification_to).split(DELIMITER)):
                pairs_to_show[i] = modification_pair
                continue

        self.modification_change_view.modification_pairs = pairs_to_show

        # Draw
        self.modification_change_view.draw_overrides(col, row)
