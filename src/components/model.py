import os
from typing import List

from OpenGL.GL import *
import glm
import numpy as np
from OpenGL.GL.shaders import ShaderProgram
from PIL import Image


def load_texture(file_path) -> int:
    """
    Função para carregar uma textura de um arquivo de imagem.

    :param file_path: Caminho do arquivo de imagem.
    :return: ID da textura carregada na GPU. Corresponde à posição na memória e permite organizar várias texturas.
    Sem ter que contar os vértices manualmente.
    """
    image = Image.open(file_path)
    img_data = image.convert("RGBA").tobytes("raw", "RGBA", 0, -1)
    texture_id = glGenTextures(1)

    glBindTexture(GL_TEXTURE_2D, texture_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, image.width, image.height, 0, GL_RGBA, GL_UNSIGNED_BYTE, img_data)

    return texture_id


def read_wavefront(file_path):
    """
    Função para ler um arquivo .obj e retornar os vértices, coordenadas de textura e faces.

    :param file_path: Caminho do arquivo .obj.
    :return: Uma tupla com os vértices, coordenadas de textura e faces.
    """
    vertices = []
    texture_coords = []
    normals = []
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
            elif line.startswith('vn '):
                normals.append(list(map(float, line.strip().split()[1:4])))

    if not faces["default"]:
        faces.pop("default")

    return vertices, texture_coords, faces, normals


