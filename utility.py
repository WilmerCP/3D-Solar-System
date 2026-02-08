import pygame
from OpenGL.GL import *
from PyQt5.QtGui import QImage

def load_shader_source(path):
    with open(path, 'r') as file:
        return file.read()

def load_texture_qt(path):
    image = QImage(path)

    if image.isNull():
        raise RuntimeError(f"Failed to load texture: {path}")

    # Ensure RGBA8 format
    image = image.convertToFormat(QImage.Format_RGBA8888)

    width = image.width()
    height = image.height()

    # QImage stores pixels upside-down relative to OpenGL
    image = image.mirrored()

    ptr = image.bits()
    ptr.setsize(image.byteCount())
    data = ptr.asstring()

    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)

    glTexImage2D(
        GL_TEXTURE_2D,
        0,
        GL_RGBA,
        width,
        height,
        0,
        GL_RGBA,
        GL_UNSIGNED_BYTE,
        data
    )

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)

    glBindTexture(GL_TEXTURE_2D, 0)

    #print('texture loaded with Qt:', tex_id)
    return tex_id


def load_texture(path):
    surface = pygame.image.load(path).convert_alpha()

    width, height = surface.get_size()
    data = pygame.image.tostring(surface, "RGBA", True)

    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)

    glTexImage2D(
        GL_TEXTURE_2D, 0, GL_RGBA,
        width, height, 0,
        GL_RGBA, GL_UNSIGNED_BYTE, data
    )

    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

    glBindTexture(GL_TEXTURE_2D, 0)
    return tex_id
