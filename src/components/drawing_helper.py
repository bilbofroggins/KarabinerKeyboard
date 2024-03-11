from raylib import *
from src.config import config
from src.devices.mouse_controller import MouseController
from src.logic.modification import Modification
from src.panels.click_handler import ClickHandler


class DrawingHelper:
    @staticmethod
    def is_mouse_over(mouse_x, mouse_y, x, y, width, height):
        return x <= mouse_x <= x + width and y <= mouse_y <= y + height

    @staticmethod
    def clickable_link(text, row, col, fontSize, color, callback, args=[]):
        mouse_position = GetMousePosition()
        text = text.encode('utf-8')

        DrawText(text, col, row, fontSize, color)
        width = MeasureText(text, fontSize)

        if DrawingHelper.is_mouse_over(mouse_position.x, mouse_position.y, col,
                                   row, width, fontSize):
            MouseController.set_hand_mouse(True)
            DrawLine(col, row + fontSize, col + width,
                     row + fontSize, config.default_text_color)

            ClickHandler.append(callback, args)

        return width

    @staticmethod
    def button(*, text, row, col, width, height, font_size, bg_color, text_color, callback, args=[]):
        mouse_position = GetMousePosition()
        text = text.encode('utf-8')

        DrawRectangle(col, row, width, height, bg_color)

        if DrawingHelper.is_mouse_over(
                mouse_position.x, mouse_position.y,
                col, row, width, height
        ):
            MouseController.set_hand_mouse(True)
            DrawRectangle(col, row, width, height, DARKBROWN)

            ClickHandler.append(callback, args)

        DrawText(text, col, row, font_size, text_color)

        return width

    @staticmethod
    def highlight_box(row, col, height, width, color, hovercolor, callback, args=[]):
        mouse_position = GetMousePosition()

        DrawRectangle(col, row, width, height, color)

        if DrawingHelper.is_mouse_over(mouse_position.x, mouse_position.y, col,
                                            row, width, height):
            DrawRectangle(col, row, width, height, hovercolor)
            MouseController.set_hand_mouse(True)

            ClickHandler.append(callback, args)

        return

    @staticmethod
    def modification_view(modification: Modification, being_edited, row, col, click_callback, args=[]):
        from_text = str(modification)

        if being_edited:
            if modification.edit_object.eo_currently_changing():
                DrawText(
                    str(modification.edit_object).encode('utf-8'),
                    col, row, config.font_size, RED)
                width = MeasureText(
                    str(modification.edit_object).encode('utf-8'),
                    config.font_size)
            else:
                DrawText(b"press keys...", col, row, config.font_size, RED)
                width = MeasureText(b"press keys...", config.font_size)
        else:
            width = DrawingHelper.clickable_link(from_text, row, col,
                                                 config.font_size, config.default_text_color, click_callback, args)

        row += config.font_size
        return (row, width)