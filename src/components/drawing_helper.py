import pyray as ray
from src.config import config
from src.devices.mouse_controller import MouseController
from src.logic.key_mappings import *
from src.logic.modification import Modification
from src.panels.click_handler import ClickHandler
import src.panels.global_vars as g


class DrawingHelper:
    @staticmethod
    def is_mouse_over(mouse_x, mouse_y, x, y, width, height):
        return x <= mouse_x <= x + width and y <= mouse_y <= y + height

    @staticmethod
    def clickable_link(text, row, col, fontSize, color, callback, args=None):
        if args is None:
            args = []
        mouse_position = ray.get_mouse_position()

        if set(text) & g.unicode_chars:
            ray.draw_text_ex(g.special_font[0], text, (col, row), fontSize, 1, color)
        else:
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
    def brighten(color):
        ret = list(color)
        for i in range(0, 3):
            ret[i] = min(255, color[i] + 100)

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
    def modification_link(modification: Modification, row, col, font_size, color, click_callback, args=None):
        og_col = col
        if args is None:
            args = []

        def draw_mod(mod):
            nonlocal col
            kb_begin_text = mod[:5]
            if kb_begin_text == 'left_' and mod != "left_arrow":
                char_color = config.left_mod_color
            elif kb_begin_text == 'right' and mod != "right_arrow":
                char_color = config.right_mod_color
            else:
                char_color = config.default_text_color

            if mod:
                text = rl_to_display_key_map[kb_to_rl_key_map[mod]]
            if mod in kb_to_rl_key_map and kb_to_rl_key_map[mod] in special_chars:
                ray.draw_text_codepoint(g.special_font[0], ord(text), (col, row),
                                        font_size, char_color)
                col += font_size
            elif mod:
                ray.draw_text(text, col, row, font_size, char_color)
                col += ray.measure_text(text, font_size) + config.small_padding

        def draw_delimiter():
            nonlocal col
            col += int(font_size * 0.2)
            ray.draw_text_codepoint(g.special_font[0], ord('·'), (col, row),
                                    font_size, config.delimiter_color)
            col += int(font_size * 0.7)

        for i, mod in enumerate(modification.modifiers):
            draw_mod(mod)
            if i < len(modification.modifiers):
                draw_delimiter()

        draw_mod(modification.key)

        mouse_position = ray.get_mouse_position()
        if DrawingHelper.is_mouse_over(mouse_position.x, mouse_position.y, og_col, row, col - og_col, font_size):
            MouseController.set_hand_mouse(True)
            ray.draw_line(og_col, row + font_size, col,
                     row + font_size, config.default_text_color)

            ClickHandler.append(click_callback, args)

        col += config.generic_padding

        return col - og_col

    @staticmethod
    def modification_view(modification: Modification, being_edited, row, col, click_callback,
                          args=None):
        if args is None:
            args = []

        if being_edited:
            if modification.edit_object.eo_currently_changing():
                width = DrawingHelper.modification_link(modification.edit_object, row, col, config.font_size, ray.RED, click_callback, args)
            else:
                ray.draw_text("press keys...", col, row, config.font_size, ray.RED)
                width = ray.measure_text("press keys...", config.font_size)
        else:
            width = DrawingHelper.modification_link(modification, row, col, config.font_size, ray.BLACK, click_callback, args)

        row += config.font_size
        return (row, width)