class Model:
    def __init__(self, shader_program: ShaderProgram, root_dir: str):
        self.textures = None
        self.vertices = None
        self.triangle_vertices = None
        self.triangle_normals = None
        self.texture_coords = None
        self.faces = None
        self.normals = None

        self.vao = None  # Vertex Array Object
        self.vbo = None  # Vertex Buffer Object
        self.texture_ids = None

        self.ambient_coefficient = 0.1
        self.diffuse_coefficient = 0.7
        self.specular_coefficient = 0.2
        self.shininess = 1

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
        # Para cada arquivo JPG, PNG e JPEG em root_dir, retorna o caminho do arquivo
        textures = {}
        for file in os.listdir(root_dir):
            if file.endswith(('.jpg', '.png', '.jpeg')):
                textures[os.path.basename(file).split('.')[0]] = os.path.join(root_dir, file)

        return textures

    def setup_buffers(self):
        """
        Cria e configura os buffers de vértices, coordenadas de textura e normais.
        Passo inicial para renderizar o modelo, carregando os dados na GPU.

        Precisa ter setado self.triangle_vertices, self.textures e self.triangle_normals

        :return: None
        """
        self.vao = glGenVertexArrays(1)
        self.vbo = glGenBuffers(1)

        glBindVertexArray(self.vao)
        glBindBuffer(GL_ARRAY_BUFFER, self.vbo)

        total_vertices = np.concatenate(list(self.triangle_vertices.values()))
        total_texture_coords = np.concatenate(list(self.textures.values()))
        total_normals = np.concatenate(list(self.triangle_normals.values()))

        vertices_size = total_vertices.nbytes
        textures_size = total_texture_coords.nbytes
        normals_size = total_normals.nbytes

        glBufferData(GL_ARRAY_BUFFER, vertices_size + textures_size + normals_size, None, GL_STATIC_DRAW)
        glBufferSubData(GL_ARRAY_BUFFER, 0, vertices_size, total_vertices)
        glBufferSubData(GL_ARRAY_BUFFER, vertices_size, textures_size, total_texture_coords)
        glBufferSubData(GL_ARRAY_BUFFER, vertices_size + textures_size, normals_size, total_normals)

        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
        glEnableVertexAttribArray(0)

        glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(vertices_size))
        glEnableVertexAttribArray(1)

        glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 0, ctypes.c_void_p(vertices_size + textures_size))
        glEnableVertexAttribArray(2)

        glBindBuffer(GL_ARRAY_BUFFER, 0)
        glBindVertexArray(0)

    def load(self, wavefront_file):
        """
        Dado um arquivo Wavefront (OBJ), busca os vértices, coordenadas de textura e faces.
        Também carrega texturas definidas no OBJ (não suporta MTL) que estejam no mesmo diretório.

        :param wavefront_file: Caminho do arquivo Wavefront (OBJ).
        :return: None
        """
        self.vertices, self.texture_coords, self.faces, self.normals = read_wavefront(wavefront_file)

        if "default" in self.faces:
            if len(self.available_textures) == 0:
                raise FileNotFoundError("No texture file found and no material specified in OBJ")

            obj_name = os.path.basename(wavefront_file).split('.')[0]

            if self.available_textures.get(obj_name, None) is not None:
                self.faces[obj_name] = self.faces.pop("default")
            else:
                raise FileNotFoundError("Unnamed material with no texture with the obj file name found")

        self.texture_ids = {}
        self.textures = {}
        self.triangle_vertices = {}
        self.triangle_normals = {}

        for material in self.faces:
            if material not in self.available_textures:
                continue

            texture_id = load_texture(self.available_textures[material])
            self.texture_ids[material] = texture_id

            triangle_vertice = []
            triangle_normals = []
            texture_vertice = []

            for face in self.faces[material]:  # Para cada face
                for i in range(1, len(face) - 1):  # Para cada vertice da face, cria um triângulo, ex: quadrado vira dois triângulos
                    for idx in [0, i, i + 1]:  # Cria um triângulo
                        vertex = self.vertices[face[idx][0] - 1]
                        texture_coord = self.texture_coords[face[idx][1] - 1]
                        triangle_vertice.extend(vertex)
                        texture_vertice.extend(texture_coord)
                        # copia a normal para cada face nova criada
                        if self.normals: # fazer alguma coisa com a normal aqui
                            normals = self.normals[face[idx][2] - 1]
                            triangle_normals.extend(normals)

            # just copy normals to equate number of new faces
            self.triangle_vertices[material] = np.array(triangle_vertice, dtype=np.float32)
            self.textures[material] = np.array(texture_vertice, dtype=np.float32)
            self.triangle_normals[material] = np.array(triangle_normals, dtype=np.float32)

        self.setup_buffers()

    def draw(self, matrix, light_sources: List = None):
        if not self.vao:
            self.setup_buffers()

        # Send the model matrix to the shader
        glUniformMatrix4fv(glGetUniformLocation(self.shader_program, "model"), 1, GL_FALSE, glm.value_ptr(matrix))

        # set k_a, k_d, k_s
        glUniform1f(glGetUniformLocation(self.shader_program, "ambientCoefficient"), self.ambient_coefficient)
        glUniform1f(glGetUniformLocation(self.shader_program, "diffuseCoefficient"), self.diffuse_coefficient)
        glUniform1f(glGetUniformLocation(self.shader_program, "specularCoefficient"), self.specular_coefficient)

        glUniform1f(glGetUniformLocation(self.shader_program, "shininess"), self.shininess)

        num_lights = int(len(light_sources) - 1 if light_sources else 0)
        glUniform1i(glGetUniformLocation(self.shader_program, "numLights"), num_lights)

        ambient_light = glm.vec3(0.0, 0.0, 0.0) if not light_sources else light_sources[0].luminance

        glUniform3fv(glGetUniformLocation(self.shader_program, "ambientLight"), 1, glm.value_ptr(ambient_light))

        if num_lights > 0:
            light_sources = light_sources[1:10]

            # Send light positions and colors to the shader
            light_positions = [light.position for light in light_sources]
            light_colors = [light.luminance for light in light_sources]

            for i, (position, color) in enumerate(zip(light_positions, light_colors)):
                glUniform3fv(glGetUniformLocation(self.shader_program, f"lightPos[{i}]"), 1, glm.value_ptr(position))
                glUniform3fv(glGetUniformLocation(self.shader_program, f"lightColor[{i}]"), 1, glm.value_ptr(color))

        for material in self.triangle_vertices:
            glBindTexture(GL_TEXTURE_2D, self.texture_ids[material])

            # bind normal to
            glBindVertexArray(self.vao)
            # Divide by 3 because there are 3 coordinates per triangle
            glDrawArrays(GL_TRIANGLES, 0, len(self.triangle_vertices[material]) // 3)
            glBindVertexArray(0)

        glBindTexture(GL_TEXTURE_2D, 0)

        # remove light sources
        glUniform1i(glGetUniformLocation(self.shader_program, "numLights"), 0)
        glUniform3fv(glGetUniformLocation(self.shader_program, "ambientLight"), 1,
                     glm.value_ptr(glm.vec3(0.0, 0.0, 0.0)))
