import sys
from raylib import *


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
    default_text_color = BLACK
    secondary_color = BLUE
    background_color = GRAY
    disabled_color = LIGHTGRAY
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