from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtCore import QTimer, Qt
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
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus() 

        # Timer → drives animation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(16)  # ~60 FPS
        self.camera_distance = 80
        self.camera_pitch = 15
        self.aspect = 800 / 600
        self.program_background = None
        self.background_vao = None

    def keyPressEvent(self, event):

        if event.key() == Qt.Key_W:
            self.camera_distance -= 1  # Move closer
        elif event.key() == Qt.Key_S:
            self.camera_distance += 1  # Move farther
        elif event.key() == Qt.Key_Up:
            self.camera_pitch += 1     # Look up
        elif event.key() == Qt.Key_Down:
            self.camera_pitch -= 1     # Look down
        elif event.key() == Qt.Key_Escape:
            self.close()

        # Clamp camera distance to avoid going through the scene
        self.camera_distance = max(10, min(self.camera_distance, 200))
        self.camera_pitch = max(-89, min(self.camera_pitch, 89)) 
        
        self.view_matrix = geometry.get_view_matrix(self.camera_distance, self.camera_pitch)
        self.projection_matrix = geometry.get_projection_matrix(
            math.radians(45), self.aspect, 0.1, 300.0
        )
        self.model_matrix = np.identity(4)

        # Update all programs' uniforms
     
        for p in self.planets:
            self.setup_program_uniforms(p.program, self.view_matrix, self.projection_matrix, self.model_matrix)
            self.setup_program_uniforms(self.program_ring, self.view_matrix, self.projection_matrix, self.model_matrix)
        self.update()  # Request a redraw

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

        if index_data is not None:
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

    def paint_background(self):
        glDepthMask(GL_FALSE)
        glUseProgram(self.program_background)
        glBindVertexArray(self.background_vao)
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.texture_bg)
        bg_texture_loc = glGetUniformLocation(self.program_background, "bgTexture")
        glUniform1i(bg_texture_loc, 1)

        glDrawArrays(GL_TRIANGLE_FAN, 0, 4)
        glBindVertexArray(0)
        glDepthMask(GL_TRUE)

    
    def draw_planet(self,object,delta_time):
            #Use the sphere program
            glUseProgram(object.program)

            object.update(delta_time)

            glBindVertexArray(object.vao)
            model_loc = glGetUniformLocation(object.program, "model")

            model_matrix = object.get_model_matrix()
            self.setup_program_uniforms(object.program, self.view_matrix, self.projection_matrix, model_matrix)

            object.update_uniforms()

            indices_per_strip = (geometry.SECTORS + 1) * 2

            offset = 0
            for i in range(geometry.STACKS):
                glDrawElements(GL_TRIANGLE_STRIP,indices_per_strip,GL_UNSIGNED_INT,ctypes.c_void_p(offset * 4))
                offset += indices_per_strip

            glUseProgram(self.program_ring)
            glBindVertexArray(self.ring_vao)
            scaling_matrix = np.identity(4, dtype=np.float32)
            scaling_matrix[0, 0] = object.orbit_radius  
            scaling_matrix[1, 1] = 1.0     
            scaling_matrix[2, 2] = object.orbit_radius 
            
            model_matrix = np.dot(self.model_matrix,scaling_matrix)

            self.setup_program_uniforms(self.program_ring,self.view_matrix,self.projection_matrix,model_matrix)
            ring_color = np.array([1.0, 1.0, 1.0], dtype=np.float32)
            ring_color_loc = glGetUniformLocation(self.program_ring, "ringColor")
            glUniform3fv(ring_color_loc, 1, ring_color)  # White color, for example
            
            glDrawArrays(GL_LINE_STRIP, 0, 101)
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

        background_vertex = utility.load_shader_source("shaders/bg_vertex.glsl")
        background_fragment = utility.load_shader_source("shaders/bg_fragment.glsl")

        ring_vertex = utility.load_shader_source("shaders/ring_vertex.glsl")
        ring_fragment = utility.load_shader_source("shaders/ring_fragment.glsl")

        background_vertices = geometry.get_background_vertices()
        ring_vertices = geometry.get_orbit_ring_vertices(radius=1.0, segments=100)

        glEnable(GL_DEPTH_TEST)      # Enable depth testing
        glDepthFunc(GL_LESS)    # Specify depth test function

        program = self.create_shader_program(vertex_shader_source, fragment_shader_source)
        program_sun = self.create_shader_program(sun_vertex, sun_fragment)
        program_textured = self.create_shader_program(textured_vertex,textured_fragment)
        self.program_ring = self.create_shader_program(ring_vertex,ring_fragment)

        self.ring_vao = self.setup_buffer(self.program_ring, ring_vertices, None)

        glUseProgram(self.program_ring)
        ring_color = np.array([1.0, 1.0, 1.0], dtype=np.float32)
        ring_color_loc = glGetUniformLocation(self.program_ring, "ringColor")
        glUniform3fv(ring_color_loc, 1, ring_color)
        glUseProgram(0)

        self.program_background = self.create_shader_program(background_vertex,background_fragment)
        self.background_vao = self.setup_buffer(self.program_background, background_vertices, None)

        self.texture_bg = utility.load_texture_qt("textures/space.jpg")
        glActiveTexture(GL_TEXTURE1)
        glBindTexture(GL_TEXTURE_2D, self.texture_bg)
        bg_texture_loc = glGetUniformLocation(self.program_background, "bgTexture")
        glUniform1i(bg_texture_loc, 1)

        # Build vertex data for a sphere
        data = geometry.get_sphere_vertices()

        index_data = geometry.get_sphere_indices()

        vao_planet = self.setup_buffer(program, data,index_data)
        vao_sun = self.setup_buffer(program_sun, data,index_data)

        view_matrix = geometry.get_view_matrix(80,15)
        projection_matrix = geometry.get_projection_matrix(math.radians(45), self.aspect, 0.1, 300.0)
        model_matrix = np.identity(4)

        self.setup_program_uniforms(program,view_matrix,projection_matrix,model_matrix)
        self.setup_program_uniforms(program_sun,view_matrix,projection_matrix,model_matrix)
        self.setup_program_uniforms(program_textured,view_matrix,projection_matrix,model_matrix)
        self.setup_program_uniforms(self.program_ring,view_matrix,projection_matrix,model_matrix)
        
        self.model_matrix = model_matrix
        self.view_matrix = view_matrix
        self.projection_matrix = projection_matrix

        #Create planets

        sun = Sun("Sun", radius=5.0, spin_speed=math.radians(20))
        sun.vao = vao_sun
        sun.program = program_sun

        earth = TexturedPlanet("Earth", radius=1.3,
                orbit_radius=20.0,
                orbit_speed=1,
                spin_speed=1.8)
        earth.vao = vao_planet
        earth.orbit_angle = math.radians(0)
        earth.program = program_textured

        moon = Planet("Moon", radius=0.27, orbit_radius=2.1, orbit_speed=2.0, parent=earth,    
                color_left=np.array([0.8, 0.8, 0.78]),
                color_right=np.array([0.6, 0.6, 0.58]),)
        moon.vao = vao_planet
        moon.orbit_angle = math.radians(0)
        moon.program = program

        texture_id = utility.load_texture_qt("textures/flat_earth.jpg")
        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, texture_id)
        earth.texture_unit = 0
        earth.texture_id = texture_id

        mercury = Planet("Mercury", radius=0.5,
                color_left=np.array([0.7, 0.7, 0.6]),
                color_right=np.array([0.5, 0.4, 0.3]),
                orbit_radius=14.0,
                orbit_speed=3.0,
                spin_speed=2)
        mercury.vao = vao_planet
        mercury.orbit_angle = math.radians(20)
        mercury.program = program

        venus = Planet("Venus", radius=1.2,
                color_left=np.array([0.95, 0.85, 0.55]),
                color_right=np.array([0.9, 0.75, 0.35]),
                orbit_radius=25.6,
                orbit_speed=1.62,
                spin_speed=-1.5)
        venus.vao = vao_planet
        venus.orbit_angle = math.radians(180)
        venus.program = program

        mars = Planet("Mars", radius=1.0,
                color_left=np.array([0.85, 0.45, 0.25]),
                color_right=np.array([0.6, 0.3, 0.18]),
                orbit_radius=33.0,
                orbit_speed=0.73,
                spin_speed=3.1)
        mars.vao = vao_planet
        mars.orbit_angle = math.radians(100)
        mars.program = program

        jupiter = Planet("Jupiter", radius=3.0,
                color_left=np.array([0.95, 0.85, 0.65]),
                color_right=np.array([0.85, 0.55, 0.25]),
                orbit_radius=41.0,
                orbit_speed=0.06,
                spin_speed=4)
        jupiter.vao = vao_planet
        jupiter.orbit_angle = math.radians(270)
        jupiter.program = program

        saturn = Planet("Saturn", radius=2.5,
                color_left=np.array([0.95, 0.90, 0.70]),
                color_right=np.array([0.85, 0.75, 0.45]),
                orbit_radius=48.0,
                orbit_speed=0.18,
                spin_speed=9)
        saturn.vao = vao_planet
        saturn.orbit_angle = math.radians(200)
        saturn.program = program

        uranus = Planet("Uranus", radius=1.7,
                color_left=np.array([0.65, 0.85, 0.95]),
                color_right=np.array([0.45, 0.75, 0.95]),
                orbit_radius=55.0,
                orbit_speed=0.1,
                spin_speed=-8)
        uranus.vao = vao_planet
        uranus.orbit_angle = math.radians(90)
        uranus.program = program

        neptune = Planet("Neptune", radius=1.6,
                color_left=np.array([0.35, 0.55, 0.95]),
                color_right=np.array([0.25, 0.35, 0.75]),
                orbit_radius=60.0,
                orbit_speed=0.08,
                spin_speed=8.0)
        neptune.vao = vao_planet
        neptune.orbit_angle = math.radians(140)
        neptune.program = program

        self.planets = [sun,earth,moon,mercury,venus,mars,jupiter,saturn,uranus,neptune]


    def resizeGL(self, w, h):
        glViewport(0, 0, w, h)

        # Rebuild projection matrix
        self.aspect = w / h
        projection_matrix = geometry.get_projection_matrix(math.radians(45), self.aspect, 0.1, 300.0)
        self.projection_matrix = projection_matrix
        

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        current_time = time.time()
        delta_time = current_time - self.last_time
        self.last_time = current_time
        
        #Clear the screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.paint_background()

        for p in self.planets:
            self.draw_planet(p,delta_time)

