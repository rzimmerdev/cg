import glm

from src.components import InteractiveObject


class LightSource(InteractiveObject):
    def __init__(self, luminance=None):
        super().__init__(None)
        if isinstance(luminance, glm.vec3):
            self.luminance = luminance
        else:
            self.luminance = glm.vec3(1.0, 1.0, 1.0) if luminance is None else glm.vec3(*luminance)

    def draw(self, lights: list = None):
        super().draw(None)
