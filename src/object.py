from OpenGL.GL import *
import glm
import numpy as np
from OpenGL.GL.shaders import ShaderProgram
from PIL import Image


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
    def __init__(self, shader_program: ShaderProgram, obj_file=None, texture_files=None):
        self.vertices = None
        self.triangle_vertices = None
        self.texture_coords = None
        self.faces = None

        self.vao = None
        self.vbo = None
        self.texture_ids = None

        self.shader_program = shader_program
        if not isinstance(shader_program, ShaderProgram):
            raise ValueError("Invalid argument passed as shader program")

        if obj_file and texture_files:
            self.load(obj_file, texture_files)

    def load(self, obj_file, texture_files):
        if not isinstance(texture_files, list):
            texture_files = [texture_files]
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

        position = glGetAttribLocation(self.shader_program, "position")
        glVertexAttribPointer(position, 3, GL_FLOAT, GL_FALSE, 5 * sizeof(GLfloat), None)
        glEnableVertexAttribArray(position)

        texture_coord = glGetAttribLocation(self.shader_program, "texture_coord")
        glVertexAttribPointer(texture_coord, 2, GL_FLOAT, GL_FALSE, 5 * sizeof(GLfloat),
                              ctypes.c_void_p(3 * sizeof(GLfloat)))
        glEnableVertexAttribArray(texture_coord)

        self.texture_ids = [load_texture(texture_file) for texture_file in texture_files]
        glUniform1i(glGetUniformLocation(self.shader_program, "samplerTexture"), 0)

    def draw(self, matrix):
        glUniformMatrix4fv(glGetUniformLocation(self.shader_program, "model"), 1, GL_FALSE, glm.value_ptr(matrix))
        glBindVertexArray(self.vao)
        glActiveTexture(GL_TEXTURE0)
        for texture_id in self.texture_ids:
            glBindTexture(GL_TEXTURE_2D, texture_id)
            glDrawArrays(GL_TRIANGLES, 0, len(self.triangle_vertices) // 5)  # this draws all faces
            # should draw only face related to the texture


class Object:
    def __init__(self, model: Model = None):
        self.model = model
        self.position = glm.vec3(0.0, 0.0, 0.0)
        self.rotation = glm.vec3(0.0, 0.0, 0.0)
        self.scale = glm.vec3(1.0, 1.0, 1.0)

    def set_model(self, model):
        self.model = model

    def draw(self):
        matrix = glm.mat4(1.0)
        matrix = glm.translate(matrix, self.position)
        matrix = glm.rotate(matrix, self.rotation.x, glm.vec3(1.0, 0.0, 0.0))
        matrix = glm.rotate(matrix, self.rotation.y, glm.vec3(0.0, 1.0, 0.0))
        matrix = glm.rotate(matrix, self.rotation.z, glm.vec3(0.0, 0.0, 1.0))
        matrix = glm.scale(matrix, self.scale)
        self.model.draw(matrix)
