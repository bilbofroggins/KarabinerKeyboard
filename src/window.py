import sys

import pyray as ray

from src.devices.keyboard_controller import KeyboardController
from src.devices.mouse_controller import MouseController
from src.logic.bundle_ids import BundleIds
from src.panels.click_handler import handle_clicks
from src.panels.list_panel import ListPanel
from src.panels.content_panel import ContentPanel
from src.panels.global_vars import panel_registry, special_font
from config import config


class MyApp:
    def __init__(self):
        title = "Karabiner Keyboard"
        ray.init_window(config.window_width, config.window_height, title)
        ray.set_target_fps(60)
        ray.set_exit_key(ray.KEY_NULL)

        font_chars = [
            ord('?'), ord('⌫'),ord('⇥'),ord('⇪'),ord('↵'),ord('⇧'),ord('⇧'),ord('␣'),ord('⌘'),ord('⌘'),
            ord('⌥'),ord('⌥'),ord('⌃'),ord('⌃'),ord('←'),ord('↑'),ord('↓'),ord('→'),ord('⇱'),
            ord('⇞'),ord('⌦'),ord('⇲'),ord('⇟'),ord('⇭'),ord('·')
        ]
        special_font.append(ray.load_font_ex("../resources/DejaVuSans.ttf", 48, font_chars, len(font_chars)))

        self.list_panel = ListPanel()
        self.content_panel = ContentPanel(self.list_panel)
        BundleIds()

    def run(self):
        while not ray.window_should_close():
            KeyboardController.update()

            for panel in panel_registry:
                panel.update()

            ray.begin_drawing()
            ray.clear_background(ray.RAYWHITE)

            for panel in panel_registry:
                panel.draw()

            MouseController.draw()
            handle_clicks()

            ray.end_drawing()

        ray.close_window()
