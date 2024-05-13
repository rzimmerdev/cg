import glfw
from OpenGL.GL import *


class Window:
    """
    Encapsula a janela gráfica do jogo.
    Comunica com a biblioteca GLFW para criar e gerenciar a janela.

    Funções:
        - create_window: Cria a janela gráfica.
        - close_window: Fecha a janela gráfica.
        - set_framebuffer_size_callback: Define o callback para redimensionamento da janela.
        - set_cursor_callback: Define o callback para movimento do cursor.
        - set_key_callback: Define o callback para pressionamento de teclas.
        - set_input_mode: Define o modo de input do cursor.
    """

    def __init__(self, width: int = 800, height: int = 600, title: str = "Game"):
        self.width = width
        self.height = height

        self._x = 100
        self._y = 100

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
        glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_NORMAL)

        return self.window

    def close_window(self):
        glfw.terminate()

    def set_framebuffer_size_callback(self, callback):
        glfw.set_framebuffer_size_callback(self.window, callback)

    def set_cursor_callback(self, callback):
        glfw.set_cursor_pos_callback(self.window, callback)

    def set_key_callback(self, callback):
        glfw.set_key_callback(self.window, callback)

    def set_input_mode(self, mode):
        glfw.set_input_mode(self.window, glfw.CURSOR, mode)

    def should_close(self):
        return glfw.window_should_close(self.window)

    def swap_buffers(self):
        glfw.swap_buffers(self.window)

    def poll_events(self):
        glfw.poll_events()

    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            monitor = glfw.get_primary_monitor()
            mode = glfw.get_video_mode(monitor)
            size = mode[0]

            # Seta o tamanho da janela para o tamanho do monitor
            glfw.set_window_monitor(self.window, monitor, self._x, self._y, size.width, size.height, mode.refresh_rate)
            glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_DISABLED)
        else:
            # Seta o tamanho da janela para o tamanho original
            glfw.set_window_monitor(self.window, None, 100, 100, self.width, self.height, 0)
            glfw.set_input_mode(self.window, glfw.CURSOR, glfw.CURSOR_NORMAL)

    def resize(self, window, width, height, *args):
        glViewport(0, 0, width, height)
