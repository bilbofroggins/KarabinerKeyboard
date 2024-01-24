class ModificationPair:
    # Takes in keys in karabiner form and converts them to raylib ids
    def __init__(self, modification_from, modification_to):
        self.modification_from = modification_from
        self.modification_to = modification_to

    def to_json(self):
        description = "change stuff"
        return {
            "description": description,
            "manipulators": [
                {
                    "from": self.modification_from.to_json(is_to_field=False),
                    "to": [self.modification_to.to_json(is_to_field=True)],
                    "type": "basic"
                }
            ]
        }