from dataclasses import dataclass
from typing import Set

import glfw
import glm
from OpenGL.GL import glUniform3fv, glGetUniformLocation


@dataclass
class Camera:
    """
    Dataclass para a câmera do jogo.

    Atributos:

    - position: A posição da câmera no mundo.
    - front: A direção para a qual a câmera está olhando.
    - up: O vetor que aponta para cima. (0, 1, 0) é o padrão. Serve para lidar com rotações.
    - yaw: O ângulo em torno do eixo y.
    - pitch: O ângulo em torno do eixo x.
    - last_x: A última posição x do cursor.
    - last_y: A última posição y do cursor.
    - fov: O campo de visão da câmera.
    - first_mouse: Flag para indicar se é a primeira vez que o mouse é movido.
    """
    def __init__(self, width, height, pos: glm.vec3 = None, front: glm.vec3 = None, up: glm.vec3 = None):
        self.position = pos if pos else glm.vec3(0.0, 0.0, 3.0)
        self.front = front if front else glm.vec3(0.0, 0.0, -1.0)
        self.up = up if up else glm.vec3(0.0, 1.0, 0.0)
        self.yaw = -90.0
        self.pitch = 0.0
        self.last_x = width / 2
        self.last_y = height / 2
        self.fov = 45.0
        self.first_mouse = True
        self.speed = 2

    def apply_movement(self, key_actions: Set[int], delta: float):
        if glfw.KEY_W in key_actions:
            self.position += self.speed * self.front * delta

        if glfw.KEY_S in key_actions:
            self.position -= self.speed * self.front * delta

        if glfw.KEY_A in key_actions:
            self.position -= glm.normalize(glm.cross(self.front, self.up)) * self.speed * delta

        if glfw.KEY_D in key_actions:
            self.position += glm.normalize(glm.cross(self.front, self.up)) * self.speed * delta

        if glfw.KEY_SPACE in key_actions:
            self.position += self.up * self.speed * delta

        if glfw.KEY_LEFT_SHIFT in key_actions:
            self.position -= self.up * self.speed * delta

    def update(self, shader_program):
        # update in vec3 cameraPos
        glUniform3fv(glGetUniformLocation(shader_program, "cameraPos"), 1, glm.value_ptr(self.position))
