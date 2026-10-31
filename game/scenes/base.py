class BaseScene:
    def __init__(self, app):
        self.app = app

    def on_enter(self, **kwargs):
        del kwargs

    def on_exit(self):
        pass

    def handle_event(self, event):
        del event

    def update(self, delta_time):
        del delta_time

    def draw(self, surface):
        raise NotImplementedError
