import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileShader, compileProgram
import glm
from PIL import Image
import numpy as np


def window_resize(window, width, height):
    glViewport(0, 0, width, height)


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


def main():
    # Initialize GLFW
    if not glfw.init():
        return

    window_width, window_height = 800, 600

    # Create a windowed mode window and its OpenGL context
    window = glfw.create_window(window_width, window_height, "Cube with Texture", None, None)
    if not window:
        glfw.terminate()
        return

    # Make the window's context current
    glfw.make_context_current(window)
    glfw.set_window_size_callback(window, window_resize)

    vertex_shader_source = open("../shaders/vertex.glsl").read()
    fragment_shader_source = open("../shaders/fragment.glsl").read()

    vertex_shader = compileShader(vertex_shader_source, GL_VERTEX_SHADER)
    fragment_shader = compileShader(fragment_shader_source, GL_FRAGMENT_SHADER)
    shader = compileProgram(vertex_shader, fragment_shader)

    glUseProgram(shader)

    class Model:
        def __init__(self):
            self.vertices = None
            self.triangle_vertices = None
            self.texture_coords = None
            self.faces = None

            self.vao = None
            self.vbo = None
            self.texture_id = None

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

            position = glGetAttribLocation(shader, "position")
            glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 5 * sizeof(GLfloat), None)
            glEnableVertexAttribArray(position)

            texture_coord = glGetAttribLocation(shader, "texture_coord")
            glVertexAttribPointer(texture_coord, 2, GL_FLOAT, GL_FALSE, 5 * sizeof(GLfloat),
                                  ctypes.c_void_p(3 * sizeof(GLfloat)))
            glEnableVertexAttribArray(texture_coord)

            self.texture_id = load_texture(texture_file)
            glUniform1i(glGetUniformLocation(shader, "samplerTexture"), 0)

        def draw(self):
            glBindVertexArray(self.vao)
            glDrawArrays(GL_TRIANGLES, 0, len(self.triangle_vertices) // 5)

    class Object:
        def __init__(self):
            self.model = None
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
            glUniformMatrix4fv(glGetUniformLocation(shader, "model"), 1, GL_FALSE, glm.value_ptr(model))
            self.model.draw()

    # Load cube data
    # vertices, texture_coords, faces = load_obj("caixa.obj")
    #
    # # Convert faces to triangle vertices
    # triangle_vertices = []
    # for face in faces:
    #     for i in range(1, len(face) - 1):
    #         for idx in [0, i, i + 1]:
    #             vertex = vertices[face[idx][0] - 1]
    #             texture_coord = texture_coords[face[idx][1] - 1]
    #             triangle_vertices.extend(vertex)
    #             triangle_vertices.extend(texture_coord)
    #
    # triangle_vertices = np.array(triangle_vertices, dtype=np.float32)
    #
    # vao = glGenVertexArrays(1)
    # glBindVertexArray(vao)
    #
    # vbo = glGenBuffers(1)
    # glBindBuffer(GL_ARRAY_BUFFER, vbo)
    # glBufferData(GL_ARRAY_BUFFER, triangle_vertices, GL_STATIC_DRAW)
    #
    # # Specify vertex attributes
    # position = glGetAttribLocation(shader, "position")
    # glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 5 * sizeof(GLfloat), None)
    # glEnableVertexAttribArray(position)
    #
    # texture_coord = glGetAttribLocation(shader, "texture_coord")
    # glVertexAttribPointer(texture_coord, 2, GL_FLOAT, GL_FALSE, 5 * sizeof(GLfloat),
    #                       ctypes.c_void_p(3 * sizeof(GLfloat)))
    # glEnableVertexAttribArray(texture_coord)
    #
    # # Load texture
    # texture_id = load_texture("caixa.jpg")
    # glUniform1i(glGetUniformLocation(shader, "samplerTexture"), 0)
    my_model = Model()
    my_model.load("caixa.obj", "caixa.jpg")

    my_object = Object()
    my_object.set_model(my_model)

    # Set projection matrix
    projection = glm.perspective(glm.radians(45), window_width / window_height, 0.1, 1000.0)
    glUniformMatrix4fv(glGetUniformLocation(shader, "projection"), 1, GL_FALSE, glm.value_ptr(projection))

    # Set view matrix
    view = glm.lookAt(glm.vec3(0, 0, 5), glm.vec3(0, 0, 0), glm.vec3(0, 1, 0))
    glUniformMatrix4fv(glGetUniformLocation(shader, "view"), 1, GL_FALSE, glm.value_ptr(view))

    glEnable(GL_DEPTH_TEST)

    # Loop until the user closes the window
    while not glfw.window_should_close(window):
        # Clear the color and depth buffers
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Set model matrix
        my_object.rotation = glm.vec3(0.0, glfw.get_time(), 0.0)
        my_object.draw()

        # Swap front and back buffers
        glfw.swap_buffers(window)

        # Poll for and process events
        glfw.poll_events()

    glfw.terminate()


if __name__ == "__main__":
    main()
