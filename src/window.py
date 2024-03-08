from raylib import *

from src.devices.keyboard_controller import KeyboardController
from src.devices.mouse_controller import MouseController
from src.logic.bundle_ids import BundleIds
from src.panels.list_panel import ListPanel
from src.panels.content_panel import ContentPanel
from src.panels.panel_registry import panel_registry
from config import config


class MyApp:
    def __init__(self):
        title = "Karabiner Keyboard"
        InitWindow(config.window_width, config.window_height, title.encode('utf-8'))
        SetTargetFPS(60)
        SetExitKey(KEY_NULL)
        self.list_panel = ListPanel()
        self.content_panel = ContentPanel(self.list_panel)
        BundleIds()

    def run(self):
        while not WindowShouldClose():
            KeyboardController.update()

            for panel in panel_registry:
                panel.update()

            BeginDrawing()
            ClearBackground(RAYWHITE)

            for panel in panel_registry:
                panel.draw()

            MouseController.draw()

            EndDrawing()

        CloseWindow()
