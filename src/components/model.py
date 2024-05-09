import os

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


def read_wavefront(file_path):
    vertices = []
    texture_coords = []
    material = "default"
    faces = {material: []}

    with open(file_path, 'r') as file:
        for line in file:
            if line.startswith('v '):
                vertices.append(list(map(float, line.strip().split()[1:4])))
            elif line.startswith('vt '):
                texture_coords.append(list(map(float, line.strip().split()[1:3])))
            elif line.startswith('usemtl') or line.startswith('usemat'):
                material = line.strip().split()[1]
                if material not in faces:
                    faces[material] = []
            elif line.startswith('f '):
                face = line.strip().split()[1:]
                face = [list(map(int, f.split('/'))) for f in face]
                faces[material].append(face)

    if not faces["default"]:
        faces.pop("default")

    return vertices, texture_coords, faces


class Model:
    def __init__(self, shader_program: ShaderProgram, root_dir: str):
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

        self.root_dir = root_dir
        wavefront_file = None

        for file in os.listdir(root_dir):
            if file.endswith('.obj'):
                wavefront_file = os.path.join(root_dir, file)
                break

        if not wavefront_file:
            raise FileNotFoundError("No obj file found in directory")

        self.available_textures = self.get_textures(root_dir)
        self.load(wavefront_file)

    @staticmethod
    def get_textures(root_dir):
        # for each .jpg, .png, .jpeg file in root_dir, return the file path
        textures = {}
        for file in os.listdir(root_dir):
            if file.endswith(('.jpg', '.png', '.jpeg')):
                textures[os.path.basename(file).split('.')[0]] = os.path.join(root_dir, file)

        return textures

    def load(self, wavefront_file):
        self.vertices, self.texture_coords, self.faces = read_wavefront(wavefront_file)

        triangle_vertices = []
        for material in self.faces:
            for face in self.faces[material]:
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

        self.texture_ids = []

        if "default" in self.faces:
            if len(self.available_textures) == 0:
                raise FileNotFoundError("No texture file found and no material specified in OBJ")

            obj_name = os.path.basename(wavefront_file).split('.')[0]

            if self.available_textures.get(obj_name, None) is not None:
                self.faces[obj_name] = self.faces.pop("default")
            else:
                raise FileNotFoundError("Unnamed material with no texture with the obj file name found")

        for material in self.faces:
            if material not in self.available_textures:
                continue
            texture_id = load_texture(self.available_textures[material])
            self.texture_ids.append(texture_id)
        glUniform1i(glGetUniformLocation(self.shader_program, "samplerTexture"), 0)

    def draw(self, matrix):
        glUniformMatrix4fv(glGetUniformLocation(self.shader_program, "model"), 1, GL_FALSE, glm.value_ptr(matrix))
        glBindVertexArray(self.vao)
        glActiveTexture(GL_TEXTURE0)
        for texture_id in self.texture_ids:
            glBindTexture(GL_TEXTURE_2D, texture_id)
            # glDrawArrays(GL_TRIANGLES, 0, len(self.triangle_vertices) // 5)  # this draws all faces
            # should draw only face related to the texture
