class Version:
    def __init__(self, version_str):
        self.parts = [int(part) for part in version_str.split('.')]

    def __eq__(self, other):
        return self.compare(other) == 0

    def __lt__(self, other):
        return self.compare(other) < 0

    def __le__(self, other):
        return self.compare(other) <= 0

    def __gt__(self, other):
        return self.compare(other) > 0

    def __ge__(self, other):
        return self.compare(other) >= 0

    def __str__(self):
        return '.'.join([str(part) for part in self.parts])

    def compare(self, other):
        """
        Compares this Version object to another.

        :param other: Another Version object.
        :return: -1 if self < other, 1 if self > other, 0 if equal.
        """
        max_length = max(len(self.parts), len(other.parts))
        extended_parts = self.parts + [0] * (max_length - len(self.parts))
        other_extended_parts = other.parts + [0] * (max_length - len(other.parts))

        for self_part, other_part in zip(extended_parts, other_extended_parts):
            if self_part < other_part:
                return -1
            if self_part > other_part:
                return 1
        return 0

