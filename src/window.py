import glfw
from OpenGL.GL import *
import numpy as np


class Window:
    def __init__(self, width, height, title):
        self.width = width
        self.height = height
        self.title = title

        if not glfw.init():
            raise Exception("glfw can not be initialized!")

        self.window = glfw.create_window(self.width, self.height, self.title, None, None)

        if not self.window:
            glfw.terminate()
            raise Exception("glfw window can not be created!")

        glfw.make_context_current(self.window)

        glfw.set_key_callback(self.window, self.on_key)
        glfw.set_cursor_pos_callback(self.window, self.on_mouse_move)
        glfw.set_mouse_button_callback(self.window, self.on_mouse_button)
        glfw.set_scroll_callback(self.window, self.on_mouse_scroll)

    def on_key(self, window, key, scancode, action, mods):
        if key == glfw.KEY_ESCAPE and action == glfw.PRESS:
            glfw.set_window_should_close(window, True)

    def on_mouse_move(self, window, x, y):
        pass

    def on_mouse_button(self, window, button, action, mods):
        pass

    def on_mouse_scroll(self, window, xoffset, yoffset):
        pass

    def run(self):
        while not glfw.window_should_close(self.window):
            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glfw.swap_buffers(self.window)
            glfw.poll_events()

        glfw.terminate()


if __name__ == "__main__":
    window = Window(800, 600, "Hello World")
    window.run()
