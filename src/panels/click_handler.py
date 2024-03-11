from raylib import IsMouseButtonPressed, MOUSE_BUTTON_LEFT


class ClickHandler:
    stack = []

    @staticmethod
    def append(callback, args):
        ClickHandler.stack.append((callback, args))

def handle_clicks():
    while ClickHandler.stack:
        callback, args = ClickHandler.stack.pop()
        if IsMouseButtonPressed(MOUSE_BUTTON_LEFT):
            callback(*args) if len(args) else callback()
            break

    ClickHandler.stack = []