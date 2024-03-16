from src.components.drawing_helper import DrawingHelper
from src.config import config
from src.devices.mouse_controller import MouseController
from src.logic.bundle_ids import BundleIds
from src.logic.condition import Condition
from src.logic.keyboard_state_controller import *
from src.panels.base_panel import BaseView
import pyray as ray

from src.panels.click_handler import ClickHandler


class AskView(BaseView):
    def __init__(self, mod_change_view, keyboard_state_controller):
        super().__init__()
        self.visible = False
        self.mod_pair = None
        self.keyboard_state_controller = keyboard_state_controller
        self.input_active = True
        self.frame_counter = 0
        self.search_text = ""
        self.show_results = True
        self.mod_change_view = mod_change_view
        self.background_listeners = {} # key: callback

    def message_consumer(self, message):
        if message == "close_ask_window":
            self.visible = False
            self.mod_change_view.ask_highlight = None

    def show(self, modification_pair):
        self.visible = True
        self.keyboard_state_controller.set_state(STATE_BUNDLE_SEARCH)

        self.mod_pair = modification_pair

        self.bundle_identifiers = self.mod_pair.condition.bundle_identifiers[:]
        self.include_type_str = self.mod_pair.condition.include_type_str

        self.button_width = 50
        self.window_width = 300
        self.start_col = config.window_width - 300
        self.start_col_side = self.start_col + self.button_width
        self.side_width = self.window_width - self.button_width

    def draw_toggle(self, row, col, val):
        left_color = ray.GREEN if val == 0 else ray.GRAY
        right_color = ray.RED if val == 1 else ray.GRAY

        rec_size = config.small_font_size
        ray.draw_rectangle(col - (rec_size//2), row, rec_size, rec_size, ray.GRAY)
        ray.draw_circle(col - (rec_size//2), row + (config.small_font_size//2), (config.small_font_size//2), left_color)
        ray.draw_circle(col + (rec_size//2), row + (config.small_font_size//2), (config.small_font_size//2), right_color)

        def callback():
            self.include_type_str = "frontmost_application_unless" if self.include_type_str == "frontmost_application_if" else "frontmost_application_if"

        mouse_position = ray.get_mouse_position()
        if DrawingHelper.is_mouse_over(
                mouse_position.x, mouse_position.y,
                col - (rec_size // 2) - (config.small_font_size // 2),
                row,
                rec_size + config.small_font_size,
                config.small_font_size
        ):
            MouseController.set_hand_mouse(True)
            ClickHandler.append(callback, [])

        return 1 if self.include_type_str == "frontmost_application_unless" else 0

    def draw_include_exclude(self, row):
        if self.include_type_str == "frontmost_application_unless":
            toggle_val = 1
        else:
            toggle_val = 0
        toggle_result = self.draw_toggle(row, (self.start_col_side + config.window_width)//2, toggle_val)

        ray.draw_text(
            "Include",
            self.start_col_side + config.generic_padding,
            row,
            config.small_font_size, config.left_mod_kb_color if toggle_result == 0 else ray.GRAY
        )

        exclude_width = ray.measure_text("Exclude", config.small_font_size)
        ray.draw_text(
            "Exclude",
            config.window_width - exclude_width - config.generic_padding,
            row,
            config.small_font_size, config.error_color if toggle_result == 1 else ray.GRAY
        )
        return row + config.small_font_size + config.generic_padding

    def draw_text_box(self, row):
        textbox_width = self.side_width - 100
        textbox_start_col = (self.start_col_side + config.window_width)//2 - textbox_width//2
        ray.draw_rectangle(textbox_start_col, row, textbox_width, int(config.small_font_size*1.4), ray.WHITE)
        if (self.input_active):
            ray.draw_rectangle_lines(textbox_start_col, row, textbox_width, int(config.small_font_size*1.4), ray.RED)
        else:
            ray.draw_rectangle_lines(textbox_start_col, row, textbox_width, int(config.small_font_size*1.4), ray.DARKBLUE)

        def callback():
            self.show_results = True

        mouse_position = ray.get_mouse_position()
        if DrawingHelper.is_mouse_over(
                mouse_position.x, mouse_position.y,
                textbox_start_col, row, textbox_width, int(config.small_font_size*1.4)
        ):
            ClickHandler.append(callback, [])

        padding = (config.font_size*1.4 - config.font_size)//2
        textbox_start_col = int(textbox_start_col + padding)
        row = int(row + padding)
        width = ray.measure_text(self.search_text, config.small_font_size)
        ray.draw_text(self.search_text, textbox_start_col, row, config.small_font_size, config.default_text_color)
        if self.frame_counter < 30 and self.input_active:
            ray.draw_text("|", textbox_start_col + width, row, config.small_font_size, config.default_text_color)

        if self.input_active:
            key = ray.get_char_pressed()
            # Check if more characters have been pressed on the same frame
            while key > 0:
                self.show_results = True
                if 32 <= key <= 125:
                    self.search_text += chr(key)
                key = ray.get_char_pressed()

            if ray.is_key_pressed(ray.KEY_BACKSPACE) and len(self.search_text) > 0:
                self.show_results = True
                self.search_text = self.search_text[:-1]  # Remove the last character

    def bundle_to_display(self, bundle):
        return bundle.pystring

    def draw_bundle_list(self, row):
        col = self.start_col_side + config.generic_padding
        def click_callback(index):
            if self.show_results and self.search_text:
                return
            del self.bundle_identifiers[index]
        def draw_callback(row, col, text):
            ray.draw_text(text, col, row, config.small_font_size, config.default_text_color)
        def hover_callback(row, col, text):
            ray.draw_text(text, col, row, config.small_font_size, config.error_color)

        for i, bundle in enumerate(self.bundle_identifiers):
            width = ray.measure_text(self.bundle_to_display(bundle), config.small_font_size)
            DrawingHelper.generic_clickable(
                row, col, width, config.small_font_size,
                draw_callback, hover_callback, click_callback, [i], [self.bundle_to_display(bundle)]
            )
            row += config.small_font_size + config.small_padding

    def search(self, search_text):
        apps = BundleIds().fuzzy_search(search_text)
        return apps

    def background_click_callback(self):
        self.show_results = False

    def draw_search_results(self, row):
        if 'ask_view_search_results' not in self.background_listeners:
            self.background_listeners['ask_view_search_results'] = self.background_click_callback

        if not self.show_results or not self.search_text:
            return
        width = self.side_width - 50
        box_start_col = (self.start_col_side + config.window_width)//2 - width//2

        def click_callback(app):
            bundle = app.bundle()
            # TODO: Let the user know something is wrong, preferably don't show it in the fitst place
            if bundle == None:
                return

            self.search_text = ""
            self.bundle_identifiers.append(app.bundle())
        def draw_callback(row, col):
            ray.draw_rectangle(col, row, width, config.small_font_size * 2, ray.LIGHTGRAY)
        def hover_callback(row, col):
            ray.draw_rectangle(col, row, width, config.small_font_size*2, DrawingHelper.brighten(ray.LIGHTGRAY))

        apps = self.search(self.search_text)
        for app in apps:
            DrawingHelper.generic_clickable(
                row, box_start_col, width, config.small_font_size*2,
                draw_callback, hover_callback, click_callback, [app]
            )
            row = int(row + (config.small_font_size) - config.small_font_size // 2)
            col = box_start_col + config.small_padding
            ray.draw_text(app.name, col, row, config.small_font_size, ray.DARKBLUE)
            row += config.small_font_size*2 + config.small_padding

    def draw_save_button(self):
        width = 100
        col = (self.start_col_side + config.window_width)//2 - width//2
        height = 30
        row = config.window_height - 100

        def draw_callback(row, col):
            ray.draw_rectangle(col, row, width, height, config.ask_save_color)
        def hover_callback(row, col):
            ray.draw_rectangle(col, row, width, height, DrawingHelper.brighten(config.ask_save_color))
        def click_callback():
            if len(self.bundle_identifiers) and not self.include_type_str:
                self.include_type_str = "frontmost_application_if"
            condition = Condition(self.bundle_identifiers, self.include_type_str)
            self.mod_pair.condition = condition
            self.mod_change_view.save()
            self.mod_change_view.ask_highlight = None
            self.keyboard_state_controller.set_state(STATE_LOCKED)
            self.visible = False

        DrawingHelper.generic_clickable(
            row, col, width, height,
            draw_callback, hover_callback, click_callback
        )
        row = int(row + (height // 2) - config.small_font_size//2)
        col = int(col + (width // 2) - ray.measure_text("Save", config.small_font_size)//2)
        ray.draw_text("Save", col, row, config.small_font_size, ray.WHITE)

    def draw(self):
        if not self.visible:
            return
        self.frame_counter += 1
        if self.frame_counter > 60:
            self.frame_counter = 0

        def background_click():
            for callback in self.background_listeners.values():
                callback()

        ray.draw_rectangle(self.start_col, 0, config.window_width, config.window_height, ray.ORANGE)
        mouse_position = ray.get_mouse_position()
        if DrawingHelper.is_mouse_over(
                mouse_position.x, mouse_position.y,
                self.start_col, 0,
                config.window_width, config.window_height
        ):
            ClickHandler.append(background_click, [])

        def draw_callback(row, col):
            ray.draw_rectangle(col, row, self.button_width, config.window_height, config.ask_highlight_color)
        def hover_callback(row, col):
            ray.draw_rectangle(col, row, self.button_width, config.window_height, DrawingHelper.brighten(config.ask_highlight_color))
        def click_callback():
            self.visible = False
            self.keyboard_state_controller.set_state(STATE_LOCKED)
            self.mod_change_view.ask_highlight = None
        # Close Button
        DrawingHelper.generic_clickable(
            0, self.start_col, self.button_width, config.window_height,
            draw_callback,
            hover_callback,
            click_callback
        )
        arrow_width = ray.measure_text(">", config.large_font_size)
        ray.draw_text(
            ">",
            self.start_col + (self.button_width//2) - (arrow_width//2),
            config.window_height//2 - (arrow_width//2),
            config.large_font_size, config.default_text_color
        )

        text_width = ray.measure_text("Application Specific Keybinding", config.small_font_size)
        ray.draw_text(
            "Application Specific Keybinding",
            self.start_col_side + (self.side_width//2) - (text_width // 2),
            config.generic_padding,
            config.small_font_size, config.default_text_color
        )

        row = self.draw_include_exclude(config.generic_padding*2 + config.small_font_size)

        text_width = ray.measure_text("For applications", config.small_font_size)
        ray.draw_text(
            "For applications:",
            (self.side_width//2) + self.start_col_side - text_width//2,
            row,
            config.small_font_size,
            config.default_text_color
        )
        row += config.small_font_size + config.small_padding

        self.draw_text_box(row)
        row += int(config.small_font_size*1.4) + config.generic_padding
        self.draw_bundle_list(row)
        self.draw_search_results(row)
        self.draw_save_button()