import time
from typing import Dict

import glfw
import glm
import numpy as np
from OpenGL.GL.shaders import ShaderProgram, compileProgram
from OpenGL.GL import *

from src.components import Player
from src.view import Camera, Window
from src.engine import Engine


vertex_shader_source = open("shaders/vertex.glsl").read()
fragment_shader_source = open("shaders/fragment.glsl").read()


class Game:
    def __init__(self, width: int = 800, height: int = 600, title: str = "Game"):
        self.window = Window(width, height, title)
        self.camera: Camera = Camera(width, height)

        self.shader_program: ShaderProgram | None = None
        self.engine: Engine | None = None
        self.selected_keys = set()
        self.polygon_mode = False

        self.players: Dict[int, Player] = {}

    def create(self):
        self.window.create_window()
        self.window.set_cursor_callback(self.mouse_callback)
        self.window.set_key_callback(self.key_callback)
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

        glHint(GL_LINE_SMOOTH_HINT, GL_DONT_CARE)
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        glEnable(GL_LINE_SMOOTH)

        self.engine = Engine(self.shader_program)

    def start(self):
        start_time = time.time()

        framerate = 60
        delay = 1 / framerate

        while not self.window.should_close():
            self.tick()
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

    @property
    def current_player(self):
        return self.players.get(0, None)

    def add_player(self, player: Player):
        player.id = len(self.players)
        self.players[player.id] = player
        self.engine.register_object(player)

    def tick(self):
        current_frame = glfw.get_time()
        delta = current_frame - self.window.previous_frame

        # cap delta to 60 fps
        if delta > 1 / 60:
            delta = 1 / 60

        if self.current_player:
            self.current_player.apply_movement(self.selected_keys, self.camera.front, self.camera.up, delta)
            self.camera.position = self.current_player.position

        self.engine.tick(self.selected_keys, delta)

    def key_callback(self, window, key, scancode, action, mods):
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            glfw.set_window_should_close(window, True)

        if key == glfw.KEY_F11 and action == glfw.PRESS:
            self.window.toggle_fullscreen()
            return

        if key == glfw.KEY_P and action == glfw.PRESS:
            self.polygon_mode = not self.polygon_mode
            if self.polygon_mode:
                glPolygonMode(GL_FRONT_AND_BACK,GL_LINE)
            else:
                glPolygonMode(GL_FRONT_AND_BACK,GL_FILL)


        if action == glfw.PRESS:
            self.selected_keys.add(key)

        if action == glfw.RELEASE:
            try:
                self.selected_keys.remove(key)
            except KeyError:
                pass

    def mouse_callback(self, window, xpos, ypos):
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
        view = glm.lookAt(self.camera.position, self.camera.position + self.camera.front, self.camera.up)

        glUniformMatrix4fv(glGetUniformLocation(self.shader_program, "model"), 1, GL_FALSE,
                           glm.value_ptr(model))

        glUniformMatrix4fv(glGetUniformLocation(self.shader_program, "view"), 1, GL_FALSE,
                           glm.value_ptr(view))

        glUniformMatrix4fv(glGetUniformLocation(self.shader_program, "projection"), 1, GL_FALSE,
                           glm.value_ptr(projection))

        self.engine.render()
