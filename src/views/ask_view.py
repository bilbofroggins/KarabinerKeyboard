from src.components.drawing_helper import DrawingHelper
from src.config import config
from src.devices.mouse_controller import MouseController
from src.logic.bundle_ids import BundleIds
from src.logic.condition import Condition
from src.logic.keyboard_state_controller import *
from src.panels.base_panel import BaseView
from raylib import *


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
        self.clicked_input = False
        self.mod_change_view = mod_change_view

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
        left_color = GREEN if val == 0 else GRAY
        right_color = RED if val == 1 else GRAY

        rec_size = config.small_font_size
        DrawRectangle(col - (rec_size//2), row, rec_size, rec_size, GRAY)
        DrawCircle(col - (rec_size//2), row + (config.small_font_size//2), (config.small_font_size//2), left_color)
        DrawCircle(col + (rec_size//2), row + (config.small_font_size//2), (config.small_font_size//2), right_color)

        mouse_position = GetMousePosition()
        if DrawingHelper.is_mouse_over(
                mouse_position.x, mouse_position.y,
                col - (rec_size // 2) - (config.small_font_size // 2),
                row,
                rec_size + config.small_font_size,
                config.small_font_size
        ):
            MouseController.set_hand_mouse(True)
            if IsMouseButtonPressed(MOUSE_BUTTON_LEFT):
                self.include_type_str = "frontmost_application_unless" if self.include_type_str == "frontmost_application_if" else "frontmost_application_if"

        return 1 if self.include_type_str == "frontmost_application_unless" else 0

    def draw_include_exclude(self, row):
        if self.include_type_str == "frontmost_application_unless":
            toggle_val = 1
        else:
            toggle_val = 0
        toggle_result = self.draw_toggle(row, (self.start_col_side + config.window_width)//2, toggle_val)

        DrawText(
            "Include".encode('utf-8'),
            self.start_col_side + config.generic_padding,
            row,
            config.small_font_size, GREEN if toggle_result == 0 else GRAY
        )

        exclude_width = MeasureText("Exclude".encode('utf-8'), config.small_font_size)
        DrawText(
            "Exclude".encode('utf-8'),
            config.window_width - exclude_width - config.generic_padding,
            row,
            config.small_font_size, RED if toggle_result == 1 else GRAY
        )
        return row + config.small_font_size + config.generic_padding

    def draw_text_box(self, row):
        self.clicked_input = False
        textbox_width = self.side_width - 100
        textbox_start_col = (self.start_col_side + config.window_width)//2 - textbox_width//2
        DrawRectangle(textbox_start_col, row, textbox_width, int(config.small_font_size*1.4), WHITE)
        if (self.input_active):
            DrawRectangleLines(textbox_start_col, row, textbox_width, int(config.small_font_size*1.4), RED)
        else:
            DrawRectangleLines(textbox_start_col, row, textbox_width, int(config.small_font_size*1.4), DARKBLUE)

        mouse_position = GetMousePosition()
        if DrawingHelper.is_mouse_over(
                mouse_position.x, mouse_position.y,
                textbox_start_col, row, textbox_width, int(config.small_font_size*1.4)
        ):
            if IsMouseButtonPressed(MOUSE_BUTTON_LEFT):
                self.clicked_input = True
                self.show_results = True

        padding = (config.font_size*1.4 - config.font_size)//2
        textbox_start_col = int(textbox_start_col + padding)
        row = int(row + padding)
        width = MeasureText(self.search_text.encode('utf-8'), config.small_font_size)
        DrawText(self.search_text.encode('utf-8'), textbox_start_col, row, config.small_font_size, config.default_text_color)
        if self.frame_counter < 30 and self.input_active:
            DrawText(b"|", textbox_start_col + width, row, config.small_font_size, config.default_text_color)

        if self.input_active:
            key = GetCharPressed()
            # Check if more characters have been pressed on the same frame
            while key > 0:
                self.show_results = True
                if 32 <= key <= 125:
                    self.search_text += chr(key)
                key = GetCharPressed()

            if IsKeyPressed(KEY_BACKSPACE) and len(self.search_text) > 0:
                self.show_results = True
                self.search_text = self.search_text[:-1]  # Remove the last character

    def bundle_to_display(self, bundle):
        return bundle.pystring

    def draw_bundle_list(self, row):
        def callback(index):
            if self.show_results and self.search_text:
                return
            del self.bundle_identifiers[index]

        for i, bundle in enumerate(self.bundle_identifiers):
            DrawingHelper.clickable_link(
                self.bundle_to_display(bundle),
                row,
                self.start_col_side + config.generic_padding,
                config.small_font_size,
                config.default_text_color,
                callback,
                [i]
            )
            row += config.small_font_size + config.small_padding

    def search(self, search_text):
        apps = BundleIds().fuzzy_search(search_text)
        return apps

    def draw_search_results(self, row):
        if not self.show_results or not self.search_text:
            return
        width = self.side_width - 50
        box_start_col = (self.start_col_side + config.window_width)//2 - width//2

        has_clicked = False
        def callback(app):
            bundle = app.bundle()
            # TODO: Let the user know something is wrong, preferably don't show it in the fitst place
            if bundle == None:
                return

            nonlocal has_clicked
            has_clicked = True
            self.search_text = ""
            self.bundle_identifiers.append(app.bundle())

        apps = self.search(self.search_text)
        for app in apps:
            DrawingHelper.button(
                text=app.name,
                row=row,
                col=box_start_col,
                width=width,
                height=config.small_font_size*2,
                font_size=config.small_font_size,
                bg_color=LIGHTGRAY,
                text_color=DARKBLUE,
                callback=callback,
                args=[app]
            )
            row += config.small_font_size*2 + config.small_padding

        if not has_clicked and not self.clicked_input and IsMouseButtonPressed(MOUSE_BUTTON_LEFT):
            self.show_results = False

    def draw_save_button(self):
        def save():
            condition = Condition(self.bundle_identifiers, self.include_type_str)
            self.mod_pair.condition = condition
            self.mod_change_view.save()
            self.mod_change_view.ask_highlight = None
            self.visible = False

        width = 200
        col = (self.start_col_side + config.window_width)//2 - width//2
        DrawingHelper.button(
            text="Save",
            row=config.window_height - 100,
            col=col,
            width=width,
            height=50,
            font_size=config.small_font_size,
            bg_color=BLUE,
            text_color=WHITE,
            callback=save
        )

    def draw(self):
        if not self.visible:
            return
        self.frame_counter += 1
        if self.frame_counter > 60:
            self.frame_counter = 0

        def close_ask_window():
            self.visible = False
            self.keyboard_state_controller.set_state(STATE_LOCKED)
            self.mod_change_view.ask_highlight = None

        DrawRectangle(self.start_col, 0, config.window_width, config.window_height, ORANGE)

        # Close Button
        DrawingHelper.highlight_box(0, self.start_col, config.window_height, self.button_width, PURPLE, BLUE, close_ask_window)
        arrow_width = MeasureText(">".encode('utf-8'), config.large_font_size)
        DrawText(
            ">".encode('utf-8'),
            self.start_col + (self.button_width//2) - (arrow_width//2),
            config.window_height//2 - (arrow_width//2),
            config.large_font_size, config.default_text_color
        )

        text_width = MeasureText("Application Specific Keybinding".encode('utf-8'), config.small_font_size)
        DrawText(
            "Application Specific Keybinding".encode('utf-8'),
            self.start_col_side + (self.side_width//2) - (text_width // 2),
            config.generic_padding,
            config.small_font_size, config.default_text_color
        )

        row = self.draw_include_exclude(config.generic_padding*2 + config.small_font_size)

        text_width = MeasureText("For applications".encode('utf-8'), config.small_font_size)
        DrawText(
            "For applications:".encode('utf-8'),
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