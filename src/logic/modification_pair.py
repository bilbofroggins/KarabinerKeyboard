class ModificationPair:
    # Takes in keys in karabiner form and converts them to raylib ids
    def __init__(self, modification_from, modification_to, condition):
        self.modification_from = modification_from
        self.modification_to = modification_to
        self.condition = condition

    def to_json(self):
        pair = {
            "description": str(self.modification_from) + " -> " + str(self.modification_to),
            "manipulators": [
                {
                    "from": self.modification_from.to_json(is_to_field=False),
                    "to": [self.modification_to.to_json(is_to_field=True)],
                    "type": "basic"
                }
            ]
        }
        if self.condition:
            pair["manipulators"][0]["conditions"] = self.condition.to_json()

        return pair