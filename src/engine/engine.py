import threading
from typing import List, Dict

from OpenGL.GL.shaders import ShaderProgram

from src.engine.multiplayer import Multiplayer
from src.components import Object, Model, Player, Scene


class Engine:
    def __init__(self, shader_program: ShaderProgram):
        self.objects: List[Object] = []
        self.player_model = Model(shader_program, "models/monster/monster.obj", "models/monster/monster.jpg")
        self.players: Dict[int, Player] = {}

        self.running = threading.Event()
        self.conn = Multiplayer()
        self.server = None

        self.models = {}
        self.scenes = {}

    def register_model(self, path: str, texture: str, name: str = None):
        model = Model(self.player_model.shader_program, path, texture)
        if name:
            self.models[name] = model
        else:
            self.models[path] = model
        return model

    def register_object(self, obj: List | Object):
        if isinstance(obj, list):
            self.objects.extend(obj)
        else:
            self.objects.append(obj)

    def register_scene(self, scene: Scene):
        self.scenes[scene.name] = scene

    def physics(self):
        pass

    def graphics(self):
        for obj in self.objects:
            obj.draw()
        for scene in self.scenes.values():
            scene.draw()
        for player in self.players.values():
            player.draw()

    def start(self):
        self.running.set()
        thread = threading.Thread(target=self.tick)
        thread.start()

    def tick(self):
        while self.running.is_set():
            self.physics()
            self.graphics()
