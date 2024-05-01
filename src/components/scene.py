from typing import List

from .object import Object


class Scene:
    def __init__(self, name: str, objects: List[Object] = None):
        self.name = name
        self.objects: List[Object] = []

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

    def draw(self):
        for obj in self.objects:
            obj.draw()
