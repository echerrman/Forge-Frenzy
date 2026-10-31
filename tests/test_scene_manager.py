from game.scene_manager import SceneManager


class FakeScene:
    def __init__(self):
        self.entered_with = None
        self.exited = False
        self.updated_by = 0.0
        self.drawn = False

    def on_enter(self, **kwargs): self.entered_with = kwargs
    def on_exit(self): self.exited = True
    def handle_event(self, event): pass
    def update(self, delta_time): self.updated_by += delta_time
    def draw(self, surface): self.drawn = True


def test_switch_calls_scene_lifecycle():
    manager = SceneManager()
    first, second = FakeScene(), FakeScene()
    manager.register("first", lambda: first)
    manager.register("second", lambda: second)
    manager.switch("first", purpose="test")
    assert first.entered_with == {"purpose": "test"}
    manager.switch("second")
    assert first.exited and manager.active_scene is second


def test_routes_update_and_draw():
    manager = SceneManager()
    scene = FakeScene()
    manager.register("scene", lambda: scene)
    manager.switch("scene")
    manager.update(0.25)
    manager.draw(object())
    assert scene.updated_by == 0.25 and scene.drawn
