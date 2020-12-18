#!/usr/bin/env python3

#I used the following sites for help and more information:
#https://www.cs.cmu.edu/afs/cs/academic/class/15462-s09/www/lec/06/lec06.pdf
#https://www.tutorialspoint.com/computer_graphics/3d_computer_graphics.htm
#http://www.cs.sjtu.edu.cn/~shengbin/course/cg/lecture%20notes/CG10_(ch10)%203D%20Viewing_new.pdf
#https://www.geeksforgeeks.org/multiplication-two-matrices-single-line-using-numpy-python/
#https://www.cs.drexel.edu/~david/Classes/CS430/Lectures/L-18_CullingZbufRays.pdf
#https://www.cs.drexel.edu/~david/Classes/CS430/Lectures/L-15_Surfaces.pdf


import sys
import math
from math import sin, cos, radians
List = []
vertices = []
face = []
new_vertices = []
polygons = []
x1_world = 0.0
y1_world = 0.0
x2_world = 0.0
y2_world = 0.0
boundary = 0
poly = []
transformed_list = []
clipped_list = []
pbm_file = []
postscript_file = "bound-lo-sphere.smf"
scaling_factor = float(1.0)
rotation = int(0)
x_translation = int(0)
y_translation = int(0)
x_lower = int(0)
y_lower = int(0)
x_upper = int(499)
y_upper = int(499)
x_intersect = 0
y_intersect = 0
viewport_x_lower = 0
viewport_y_lower = 0
viewport_x_upper = 500
viewport_y_upper = 500

x_prp = 0.0
y_prp = 0.0
z_prp = 1.0
x_vrp = 0.0
y_vrp = 0.0
z_vrp = 0.0
x_vpn = 0.0
y_vpn = 0.0
z_vpn = -1.0
x_vup = 0.0
y_vup = 1.0
z_vup = 0.0
u_min_vrc = -0.7
v_min_vrc = -0.7
u_max_vrc = 0.7
v_max_vrc = 0.7
parallel = False
culling = False
front = 0.6
back = -0.6

#python code to read file and output lines in terminal
def read_psfile(filename):
	with open(filename, 'r') as Lines:
		for line in Lines:
			line_num = line.split()
			List.append(line_num)

	#create list of vertices and faces
	for a in range(len(List)):
		if(List[a][0] == 'v'):
			vert = (List[a][1], List[a][2], List[a][3], 1.0)
			vertices.append(vert)

		elif(List[a][0] == 'f'):
			f = (int(List[a][1])-1, int(List[a][2])-1, int(List[a][3])-1)
			face.append(f)	

def translate_m(t_vrp):
	t_vrp[0][0] = 1
	t_vrp[0][1] = 0
	t_vrp[0][2] = 0
	t_vrp[0][3] = -x_vrp

	t_vrp[1][0] = 0
	t_vrp[1][1] = 1
	t_vrp[1][2] = 0
	t_vrp[1][3] = -y_vrp

	t_vrp[2][0] = 0
	t_vrp[2][1] = 0
	t_vrp[2][2] = 1
	t_vrp[2][3] = -z_vrp

	t_vrp[3][0] = 0
	t_vrp[3][1] = 0
	t_vrp[3][2] = 0
	t_vrp[3][3] = 1

	return t_vrp

def shear_m(shear):
	shear[0][0] = 1
	shear[0][1] = 0
	shear[0][2] = ((.5 * (u_max_vrc + u_min_vrc)) - x_prp)/z_prp
	shear[0][3] = 0

	shear[1][0] = 0
	shear[1][1] = 1
	shear[1][2] = ((.5 * (v_max_vrc + v_min_vrc)) - y_prp)/z_prp
	shear[1][3] = 0

	shear[2][0] = 0
	shear[2][1] = 0
	shear[2][2] = 1
	shear[2][3] = 0

	shear[3][0] = 0
	shear[3][1] = 0
	shear[3][2] = 0
	shear[3][3] = 1

	return shear

