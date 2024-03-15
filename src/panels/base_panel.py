from src.panels.global_vars import panel_registry


class BaseView:
    def __init__(self):
        panel_registry.append(self)

    def update(self):
        pass

    def draw(self):
        pass

    def base_message(self, message):
        for panel in panel_registry:
            if hasattr(panel, "message_consumer"):
                method = getattr(panel, "message_consumer")
                if callable(method):
                    method(message)
