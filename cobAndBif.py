import numpy as np
from OpenGL.GL import *
# import win32gui
# import re


class CobwebAndBifurcationClass(object):
    # class WindowMgr:
    #     """Encapsulates some calls to the winapi for window management"""
    #
    #     def __init__(self):
    #         """Constructor"""
    #         self._handle = None
    #
    #     def find_window(self, class_name, window_name=None):
    #         """find a window by its class_name"""
    #         self._handle = win32gui.FindWindow(class_name, window_name)
    #
    #     def _window_enum_callback(self, hwnd, wildcard):
    #         """Pass to win32gui.EnumWindows() to check all the opened windows"""
    #         if re.match(wildcard, str(win32gui.GetWindowText(hwnd))) is not None:
    #             self._handle = hwnd
    #
    #     def find_window_wildcard(self, wildcard):
    #         """find a window whose title matches the wildcard regex"""
    #         self._handle = None
    #         win32gui.EnumWindows(self._window_enum_callback, wildcard)
    #
    #     def set_foreground(self):
    #         """put the window in the foreground"""
    #         win32gui.SetForegroundWindow(self._handle)

    @staticmethod
    def f(x, a=1, n=1):
        if n > 1:
            return CobwebAndBifurcationClass.f(CobwebAndBifurcationClass.f(x, a, n - 1), a, n=1)
        # return a * x * (1 - np.power(x, 2))
        return a * np.sin(x) * (1 - np.power(x, 2)) - 1

    @staticmethod
    def upload_array_buffer(vbo, binding_index, data, offset, stride, draw_type):
        glBindBuffer(GL_ARRAY_BUFFER, vbo)
        glBufferData(GL_ARRAY_BUFFER, data.nbytes, data.ptr, draw_type)
        glBindVertexBuffer(binding_index, vbo, offset, stride)

    @staticmethod
    def setup_shader(folder, geometry=False):
        program = glCreateProgram()
        vertex = glCreateShader(GL_VERTEX_SHADER)
        fragment = glCreateShader(GL_FRAGMENT_SHADER)
        with open(folder + '\\ex3_cobweb_float.vs') as file:
            vertex_code = file.read()
        with open(folder + '\\ex3_cobweb_float.fs') as file:
            fragment_code = file.read()
        glShaderSource(vertex, vertex_code)
        glShaderSource(fragment, fragment_code)
        glCompileShader(vertex)
        if not glGetShaderiv(vertex, GL_COMPILE_STATUS):
            _error = glGetShaderInfoLog(vertex).decode()
            print(_error)
            raise RuntimeError("Vertex shader compilation error")
        glCompileShader(fragment)
        if not glGetShaderiv(fragment, GL_COMPILE_STATUS):
            _error = glGetShaderInfoLog(fragment).decode()
            print(_error)
            raise RuntimeError("Fragment shader compilation error")
        glAttachShader(program, vertex)
        if geometry:
            geometry = glCreateShader(GL_GEOMETRY_SHADER)
            with open(folder + '\\ex3_cobweb_float.gs') as file:
                geometry_code = file.read()
            glShaderSource(geometry, geometry_code)
            glCompileShader(geometry)
            if not glGetShaderiv(geometry, GL_COMPILE_STATUS):
                _error = glGetShaderInfoLog(geometry).decode()
                print(_error)
                raise RuntimeError("Geometry shader compilation error")
            glAttachShader(program, geometry)
        glAttachShader(program, fragment)
        glLinkProgram(program)
        if not glGetProgramiv(program, GL_LINK_STATUS):
            print(glGetProgramInfoLog(program))
            raise RuntimeError('Linking error')
        glDetachShader(program, vertex)
        glDetachShader(program, fragment)
        if geometry:
            glDetachShader(program, geometry)
        return program
