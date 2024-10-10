import pyray as ray

from src.components.drawing_helper import DrawingHelper
from src.config import config
from src.logic.key_mappings import kb_to_rl_key_map, rl_to_display_key_map
from src.logic.yaml_config import YAML_Config
from src.panels.base_panel import BaseView


class KeybindSectionView(BaseView):
    def __init__(self, current_key, reset_current_key_callback):
        super().__init__()
        # [[left_control, k], ...]
        self.state = []
        self.reset_current_key_callback = reset_current_key_callback
        self.current_key = current_key

    def submit(self):
        save_type = 'single' if len(self.state) == 1 else 'multi'
        if save_type == 'single':
            save_data = ' + '.join(self.state[0])
        else:
            save_data = [' + '.join(chord) for chord in self.state]
        YAML_Config().save(self.current_key[0].split(':')[0], self.current_key[0].split(':')[1], save_type, save_data)
        self.reset_current_key_callback()

    def draw_section(self, row, col):
        row += config.small_padding
        row_under = row + config.font_size
        for chord in self.state:
            chord_text = ''.join([rl_to_display_key_map[kb_to_rl_key_map[key]] for key in chord])
            width = DrawingHelper.clickable_link(chord_text, row, col, config.font_size, ray.BLACK, lambda: None, [])
            ray.draw_line_ex(ray.Vector2(col, row_under),
                             ray.Vector2(col + width, row_under), 2,
                             ray.BLACK)
            col += width + config.small_padding

        ray.draw_line_ex(ray.Vector2(col, row_under), ray.Vector2(col + config.font_size, row_under), 2, ray.MAROON)
        col += config.font_size + config.generic_padding

        row -= config.small_padding
        DrawingHelper.button("Confirm", False, row, col, config.font_size, self.submit, [])


    def reset_values(self):
        self.state = []

    def set_values(self, current_key):
        self.reset_values()
        key_type, data = YAML_Config().key_overriddes(current_key[0].split(':')[0], current_key[0].split(':')[1])
        if key_type == 'single':
            self.state.append(data.split(' + '))
        else:
            for motion in data:
                self.state.append(motion.split(' + '))