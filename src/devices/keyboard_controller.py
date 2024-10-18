import pyray as ray

from src.logic.key_mappings import rl_to_kb_key_map, modification_keys


class KeyboardController():
    last_frame_pressed_keys = set()
    pressed_keys = set()
    keys_held_down = set()

    @classmethod
    def update(cls):
        cls.last_frame_pressed_keys = cls.pressed_keys.copy()
        # Check for all key presses since the last frame
        pressed_key = ray.get_key_pressed()
        while pressed_key != 0:  # Loop until the queue is empty
            cls.pressed_keys.add(pressed_key)
            pressed_key = ray.get_key_pressed()

        to_remove = []
        for key in cls.pressed_keys:
            if ray.is_key_up(key):
                to_remove.append(key)
        for key in to_remove:
            cls.pressed_keys.remove(key)

    @classmethod
    def removed_keys(cls):
        return cls.last_frame_pressed_keys - cls.pressed_keys

    @classmethod
    def added_keys(cls):
        return cls.pressed_keys - cls.last_frame_pressed_keys

    @classmethod
    def listen_to_keys(cls):
        if len(cls.keys_held_down) and len(KeyboardController.removed_keys()):
            to_add = []
            keys_held_copy = cls.keys_held_down.copy()
            # Put the mod keys in first, then normal keys
            for key in keys_held_copy:
                kb_key = rl_to_kb_key_map[key]
                if kb_key in modification_keys:
                    to_add.append(kb_key)
                    cls.keys_held_down.remove(key)
            for key in cls.keys_held_down:
                kb_key = rl_to_kb_key_map[key]
                to_add.append(kb_key)

            cls.keys_held_down = set()
            return to_add[:]
        for key in KeyboardController.added_keys():
            cls.keys_held_down.add(key)