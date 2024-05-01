from dataclasses import dataclass

import glm


@dataclass
class Camera:
    def __init__(self, width, height, pos: glm.vec3 = None, front: glm.vec3 = None, up: glm.vec3 = None):
        self.pos = pos if pos else glm.vec3(0.0, 0.0, 3.0)
        self.front = front if front else glm.vec3(0.0, 0.0, -1.0)
        self.up = up if up else glm.vec3(0.0, 1.0, 0.0)
        self.yaw = -90.0
        self.pitch = 0.0
        self.last_x = width / 2
        self.last_y = height / 2
        self.fov = 45.0
        self.first_mouse = True
        self.speed = 2
