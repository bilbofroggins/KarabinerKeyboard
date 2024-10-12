import pyray as ray
from src.config import config
from src.devices.mouse_controller import MouseController
from src.logic.key_mappings import *
from src.panels.click_handler import ClickHandler
import src.panels.global_vars as g


class DrawingHelper:
    @staticmethod
    def is_mouse_over(mouse_x, mouse_y, x, y, width, height):
        return x <= mouse_x <= x + width and y <= mouse_y <= y + height

    @staticmethod
    def measure_unicode_plus_text(text, font_size):
        col_offset = 0
        for char in text:
            if char in g.unicode_chars:
                char_width = int(ray.measure_text_ex(g.special_font[0], char, font_size, 1).x)
            else:
                char_width = ray.measure_text(char, font_size)
            col_offset += char_width + config.small_padding
        return col_offset

    @staticmethod
    def draw_unicode_plus_text(text, row, col, font_size, color):
        col_offset = 0
        for char in text:
            if char in g.unicode_chars:
                ray.draw_text_ex(g.special_font[0], char, (col + col_offset, row), font_size,
                                 1, color)
                char_width = int(ray.measure_text_ex(g.special_font[0], char, font_size, 1).x)
            else:
                ray.draw_text(char, col + col_offset, row, font_size, color)
                char_width = ray.measure_text(char, font_size)
            col_offset += char_width + config.small_padding
        return col_offset

    @staticmethod
    def clickable_link(text, row, col, fontSize, color, callback, args=None):
        if args is None:
            args = []
        mouse_position = ray.get_mouse_position()

        width = DrawingHelper.draw_unicode_plus_text(text, row, col, fontSize, color)

        if DrawingHelper.is_mouse_over(mouse_position.x, mouse_position.y, col,
                                   row, width, fontSize):
            MouseController.set_hand_mouse(True)
            ray.draw_line(col, row + fontSize, col + width,
                     row + fontSize, config.default_text_color)

            ClickHandler.append(callback, args)

        return width

    @staticmethod
    def brighten(color, amount=100):
        if type(color) == tuple:
            ret = list(color)
        else:
            ret = color.to_tuple()
        for i in range(0, 3):
            ret[i] = min(255, color[i] + amount)

        return ret

    @staticmethod
    def make_transparent(color, amount=100):
        if type(color) == tuple:
            ret = list(color)
        else:
            ret = color.to_tuple()
        ret[3] = max(0, color[3] - amount)

        return ret

    @staticmethod
    def generic_clickable(row, col, width, height, draw_callback, hover_callback, click_callback, click_args=None, draw_args=None):
        if click_args is None:
            click_args = []
        if draw_args is None:
            draw_args = []
        mouse_position = ray.get_mouse_position()

        if DrawingHelper.is_mouse_over(mouse_position.x, mouse_position.y, col,
                                   row, width, height):
            MouseController.set_hand_mouse(True)
            if len(draw_args):
                hover_callback(row, col, *draw_args)
            else:
                hover_callback(row, col)
            ClickHandler.append(click_callback, click_args)
        else:
            if len(draw_args):
                draw_callback(row, col, *draw_args)
            else:
                draw_callback(row, col)

    @staticmethod
    def button(text, pressed, row, col, font_size, click_callback, click_args=None):
        text_width = ray.measure_text(text, font_size)

        def draw_callback(row, col):
            ray.draw_rectangle(col, row,
                               text_width + config.small_padding * 2,
                               font_size + config.small_padding * 2,
                               config.button_color)
            ray.draw_text(text, col + config.small_padding, row + config.small_padding, font_size,
                          config.default_text_color)
        def hover_callback(row, col):
            ray.draw_rectangle(col, row,
                               text_width + config.small_padding * 2,
                               font_size + config.small_padding * 2,
                               DrawingHelper.brighten(config.button_color))
            ray.draw_text(text, col + config.small_padding, row + config.small_padding, font_size,
                          DrawingHelper.brighten(config.default_text_color))

        DrawingHelper.generic_clickable(
            row, col,
            text_width + config.small_padding*2, font_size + config.small_padding*2,
            hover_callback if pressed else draw_callback, hover_callback, click_callback, click_args
        )
        return text_width + config.small_padding*2