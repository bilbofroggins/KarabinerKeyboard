import pyray as ray
from src.config import config
from src.panels.base_panel import BaseView
from src.versions.update_view import UpdateView
from src.views.help_view import HelpView
from src.views.keyboard_search_section import KeyboardSearchSection
from src.logic.keyboard_state_controller import KeyboardStateController
from src.views.keyboard_view import KeyboardView
from src.views.overrides_view import OverridesView


class ContentPanel(BaseView):
    def __init__(self, list_panel):
        super().__init__()
        self.kb_state_controller = KeyboardStateController()
        self.list_panel = list_panel
        self.background_color = config.background_color
        self.keyboard_view = KeyboardView(self.kb_state_controller)
        self.overrides_view = OverridesView(self.kb_state_controller)
        self.help_view = HelpView()
        self.keyboard_search_section = KeyboardSearchSection(self.kb_state_controller)
        self.update_view = UpdateView()

    def draw(self):
        left_panel_width = self.list_panel.panel_width

        # Draw the background for the content panel
        ray.draw_rectangle(left_panel_width, 0, config.window_width - left_panel_width, config.window_height,
                      self.background_color)

        if self.list_panel.selected_option:
            if self.list_panel.selected_option == "Keyboard":
                # Draw two lines of text at the bottom
                bottom_text_row = 280  # Adjusted Y position of the bottom text section
                self.keyboard_search_section.draw_overrides(
                    bottom_text_row + config.generic_padding,
                    left_panel_width + config.generic_padding
                )

                # Draw keyboard with some padding
                self.keyboard_view.draw_keyboard(left_panel_width + config.generic_padding, config.generic_padding)
            elif self.list_panel.selected_option == "Overrides":
                self.overrides_view.draw_overrides(left_panel_width + config.generic_padding, config.generic_padding)
            elif self.list_panel.selected_option == "Help":
                self.help_view.draw_help(left_panel_width + config.generic_padding,
                                               config.generic_padding)

        self.update_view.draw_updates(0, left_panel_width, config.window_height, config.window_width)