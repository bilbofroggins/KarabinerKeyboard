import pyray as ray

from src.components.drawing_helper import DrawingHelper
from src.config import config
from src.devices.keyboard_controller import KeyboardController
from src.logic.global_state import GlobalState
from src.logic.key_mappings import kb_to_rl_key_map, rl_to_display_key_map
from src.logic.yaml_config import YAML_Config
from src.panels.base_panel import BaseView
import src.panels.global_vars as g


class KeybindSectionView(BaseView):
    def __init__(self, current_key, reset_current_key_callback):
        super().__init__()
        # [[left_control, k], ...]
        self.state = []
        self.reset_current_key_callback = reset_current_key_callback
        self.current_key = current_key
        self.trail = []
        self.keys_held_down = set()

    def submit(self):
        save_type = 'single' if len(self.state) == 1 else 'multi'
        if save_type == 'single':
            save_data = ' + '.join(self.state[0])
        else:
            save_data = [' + '.join(chord) for chord in self.state]
        YAML_Config().save(self.current_key[0].split(':')[0], self.current_key[0].split(':')[1], save_type, save_data)
        self.reset_current_key_callback()

    def draw_waiting_animation(self, row, col, width, height):
        frame = GlobalState().frame
        perimeter = 2 * (width + height)
        frames_per_cycle = 60

        fraction_of_cycle = (frame % frames_per_cycle) / frames_per_cycle

        # Calculate the distance along the perimeter based on the fraction
        distance = fraction_of_cycle * perimeter

        # Determine the current position along the rectangle's perimeter
        if distance < width:  # Top edge
            current_col = col + distance
            current_row = row
        elif distance < width + height:  # Right edge
            current_col = col + width
            current_row = row + (distance - width)
        elif distance < 2 * width + height:  # Bottom edge
            current_col = col + (2 * width + height - distance)
            current_row = row + height
        else:  # Left edge
            current_col = col
            current_row = row + (perimeter - distance)

        self.trail.append((current_col, current_row))

        # Limit the trail length
        if len(self.trail) > 60:
            self.trail.pop(0)

        # Draw the trail
        for i in range(1, len(self.trail)):
            ray.draw_line_ex(
                ray.Vector2(int(self.trail[i - 1][0]), int(self.trail[i - 1][1])),
                ray.Vector2(int(self.trail[i][0]), int(self.trail[i][1])),
                2,
                DrawingHelper.make_transparent(ray.MAROON, (len(self.trail) - i) * 6)
            )
    def add_keys_held_down(self):
        if GlobalState().input_focus == 'edit_view':
            keys = KeyboardController.listen_to_keys()
            if keys:
                self.state.append(keys)

    def draw_section(self, row, col):
        row += config.small_padding
        row_under = row + config.font_size

        def draw_chord(row, col, chord_text, width):
            DrawingHelper.draw_unicode_plus_text(chord_text, row, col, config.font_size, ray.BLACK, 1)
        def hover_chord(row, col, chord_text, width):
            col = col + width/2 - config.font_size/2
            ray.draw_texture_ex(g.textures['trash'], (col, row), 0, 0.15, config.error_color)
        def click_chord(index):
            del self.state[index]

        for i, chord in enumerate(self.state):
            chord_text = ''.join([rl_to_display_key_map[kb_to_rl_key_map[key]] for key in chord])
            width = DrawingHelper.measure_unicode_plus_text(chord_text, config.font_size, 1)
            DrawingHelper.generic_clickable(row, col, width, config.font_size, draw_chord, hover_chord, click_chord, [i], [chord_text, width])
            ray.draw_line_ex(ray.Vector2(col, row_under),
                             ray.Vector2(col + width, row_under), 2,
                             ray.BLACK)
            col += width + config.small_padding*2

        self.add_keys_held_down()
        self.draw_waiting_animation(row, col, config.font_size, row_under - row)
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