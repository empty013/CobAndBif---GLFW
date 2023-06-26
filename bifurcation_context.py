import cobAndBif
from dataclasses import dataclass, fields
import numpy as np
import glm
from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.WGL import *
from glfw.GLFW import *


class BifurcationContext(cobAndBif.CobwebAndBifurcationClass):

    @dataclass
    class AttributeLocations:
        pos: int
        trafo: int
        a_scale: int
        x_scale: int
        a_offset: int
        x_offset: int
        a: int

    @dataclass
    class BindingIndices:
        axis: int
        bif: int

    @dataclass
    class Uniforms:
        a_scale: np.ndarray
        x_scale: np.ndarray
        a_offset: np.ndarray
        x_offset: np.ndarray
        x0: np.ndarray
        n_iter: int

        def upload_all(self, context: "BifurcationContext", program=None):
            # Expects name of uniform variable and its location to be the same
            for field in fields(self):
                self.upload_single(context, field.name, program=program)

        def upload_single(self, context: "BifurcationContext", *uniform_names, program=None):
            # TODO: Problematic if uniforms are not used in shader (thrown out at compilation time) and loc should be -1
            if program is None:
                self.upload_single(context, *uniform_names, program=context.program)
                self.upload_single(context, *uniform_names, program=context.program_bif)
            else:
                glfwMakeContextCurrent(context.window)
                for uniform_name in uniform_names:
                    loc = glGetUniformLocation(program, uniform_name)
                    if type(getattr(self, uniform_name)) is type(int(1)):
                        glProgramUniform1i(program, loc, getattr(self, uniform_name))
                    else:
                        glProgramUniform1f(program, loc, getattr(self, uniform_name))
                    if uniform_name == "n_iter":
                        glfwSetWindowTitle(context.window,
                                           ''.join(['n_iter=', str(getattr(self, uniform_name))]))

    def __init__(self, window):
        self.window = window
        self.loc_pos = 0
        self.loc_trafo = 1
        self.loc = self.AttributeLocations(0, 1, 2, 3, 4, 5, 6)
        self.uniforms = self.Uniforms(a_scale=np.array([3], dtype=np.float32),
                                      x_scale=np.array([3], dtype=np.float32),
                                      a_offset=np.array([0], dtype=np.float32),
                                      x_offset=np.array([0], dtype=np.float32),
                                      x0=np.array([0.5], dtype=np.float32),
                                      n_iter=10000)
        # self.x0s = glm.array(np.linspace(-6, 6, 10, dtype=np.float32))
        self.ind = self.BindingIndices(0, 1)
        self.a_points = 1920
        self.x_points = 1080
        self.vbo = glGenBuffers(2)
        self.cross_matrix = glm.mat4(1)
        self.num_unstable = None

        self.cob = None

        self.program = self.setup_shader('cobweb_shader')
        self.program_bif = self.setup_shader('bifurcation_shader')
        glVertexAttribFormat(self.loc.pos, 2, GL_FLOAT, False, 0 * glm.sizeof(glm.float32))
        glEnableVertexAttribArray(self.loc.pos)

        self.setup_data()

        self.uniforms.upload_all(self)
        self.trafo = None
        self.update_trafo()
        id = glm.mat4(1.0)
        # glProgramUniformMatrix4fv(self.program_bif, glGetUniformLocation(self.program_bif, 'trafo'), 1, False,
        #                           glm.value_ptr(id))
        # glProgramUniform1i(self.program_bif, glGetUniformLocation(self.program_bif, "n"), self.uniforms.n_iter)
        color = glm.vec4(1, 0, 0, 1)
        glProgramUniform4f(self.program, glGetUniformLocation(self.program, "f_color"), 1, 0, 1, 1)

    def setup_axis_data(self):
        x_axis = glm.array(glm.float32,
                           -100, 0,
                           100, 0)
        y_axis = glm.array(glm.float32,
                           0, -100,
                           0, 100)
        cross_point = glm.array(glm.float32,
                                0, 0)
        return x_axis.concat(y_axis).concat(cross_point)

    def setup_data(self):
        # Axis vertex data
        data = self.setup_axis_data()

        # # Append unstable attractors
        # data2 = np.load("coordinates3.npy").astype(dtype=np.float32)
        # self.num_unstable = int(data2.size / 2)
        # data2 = glm.array(data2)
        # data = data.concat(data2)

        self.upload_array_buffer(self.vbo[0], self.ind.axis, data, 0, 2 * glm.sizeof(glm.float32), GL_STATIC_DRAW)

        # Initial data for bifurcation diagram
        a_range = np.linspace(-1, 1, self.a_points)
        x_range= np.linspace(-1, 1, self.x_points)
        aas, xxs = np.meshgrid(a_range, x_range)
        data = np.zeros(2 * self.a_points * self.x_points, dtype=np.float32)
        data[::2] = aas.reshape(-1)
        data[1::2] = xxs.reshape(-1)
        data = glm.array(data)
        self.upload_array_buffer(self.vbo[1], self.ind.bif, data, 0, 2 * glm.sizeof(glm.float32), GL_STATIC_DRAW)

        #
        # self.upload_array_buffer(self.vbo[1], self.ind.bif, data,
        #                          (2 * self.a_points * self.x_points) * (glm.sizeof(glm.float32)),
        #                          2 * glm.sizeof(glm.float32),
        #                          GL_STATIC_DRAW)


    def update_trafo(self, inv=False, program=None):
        self.trafo = glm.scale(glm.translate(glm.mat4(1), glm.vec3(self.uniforms.a_offset, self.uniforms.x_offset, 0)),
                          glm.vec3(self.uniforms.a_scale, self.uniforms.x_scale, 1))
        if not program:
            self.update_trafo(inv, program=self.program)
            self.update_trafo(inv, program=self.program_bif)
        else:
            if not inv:
                glProgramUniformMatrix4fv(program, glGetUniformLocation(self.program_bif, 'trafo'), 1, False,
                                          glm.value_ptr(self.trafo))
            else:
                trafo_inv = glm.inverse(self.trafo)
                glProgramUniformMatrix4fv(program, glGetUniformLocation(self.program_bif, 'trafo'), 1, False,
                                          glm.value_ptr(trafo_inv))

    def set_cross(self, a, x):
        a_x_norm = glm.inverse(self.trafo) * glm.vec4(a, x, 0, 1)
        self.cross_matrix = glm.translate(glm.mat4(1), glm.vec3(a_x_norm))

    # def redisplay(self):
    #     glutPostRedisplay()

    def processInput(self, window):
        zoom_factor = 1.02
        translate_factor = 0.01
        if glfwGetKey(window, GLFW_KEY_RIGHT) == GLFW_PRESS:  # key == GLFW_KEY_RIGHT and action == GLFW_PRESS:
            self.uniforms.a_offset += translate_factor * self.uniforms.a_scale
            self.uniforms.upload_single(self, "a_offset")

        if glfwGetKey(window, GLFW_KEY_LEFT) == GLFW_PRESS:  #  key == GLFW_KEY_LEFT and action == GLFW_PRESS:
            self.uniforms.a_offset += -translate_factor * self.uniforms.a_scale
            self.uniforms.upload_single(self, "a_offset")

        if glfwGetKey(window, GLFW_KEY_UP) == GLFW_PRESS:  # key == GLFW_KEY_UP and action == GLFW_PRESS:
            self.uniforms.x_offset += translate_factor * self.uniforms.x_scale
            self.uniforms.upload_single(self, "x_offset")

        if glfwGetKey(window, GLFW_KEY_DOWN) == GLFW_PRESS:  # key == GLFW_KEY_DOWN and action == GLFW_PRESS:
            self.uniforms.x_offset += -translate_factor * self.uniforms.x_scale
            self.uniforms.upload_single(self, "x_offset")

        if glfwGetKey(window, GLFW_KEY_END) == GLFW_PRESS:  # key == GLFW_KEY_END and action == GLFW_PRESS:
            self.uniforms.a_scale = self.uniforms.a_scale * zoom_factor
            self.uniforms.upload_single(self, "a_scale")

        if glfwGetKey(window, GLFW_KEY_HOME) == GLFW_PRESS:  #  key == GLFW_KEY_HOME and action == GLFW_PRESS:
            self.uniforms.a_scale = self.uniforms.a_scale / zoom_factor
            self.uniforms.upload_single(self, "a_scale")

        if glfwGetKey(window, GLFW_KEY_PAGE_DOWN) == GLFW_PRESS:  # key == GLFW_KEY_PAGE_DOWN and action == GLFW_PRESS:
            self.uniforms.x_scale = self.uniforms.x_scale / zoom_factor
            self.uniforms.upload_single(self, "x_scale")

        if glfwGetKey(window, GLFW_KEY_PAGE_UP) == GLFW_PRESS:  # key == GLFW_KEY_PAGE_UP and action == GLFW_PRESS:
            self.uniforms.x_scale = self.uniforms.x_scale * zoom_factor
            self.uniforms.upload_single(self, "x_scale")

        if glfwGetKey(window, GLFW_KEY_INSERT) == GLFW_PRESS:  # key == GLFW_KEY_INSERT and action == GLFW_PRESS:
            self.uniforms.a_scale = self.uniforms.a_scale * zoom_factor
            self.uniforms.x_scale = self.uniforms.x_scale * zoom_factor
            self.uniforms.upload_single(self, "a_scale", "x_scale")

        if glfwGetKey(window, GLFW_KEY_DELETE) == GLFW_PRESS:  # key == GLFW_KEY_DELETE and action == GLFW_PRESS:  # Delete Key
            self.uniforms.a_scale = self.uniforms.a_scale / zoom_factor
            self.uniforms.x_scale = self.uniforms.x_scale / zoom_factor
            self.uniforms.upload_single(self, "a_scale", "x_scale")

    def keyCallback(self, window, key, scancode, action, mods):
        if key in [GLFW_KEY_KP_1, GLFW_KEY_KP_2]:

            if key == GLFW_KEY_KP_1 and action == GLFW_PRESS:  # b'1':
                self.uniforms.n_iter -= 1
                self.uniforms.upload_single(self, "n_iter")

            elif key == GLFW_KEY_KP_2 and action == GLFW_PRESS:  # b'2':
                self.uniforms.n_iter += 1
                self.uniforms.upload_single(self, "n_iter")

    def mouse(self, window, button, action, mods):
        # print(button, state, x, y)
        if button == GLFW_MOUSE_BUTTON_LEFT and action == GLFW_PRESS:
            a_screen, x_screen = glfwGetCursorPos(window)
            width, height = glfwGetWindowSize(window)
            x_norm = -2 * (x_screen / (height - 1) - 0.5)
            a_norm = 2 * (a_screen / (width - 1) - 0.5)
            x = self.uniforms.x_scale * x_norm + self.uniforms.x_offset
            a = self.uniforms.a_scale * a_norm + self.uniforms.a_offset
            if self.cob is not None:
                # tmp = glm.scale(glm.translate(glm.mat4(1), glm.vec3(self.uniforms.a_offset, self.uniforms.x_offset, 0)),
                #           glm.vec3(self.uniforms.a_scale, self.uniforms.x_scale, 1))
                # self.cross = glm.inverse(tmp)
                # print('tmp: ', tmp)
                # print('self.cross: ', self.cross)
                self.cross_matrix = glm.translate(glm.vec3(a_norm, x_norm, 0))
                # print(self.cross_matrix)
                self.cob.uniforms.a = a
                self.cob.update_x0(x)
                # glfwMakeContextCurrent(self.cob.window)
                self.cob.uniforms.upload_single(self.cob, "a", program=self.cob.program_func)

    @staticmethod
    def reshape(window, width, height):
        glfwMakeContextCurrent(window)
        glViewport(0, 0, width, height)

    def display_func(self):
        # trafo = glm.scale(glm.translate(glm.mat4(1), glm.vec3(self.uniforms.a_offset, self.uniforms.x_offset, 0)),
        #                   glm.vec3(self.uniforms.a_scale, self.uniforms.x_scale, 1))
        # trafo_inv = glm.inverse(trafo)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        # Draw axis
        glUseProgram(self.program)
        glProgramUniform4f(self.program, glGetUniformLocation(self.program, "f_color"), 1, 1, 1, 1)
        self.update_trafo(inv=True)
        # glProgramUniformMatrix4fv(self.program, glGetUniformLocation(self.program, 'trafo'), 1, False,
        #                           glm.value_ptr(trafo_inv))
        glVertexAttribBinding(self.loc.pos, self.ind.axis)
        glDrawArrays(GL_LINES, 0, 4)

        # Draw bifurcation diagram
        glUseProgram(self.program_bif)
        glPointSize(1)
        self.update_trafo(inv=False, program=self.program_bif)
        # glProgramUniformMatrix4fv(self.program_bif, glGetUniformLocation(self.program, 'trafo'), 1, False,
        #                           glm.value_ptr(trafo))
        glVertexAttribBinding(self.loc.pos, self.ind.bif)
        glDrawArrays(GL_POINTS, 0, self.a_points * self.x_points)

        # # Draw bifurcation diagram with one additional iteration
        # glProgramUniform1i(self.program_bif, glGetUniformLocation(self.program_bif, "n_iter"), self.n_iter + 1)
        # glDrawArrays(GL_POINTS, 0, self.a_points * self.x_points)

        # Draw cursor for cobweb
        glUseProgram(self.program)
        glVertexAttribBinding(self.loc.pos, self.ind.axis)
        self.update_trafo()
        self.set_cross(self.cob.uniforms.a, self.cob.x0)
        glProgramUniformMatrix4fv(self.program, glGetUniformLocation(self.program, "trafo"), 1, False, glm.value_ptr(self.cross_matrix))
        glProgramUniform4f(self.program, glGetUniformLocation(self.program, "f_color"), 1, 0, 1, 1)
        glPointSize(5)
        glDrawArrays(GL_POINTS, 5, 1)

        # # Draw unstable attractors
        # glPointSize(1)
        # glProgramUniform4f(self.program, glGetUniformLocation(self.program, "f_color"), 0, 0, 1, 1)
        # self.update_trafo(inv=True, program=self.program)
        # glDrawArrays(GL_POINTS, 6, self.num_unstable)
