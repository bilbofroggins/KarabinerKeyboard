from raylib import *

from src.config import config
from src.logic.key_mappings import *

DELIMITER = ' + '

class Modification:
    def __init__(self, modifiers: [] =None, key=''):
        if modifiers is None:
            modifiers = []
        self.modifiers = modifiers
        self.key = key
        self.edit_object = None

    def reset(self):
        self.modifiers = []
        self.key = ''

    def new_from_rl(self, rl_keys_set):
        self.reset()
        for key in rl_keys_set:
            kb_key = rl_to_kb_key_map[key]
            if kb_key in modification_keys:
                self.modifiers.append(kb_key)
            else:
                self.key = kb_key

        if self.key == '' and len(self.modifiers):
            self.key = self.modifiers[0]
            self.modifiers = []
        return self

    def update_dirty(self, rl_keys_set):
        if not self.edit_object:
            self.edit_object = Modification()
        self.edit_object.new_from_rl(rl_keys_set)

    def save(self):
        self.modifiers = self.edit_object.modifiers[:]
        self.key = self.edit_object.key
        self.edit_object = Modification()

    def to_json(self, *, is_to_field):
        obj = {
            "key_code": self.key,
        }
        if self.modifiers:
            if is_to_field:
                obj["modifiers"] = self.modifiers
            else:
                obj["modifiers"] = {
                    "mandatory": self.modifiers
                }
        return obj

    def __str__(self):
        if not len(self.modifiers):
            return self.key

        return DELIMITER.join(self.modifiers) + DELIMITER + self.key

    def draw(self, row, col, font_size, color, callback, args):
        og_col = col
        for mod in self.modifiers:
            display_mod = rl_to_display_key_map[kb_to_rl_key_map[str(mod)]]
            text_width = MeasureText(display_mod.encode('utf-8'), config.key_font_size)

            rect = (col, row + config.key_padding, text_width + config.key_padding*4, config.font_size - config.key_padding*2)
            DrawRectangleRoundedLines(rect, 0.1, 10, 0.5, color)
            DrawText(display_mod.encode('utf-8'), col + config.key_padding*2, row + config.key_padding, config.key_font_size, color)
            col += text_width + config.key_padding*2
            col += config.generic_padding

        display_key = rl_to_display_key_map[kb_to_rl_key_map[str(self.key)]]
        DrawText(display_key.encode('utf-8'), col, row, font_size, color)

        return col - og_col

    # Only used by internal edit_object
    def eo_currently_changing(self):
        return bool(self.key) or bool(self.modifiers)