from raylib import *
from mouse_controller import MouseController

class DrawingHelper:
    @staticmethod
    def is_mouse_over_text(mouse_x, mouse_y, x, y, width, height):
        return x <= mouse_x <= x + width and y <= mouse_y <= y + height

    @staticmethod
    def clickable_link(text, posX, posY, fontSize, color, callback):
        mouse_position = GetMousePosition()
        text = text.encode('utf-8')

        DrawText(text, posX, posY, fontSize, color)
        width = MeasureText(text, fontSize)

        if DrawingHelper.is_mouse_over_text(mouse_position.x, mouse_position.y, posX,
                                   posY, width, fontSize):
            MouseController.set_hand_mouse(True)
            DrawLine(posX, posY + fontSize, posX + width,
                     posY + fontSize, BLACK)
            if IsMouseButtonPressed(MOUSE_BUTTON_LEFT):
                callback()

        return width
