import pyray as ray

from src.components.drawing_helper import DrawingHelper
from src.config import config
from src.logic.yaml_config import YAML_Config
from src.panels.base_panel import BaseView


class OSMSectionView(BaseView):
    def __init__(self, current_key, reset_current_key_callback):
        super().__init__()
        self.state = {"Shift": False, "Opt": False, "Ctrl": False, "Cmd": False}
        self.map_to_key = {
            "right_shift": "Shift", "right_alt": "Opt", "right_control": "Ctrl", "right_command": "Cmd",
            "left_shift": "Shift", "left_alt": "Opt", "left_control": "Ctrl", "left_command": "Cmd"
        }
        self.reverse_mapping = {v: k for k, v in self.map_to_key.items()}
        self.reset_current_key_callback = reset_current_key_callback
        self.current_key = current_key

    def click_callback(self, mod_key):
        self.state[mod_key] = not self.state[mod_key]

    def submit(self):
        save_type = "osm"
        save_data = ' + '.join([self.reverse_mapping[key] for key, value in self.state.items() if value])
        YAML_Config().save(self.current_key[0].split(':')[0], self.current_key[0].split(':')[1], save_type, save_data)
        self.reset_current_key_callback()

    def draw_section(self, row, col):
        for mod_key in self.state.keys():
            col += DrawingHelper.button(
                mod_key, self.state[mod_key],
                row, col, config.small_font_size,
                self.click_callback,
                [mod_key]
            )
            col += config.small_padding

        DrawingHelper.button("Confirm", False, row, col, config.small_font_size, self.submit, [])

    def reset_values(self):
        self.state = {"Shift": False, "Opt": False, "Ctrl": False, "Cmd": False}

    def set_values(self, current_key):
        self.reset_values()
        osm_string = YAML_Config().key_overriddes(current_key[0].split(':')[0], current_key[0].split(':')[1])[1]
        kb_keys = osm_string.split(' + ')
        for kb_key in kb_keys:
            self.state[self.map_to_key[kb_key]] = True