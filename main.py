import random
import threading

import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram
import glm
import numpy as np

from src.object import Model, Object

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

from src.server import Multiplayer, Server, Engine

conn = Multiplayer()
server = None

try:
    conn.connect()
except:
    server = Server()
    server.start()
    conn.connect()


# Callback functions
def framebuffer_size_callback(window, width, height):
    glViewport(0, 0, width, height)


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

    conn.update(f"{camera_pos.x} {camera_pos.y} {camera_pos.z} {camera_front.x} {camera_front.y} {camera_front.z}")


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

    conn.update(f"{camera_pos.x} {camera_pos.y} {camera_pos.z} {camera_front.x} {camera_front.y} {camera_front.z}")


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
    glfw.set_cursor_pos_callback(window, mouse_callback)
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

    a, b = -3, 3

    n = 3
    cube_model = Model(shader_program)
    cube_model.load("models/caixa/caixa.obj", "models/caixa/caixa.jpg")

    monster_model = Model(shader_program, "models/monster/monster.obj", "models/monster/monster.jpg")
    monster = Object(monster_model)

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

    engine = Engine()
    engine.add_objects(cubes)
    engine.add_objects(monster)
    engine.add_objects(sky)
    engine.add_objects(ground)

    # run conn.tick in a separate thread

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

    conn.disconnect()
    glfw.terminate()


if __name__ == "__main__":
    main()
    if server:
        server.stop()