from typing import Set

import glfw
import glm

from .object import InteractiveObject


class Player(InteractiveObject):
    def apply_movement(self, key_actions: Set[int], front, up, delta: float):
        if glfw.KEY_W in key_actions:
            self.position += self.speed * front * delta

        if glfw.KEY_S in key_actions:
            self.position -= self.speed * front * delta

        if glfw.KEY_A in key_actions:
            self.position -= glm.normalize(glm.cross(front, up)) * self.speed * delta

        if glfw.KEY_D in key_actions:
            self.position += glm.normalize(glm.cross(front, up)) * self.speed * delta

        if glfw.KEY_SPACE in key_actions:
            self.position += up * self.speed * delta

        if glfw.KEY_LEFT_SHIFT in key_actions:
            self.position -= up * self.speed * delta
