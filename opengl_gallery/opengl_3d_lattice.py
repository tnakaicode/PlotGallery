import random
import math
from OpenGL.GL import *
from OpenGL.GLU import *
from OpenGL.GLUT import *


# Define xyz index
PX = 0
PY = 1
PZ = 2
VX = 3
VY = 4
VZ = 5
FX = 6
FY = 7
FZ = 8

# mouse move
mx = 0.0
my = 0.0

# lattice size
lsize = 1.0

# init pos is .. 20 * 20 * 20
PN = 8000
th = math.pi * 0.5
ph = math.pi * 0.5

# ready to 9 parameters for particle
#(PX, PY, PZ, VX, VY, VZ, FX, FY, FZ)
xyz = [[0 for i in range(9)] for j in range(PN)]


def init_lattice():

    # dens^3 = PN
    dens = 20
    delt = lsize / dens
    xv_sum = 0
    yv_sum = 0
    zv_sum = 0

    pnum = 0
    k = 0
    while k < dens:
        j = 0
        while j < dens:
            i = 0
            while i < dens:
                xyz[pnum][PX] = delt * i
                xyz[pnum][PY] = delt * j
                xyz[pnum][PZ] = delt * k
                pnum += 1
                i += 1
            j += 1
        k += 1


def draw():
    cx = cy = cz = lsize * 0.5
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClearColor(0.0, 0.0, 0.0, 1.0)

    glLoadIdentity()
    glColor3f(1.0, 1.0, 0.0)

    gluLookAt(5 * math.sin(th) * math.cos(ph) + cx, 5 * math.cos(th) + cy, 5 * math.sin(th) * math.sin(ph) + cz,
              cx, cy, cz, -math.cos(th) * math.cos(ph), math.sin(th), -math.cos(th) * math.sin(ph))

    glBegin(GL_LINE_LOOP)
    glVertex3d(0, 0, 0)
    glVertex3d(0, lsize, 0)
    glVertex3d(lsize, lsize, 0)
    glVertex3d(lsize, 0, 0)
    glEnd()
    glBegin(GL_LINE_LOOP)
    glVertex3d(0, 0, lsize)
    glVertex3d(0, lsize, lsize)
    glVertex3d(lsize, lsize, lsize)
    glVertex3d(lsize, 0, lsize)
    glEnd()
    glBegin(GL_LINES)
    glVertex3d(0, 0, 0)
    glVertex3d(0, 0, lsize)
    glEnd()
    glBegin(GL_LINES)
    glVertex3d(0, lsize, 0)
    glVertex3d(0, lsize, lsize)
    glEnd()
    glBegin(GL_LINES)
    glVertex3d(lsize, 0, 0)
    glVertex3d(lsize, 0, lsize)
    glEnd()
    glBegin(GL_LINES)
    glVertex3d(lsize, lsize, 0)
    glVertex3d(lsize, lsize, lsize)
    glEnd()

    nnum = 0
    while nnum < len(xyz):
        glPointSize(3.0)
        glColor3f(0.3, 0.3, 1.0)
        glBegin(GL_POINTS)
        glVertex3d(xyz[nnum][PX], xyz[nnum][PY], xyz[nnum][PZ])
        glEnd()
        nnum = nnum + 1

    glutSwapBuffers()


def init():
    glClearColor(0.7, 0.7, 0.7, 0.7)


def idle():
    glutPostRedisplay()


def reshape(w, h):
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(30.0, w / h, 1.0, 100.0)
    glMatrixMode(GL_MODELVIEW)


def motion(x, y):
    global ph, th, mx, my

    dltx = mx - x
    dlty = my - y

    # Invalid large motion
    if 10 < abs(dltx):
        dltx = 0
    if 10 < abs(dlty):
        dlty = 0

    ph = ph - 0.01 * dltx
    th = th + 0.01 * dlty
    glutPostRedisplay()
    glutSwapBuffers()
    mx = x
    my = y


if __name__ == "__main__":
    init_lattice()

    glutCreateWindow("pyOpenGL TEST".encode('utf-8'))
    glutInitWindowPosition(50, 50)
    glutInitWindowSize(340, 340)
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE)
    glutDisplayFunc(draw)
    glutReshapeFunc(reshape)
    glutMotionFunc(motion)
    init()
    glutIdleFunc(idle)
    glutMainLoop()

    # "./img/20200206180433.png"
    # "./img/20200206180445.png"
