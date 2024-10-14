import pyray as ray

from src.components.drawing_helper import DrawingHelper
from src.config import config
from src.logic.yaml_config import YAML_Config
from src.panels.base_panel import BaseView


class LayerSectionView(BaseView):
    def __init__(self, current_key, reset_current_key_callback):
        super().__init__()
        self.state = {'layer': None, 'layer_type': None}
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

        col += config.generic_padding
        DrawingHelper.button("Confirm", False, row, col, config.small_font_size, self.submit, [])
        return row + config.small_font_size + config.generic_padding

    def draw_section(self, row, col):
        row = self.draw_layers(row, col)
        self.draw_layer_types(row, col)

    def reset_values(self):
        self.state = {'layer': None, 'layer_type': None}

    def set_values(self, current_key):
        self.reset_values()
        layer_type = YAML_Config().key_type(current_key[0].split(':')[0], current_key[0].split(':')[1]).split('|')[1]
        layer = YAML_Config().key_overriddes(current_key[0].split(':')[0], current_key[0].split(':')[1])[1]
        self.state['layer_type'] = layer_type
        self.state['layer'] = layer

