from raylib import *
from src.components.drawing_helper import DrawingHelper
from src.config import config
from src.logic.karabiner_config import KarabinerConfig
from src.logic.keyboard_state_controller import *
from src.logic.modification import Modification
from src.logic.modification_pair import ModificationPair


class ModificationChangeView():
    def __init__(self, modification_pairs, keyboard_state_controller: KeyboardStateController):
        super().__init__()
        self.modification_pairs = modification_pairs # Dict
        self.from_modification_being_edited: Modification = None
        self.to_modification_being_edited: Modification = None
        self.to_delete = None
        self.keyboard_state_controller = keyboard_state_controller
        self.new_modification = Modification()

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
                if self.to_modification_being_edited == self.new_modification:
                    new_pair = ModificationPair(self.keyboard_state_controller.locked_Modification, self.new_modification)
                    self.modification_pairs['new_obj'] = new_pair
                KarabinerConfig().write_overrides(self.modification_pairs)
                self.new_modification.reset()
                self.from_modification_being_edited = None
                self.to_modification_being_edited = None
            self.keyboard_state_controller.overrides_have_stopped()
        # Editing
        elif self.from_modification_being_edited:
            self.from_modification_being_edited.update_dirty(KeyboardController.last_frame_pressed_keys)
        elif self.to_modification_being_edited:
            self.to_modification_being_edited.update_dirty(KeyboardController.last_frame_pressed_keys)

    def draw_instructions(self, row, col):
        text = b"Press keys and hold to rebind..."
        DrawText(text, col, row, config.font_size, config.default_text_color)

    def draw_add_row(self, row, col):
        being_edited = self.to_modification_being_edited is self.new_modification

        def edit_callback():
            self.to_modification_being_edited = self.new_modification
            self.keyboard_state_controller.something_is_doing_overrides()

        DrawText(str(self.keyboard_state_controller.locked_Modification).encode('utf-8'), col, row, config.font_size, self.keyboard_state_controller.color())
        width = MeasureText(
            str(self.keyboard_state_controller.locked_Modification).encode('utf-8'),
            config.font_size) + config.generic_padding
        DrawText("->".encode('utf-8'), col + width, row, config.font_size,
                 config.default_text_color)
        width += MeasureText(
            "->".encode('utf-8'),
            config.font_size) + config.generic_padding

        if self.to_modification_being_edited == self.new_modification:
            DrawingHelper.modification_view(self.new_modification, being_edited,
                                            edit_callback, row, col + width)
        else:
            DrawingHelper.clickable_link("Add new binding...", row, col + width, config.font_size, PURPLE, edit_callback)

    def draw_overrides(self, start_row, start_col):
        if not len(self.modification_pairs) and self.keyboard_state_controller.state not in (STATE_IS_PRESSING, STATE_LOCKED, STATE_OVERRIDING):
            self.draw_instructions(start_row, start_col)
            return
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
            max_from_end = max(col + width + config.generic_padding, max_from_end)

        row = start_row
        width = 0
        col = max_from_end
        for override_pair in self.modification_pairs.values():
            DrawText("->".encode('utf-8'), col, row, config.font_size, config.default_text_color)
            width = MeasureText(
                    "->".encode('utf-8'),
                    config.font_size)
            row += config.font_size

        # TO modifications
        row = start_row
        col += width + config.generic_padding
        for override_pair in self.modification_pairs.values():
            current_modification = override_pair.modification_to
            being_edited = self.to_modification_being_edited is current_modification
            def edit_callback():
                self.to_modification_being_edited = override_pair.modification_to
                self.keyboard_state_controller.something_is_doing_overrides()

            row, width = DrawingHelper.modification_view(current_modification, being_edited, edit_callback, row, col)
            max_from_end = max(col + width + config.generic_padding, max_from_end)

        row = start_row
        col = max_from_end
        self.to_delete = None
        for i, _ in self.modification_pairs.items():
            def edit_callback(to_del):
                self.to_delete = to_del

            DrawingHelper.clickable_link("x", row, col, config.font_size, RED, edit_callback, [i])
            row += config.font_size

        if self.to_delete is not None:
            print(self.to_delete)
            KarabinerConfig().remove_override(self.to_delete)

        return row