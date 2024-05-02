import time

import glfw
import glm
import numpy as np
from OpenGL.GL.shaders import ShaderProgram, compileProgram
from OpenGL.GL import *

from src.view.camera import Camera
from src.engine import Engine
from src.view.window import Window


vertex_shader_source = open("shaders/vertex.glsl").read()
fragment_shader_source = open("shaders/fragment.glsl").read()


class Game:
    def __init__(self, width: int = 800, height: int = 600, title: str = "Game"):
        self.window = Window(width, height, title)
        self.camera: Camera = Camera(width, height)

        self.shader_program: ShaderProgram | None = None
        self.engine: Engine | None = None

    def create(self):
        self.window.create_window()
        self.window.setup(self.mouse_callback)
        self.create_shader()

    def create_shader(self):
        vertex_shader = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vertex_shader, vertex_shader_source)
        glCompileShader(vertex_shader)

        fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(fragment_shader, fragment_shader_source)
        glCompileShader(fragment_shader)

        self.shader_program = compileProgram(vertex_shader, fragment_shader)
        glUseProgram(self.shader_program)
        glEnable(GL_DEPTH_TEST)

        self.engine = Engine(self.shader_program)

    def start(self):
        start_time = time.time()

        framerate = 60
        delay = 1 / framerate

        while not self.window.should_close():
            self.move_camera()
            self.render()

            elapsed_time = time.time() - start_time
            if elapsed_time < delay:
                time.sleep(delay - elapsed_time)
            start_time = time.time()

            self.window.swap_buffers()
            self.window.poll_events()

    def stop(self):
        glfw.destroy_window(self.window.window)
        glfw.terminate()

    def move_camera(self):
        current_frame = glfw.get_time()
        delta = current_frame - self.window.previous_frame
        self.window.previous_frame = current_frame

        if glfw.get_key(self.window.window, glfw.KEY_ESCAPE) == glfw.PRESS:
            glfw.set_window_should_close(self.window.window, True)

        if glfw.get_key(self.window.window, glfw.KEY_W) == glfw.PRESS:
            self.camera.pos += self.camera.speed * self.camera.front * delta

        elif glfw.get_key(self.window.window, glfw.KEY_S) == glfw.PRESS:
            self.camera.pos -= self.camera.speed * self.camera.front * delta

        if glfw.get_key(self.window.window, glfw.KEY_A) == glfw.PRESS:
            self.camera.pos -= glm.normalize(glm.cross(self.camera.front, self.camera.up)) * self.camera.speed * delta

        if glfw.get_key(self.window.window, glfw.KEY_D) == glfw.PRESS:
            self.camera.pos += glm.normalize(glm.cross(self.camera.front, self.camera.up)) * self.camera.speed * delta

        if glfw.get_key(self.window.window, glfw.KEY_SPACE) == glfw.PRESS:
            self.camera.pos += self.camera.up * self.camera.speed * delta

        elif glfw.get_key(self.window.window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS:
            self.camera.pos -= self.camera.up * self.camera.speed * delta

        if glfw.get_key(self.window.window, glfw.KEY_F11) == glfw.PRESS:
            self.window.toggle_fullscreen()

    def mouse_callback(self, window, xpos, ypos):
        # global first_mouse, last_x, last_y, yaw, pitch

        if self.camera.first_mouse:
            self.camera.last_x = xpos
            self.camera.last_y = ypos
            self.camera.first_mouse = False

        xoffset = xpos - self.camera.last_x
        yoffset = self.camera.last_y - ypos
        self.camera.last_x = xpos
        self.camera.last_y = ypos

        sensitivity = 0.1
        xoffset *= sensitivity
        yoffset *= sensitivity

        self.camera.yaw += xoffset
        self.camera.pitch += yoffset

        if self.camera.pitch > 89.0:
            self.camera.pitch = 89.0
        if self.camera.pitch < -89.0:
            self.camera.pitch = -89.0

        front = glm.vec3()
        front.x = np.cos(glm.radians(self.camera.yaw)) * np.cos(glm.radians(self.camera.pitch))
        front.y = np.sin(glm.radians(self.camera.pitch))
        front.z = np.sin(glm.radians(self.camera.yaw)) * np.cos(glm.radians(self.camera.pitch))
        self.camera.front = glm.normalize(front)

    def render(self):
        glClearColor(0.2, 0.3, 0.3, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        model = glm.mat4(1.0)
        projection = glm.perspective(glm.radians(self.camera.fov), self.window.width / self.window.height, 0.1, 100.0)
        view = glm.lookAt(self.camera.pos, self.camera.pos + self.camera.front, self.camera.up)

        glUniformMatrix4fv(glGetUniformLocation(self.shader_program, "model"), 1, GL_FALSE,
                           glm.value_ptr(model))

        glUniformMatrix4fv(glGetUniformLocation(self.shader_program, "view"), 1, GL_FALSE,
                           glm.value_ptr(view))

        glUniformMatrix4fv(glGetUniformLocation(self.shader_program, "projection"), 1, GL_FALSE,
                           glm.value_ptr(projection))

        self.engine.render()
