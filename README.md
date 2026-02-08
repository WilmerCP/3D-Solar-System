# 🌌 Solar System 3D Simulation

## Project Overview
This project is a **3D Solar System simulation** developed in **Python** using **OpenGL with the programmable pipeline**.  
The graphical user interface is implemented with **PyQt**, and rendering is performed inside a `QOpenGLWidget`.

---

## 🚀 Features
- ☀️ Sun positioned at the center of world space
- 🪐 All planets orbiting around the Sun
- 🌙 Moon orbiting around the Earth
- 💡 Lambert shading for realistic light diffusion from the Sun
- 🔵 Orbit rings rendered for every planet
- 🌌 Space background texture
- 🎮 Camera controls:
  - Pitch and Yaw movement with `W` `A` `S` `D` keys
  - Zoom in and out using left and right click
- 👁️ Change between 3 visualization modes with `P` key:
  - Explore mode: move freely around the scene
  - Focus mode: up-close visualization of a planet
  - Follow mode: the camera follows the movement of the planet

---

## 🧱 Classes

### Planet
Represents a general planet and contains all parameters required for rendering.  
Uses two colors passed to the fragment shader to generate a gradient effect.

#### Attributes
- Color 1
- Color 2
- Radius
- Orbit radius
- Orbit speed
- Spin speed
- Vertex Array Object (VAO)
- Shader Program
- Parent object
- Position

#### Methods
- **update(dt)**
  - Receives the elapsed time between frames (milliseconds)
  - Updates orbit angle, spin angle, and world position

- **get_model_matrix()**
  - Computes the model matrix based on radius, orbit radius, angles, and position
  - Sent to the vertex shader

- **update_uniforms()**
  - Uploads color values to shader uniforms
  - Shared shader program is reused with different parameters

---

### TexturedPlanet
Child class of `Planet` that renders planets using textures instead of color grading.

#### Unique Attributes
- Texture unit
- Texture ID

#### Overridden Methods
- **update_uniforms()**
  - Activates the correct texture unit
  - Updates shader uniforms for texture rendering

---

### Sun
Child class of `Planet` that includes advanced procedural shading effects.

#### Effects Implemented
- Limb Darkening
- Rim Glow
- Procedural Noise
- Smoothstep Edge Fading

#### Unique Attributes
- Time

#### Overridden Methods
- **update_uniforms()**
  - Sends elapsed time to fragment shader for procedural calculations

---

## 🔄 Program Flow

### Initialization (`initializeGL`)
- Compile all shader programs
- Create scene objects
- Generate Vertex Array Objects (VAO), Vertex Buffers, and Element Buffers
- Store planets in an array
- Load textures
- Create View and Projection matrices
- Upload matrices to shader programs

### Rendering Loop
Each frame performs:

1. Render space background using:
   - `GL_TRIANGLE_FAN` (2 triangles forming a quad)
2. Iterate through planet array:
   - Render planets using `GL_TRIANGLE_STRIP`
   - Render orbit rings using `GL_LINE_STRIP`

---

## 🟠 Sphere Rendering
Spheres are constructed using `GL_TRIANGLE_STRIP` for efficient rendering and reduced vertex duplication.

---

## 💡 Lambert Lighting
Lambert's cosine law is used to simulate diffuse lighting from the Sun.

$Light Intensity = cos(angle)$


- For a sphere, vertex coordinates equal the surface normals
- Normals are transformed into world space using:

$transpose(inverse(ModelMatrix)) * normal$

- Result is passed to the fragment shader for lighting calculations

---

## 🧮 MVP Matrix

### Projection Matrix
- Perspective projection
- Resolution: 800 × 600
- Near plane: 0.1
- Far plane: 200
- Field of view: 45°

Defines the viewing frustum and maps points into normalized device coordinates.

### View Matrix
- Translation from origin
- Pitch rotation for elevated camera angle
- Updated only when user input changes

### Model Matrix
- Unique for each object
- Updated every frame based on transformations

---

## 🌍 Earth Texture
The Earth uses an **Equirectangular Projection Texture** obtained from:

NASA / Goddard Space Flight Center Scientific Visualization Studio  
https://svs.gsfc.nasa.gov/3615/

---

## 🖥️ Technologies Used
- Python
- OpenGL (Programmable Pipeline)
- PyQt
- GLSL Shaders
