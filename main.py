import random
from typing import Dict, Set

from src.game import Game
from src.components import Object, Scene, Model, Player, SphereBound, NormalBound


def generate(model, n, a, b, y=0.5):
    return [Object(model).move((random.uniform(a, b), y, random.uniform(a, b))) for _ in range(n)]


class MainScene(Scene):
    def __init__(self, engine):
        super().__init__("main", [])
        self.models: Dict[str, Model] = {}
        self.engine = engine

    def register(self):
        sky = self.engine.register_model("models/sky/sky.obj", "models/sky/sky.jpg", "sky")
        rock = self.engine.register_model("models/terrain/rock.obj", "models/terrain/rock.jpg", "terrain")

        ground = self.engine.register_model("models/ground/ground.obj", "models/ground/ground.jpg", "ground")
        house = self.engine.register_model("models/house/house.obj", "models/house/house.png", "house")
        cube = self.engine.register_model("models/caixa/caixa.obj", "models/caixa/caixa.jpg", "cube")
        monster = self.engine.register_model("models/monster/monster.obj", "models/monster/monster.jpg", "monster")
        # fabienne = engine.register_model("models/fabienne/fabienne.obj", "models/fabienne/fabienne.jpg", "fabienne")

        # denis = engine.register_model("models/denis/denis.obj", "models/denis/denis.jpg", "denis")
        # engine.register_model("models/tree/Tree1.obj", "models/tree/BarkDecidious0143_5_S.jpg", "tree")
        self.models = {
            "sky": sky,
            "rock": rock,
            "ground": ground,
            "house": house,
            "cube": cube,
            "monster": monster,
            # "fabienne": fabienne,
            # "denis": denis,
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
        sky = Object(self.models["sky"])
        sky.rescale((1, 1, 1))
        terrain = Object(self.models["rock"])
        terrain.rescale((0.2, 0.05, 0.2))
        terrain.move((0, -1.5, 0))

        sky_bound = SphereBound((0, 0, 0), radius=45)
        self.engine.physics.register_object(sky_bound)

        normal_bound = NormalBound((0, -1, 0), (0, -0.7, 0))
        self.engine.physics.register_object(normal_bound)

        return Scene("environment", [sky, terrain])

    @property
    def inside(self):
        # house model
        house = Object(self.models["house"])
        ground = Object(self.models["ground"])
        ground.rescale((10, 0.05, 10))

        # boxes
        a, b = -3, 3
        boxes = generate(self.models["cube"], 2, a, b, 0.9)

        # monster
        monster = Object(self.models["monster"])
        monster.move((0, 0, -2))
        monster.rescale((0.5, 0.5, 0.5))

        import glfw
        import glm

        def apply_movement(key_actions: Set[int], delta: float):
            up = glm.vec3(0.0, 1.0, 0.0)
            front = glm.vec3(0.0, 0.0, 1.0)

            if glfw.KEY_UP in key_actions:
                monster.position += monster.speed * front * delta

            if glfw.KEY_DOWN in key_actions:
                monster.position -= monster.speed * front * delta

            if glfw.KEY_LEFT in key_actions:
                monster.position -= glm.normalize(glm.cross(front, up)) * monster.speed * delta

            if glfw.KEY_RIGHT in key_actions:
                monster.position += glm.normalize(glm.cross(front, up)) * monster.speed * delta

        monster.tick_methods.append(apply_movement)

        # fabienne
        # fabienne = Object(self.models["fabienne"])
        # fabienn_scale = 1e-2
        # fabienne.rescale(tuple([fabienn_scale] * 3))
        # fabienne.move((-3, 0, 4))
        # fabienne.rotate((0, 1, 0))

        return Scene("inside", [house] + boxes + [ground] + [monster] + [])

    @property
    def outside(self):
        # denis
        # denis = Object(self.models["denis"])
        # denis_scale = 1e-2
        # denis.rescale(tuple([denis_scale] * 3))
        # denis.move((0, 0, 5))

        # trees
        # trees = generate(engine.models["tree"], 100, a, b)

        # car
        # car = Object(engine.models["car"])

        return Scene("outside", [])


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
