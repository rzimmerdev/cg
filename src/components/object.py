from abc import ABC
from typing import Union, Set

import glfw
import glm

from .model import Model


class Object:
    def __init__(self, model: Model = None):
        self.model = model
        self.position = glm.vec3(0.0, 0.0, 0.0)
        self.rotation = glm.vec3(0.0, 0.0, 0.0)
        self.scale = glm.vec3(1.0, 1.0, 1.0)
        self.speed = 2

        self.tick_methods = []

    def set_model(self, model):
        self.model = model

    def draw(self):
        if not self.model:
            return
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

    def tick(self, *args, **kwargs):
        for method in self.tick_methods:
            method(*args, **kwargs)
        return self

    def apply_movement(self, key_actions: Set[int], front, up, delta: float):
        if glfw.KEY_W in key_actions:
            self.position += self.speed * front * delta

        if glfw.KEY_S in key_actions:
            self.position -= self.speed * front * delta

        if glfw.KEY_A in key_actions:
            self.position -= glm.normalize(glm.cross(front, up)) * self.speed * delta

        if glfw.KEY_D in key_actions:
            self.position += glm.normalize(glm.cross(front, up)) * self.speed * delta

        if glfw.KEY_SPACE in key_actions:
            self.position += up * self.speed * delta

        if glfw.KEY_LEFT_SHIFT in key_actions:
            self.position -= up * self.speed * delta

    def apply_arrow_movement(self, key_actions: Set[int], front, up, delta: float):
        if glfw.KEY_UP in key_actions:
            self.position += self.speed * front * delta

        if glfw.KEY_DOWN in key_actions:
            self.position -= self.speed * front * delta

        if glfw.KEY_LEFT in key_actions:
            self.position -= glm.normalize(glm.cross(front, up)) * self.speed * delta

        if glfw.KEY_RIGHT in key_actions:
            self.position += glm.normalize(glm.cross(front, up)) * self.speed * delta

        if glfw.KEY_SPACE in key_actions:
            self.position += up * self.speed * delta

        if glfw.KEY_LEFT_SHIFT in key_actions:
            self.position -= up * self.speed * delta


class BoundObject(ABC):
    def __init__(self, *args, **kwargs):
        pass

    def contains(self, point):
        pass

    def clip(self, point):
        pass


class CuboidBound(BoundObject):
    def __init__(self, min_point, max_point):
        super().__init__()
        self.min_point = min_point
        self.max_point = max_point

    def contains(self, point):
        return all(self.min_point[i] <= point[i] <= self.max_point[i] for i in range(3))


class SphereBound(BoundObject):
    def __init__(self, center, radius):
        super().__init__()
        self.center = glm.vec3(*center) if isinstance(center, tuple) else center
        self.radius = radius

    def contains(self, point):
        return glm.distance(self.center, point) < self.radius

    def clip(self, point):
        return self.center + glm.normalize(point - self.center) * self.radius


class NormalBound(BoundObject):  # 2D plane with no bounds
    def __init__(self, normal, point):
        super().__init__()
        self.normal = glm.vec3(*normal) if isinstance(normal, tuple) else normal
        self.point = glm.vec3(*point) if isinstance(point, tuple) else point

    def contains(self, point):
        return glm.dot(self.normal, point - self.point) < 0

    def clip(self, point):
        return point - glm.dot(self.normal, point - self.point) * self.normal


class InteractiveObject(Object):
    def tick(self, key_actions):
        for method in self.tick_methods:
            method(key_actions)
        return self

    def interact(self, obj: Union["InteractiveObject", BoundObject], delta):
        if isinstance(obj, BoundObject):
            self.position = obj.clip(self.position)
