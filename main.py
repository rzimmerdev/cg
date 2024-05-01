import random

from src.game import Game
from src.components import Object, Scene


def main():
    game = Game()
    game.create()

    a, b = -3, 3

    engine = game.engine

    engine.register_model("models/caixa/caixa.obj", "models/caixa/caixa.jpg", "cube")
    engine.register_model("models/sky/sky.obj", "models/sky/sky.jpg", "sky")
    engine.register_model("models/ground/ground.obj", "models/ground/ground.jpg", "ground")

    sky = Object(engine.models["sky"])
    sky.rescale((1, 1, 1))

    ground = Object(engine.models["ground"])
    ground.rescale((100, 0.1, 100))
    ground.move((0, -1, 0))

    n = 3
    cubes = []

    for _ in range(n):
        pos = tuple(random.uniform(a, b) for _ in range(3))

        cube = Object(engine.models["cube"])
        cube.move(pos)
        cubes.append(cube)

    engine.register_scene(Scene("main", [sky, ground, cubes]))

    try:
        game.start()
    except KeyboardInterrupt:
        pass
    finally:
        game.stop()


if __name__ == "__main__":
    main()
