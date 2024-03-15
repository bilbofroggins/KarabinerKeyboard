import pyray as ray
from src.components.drawing_helper import DrawingHelper
from src.config import config
from src.logic.condition import Condition
from src.logic.karabiner_config import KarabinerConfig
from src.logic.keyboard_state_controller import *
from src.logic.modification import Modification
from src.logic.modification_pair import ModificationPair
from src.panels.click_handler import ClickHandler
from src.views.ask_view import AskView


class ModificationChangeView():
    def __init__(self, modification_pairs, keyboard_state_controller: KeyboardStateController):
        super().__init__()
        self.modification_pairs = modification_pairs # Dict
        self.from_modification_being_edited: Modification = None
        self.to_modification_being_edited: Modification = None
        self.keyboard_state_controller = keyboard_state_controller
        self.new_modification = Modification()
        self.ask_view = AskView(self, keyboard_state_controller)
        self.ask_highlight = None
        self.background_listeners = {} # key: callback

    def background_click_callback(self):
        if self.from_modification_being_edited or self.to_modification_being_edited:
            self.from_modification_being_edited = False
            self.to_modification_being_edited = False
            self.keyboard_state_controller.overrides_have_stopped()

    def update_fn(self):
        if 'mod_change_view' not in self.background_listeners:
            self.background_listeners['mod_change_view'] = self.background_click_callback

        if self.keyboard_state_controller.state != STATE_OVERRIDING:
            return
        # Set new bindings
        if KeyboardController.removed_keys():
            if self.from_modification_being_edited:
                self.from_modification_being_edited.save()
            elif self.to_modification_being_edited:
                self.to_modification_being_edited.save()
            if self.from_modification_being_edited or self.to_modification_being_edited:
                if self.to_modification_being_edited == self.new_modification:
                    new_pair = ModificationPair(self.keyboard_state_controller.locked_Modification, self.new_modification, Condition())
                    self.modification_pairs['new_obj'] = new_pair
                self.save()
                self.new_modification.reset()
                self.from_modification_being_edited = None
                self.to_modification_being_edited = None
            self.keyboard_state_controller.overrides_have_stopped()
        # Editing
        elif self.from_modification_being_edited:
            self.from_modification_being_edited.update_dirty(KeyboardController.last_frame_pressed_keys)
        elif self.to_modification_being_edited:
            self.to_modification_being_edited.update_dirty(KeyboardController.last_frame_pressed_keys)

    def save(self):
        KarabinerConfig().write_overrides(self.modification_pairs)

    def draw_instructions(self, row, col):
        text = "Press keys and hold to rebind..."
        ray.draw_text(text, col, row, config.font_size, config.default_text_color)

    def draw_add_row(self, row, col):
        being_edited = self.to_modification_being_edited is self.new_modification

        def edit_callback():
            self.to_modification_being_edited = self.new_modification
            self.keyboard_state_controller.something_is_doing_overrides()

        width = DrawingHelper.modification_link(self.keyboard_state_controller.locked_Modification, row, col, config.font_size, ray.BLACK, edit_callback)
        ray.draw_text("->", col + width, row, config.font_size,
                 config.default_text_color)
        width += ray.measure_text(
            "->",
            config.font_size) + config.generic_padding

        if self.to_modification_being_edited == self.new_modification:
            DrawingHelper.modification_view(self.new_modification, being_edited,
                                            row, col + width, edit_callback)
        else:
            DrawingHelper.clickable_link("Add new binding...", row, col + width, config.font_size, ray.PURPLE, edit_callback)

    def open_ask_panel(self, mod_pair):
        self.ask_view.show(mod_pair)

    def draw_overrides(self, start_row, start_col):
        def background_click():
            for callback in self.background_listeners.values():
                callback()
        mouse_position = ray.get_mouse_position()
        if DrawingHelper.is_mouse_over(
                mouse_position.x, mouse_position.y,
                start_col, start_row,
                config.window_width, config.window_height
        ):
            ClickHandler.append(background_click, [])

        if not len(self.modification_pairs) and self.keyboard_state_controller.state not in (STATE_IS_PRESSING, STATE_LOCKED, STATE_OVERRIDING):
            self.draw_instructions(start_row, start_col)
            return
        max_from_end = 0

        if self.ask_highlight:
            ray.draw_rectangle(start_col, self.ask_highlight, config.window_width, config.font_size, ray.PURPLE)

        # FROM modifications
        row = start_row
        col = start_col
        for override_pair in self.modification_pairs.values():
            current_modification = override_pair.modification_from
            being_edited = self.from_modification_being_edited is current_modification
            def edit_callback(ov_pair):
                self.from_modification_being_edited = ov_pair.modification_from
                self.keyboard_state_controller.something_is_doing_overrides()

            row, width = DrawingHelper.modification_view(current_modification, being_edited, row, col, edit_callback, [override_pair])
            max_from_end = max(col + width + config.generic_padding, max_from_end)

        row = start_row
        width = 0
        col = max_from_end
        for override_pair in self.modification_pairs.values():
            ray.draw_text("->", col, row, config.font_size, config.default_text_color)
            width = ray.measure_text(
                    "->",
                    config.font_size)
            row += config.font_size

        # TO modifications
        row = start_row
        col += width + config.generic_padding
        for override_pair in self.modification_pairs.values():
            current_modification = override_pair.modification_to
            being_edited = self.to_modification_being_edited is current_modification
            def edit_callback(ov_pair):
                self.to_modification_being_edited = ov_pair.modification_to
                self.keyboard_state_controller.something_is_doing_overrides()

            row, width = DrawingHelper.modification_view(current_modification, being_edited, row, col, edit_callback, [override_pair])
            max_from_end = max(col + width + config.generic_padding, max_from_end)

        row = start_row
        col = max_from_end
        for i, _ in self.modification_pairs.items():
            ray.draw_text(" ::", col, row, config.font_size, config.default_text_color)
            width = ray.measure_text(" ::", config.font_size)
            row += config.font_size
        max_from_end = max(col + width + config.generic_padding, max_from_end)

        row = start_row
        col = max_from_end
        for i, mod_pair in self.modification_pairs.items():
            def ask_callback(row, inner_mod_pair):
                self.open_ask_panel(inner_mod_pair)
                self.ask_highlight = row

            width = DrawingHelper.clickable_link("ASK", row, col, config.font_size, mod_pair.condition.color(), ask_callback, [row, mod_pair])
            row += config.font_size
        max_from_end = max(col + width + config.generic_padding, max_from_end)

        row = start_row
        col = max_from_end
        for i, _ in self.modification_pairs.items():
            def edit_callback(to_del):
                KarabinerConfig().remove_override(to_del)

            DrawingHelper.clickable_link("x", row, col, config.font_size, ray.RED, edit_callback, [i])
            row += config.font_size

        return row