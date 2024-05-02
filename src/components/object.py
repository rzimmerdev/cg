import glm

from .model import Model


class Object:
    def __init__(self, model: Model = None):
        self.model = model
        self.position = glm.vec3(0.0, 0.0, 0.0)
        self.rotation = glm.vec3(0.0, 0.0, 0.0)
        self.scale = glm.vec3(1.0, 1.0, 1.0)

        self.tick_methods = []

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

    def rescale(self, factor: tuple):
        self.scale *= glm.vec3(*factor)
        return self

    def move(self, position: tuple):
        self.position += glm.vec3(*position)
        return self

    def rotate(self, rotation: tuple):
        self.rotation += glm.vec3(*rotation)
        return self

    def tick(self):
        for method in self.tick_methods:
            method()
        return self
