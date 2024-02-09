from raylib import *
from base_panel import BaseView
from config import Config
from drawing_helper import DrawingHelper
from karabiner_config import KarabinerConfig
from src.keyboard_controller import KeyboardController
from src.modification import Modification

class ModificationChangeView(BaseView):
    def __init__(self, modification_pairs):
        super().__init__()
        self.karabiner_config = KarabinerConfig()
        self.modification_pairs = modification_pairs # Dict
        self.from_modification_being_edited: Modification = None
        self.to_modification_being_edited: Modification = None
        self.to_delete = None

    def update(self):
        # Reset
        if (self.from_modification_being_edited or self.to_modification_being_edited) and IsMouseButtonPressed(MOUSE_BUTTON_LEFT):
            self.from_modification_being_edited = False
            self.to_modification_being_edited = False
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

            row, width = DrawingHelper.modification_view(current_modification, being_edited, edit_callback, row, col)
            max_from_end = max(col + width + Config.generic_padding, max_from_end)

        # TO modifications
        row = start_row
        col = max_from_end
        for override_pair in self.modification_pairs.values():
            current_modification = override_pair.modification_to
            being_edited = self.to_modification_being_edited is current_modification
            def edit_callback():
                self.to_modification_being_edited = override_pair.modification_to

            row, width = DrawingHelper.modification_view(current_modification, being_edited, edit_callback, row, col)
            max_from_end = max(col + width + Config.generic_padding, max_from_end)

        row = start_row
        col = max_from_end
        self.to_delete = None
        for i, _ in self.modification_pairs.items():
            def edit(to_del):
                self.to_delete = to_del

            DrawingHelper.clickable_link("x", col, row, Config.font_size, RED, edit, [i])
            row += Config.font_size

        if self.to_delete is not None:
            KarabinerConfig().remove_override(self.to_delete)
