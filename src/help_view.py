from raylib import *
from base_panel import BaseView
from config import Config
from drawing_helper import DrawingHelper
from karabiner_config import KarabinerConfig


class HelpView(BaseView):
    def __init__(self):
        super().__init__()

    def update(self):
        pass

    def draw_help(self, start_x, start_y):
        DrawText(b"This application is pre-alpha and may screw up your karabiner file",
                 start_x, start_y, Config.font_size, BLACK)
        start_y += Config.font_size
        DrawText(b"We save a copy of your karabiner config file before we make changes to it",
                 start_x, start_y, Config.font_size, BLACK)
        start_y += Config.font_size
        DrawText(b"Resetting your karabiner file will destroy all changes you've made through this app",
                 start_x, start_y, Config.font_size, BLACK)
        start_y += Config.font_size * 2

        if KarabinerConfig().backup_exists():
            DrawingHelper.clickable_link("Reset", start_x, start_y, Config.font_size, BLACK, KarabinerConfig().help_blow_away_config)
        else:
            DrawText(b"(No changes have been made to your keybindings so far)",
                 start_x, start_y, Config.font_size, BLACK)
