from raylib import *
from base_panel import BaseView
from config import Config

class ListPanel(BaseView):
    def __init__(self, options):
        super().__init__()
        self.options = options
        self.selected_option = b"Keyboard"
        self.font_size = 20
        self.panel_width = self.calculate_max_width()

    def calculate_max_width(self):
        max_width = 0
        for option in self.options:
            text_width = MeasureText(option, self.font_size)
            if text_width > max_width:
                max_width = text_width
        return max_width + 20  # Add some padding

    def update(self):
        if IsMouseButtonPressed(MOUSE_BUTTON_LEFT):
            mouse_position = GetMousePosition()
            # Check if a list item is clicked
            for i, option in enumerate(self.options):
                if 10 <= mouse_position.y <= 30 + i*20 and mouse_position.x <= self.panel_width:
                    self.selected_option = option
                    break

    def draw(self):
        DrawRectangle(0, 0, self.panel_width, Config.window_height, GREEN)

        for i, option in enumerate(self.options):
            if option == self.selected_option:
                DrawText(option, 10, 10 + i * 20, 20, RED)
            else:
                DrawText(option, 10, 10 + i * 20, 20, BLACK)
