import pyray as ray

from src.components.drawing_helper import DrawingHelper
from src.config import config
from src.devices.keyboard_controller import KeyboardController
from src.logic.global_state import GlobalState
from src.logic.key_mappings import kb_to_rl_key_map, rl_to_display_key_map
from src.logic.yaml_config import YAML_Config
from src.panels.base_panel import BaseView


class LayerSectionView(BaseView):
    def __init__(self, current_key, reset_current_key_callback):
        super().__init__()
        self.state = {'layer': None, 'layer_type': None, 'tap_key': None}
        self.current_key = current_key
        self.reset_current_key_callback = reset_current_key_callback

    def click_layer_callback(self, layer):
        self.state['layer'] = layer
        if max(YAML_Config().data['layers'].keys()) < layer:
            YAML_Config().data['layers'][layer] = {}

    def click_layer_type_callback(self, layer_type):
        self.state['layer_type'] = layer_type

    def submit(self):
        if self.state['layer_type'] is None and self.state['layer'] is None:
            save_type = None
            save_data = None
            YAML_Config().save(self.current_key[0].split(':')[0],
                               self.current_key[0].split(':')[1], save_type, save_data)
            self.reset_current_key_callback()
        elif self.state['layer_type'] is None or self.state['layer'] is None:
            return
        else:
            save_type = "layer|" + self.state['layer_type']
            if self.state['layer_type'] == 'LT' and self.state['tap_key'] is not None:
                save_data = self.state['layer'] + '|' + self.state['tap_key']
            else:
                save_data = self.state['layer']
            YAML_Config().save(self.current_key[0].split(':')[0], self.current_key[0].split(':')[1], save_type, save_data)
            self.reset_current_key_callback()

    def draw_layers(self, row, col):
        for layer in YAML_Config().layers():
            text = str(layer) if layer > 0 else "Default"
            col += DrawingHelper.button(text, str(self.state['layer']) == str(layer), row, col, config.small_font_size, self.click_layer_callback, [layer])
            col += config.small_padding

        text = "New Layer"
        col += DrawingHelper.button(text, False, row, col, config.small_font_size, self.click_layer_callback, [layer + 1])
        col += config.small_padding

        return row + config.small_font_size + config.generic_padding

    def draw_layer_types(self, row, col):
        layer_types = ['MO', 'LT', 'TO'] # Momentary, Momentary w Tap, Toggle
        for layer_type in layer_types:
            col += DrawingHelper.button(layer_type, self.state['layer_type'] == layer_type, row, col, config.small_font_size, self.click_layer_type_callback, [layer_type])
            col += config.small_padding

        return row + config.small_font_size + config.generic_padding

    def add_tap_key(self):
        if GlobalState().input_focus == 'edit_view':
            keys = KeyboardController.listen_to_keys()
            if keys:
                self.state['tap_key'] = keys[0]

    def draw_tap_key_input(self, row, col):
        DrawingHelper.draw_unicode_plus_text("Tap Key:", row, col, config.small_font_size, ray.BLACK)
        col += DrawingHelper.measure_unicode_plus_text("Tap Key:", config.small_font_size) + config.generic_padding * 2

        if self.state['tap_key']:
            tap_text = ''.join([rl_to_display_key_map[kb_to_rl_key_map[key]] for key in self.state['tap_key']])
            DrawingHelper.draw_unicode_plus_text(tap_text, row, col, config.small_font_size, ray.BLACK)
            col += DrawingHelper.measure_unicode_plus_text(tap_text, config.small_font_size) + config.small_padding * 5

            def clear_tap_key():
                self.state['tap_key'] = None
            DrawingHelper.clickable_link("Clear", row, col, config.small_font_size, ray.MAROON, clear_tap_key, [])
        else:
            DrawingHelper.draw_unicode_plus_text("(press a key or leave empty for default)", row, col, config.small_font_size, ray.GRAY)

        self.add_tap_key()
        return row + config.small_font_size + config.generic_padding

    def draw_section(self, row, col):
        row = self.draw_layers(row, col)
        row = self.draw_layer_types(row, col)

        # Show tap key input only when LT is selected
        if self.state['layer_type'] == 'LT':
            row = self.draw_tap_key_input(row, col)

        DrawingHelper.button("Confirm", False, row, col, config.small_font_size, self.submit, [])

    def reset_values(self):
        self.state = {'layer': None, 'layer_type': None, 'tap_key': None}

    def set_values(self, current_key):
        self.reset_values()
        layer_type = YAML_Config().key_type(current_key[0].split(':')[0], current_key[0].split(':')[1]).split('|')[1]
        layer_data = YAML_Config().key_overriddes(current_key[0].split(':')[0], current_key[0].split(':')[1])[1]
        self.state['layer_type'] = layer_type

        # Handle both old format (int) and new format (dict with layer and tap_key)
        if isinstance(layer_data, str):
            layer_strings = layer_data.split('|')
            if len(layer_strings) > 1:
                layernum = layer_strings[0]
                tap_key_str = layer_strings[1]
            else:
                layernum = layer_strings[0]
                tap_key_str = None

            self.state['layer'] = layernum
            if tap_key_str:
                self.state['tap_key'] = tap_key_str
        else:
            self.state['layer'] = layer_data

