from raylib import *
from mouse_controller import MouseController
from src.config import Config
from src.modification import Modification


class DrawingHelper:
    @staticmethod
    def is_mouse_over_text(mouse_x, mouse_y, x, y, width, height):
        return x <= mouse_x <= x + width and y <= mouse_y <= y + height

    @staticmethod
    def clickable_link(text, posX, posY, fontSize, color, callback, args=[]):
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
                callback(*args) if len(args) else callback()

        return width

    def modification_view(modification: Modification, being_edited, click_callback, row, col):
        from_text = str(modification)

        if being_edited:
            if modification.edit_object.currently_changing():
                DrawText(
                    str(modification.edit_object).encode('utf-8'),
                    col, row, Config.font_size, RED)
                width = MeasureText(
                    str(modification.edit_object).encode('utf-8'),
                    Config.font_size)
            else:
                DrawText(b"press keys...", col, row, Config.font_size, RED)
                width = MeasureText(b"press keys...", Config.font_size)
        else:
            width = DrawingHelper.clickable_link(from_text, col, row,
                                                 Config.font_size, BLACK, click_callback)

        row += Config.font_size
        return (row, width)