from raylib import *
from config import Config
from drawing_helper import DrawingHelper
from karabiner_config import KarabinerConfig
from src.keyboard_state_controller import *
from src.modification import Modification

class ModificationChangeView():
    def __init__(self, modification_pairs, keyboard_state_controller: KeyboardStateController):
        super().__init__()
        self.karabiner_config = KarabinerConfig()
        self.modification_pairs = modification_pairs # Dict
        self.from_modification_being_edited: Modification = None
        self.to_modification_being_edited: Modification = None
        self.to_delete = None
        self.keyboard_state_controller = keyboard_state_controller

    def update_fn(self):
        if self.keyboard_state_controller.state != STATE_OVERRIDING:
            return
        # Reset
        if (self.from_modification_being_edited or self.to_modification_being_edited) and IsMouseButtonPressed(MOUSE_BUTTON_LEFT):
            self.from_modification_being_edited = False
            self.to_modification_being_edited = False
            self.keyboard_state_controller.overrides_have_stopped()
        # Set new bindings
        elif KeyboardController.removed_keys():
            if self.from_modification_being_edited:
                self.from_modification_being_edited.save()
            elif self.to_modification_being_edited:
                self.to_modification_being_edited.save()
            if self.from_modification_being_edited or self.to_modification_being_edited:
                KarabinerConfig().write_overrides(self.modification_pairs)
                self.from_modification_being_edited = None
                self.to_modification_being_edited = None
            self.keyboard_state_controller.overrides_have_stopped()
        # Editing
        elif self.from_modification_being_edited:
            self.from_modification_being_edited.update_dirty(KeyboardController.last_frame_pressed_keys)
        elif self.to_modification_being_edited:
            self.to_modification_being_edited.update_dirty(KeyboardController.last_frame_pressed_keys)

    def draw_overrides(self, start_col, start_row):
        max_from_end = 0

        # FROM modifications
        row = start_row
        col = start_col
        for override_pair in self.modification_pairs.values():
            current_modification = override_pair.modification_from
            being_edited = self.from_modification_being_edited is current_modification
            def edit_callback():
                self.from_modification_being_edited = override_pair.modification_from
                self.keyboard_state_controller.something_is_doing_overrides()

            row, width = DrawingHelper.modification_view(current_modification, being_edited, edit_callback, row, col)
            max_from_end = max(col + width + Config.generic_padding, max_from_end)

        row = start_row
        width = 0
        col = max_from_end
        for override_pair in self.modification_pairs.values():
            DrawText("->".encode('utf-8'), col, row, Config.font_size, Config.default_text_color)
            width = MeasureText(
                    "->".encode('utf-8'),
                    Config.font_size)
            row += Config.font_size

        # TO modifications
        row = start_row
        col += width + Config.generic_padding
        for override_pair in self.modification_pairs.values():
            current_modification = override_pair.modification_to
            being_edited = self.to_modification_being_edited is current_modification
            def edit_callback():
                self.to_modification_being_edited = override_pair.modification_to
                self.keyboard_state_controller.something_is_doing_overrides()

            row, width = DrawingHelper.modification_view(current_modification, being_edited, edit_callback, row, col)
            max_from_end = max(col + width + Config.generic_padding, max_from_end)

        row = start_row
        col = max_from_end
        self.to_delete = None
        for i, _ in self.modification_pairs.items():
            def edit_callback(to_del):
                self.to_delete = to_del

            DrawingHelper.clickable_link("x", col, row, Config.font_size, RED, edit_callback, [i])
            row += Config.font_size

        if self.to_delete is not None:
            KarabinerConfig().remove_override(self.to_delete)
