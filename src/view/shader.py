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
