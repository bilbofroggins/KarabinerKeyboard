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