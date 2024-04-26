import glm

from .model import Model


class Object:
    def __init__(self, model: Model = None):
        self.model = model
        self.position = glm.vec3(0.0, 0.0, 0.0)
        self.rotation = glm.vec3(0.0, 0.0, 0.0)
        self.scale = glm.vec3(1.0, 1.0, 1.0)

    def set_model(self, model):
        self.model = model

    def draw(self):
        matrix = glm.mat4(1.0)
        matrix = glm.translate(matrix, self.position)
        matrix = glm.rotate(matrix, self.rotation.x, glm.vec3(1.0, 0.0, 0.0))
        matrix = glm.rotate(matrix, self.rotation.y, glm.vec3(0.0, 1.0, 0.0))
        matrix = glm.rotate(matrix, self.rotation.z, glm.vec3(0.0, 0.0, 1.0))
        matrix = glm.scale(matrix, self.scale)
        self.model.draw(matrix)
