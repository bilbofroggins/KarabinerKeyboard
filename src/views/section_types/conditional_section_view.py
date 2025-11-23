import pyray as ray

from src.components.drawing_helper import DrawingHelper
from src.components.text_input import TextInput
from src.config import config
from src.logic.yaml_config import YAML_Config
from src.panels.base_panel import BaseView


class ConditionalSectionView(BaseView):
    def __init__(self, current_key, reset_current_key_callback):
        super().__init__()
        self.current_key = current_key
        self.reset_current_key_callback = reset_current_key_callback
        self.variable_input = TextInput()
        self.mode = 'get'  # 'get' or 'toggle'

    def submit(self):
        """Save the conditional configuration."""
        variable_name = self.variable_input.get_text().strip()
        if not variable_name:
            return

        layer, key = self.current_key[0].split(':')

        if self.mode == 'get':
            # Add 'if' condition to existing key
            YAML_Config().set_if_variable(layer, key, variable_name)
        else:
            # Change to type: conditional (toggle mode - no value needed)
            YAML_Config().save(layer, key, 'conditional', variable_name)

        self.reset_current_key_callback()

    def draw_section(self, row, col):
        row += config.small_padding

        # Variable name input
        ray.draw_text("Variable name:", col, row, config.font_size, config.default_text_color)
        row += config.font_size + config.small_padding

        input_width = 300
        self.variable_input.draw(row, col, input_width)
        row += config.font_size + config.small_padding * 3

        # Mode toggle (Get/Toggle)
        ray.draw_text("Mode:", col, row, config.font_size, config.default_text_color)
        row += config.font_size + config.small_padding

        # Get button
        get_pressed = self.mode == 'get'
        get_width = DrawingHelper.button("Get", get_pressed, row, col, config.font_size,
                                        lambda: setattr(self, 'mode', 'get'), [])

        # Toggle button
        toggle_pressed = self.mode == 'toggle'
        DrawingHelper.button("Toggle", toggle_pressed, row, col + get_width + config.small_padding,
                           config.font_size, lambda: setattr(self, 'mode', 'toggle'), [])

        row += config.font_size + config.generic_padding

        # Confirm button
        DrawingHelper.button("Confirm", False, row, col, config.font_size, self.submit, [])

    def reset_values(self):
        """Clear inputs."""
        self.variable_input.set_text("")
        self.variable_input.is_focused = False
        self.mode = 'get'

    def set_values(self, current_key):
        """Load existing conditional data."""
        self.reset_values()
        layer, key = current_key[0].split(':')
        key_type = YAML_Config().key_type(layer, key)
        current_if = YAML_Config().get_if_variable(layer, key)

        # Check if key has an 'if' condition
        if current_if:
            self.mode = 'get'
            self.variable_input.set_text(current_if)
        # Check if key is type: conditional
        elif key_type == 'conditional':
            self.mode = 'toggle'
            _, data = YAML_Config().key_overriddes(layer, key)
            if data:
                # Data is just the variable name (no pipe for toggle)
                self.variable_input.set_text(data)
