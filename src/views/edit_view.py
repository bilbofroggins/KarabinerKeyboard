import pyray as ray

from src.components.drawing_helper import DrawingHelper
from src.config import config
from src.logic.event_bus import EventBus
from src.logic.global_state import GlobalState
from src.logic.yaml_config import YAML_Config
from src.panels.base_panel import BaseView
from src.views.section_types.keybind_section_view import KeybindSectionView
from src.views.section_types.layer_section_view import LayerSectionView
from src.views.section_types.shell_section_view import ShellSectionView


class EditView(BaseView):
    def __init__(self, current_key):
        super().__init__()
        EventBus().register('key_click', self)
        self.current_key = current_key
        self.sections = {
            "Keybind": KeybindSectionView(current_key, self.reset_current_key), "Shell": ShellSectionView(current_key, self.reset_current_key),
            "Layer": LayerSectionView(current_key, self.reset_current_key)
        }
        self.section_shown = self.sections["Keybind"]

    def reset_current_key(self):
        GlobalState().input_focus = 'keyboard'
        self.current_key[0] = None
        EventBus().notify('key_click')

    def clear_key(self):
        YAML_Config().save(self.current_key[0].split(':')[0], self.current_key[0].split(':')[1], None, None)
        self.reset_current_key()

    # Clicked on a new key in keyboard
    def notify(self):
        for section in self.sections.values():
            section.reset_values()

        if self.current_key[0] is None:
            return

        key_type = YAML_Config().key_type(*(self.current_key[0].split(":")))
        if key_type in ['single', 'multi']:
            self.section_shown = self.sections["Keybind"]
        elif key_type == 'shell':
            self.section_shown = self.sections["Shell"]
        elif key_type.split('|')[0] == 'layer':
            self.section_shown = self.sections["Layer"]
        else:
            self.section_shown = self.sections["Keybind"]

        if key_type:
            self.section_shown.set_values(self.current_key)

    def draw_section_titles(self, row, col):
        def click_callback(section_name):
            self.section_shown = self.sections[section_name]

        for section_name, section_view in self.sections.items():
            width = DrawingHelper.button(section_name, type(self.section_shown) == type(section_view), row, col, config.font_size, click_callback, [section_name])
            col += width + config.small_padding

        DrawingHelper.clickable_link("Clear Key", row + config.small_padding, col + config.generic_padding, config.font_size, ray.MAROON, self.clear_key, [])

        return row + config.font_size + config.generic_padding

    def draw_edit_section(self, col, row):
        if not self.current_key[0]:
            return False

        DrawingHelper.clickable_link("X", row, config.window_width - 50, config.font_size, ray.MAROON, self.reset_current_key, [])
        row = self.draw_section_titles(row, col)
        if self.section_shown:
            self.section_shown.draw_section(row, col)