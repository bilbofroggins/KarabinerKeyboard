from raylib import *
from base_panel import BaseView
from config import Config
from drawing_helper import DrawingHelper
from karabiner_config import KarabinerConfig
from src.keyboard_controller import KeyboardController
from src.modification import Modification


class OverridesView(BaseView):
    def __init__(self):
        super().__init__()
        self.karabiner_config = KarabinerConfig()
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
                KarabinerConfig().write_overrides()
                self.from_modification_being_edited = None
                self.to_modification_being_edited = None
        # Editing
        elif self.from_modification_being_edited:
            self.from_modification_being_edited.update_dirty(KeyboardController.last_frame_pressed_keys)
        elif self.to_modification_being_edited:
            self.to_modification_being_edited.update_dirty(KeyboardController.last_frame_pressed_keys)

    def draw_overrides(self, start_x, start_y):
        max_from_end = 0
        max_to_end = 0

        row_pixels = start_y
        for override_pair in self.karabiner_config.modification_pairs:
            from_text = str(override_pair.modification_from)

            def edit():
                self.from_modification_being_edited = override_pair.modification_from

            if self.from_modification_being_edited is override_pair.modification_from:
                if self.from_modification_being_edited.edit_object.being_edited():
                    DrawText(str(self.from_modification_being_edited.edit_object).encode('utf-8'), start_x, row_pixels, Config.font_size, RED)
                    width = MeasureText(str(self.from_modification_being_edited.edit_object).encode('utf-8'), Config.font_size)
                else:
                    DrawText(b"press keys...", start_x, row_pixels, Config.font_size, RED)
                    width = MeasureText(b"press keys...", Config.font_size)
            else:
                width = DrawingHelper.clickable_link(from_text, start_x, row_pixels, Config.font_size, BLACK, edit)

            max_from_end = max(start_x + width + Config.generic_padding, max_from_end)
            row_pixels += Config.font_size

        row_pixels = start_y

        for override_pair in self.karabiner_config.modification_pairs:
            to_text = str(override_pair.modification_to)

            def edit():
                self.to_modification_being_edited = override_pair.modification_to

            if self.to_modification_being_edited is override_pair.modification_to:
                if self.to_modification_being_edited.edit_object.being_edited():
                    DrawText(str(self.to_modification_being_edited.edit_object).encode('utf-8'), max_from_end, row_pixels, Config.font_size, RED)
                    width = MeasureText(str(self.to_modification_being_edited.edit_object).encode('utf-8'), Config.font_size)
                else:
                    DrawText(b"press keys...", max_from_end, row_pixels, Config.font_size, RED)
                    width = MeasureText(b"press keys...", Config.font_size)
            else:
                width = DrawingHelper.clickable_link(to_text, max_from_end, row_pixels, Config.font_size, BLACK, edit)

            max_to_end = max(max_from_end + width + Config.generic_padding, max_to_end)
            row_pixels += Config.font_size

        row_pixels = start_y

        self.to_delete = None
        for i, _ in enumerate(self.karabiner_config.modification_pairs):
            def edit(to_del):
                self.to_delete = to_del

            DrawingHelper.clickable_link("x", max_to_end, row_pixels, Config.font_size, RED, edit, [i])
            row_pixels += Config.font_size

        if self.to_delete is not None:
            del self.karabiner_config.modification_pairs[self.to_delete]
            KarabinerConfig().write_overrides()
