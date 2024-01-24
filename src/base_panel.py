from registry import panel_registry

class BaseView:
    def __init__(self):
        panel_registry.append(self)

    def update(self):
        pass

    def draw(self):
        pass
