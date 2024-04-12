import glfw
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
import numpy as np
import glm
from object import Object
from teapot import teapot

# OBJ file path
obj_path = "models/cube.obj"

# Vertex shader source code - shaders/vertex.vs
vertex_shader = open("shaders/vertex.cpp", "r").read()

# Fragment shader source code - shaders/fragment.fs
fragment_shader = open("shaders/fragment.cpp", "r").read()


class Window:
    def __init__(self, width, height, title):
        self.width = width
        self.height = height
        self.title = title
        self.window = None

    def create(self):
        if not glfw.init():
            return

        self.window = glfw.create_window(self.width, self.height, self.title, None, None)
        if not self.window:
            glfw.terminate()
            return

        glfw.make_context_current(self.window)
        glfw.set_framebuffer_size_callback(self.window, self.framebuffer_size_callback)

        return True

    def framebuffer_size_callback(self, window, width, height):
        glViewport(0, 0, width, height)

t_x_inc = 0
t_y_inc = 0

angulo_x_inc = 0
angulo_y_inc = 0
angulo_z_inc = 0

s_inc = 1.0


def main():
    glfw.init()
    glfw.window_hint(glfw.VISIBLE, glfw.FALSE)
    window = glfw.create_window(700, 700, "BULE", None, None)
    glfw.make_context_current(window)

    program = glCreateProgram()
    vertex = glCreateShader(GL_VERTEX_SHADER)
    fragment = glCreateShader(GL_FRAGMENT_SHADER)

    glShaderSource(vertex, vertex_shader)
    glShaderSource(fragment, fragment_shader)

    glCompileShader(vertex)
    if not glGetShaderiv(vertex, GL_COMPILE_STATUS):
        print(glGetShaderInfoLog(vertex))
        return

    glCompileShader(fragment)
    if not glGetShaderiv(fragment, GL_COMPILE_STATUS):
        print(glGetShaderInfoLog(fragment))
        return

    glAttachShader(program, vertex)
    glAttachShader(program, fragment)

    glLinkProgram(program)
    if not glGetProgramiv(program, GL_LINK_STATUS):
        print(glGetProgramInfoLog(program))
        raise RuntimeError('Linking error')
    glUseProgram(program)

    cube = np.array(Object(obj_path).vertices)
    vertices = np.zeros(len(cube), [("position", np.float32, 3)])
    vertices['position'] = cube

    buffer = glGenBuffers(1)
    glBindBuffer(GL_ARRAY_BUFFER, buffer)

    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_DYNAMIC_DRAW)
    glBindBuffer(GL_ARRAY_BUFFER, buffer)

    stride = vertices.strides[0]
    offset = ctypes.c_void_p(0)

    loc = glGetAttribLocation(program, "position")
    glEnableVertexAttribArray(loc)

    glVertexAttribPointer(loc, 3, GL_FLOAT, False, stride, offset)

    loc_color = glGetUniformLocation(program, "color")

    # exemplo para matriz de translacao

    def key_event(window, key, scancode, action, mods):
        global t_x_inc, t_y_inc, angulo_x_inc, angulo_y_inc, angulo_z_inc, s_inc
        if key == 265: t_y_inc += 0.01  # cima
        if key == 264: t_y_inc -= 0.01  # baixo
        if key == 263: t_x_inc -= 0.01  # esquerda
        if key == 262: t_x_inc += 0.01  # direita

        # teclas a, s, d
        if key == 65: angulo_x_inc += 0.01  # rotacao x
        if key == 83: angulo_y_inc += 0.01  # rotacao y
        if key == 68: angulo_z_inc += 0.01  # rotacao z

        # teclas z , x
        if key == 90: s_inc -= 0.01  # aumenta escala
        if key == 88: s_inc += 0.01  # reduz escala

    glfw.set_key_callback(window, key_event)

    glfw.show_window(window)

    import math
    import random
    d = 0.0
    glEnable(GL_DEPTH_TEST)

    def multiplica_matriz(a, b):
        m_a = a.reshape(4, 4)
        m_b = b.reshape(4, 4)
        m_c = np.dot(m_a, m_b)
        c = m_c.reshape(1, 16)
        return c

    counter = 0
    while not glfw.window_should_close(window):

        glfw.poll_events()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        glClearColor(1.0, 1.0, 1.0, 1.0)

        mat_ident = np.array([1.0, 0.0, 0.0, 0.0,
                              0.0, 1.0, 0.0, 0.0,
                              0.0, 0.0, 1.0, 0.0,
                              0.0, 0.0, 0.0, 1.0], np.float32)

        t_x = t_x_inc
        t_y = t_y_inc
        t_z = 0.0
        mat_translate = np.array([1.0, 0.0, 0.0, t_x,
                                  0.0, 1.0, 0.0, t_y,
                                  0.0, 0.0, 1.0, t_z,
                                  0.0, 0.0, 0.0, 1.0], np.float32)

        angulo_x = angulo_x_inc
        angulo_y = angulo_y_inc
        angulo_z = angulo_z_inc

        mat_rotation_z = np.array([math.cos(angulo_z), -math.sin(angulo_z), 0.0, 0.0,
                                   math.sin(angulo_z), math.cos(angulo_z), 0.0, 0.0,
                                   0.0, 0.0, 1.0, 0.0,
                                   0.0, 0.0, 0.0, 1.0], np.float32)

        mat_rotation_x = np.array([1.0, 0.0, 0.0, 0.0,
                                   0.0, math.cos(angulo_x), -math.sin(angulo_x), 0.0,
                                   0.0, math.sin(angulo_x), math.cos(angulo_x), 0.0,
                                   0.0, 0.0, 0.0, 1.0], np.float32)

        mat_rotation_y = np.array([math.cos(angulo_y), 0.0, math.sin(angulo_y), 0.0,
                                   0.0, 1.0, 0.0, 0.0,
                                   -math.sin(angulo_y), 0.0, math.cos(angulo_y), 0.0,
                                   0.0, 0.0, 0.0, 1.0], np.float32)

        s_x = s_inc
        s_y = s_inc
        s_z = s_inc
        mat_scale = np.array([s_x, 0.0, 0.0, 0.0,
                              0.0, s_y, 0.0, 0.0,
                              0.0, 0.0, s_z, 0.0,
                              0.0, 0.0, 0.0, 1.0], np.float32)

        mat_transform = multiplica_matriz(mat_translate, mat_rotation_x)
        mat_transform = multiplica_matriz(mat_rotation_z, mat_transform)
        mat_transform = multiplica_matriz(mat_rotation_y, mat_transform)
        mat_transform = multiplica_matriz(mat_scale, mat_transform)

        loc = glGetUniformLocation(program, "mat_transformation")
        glUniformMatrix4fv(loc, 1, GL_TRUE, mat_transform)

        # Draw polygon vertices in the order
        glDrawArrays(GL_LINE_LOOP, 0, len(vertices))

        glfw.swap_buffers(window)

        counter += 1

    glfw.terminate()


if __name__ == "__main__":
    main()