def rotation_m(rotation):
	#Rz = (VPN) / |VPN|
	length_VPN = float(math.sqrt(x_vpn*x_vpn + y_vpn*y_vpn + z_vpn*z_vpn))

	r1z = x_vpn/length_VPN
	r2z = y_vpn/length_VPN
	r3z = z_vpn/length_VPN

	#Rx = (VUP x Rz) / |(VUP x Rz)|
	Rx_results = cross_product(x_vup, y_vup, z_vup, r1z, r2z, r3z)
	length_results = float(math.sqrt(Rx_results[0]*Rx_results[0] + Rx_results[1]*Rx_results[1] + Rx_results[2]*Rx_results[2]))

	r1x = Rx_results[0]/length_results
	r2x = Rx_results[1]/length_results
	r3x = Rx_results[2]/length_results

	#Ry = (Rz x Rx)
	Ry_results = cross_product(r1z, r2z, r3z, r1x, r2x, r3x)

	r1y = Ry_results[0]
	r2y = Ry_results[1]
	r3y = Ry_results[2]

	rotation[0][0] = r1x
	rotation[0][1] = r2x
	rotation[0][2] = r3x
	rotation[0][3] = 0

	rotation[1][0] = r1y
	rotation[1][1] = r2y
	rotation[1][2] = r3y
	rotation[1][3] = 0

	rotation[2][0] = r1z
	rotation[2][1] = r2z
	rotation[2][2] = r3z
	rotation[2][3] = 0

	rotation[3][0] = 0
	rotation[3][1] = 0
	rotation[3][2] = 0
	rotation[3][3] = 1

	return rotation

def t_par_m(t_par):
	t_par[0][0] = 1
	t_par[0][1] = 0
	t_par[0][2] = 0
	t_par[0][3] = -(u_max_vrc + u_min_vrc)/2

	t_par[1][0] = 0
	t_par[1][1] = 1
	t_par[1][2] = 0
	t_par[1][3] = -(v_max_vrc + v_min_vrc)/2

	t_par[2][0] = 0
	t_par[2][1] = 0
	t_par[2][2] = 1
	t_par[2][3] = -front

	t_par[3][0] = 0
	t_par[3][1] = 0
	t_par[3][2] = 0
	t_par[3][3] = 1

	return t_par

def s_par_m(s_par):
	s_par[0][0] = 2/(u_max_vrc - u_min_vrc)
	s_par[0][1] = 0
	s_par[0][2] = 0
	s_par[0][3] = 0

	s_par[1][0] = 0
	s_par[1][1] = 2/(v_max_vrc - v_min_vrc)
	s_par[1][2] = 0
	s_par[1][3] = 0

	s_par[2][0] = 0
	s_par[2][1] = 0
	s_par[2][2] = 1/(front - back)
	s_par[2][3] = 0

	s_par[3][0] = 0
	s_par[3][1] = 0
	s_par[3][2] = 0
	s_par[3][3] = 1

	return s_par

def t_prp_m(t_prp):
	t_prp[0][0] = 1
	t_prp[0][1] = 0
	t_prp[0][2] = 0
	t_prp[0][3] = -x_prp

	t_prp[1][0] = 0
	t_prp[1][1] = 1
	t_prp[1][2] = 0
	t_prp[1][3] = -y_prp

	t_prp[2][0] = 0
	t_prp[2][1] = 0
	t_prp[2][2] = 1
	t_prp[2][3] = -z_prp

	t_prp[3][0] = 0
	t_prp[3][1] = 0
	t_prp[3][2] = 0
	t_prp[3][3] = 1

	return t_prp

def s_per_m(s_per):
	s_per[0][0] = (2 * z_prp)/((u_max_vrc - u_min_vrc) * (z_prp - back))
	s_per[0][1] = 0
	s_per[0][2] = 0
	s_per[0][3] = 0

	s_per[1][0] = 0
	s_per[1][1] = (2 * z_prp)/((v_max_vrc - v_min_vrc) * (z_prp - back))
	s_per[1][2] = 0
	s_per[1][3] = 0

	s_per[2][0] = 0
	s_per[2][1] = 0
	s_per[2][2] = 1/(z_prp - back)
	s_per[2][3] = 0

	s_per[3][0] = 0
	s_per[3][1] = 0
	s_per[3][2] = 0
	s_per[3][3] = 1

	return s_per

def cross_product(x1, y1, z1, x2, y2, z2):
	results_list = []
	results_list.append(float((y1 * z2) - (z1 * y2)))
	results_list.append(float((z1 * x2) - (x1 * z2)))
	results_list.append(float((x1 * y2) - (y1 * x2)))

	return results_list

