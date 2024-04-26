import random

import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram
import glm
import numpy as np

from src.objects.object import Model, Object

vertex_shader_source = open("shaders/vertex.glsl").read()
fragment_shader_source = open("shaders/fragment.glsl").read()

width, height = 800, 600

fullscreen = False


def window_resize(window, width, height):
    glViewport(0, 0, width, height)


camera_pos = glm.vec3(0.0, 0.0, 3.0)
camera_front = glm.vec3(0.0, 0.0, -1.0)
camera_up = glm.vec3(0.0, 1.0, 0.0)
yaw = -90.0
pitch = 0.0
last_x, last_y = width / 2, height / 2
fov = 45.0
first_mouse = True

# Time
delta_time = 0.0
last_frame = 0.0

# Movement speed
speed = 2


class Camera:
    def __init__(self, pos: glm.vec3, front: glm.vec3, up: glm.vec3):
        self.pos = pos
        self.front = front
        self.up = up
        self.yaw = -90.0
        self.pitch = 0.0
        self.last_x = width / 2
        self.last_y = height / 2
        self.fov = 45.0
        self.first_mouse = True


class Window:
    def __init__(self, width: int, height: int, title: str):
        self.width = width
        self.height = height
        self.title = title
        self.window = None

    def create_window(self):
        if not glfw.init():
            return

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

        self.window = glfw.create_window(self.width, self.height, self.title, None, None)
        if not self.window:
            glfw.terminate()
            return

        glfw.make_context_current(self.window)
        glfw.set_framebuffer_size_callback(self.window, window_resize)
        glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_DISABLED)
        return self.window

    def setup(self, mouse_callback):
        glfw.set_cursor_pos_callback(self.window, mouse_callback)

    def close_window(self):
        glfw.terminate()

    def set_framebuffer_size_callback(self, callback):
        glfw.set_framebuffer_size_callback(self.window, callback)

    def set_cursor_pos_callback(self, callback):
        glfw.set_cursor_pos_callback(self.window, callback)

    def set_input_mode(self, mode):
        glfw.set_input_mode(self.window, glfw.CURSOR, mode)

    def should_close(self):
        return glfw.window_should_close(self.window)

    def swap_buffers(self):
        glfw.swap_buffers(self.window)

    def poll_events(self):
        glfw.poll_events()

    def terminate(self):
        glfw.terminate()


class Game:
    def __init__(self):
        self.engine = None
        self.window = None
        self.current_camera = None
        self.shader_program = None

    def load(self):
        self.window = Window(width, height, "Game")
        self.window.create_window()

        self.setup_shader_program()

        self.current_camera = Camera(camera_pos, camera_front, camera_up)


    def setup_shader_program(self):
        vertex_shader = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vertex_shader, vertex_shader_source)
        glCompileShader(vertex_shader)

        fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(fragment_shader, fragment_shader_source)
        glCompileShader(fragment_shader)

        self.shader_program = compileProgram(vertex_shader, fragment_shader)
        glUseProgram(self.shader_program)

        glEnable(GL_DEPTH_TEST)

    def start(self):
        self.engine = Engine(self.shader_program)
        self.engine.start()

    def process_input(self):
        pass

    def render(self):
        pass

    def main_loop(self):
        while not self.window.should_close():
            self.process_input()
            self.render()
            self.window.swap_buffers()
            self.window.poll_events()



from src.engine import Engine, Server


# Callback functions
def framebuffer_size_callback(window, width, height):
    glViewport(0, 0, width, height)


