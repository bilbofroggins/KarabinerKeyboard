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
    karabiner_file = '~/.config/karabiner/karabiner_debug.json'




def merge_configs_if_debug(debug_mode):
    if debug_mode:
        # Iterate through each attribute in Config_Debug
        for attribute_name in dir(Config_Debug):
            if not attribute_name.startswith("__"):  # Ignore magic methods and attributes
                # Get attribute value from Config_Debug
                attribute_value = getattr(Config_Debug, attribute_name)
                # Set/Update this attribute in Config
                setattr(Config, attribute_name, attribute_value)

# Example usage
if not getattr(sys, 'frozen', False):
    debug_mode = True
else:
    debug_mode = False
merge_configs_if_debug(debug_mode)