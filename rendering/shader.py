#shader.py
from OpenGL.GL import *

def load_shaders(vertex_path, fragment_path):
        with open(vertex_path, 'r') as vf:
            vertex_src = vf.read()
        with open(fragment_path, 'r') as ff:
            fragment_src = ff.read()

        vertex_shader = glCreateShader(GL_VERTEX_SHADER)
        glShaderSource(vertex_shader, vertex_src)
        glCompileShader(vertex_shader)

        if not glGetShaderiv(vertex_shader, GL_COMPILE_STATUS):
            error = glGetShaderInfoLog(vertex_shader).decode()
            print("Vertex shader compilation error:\n", error)
            glDeleteShader(vertex_shader)
            return 0

        fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
        glShaderSource(fragment_shader, fragment_src)
        glCompileShader(fragment_shader)

        if not glGetShaderiv(fragment_shader, GL_COMPILE_STATUS):
            error = glGetShaderInfoLog(fragment_shader).decode()
            print("Fragment shader compilation error:\n", error)
            glDeleteShader(fragment_shader)
            glDeleteShader(vertex_shader)
            return 0

        shader_program = glCreateProgram()
        glAttachShader(shader_program, vertex_shader)
        glAttachShader(shader_program, fragment_shader)
        glLinkProgram(shader_program)

        if not glGetProgramiv(shader_program, GL_LINK_STATUS):
            error = glGetProgramInfoLog(shader_program).decode()
            print("Shader program linking error:\n", error)
            glDeleteProgram(shader_program)
            glDeleteShader(vertex_shader)
            glDeleteShader(fragment_shader)
            return 0

        # Cleanup shaders after linking
        glDeleteShader(vertex_shader)
        glDeleteShader(fragment_shader)

        return shader_program
