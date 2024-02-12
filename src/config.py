import sys
from raylib import *


class Config:
    window_width = 960
    window_height = 540
    font_size = 20
    generic_padding = 20
    karabiner_file = '~/.config/karabiner/karabiner.json'
    default_text_color = BLACK

class Config_Debug:
    karabiner_file = '~/.config/karabiner/karabiner.json'




def merge_configs_if_debug(debug_mode):
    if debug_mode:
        for attribute_name in dir(Config_Debug):
            if not attribute_name.startswith("__"):
                attribute_value = getattr(Config_Debug, attribute_name)
                setattr(Config, attribute_name, attribute_value)

if not getattr(sys, 'frozen', False):
    debug_mode = True
else:
    debug_mode = False
merge_configs_if_debug(debug_mode)