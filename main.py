import math

import glfw
from OpenGL.GL import *
import glm
from PIL import Image
import numpy as np

vertex_shader_source = """
attribute vec3 position;
                
uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;        
        
void main(){
    gl_Position = projection * view * model * vec4(position,1.0);
}
"""

# Fragment Shader code
fragment_shader_source = """
uniform vec4 color;
void main(){
    gl_FragColor = color;
}
"""


class ObjectLoader:
    def __init__(self, model_dir='models/', texture_dir='textures/'):
        self.model_dir = model_dir
        self.texture_dir = texture_dir

    def new(self, model_name, texture_name):
        obj = Object()
        obj.load(self.model_dir + model_name)
        obj.load_texture(self.texture_dir + texture_name)

        return obj


class Object:
    def __init__(self):
        self.vertices = np.array([])
        self.textures = np.array([])
        self.faces = np.array([])

        self.position = glm.vec3(0, 0, 0)
        self.rotation = glm.vec3(0, 0, 0)
        self.scale = glm.vec3(1, 1, 1)

        self.texture = None

    def load(self, path):
        self.vertices = []
        self.textures = []
        self.faces = []

        with open(path, 'r') as file:
            for line in file:
                if line.startswith('v '):
                    self.vertices.append(list(map(float, line.strip().split()[1:4])))
                elif line.startswith('vt '):
                    self.textures.append(list(map(float, line.strip().split()[1:3])))
                elif line.startswith('f '):
                    face = [list(map(int, vert.split('/'))) for vert in line.strip().split()[1:]]
                    self.faces.append(face)

        self.vertices = np.array(self.vertices)
        self.textures = np.array(self.textures)
        self.faces = np.array(self.faces)

        return self.vertices, self.textures, self.faces

    def load_texture(self, file_path):
        img = Image.open(file_path)
        img_data = np.array(list(img.getdata()), np.uint8)
        texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, texture)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGB, img.width, img.height, 0, GL_RGB, GL_UNSIGNED_BYTE, img_data)
        glGenerateMipmap(GL_TEXTURE_2D)

        self.texture = texture

        return texture

    @property
    def mat_transform(self):
        mat = glm.mat4(1)
        mat = glm.translate(mat, self.position)
        mat = glm.rotate(mat, self.rotation.x, glm.vec3(1, 0, 0))
        mat = glm.rotate(mat, self.rotation.y, glm.vec3(0, 1, 0))
        mat = glm.rotate(mat, self.rotation.z, glm.vec3(0, 0, 1))
        mat = glm.scale(mat, self.scale)

        return mat

    def draw(self, program, camera):
        # Set matrices and draw object with texture, face by face
        model_loc = glGetUniformLocation(program, 'model')
        view_loc = glGetUniformLocation(program, 'view')
        projection_loc = glGetUniformLocation(program, 'projection')

        glUniformMatrix4fv(model_loc, 1, GL_FALSE, glm.value_ptr(self.mat_transform))
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, glm.value_ptr(camera.get_view()))
        glUniformMatrix4fv(projection_loc, 1, GL_FALSE, glm.value_ptr(camera.get_projection(800 / 600)))

        glBindTexture(GL_TEXTURE_2D, self.texture)

        for face in self.faces:
            glBegin(GL_TRIANGLES)
            for vert in face:
                glVertex3fv(self.vertices[vert[0] - 1])
            glEnd()

    def move(self, x, y, z):
        self.position = glm.vec3(x, y, z)


class Camera:
    def __init__(self):
        self.position = glm.vec3(0, 0, 3)
        self.front = glm.vec3(0, 0, -1)
        self.up = glm.vec3(0, 1, 0)
        self.right = glm.vec3(1, 0, 0)
        self.world_up = glm.vec3(0, 1, 0)

        self.yaw = -90
        self.pitch = 0

        self.fov = 45
        self.near = 0.1
        self.far = 100

    def get_view(self):
        return glm.lookAt(self.position, self.position + self.front, self.up)

    def get_projection(self, aspect_ratio):
        return glm.perspective(glm.radians(self.fov), aspect_ratio, self.near, self.far)

    def get_clip(self):
        return glm.vec4(self.near, self.far, 0, 0)

    def mouse_callback(self, xpos, ypos):
        sensitivity = 0.1
        xpos *= sensitivity
        ypos *= sensitivity

        self.yaw += xpos
        self.pitch += ypos

        if self.pitch > 89:
            self.pitch = 89
        if self.pitch < -89:
            self.pitch = -89

    def key_callback(self, key, scancode, action, mods):
        camera_speed = 0.05
        if key == glfw.KEY_W:
            self.position += self.front * camera_speed
        if key == glfw.KEY_S:
            self.position -= self.front * camera_speed
        if key == glfw.KEY_A:
            self.position -= glm.normalize(glm.cross(self.front, self.up)) * camera_speed
        if key == glfw.KEY_D:
            self.position += glm.normalize(glm.cross(self.front, self.up)) * camera_speed

    def update_camera_vectors(self):
        front = glm.vec3(0, 0, 0)
        front.x = math.cos(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch))
        front.y = math.sin(glm.radians(self.pitch))
        front.z = math.sin(glm.radians(self.yaw)) * math.cos(glm.radians(self.pitch))
        self.front = glm.normalize(front)

        self.right = glm.normalize(glm.cross(self.front, self.world_up))
        self.up = glm.normalize(glm.cross(self.right, self.front))