def multiply(one, two):
	one_row = len(one)
	one_col = len(one[0])
	two_col = len(two[0])

	multiplied_matrix = [[0 for i in range(two_col)] for j in range(one_row)] 

	for a in range(one_row):
		for b in range(two_col):
			for c in range(one_col):
				multiplied_matrix[a][b] = float(multiplied_matrix[a][b]) + (float(one[a][c]) * (float(two[c][b])))
	
	return multiplied_matrix

def transformations():
	#translation matrix
	t_vrp = [[0 for i in range(4)] for j in range(4)]
	t_vrp = translate_m(t_vrp)

	#rotation matrix
	rotation = [[0 for i in range(4)] for j in range(4)]
	rotation = rotation_m(rotation)

	#shear matrix 
	shear = [[0 for i in range(4)] for j in range(4)]
	shear = shear_m(shear)

	if(parallel):
		t_par = [[0 for i in range(4)] for j in range(4)]
		t_par = t_par_m(t_par)

		s_par = [[0 for i in range(4)] for j in range(4)]
		s_par = s_par_m(s_par)
		#print(s_par)

		#N_par = (S_par • (T_par • (SH_par • (R • T(-VRP)))))
		first_mult = multiply(rotation, t_vrp)
		second_mult = multiply(shear, first_mult)
		
		third_mult = multiply(t_par, second_mult)
		n_par = multiply(s_par, third_mult)
		

		for a in range(len(vertices)):
			current_vertice = [[0 for i in range(1)] for j in range(4)]

			current_vertice[0][0] = float(vertices[a][0])
			current_vertice[1][0] = float(vertices[a][1])
			current_vertice[2][0] = float(vertices[a][2])
			current_vertice[3][0] = float(vertices[a][3])
			#print(current_vertice)
			fourth_mult = multiply(n_par, current_vertice)

			row = []
			row.append(fourth_mult[0][0])
			row.append(fourth_mult[1][0])

			if(culling):
				row.append(fourth_mult[2][0])

			vertices[a] = row
	
	else:	#perspective

		t_prp = [[0 for i in range(4)] for j in range(4)]
		t_prp = t_prp_m(t_prp)

		s_per = [[0 for i in range(4)] for j in range(4)]
		s_per = s_per_m(s_per)

		#Nper = (Sper • (SHpar • (T(-PRP) • (R • T(-VRP)))))
		first_mult = multiply(rotation, t_vrp)
		second_mult = multiply(t_prp, first_mult)
		third_mult = multiply(shear, second_mult)
		n_per = multiply(s_per, third_mult)
		#print(n_per)
		#print(vertices)
		for a in range(len(vertices)):
			current_vertice = [[0 for i in range(1)] for j in range(4)]
			
			current_vertice[0][0] = vertices[a][0]
			current_vertice[1][0] = vertices[a][1]
			current_vertice[2][0] = vertices[a][2]
			current_vertice[3][0] = vertices[a][3]
			#print(current_vertice)
			fourth_mult = multiply(n_per, current_vertice)
			
			#print(fourth_mult)
			row = []
			row.append(fourth_mult[0][0])
			row.append(fourth_mult[1][0])
			row.append(fourth_mult[2][0])
			vertices[a] = row

	#print(vertices)

def backface_culling():
	#print(vertices)
	a = 0
	while a < (len(face)):
		global poly
		poly = []
		face_1 = int(face[a][0])
		face_2 = int(face[a][1])
		face_3 = int(face[a][2])

		row1 = vertices[face_1]
		row2 = vertices[face_2]
		row3 = vertices[face_3]

		x0 = row1[0]
		x1 = row2[0]
		x2 = row3[0]
		y0 = row1[1]
		y1 = row2[1]
		y2 = row3[1]
		z0 = row1[2]
		z1 = row2[2]
		z2 = row3[2]

		normal = cross_product(x1-x0, y1-y0, z1-z0, x2-x0, y2-y0, z2-z0)
		#print(normal)
		if(normal[2] >= 0):
			poly.append(row1)
			poly.append(row2)
			poly.append(row3)
			polygons.append(poly)
		a = a + 1
	#print(polygons)

def create_row(x,y):
	row = []
	row.append(x)
	row.append(y)
	return row

