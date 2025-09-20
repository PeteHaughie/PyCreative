"""
Example: Initializing an OpenGL context with Pygame and using FBO.
"""

import pygame
from OpenGL.GL import glClearColor, glClear, GL_COLOR_BUFFER_BIT
import sys

sys.path.append("src")
from fbo import FBO


def main():
    pygame.init()
    pygame.display.set_mode((640, 480), pygame.OPENGL | pygame.DOUBLEBUF)
    pygame.display.set_caption("OpenGL Context Example")

    # Create an FBO for offscreen rendering
    fbo = FBO(256, 256)

    from OpenGL.GL import (
        glClearColor,
        glClear,
        GL_COLOR_BUFFER_BIT,
        glBegin,
        glEnd,
        glVertex2f,
        glColor3f,
        GL_TRIANGLES,
        glEnable,
        glBindTexture,
        glTexCoord2f,
        GL_TEXTURE_2D,
        GL_QUADS,
        glDisable,
        glViewport,
        glMatrixMode,
        glLoadIdentity,
        GL_PROJECTION,
        GL_MODELVIEW,
    )
    from OpenGL.GLU import gluOrtho2D

    width, height = 640, 480
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

        # --- Render to FBO ---
        fbo.bind()
        glViewport(0, 0, fbo.width, fbo.height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, fbo.width, 0, fbo.height)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glClearColor(0.2, 0.3, 0.4, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        # Draw a colored triangle to the FBO
        glBegin(GL_TRIANGLES)
        glColor3f(1, 0, 0)
        glVertex2f(30, 30)
        glColor3f(0, 1, 0)
        glVertex2f(fbo.width - 30, 30)
        glColor3f(0, 0, 1)
        glVertex2f(fbo.width // 2, fbo.height - 30)
        glEnd()
        fbo.unbind()

        # --- Render to screen (default framebuffer) ---
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, width, 0, height)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()
        glClearColor(0.1, 0.1, 0.1, 1.0)
        glClear(GL_COLOR_BUFFER_BIT)
        # Draw the FBO texture to the screen using a textured quad
        glEnable(GL_TEXTURE_2D)
        glBindTexture(GL_TEXTURE_2D, fbo.texture)
        glBegin(GL_QUADS)
        glTexCoord2f(0, 0)
        glVertex2f(100, 100)
        glTexCoord2f(1, 0)
        glVertex2f(356, 100)
        glTexCoord2f(1, 1)
        glVertex2f(356, 356)
        glTexCoord2f(0, 1)
        glVertex2f(100, 356)
        glEnd()
        glBindTexture(GL_TEXTURE_2D, 0)
        glDisable(GL_TEXTURE_2D)

        pygame.display.flip()
        pygame.time.wait(10)

    pygame.quit()


if __name__ == "__main__":
    main()
