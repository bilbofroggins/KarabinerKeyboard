class EventBus:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.listeners = {}
            # listeners = { event_type: [] }
        return cls._instance

    def register(self, event_type, obj):
        if event_type not in self.listeners:
            self.listeners[event_type] = []
        self.listeners[event_type].append(obj)

    def notify(self, event_type):
        for listener in self.listeners[event_type]:
            listener.notify()