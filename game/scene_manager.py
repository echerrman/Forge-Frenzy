"""Scene lifecycle and routing."""


class SceneManager:
    def __init__(self):
        self._factories = {}
        self.active_scene = None
        self.active_name = None

    def register(self, name, factory):
        self._factories[name] = factory

    def switch(self, name, **kwargs):
        if name not in self._factories:
            raise KeyError(f"Unknown scene: {name}")
        if self.active_scene:
            self.active_scene.on_exit()
        self.active_scene = self._factories[name]()
        self.active_name = name
        self.active_scene.on_enter(**kwargs)

    def handle_event(self, event):
        if self.active_scene:
            self.active_scene.handle_event(event)

    def update(self, delta_time):
        if self.active_scene:
            self.active_scene.update(delta_time)

    def draw(self, surface):
        if self.active_scene:
            self.active_scene.draw(surface)