def projection():
	if(culling):
		if(parallel):
			for a in range(len(polygons)):
				for b in range(len(polygons[a])):
					x = polygons[a][b][0]
					y = polygons[a][b][1]
					row = create_row(x,y)

					polygons[a][b] = row

		else:
			for a in range(len(polygons)):
				for b in range(len(polygons[a])):
					x = polygons[a][b][0]
					y = polygons[a][b][1]
					z = polygons[a][b][2]
					denominator = z/d

					row = create_row(x/denominator, y/denominator)
					polygons[a][b] = row

	if(not parallel):
		for a in range(len(vertices)):
			x = vertices[a][0]
			y = vertices[a][1]
			z = vertices[a][2]
			denominator = z/d
			
			row = create_row(x/denominator, y/denominator)
			vertices[a] = row
		#	print(vertices)

def create_polygons():
	for a in range(len(face)):
		poly = []
		face_1 = int(face[a][0])
		face_2 = int(face[a][1])
		face_3 = int(face[a][2])

		poly.append(vertices[face_1])
		poly.append(vertices[face_2])
		poly.append(vertices[face_3])

		polygons.append(poly)

def region_code(x,y): 
	
	#checking above window.
	if (boundary == 0 and y < y2_world):
		return True

	#checking below window.
	elif (boundary == 1 and y > y1_world):
		return True		

	#checking left of window.
	elif(boundary == 2 and x > x1_world):
		return True

	#checking right of window.
	elif (boundary == 3 and x < x2_world):
		return True

	return False
	
def transfer():
	#transfer the points 
	polygons.clear()

	a = 0
	while a < (len(clipped_list)):
		poly = []
		b = 0
		while b < (len(clipped_list[a])):
			row = create_row(clipped_list[a][b][0], clipped_list[a][b][1])
			poly.append(row)
			b = b + 1
		polygons.append(poly)
		a = a + 1
	clipped_list.clear()

def clipping():
	global x1_world, y1_world, x2_world, y2_world
	if(not parallel):
		x1_world = -abs(d)
		y1_world = -abs(d)
		x2_world = abs(d)
		y2_world = abs(d)
	else:
		x1_world = -1.0
		y1_world = -1.0
		x2_world = 1.0
		y2_world = 1.0

	boundary = 0 #top
	clipper()
	transfer()

	boundary = 1 #bottom
	clipper()
	transfer()
	
	boundary = 2 #left
	clipper()
	transfer()

	boundary = 3 #right
	clipper()
	#print(clipped_list)

def clipper():
	poly = []
	a = 0
	while a < (len(polygons)):
		for b in range(len(polygons[a])-1):
			x1 = float((polygons[a][b][0]))
			y1 = float((polygons[a][b][1]))
			x2 = float((polygons[a][b+1][0]))
			y2 = float((polygons[a][b+1][1]))

			if(region_code(x1, y1)):
				if(b == 0):
					row = create_row(x1, y1)
					poly.append(row)

				if(region_code(x2, y2)):
					row = create_row(x2, y2)
					poly.append(row)
				else:
					intersection(x1, y1, x2, y2, boundary)
					row = create_row(x_intersect, y_intersect)
					poly.append(row)

			else:
				if(region_code(x2, y2)):
					intersection(x2, y2, x1, y1, boundary)
					row = create_row(x_intersect, y_intersect)
					poly.append(row)
					row = create_row(x2, y2)
					poly.append(row)

		if(poly):
			clipped_list.append(poly)
		poly = []
		#print(clipped_list)
		a = a + 1
	
	#add first point to last for all polygons
	a = 0
	while a < (len(clipped_list)):
		row = create_row(clipped_list[a][0][0], clipped_list[a][0][1])
		clipped_list[a].append(row)
		a = a + 1

def intersection(x1, y1, x2, y2, boundary):
	dx = x2 - x1
	dy = y2 - y1
	#if it is a vertical line
	if(dx == 0 or dy == 0):
		if(boundary == 0):
			x_intersect = x1
			y_intersect = y2_world
		elif(boundary == 1):
			x_intersect = x1
			y_intersect = y1_world
		elif(boundary == 2):
			x_intersect = x1_world
			y_intersect = y1
		elif(boundary == 3):
			x_intersect = x2_world
			y_intersect = y1
	else:
		slope = dy/dx
		#print(slope)
		if(boundary == 0):
			x_intersect = (y2_world - y1)/slope + x1
			y_intersect = y2_world
		if(boundary == 1):
			x_intersect = (y1_world - y1)/slope + x2
			y_intersect = y2_world
		if(boundary == 2):
			x_intersect = x1_world
			y_intersect = slope * (x1_world - x1) + y1
		if(boundary == 3):
			x_intersect = x2_world
			y_intersect = slope * (x2_world - x1) + y1
	

