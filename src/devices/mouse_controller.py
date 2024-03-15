import pyray as ray

class MouseController():
    is_hand_mouse = False
    is_hand_type = False

    @classmethod
    def set_hand_mouse(cls, state):
        cls.is_hand_mouse = state

    @classmethod
    def set_hand_type(cls, state):
        cls.is_hand_type = state

    @staticmethod
    def draw():
        if MouseController.is_hand_mouse:
            MouseController.set_hand_mouse(False)
            ray.set_mouse_cursor(ray.MOUSE_CURSOR_POINTING_HAND)
        elif MouseController.is_hand_type:
            MouseController.set_hand_type(False)
            ray.set_mouse_cursor(ray.MOUSE_CURSOR_IBEAM)
        else:
            ray.set_mouse_cursor(ray.MOUSE_CURSOR_DEFAULT)