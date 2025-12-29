import math
import numpy as np

RADIUS = 1.0
STACKS = 20     # vertical divisions
SECTORS = 30    # horizontal divisions

def get_sphere_vertices():

    vertices = []

    for i in range(STACKS + 1):
        phi = np.pi * i / STACKS - np.pi / 2   # -90 to +90 degrees
        y = RADIUS * np.sin(phi)
        r = RADIUS * np.cos(phi)

        for j in range(SECTORS + 1):
            theta = 2 * np.pi * j / SECTORS  # 0 to 360 degrees

            x = r * np.cos(theta)
            z = r * np.sin(theta)
            vertices.extend([x, y, z])

    return np.array(vertices, dtype=np.float32)

def get_sphere_indices():
    indices = []

    for i in range(STACKS):
        for j in range(SECTORS + 1):
            first  = i * (SECTORS + 1) + j
            second = first + SECTORS + 1

            indices.extend([first, second])

    return np.array(indices, dtype=np.uint32)


def get_view_matrix(distance,pitch_degrees):
    pitch = np.radians(pitch_degrees) 
    # Rotation matrix around X axis
    Rx = np.array([
        [1, 0,           0,          0],
        [0, np.cos(pitch), -np.sin(pitch), 0],
        [0, np.sin(pitch),  np.cos(pitch), 0],
        [0, 0,           0,          1]
    ], dtype=np.float32)

    view = np.array([[1, 0, 0, 0],
                     [0, 1, 0, 0],
                     [0, 0, 1, -distance],
                     [0, 0, 0, 1]], dtype=np.float32)
    return view @ Rx

def get_projection_matrix(fov, aspect, near, far):

    c = 1 / math.tan(fov / 2)

    projection = np.array([[c / aspect, 0, 0, 0],
                     [0, c, 0, 0],
                     [0, 0, (far + near) / (near - far), (2 * far * near) / (near - far)],
                     [0, 0, -1, 0]], dtype=np.float32)
    return projection

def get_model_matrix():
    scale = 2.0  # Set your desired scale
    model = np.array([
        [scale, 0,     0,     0],
        [0,     scale, 0,     0],
        [0,     0,     scale, 0],
        [0,     0,     0,     1]
    ], dtype=np.float32)
    return model

def get_background_vertices():
    vertices = [
        -1.0,  1.0, 0.0,
        -1.0, -1.0, 0.0,
         1.0, -1.0, 0.0,
         1.0,  1.0, 0.0
    ]
    return np.array(vertices, dtype=np.float32)