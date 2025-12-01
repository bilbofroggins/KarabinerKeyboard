import os

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
    yaml_location = os.path.expanduser('~/.config/karabiner_keyboard/default.yaml')
    
    # Colors as RGBA tuples (matching raylib's color values)
    # This avoids importing pyray at module load time
    default_text_color = (0, 0, 0, 255)        # BLACK
    secondary_color = (0, 121, 241, 255)       # BLUE
    background_color = (130, 130, 130, 255)    # GRAY
    disabled_color = (200, 200, 200, 255)      # LIGHTGRAY
    ask_save_color = (0, 121, 241, 255)        # BLUE
    
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
    scroll_speed = 4
    enabled_flag = None
