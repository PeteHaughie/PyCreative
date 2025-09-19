"""
Module for creating and managing Framebuffer Objects (FBOs) using OpenGL via pygame.
"""
import pygame
from OpenGL.GL import *

class FBO:
    """
    Framebuffer Object for offscreen rendering.
    """
    def __init__(self, width, height):
        """
        Create an FBO with a texture attachment.
        Args:
            width (int): Width of the FBO.
            height (int): Height of the FBO.
        """
        self.width = width
        self.height = height
        self.fbo = glGenFramebuffers(1)
        self.texture = glGenTextures(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
        glBindTexture(GL_TEXTURE_2D, self.texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.texture, 0)
        status = glCheckFramebufferStatus(GL_FRAMEBUFFER)
        if status != GL_FRAMEBUFFER_COMPLETE:
            raise RuntimeError(f"FBO incomplete: {status}")
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

    def bind(self):
        """
        Bind the FBO for rendering.
        """
        glBindFramebuffer(GL_FRAMEBUFFER, self.fbo)
        glViewport(0, 0, self.width, self.height)

    def unbind(self):
        """
        Unbind the FBO (return to default framebuffer).
        """
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
