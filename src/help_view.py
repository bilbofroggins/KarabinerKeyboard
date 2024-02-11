import threading

from raylib import *
from versions.version import __version__

from base_panel import BaseView
from config import Config
from drawing_helper import DrawingHelper
from karabiner_config import KarabinerConfig
from src.versions.updates import *


class HelpView(BaseView):
    def __init__(self):
        super().__init__()
        self.script_path, self.dir_path = "", ""
        threading.Thread(target=self.check_updates, daemon=True).start()

    def check_updates(self):
        self.is_updated, self.latest_version = check_up_to_date()

    def draw_help(self, start_x, start_y):
        DrawText(f"Version: {__version__}".encode('utf-8'),
                 start_x, start_y, Config.font_size, BLACK)
        start_y += Config.font_size
        DrawText(b"This application is pre-alpha and may screw up your karabiner file",
                 start_x, start_y, Config.font_size, BLACK)
        start_y += Config.font_size
        DrawText(b"We save a copy of your karabiner config file before we make changes to it",
                 start_x, start_y, Config.font_size, BLACK)
        start_y += Config.font_size
        DrawText(b"Resetting your karabiner file will destroy all changes you've made",
                 start_x, start_y, Config.font_size, BLACK)
        start_y += Config.font_size
        DrawText(b"through this app",
                 start_x, start_y, Config.font_size, BLACK)
        start_y += Config.font_size * 2

        if KarabinerConfig().backup_exists():
            DrawingHelper.clickable_link("Reset", start_x, start_y, Config.font_size, BLACK, KarabinerConfig().help_blow_away_config)
        else:
            DrawText(b"(No changes have been made to your keybindings so far)",
                 start_x, start_y, Config.font_size, BLACK)

        start_y += Config.font_size * 4
        if not self.is_updated:
            DrawText(f"Update available: {self.latest_version}".encode('utf-8'),
                     start_x, start_y, Config.font_size, BLACK)
            start_y += Config.font_size * 2
            DrawingHelper.clickable_link("Update", start_x, start_y, Config.font_size, BLACK, update_app, [self.latest_version])