def final_transformation():
	#translate to world origin
	translated = []
	a = 0
	while a < (len(clipped_list)):
		poly = []
		b = 0
		while b < (len(clipped_list[a])):
			row = create_row(clipped_list[a][b][0] - x1_world, clipped_list[a][b][1] - y1_world)
			poly.append(row)
			b = b + 1

		translated.append(poly)
		a = a + 1

	#scale
	scaled = []
	a = 0
	while a < (len(translated)):
		poly = []
		b = 0
		while b < (len(translated[a])):
			row = create_row(translated[a][b][0] * ((viewport_x_upper - viewport_x_lower)/(x2_world - x1_world)), translated[a][b][1] * ((viewport_y_upper - viewport_y_lower)/(y2_world - y1_world)))
			poly.append(row)
			b = b + 1

		scaled.append(poly)
		a = a + 1

	#translate to viewport origin
	a = 0
	while a < (len(scaled)):
		poly = []
		b = 0
		while b < (len(scaled[a])):
			row = create_row(scaled[a][b][0] + viewport_x_lower, scaled[a][b][1] + viewport_y_lower)
			poly.append(row)
			b = b + 1

		transformed_list.append(poly)
		a = a + 1
	#print(transformed_list)

def worldview():
	#print(clipped_list)
	x_scale = (viewport_x_upper-viewport_x_lower)/(x_upper-x_lower)
	y_scale = (viewport_y_upper-viewport_y_lower)/(y_upper-y_lower)
	for a in range(len(clipped_list)):
		clipped_list[a][0] = round(viewport_x_lower + (clipped_list[a][0] - x_lower)*x_scale)
		clipped_list[a][1] = round(viewport_y_lower + (clipped_list[a][1] - y_lower)*y_scale)
		clipped_list[a][2] = round(viewport_x_lower + (clipped_list[a][2] - x_lower)*x_scale)
		clipped_list[a][3] = round(viewport_y_lower + (clipped_list[a][3] - y_lower)*y_scale)
	#print(clipped_list)

def dda():
	a = 0
	while a < (len(transformed_list)):
		b = 0
		while b < (len(transformed_list[a])-1):
			x1 = float(transformed_list[a][b][0])
			y1 = float(transformed_list[a][b][1])
			x2 = float(transformed_list[a][b+1][0])
			y2 = float(transformed_list[a][b+1][1])

			#print(x1, y1, x2, y2)
			dx = (x2-x1)
			dy = (y2-y1)
			
			if (abs(dx) > abs(dy)):
				length = abs(dx)
			else:
				length = abs(dy)
			
			if((x1 == x2) and dy<0):
				length = abs(dy)

			if(x1 == x2 and y1 == y2):
				xinc = 0
				yinc = 0

			else:
				xinc = (dx/(length))
				yinc = (dy/(length))

			x = int(round(x1))
			y = int(round(y1))
			#x_2 = int(round(x2))
			#y_2 = int(round(y2))
			#print(y, x)
			#point = (y, x)
			#point2 = (y_2, x_2)
			#pbm_file[y][x] = 1

			c = 0
			while c < (int(length)):
				if(not(x < viewport_x_lower or y < viewport_y_lower or x > viewport_x_upper or y > viewport_y_upper)):
					pbm_file[round(y)][round(x)] = 1;

				x = x + xinc
				y = y + yinc
				c = c + 1
			b = b + 1
		a = a + 1

			
	#print(not_horizontal)
	#print(list_points) #without all of the horizontal points

def draw():
	#if(len(clipped_list) == 0):
	#	print("P1")
	#	print("#test.pbm") #change this
	#	print("%s %s" % (width, height))
	#	for d in reversed(pbm_file):
	#		print (" ".join(str(e) for e in d))
	#		if(d == (width)):
	#			print("\"")

	#else:
		#print(list_pbm)
	print("P1")
	print("#test.pbm") #change this
	print("%s %s" % (width, height))
	for d in reversed(pbm_file):
		print (" ".join(str(e) for e in d))
		if(d == (width)):
			print("\"")


