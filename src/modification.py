from src.key_mappings import rl_to_kb_key_map, modification_keys

class Modification:
    def __init__(self, modifiers=None, key=''):
        if modifiers is None:
            modifiers = []
        self.modifiers = modifiers
        self.key = key
        self.edit_object = None

    def update_dirty(self, rl_keys_set):
        if not self.edit_object:
            self.edit_object = Modification()
        self.edit_object.modifiers = []
        self.edit_object.key = ''
        for key in rl_keys_set:
            kb_key = rl_to_kb_key_map[key]
            if kb_key in modification_keys:
                self.edit_object.modifiers.append(kb_key)
            else:
                self.edit_object.key = kb_key

        if self.edit_object.key == '' and len(self.edit_object.modifiers):
            self.edit_object.key = self.edit_object.modifiers[0]
            self.edit_object.modifiers = []
        return self.edit_object

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

        return ' + '.join(self.modifiers) + ' + ' + self.key

    def currently_changing(self):
        return bool(self.key) or bool(self.modifiers)
