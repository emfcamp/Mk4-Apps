"""3d rotating polyhedra. 2016 badge competition winner, ported for 2018!"""

___name___         = "3D Spin"
___license___      = "MIT"
___categories___   = ["Demo"]
___dependencies___ = ["app", "ugfx_helper", "random", "sleep", "buttons"]

import ugfx
from tilda import Buttons
import math
from uos import listdir
import time
# from imu import IMU
import gc
# import pyb
import app

app_path = './3dspin'

from math import sqrt

class Vector3D:
	def __init__(self, x=0.0, y=0.0, z=0.0):
		self.x = x
		self.y = y
		self.z = z

	def magnitude(self):
		return sqrt(self.x*self.x+self.y*self.y+self.z*self.z)

	def __sub__(self, v):
		return Vector3D(self.x-v.x, self.y-v.y, self.z-v.z)

	def normalize(self):
		mag = self.magnitude()
		if (mag > 0.0):
			self.x /= mag
			self.y /= mag
			self.z /= mag
		else:
			raise Exception('*** Vector: error, normalizing zero vector! ***')

	def cross(self, v): #cross product
		return Vector3D(self.y*v.z-self.z*v.y, self.z*v.x-self.x*v.z, self.x*v.y-self.y*v.x)


#The layout of the matrix (row- or column-major) matters only when the user reads from or writes to the matrix (indexing). For example in the multiplication function we know that the first components of the Matrix-vectors need to be multiplied by the vector. The memory-layout is not important
class Matrix:
	''' Column-major order '''

	def __init__(self, createidentity=True):# (2,2) creates a 2*2 Matrix
		# if rows < 2 or cols < 2:
		# 	raise Exception('*** Matrix: error, getitem((row, col)), row, col problem! ***')
		self.rows = 4
		self.cols = 4
		self.m = [[0.0]*self.rows for x in range(self.cols)]

		#If quadratic matrix then create identity one
		if createidentity:
			for i in range(self.rows):
				self.m[i][i] = 1.0

	def mul(self, right):
		if isinstance(right, Matrix):
			r = Matrix(False)
			for i in range(self.rows):
				for j in range(right.cols):
					for k in range(self.cols):
						r.m[i][j] += self.m[i][k]*right.m[k][j]
			return r
		elif isinstance(right, Vector3D): #Translation: the last column of the matrix. Remains unchanged due to the the fourth coord of the vector (1).
#			if self.cols == 4:
			r = Vector3D()
			addx = addy = addz = 0.0
			if self.rows == self.cols == 4:
				addx = self.m[0][3]
				addy = self.m[1][3]
				addz = self.m[2][3]
			r.x = self.m[0][0]*right.x+self.m[0][1]*right.y+self.m[0][2]*right.z+addx
			r.y = self.m[1][0]*right.x+self.m[1][1]*right.y+self.m[1][2]*right.z+addy
			r.z = self.m[2][0]*right.x+self.m[2][1]*right.y+self.m[2][2]*right.z+addz

			#In 3D game programming we use homogenous coordinates instead of cartesian ones in case of Vectors in order to be able to use them with a 4*4 Matrix. The 4th coord (w) is not included in the Vector-class but gets computed on the fly
			w = self.m[3][0]*right.x+self.m[3][1]*right.y+self.m[3][2]*right.z+self.m[3][3]
			if (w != 1 and w != 0):
				r.x = r.x/w;
				r.y = r.y/w;
				r.z = r.z/w;
			return r
		else:
			raise Exception('*** Matrix: error, matrix multiply with not matrix, vector or int or float! ***')

def loadObject(filename):
    print(filename)
    if (".obj" in filename):
        loadObj(filename)
    if (".dat" in filename):
        loadDat(filename)

def loadDat(filename):
    global obj_vertices
    global obj_faces
    obj_vertices = []
    obj_faces = []
    f = open(app_path + "/" + filename)
    for line in f:
        if line[:2] == "v ":
            parts = line.split(" ")
            obj_vertices.append(
                Vector3D(
                    float(parts[1]),
                    float(parts[2]),
                    float(parts[3])
                )
            )
            gc.collect()
        elif line[:2] == "f ":
            parts = line.split(" ")
            face = []
            for part in parts[1:]:
                face.append(int(part.split("/",1)[0])-1)
            obj_faces.append(face)
            gc.collect()
    f.close()

