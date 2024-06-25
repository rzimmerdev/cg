import random
from typing import Dict, Set

from src.game import Game
from src.components import Object, LightSource, Scene, Model, Player, SphereBound, NormalBound

import glfw
import glm


class Monster(Object):
    """
    Classe que representa um monstro no jogo.
    Herda de Object e adiciona métodos específicos para movimentação e interação, com o lado direito do teclado.

    Para movimentar o monstro, use:

    - Setas direcionais para frente, trás, esquerda e direita para movimentação no plano xz.

    - Teclas Right Control e Shift para rotação no eixo y.

    - Teclas `[` e `]` para rotação no eixo x.

    - Teclas `+` e `-` para escalar o monstro.
    """
    def __init__(self, model: Model):
        super().__init__(model)
        self.rotate_speed = 1e-2
        self.scale_speed = 1.01

        self.tick_methods.append(self.arrow_movement)

    def arrow_movement(self, key_actions: Set[int], delta: float):
        up = glm.vec3(0.0, 1.0, 0.0)
        front = glm.vec3(0.0, 0.0, 1.0)

        if glfw.KEY_UP in key_actions:
            self.position += self.speed * front * delta

        if glfw.KEY_DOWN in key_actions:
            self.position -= self.speed * front * delta

        if glfw.KEY_LEFT in key_actions:
            self.position -= glm.normalize(glm.cross(front, up)) * self.speed * delta

        if glfw.KEY_RIGHT in key_actions:
            self.position += glm.normalize(glm.cross(front, up)) * self.speed * delta

        # Rotaciona o monstro no eixo y
        if glfw.KEY_RIGHT_CONTROL in key_actions:
            self.rotate((0, 1, 0), self.rotate_speed)

        if glfw.KEY_RIGHT_SHIFT in key_actions:
            self.rotate((0, -1, 0), self.rotate_speed)

        # Rotaciona o monstro no eixo x
        if glfw.KEY_LEFT_BRACKET in key_actions:
            self.rotate((1, 0, 0), self.rotate_speed)

        if glfw.KEY_RIGHT_BRACKET in key_actions:
            self.rotate((-1, 0, 0), self.rotate_speed)

        # Escala o monstro
        if glfw.KEY_EQUAL in key_actions:
            self.rescale((1, 1, 1), self.scale_speed)

        if glfw.KEY_MINUS in key_actions:
            self.rescale((1, 1, 1), 1 / self.scale_speed)


def generate(model, n, a, b, y=0.5, radius=1, distance=1):
    objs = [Object(model).move((random.uniform(a, b), y, random.uniform(a, b))) for _ in range(n)]
    # se os objetos estiverem muito próximos, distanciar
    for i in range(n):
        for j in range(i + 1, n):
            while glm.distance(objs[i].position, objs[j].position) < distance:
                objs[j].move((random.uniform(a, b), 0, random.uniform(a, b)))

    # make objects at least radius away from center
    # define uma distância mínima do raio do centro
    for obj in objs:
        while glm.distance(obj.position, glm.vec3(0, 0, 0)) < radius:
            obj.move((random.uniform(a, b), 0, random.uniform(a, b)))
    return objs


