import pyray as ray
from src.config import config
from src.panels.base_panel import BaseView
from src.versions.update_view import UpdateView
from src.views.edit_view import EditView
from src.views.help_view import HelpView
from src.views.keyboard_view import KeyboardView
from src.views.layer_tabs_view import LayerTabsView


class ContentPanel(BaseView):
    def __init__(self, list_panel):
        super().__init__()
        self.list_panel = list_panel
        self.background_color = config.background_color
        self.layer = [0]
        self.current_key = [None]
        self.keyboard_view = KeyboardView(self.layer, self.current_key)
        self.edit_view = EditView(self.current_key)
        self.layer_tabs_view = LayerTabsView(self.layer)
        self.help_view = HelpView()
        self.update_view = UpdateView()

    def draw(self):
        left_panel_width = self.list_panel.panel_width

        # Draw the background for the content panel
        ray.draw_rectangle(left_panel_width, 0, config.window_width - left_panel_width, config.window_height,
                      self.background_color)

        if self.list_panel.selected_option:
            if self.list_panel.selected_option == "Keyboard":
                row = self.layer_tabs_view.draw_tabs(config.small_padding*3, left_panel_width + config.generic_padding)
                # Draw keyboard with some padding
                row = self.keyboard_view.draw_keyboard(left_panel_width + config.generic_padding, row + config.small_padding*2)
                self.edit_view.draw_edit_section(left_panel_width + config.generic_padding, row + config.small_padding*2)
            elif self.list_panel.selected_option == "Help":
                self.help_view.draw_help(left_panel_width + config.generic_padding,
                                               config.generic_padding)

        self.update_view.draw_updates(0, left_panel_width, config.window_height, config.window_width)