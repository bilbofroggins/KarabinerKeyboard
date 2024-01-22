from raylib import *
from base_panel import BaseView
from key_mappings import *
from overrides import Overrides


class OverridesView(BaseView):
    def __init__(self):
        super().__init__()
        self.overrides = Overrides()

    def update(self):
        pass

    def draw_overrides(self, start_x, start_y):
        for override in self.overrides.modifications:
            from_text = (''.join(override['from']['modifiers']) + '+' + override['from']['key']).encode('utf-8')
            to_text = (''.join(override['to']['modifiers']) + '+' + override['to']['key']).encode('utf-8')
            DrawText(from_text, start_x, start_y, 20, BLACK)
            DrawText(to_text, start_x + 200, start_y, 20, BLACK)
            start_y = start_y + 20
