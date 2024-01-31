from raylib import *

class KeyboardController():
    last_frame_pressed_keys = set()
    pressed_keys = set()

    @classmethod
    def update(cls):
        cls.last_frame_pressed_keys = cls.pressed_keys.copy()
        # Check for all key presses since the last frame
        pressed_key = GetKeyPressed()
        while pressed_key != 0:  # Loop until the queue is empty
            cls.pressed_keys.add(pressed_key)
            pressed_key = GetKeyPressed()

        to_remove = []
        for key in cls.pressed_keys:
            if IsKeyUp(key):
                to_remove.append(key)
        for key in to_remove:
            cls.pressed_keys.remove(key)

    @classmethod
    def removed_keys(cls):
        if len(cls.pressed_keys) < len(cls.last_frame_pressed_keys):
            return True
        return False