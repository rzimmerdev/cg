import math

import glm
import numpy as np
from OpenGL.GL import *
from PIL import Image


class Shader:
    def __init__(self, vertex_shader, fragment_shader):
        with open(vertex_shader, "r") as file:
            vertex_shader = file.read()

        with open(fragment_shader, "r") as file:
            fragment_shader = file.read()

        self.vertex_shader = self.compile_shader(vertex_shader, GL_VERTEX_SHADER)
        self.fragment_shader = self.compile_shader(fragment_shader, GL_FRAGMENT_SHADER)
        self.shader_program = self.create_shader_program()

    def compile_shader(self, source, shader_type):
        shader = glCreateShader(shader_type)
        glShaderSource(shader, source)
        glCompileShader(shader)

        if not glGetShaderiv(shader, GL_COMPILE_STATUS):
            raise Exception(glGetShaderInfoLog(shader))

        return shader

    def create_shader_program(self):
        shader_program = glCreateProgram()
        glAttachShader(shader_program, self.vertex_shader)
        glAttachShader(shader_program, self.fragment_shader)
        glLinkProgram(shader_program)

        if not glGetProgramiv(shader_program, GL_LINK_STATUS):
            raise Exception(glGetProgramInfoLog(shader_program))

        return shader_program

    def use(self):
        glUseProgram(self.shader_program)

    def set_bool(self, name, value):
        glUniform1i(glGetUniformLocation(self.shader_program, name), int(value))

    def set_int(self, name, value):
        glUniform1i(glGetUniformLocation(self.shader_program, name), value)

    def set_float(self, name, value):
        glUniform1f(glGetUniformLocation(self.shader_program, name), value)

    def set_vec2(self, name, value):
        glUniform2fv(glGetUniformLocation(self.shader_program, name), 1, glm.value_ptr(value))

    def set_vec3(self, name, value):
        glUniform3fv(glGetUniformLocation(self.shader_program, name), 1, glm.value_ptr(value))

    def set_vec4(self, name, value):
        glUniform4fv(glGetUniformLocation(self.shader_program, name), 1, glm.value_ptr(value))

    def set_mat2(self, name, value):
        glUniformMatrix2fv(glGetUniformLocation(self.shader_program, name), 1, GL_FALSE, glm.value_ptr(value))

    def set_mat3(self, name, value):
        glUniformMatrix3fv(glGetUniformLocation(self.shader_program, name), 1, GL_FALSE, glm.value_ptr(value))

    def set_mat4(self, name, value):
        glUniformMatrix4fv(glGetUniformLocation(self.shader_program, name), 1, GL_FALSE, glm.value_ptr(value))

    def load_texture(self, filename):
        image = Image.open(filename)
        image = image.transpose(Image.Transpose.FLIP_TOP_BOTTOM)
        image_data = np.array(list(image.getdata()), np.uint8)

        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, image.width, image.height, 0, GL_RGB, GL_UNSIGNED_BYTE, image_data)
        glGenerateMipmap(GL_TEXTURE_2D)

        self.texture = texture

    def draw(self, object):
        self.use()
        self.set_mat4("model", object.model)
        self.set_vec3("objectColor", glm.vec3(1, 0, 0))
        self.set_vec3("lightColor", glm.vec3(1, 1, 1))
        self.set_vec3("lightPos", glm.vec3(0, 0, 0))
        self.set_vec3("viewPos", glm.vec3(0, 0, 3))

        if self.texture:
            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.texture)
            self.set_int("texture1", 0)

        VAO = glGenVertexArrays(1)
        VBO = glGenBuffers(1)
        EBO = glGenBuffers(1)
