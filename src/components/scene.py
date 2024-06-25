from typing import List, Dict

import glm

from .object import Object, LightSource


class Scene:
    def __init__(self, name: str, objects: List[Object] = None, lights: List[LightSource] = None):
        self.name = name
        self.objects: List[Object] = []
        self.lights: List[LightSource] = []
        self.sub_scenes: Dict[str, "Scene"] = {}

        self.position = glm.vec3(0.0, 0.0, 0.0)
        self.rotation = glm.vec3(0.0, 0.0, 0.0)
        self.scale = glm.vec3(1.0, 1.0, 1.0)

        if objects:
            self.add_object(objects)
        if lights:
            self.add_lights(lights)

        self.tick_methods = []

    def add_object(self, obj: List | Object):
        if isinstance(obj, list):
            self.objects.extend(obj)
        else:
            self.objects.append(obj)

    def add_lights(self, lights: List | LightSource):
        if isinstance(lights, list):
            self.lights.extend(lights)
        else:
            self.lights.append(lights)

    def add_scene(self, scene: "Scene"):
        self.sub_scenes[scene.name] = scene

    def draw(self, lights: list = None):
        lights = lights + self.lights if lights else self.lights
        for light in self.lights:
            light.draw()
        for obj in self.objects:
            obj.draw(lights)
        for scene in self.sub_scenes.values():
            scene.draw(lights)

    def move(self, position: tuple):
        self.position += glm.vec3(*position)

        for obj in self.objects:
            obj.move(position)
        for scene in self.sub_scenes.values():
            scene.move(position)

    def rescale(self, factor: tuple):
        self.scale *= glm.vec3(*factor)

        for obj in self.objects:
            obj.position -= self.position
            obj.position *= glm.vec3(*factor)
            obj.position += self.position

            obj.scale *= glm.vec3(*factor)

        for scene in self.sub_scenes.values():
            scene.rescale(factor)

    def rotate(self, rotation: tuple):
        self.rotation = glm.vec3(*rotation)
        rotation_matrix = glm.rotate(glm.mat4(1.0), self.rotation.x, glm.vec3(1.0, 0.0, 0.0))
        rotation_matrix = glm.rotate(rotation_matrix, self.rotation.y, glm.vec3(0.0, 1.0, 0.0))
        rotation_matrix = glm.rotate(rotation_matrix, self.rotation.z, glm.vec3(0.0, 0.0, 1.0))

        for obj in self.objects:
            obj.position -= self.position
            obj.position = glm.vec3(rotation_matrix * glm.vec4(obj.position, 1.0))
            obj.position += self.position

            obj.rotation += self.rotation

        for scene in self.sub_scenes.values():
            scene.rotate(rotation)

    def tick(self, *args, **kwargs):
        for method in self.tick_methods:
            method(*args, **kwargs)
        for obj in self.objects:
            obj.tick(*args, **kwargs)
        for scene in self.sub_scenes.values():
            scene.tick(*args, **kwargs)
        return self
