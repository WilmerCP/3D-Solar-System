from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import QTimer
from OpenGL.GL import *
import numpy as np
import time
import geometry
import utility
import time
import math
from planet import Planet
from planet import Sun
from planet import TexturedPlanet

class SolarSystemGL(QOpenGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.start_time = time.time()

        # Timer → drives animation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(16)  # ~60 FPS

    @staticmethod
    def create_shader_program(vertex_shader_source, fragment_shader_source):
        # Create a OpenGL program and shaders
        program = glCreateProgram()
        vertex_shader = glCreateShader(GL_VERTEX_SHADER)
        fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)

        # Set shader source code
        glShaderSource(vertex_shader, vertex_shader_source)
        glShaderSource(fragment_shader, fragment_shader_source)

        # Compile shaders

        glCompileShader(vertex_shader)
        if not glGetShaderiv(vertex_shader, GL_COMPILE_STATUS):
            error = glGetShaderInfoLog(vertex_shader).decode()
            print("Vertex shader compilation error:", error)
            raise RuntimeError("Vertex shader compilation failed")
        glCompileShader(fragment_shader)
        if not glGetShaderiv(fragment_shader, GL_COMPILE_STATUS):
            error = glGetShaderInfoLog(fragment_shader).decode()
            print("Fragment shader compilation error:", error)
            raise RuntimeError("Fragment shader compilation failed")
        # Link shaders to the program

        glAttachShader(program, vertex_shader)
        glAttachShader(program, fragment_shader)
        # Link the program
        glLinkProgram(program)

        if not glGetProgramiv(program,GL_LINK_STATUS):
            print(glGetProgramInfoLog(program))
            raise RuntimeError('Linking error')

        # Get rid of the shaders 
        glDetachShader(program, vertex_shader)
        glDetachShader(program, fragment_shader)

        #Set the default program for usage
        glUseProgram(program)
        return program

    @staticmethod
    def setup_buffer(program,data,index_data):

        vao = glGenVertexArrays(1)
        glBindVertexArray(vao)

        #Request buffer slot from GPU and set as current
        buffer = glGenBuffers(1)
        glBindBuffer(GL_ARRAY_BUFFER, buffer)

        # Upload data to GPU
        # numpy provides the size in bytes of the array with nbytes
        glBufferData(GL_ARRAY_BUFFER,data.nbytes,data,GL_DYNAMIC_DRAW)

        stride = 3*4
        #offset for position is 0
        offset = ctypes.c_void_p(0)
        # Find the location for "position" and enable it
        loc = glGetAttribLocation(program, "position")
        glEnableVertexAttribArray(loc)
        #tell OpenGL how to interpret the position attribute
        glVertexAttribPointer(loc, 3, GL_FLOAT, False, stride, offset)

        EBO = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, EBO)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, index_data.nbytes, index_data, GL_STATIC_DRAW)

        glBindVertexArray(0)
        return vao

    @staticmethod
    def setup_program_uniforms(program,view_matrix,projection_matrix,model_matrix):

        glUseProgram(program)

        view_loc = glGetUniformLocation(program, "view")
        glUniformMatrix4fv(view_loc, 1, GL_FALSE, view_matrix.T)

        projection_loc = glGetUniformLocation(program, "projection")
        glUniformMatrix4fv(projection_loc, 1, GL_FALSE, projection_matrix.T)

        model_loc = glGetUniformLocation(program, "model")
        glUniformMatrix4fv(model_loc, 1, GL_FALSE, model_matrix.T)

    @staticmethod
    def draw_planet(object,delta_time):
            #Use the sphere program
            glUseProgram(object.program)

            object.update(delta_time)

            glBindVertexArray(object.vao)
            model_loc = glGetUniformLocation(object.program, "model")

            model_matrix = object.get_model_matrix()
            glUniformMatrix4fv(model_loc, 1, GL_FALSE, model_matrix.T)

            object.update_uniforms()

            indices_per_strip = (geometry.SECTORS + 1) * 2

            offset = 0
            for i in range(geometry.STACKS):
                glDrawElements(GL_TRIANGLE_STRIP,indices_per_strip,GL_UNSIGNED_INT,ctypes.c_void_p(offset * 4))
                offset += indices_per_strip

            glBindVertexArray(0)

    def initializeGL(self):
        glEnable(GL_DEPTH_TEST)
        glClearColor(0.0, 0.0, 0.0, 1.0)

        self.last_time = time.time()

        # Vertex shader with color source code
        vertex_shader_source = utility.load_shader_source("shaders/planet_vertex.glsl")
        # Fragment shader with color source code
        fragment_shader_source = utility.load_shader_source("shaders/planet_fragment.glsl")

        sun_vertex = utility.load_shader_source("shaders/sun_vertex.glsl")
        sun_fragment = utility.load_shader_source("shaders/sun_fragment.glsl")

        textured_vertex = utility.load_shader_source("shaders/textured_vertex.glsl")
        textured_fragment = utility.load_shader_source("shaders/textured_fragment.glsl")

        glEnable(GL_DEPTH_TEST)      # Enable depth testing
        glDepthFunc(GL_LESS)    # Specify depth test function

        program = self.create_shader_program(vertex_shader_source, fragment_shader_source)
        program_sun = self.create_shader_program(sun_vertex, sun_fragment)
        program_textured = self.create_shader_program(textured_vertex,textured_fragment)

        # Build vertex data for a sphere
        data = geometry.get_sphere_vertices()

        index_data = geometry.get_sphere_indices()

        vao_planet = self.setup_buffer(program, data,index_data)
        vao_sun = self.setup_buffer(program_sun, data,index_data)

        aspect = 800 / 600
        view_matrix = geometry.get_view_matrix(80,15)
        projection_matrix = geometry.get_projection_matrix(math.radians(45), aspect, 0.1, 150.0)
        model_matrix = np.identity(4)

        self.setup_program_uniforms(program,view_matrix,projection_matrix,model_matrix)
        self.setup_program_uniforms(program_sun,view_matrix,projection_matrix,model_matrix)
        self.setup_program_uniforms(program_textured,view_matrix,projection_matrix,model_matrix)

        #Create planets

        sun = Sun("Sun", radius=5.0, spin_speed=math.radians(20))
        sun.vao = vao_sun
        sun.program = program_sun

        earth = TexturedPlanet("Earth", radius=1.3,
                orbit_radius=18.0,
                orbit_speed=1,
                spin_speed=1.8)
        earth.vao = vao_planet
        earth.orbit_angle = math.radians(0)
        earth.program = program_textured

        texture_id = utility.load_texture_qt("textures/flat_earth.jpg")
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        earth.texture_unit = 0
        earth.texture_id = texture_id

        mercury = Planet("Mercury", radius=0.5,
                color_left=np.array([0.7, 0.7, 0.6]),
                color_right=np.array([0.5, 0.4, 0.3]),
                orbit_radius=12.0,
                orbit_speed=3.0,
                spin_speed=2)
        mercury.vao = vao_planet
        mercury.orbit_angle = math.radians(20)
        mercury.program = program

        venus = Planet("Venus", radius=1.2,
                color_left=np.array([0.95, 0.85, 0.55]),
                color_right=np.array([0.9, 0.75, 0.35]),
                orbit_radius=15.6,
                orbit_speed=1.62,
                spin_speed=-1.5)
        venus.vao = vao_planet
        venus.orbit_angle = math.radians(180)
        venus.program = program

        mars = Planet("Mars", radius=1.0,
                color_left=np.array([0.85, 0.45, 0.25]),
                color_right=np.array([0.6, 0.3, 0.18]),
                orbit_radius=21.0,
                orbit_speed=0.73,
                spin_speed=3.1)
        mars.vao = vao_planet
        mars.orbit_angle = math.radians(100)
        mars.program = program

        jupiter = Planet("Jupiter", radius=3.0,
                color_left=np.array([0.95, 0.85, 0.65]),
                color_right=np.array([0.85, 0.55, 0.25]),
                orbit_radius=24.0,
                orbit_speed=0.06,
                spin_speed=4)
        jupiter.vao = vao_planet
        jupiter.orbit_angle = math.radians(270)
        jupiter.program = program

        saturn = Planet("Saturn", radius=2.5,
                color_left=np.array([0.95, 0.90, 0.70]),
                color_right=np.array([0.85, 0.75, 0.45]),
                orbit_radius=29.0,
                orbit_speed=0.18,
                spin_speed=9)
        saturn.vao = vao_planet
        saturn.orbit_angle = math.radians(200)
        saturn.program = program

        uranus = Planet("Uranus", radius=1.7,
                color_left=np.array([0.65, 0.85, 0.95]),
                color_right=np.array([0.45, 0.75, 0.95]),
                orbit_radius=35.0,
                orbit_speed=0.1,
                spin_speed=-8)
        uranus.vao = vao_planet
        uranus.orbit_angle = math.radians(90)
        uranus.program = program

        neptune = Planet("Neptune", radius=1.6,
                color_left=np.array([0.35, 0.55, 0.95]),
                color_right=np.array([0.25, 0.35, 0.75]),
                orbit_radius=40.0,
                orbit_speed=0.08,
                spin_speed=8.0)
        neptune.vao = vao_planet
        neptune.orbit_angle = math.radians(140)
        neptune.program = program

        self.planets = [sun,earth,mercury,venus,mars,jupiter,saturn,uranus,neptune]


    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)

        # Rebuild projection matrix here if needed

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        current_time = time.time()
        delta_time = current_time - self.last_time
        self.last_time = current_time
        
        #Clear the screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        for p in self.planets:
            self.draw_planet(p,delta_time)

