# from OpenGL.GL import *
# import glm
# import numpy as np
try:
    from OpenGL.GL import *
    from glfw.GLFW import *
    # from glfw import _GLFWwindow as GLFWwindow
    import glm
    import numpy as np

except ImportError:
    import requirements
    from OpenGL.GL import *
    from glfw.GLFW import *
    from glfw import _GLFWwindow as GLFWwindow
    import glm
    import numpy as np


from cobweb_context import *
from bifurcation_context import *
# from glfw.GLFW import *


win_x = 800
win_y = 600


glfwInit()
# glfwWindowHint(GLFW_CONTEXT_VERSION_MAJOR, 4);
# glfwWindowHint(GLFW_CONTEXT_VERSION_MINOR, 6);

window = glfwCreateWindow(win_x, win_y, "Cobweb", None, None)
glfwSetWindowPos(window, 50, 50)
glfwMakeContextCurrent(window)
cob = CobwebContext(window)
glfwSetFramebufferSizeCallback(window, cob.reshape)
glfwSetKeyCallback(window, cob.keyCallback)

window2 = glfwCreateWindow(win_x, win_y, "Cobweb", None, None)
glfwSetWindowPos(window2, 870, 50)
glfwMakeContextCurrent(window2)
bif = BifurcationContext(window2)
glfwSetFramebufferSizeCallback(window2, bif.reshape)
glfwSetKeyCallback(window2, bif.keyCallback)
glfwSetMouseButtonCallback(window2, bif.mouse)

bif.cob = cob
cob.bif = bif
bif.set_cross(cob.uniforms.a, cob.x0)


while not glfwWindowShouldClose(window):
    glfwMakeContextCurrent(window)
    cob.processInput(window)
    cob.display_func()
    glfwSwapBuffers(window)

    glfwMakeContextCurrent(window2)
    bif.processInput(window2)
    bif.display_func()
    glfwSwapBuffers(window2)

    glfwPollEvents()
glfwTerminate()



# glutInit()
# glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
# glutInitWindowSize(800, 600)
# glutInitWindowPosition(0, 0)
#
# win = glutCreateWindow('Cobweb')
# cob = CobwebContext()
# glutDisplayFunc(cob.display_func)
# glutSpecialFunc(cob.specialInput)
# glutKeyboardFunc(cob.keyboard)
#
# glutInitWindowPosition(850, 0)
# win2 = glutCreateWindow('Bifurcation Diagram')
# bif = BifurcationContext()
# bif.cob = cob
# cob.bif = bif
# glutDisplayFunc(bif.display)
# glutSpecialFunc(bif.specialInput)
# glutKeyboardFunc(bif.keyboard)
# glutMouseFunc(bif.mouse)
#
# glutMainLoop()
