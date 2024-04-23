import random

import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram
import glm
import numpy as np
from PIL import Image

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

    def load_texture(file_path):
        image = Image.open(file_path)
        image = image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        img_data = np.array(list(image.getdata()), np.uint8)
        texture_id = glGenTextures(1)

        glBindTexture(GL_TEXTURE_2D, texture_id)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image.width, image.height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)

        return texture_id

    def load_obj(file_path):
        vertices = []
        texture_coords = []
        faces = []

        with open(file_path, 'r') as file:
            for line in file:
                if line.startswith('v '):
                    vertices.append(list(map(float, line.strip().split()[1:4])))
                elif line.startswith('vt '):
                    texture_coords.append(list(map(float, line.strip().split()[1:3])))
                elif line.startswith('f '):
                    face = line.strip().split()[1:]
                    face = [list(map(int, f.split('/'))) for f in face]
                    faces.append(face)

        return vertices, texture_coords, faces

    class Model:
        def __init__(self, obj_file=None, texture_file=None):
            self.vertices = None
            self.triangle_vertices = None
            self.texture_coords = None
            self.faces = None

            self.vao = None
            self.vbo = None
            self.texture_id = None

            if obj_file and texture_file:
                self.load(obj_file, texture_file)

        def load(self, obj_file, texture_file):
            self.vertices, self.texture_coords, self.faces = load_obj(obj_file)

            triangle_vertices = []
            for face in self.faces:
                for i in range(1, len(face) - 1):
                    for idx in [0, i, i + 1]:
                        vertex = self.vertices[face[idx][0] - 1]
                        texture_coord = self.texture_coords[face[idx][1] - 1]
                        triangle_vertices.extend(vertex)
                        triangle_vertices.extend(texture_coord)

            self.triangle_vertices = np.array(triangle_vertices, dtype=np.float32)

            self.vao = glGenVertexArrays(1)
            glBindVertexArray(self.vao)

            self.vbo = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
            glBufferData(GL_ARRAY_BUFFER, self.triangle_vertices, GL_STATIC_DRAW)

            position = glGetAttribLocation(shader_program, "position")
            glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 5 * sizeof(GLfloat), None)
            glEnableVertexAttribArray(position)

            texture_coord = glGetAttribLocation(shader_program, "texture_coord")
            glVertexAttribPointer(texture_coord, 2, GL_FLOAT, GL_FALSE, 5 * sizeof(GLfloat),
                                  ctypes.c_void_p(3 * sizeof(GLfloat)))
            glEnableVertexAttribArray(texture_coord)

            self.texture_id = load_texture(texture_file)
            glUniform1i(glGetUniformLocation(shader_program, "samplerTexture"), 0)

        def draw(self):
            glBindVertexArray(self.vao)
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.texture_id)
            glDrawArrays(GL_TRIANGLES, 0, len(self.triangle_vertices) // 5)

    class Object:
        def __init__(self, model=None):
            self.model = model
            self.position = glm.vec3(0.0, 0.0, 0.0)
            self.rotation = glm.vec3(0.0, 0.0, 0.0)
            self.scale = glm.vec3(1.0, 1.0, 1.0)

        def set_model(self, model):
            self.model = model

        def draw(self):
            model = glm.mat4(1.0)
            model = glm.translate(model, self.position)
            model = glm.rotate(model, self.rotation.x, glm.vec3(1.0, 0.0, 0.0))
            model = glm.rotate(model, self.rotation.y, glm.vec3(0.0, 1.0, 0.0))
            model = glm.rotate(model, self.rotation.z, glm.vec3(0.0, 0.0, 1.0))
            model = glm.scale(model, self.scale)
            glUniformMatrix4fv(glGetUniformLocation(shader_program, "model"), 1, GL_FALSE, glm.value_ptr(model))
            self.model.draw()

    n = 3
    cube_model = Model()
    cube_model.load("models/caixa/caixa.obj", "models/caixa/caixa.jpg")

    monster_model = Model("models/monster/monster.obj", "models/monster/monster.jpg")
    monster = Object(monster_model)

    sky_model = Model("models/sky/sky.obj", "models/sky/sky.jpg")
    sky = Object(sky_model)
    sky.scale = glm.vec3(1, 1, 1)

    ground_model = Model("models/ground/ground.obj", "models/ground/ground.jpg")
    ground = Object(ground_model)
    ground.scale = glm.vec3(100, 0.1, 100)
    ground.position = glm.vec3(0, -1, 0)

    cubes = [Object(cube_model) for _ in range(n)]

    # set cubes positions randomly
    for cube in cubes:
        cube.position = glm.vec3(random.uniform(a, b), random.uniform(a, b), random.uniform(a, b))

    class Engine:
        def __init__(self):
            self.objects = []

        def add_objects(self, obj):
            if isinstance(obj, list):
                self.objects.extend(obj)
            else:
                self.objects.append(obj)

        def draw(self):
            for obj in self.objects:
                obj.draw()

    engine = Engine()
    engine.add_objects(cubes)
    engine.add_objects(monster)
    engine.add_objects(sky)
    engine.add_objects(ground)

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

    # Clear resources
    glfw.terminate()


if __name__ == "__main__":
    main()
