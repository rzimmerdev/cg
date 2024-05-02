from typing import List, Dict

import glm

from .object import Object


class Scene:
    def __init__(self, name: str, objects: List[Object] = None):
        self.name = name
        self.objects: List[Object] = []
        self.sub_scenes: Dict[str, "Scene"] = {}

        self.position = glm.vec3(0.0, 0.0, 0.0)
        self.rotation = glm.vec3(0.0, 0.0, 0.0)
        self.scale = glm.vec3(1.0, 1.0, 1.0)

        if objects:
            self.add_object(objects)

    def add_object(self, obj: List | Object):
        if isinstance(obj, Object):
            self.objects.append(obj)
        elif isinstance(obj, list):
            for o in obj:
                if isinstance(o, Object):
                    self.objects.append(o)
                elif isinstance(o, list):
                    self.add_object(o)

    def add_scene(self, scene: "Scene"):
        self.sub_scenes[scene.name] = scene

    def draw(self):
        for obj in self.objects:
            obj.draw()
        for scene in self.sub_scenes.values():
            scene.draw()

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
