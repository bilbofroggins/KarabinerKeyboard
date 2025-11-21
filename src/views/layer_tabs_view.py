import pyray as ray

from src.components.drawing_helper import DrawingHelper
from src.config import config
from src.logic.global_state import GlobalState
from src.logic.layer_colors import layer_color
from src.logic.merge_kb_config import merge_into_karabiner_config, write_enabled_flag
from src.logic.yaml_config import YAML_Config
from src.panels.base_panel import BaseView


class LayerTabsView(BaseView):
    def __init__(self, layer):
        super().__init__()
        self.current_layer = layer
        self.merge_feedback_frame = 0
        self.merge_feedback_state = None  # None, 'success', or 'failure'

    def draw_layer_text(self, row, col):
        text = "Layers:"
        ray.draw_text(text, col, row, config.small_font_size, config.default_text_color)
        col_size = ray.measure_text(text, config.small_font_size)
        return (row + config.small_font_size, col + col_size)

    def click_callback(self, layer):
        self.current_layer[0] = layer
        return

    def draw_on_off_toggle(self, row, col):
        off_size = ray.measure_text("OFF", config.small_font_size)
        on_size = ray.measure_text("ON", config.small_font_size)

        def draw_callback(row, col):
            row += config.small_padding
            rect_width = 10
            ray.draw_text("OFF", col, row,
                          config.small_font_size, ray.DARKGRAY)
            col += config.generic_padding + off_size
            ray.draw_rectangle(col, row, rect_width, config.small_font_size, ray.DARKGRAY)
            if config.enabled_flag:
                ray.draw_circle(col, row + config.small_font_size // 2,
                                config.small_font_size // 2, ray.DARKGRAY)
                ray.draw_circle(col + rect_width, row + config.small_font_size // 2,
                                config.small_font_size // 2, ray.GREEN)
            else:
                ray.draw_circle(col + rect_width, row + config.small_font_size // 2,
                                config.small_font_size // 2,
                                ray.GREEN if config.enabled_flag else ray.DARKGRAY)
                ray.draw_circle(col, row + config.small_font_size // 2,
                                config.small_font_size // 2,
                                ray.DARKGRAY if config.enabled_flag else ray.BLACK)
            ray.draw_text("ON", col + config.generic_padding + config.small_padding, row,
                          config.small_font_size, ray.DARKGRAY)
        def hover_callback(row, col):
            draw_callback(row, col)
        def click_callback():
            config.enabled_flag = not config.enabled_flag
            write_enabled_flag()

        DrawingHelper.generic_clickable(
            row, col,
            config.generic_padding + off_size + config.generic_padding + config.small_padding + on_size, config.small_font_size + config.small_padding*2,
            draw_callback, hover_callback, click_callback
        )

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

        self.draw_on_off_toggle(row - config.small_padding, config.window_width - 300)

        # Merge button with success feedback
        self.draw_merge_button(row - config.small_padding, config.window_width)

        return last_row

    def merge_button_callback(self):
        """Wrapper for merge that tracks success/failure state."""
        success = merge_into_karabiner_config()
        self.merge_feedback_frame = GlobalState().frame
        self.merge_feedback_state = 'success' if success else 'failure'

    def get_merge_feedback_state(self):
        """Check if merge button should still show feedback state.

        Returns 'success', 'failure', or None based on feedback state.
        Feedback displays for 2 seconds (120 frames at 60fps).
        """
        if self.merge_feedback_state is None:
            return None
        frames_to_show_feedback = 120  # 2 seconds at 60fps
        if GlobalState().frame - self.merge_feedback_frame > frames_to_show_feedback:
            self.merge_feedback_state = None
            return None
        return self.merge_feedback_state

    def draw_merge_button(self, row, right_edge):
        """Draw merge button with success/failure feedback."""
        feedback_state = self.get_merge_feedback_state()

        # Set text and color based on state
        if feedback_state == 'success':
            text = "Merged Successfully!"
            bg_color = ray.GREEN
            hover_bg_color = DrawingHelper.brighten(ray.GREEN)
        elif feedback_state == 'failure':
            text = "Err: check logs"
            bg_color = ray.RED
            hover_bg_color = DrawingHelper.brighten(ray.RED)
        else:
            text = "Merge to Config ->"
            bg_color = config.button_color
            hover_bg_color = DrawingHelper.brighten(config.button_color)

        text_width = ray.measure_text(text, config.small_font_size)
        button_width = text_width + config.small_padding * 2
        col = right_edge - button_width

        def draw_callback(row, col):
            ray.draw_rectangle(col, row,
                               button_width,
                               config.small_font_size + config.small_padding * 2,
                               bg_color)
            ray.draw_text(text, col + config.small_padding, row + config.small_padding,
                          config.small_font_size, config.default_text_color)

        def hover_callback(row, col):
            ray.draw_rectangle(col, row,
                               button_width,
                               config.small_font_size + config.small_padding * 2,
                               hover_bg_color)
            ray.draw_text(text, col + config.small_padding, row + config.small_padding,
                          config.small_font_size, DrawingHelper.brighten(config.default_text_color))

        DrawingHelper.generic_clickable(
            row, col,
            button_width, config.small_font_size + config.small_padding * 2,
            draw_callback, hover_callback, self.merge_button_callback, []
        )