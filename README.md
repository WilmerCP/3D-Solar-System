# 🌌 Solar System 3D Simulation

## Project Overview
This project is a **3D Solar System simulation** developed in **Python** using **OpenGL with the programmable pipeline**.  
The graphical user interface is implemented with **PyQt**, and rendering is performed inside a `QOpenGLWidget`.


<img src="https://github.com/WilmerCP/3D-Solar-System/blob/master/screenshots/Menu.png" width="500">

---

## 🚀 Features
- ☀️ Sun positioned at the center of world space
- 🪐 All planets orbiting around the Sun
- 🌙 Moon orbiting around the Earth
- 🪐 Saturn's rings with shadow projection
- 💡 Lambert shading for realistic light diffusion from the Sun
- 🔵 Orbit rings rendered for every planet
- 🌌 Space background texture
- 🎮 Scene exploration with flexible camera controls

---

<img src="https://github.com/WilmerCP/3D-Solar-System/blob/master/screenshots/SolarSystem.png" width="500">

## 👁️ Modes

- Change between 3 visualization modes with `P` key:
- Select a planet anytime by clicking on it
- Click anywhere else to discard planet selection

### 🧭 Explore mode: 
- Move freely around the scene
  - Pitch and Yaw movement with `W` `A` `S` `D` keys
  - Zoom in and out using left and right click or mouse wheel
  - Fix camera orientation with `F` key

### 🎥 Follow mode: 
- The camera follows the movement of the planet
  - Zoom in and out using mouse wheel

### 🔍 Focus mode: 
- Up-close visualization of a planet
  - Pivot around the planet with `W` `A` `S` `D` keys
  - Zoom in and out using mouse wheel


<img src="https://github.com/WilmerCP/3D-Solar-System/blob/master/screenshots/Controls.png" width="500">

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
   - Render saturn's rings using `GL_TRIANGLE_STRIP`
3. Write text on the screen with QPainter()

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
## 🎯 Ray Casting

Ray casting system was implemented to select planets directly from the 3D scene whenever Focus mode or Follow mode are active.

When the user clicks on the screen, a ray is generated from the camera position through the mouse coordinates into world space. The screen coordinates are converted into Normalized Device Coordinates and then transformed using the inverse Projection and View matrices to obtain the ray direction.

Each planet is represented with a bounding sphere using its world position and radius. A ray–sphere intersection test is performed against all planets, and the closest intersected object becomes the selected element.

---

## ☀️ Sun with Procedural Shading effects
- Limb Darkening
- Rim Glow
- Procedural Noise
- Smoothstep Edge Fading

# 🌓 Saturn’s Ring Shadow Projection

The shader performs a ray–sphere intersection test between each ring fragment and the planet’s bounding sphere. 

If the fragment is behind the planet relative to the Sun, a smooth shadow is applied using the penetration depth and the discriminant of the intersection. 

This creates a soft, physically accurate shadow on the rings, enhancing visual realism.

<img src="https://github.com/WilmerCP/3D-Solar-System/blob/master/screenshots/FocusMode.png" width="500">

## 🧮 MVP Matrix

### Projection Matrix
- Perspective projection
- Resolution: 800 × 600
- Near plane: 0.1
- Far plane: 800
- Field of view: 45°

Defines the viewing frustum and maps points into normalized device coordinates.

### View Matrix
- Look-at matrix is used for flexibility between view modes
- Constructed using camera position, target and up vectors

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
