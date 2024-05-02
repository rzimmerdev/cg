import glfw
from OpenGL.GL import *


class Window:
    def __init__(self, width: int = 800, height: int = 600, title: str = "Game"):
        self.width = width
        self.height = height
        self.title = title
        self.window = None

        self.previous_frame = 0.0
        self.fullscreen = False

    def create_window(self):
        if not glfw.init():
            return

        glfw.window_hint(glfw.CONTEXT_VERSION_MAJOR, 3)
        glfw.window_hint(glfw.CONTEXT_VERSION_MINOR, 3)
        glfw.window_hint(glfw.OPENGL_PROFILE, glfw.OPENGL_CORE_PROFILE)

        self.window = glfw.create_window(self.width, self.height, self.title, None, None)
        if not self.window:
            glfw.terminate()
            return

        glfw.make_context_current(self.window)
        glfw.set_framebuffer_size_callback(self.window, self.resize)
        glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_DISABLED)
        return self.window

    def setup(self, mouse_callback):
        glfw.set_cursor_pos_callback(self.window, mouse_callback)

    def close_window(self):
        glfw.terminate()

    def set_framebuffer_size_callback(self, callback):
        glfw.set_framebuffer_size_callback(self.window, callback)

    def set_cursor_pos_callback(self, callback):
        glfw.set_cursor_pos_callback(self.window, callback)

    def set_input_mode(self, mode):
        glfw.set_input_mode(self.window, glfw.CURSOR, mode)

    def should_close(self):
        return glfw.window_should_close(self.window)

    def swap_buffers(self):
        glfw.swap_buffers(self.window)

    def poll_events(self):
        glfw.poll_events()

    def toggle_fullscreen(self):
        if self.fullscreen:
            glfw.set_window_monitor(self.window, None, 100, 100, self.width, self.height, glfw.DONT_CARE)
            self.fullscreen = False
        else:
            monitor = glfw.get_primary_monitor()
            mode = glfw.get_video_mode(monitor)
            glfw.set_window_monitor(self.window, monitor, 0, 0, mode.size.width, mode.size.height, mode.refresh_rate)
            self.fullscreen = True

    def resize(self, width, height):
        self.width = width
        self.height = height
        glViewport(0, 0, self.width, self.height)
