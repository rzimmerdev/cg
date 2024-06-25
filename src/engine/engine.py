from typing import List, Dict, Set

from OpenGL.GL.shaders import ShaderProgram

from src.components import Object, Model, Scene, BoundObject, InteractiveObject


class Physics:
    """
    Classe responsável por gerenciar a física do jogo.
    No momento a física é apenas para bounding, ou seja, para limitar espaços onde objetos podem ser movidos.
    """
    def __init__(self):
        self.objects: List[BoundObject] = []

    def register_object(self, obj: BoundObject):
        self.objects.append(obj)

    def tick(self, interactive_objects: List[InteractiveObject], delta):
        for obj in self.objects:
            if not isinstance(obj, BoundObject):
                continue
            for interactive_object in interactive_objects:
                if not obj.contains(interactive_object.position):
                    interactive_object.interact(obj, delta)


class Engine:
    """
    Classe responsável por gerenciar os objetos e cenas do jogo.
    Tem duas funções principais: `tick` e `render`.
    """
    def __init__(self, shader_program: ShaderProgram):
        self.objects: List[Object] = []
        self.interactive_objects: List[InteractiveObject] = []
        self.shader_program = shader_program

        self.models: Dict[str, Model] = {}
        self.scenes: Dict[str, Scene] = {}

        self.physics = Physics()
        self.day = None

    def register_model(self, name: str, wavefront_path: str):
        model = Model(self.shader_program, wavefront_path)
        self.models[name] = model
        return model

    def register_object(self, obj: List | Object):
        if isinstance(obj, InteractiveObject):
            self.interactive_objects.append(obj)
            return

        if isinstance(obj, list):
            self.objects.extend(obj)
        else:
            self.objects.append(obj)

    def register_scene(self, scene: Scene):
        self.scenes[scene.name] = scene

    def tick(self, key_actions: Set[int], delta: float, player=None):
        """Chama o método tick de todos os objetos e cenas registrados."""
        for obj in self.objects + self.interactive_objects:
            obj.tick(key_actions, delta)

        for scene in self.scenes.values():
            scene.tick(key_actions, delta, player)

        self.physics.tick(self.interactive_objects, delta)

    def render(self):
        """Chama o método draw de todos os objetos e cenas registrados."""
        for obj in self.objects:
            obj.draw()
        for scene in self.scenes.values():
            scene.draw()