def loadObj(filename):
    global obj_vertices
    global obj_faces
    obj_vertices = []
    obj_faces = []
    f = open(app_path + "/" + filename)
    for line in f:
        if line[:2] == "v ":
            parts = line.split(" ")
            obj_vertices.append(
                Vector3D(
                    float(parts[1]),
                    float(parts[2]),
                    float(parts[3])
                )
            )
            gc.collect()
        elif line[:2] == "f ":
            parts = line.split(" ")
            face = []
            for part in parts[1:]:
                face.append(int(part.split("/",1)[0])-1)
            obj_faces.append(face)
            gc.collect()
    f.close()

def toScreenCoords(pv):
	px = int((pv.x+1)*0.5*240)
	py = int((1-(pv.y+1)*0.5)*320)
	return [px, py]

def createCameraMatrix(x,y,z):
    camera_transform = Matrix()
    camera_transform.m[0][3] = x
    camera_transform.m[1][3] = y
    camera_transform.m[2][3] = z
    return camera_transform

def createProjectionMatrix(horizontal_fov, zfar, znear):
    s = 1/(math.tan(math.radians(horizontal_fov/2)))
    proj = Matrix()
    proj.m[0][0] = s * (320/240) # inverse aspect ratio
    proj.m[1][1] = s
    proj.m[2][2] = -zfar/(zfar-znear)
    proj.m[3][2] = -1.0
    proj.m[2][3] = -(zfar*znear)/(zfar-znear)
    return proj

def createRotationMatrix(x_rotation, y_rotation, z_rotation):
    rot_x = Matrix()
    rot_x.m[1][1] = rot_x.m[2][2] = math.cos(x_rotation)
    rot_x.m[2][1] = math.sin(x_rotation)
    rot_x.m[1][2] = -rot_x.m[2][1]

    rot_y = Matrix()
    rot_y.m[0][0] = rot_y.m[2][2] = math.cos(y_rotation)
    rot_y.m[0][2] = math.sin(y_rotation)
    rot_y.m[2][0] = -rot_y.m[0][2]

    rot_z = Matrix()
    rot_z.m[0][0] = rot_z.m[1][1] = math.cos(z_rotation)
    rot_z.m[1][0] = math.sin(z_rotation)
    rot_z.m[0][1] = -rot_z.m[1][0]

    return rot_z.mul(rot_x).mul(rot_y)

def normal(face, vertices, normalize = True):
    # Work out the face normal for lighting
    normal = (vertices[face[1]]-vertices[face[0]]).cross(vertices[face[2]]-vertices[face[0]])
    if normalize == True:
        normal.normalize()
    return normal

def clear_screen():
    # Selectively clear the screen by re-rendering the previous frame in black
    global last_polygons
    global last_mode
    for poly in last_polygons:
        if last_mode == FLAT:
            ugfx.fill_polygon(0,0, poly, ugfx.BLACK)
        ugfx.polygon(0,0, poly, ugfx.BLACK)

def render(mode, rotation):
    # Rotate all the vertices in one go
    vertices = [rotation.mul(vertex) for vertex in obj_vertices]
    # Calculate normal for each face (for lighting)
    if mode == FLAT:
        face_normal_zs = [normal(face, vertices).z for face in obj_faces]
    # Project (with camera) all the vertices in one go as well
    vertices = [camera_projection.mul(vertex) for vertex in vertices]
    # Calculate projected normals for each face
    if mode != WIREFRAME:
        proj_normal_zs = [normal(face, vertices, False).z for face in obj_faces]
    # Convert to screen coordinates all at once
    # We could do this faster by only converting vertices that are
    # in faces that will be need rendered, but it's likely that test
    # would take longer.
    vertices = [toScreenCoords(v) for v in vertices]
    # Render the faces to the screen
    vsync()
    clear_screen()

    global last_polygons
    global last_mode
    last_polygons = []
    last_mode = mode

    for index in range(len(obj_faces)):
        # Only render things facing towards us (unless we're in wireframe mode)
        if (mode == WIREFRAME) or (proj_normal_zs[index] > 0):
            # Convert polygon
            poly = [vertices[v] for v in obj_faces[index]]
            # Calculate colour and render
            ugcol = ugfx.WHITE
            if mode == FLAT:
                # Simple lighting calculation
                colour5 = int(face_normal_zs[index] * 31)
                colour6 = int(face_normal_zs[index] * 63)
                # Create a 5-6-5 grey
                ugcol = (colour5 << 11) | (colour6 << 5) | colour5
                # Render polygon
                ugfx.fill_polygon(0,0, poly, ugcol)
            # Always draw the wireframe in the same colour to fill gaps left by the
            # fill_polygon method
            ugfx.polygon(0,0, poly, ugcol)
            last_polygons.append(poly)

