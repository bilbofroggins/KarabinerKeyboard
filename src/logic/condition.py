import pyray as ray

from src.config import config
from src.logic.bundle import Bundle


class Condition:
    def __init__(self, bundle_identifiers=[], include_type_str=''):
        if len(bundle_identifiers) and type(bundle_identifiers[0]) is Bundle:
            self.bundle_identifiers = bundle_identifiers
        else:
            self.bundle_identifiers = [Bundle(json_string=bundle) for bundle in bundle_identifiers]
        self.include_type_str = include_type_str

        self.include_str = "frontmost_application_if"
        self.exclude_str = "frontmost_application_unless"

    def color(self):
        if self.include_type_str == self.include_str:
            return ray.GREEN
        elif self.include_type_str == self.exclude_str:
            return ray.RED
        return config.disabled_color

    def __bool__(self):
        if len(self.bundle_identifiers):
            return True
        return False

    def to_json(self):
        return [
            {
                "bundle_identifiers": [bundle.to_json() for bundle in self.bundle_identifiers],
                "type": self.include_type_str
            }
        ]