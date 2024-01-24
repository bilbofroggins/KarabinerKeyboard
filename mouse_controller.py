from raylib import *

class MouseController():
    is_hand_mouse = False

    @classmethod
    def set_hand_mouse(cls, state):
        cls.is_hand_mouse = state

    @staticmethod
    def draw():
        if MouseController.is_hand_mouse:
            MouseController.set_hand_mouse(False)
            SetMouseCursor(MOUSE_CURSOR_POINTING_HAND)
        else:
            SetMouseCursor(MOUSE_CURSOR_DEFAULT)