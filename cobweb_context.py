import cobAndBif
import numpy as np
import glm
from OpenGL_accelerate import *
import OpenGL_accelerate
from OpenGL.GL import *
from glfw.GLFW import *
from dataclasses import dataclass, fields
from OpenGL.WGL import *

# WGL.wglShareLists()


class CobwebContext(cobAndBif.CobwebAndBifurcationClass):

    @dataclass
    class AttributeLocations:
        pos: int
        trafo: int
        x_scale: int
        y_scale: int
        x_offset: int
        y_offset: int
        a: int

    @dataclass
    class BindingIndices:
        axis: int
        graph: int
        cob: int

    @dataclass
    class Uniforms:
        x_scale: np.ndarray
        y_scale: np.ndarray
        x_offset: np.ndarray
        y_offset: np.ndarray
        a: np.ndarray
        n: int

        def upload_all(self, cobweb_context: "CobwebContext", program=None):
            # Expects name of uniform variable and its location to be the same
            for field in fields(self):
                # print(field.type is type(int(1)))
                self.upload_single(cobweb_context, field.name, program=program)

        def upload_single(self, cobweb_context: "CobwebContext", *uniform_names, program=None):
            # TODO: Problematic if uniforms are not used in shader (thrown out at compilation time) and loc should be -1
            if program is None:
                # print(cobweb_context.program, context_proprogram)
                self.upload_single(cobweb_context, *uniform_names, program=cobweb_context.program)
                self.upload_single(cobweb_context, *uniform_names, program=cobweb_context.program_func)
            else:
                for uniform_name in uniform_names:
                    glfwMakeContextCurrent(cobweb_context.window)
                    loc = glGetUniformLocation(program, uniform_name)
                    if type(getattr(self, uniform_name)) is type(int(1)):
                        # if program == cobweb_context.program_func:
                            # print("int: ------------------------")
                            # print("uni_name: ", uniform_name)
                            # print("program: ", program)
                            # print("loc: ", loc)
                        glProgramUniform1i(program, loc, getattr(self, uniform_name))
                            # glProgramUniform1i(1, 0, 2)
                    else:
                        glProgramUniform1f(program, loc, getattr(self, uniform_name))
                        if uniform_name == "a" or uniform_name == "n":
                            cobweb_context.update_title()

    def __init__(self, window):
        self.window = window
        self.loc = self.AttributeLocations(pos=0, trafo=1, x_scale=2, x_offset=3, y_scale=4, y_offset=5, a=6)
        self.ind = self.BindingIndices(axis=0, graph=1, cob=2)
        self.uniforms = self.Uniforms(x_scale=np.array([10], dtype=np.float32),
                                      y_scale=np.array([10], dtype=np.float32),
                                      x_offset=np.array([2], dtype=np.float32),
                                      y_offset=np.array([0], dtype=np.float32),
                                      a=np.array([2], dtype=np.float32),
                                      n=1)
        self.trafo = None
        self.num_points = 1000
        self.x0 = 0.3
        self.cob_len = 1500
        self.cob = None
        self.vbo = glGenBuffers(3)
        self.program_func = self.setup_shader("function_shader")
        self.program = self.setup_shader("cobweb_shader")
        self.bif = None
        glVertexAttribFormat(self.loc.pos, 2, GL_FLOAT, False, 0 * glm.sizeof(glm.float32))
        glEnableVertexAttribArray(self.loc.pos)

        self.setup_data()
        self.uniforms.upload_all(self)

    def update_title(self):
        glfwSetWindowTitle(self.window,
                           ''.join(['a=', self.uniforms.a.astype(str)[0],
                                    '  x0=', str(self.x0), '  n=', str(self.uniforms.n)]))
    def update_x0(self, x0):
        self.x0 = x0
        self.update_title()
        glfwSetWindowTitle(self.window, ''.join(['a=', str(self.uniforms.a), '  x0=', str(self.x0)]))

    def update_cobweb(self):
        self.cob = self.cobweb()
        self.upload_array_buffer(self.vbo[2], self.ind.cob, self.cob, 0, 2 * glm.sizeof(glm.float32), GL_DYNAMIC_DRAW)
        self.update_title()
        # glfwSetWindowTitle(self.window,
        #                    ''.join(['a=', self.uniforms.a.astype(str)[0],
        #                             '  x0=', str(self.x0), '  n=', str(self.uniforms.n)]))

    def setup_data(self):
        # Axis vertex data
        data = self.setup_axis_data()
        self.upload_array_buffer(self.vbo[0], self.ind.axis, data, 0, 2 * glm.sizeof(glm.float32), GL_STATIC_DRAW)

        # Initial function vertex data
        self.setup_function_data()
        # data = self.setup_function_data()
        # self.upload_array_buffer(self.vbo[1], self.ind.graph, data, 0, 2 * glm.sizeof(glm.float32), GL_STATIC_DRAW)

        # Initial cobweb vertex data
        self.update_cobweb()

        # self.trafo = glm.translate(glm.scale(glm.mat4(1), glm.vec3(1, 1, 1)),
        #                            glm.vec3(self.uniforms.x_offset, self.uniforms.y_offset, 0))
        glProgramUniformMatrix4fv(self.program, glGetUniformLocation(self.program, 'trafo'), 1, False, glm.value_ptr(glm.mat4(1)))
        glProgramUniform4f(self.program, glGetUniformLocation(self.program, "f_color"), 1, 1, 1, 1)

    def cobweb(self, x0=None, n=None):
        if x0 is None:
            x0 = self.x0
        if n is None:
            n = self.cob_len
        cob = [x0, x0]
        x = x0
        for i in range(n):
            y = self.f(x, self.uniforms.a, n=0)
            if y >= 1000 or y <= -1000:
                break
            cob.append(x)
            cob.append(y)

            cob.append(y)
            cob.append(y)
            x = y
        return glm.array(glm.float32, *cob)

    def setup_axis_data(self):
        x_axis = glm.array(glm.float32,
                           -100, 0,
                           100, 0)
        y_axis = glm.array(glm.float32,
                           0, -100,
                           0, 100)
        id = glm.array(glm.float32,  # Identity axis
                       -100, -100,
                       100, 100)
        cross_point = glm.array(glm.float32, 0, 0)
        return x_axis.concat(y_axis).concat(id).concat(cross_point)

    def setup_function_data(self):  # Y_data will be computed in function shader with variable a
        x_data = np.linspace(-1, 1, self.num_points)
        graph = np.zeros(2 * x_data.shape[0], dtype=np.float32)
        graph[::2] = x_data
        # graph[1::2] = np.zeros(self.num_points, dtype=np.float32) + 0.5
        self.upload_array_buffer(self.vbo[1], self.ind.graph, glm.array(graph), 0, 2 * glm.sizeof(glm.float32), GL_DYNAMIC_DRAW)
        # return glm.array(graph)

    def processInput(self, window):
        zoom_factor = 1.02
        translate_factor = 0.01
        if glfwGetKey(window, GLFW_KEY_ESCAPE) == GLFW_PRESS:
            glfwSetWindowShouldClose(window, True)

        if glfwGetKey(window, GLFW_KEY_RIGHT) == GLFW_PRESS:  #key == GLUT_KEY_RIGHT:  # Move right
            self.uniforms.x_offset += translate_factor * self.uniforms.x_scale
            self.uniforms.upload_single(self, "x_offset")

        if glfwGetKey(window, GLFW_KEY_LEFT) == GLFW_PRESS:  # Move left
            self.uniforms.x_offset += -translate_factor * self.uniforms.x_scale
            self.uniforms.upload_single(self, "x_offset")

        if glfwGetKey(window, GLFW_KEY_UP) == GLFW_PRESS:  # Move up
            self.uniforms.y_offset += translate_factor * self.uniforms.y_scale
            self.uniforms.upload_single(self, "y_offset")

        if glfwGetKey(window, GLFW_KEY_DOWN) == GLFW_PRESS:  # Move down
            self.uniforms.y_offset += -translate_factor * self.uniforms.y_scale
            self.uniforms.upload_single(self, "y_offset")

        if glfwGetKey(window, GLFW_KEY_PAGE_UP) == GLFW_PRESS:  # Scale y-Axis (Zoom out)
            self.uniforms.y_scale = self.uniforms.y_scale * zoom_factor
            self.uniforms.upload_single(self, "y_scale")

        if glfwGetKey(window, GLFW_KEY_PAGE_DOWN) == GLFW_PRESS:  # Scale y-Axis (Zoom in)
            self.uniforms.y_scale = self.uniforms.y_scale / zoom_factor
            self.uniforms.upload_single(self, "y_scale")

        if glfwGetKey(window, GLFW_KEY_HOME) == GLFW_PRESS:  # Scale x-Axis (Zoom out)
            self.uniforms.x_scale = self.uniforms.x_scale * zoom_factor
            self.uniforms.upload_single(self, "x_scale")

        if glfwGetKey(window, GLFW_KEY_END) == GLFW_PRESS:  # Scale x-Axis (Zoom in)
            self.uniforms.x_scale = self.uniforms.x_scale / zoom_factor
            self.uniforms.upload_single(self, "x_scale")

        if glfwGetKey(window, GLFW_KEY_INSERT) == GLFW_PRESS:  # Scale x- and y-Axis uniformly (Zoom out)
            self.uniforms.x_scale = self.uniforms.x_scale * zoom_factor
            self.uniforms.y_scale = self.uniforms.y_scale * zoom_factor
            self.uniforms.upload_single(self, "x_scale", "y_scale")

        if glfwGetKey(window, GLFW_KEY_KP_MULTIPLY) == GLFW_PRESS:  # Increase a
            self.uniforms.a = self.uniforms.a * 1.0008
            self.uniforms.upload_single(self, "a")
            if self.bif is not None:
                self.bif.set_cross(self.uniforms.a, self.x0)

        if glfwGetKey(window, GLFW_KEY_KP_DIVIDE) == GLFW_PRESS:  # Decrease a
            self.uniforms.a = self.uniforms.a / 1.0008
            self.uniforms.upload_single(self, "a")
            if self.bif is not None:
                self.bif.set_cross(self.uniforms.a, self.x0)

        if glfwGetKey(window, GLFW_KEY_DELETE) == GLFW_PRESS:  # (Delete Key) Scale x- and y-Axis uniformly (Zoom in)
            self.uniforms.x_scale = self.uniforms.x_scale / zoom_factor
            self.uniforms.y_scale = self.uniforms.y_scale / zoom_factor
            self.uniforms.upload_single(self, "x_scale", "y_scale")

        if glfwGetKey(window, GLFW_KEY_KP_4) == GLFW_PRESS:  # Change initial condition (decrease)
            self.update_x0(self.x0 - 0.001 * self.uniforms.x_scale)
            self.cob = self.cobweb()
            self.update_cobweb()
            if self.bif is not None:
                self.bif.set_cross(self.uniforms.a, self.x0)
                # wglMakeCurrent(self.dc, self.wgl)

        if glfwGetKey(window, GLFW_KEY_KP_6) == GLFW_PRESS:  # Change initial condition (increase)
            self.update_x0(self.x0 + 0.001 * self.uniforms.x_scale)
            self.cob = self.cobweb()
            self.update_cobweb()
            if self.bif is not None:
                self.bif.set_cross(self.uniforms.a, self.x0)

    def keyCallback(self, window, key, scancode, action, mods):
        if key == GLFW_KEY_KP_ADD and action == GLFW_PRESS:
            self.uniforms.n += 1
            self.uniforms.upload_single(self, "n", program=self.program_func)

        if key == GLFW_KEY_KP_SUBTRACT and action == GLFW_PRESS:
            self.uniforms.n += -1
            self.uniforms.upload_single(self, "n", program=self.program_func)

    def display_func(self):
        glClear(GL_COLOR_BUFFER_BIT)
        glPointSize(1)
        self.update_cobweb()
        trafo = glm.scale(glm.translate(glm.mat4(1), glm.vec3(self.uniforms.x_offset, self.uniforms.y_offset, 0)),
                          glm.vec3(self.uniforms.x_scale, self.uniforms.y_scale, 1))
        trafo_inv = glm.inverse(trafo)

        # Draw function
        glUseProgram(self.program_func)
        loc = glGetAttribLocation(self.program_func, 'position')
        glVertexAttribBinding(loc, self.ind.graph)
        glDrawArrays(GL_LINE_STRIP, 0, self.num_points)

        # Draw axis
        glUseProgram(self.program)
        glProgramUniform4f(self.program, glGetUniformLocation(self.program, "f_color"), 1, 1, 1, 1)
        glProgramUniformMatrix4fv(self.program, glGetUniformLocation(self.program, 'trafo'), 1, False, glm.value_ptr(trafo_inv))
        glVertexAttribBinding(glGetAttribLocation(self.program, 'position'), self.ind.axis)
        glDrawArrays(GL_LINES, 0, 6)

        # Draw cobweb
        glProgramUniform4f(self.program, glGetUniformLocation(self.program, "f_color"), 0, 1, 0, 1)
        glProgramUniformMatrix4fv(self.program, glGetUniformLocation(self.program, 'trafo'), 1, False, glm.value_ptr(trafo_inv))
        glVertexAttribBinding(glGetAttribLocation(self.program, 'position'), self.ind.cob)
        glDrawArrays(GL_LINE_STRIP, 0, int(len(self.cob) / 2))

        # Draw x0 for cobweb
        glProgramUniform4f(self.program, glGetUniformLocation(self.program, "f_color"), 1, 0, 1, 1)
        glPointSize(5)
        glDrawArrays(GL_POINTS, 0, 1)

    @staticmethod
    def reshape(window, width, height):
        glfwMakeContextCurrent(window)
        glViewport(0, 0, width, height)
