import sys

import pyray as ray

class config:
    window_width = 960
    window_height = 540
    small_font_size = 14
    font_size = 20
    large_font_size = 40
    generic_padding = 20
    list_padding = 10
    small_padding = 5
    karabiner_file = '~/.config/karabiner/karabiner.json'
    default_text_color = ray.BLACK
    secondary_color = ray.BLUE
    background_color = ray.GRAY
    disabled_color = ray.LIGHTGRAY
    delimiter_color = (221, 148, 224, 255)
    left_mod_color = (81, 199, 77, 255)
    left_mod_kb_color = (61, 161, 57, 255)
    right_mod_color = (105, 211, 250, 255)
    right_mod_kb_color = (75, 181, 220, 255)
    error_color = (150, 50, 50, 255)
    lime_color = (151, 186, 153, 255)
    active_tab_color = (122, 41, 136, 255)
    ask_highlight_color = (180, 151, 186, 255)
    ask_save_color = ray.BLUE
    scroll_speed = 4

class config_debug:
    karabiner_file = '~/.config/karabiner/karabiner_debug.json'


def merge_configs_if_debug(debug_mode):
    if debug_mode:
        for attribute_name in dir(config_debug):
            if not attribute_name.startswith("__"):
                attribute_value = getattr(config_debug, attribute_name)
                setattr(config, attribute_name, attribute_value)

if not getattr(sys, 'frozen', False):
    debug_mode = True
else:
    debug_mode = False
merge_configs_if_debug(debug_mode)


class DiggableWrapper:
    def __init__(self, value):
        # Automatically wrap lists and dictionaries
        if isinstance(value, list):
            self._value = [DiggableWrapper(item) for item in value]
        elif isinstance(value, dict):
            self._value = {key: DiggableWrapper(item) for key, item in value.items()}
        else:
            self._value = value

    def dig(self, *keys, default=None):
        value = self._value
        try:
            for key in keys:
                if isinstance(value, DiggableWrapper):
                    value = value._value
                if isinstance(value, list) and isinstance(key, int):
                    value = value[key]
                elif isinstance(value, dict) and isinstance(key, (str, int)):
                    value = value[key]
                else:
                    return default
                value = DiggableWrapper(value)  # Re-wrap the nested value
        except (IndexError, KeyError, TypeError):
            return default
        return value._value if isinstance(value, DiggableWrapper) else value

    def __getitem__(self, key):
        return self._value[key]

    def __len__(self):
        if isinstance(self._value, (list, dict)):
            return len(self._value)
        raise TypeError(f"object of type '{type(self._value).__name__}' has no len()")

    def __contains__(self, item):
        if isinstance(self._value, (list, dict)):
            return item in self._value
        raise TypeError(f"object of type '{type(self._value).__name__}' has no contains()")

    def __repr__(self):
        return repr(self._value)