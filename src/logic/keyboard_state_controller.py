from raylib import GetFPS

from src.devices.keyboard_controller import KeyboardController
from src.panels.base_panel import BaseView

STATE_EMPTY = 0
STATE_IS_PRESSING = 1
STATE_LOCKED = 2
STATE_OVERRIDING = 3

class KeyboardStateController(BaseView):
    def __init__(self):
        super().__init__()
        self.listeners = []
        self.state = STATE_EMPTY
        self.timer = 0
        self.timer_reset()

    def register(self, instance):
        self.listeners.append(instance)

    def notify_listeners(self):
        for listener in self.listeners:
            listener.change_keyboard_state(self.state)

    def timer_reset(self):
        self.timer = 0.6

    def something_is_doing_overrides(self):
        self.state = STATE_OVERRIDING

    def overrides_have_stopped(self):
        self.state = STATE_EMPTY

    def update(self):
        if self.state == STATE_OVERRIDING:
            self.notify_listeners()
            return

        fps = max(GetFPS(), 1)
        if self.state == STATE_EMPTY:
            if KeyboardController.added_keys():
                self.state = STATE_IS_PRESSING
            self.timer_reset()
        elif self.state == STATE_IS_PRESSING:
            if len(KeyboardController.pressed_keys) == 0:
                self.state = STATE_EMPTY
            self.timer -= 1 / fps
            if KeyboardController.added_keys():
                self.timer_reset()
            if KeyboardController.removed_keys():
                self.timer_reset()
            elif self.timer <= 0 and len(KeyboardController.pressed_keys):
                self.state = STATE_LOCKED
        elif self.state == STATE_LOCKED:
            if KeyboardController.added_keys():
                self.timer_reset()
                self.state = STATE_IS_PRESSING

        self.notify_listeners()