def main():
    # Initialize GLFW
    if not glfw.init():
        return

    # Configure GLFW
    glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
    glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
    glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(width, height, "LearnOpenGL", None, None)
    if not window:
        glfw.terminate()
        return

    # Make the window's context current
    glfw.make_context_current(window)
    glfw.set_framebuffer_size_callback(window, framebuffer_size_callback)
    glfw.set_input_mode(window, glfw.CURSOR, glfw.CURSOR_DISABLED)

    # Compile shaders
    vertex_shader = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vertex_shader, vertex_shader_source)
    glCompileShader(vertex_shader)

    fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(fragment_shader, fragment_shader_source)
    glCompileShader(fragment_shader)

    # Create shader program
    shader_program = compileProgram(vertex_shader, fragment_shader)
    glUseProgram(shader_program)

    # Enable depth testing
    glEnable(GL_DEPTH_TEST)
    projection = glm.perspective(glm.radians(fov), width / height, 0.1, 100.0)

    engine = Engine(shader_program)
    server = None

    try:
        player_id = engine.conn.connect()
    except ConnectionRefusedError:
        server = Server()
        server.start()
        player_id = engine.conn.connect()

    def process_input(window):
        global delta_time, last_frame, camera_pos, speed, fullscreen, width, height

        current_frame = glfw.get_time()
        delta_time = current_frame - last_frame
        last_frame = current_frame

        if glfw.get_key(window, glfw.KEY_ESCAPE) == glfw.PRESS:
            glfw.set_window_should_close(window, True)

        if glfw.get_key(window, glfw.KEY_W) == glfw.PRESS:
            camera_pos += speed * camera_front * delta_time

        if glfw.get_key(window, glfw.KEY_S) == glfw.PRESS:
            camera_pos -= speed * camera_front * delta_time

        if glfw.get_key(window, glfw.KEY_A) == glfw.PRESS:
            camera_pos -= glm.normalize(glm.cross(camera_front, camera_up)) * speed * delta_time

        if glfw.get_key(window, glfw.KEY_D) == glfw.PRESS:
            camera_pos += glm.normalize(glm.cross(camera_front, camera_up)) * speed * delta_time

        if glfw.get_key(window, glfw.KEY_SPACE) == glfw.PRESS:
            camera_pos += camera_up * speed * delta_time

        if glfw.get_key(window, glfw.KEY_LEFT_SHIFT) == glfw.PRESS:
            camera_pos -= camera_up * speed * delta_time

        if glfw.get_key(window, glfw.KEY_F11) == glfw.PRESS:
            if fullscreen:
                glfw.set_window_monitor(window, None, 100, 100, width, height, glfw.DONT_CARE)
                fullscreen = False
            else:
                monitor = glfw.get_primary_monitor()
                mode = glfw.get_video_mode(monitor)
                glfw.set_window_monitor(window, monitor, 0, 0, mode.size.width, mode.size.height, mode.refresh_rate)
                fullscreen = True

        msg = {player_id: [camera_pos.x,
                           camera_pos.y,
                           camera_pos.z,
                           camera_front.x,
                           camera_front.y,
                           camera_front.z,
                           ]}
        engine.conn.update(msg)

    def mouse_callback(window, xpos, ypos):
        global first_mouse, last_x, last_y, yaw, pitch

        if first_mouse:
            last_x = xpos
            last_y = ypos
            first_mouse = False

        xoffset = xpos - last_x
        yoffset = last_y - ypos
        last_x = xpos
        last_y = ypos

        sensitivity = 0.1
        xoffset *= sensitivity
        yoffset *= sensitivity

        yaw += xoffset
        pitch += yoffset

        if pitch > 89.0:
            pitch = 89.0
        if pitch < -89.0:
            pitch = -89.0

        front = glm.vec3()
        front.x = np.cos(glm.radians(yaw)) * np.cos(glm.radians(pitch))
        front.y = np.sin(glm.radians(pitch))
        front.z = np.sin(glm.radians(yaw)) * np.cos(glm.radians(pitch))
        global camera_front
        camera_front = glm.normalize(front)

        msg = {player_id: [camera_pos.x,
                           camera_pos.y,
                           camera_pos.z,
                           camera_front.x,
                           camera_front.y,
                           camera_front.z,
                           ]}
        engine.conn.update(msg)

    glfw.set_cursor_pos_callback(window, mouse_callback)

    a, b = -3, 3

    n = 3
    cube_model = Model(shader_program)
    cube_model.load("models/caixa/caixa.obj", "models/caixa/caixa.jpg")

    sky_model = Model(shader_program, "models/sky/sky.obj", "models/sky/sky.jpg")
    sky = Object(sky_model)
    sky.scale = glm.vec3(1, 1, 1)

    ground_model = Model(shader_program, "models/ground/ground.obj", "models/ground/ground.jpg")
    ground = Object(ground_model)
    ground.scale = glm.vec3(100, 0.1, 100)
    ground.position = glm.vec3(0, -1, 0)

    cubes = [Object(cube_model) for _ in range(n)]

    # set cubes positions randomly
    for cube in cubes:
        cube.position = glm.vec3(random.uniform(a, b), random.uniform(a, b), random.uniform(a, b))

    engine.add_objects(cubes)
    engine.add_objects(sky)
    engine.add_objects(ground)

    # run conn.tick in a separate thread
    engine.start()

    # Render loop
    while not glfw.window_should_close(window):
        # Input
        process_input(window)

        # Clear the color buffer
        glClearColor(0.2, 0.3, 0.3, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # View matrix
        view = glm.lookAt(camera_pos, camera_pos + camera_front, camera_up)

        # Set matrices
        model = glm.mat4(1.0)
        glUniformMatrix4fv(glGetUniformLocation(shader_program, "model"), 1, GL_FALSE, glm.value_ptr(model))
        glUniformMatrix4fv(glGetUniformLocation(shader_program, "view"), 1, GL_FALSE, glm.value_ptr(view))
        glUniformMatrix4fv(glGetUniformLocation(shader_program, "projection"), 1, GL_FALSE, glm.value_ptr(projection))

        engine.draw()

        # Swap front and back buffers
        glfw.swap_buffers(window)

        # Poll for and process events
        glfw.poll_events()

    engine.conn.disconnect()
    glfw.terminate()
    return server


if __name__ == "__main__":
    server = main()
    if server:
        server.stop()
