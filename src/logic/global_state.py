class GlobalState:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.input_focus = 'keyboard'
            cls._instance.frame = 0
        return cls._instance

    def tick(self):
        self.frame += 1