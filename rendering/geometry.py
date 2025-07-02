#geometry.py
import numpy as np
from OpenGL.GL import *
from pyrr import Matrix44

def generate_cube(uv_scale=1.0):
    positions = [
        # Front
        [-0.5,-0.5, 0.5], [ 0.5,-0.5, 0.5], [ 0.5, 0.5, 0.5], [-0.5, 0.5, 0.5],
        # Back
        [ 0.5,-0.5,-0.5], [-0.5,-0.5,-0.5], [-0.5, 0.5,-0.5], [ 0.5, 0.5,-0.5],
        # Left
        [-0.5,-0.5,-0.5], [-0.5,-0.5, 0.5], [-0.5, 0.5, 0.5], [-0.5, 0.5,-0.5],
        # Right
        [ 0.5,-0.5, 0.5], [ 0.5,-0.5,-0.5], [ 0.5, 0.5,-0.5], [ 0.5, 0.5, 0.5],
        # Top
        [-0.5, 0.5, 0.5], [ 0.5, 0.5, 0.5], [ 0.5, 0.5,-0.5], [-0.5, 0.5,-0.5],
        # Bottom
        [-0.5,-0.5,-0.5], [ 0.5,-0.5,-0.5], [ 0.5,-0.5, 0.5], [-0.5,-0.5, 0.5],
    ]

    normals = [
        [ 0,  0,  1], [ 0,  0,  1], [ 0,  0,  1], [ 0,  0,  1],
        [ 0,  0, -1], [ 0,  0, -1], [ 0,  0, -1], [ 0,  0, -1],
        [-1,  0,  0], [-1,  0,  0], [-1,  0,  0], [-1,  0,  0],
        [ 1,  0,  0], [ 1,  0,  0], [ 1,  0,  0], [ 1,  0,  0],
        [ 0,  1,  0], [ 0,  1,  0], [ 0,  1,  0], [ 0,  1,  0],
        [ 0, -1,  0], [ 0, -1,  0], [ 0, -1,  0], [ 0, -1,  0],
    ]

    # Apply uv_scale to all UVs
    uvs = [
        [0.0, 0.0], [1.0 * uv_scale, 0.0], [1.0 * uv_scale, 1.0 * uv_scale], [0.0, 1.0 * uv_scale],  # Front
        [0.0, 0.0], [1.0 * uv_scale, 0.0], [1.0 * uv_scale, 1.0 * uv_scale], [0.0, 1.0 * uv_scale],  # Back
        [0.0, 0.0], [1.0 * uv_scale, 0.0], [1.0 * uv_scale, 1.0 * uv_scale], [0.0, 1.0 * uv_scale],  # Left
        [0.0, 0.0], [1.0 * uv_scale, 0.0], [1.0 * uv_scale, 1.0 * uv_scale], [0.0, 1.0 * uv_scale],  # Right
        [0.0, 0.0], [1.0 * uv_scale, 0.0], [1.0 * uv_scale, 1.0 * uv_scale], [0.0, 1.0 * uv_scale],  # Top
        [0.0, 0.0], [1.0 * uv_scale, 0.0], [1.0 * uv_scale, 1.0 * uv_scale], [0.0, 1.0 * uv_scale],  # Bottom
    ]

    vertices = []
    for pos, norm, uv in zip(positions, normals, uvs):
        vertices.extend(pos)
        vertices.extend(norm)
        vertices.extend(uv)

    indices = []
    for i in range(0, 24, 4):
        indices += [i, i+1, i+2, i, i+2, i+3]

    return np.array(vertices, dtype=np.float32), np.array(indices, dtype=np.uint32)

def get_sphere_uv(pos):
    x, y, z = pos
    u = 0.5 + math.atan2(z, x) / (2 * math.pi)
    v = 0.5 - math.asin(y) / math.pi
    return (u, v)

def create_vao(vertices, indices):
    vao = glGenVertexArrays(1)
    vbo = glGenBuffers(1)
    ebo = glGenBuffers(1)

    glBindVertexArray(vao)

    glBindBuffer(GL_ARRAY_BUFFER, vbo)
    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_STATIC_DRAW)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, indices.nbytes, indices, GL_STATIC_DRAW)

    stride = 8 * 4  # 8 floats per vertex, 4 bytes per float

    # position attribute (location = 0)
    glEnableVertexAttribArray(0)
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(0))

    # normal attribute (location = 1)
    glEnableVertexAttribArray(1)
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(3 * 4))

    # uv attribute (location = 2)
    glEnableVertexAttribArray(2)
    glVertexAttribPointer(2, 2, GL_FLOAT, GL_FALSE, stride, ctypes.c_void_p(6 * 4))

    glBindVertexArray(0)
    return vao, vbo, ebo




