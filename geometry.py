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

def get_look_at_matrix(eye, target, up):
    f = target - eye
    f = f / np.linalg.norm(f)

    r = np.cross(f,up)
    r = r / np.linalg.norm(r)

    up = np.cross(r,f)

    lookAt = np.array([
        [r[0],r[1],r[2], -np.dot(r,eye)],
        [up[0],up[1],up[2],-np.dot(up,eye)],
        [-f[0],-f[1],-f[2],np.dot(f,eye)],
        [0,0,0,1]
    ],dtype=np.float32)

    return lookAt



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

def get_orbit_ring_vertices(radius, segments=100):
    vertices = []
    for i in range(segments + 1):
        angle = 2 * np.pi * i / segments
        x = radius * np.cos(angle)
        z = radius * np.sin(angle)
        vertices.extend([x, 0.0, z])
    return np.array(vertices, dtype=np.float32)

#normalize screen coordinates into -1 to 1 range
def get_ndc(x,size):

    return (2*x)/(size) - 1


def calulate_forward_vector(pitch,yaw):

    pitch_rad = math.radians(pitch)
    yaw_rad = math.radians(yaw)

    component_x = 0
    component_y = np.sin(pitch_rad)
    component_z = np.cos(pitch_rad)

    component_x = np.cos(pitch_rad) * np.sin(yaw_rad)
    component_z = np.cos(pitch_rad) * np.cos(yaw_rad)

    forward = np.array([component_x,component_y,-component_z])

    return forward


def calculate_turn_amout(coordinate):

    if(coordinate is None):
        return 0.0

    amount = 0.0

    if(coordinate > 0.10):
        amount = 0.1
        if(coordinate > 0.40):
            amount = 0.2
            if(coordinate > 0.70):
                amount = 0.3
    elif(coordinate < -0.10):
        amount = -0.1
        if(coordinate < -0.40):
            amount = -0.2
            if(coordinate < -0.70):
                amount = -0.3
    
    return amount

def get_ray_vertices(p1,p2):
    origin = p1.copy()
    origin[1] -= 0.1
    end_point = p1 + p2*200

    print(origin)
    print(p1)

    return np.array([origin[0], origin[1], origin[2], end_point[0], end_point[1], end_point[2]], dtype=np.float32)
    #return np.array([end_point[0], end_point[1], end_point[2], 10, 10, 100], dtype=np.float32)