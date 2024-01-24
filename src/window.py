from raylib import *
from list_panel import ListPanel
from content_panel import ContentPanel
from mouse_controller import MouseController
from registry import panel_registry
from config import Config

class MyApp:
    def __init__(self):
        title = "Karabiner Keyboard"
        InitWindow(Config.window_width, Config.window_height, title.encode('utf-8'))
        SetTargetFPS(60)
        self.list_panel = ListPanel()
        self.content_panel = ContentPanel(self.list_panel)

    def run(self):
        while not WindowShouldClose():
            for panel in panel_registry:
                panel.update()

            BeginDrawing()
            ClearBackground(RAYWHITE)

            for panel in panel_registry:
                panel.draw()

            MouseController.draw()

            EndDrawing()

        CloseWindow()
