import random

from src.game import Game
from src.components import Object, Scene


def generate(model, n, a, b):
    return [Object(model).move((random.uniform(a, b), 0.5, random.uniform(a, b))) for _ in range(n)]


def main():
    game = Game()
    game.create()

    engine = game.engine

    engine.register_model("models/sky/sky.obj", "models/sky/sky.jpg", "sky")
    engine.register_model("models/terrain/rock.obj", "models/terrain/rock.jpg", "terrain")

    engine.register_model("models/ground/ground.obj", "models/ground/ground.jpg", "ground")
    engine.register_model("models/house/house.obj", "models/house/house.png", "house")
    engine.register_model("models/caixa/caixa.obj", "models/caixa/caixa.jpg", "cube")
    engine.register_model("models/monster/monster.obj", "models/monster/monster.jpg", "monster")
    engine.register_model("models/fabienne/fabienne.obj", "models/fabienne/fabienne.jpg", "fabienne")

    engine.register_model("models/denis/denis.obj", "models/denis/denis.jpg", "denis")
    # engine.register_model("models/tree/Tree1.obj", "models/tree/BarkDecidious0143_5_S.jpg", "tree")

    # sky and terrain
    sky = Object(engine.models["sky"])
    sky.rescale((1, 1, 1))
    terrain = Object(engine.models["terrain"])
    terrain.rescale((0.2, 0.1, 0.2))
    terrain.move((0, -1.5, 0))

    ambient = Scene("ambient", [sky, terrain])

    # house model
    house = Object(engine.models["house"])
    ground = Object(engine.models["ground"])
    ground.rescale((10, 0.1, 10))

    # boxes
    a, b = -3, 3
    boxes = generate(engine.models["cube"], 2, a, b)

    # monster
    monster = Object(engine.models["monster"])
    monster.move((0, 0, -2))
    monster.rescale((0.5, 0.5, 0.5))

    # fabienne
    fabienne = Object(engine.models["fabienne"])
    fabienn_scale = 1e-2
    fabienne.rescale(tuple([fabienn_scale] * 3))
    fabienne.move((-3, 0, 4))
    fabienne.rotate((0, 1, 0))

    inside = Scene("inside", [house] + boxes + [ground] + [monster] + [fabienne])

    # denis
    denis = Object(engine.models["denis"])
    denis_scale = 1e-2
    denis.rescale(tuple([denis_scale] * 3))
    denis.move((0, 0, 5))

    # trees
    # trees = generate(engine.models["tree"], 100, a, b)

    # car
    # car = Object(engine.models["car"])
    outside = Scene("outside", [denis])

    engine.register_scene(ambient)
    engine.register_scene(inside)
    engine.register_scene(outside)

    try:
        game.start()
    except KeyboardInterrupt:
        pass
    finally:
        game.stop()


if __name__ == "__main__":
    main()
