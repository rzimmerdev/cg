import threading
from typing import List, Dict

from OpenGL.GL.shaders import ShaderProgram

from src.engine.multiplayer import Multiplayer
from src.objects import Object, Model, Player


class Engine:
    def __init__(self, shader_program: ShaderProgram):
        self.objects: List[Object] = []
        self.player_model = Model(shader_program, "models/monster/monster.obj", "models/monster/monster.jpg")
        self.players: Dict[int, Player] = {}

        self.running = threading.Event()
        self.conn = Multiplayer()
        self.server = None

    def add_objects(self, obj):
        if isinstance(obj, list):
            self.objects.extend(obj)
        else:
            self.objects.append(obj)

    def draw(self):
        for obj in self.objects:
            obj.draw()
        for player in self.players.values():
            player.draw()

    def start(self):
        self.running.set()
        thread = threading.Thread(target=self.tick)
        thread.start()

    def tick(self):
        pass

    def handle_player(self):
        pass
