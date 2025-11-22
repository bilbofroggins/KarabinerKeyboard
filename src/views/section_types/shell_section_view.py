import pyray as ray

from src.components.drawing_helper import DrawingHelper
from src.components.text_input import TextInput
from src.config import config
from src.logic.global_state import GlobalState
from src.logic.yaml_config import YAML_Config
from src.panels.base_panel import BaseView


class ShellSectionView(BaseView):
    def __init__(self, current_key, reset_current_key_callback):
        super().__init__()
        self.text_input = TextInput()
        self.reset_current_key_callback = reset_current_key_callback
        self.current_key = current_key

    def submit(self):
        """Save the shell command to the YAML config."""
        command = self.text_input.get_text().strip()
        if command:  # Only save if there's actually a command
            YAML_Config().save(
                self.current_key[0].split(':')[0],
                self.current_key[0].split(':')[1],
                'shell',
                command
            )
            self.reset_current_key_callback()

    def draw_section(self, row, col):
        row += config.small_padding

        # Draw label
        ray.draw_text("Shell Command:", col, row, config.font_size, config.default_text_color)
        row += config.font_size + config.small_padding

        # Draw text input
        input_width = config.window_width - col - config.generic_padding * 2
        self.text_input.draw(row, col, input_width)
        row += config.font_size + config.small_padding * 3

        # Focus the input when this view is shown
        if not self.text_input.is_focused and GlobalState().input_focus == 'edit_view':
            self.text_input.is_focused = True

        # Draw confirm button
        DrawingHelper.button("Confirm", False, row, col, config.font_size, self.submit, [])

    def reset_values(self):
        """Clear the text input."""
        self.text_input.set_text("")
        self.text_input.is_focused = False

    def set_values(self, current_key):
        """Load existing shell command from YAML config."""
        self.reset_values()
        key_type, data = YAML_Config().key_overriddes(
            current_key[0].split(':')[0],
            current_key[0].split(':')[1]
        )
        if key_type == 'shell' and data:
            self.text_input.set_text(data)