import pyray as ray
from src.config import config
from src.devices.mouse_controller import MouseController
from src.logic.modification import Modification
from src.panels.click_handler import ClickHandler


class DrawingHelper:
    @staticmethod
    def is_mouse_over(mouse_x, mouse_y, x, y, width, height):
        return x <= mouse_x <= x + width and y <= mouse_y <= y + height

    @staticmethod
    def clickable_link(text, row, col, fontSize, color, callback, args=None):
        if args is None:
            args = []
        mouse_position = ray.get_mouse_position()
        text = text

        ray.draw_text(text, col, row, fontSize, color)
        width = ray.measure_text(text, fontSize)

        if DrawingHelper.is_mouse_over(mouse_position.x, mouse_position.y, col,
                                   row, width, fontSize):
            MouseController.set_hand_mouse(True)
            ray.draw_line(col, row + fontSize, col + width,
                     row + fontSize, config.default_text_color)

            ClickHandler.append(callback, args)

        return width

    @staticmethod
    def button(*, text, row, col, width, height, font_size, bg_color, text_color, callback,
               args=None):
        if args is None:
            args = []
        mouse_position = ray.get_mouse_position()
        text = text

        ray.draw_rectangle(col, row, width, height, bg_color)

        if DrawingHelper.is_mouse_over(
                mouse_position.x, mouse_position.y,
                col, row, width, height
        ):
            MouseController.set_hand_mouse(True)
            ray.get_mouse_position(col, row, width, height, ray.DARKBROWN)

            ClickHandler.append(callback, args)

        ray.draw_text(text, col, row, font_size, text_color)

        return width

    @staticmethod
    def highlight_box(row, col, height, width, color, hovercolor, callback, args=None):
        if args is None:
            args = []
        mouse_position = ray.get_mouse_position()

        ray.draw_rectangle(col, row, width, height, color)

        if DrawingHelper.is_mouse_over(mouse_position.x, mouse_position.y, col,
                                            row, width, height):
            ray.draw_rectangle(col, row, width, height, hovercolor)
            MouseController.set_hand_mouse(True)

            ClickHandler.append(callback, args)

        return

    @staticmethod
    def modification_view(modification: Modification, being_edited, row, col, click_callback,
                          args=None):
        if args is None:
            args = []
        from_text = str(modification)

        if being_edited:
            if modification.edit_object.eo_currently_changing():
                ray.draw_text(
                    str(modification.edit_object),
                    col, row, config.font_size, ray.RED)
                width = ray.measure_text(
                    str(modification.edit_object),
                    config.font_size)
            else:
                ray.draw_text("press keys...", col, row, config.font_size, ray.RED)
                width = ray.measure_text("press keys...", config.font_size)
        else:
            width = DrawingHelper.clickable_link(from_text, row, col,
                                                 config.font_size, config.default_text_color, click_callback, args)

        row += config.font_size
        return (row, width)