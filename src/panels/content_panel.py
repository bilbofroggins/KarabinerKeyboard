from raylib import *
from src.config import Config
from src.panels.base_panel import BaseView
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
        self.background_color = GRAY
        self.keyboard_view = KeyboardView(self.kb_state_controller)
        self.overrides_view = OverridesView(self.kb_state_controller)
        self.help_view = HelpView()
        self.keyboard_search_section = KeyboardSearchSection(self.kb_state_controller)

    def draw(self):
        left_panel_width = self.list_panel.panel_width

        # Draw the background for the content panel
        DrawRectangle(left_panel_width, 0, Config.window_width - left_panel_width, Config.window_height,
                      self.background_color)

        if self.list_panel.selected_option:
            if self.list_panel.selected_option.decode('utf-8') == "Keyboard":
                # Draw keyboard with some padding
                self.keyboard_view.draw_keyboard(left_panel_width + Config.generic_padding, Config.generic_padding)

                # Draw two lines of text at the bottom
                bottom_text_row = 280  # Adjusted Y position of the bottom text section
                self.keyboard_search_section.draw_overrides(
                    self.keyboard_view.search_keys,
                    bottom_text_row + Config.generic_padding,
                    left_panel_width + Config.generic_padding
                )
            elif self.list_panel.selected_option.decode('utf-8') == "Overrides":
                self.overrides_view.draw_overrides(left_panel_width + Config.generic_padding, Config.generic_padding)
            elif self.list_panel.selected_option.decode('utf-8') == "Help":
                self.help_view.draw_help(left_panel_width + Config.generic_padding,
                                               Config.generic_padding)
