import pyray as ray
from src.config import config
from src.logic.global_state import GlobalState


class TextInput:
    def __init__(self):
        self.text = ""
        self.cursor_position = 0
        self.is_focused = False

    def set_text(self, text):
        """Set the text value."""
        self.text = text if text else ""
        self.cursor_position = len(self.text)

    def get_text(self):
        """Get the current text value."""
        return self.text

    def handle_input(self):
        """Handle keyboard input for the text field."""
        if not self.is_focused:
            return

        # Handle character input
        char = ray.get_char_pressed()
        while char > 0:
            # Only accept printable ASCII characters
            if 32 <= char <= 126:
                self.text = self.text[:self.cursor_position] + chr(char) + self.text[self.cursor_position:]
                self.cursor_position += 1
            char = ray.get_char_pressed()

        # Handle backspace
        if ray.is_key_pressed(ray.KEY_BACKSPACE):
            if self.cursor_position > 0:
                self.text = self.text[:self.cursor_position - 1] + self.text[self.cursor_position:]
                self.cursor_position -= 1

        # Handle delete
        if ray.is_key_pressed(ray.KEY_DELETE):
            if self.cursor_position < len(self.text):
                self.text = self.text[:self.cursor_position] + self.text[self.cursor_position + 1:]

        # Handle left arrow
        if ray.is_key_pressed(ray.KEY_LEFT):
            if self.cursor_position > 0:
                self.cursor_position -= 1

        # Handle right arrow
        if ray.is_key_pressed(ray.KEY_RIGHT):
            if self.cursor_position < len(self.text):
                self.cursor_position += 1

        # Handle home
        if ray.is_key_pressed(ray.KEY_HOME):
            self.cursor_position = 0

        # Handle end
        if ray.is_key_pressed(ray.KEY_END):
            self.cursor_position = len(self.text)

        # Handle cmd+a (select all) - just move cursor to end for now
        if ray.is_key_down(ray.KEY_LEFT_SUPER) or ray.is_key_down(ray.KEY_RIGHT_SUPER):
            if ray.is_key_pressed(ray.KEY_A):
                self.cursor_position = len(self.text)

            # Handle cmd+v (paste)
            if ray.is_key_pressed(ray.KEY_V):
                clipboard_text = ray.get_clipboard_text()
                if clipboard_text:
                    # Filter to only printable ASCII
                    filtered_text = ''.join(c for c in clipboard_text if 32 <= ord(c) <= 126)
                    self.text = self.text[:self.cursor_position] + filtered_text + self.text[self.cursor_position:]
                    self.cursor_position += len(filtered_text)

            # Handle cmd+c (copy) - copy entire text
            if ray.is_key_pressed(ray.KEY_C):
                ray.set_clipboard_text(self.text)

    def draw(self, row, col, width, height=None):
        """Draw the text input field.

        Args:
            row: Y position
            col: X position
            width: Width of the input field
            height: Height of the input field (defaults to font size + padding)
        """
        if height is None:
            height = config.font_size + config.small_padding * 2

        mouse_position = ray.get_mouse_position()
        is_hovering = col <= mouse_position.x <= col + width and row <= mouse_position.y <= row + height

        # Handle click to focus
        if is_hovering and ray.is_mouse_button_pressed(ray.MOUSE_BUTTON_LEFT):
            self.is_focused = True
        elif not is_hovering and ray.is_mouse_button_pressed(ray.MOUSE_BUTTON_LEFT):
            self.is_focused = False

        # Draw background
        bg_color = ray.LIGHTGRAY if self.is_focused else ray.GRAY
        ray.draw_rectangle(col, row, width, height, bg_color)

        # Draw border
        border_color = config.error_color if self.is_focused else ray.DARKGRAY
        ray.draw_rectangle_lines(col, row, width, height, border_color)

        # Handle input if focused
        if self.is_focused:
            self.handle_input()

        # Draw text (with clipping if it's too long)
        text_x = col + config.small_padding
        text_y = row + config.small_padding

        # Calculate visible text based on width
        display_text = self.text
        text_width = ray.measure_text(display_text, config.font_size)

        # If text is too wide, scroll to show cursor
        if text_width > width - config.small_padding * 2:
            # Calculate how much text we can show
            visible_width = width - config.small_padding * 2

            # Show text around cursor position
            left_text = self.text[:self.cursor_position]
            left_width = ray.measure_text(left_text, config.font_size)

            if left_width > visible_width:
                # Scroll left text
                while left_width > visible_width and len(left_text) > 0:
                    left_text = left_text[1:]
                    left_width = ray.measure_text(left_text, config.font_size)
                display_text = left_text + self.text[self.cursor_position:]

            # Trim from right if still too long
            while ray.measure_text(display_text, config.font_size) > visible_width and len(display_text) > 0:
                display_text = display_text[:-1]

        ray.draw_text(display_text, text_x, text_y, config.font_size, config.default_text_color)

        # Draw cursor if focused
        if self.is_focused:
            # Blink cursor
            frame = GlobalState().frame
            if (frame // 30) % 2 == 0:  # Blink every 30 frames
                cursor_text = self.text[:self.cursor_position]
                # Adjust for scrolling
                if display_text != self.text and len(self.text) > len(display_text):
                    offset = len(self.text) - len(display_text)
                    if self.cursor_position >= offset:
                        cursor_text = self.text[offset:self.cursor_position]
                    else:
                        cursor_text = ""

                cursor_x = text_x + ray.measure_text(cursor_text, config.font_size)
                ray.draw_line(cursor_x, text_y, cursor_x, text_y + config.font_size, config.default_text_color)

        return (row + height, col + width)
