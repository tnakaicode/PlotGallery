import cv2
import numpy as np
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *


def main():
    DISPLAY_WIDTH = 900
    DISPLAY_HEIGHT = 900

    pygame.init()
    pygame.display.set_mode(
        (DISPLAY_WIDTH, DISPLAY_HEIGHT), DOUBLEBUF | OPENGL)
    gluPerspective(90, (DISPLAY_WIDTH / DISPLAY_HEIGHT), 0.01, 12)

    glEnable(GL_TEXTURE_2D)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)

    glRotatef(-90, 1, 0, 0)  # Straight rotation
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glRotatef(285, 0, 0, 1)  # Rotate yaw
    glTranslatef(-5, -3, -2)  # Move to position

    # Draw rectangle
    glBegin(GL_QUADS)
    glColor3f(1, 0, 0)
    glVertex3f(2, 2, 0)
    glVertex3f(2, 2, 2)
    glVertex3f(2, 6, 2)
    glVertex3f(2, 6, 0)
    glEnd()

    image_buffer = glReadPixels(
        0, 0, DISPLAY_WIDTH, DISPLAY_HEIGHT, OpenGL.GL.GL_RGB, OpenGL.GL.GL_UNSIGNED_BYTE)
    image = np.frombuffer(image_buffer, dtype=np.uint8).reshape(
        DISPLAY_WIDTH, DISPLAY_HEIGHT, 3)

    cv2.imwrite("image.png", image)

    pygame.quit()


if __name__ == "__main__":
    main()
    # AttributeError: module 'numpy' has no attribute 'float128'
