from PyQt5.QtWidgets import QOpenGLWidget
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
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

MODE_NORMAL = 0
MODE_FOLLOW = 1
MODE_FOCUS = 2

class SolarSystemGL(QOpenGLWidget):

    back_to_menu = pyqtSignal()

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
        self.camera_pitch = -14
        self.camera_yaw = 0
        self.aspect = 800 / 600
        self.width = 800
        self.height = 600
        self.program_background = None
        self.background_vao = None
        self.pressed_keys = set()
        self.pressed_mouse_buttons = set()
        self.eye_position = np.array([0,20,80],dtype=np.float32)
        self.x_ndc = None
        self.y_ndc = None
        self.fix_navigation = False
        self.singleClick = False
        self.selectedPlanet = 1
        self.mode = MODE_NORMAL

    def toggleMode(self):
        if self.mode >= 2:
            self.mode = 0
        else:
            self.mode += 1

    def toggleSelection(self):
        if self.selectedPlanet is not None:
            if self.selectedPlanet >= 9:
                self.selectedPlanet = 0
            if self.selectedPlanet == 1:
                self.selectedPlanet +=2
            else:
                self.selectedPlanet += 1
        elif self.selectedPlanet is None:
            self.selectedPlanet = 1

    def detectSelection(self,x_ndc,y_ndc):

        inverse_projection = np.linalg.inv(self.projection_matrix)
        inverse_view = np.linalg.inv(self.view_matrix)
        inverse_map = inverse_view @ inverse_projection

        v1 = np.array([x_ndc,y_ndc,1,1],dtype=np.float32)

        v1_transformed = np.dot(inverse_map,v1)


        v1_3d = v1_transformed[:3] / v1_transformed[3]

        dir = v1_3d - self.eye_position
        dir = dir / np.linalg.norm(dir)
        origin = self.eye_position

        a = np.dot(dir,dir)

        planetHit = None
        distance = 0

        for p in self.planets:
            center = p.position
            L = origin - center

            b = 2 * np.dot(dir,L)
            c = np.dot(L,L) - math.pow(p.radius,2)

            discriminant = math.pow(b,2) - (4 * a * c)

            if discriminant >=0:
                t1 = (-b + math.sqrt(discriminant)) / (2 * a)
                t2 = (-b - math.sqrt(discriminant)) / (2 * a)

                if(t1 > 0 or t2 > 0):

                    t = min([t for t in [t1,t2] if t>0], default=None)

                    if t > distance:

                        planetHit = self.planets.index(p)
                        distance = t


        if planetHit is not None:
            self.selectedPlanet = planetHit
            print("Planet {} was selected".format(self.planets[planetHit].name))
            points = geometry.get_ray_vertices(origin,dir)
            print("p1 = {} {} {}".format(points[0],points[1],points[2]))
            print("p2 = {} {} {}".format(points[3],points[4],points[5]))
            self.ray_points = points
        else:
            self.selectedPlanet = None
            print("No planet selected")
            

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Escape:
            self.back_to_menu.emit()
        elif event.key() == Qt.Key_F:
            self.fix_navigation = True
        elif event.key() == Qt.Key_P:
            self.toggleMode()
        elif event.key() == Qt.Key_Right:
            self.toggleSelection()
        elif event.key() == Qt.Key_Left:
            self.toggleSelection()
        else:
            self.pressed_keys.add(event.key())

    def keyReleaseEvent(self, event):
        self.pressed_keys.discard(event.key())

    def mousePressEvent(self, event):
        self.pressed_mouse_buttons.add(event.button())
        x = event.x()
        y = event.y()

        self.x_ndc = geometry.get_ndc(x,self.width)
        self.y_ndc = geometry.get_ndc(self.height - y, self.height)
        x = event.x()
        y = event.y()


        if self.mode == MODE_FOCUS or self.mode == MODE_FOLLOW:
            self.detectSelection(self.x_ndc, self.y_ndc)

        self.x_ndc = None
        self.y_ndc = None


        #print(f"Mouse pressed at ({x_ndc}, {y_ndc})")

    def mouseMoveEvent(self, event):
        if Qt.LeftButton in self.pressed_mouse_buttons or Qt.RightButton in self.pressed_mouse_buttons:
            x = event.x()
            y = event.y()

            self.x_ndc = geometry.get_ndc(x,self.width)
            self.y_ndc = geometry.get_ndc(self.height - y, self.height)
            self.singleClick = False

    def mouseReleaseEvent(self, event):
        self.pressed_mouse_buttons.discard(event.button())

    def updateCamera(self):

        if self.fix_navigation:

            if self.mode != MODE_NORMAL:
                self.mode = MODE_NORMAL

            target = np.array([0,0,0])
            up = np.array([0,1,0])

            direction = target - self.eye_position
            self.camera_yaw = math.degrees(math.atan2(direction[0], -direction[2]))
            horizontal_dist = math.sqrt(direction[0]**2 + direction[2]**2)
            self.camera_pitch = math.degrees(math.atan2(direction[1], horizontal_dist))

            self.view_matrix = geometry.get_look_at_matrix(self.eye_position, target, up)
       
            # Update all programs' uniforms
        
            for p in self.planets:
                self.setup_program_uniforms(p.program, self.view_matrix, self.projection_matrix, self.model_matrix)
                self.setup_program_uniforms(self.program_ring, self.view_matrix, self.projection_matrix, self.model_matrix)
            
            self.fix_navigation = False
            self.update()  # Request a redraw
            return
        
        if self.mode == MODE_FOCUS and self.selectedPlanet is not None:
            target = self.planets[self.selectedPlanet].position
            up = np.array([0,1,0],dtype=np.float32)
            direction = None
            if self.planets[self.selectedPlanet].name != "Sun":
                direction = target.copy() / np.linalg.norm(target)
            else:
                direction = np.array([0,0,1],dtype=np.float32)
            camera = target + direction * 18  + up * 5

            self.view_matrix = geometry.get_look_at_matrix(camera, target, up)
       
            # Update all programs' uniforms
        
            for p in self.planets:
                self.setup_program_uniforms(p.program, self.view_matrix, self.projection_matrix, self.model_matrix)
                self.setup_program_uniforms(self.program_ring, self.view_matrix, self.projection_matrix, self.model_matrix)
            
            self.update()  # Request a redraw
            return
        
        if self.mode == MODE_FOLLOW and self.selectedPlanet is not None:
            target = self.planets[self.selectedPlanet].position
            up = np.array([0,1,0],dtype=np.float32)

            self.view_matrix = geometry.get_look_at_matrix(self.eye_position, target, up)
       
            # Update all programs' uniforms
        
            for p in self.planets:
                self.setup_program_uniforms(p.program, self.view_matrix, self.projection_matrix, self.model_matrix)
                self.setup_program_uniforms(self.program_ring, self.view_matrix, self.projection_matrix, self.model_matrix)
            
            self.update()  # Request a redraw
            return

        # Check pressed keys and update camera
        if Qt.Key_W in self.pressed_keys:
            self.camera_pitch += 0.5
        if Qt.Key_S in self.pressed_keys:
            self.camera_pitch -= 0.5
        if Qt.Key_A in self.pressed_keys:
            self.camera_yaw -= 0.5
        if Qt.Key_D in self.pressed_keys:
            self.camera_yaw += 0.5

        # Clamp pitch
        self.camera_pitch = max(-89, min(self.camera_pitch, 89))

        if(self.camera_yaw > 360):
            self.camera_yaw -= 360
        if(self.camera_yaw < -360):
            self.camera_yaw += 360
        
        up = np.array([0,1,0])

        forward = geometry.calulate_forward_vector(self.camera_pitch,self.camera_yaw)

        if Qt.LeftButton in self.pressed_mouse_buttons:
        # Move camera forward

            self.camera_pitch += geometry.calculate_turn_amout(self.y_ndc)
            self.camera_yaw += geometry.calculate_turn_amout(self.x_ndc)
                
            # Clamp pitch
            self.camera_pitch = max(-89, min(self.camera_pitch, 89))
            forward = geometry.calulate_forward_vector(self.camera_pitch,self.camera_yaw)
            self.eye_position += (forward * 0.5)

            

        if Qt.RightButton in self.pressed_mouse_buttons:
            self.camera_pitch += geometry.calculate_turn_amout(self.y_ndc)
            self.camera_yaw += geometry.calculate_turn_amout(self.x_ndc)
            
            # Clamp pitch
            self.camera_pitch = max(-89, min(self.camera_pitch, 89))
            forward = geometry.calulate_forward_vector(self.camera_pitch,self.camera_yaw)
            self.eye_position -= (forward * 0.4)

        target = self.eye_position + forward

        self.view_matrix = geometry.get_look_at_matrix(self.eye_position,target,up)
       
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

    def setup_buffer(self,program,data,index_data,line=False):

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

        if(line == True):
            self.ray_vbo = buffer

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

            self.draw_ring(object.orbit_radius)

    def draw_ring(self,radius):
        glUseProgram(self.program_ring)
        glBindVertexArray(self.ring_vao)
        scaling_matrix = np.identity(4, dtype=np.float32)
        scaling_matrix[0, 0] = radius
        scaling_matrix[1, 1] = 1.0     
        scaling_matrix[2, 2] = radius
            
        model_matrix = np.dot(self.model_matrix,scaling_matrix)

        self.setup_program_uniforms(self.program_ring,self.view_matrix,self.projection_matrix,model_matrix)
        ring_color = np.array([1.0, 1.0, 1.0], dtype=np.float32)
        ring_color_loc = glGetUniformLocation(self.program_ring, "ringColor")
        glUniform3fv(ring_color_loc, 1, ring_color) 
            
        glDrawArrays(GL_LINE_STRIP, 0, 101)
        glBindVertexArray(0)

    def draw_ray(self):
        glUseProgram(self.program_ring)
        glBindVertexArray(self.ray_vao)
        model_matrix = np.identity(4, dtype=np.float32)
        self.setup_program_uniforms(self.program_ring,self.view_matrix,self.projection_matrix,model_matrix)
        ring_color = np.array([1.0, 1.0, 1.0], dtype=np.float32)
        ring_color_loc = glGetUniformLocation(self.program_ring, "ringColor")
        glUniform3fv(ring_color_loc, 1, ring_color) 

        glBindBuffer(GL_ARRAY_BUFFER,self.ray_vbo)
        glBufferSubData(GL_ARRAY_BUFFER, 0, self.ray_points.nbytes, self.ray_points)
        
        glLineWidth(2.0)
        glDrawArrays(GL_LINES,0,2)
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

        line_placeholder = np.array([0,0,0,0,0,0], dtype=np.float32)
        self.ray_vao = self.setup_buffer(self.program_ring, line_placeholder, None,True)


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

        target = np.array([0,0,0])
        eye = self.eye_position
        up = np.array([0,1,0])

        view_matrix = geometry.get_look_at_matrix(eye,target,up)
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
                orbit_speed=0.8,
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
                orbit_speed=1.0,
                spin_speed=2)
        mercury.vao = vao_planet
        mercury.orbit_angle = math.radians(20)
        mercury.program = program

        venus = Planet("Venus", radius=1.2,
                color_left=np.array([0.95, 0.85, 0.55]),
                color_right=np.array([0.9, 0.75, 0.35]),
                orbit_radius=25.6,
                orbit_speed=1,
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
        self.width = w
        self.height = h
        projection_matrix = geometry.get_projection_matrix(math.radians(45), self.aspect, 0.1, 300.0)
        self.projection_matrix = projection_matrix
        

    def paintGL(self):

        self.updateCamera()

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        current_time = time.time()
        delta_time = current_time - self.last_time
        self.last_time = current_time
        
        #Clear the screen
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.paint_background()

        for p in self.planets:
            self.draw_planet(p,delta_time)

        ##if self.selectedPlanet is not None and self.ray_points is not None:
        ##    self.draw_ray()