class Graphics:
    def __init__(self, window):
        self.window = window
        self.program = glCreateProgram()

        vertex = glCreateShader(GL_VERTEX_SHADER)
        fragment = glCreateShader(GL_FRAGMENT_SHADER)

        glShaderSource(vertex, vertex_shader_source)
        glShaderSource(fragment, fragment_shader_source)

        glCompileShader(vertex)
        if not glGetShaderiv(vertex, GL_COMPILE_STATUS):
            error = glGetShaderInfoLog(vertex).decode()
            print(error)
            raise RuntimeError("Shader Compilation Error")

        glCompileShader(fragment)
        if not glGetShaderiv(fragment, GL_COMPILE_STATUS):
            error = glGetShaderInfoLog(fragment).decode()
            print(error)
            raise RuntimeError("Shader Compilation Error")

        glAttachShader(self.program, vertex)
        glAttachShader(self.program, fragment)

        glLinkProgram(self.program)
        if not glGetProgramiv(self.program, GL_LINK_STATUS):
            error = glGetProgramInfoLog(self.program).decode()
            print(error)
            raise RuntimeError("Program Linking Error")

        glUseProgram(self.program)

        buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, buffer)

        glEnable(GL_DEPTH_TEST)

        self.camera = Camera()

    def draw(self, objects):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glClearColor(0.2, 0.3, 0.3, 1)

        for obj in objects:
            obj.draw(self.program, self.camera)

        self.camera.update_camera_vectors()

        glfw.swap_buffers(self.window)
        glfw.poll_events()

    def mouse_callback(self, window, xpos, ypos):
        # Camera mouse callback
        self.camera.mouse_callback(xpos, ypos)

    def key_callback(self, window, key, scancode, action, mods):
        self.camera.key_callback(key, scancode, action, mods)


class Physics:
    def __init__(self):
        pass

    def tick(self):
        pass

    def mouse_callback(self, window, xpos, ypos):
        pass

    def key_callback(self, window, key, scancode, action, mods):
        pass


class Engine:
    def __init__(self, objects=None, window_length=800, window_height=600):
        self.graphics: Graphics | None = None
        self.physics: Physics | None = None

        self.window_properties = {
            "length": window_length,
            "height": window_height
        }

        self.objects = objects if objects is not None else []

    def mouse_callback(self, window, xpos, ypos):
        if self.graphics is not None:
            self.graphics.mouse_callback(window, xpos, ypos)

        if self.physics is not None:
            self.physics.mouse_callback(window, xpos, ypos)

    def key_callback(self, window, key, scancode, action, mods):
        if self.graphics is not None:
            self.graphics.key_callback(window, key, scancode, action, mods)

        if self.physics is not None:
            self.physics.key_callback(window, key, scancode, action, mods)

    def start(self):
        glfw.init()
        glfw.window_hint(glfw.VISIBLE, glfw.FALSE)

        window_length = 800
        window_height = 600
        window = glfw.create_window(window_length, window_height, "OpenGL Window", None, None)
        glfw.make_context_current(window)

        self.graphics = Graphics(window)
        self.physics = Physics()

        glfw.set_cursor_pos_callback(window, self.mouse_callback)
        glfw.set_key_callback(window, self.key_callback)

        glfw.show_window(window)

        while not glfw.window_should_close(window):
            glfw.poll_events()
            self.physics.tick()
            self.graphics.draw(self.objects)


def main():
    model_loader = ObjectLoader()
    cube = model_loader.new('cube.obj', 'container.jpeg')

    # Set cube position to in front of the camera
    cube.move(0, 0, -3)

    engine = Engine([cube])
    engine.start()


if __name__ == "__main__":
    main()