#read in parameters
for x in range(len(sys.argv)):
	#postscript file name
	if sys.argv[x] == "-f":
		postscript_file = sys.argv[x+1]

	#integer lower bound in the viewport x dimension of the world window (499)
	if sys.argv[x] == "-j":
		viewport_x_lower = int(sys.argv[x+1])

	#integer lower bound in the viewport y dimension of the world window (499)
	if sys.argv[x] == "-k":
		viewport_y_lower = int(sys.argv[x+1])

	#integer upper bound in the viewport x dimension of the world window (499)
	if sys.argv[x] == "-o":
		viewport_x_upper = int(sys.argv[x+1])

	#integer upper bound in the viewport y dimension of the world window (499)
	if sys.argv[x] == "-p":
		viewport_y_upper = int(sys.argv[x+1])
		
	#floating point x of Projection Reference Point (PRP) in VRC coordinates (0)
	if sys.argv[x] == "-x":
		x_prp = float(sys.argv[x+1])

	#floating point y of Projection Reference Point (PRP) in VRC coordinates (0)
	if sys.argv[x] == "-y":
		y_prp = float(sys.argv[x+1])

	#floating point z of Projection Reference Point (PRP) in VRC coordinates (1)
	if sys.argv[x] == "-z":
		z_prp = float(sys.argv[x+1])

	#floating point x of View Reference Point (VRP) in world coordinates (0)
	if sys.argv[x] == "-X":
		x_vrp = float(sys.argv[x+1])

	#floating point y of View Reference Point (VRP) in world coordinates (0)
	if sys.argv[x] == "-Y":
		y_vrp = float(sys.argv[x+1])

	#floating point z of View Reference Point (VRP) in world coordinates (0)
	if sys.argv[x] == "-Z":
		z_vrp = float(sys.argv[x+1])

	#floating point x of View Plane Normal vector (VPN) in world coordinates (0)
	if sys.argv[x] == "-q":
		x_vpn = float(sys.argv[x+1])

	#floating point y of View Plane Normal vector (VPN) in world coordinates (0)
	if sys.argv[x] == "-r":
		y_vpn = float(sys.argv[x+1])

	#floating point z of View Plane Normal vector (VPN) in world coordinates (-1)
	if sys.argv[x] == "-w":
		z_vpn = float(sys.argv[x+1])

	#floating point x of View Up Vector (VUP) in world coordinates (0)
	if sys.argv[x] == "-Q":
		x_vup = float(sys.argv[x+1])

	#floating point y of View Up Vector (VUP) in world coordinates (1)
	if sys.argv[x] == "-R":
		y_vup = float(sys.argv[x+1])

	#floating point z of View Up Vector (VUP) in world coordinates (0)
	if sys.argv[x] == "-W":
		z_vup = float(sys.argv[x+1])

	#floating point u min of the VRC window in VRC coordinates (-0.7)
	if sys.argv[x] == "-u":
		u_min_vrc = float(sys.argv[x+1])

	#floating point v min of the VRC window in VRC coordinates (-0.7)
	if sys.argv[x] == "-v":
		v_min_vrc = float(sys.argv[x+1])

	#floating point u max of the VRC window in VRC coordinates (0.7)
	if sys.argv[x] == "-U":
		u_max_vrc = float(sys.argv[x+1])

	#floating point v max of the VRC window in VRC coordinates (0.7)
	if sys.argv[x] == "-V":
		v_max_vrc = float(sys.argv[x+1])
		
	#Use parallel projection. If this flag is not present, use perspective projection
	if sys.argv[x] == "-P":
		parallel = True

	if sys.argv[x] == "-b":
		culling = True

	if sys.argv[x] == "-F":
		front = float(sys.argv[x+1])

	if sys.argv[x] == "-B":
		back = float(sys.argv[x+1])

height = 501
width = 501
list_points = []
clipper_1 = [x_lower, y_lower]
clipper_2 = [x_lower, y_upper]
clipper_3 = [x_upper, y_upper]
clipper_4 = [x_upper, y_lower]
pbm_file = [[0 for i in range(width)] for j in range(height)]
read_psfile(postscript_file)
d = z_prp/(back - z_prp)

transformations()
if(culling):
	backface_culling()

projection()
create_polygons()

clipping()
final_transformation()
dda()
draw()