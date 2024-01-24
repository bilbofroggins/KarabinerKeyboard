class Modification:
    # Takes in keys in karabiner form and converts them to raylib ids
    def __init__(self, modifiers=None, key=''):
        if modifiers is None:
            modifiers = []
        self.modifiers = modifiers
        self.key = key

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
