import pyray as ray

from src.components.drawing_helper import DrawingHelper
from src.config import config
from src.logic.layer_colors import layer_color
from src.logic.merge_kb_config import merge_into_karabiner_config
from src.logic.yaml_config import YAML_Config
from src.panels.base_panel import BaseView


class LayerTabsView(BaseView):
    def __init__(self, layer):
        super().__init__()
        self.current_layer = layer

    def draw_layer_text(self, row, col):
        text = "Layers:"
        ray.draw_text(text, col, row, config.small_font_size, config.default_text_color)
        col_size = ray.measure_text(text, config.small_font_size)
        return (row + config.small_font_size, col + col_size)

    def click_callback(self, layer):
        self.current_layer[0] = layer
        return

    def draw_tab(self, layer_name, row, col, bg_color, current_layer = None):
        def click_callback(layer):
            YAML_Config().delete_layer(layer)

        layer = 0 if layer_name == "Default" else int(layer_name.split("Layer ")[1])
        text_width = ray.measure_text(layer_name, config.small_font_size)
        additional_close_width = config.small_padding*2 + config.small_font_size if layer > 0 else 0
        end_col = col + text_width + config.small_padding + additional_close_width

        if current_layer == layer:
            ray.draw_rectangle(col - config.small_padding*2, row - config.small_padding*2,
                               text_width + config.small_padding * 4 + additional_close_width,
                               config.small_font_size + config.small_padding * 4,
                               config.error_color)

        ray.draw_rectangle(col - config.small_padding, row - config.small_padding,
                           text_width + config.small_padding*2 + additional_close_width, config.small_font_size + config.small_padding*2,
                           bg_color)
        ray.draw_text(layer_name, col, row, config.small_font_size,
                         config.default_text_color)

        if layer > 0:
            DrawingHelper.clickable_link(
                "x",
                row, end_col - config.small_font_size,
                config.small_font_size, ray.MAROON,
                click_callback, [layer]
            )
        return (row + config.small_font_size, end_col)

    def draw_callback(self, row, col, layer, current_layer):
        layer_name = "Layer " + str(layer) if layer > 0 else "Default"
        color = layer_color(layer)

        text_width = ray.measure_text(layer_name, config.small_font_size)
        return self.draw_tab(layer_name, row, col, color, current_layer)

    def hover_callback(self, row, col, layer, current_layer):
        layer_name = "Layer " + str(layer) if layer > 0 else "Default"
        return self.draw_tab(layer_name, row, col, config.error_color)

    def draw_tabs(self, row, col):
        last_row, last_col = self.draw_layer_text(row, col)

        for layer in YAML_Config().layers():
            layer_name = "Layer " + str(layer) if layer > 0 else "Default"
            width = ray.measure_text(layer_name, config.small_font_size)
            _, last_col = DrawingHelper.generic_clickable(
                row, last_col + config.small_padding*2,
                width, config.small_font_size,
                self.draw_callback, self.hover_callback, self.click_callback,
                [layer], [layer, self.current_layer[0]]
            )

        width = ray.measure_text("Merge to Config ->", config.small_font_size) + config.generic_padding*2
        DrawingHelper.button("Merge to Config ->", False, row - config.small_padding, config.window_width - width, config.small_font_size, merge_into_karabiner_config, [])

        return last_row