from raylib import *
from list_panel import ListPanel
from content_panel import ContentPanel
from registry import panel_registry
from config import Config

class MyApp:
    def __init__(self):
        title = "Karabiner Keyboard"
        InitWindow(Config.window_width, Config.window_height, title.encode('utf-8'))
        SetTargetFPS(60)
        self.list_panel = ListPanel([b"Keyboard", b"Overrides"])
        self.content_panel = ContentPanel(self.list_panel)

    def run(self):
        while not WindowShouldClose():
            for panel in panel_registry:
                panel.update()

            BeginDrawing()
            ClearBackground(RAYWHITE)

            for panel in panel_registry:
                panel.draw()

            EndDrawing()

        CloseWindow()