class MainScene(Scene):
    def __init__(self, engine):
        super().__init__("main", [])
        self.models: Dict[str, Model] = {}
        self.engine = engine

    def register(self):
        sky = self.engine.register_model("sky", "models/sky")
        terrain = self.engine.register_model("terrain", "models/terrain") # vn

        ground = self.engine.register_model("ground", "models/ground")
        house = self.engine.register_model("house", "models/house")
        cube = self.engine.register_model("cube", "models/caixa")
        monster = self.engine.register_model("monster", "models/monster")  # vn
        fabienne = self.engine.register_model("fabienne", "models/fabienne")
        stool = self.engine.register_model("stool", "models/stool")
        lantern = self.engine.register_model("lantern", "models/lantern")

        denis = self.engine.register_model("denis", "models/denis")
        tree = self.engine.register_model("tree", "models/tree")
        grass = self.engine.register_model("grass", "models/grass")
        horse = self.engine.register_model("horse", "models/horse") # vn

        self.models = {
            "sky": sky,
            "terrain": terrain,
            "ground": ground,
            "house": house,
            "cube": cube,
            "monster": monster,
            "fabienne": fabienne,
            "denis": denis,
            "tree": tree,
            "grass": grass,
            "horse": horse,
            "stool": stool,
            "lantern": lantern
        }

        self.engine.register_scene(self)

        return self

    def load(self):
        self.add_scene(self.environment)
        inside = self.inside
        inside.move((0, -1, 0))
        self.add_scene(inside)
        self.add_scene(self.outside)

        return self

    @property
    def environment(self):
        """
        Ambiente de fundo, contém o céu e o chão fixo.
        """
        sky = Object(self.models["sky"])
        sky.rescale((1, 1, 1))
        terrain = Object(self.models["terrain"])
        terrain.rescale((0.2, 0.05, 0.2))
        terrain.move((0, -1.5, 0))

        sky_bound = SphereBound((0, 0, 0), radius=45)
        self.engine.physics.register_object(sky_bound)

        normal_bound = NormalBound((0, -1, 0), (0, -0.7, 0))
        self.engine.physics.register_object(normal_bound)

        ambience = LightSource(luminance=(2, 2, 2))

        # return Scene("environment", [sky, terrain])
        return Scene("environment", [sky, terrain] + [], [ambience])

    @property
    def inside(self):
        """
        Ambiente interno, contém uma casa, caixas, um monstro, uma pessoa e um banco.
        """
        # house model
        house = Object(self.models["house"])
        ground1 = Object(self.models["ground"])
        ground1.rescale((6, 0.25, 4))
        # ground1.move((0, 0, 1))

        ground2 = Object(self.models["ground"])
        ground2.rescale((1, 0.25, 1))
        ground2.move((10, 1, 10))

        # boxes
        a, b = -3, 3
        boxes = generate(self.models["cube"], 2, a, b, 0.8)

        for box in boxes:
            box.rescale((0.6, 0.6, 0.6))

        # monster
        monster = Monster(self.models["monster"])
        monster.move((0, 0.25, -2))
        monster.rescale((0.5, 0.5, 0.5))

        # fabienne
        fabienne = Object(self.models["fabienne"])
        fabienn_scale = 1e-2
        fabienne.rescale(tuple([fabienn_scale] * 3))
        fabienne.move((-3, 0.25, 4))
        fabienne.rotate((0, 1, 0))

        # stool
        stool = Object(self.models["stool"])
        stool.rescale((0.5, 0.5, 0.5))
        stool.move((4, 0, 3))

        ambience = LightSource(luminance=(1, 1, 1))

        lantern = LightSource(self.models['lantern'], luminance=(1, 1, 1))
        lantern.move((0, 1, 0))
        lantern.rescale((0.1, 0.1, 0.1))

        return Scene("inside", [house, ground1, ground2, monster, fabienne] + boxes + [stool],
                     [ambience, lantern])

    @property
    def outside(self):
        """
        Ambiente externo, contém, árvores, uma pessoa e um cavalo.
        """

        # denis
        denis = Object(self.models["denis"])
        denis_scale = 1e-2
        denis.rescale(tuple([denis_scale] * 3))
        denis.move((-1, -0.5, 5))

        # trees
        a, b = -10, 10
        trees = generate(self.models["tree"], 5, a, b, -1.25, 10)

        # grass
        grass = Object(self.models["grass"])
        grass.rescale((1.75, 0.01, 5))
        grass.move((8, -0.75, 0))

        horse = Object(self.models["horse"])
        horse.move((0, 0, 10))

        return Scene("outside", [denis, grass] + trees + [horse])


def main():
    game = Game()
    game.create()

    player = Player()
    player.move((0, 0.5, 0))
    game.add_player(player)

    main_scene = MainScene(game.engine).register()
    main_scene.load()

    try:
        game.start()
    except KeyboardInterrupt:
        pass
    finally:
        game.stop()


if __name__ == "__main__":
    main()
