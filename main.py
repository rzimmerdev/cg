import random

import glfw
from OpenGL.GL import *
import glm
import numpy as np
from PIL import Image

vertex_shader_source = open("shaders/vertex.glsl").read()
fragment_shader_source = open("shaders/fragment.glsl").read()

width, height = 800, 600

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
speed = 2.5 * 0.16


# Callback functions
def framebuffer_size_callback(window, width, height):
    glViewport(0, 0, width, height)


def process_input(window):
    global delta_time, last_frame, camera_pos, speed

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
    shader_program = glCreateProgram()
    glAttachShader(shader_program, vertex_shader)
    glAttachShader(shader_program, fragment_shader)
    glLinkProgram(shader_program)
    glDeleteShader(vertex_shader)
    glDeleteShader(fragment_shader)

    # Enable depth testing
    glEnable(GL_DEPTH_TEST)
    projection = glm.perspective(glm.radians(fov), width / height, 0.1, 100.0)

    a, b = -3, 3

    class Model:
        def __init__(self):
            self.vao = None
            self.num_faces = None
            self.texture = None

        def build(self, vertices, faces, texture_coords, image):
            VBO = glGenBuffers(1)
            VAO = glGenVertexArrays(1)
            glBindVertexArray(VAO)
            glBindBuffer(GL_ARRAY_BUFFER, VBO)
            glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 3 * sizeof(GLfloat), ctypes.c_void_p(0))
            glEnableVertexAttribArray(0)

            # Texture coordinates buffer
            texture_coords_buffer = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, texture_coords_buffer)
            glBufferData(GL_ARRAY_BUFFER, texture_coords.nbytes, texture_coords, GL_STATIC_DRAW)
            glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 2 * sizeof(GLfloat), ctypes.c_void_p(0))
            glEnableVertexAttribArray(1)

            # Create EBO (Element Buffer Object) for indices
            EBO = glGenBuffers(1)
            glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
            glBufferData(GL_ELEMENT_ARRAY_BUFFER, faces.nbytes, faces, GL_STATIC_DRAW)

            glBindVertexArray(0)

            texture = glGenTextures(1)
            # glActiveTexture(GL_TEXTURE0 + texture)
            glBindTexture(GL_TEXTURE_2D, texture)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
            glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)

            image_data = image.convert("RGBA").tobytes()
            glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, image_data)
            glGenerateMipmap(GL_TEXTURE_2D)
            glBindTexture(GL_TEXTURE_2D, 0)

            self.vao, self.num_faces, self.texture = VAO, len(faces), texture

        def load(self, path, texture_path):
            vertices = []
            faces = []
            tex_coords = []

            with open(path, 'r') as file:
                for line in file:
                    if line.startswith('v '):
                        vertex = list(map(float, line.strip().split()[1:]))
                        vertices.append(vertex)
                    elif line.startswith('f '):
                        face = [int(vertex.split('/')[0]) - 1 for vertex in line.strip().split()[1:]]
                        faces.append(face)
                    elif line.startswith('vt '):
                        uv = list(map(float, line.strip().split()[1:]))
                        tex_coords.append(uv)

            image = Image.open(texture_path)
            image = image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)  # OpenGL expects the image to be flipped

            vertices = np.array(vertices, dtype=np.float32)
            faces = np.array(faces, dtype=np.uint32).flatten()
            tex_coords = np.array(tex_coords, dtype=np.float32)

            self.build(vertices, faces, tex_coords, image)

        def draw(self, shader_program, pos, rot, scale):
            model = glm.translate(glm.mat4(1.0), pos)
            model = glm.rotate(model, glm.radians(rot.x), glm.vec3(1, 0, 0))
            model = glm.rotate(model, glm.radians(rot.y), glm.vec3(0, 1, 0))
            model = glm.rotate(model, glm.radians(rot.z), glm.vec3(0, 0, 1))
            model = glm.scale(model, scale)
            glUniformMatrix4fv(glGetUniformLocation(shader_program, "model"), 1, GL_FALSE, glm.value_ptr(model))
            glUniformMatrix4fv(glGetUniformLocation(shader_program, "view"), 1, GL_FALSE, glm.value_ptr(view))
            glUniformMatrix4fv(glGetUniformLocation(shader_program, "projection"), 1, GL_FALSE, glm.value_ptr(projection))

            glBindVertexArray(self.vao)
            glDrawElements(GL_TRIANGLES, self.num_faces * 3, GL_UNSIGNED_INT, None)
            glBindVertexArray(0)

            # Bind texture
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.texture)
            glUniform1i(glGetUniformLocation(shader_program, "texture_data"), 0)

    class Object:
        def __init__(self, model: Model = None):
            self.model = model
            self._pos = glm.vec3(random.uniform(a, b), random.uniform(a, b), random.uniform(a, b))
            self._rot = glm.vec3(random.uniform(0, 360), random.uniform(0, 360), random.uniform(0, 360))
            self._scale = glm.vec3(0.51, 0.51, 0.51)

        @property
        def position(self):
            return self._pos

        def draw(self):
            if self.model:
                self.model.draw(shader_program, self._pos, self._rot, self._scale)

    n = 4
    cube_model = Model()
    cube_model.load("models/caixa/caixa.obj", "models/caixa/caixa.jpg")

    cubes = [Object(cube_model) for _ in range(n)]

    # Render loop
    while not glfw.window_should_close(window):
        # Input
        process_input(window)

        # Clear the color buffer
        glClearColor(0.2, 0.3, 0.3, 1.0)
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Activate shader program
        glUseProgram(shader_program)

        # View matrix
        view = glm.lookAt(camera_pos, camera_pos + camera_front, camera_up)

        # Set matrices
        model = glm.mat4(1.0)
        glUniformMatrix4fv(glGetUniformLocation(shader_program, "model"), 1, GL_FALSE, glm.value_ptr(model))
        glUniformMatrix4fv(glGetUniformLocation(shader_program, "view"), 1, GL_FALSE, glm.value_ptr(view))
        glUniformMatrix4fv(glGetUniformLocation(shader_program, "projection"), 1, GL_FALSE, glm.value_ptr(projection))

        for cube in cubes:
            cube.draw()

        # Swap front and back buffers
        glfw.swap_buffers(window)

        # Poll for and process events
        glfw.poll_events()

    # Clear resources
    glfw.terminate()


if __name__ == "__main__":
    main()
