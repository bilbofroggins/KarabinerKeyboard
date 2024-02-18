import threading

from raylib import *

from src.config import config
from src.logic.karabiner_config import KarabinerConfig
from src.panels.base_panel import BaseView
from src.components.drawing_helper import DrawingHelper
from src.versions.updates import *
from src.versions.version import __version__


class HelpView(BaseView):
    def __init__(self):
        super().__init__()
        self.is_quitting = False
        self.quitting_done_flag = [False]
        self.is_updated = True
        threading.Thread(target=self.check_updates, daemon=True).start()

    def check_updates(self):
        self.is_updated, self.latest_version = check_up_to_date()

    def draw_help(self, start_x, start_y):
        if self.quitting_done_flag[0] == True:
            sys.exit(0)
        elif self.is_quitting:
            DrawText(b"Restarting...",
                     start_x, start_y, config.font_size * 4, config.default_text_color)
            return

        DrawText(f"Version: {__version__}".encode('utf-8'),
                 start_x, start_y, config.font_size, config.default_text_color)
        start_y += config.font_size
        DrawText(b"This application is pre-alpha and may screw up your karabiner file",
                 start_x, start_y, config.font_size, config.default_text_color)
        start_y += config.font_size
        DrawText(b"We save a copy of your karabiner config file before we make changes to it",
                 start_x, start_y, config.font_size, config.default_text_color)
        start_y += config.font_size
        DrawText(b"Resetting your karabiner file will destroy all changes you've made",
                 start_x, start_y, config.font_size, config.default_text_color)
        start_y += config.font_size
        DrawText(b"through this app",
                 start_x, start_y, config.font_size, config.default_text_color)
        start_y += config.font_size * 2

        if KarabinerConfig().backup_exists():
            DrawingHelper.clickable_link("Reset", start_y, start_x, config.font_size, config.default_text_color, KarabinerConfig().help_blow_away_config)
        else:
            DrawText(b"(No changes have been made to your keybindings so far)",
                 start_x, start_y, config.font_size, config.default_text_color)

        start_y += config.font_size * 3
        if not self.is_updated:
            DrawText(f"Update available: {self.latest_version}".encode('utf-8'),
                     start_x, start_y, config.font_size, config.default_text_color)
            start_y += config.font_size * 2
            DrawingHelper.clickable_link("Update", start_y, start_x, config.font_size, config.default_text_color, self.update_app, [self.latest_version])

    def update_app(self, new_version):
        threading.Thread(target=background_updates, args=(new_version, self.quitting_done_flag,)).start()
        self.is_quitting = True
