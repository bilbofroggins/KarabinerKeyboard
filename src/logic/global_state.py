class GlobalState:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.input_focus = 'keyboard'
            cls._instance.frame = 0
            cls._instance.highlighted_keys = []
            cls._instance.highlighted_frame_start = 0
            cls._instance.is_keyboard_hover = False

        return cls._instance

    def tick(self):
        self.frame += 1

    def highlighted_chord_to_show(self):
        if len(self.highlighted_keys) == 0:
            return []
        frames_per_switch = 60
        index = (self.frame - self.highlighted_frame_start) // frames_per_switch % len(self.highlighted_keys)
        return self.highlighted_keys[index]