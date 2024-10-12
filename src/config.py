import os
import pyray as ray

class config:
    window_width = 960
    window_height = 540
    small_font_size = 14
    corner_font_size = 11
    font_size = 20
    large_font_size = 40
    generic_padding = 20
    list_padding = 10
    small_padding = 5
    kb_config_location = os.path.expanduser('~/.config/karabiner/karabiner.json')
    # yaml_location = os.path.expanduser('~/.config/karabiner_keyboard/default.yaml')
    yaml_location = os.path.expanduser('../test/test_config.yaml')
    default_text_color = ray.BLACK
    secondary_color = ray.BLUE
    background_color = ray.GRAY
    disabled_color = ray.LIGHTGRAY
    button_color = (221, 148, 224, 255)
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
