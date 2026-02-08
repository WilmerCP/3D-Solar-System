import numpy as np
from OpenGL.GL import *

class Planet:
    def __init__(self,
                 name: str,
                 radius: float = 1.0,
                 orbit_radius: float = 0.0,
                 orbit_speed: float = 0.0,
                 spin_speed: float = 0.0,
                 color_left: np.ndarray = np.array([1.0, 1.0, 0.0]),   # horizontal gradient start
                 color_right: np.ndarray = np.array([1.0, 0.5, 0.0]),  # vertical gradient bright
                 parent: 'Planet' = None 
                 ):
        self.name = name
        self.radius = radius
        self.orbit_radius = orbit_radius
        self.orbit_speed = orbit_speed      # radians per second
        self.spin_speed = spin_speed        # radians per second
        self.color_left = color_left
        self.color_right = color_right
        self.vao = None
        self.program = None
        self.parent = parent 

        # Current angles for orbit and spin
        self.orbit_angle = 0.0
        self.spin_angle = 0.0

        # Current position in world space
        self.position = np.array([self.orbit_radius, 0.0, 0.0], dtype=float)
        self.previous_position = np.array([self.orbit_radius, 0.0, 0.0], dtype=float)
        self.time = 0.0

    def update(self, delta_time: float):
        """Update orbit and spin angles based on elapsed time."""
        self.orbit_angle += self.orbit_speed * delta_time
        self.spin_angle += self.spin_speed * delta_time

        # Update planet position based on orbit
        x = self.orbit_radius * np.cos(self.orbit_angle)
        z = self.orbit_radius * np.sin(self.orbit_angle)
        local_position = np.array([x, 0.0, z])

        if self.parent is not None:
            self.previous_position = self.position
            self.position = self.parent.position + local_position
        else:
            self.previous_position = self.position
            self.position = local_position

        self.time = delta_time

    def get_model_matrix(self):
        """Return a model matrix for rendering this planet (numpy 4x4)."""
        # Translation
        T = np.identity(4)
        T[:3, 3] = self.position

        # Scaling
        S = np.identity(4)
        S[0, 0] = self.radius
        S[1, 1] = self.radius
        S[2, 2] = self.radius

        # Spin rotation around Y
        cos_a = np.cos(self.spin_angle)
        sin_a = np.sin(self.spin_angle)
        R = np.identity(4)
        R[0, 0] = cos_a
        R[0, 2] = sin_a
        R[2, 0] = -sin_a
        R[2, 2] = cos_a

        # Model matrix: Translation * Rotation * Scale
        model = T @ R @ S
        return model
    
    def get_velocity_vector(self):

        vector = self.position - self.previous_position
        normalized = vector / np.linalg.norm(vector)

        return normalized

    def update_uniforms(self):
        """
        Update the shader uniforms for this planet.
        Assumes shader_program is bound.
        """
        # Colors
        color_left_loc = glGetUniformLocation(self.program, "color_left")
        color_right_loc = glGetUniformLocation(self.program, "color_right")

        glUniform3fv(color_left_loc, 1, self.color_left)
        glUniform3fv(color_right_loc, 1, self.color_right)

class Sun(Planet):
    def __init__(self, name, radius=1.0, orbit_radius=0.0, orbit_speed=0.0, spin_speed=0.0):
        super().__init__(name, radius, orbit_radius, orbit_speed, spin_speed)
        

    def update_uniforms(self):
        time_loc = glGetUniformLocation(self.program, "time")
        glUniform1f(time_loc,self.time)

class TexturedPlanet(Planet):
    def __init__(self, name, radius=1.0, orbit_radius=0.0, orbit_speed=0.0, spin_speed=0.0):
        super().__init__(name, radius, orbit_radius, orbit_speed, spin_speed)

        self.texture_unit = None
        self.texture_id = None
        

    def update_uniforms(self):
        #time_loc = glGetUniformLocation(shader_program, "time")
        #glUniform1f(time_loc,self.time)

        glActiveTexture(GL_TEXTURE0 + self.texture_unit)
        glBindTexture(GL_TEXTURE_2D, self.texture_id)  # texture_id must be the correct OpenGL texture handle

        uTexture_loc = glGetUniformLocation(self.program, "texture")
        glUniform1i(uTexture_loc, self.texture_unit)