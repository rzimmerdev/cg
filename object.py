from OpenGL.GL import *


class Object:
    def __init__(self, filename):
        self.vertices = []
        self.normals = []
        self.faces = []
        self.load(filename)

    def load(self, filename):
        with open(filename, 'r') as f:
            for line in f:
                if line.startswith('#'):
                    continue
                values = line.split()
                if not values:
                    continue
                if values[0] == 'v':
                    v = tuple(map(float, values[1:4]))
                    self.vertices.append(v)
                elif values[0] == 'vn':
                    vn = list(map(float, values[1:4]))
                    self.normals.append(vn)
                elif values[0] == 'f':
                    face = []
                    face_normals = []
                    for v in values[1:]:
                        w = v.split('/')
                        face.append(int(w[0]))
                        if len(w) >= 3:
                            face_normals.append(int(w[2]))
                    self.faces.append((face, face_normals))

    def render(self, shader_program):
        for face in self.faces:
            vertices, normals = face
            glBegin(GL_POLYGON)
            for i in range(len(vertices)):
                glVertex3fv(self.vertices[vertices[i] - 1])
                if normals:
                    glNormal3fv(self.normals[normals[i] - 1])
            glEnd()
