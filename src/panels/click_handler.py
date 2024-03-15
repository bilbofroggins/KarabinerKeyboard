import pyray as ray


class ClickHandler:
    stack = []

    @staticmethod
    def append(callback, args):
        ClickHandler.stack.append((callback, args))

def handle_clicks():
    while ClickHandler.stack:
        callback, args = ClickHandler.stack.pop()
        if ray.is_mouse_button_pressed(ray.MOUSE_BUTTON_LEFT):
            callback(*args) if len(args) else callback()
            break

    ClickHandler.stack = []