import math
import random
from typing import Dict, Set

from src.game import Game
from src.components import Object, LightSource, Scene, Model, Player, SphereBound, NormalBound

import glfw
import glm


class F(Object):
    """
    Classe que representa um obj multifuncionalidade no jogo.
    Herda de Object e adiciona métodos específicos para movimentação e interação, com o lado direito do teclado.

    Para movimentar o objeto, use:

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
        self.tick_methods.append(self.change_coefficients)

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

        # Rotaciona o obj no eixo y
        if glfw.KEY_RIGHT_CONTROL in key_actions:
            self.rotate((0, 1, 0), self.rotate_speed)

        if glfw.KEY_RIGHT_SHIFT in key_actions:
            self.rotate((0, -1, 0), self.rotate_speed)

        # Rotaciona o obj no eixo x
        if glfw.KEY_LEFT_BRACKET in key_actions:
            self.rotate((1, 0, 0), self.rotate_speed)

        if glfw.KEY_RIGHT_BRACKET in key_actions:
            self.rotate((-1, 0, 0), self.rotate_speed)

        # Escala o obj
        if glfw.KEY_EQUAL in key_actions:
            self.rescale((1, 1, 1), self.scale_speed)

        if glfw.KEY_MINUS in key_actions:
            self.rescale((1, 1, 1), 1 / self.scale_speed)

    def change_coefficients(self, key_actions: Set[int], delta: float):
        # Teclas 0 e 9 para mudar o coeficiente ambiente
        if glfw.KEY_0 in key_actions:
            self.model.ambient_coefficient += delta
        if glfw.KEY_9 in key_actions:
            self.model.ambient_coefficient -= delta
        # Teclas 1 e 2 para mudar o coeficiente difuso
        if glfw.KEY_1 in key_actions:
            self.model.diffuse_coefficient += delta
        if glfw.KEY_2 in key_actions:
            self.model.diffuse_coefficient -= delta
        # Teclas 3 e 4 para mudar o coeficiente especular
        if glfw.KEY_3 in key_actions:
            self.model.specular_coefficient += delta
        if glfw.KEY_4 in key_actions:
            self.model.specular_coefficient -= delta
        # Teclas 5 e 6 para mudar o coeficiente de brilho
        if glfw.KEY_5 in key_actions:
            self.model.shininess += delta / 10
        if glfw.KEY_6 in key_actions:
            self.model.shininess -= delta / 10


class Saucer(LightSource):
    def __init__(self, model: Model = None, luminance=None, radius=10, height=10):
        super().__init__(model, luminance)
        self.tick_methods.append(self.sauce)
        self.theta = 0
        self.radius = radius
        self.height = height
        self.position = glm.vec3(0, height, radius)
        self.on = True

    def sauce(self, key_actions: Set[int], delta: float):
        """Keep rotating around origin at height 10"""
        """F rotates clockwise, G rotates counter-clockwise."""
        # calculate circle coordinates
        if glfw.KEY_F in key_actions:
            self.theta = (self.theta + delta) % (2 * math.pi)
        if glfw.KEY_G in key_actions:
            self.theta = (self.theta - delta) % (2 * math.pi)

        # if key = H, turn off
        if glfw.KEY_H in key_actions:
            self.luminance = glm.clamp(self.luminance - delta, 0.0, 5.0)
        if glfw.KEY_J in key_actions:
            self.luminance = glm.clamp(self.luminance + delta, 0.0, 5.0)

        x = self.radius * math.cos(self.theta)
        z = self.radius * math.sin(self.theta)

        self.position = glm.vec3(x, self.height, z)


class Day(LightSource):
    def __init__(self, model: Model = None, luminance=None):
        super().__init__(model, luminance)
        self.tick_methods.append(self.change_time)

    def change_time(self, key_actions: Set[int], delta: float):
        if glfw.KEY_C in key_actions:
            self.update_luminance(-delta, min_luminance=0.2)
        if glfw.KEY_V in key_actions:
            self.update_luminance(delta, max_luminance=5.0)


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
        self.ambient_lights = {}
        self.current_scene = None

    def register(self):
        sky = self.engine.register_model("sky", "models/sky")
        terrain = self.engine.register_model("terrain", "models/terrain") # vn

        ground = self.engine.register_model("ground", "models/ground")
        ground.shininess = 16

        house = self.engine.register_model("house", "models/house")
        house.shininess = 1
        house.diffuse_coefficient = 0.9
        house.specular_coefficient = 0.1

        cube = self.engine.register_model("cube", "models/caixa")
        cat = self.engine.register_model("cat", "models/cat")
        cat.shininess = 128
        cat.specular_coefficient = 0.7
        cat.diffuse_coefficient = 0.8

        fabienne = self.engine.register_model("fabienne", "models/fabienne")
        stool = self.engine.register_model("stool", "models/stool")
        stool.shininess = 128
        stool.specular_coefficient = 0.5

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
            "cat": cat,
            "fabienne": fabienne,
            "denis": denis,
            "tree": tree,
            "grass": grass,
            "horse": horse,
            "stool": stool,
            "lantern": lantern
        }

        self.ambient_lights = {"outside": Day(luminance=(2, 2, 2)),
                               "inside": LightSource(None, (1, 1, 1))}
        self.current_scene = "inside"
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

        sky_bound = SphereBound((0, 0, 0), radius=45)
        self.engine.physics.register_object(sky_bound)

        normal_bound = NormalBound((0, -1, 0), (0, -0.7, 0))
        self.engine.physics.register_object(normal_bound)

        return Scene("environment", [sky])

    @property
    def inside(self):
        """
        Ambiente interno, contém uma casa, caixas, um monstro, uma pessoa e um banco.
        """
        # house model
        house = Object(self.models["house"])
        house.move((0, -0.1, 0))
        ground1 = Object(self.models["ground"])
        ground1.rescale((5.65, 0.05, 4.4))
        ground1.move((0.2, 0.2, 0.3))

        ground2 = Object(self.models["ground"])
        ground2.rescale((1.7, 0.05, 1.1))
        ground2.move((-3.7, 0.2, 5.65))

        # boxes
        a, b = -3, 3
        boxes = generate(self.models["cube"], 2, a, b, 0.8)

        for box in boxes:
            box.rescale((0.6, 0.6, 0.6))

        cat = Object(self.models["cat"])
        cat.rescale((1e-2, 1e-2, 1e-2))
        cat.rotate((-1.5, 0, 45))
        cat.move((-3, 0.3, -3))

        # fabienne
        fabienne = F(self.models["fabienne"])
        fabienn_scale = 1e-2
        fabienne.rescale(tuple([fabienn_scale] * 3))
        fabienne.move((-3, 0.25, 4))
        fabienne.rotate((0, 1, 0))

        # stool
        stool = Object(self.models["stool"])
        stool.rescale((0.5, 0.5, 0.5))
        stool.move((4, 0, 3))

        lantern = LightSource(self.models['lantern'], luminance=(3, 3, 3))
        lantern.rescale((0.1, 0.1, 0.1))
        lantern.rotate((1.5, 0, 0))
        lantern.move((0, 2, 0))

        return Scene("inside", [house, ground1, ground2, cat, fabienne] + boxes + [stool],
                     [lantern])

    @property
    def outside(self):
        """
        Ambiente externo, contém, árvores, uma pessoa e um cavalo.
        """
        # denis
        house = Object(self.models["house"])
        house.move((0, -1, 0))
        denis = Object(self.models["denis"])
        denis_scale = 1e-2
        denis.rescale(tuple([denis_scale] * 3))
        denis.move((-1, -0.5, 5))

        terrain = Object(self.models["terrain"])
        terrain.rescale((0.2, 0.05, 0.2))
        terrain.move((0, -1.5, 0))

        # trees
        a, b = -10, 10
        trees = generate(self.models["tree"], 10, a, b, -1.25, 10)

        # grass
        grass = Object(self.models["grass"])
        grass.rescale((1.75, 0.01, 5))
        grass.move((8, -0.75, 0))

        horse = Object(self.models["horse"])
        horse.move((0, 0, 10))

        saucer = Saucer(self.models["lantern"], luminance=(2, 2, 2), height=6)
        saucer.rescale((0.1, 0.1, 0.1))

        return Scene("outside", [terrain, house, denis, grass, horse] + trees, [saucer])

    def tick(self, key_actions: Set[int], delta: float, player: Player = None):
        super().tick(key_actions, delta)
        # if player is inside, use Day as light source
        if player is None:
            return
        if -3.8 < player.position.z < 4.8 and -5.8 < player.position.x < 5.8 and -0.2 < player.position.y < 4:
            self.current_scene = "inside"
        else:
            self.current_scene = "outside"
        self.ambient_lights['outside'].tick(key_actions, delta)

    def draw(self, lights: list = None, ambient_light=None):
        ambient_light = self.ambient_lights[self.current_scene]
        if self.current_scene == "inside":
            self.sub_scenes["inside"].draw([], ambient_light)
        else:
            self.sub_scenes["environment"].draw([], ambient_light)
            self.sub_scenes["outside"].draw([], ambient_light)


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