def vsync():
	None
    # while(tear.value() == 0):
    #     pass
    # while(tear.value()):
    #     pass

def calculateRotation(smoothing, accelerometer):
    # Keep a list of recent rotations to smooth things out
    global x_rotation
    global z_rotation
    # First, pop off the oldest rotation
    # if len(x_rotations) >= smoothing:
    #     x_rotations = x_rotations[1:]
    # if len(z_rotations) >= smoothing:
    #     z_rotations = z_rotations[1:]
    # Now append a new rotation
    pi_2 = math.pi / 2
    #x_rotations.append(-accelerometer['z'] * pi_2)
    #z_rotations.append(accelerometer['x'] * pi_2)
    # Calculate rotation matrix
    return createRotationMatrix(
        # this averaging isn't correct in the first <smoothing> frames, but who cares
        math.radians(x_rotation),
        math.radians(y_rotation),
        math.radians(z_rotation)
    )
print("Hello 3DSpin")

# Initialise hardware
ugfx.init()
ugfx.clear(ugfx.BLACK)
# imu=IMU()
# buttons.init()

# Enable tear detection for vsync
#  ugfx.enable_tear()
# tear = pyb.Pin("TEAR", pyb.Pin.IN)
#ugfx.set_tear_line(1)

print("Graphics initalised")

# Set up static rendering matrices
camera_transform = createCameraMatrix(0, 0, -5.0)
proj = createProjectionMatrix(45.0, 100.0, 0.1)
camera_projection = proj.mul(camera_transform)

print("Camera initalised")

# Get the list of available objects, and load the first one
obj_vertices = []
obj_faces = []
print("available objects: {}", listdir(app_path))
objects = [x for x in listdir(app_path) if (((".obj" in x) | (".dat" in x)) & (x[0] != "."))]
selected = 0
loadObject(objects[selected])

print("loaded object {}", objects[selected])

# Set up rotation tracking arrays
x_rotation = 0
z_rotation = 0
y_rotation = 0
# Smooth rotations over 5 frames
smoothing = 5

# Rendering modes
BACKFACECULL = 1
FLAT = 2
WIREFRAME = 3
# Start with backface culling mode
mode = BACKFACECULL

last_polygons = []
last_mode = WIREFRAME

# Main loop
run = True
while run:
    gc.collect()
    # Render the scene
    render(
        mode,
        calculateRotation(smoothing, None)
    )
    # Button presses
    y_rotation += 5
    x_rotation += 3
    z_rotation += 1
    if Buttons.is_pressed(Buttons.JOY_Left):
        y_rotation -= 5
    if Buttons.is_pressed(Buttons.JOY_Right):
        y_rotation += 5
    if Buttons.is_pressed(Buttons.JOY_Center):
        y_rotation = 0
    if Buttons.is_pressed(Buttons.BTN_B):
        selected += 1
        if selected >= len(objects):
            selected = 0
        loadObject(objects[selected])
        time.sleep_ms(500) # Wait a while to avoid skipping ahead if the user still has the button down
    if Buttons.is_pressed(Buttons.BTN_A):
        mode += 1
        if mode > 3:
            mode = 1
        time.sleep_ms(500) # Wait a while to avoid skipping ahead if the user still has the button down
    if Buttons.is_pressed(Buttons.BTN_Menu):
        run = False
        app.restart_to_default()
