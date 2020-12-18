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
postscript_file = "bound-sprellpsd.smf"
second_SMF = ""
third_SMF = ""
new_vertices = []
polygons = []
list_edges = []
list_of_intersections = []
x1_world = 0.0
y1_world = 0.0
x2_world = 0.0
y2_world = 0.0
boundary = 0
poly = []
transformed_list = []
clipped_list = []
pbm_file = []
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
z_far = 0
z_near = 0

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
color = ""

#python code to read file and output lines in terminal
def read_psfile(filename):
	with open(filename, 'r') as Lines:
		for line in Lines:	
			if len(line.strip()) != 0:
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

def create_row(x,y,z):
	row = []
	row.append(x)
	row.append(y)
	row.append(z)
	return row

def projection():

	if(not parallel):
		for a in range(len(vertices)):
			x = vertices[a][0]
			y = vertices[a][1]
			z = vertices[a][2]
			denominator = z/d
			
			row = create_row(x/denominator, y/denominator, z)
			vertices[a] = row
	#print(vertices)

def create_polygons():
	for a in range(len(face)):
		poly = []
		face_1 = int(face[a][0])
		face_2 = int(face[a][1])
		face_3 = int(face[a][2])
		face_4 = int(face[a][0])

		poly.append(vertices[face_1])
		poly.append(vertices[face_2])
		poly.append(vertices[face_3])
		poly.append(vertices[face_4])

		polygons.append(poly)
	
	#print(polygons)
	
def final_transformation():
	global x1_world, y1_world, x2_world, y2_world
	if(not parallel):
		x1_world = -abs(d)
		y1_world = -abs(d)
		x2_world = abs(d)
		y2_world = abs(d)
		#print(d)
	else:
		x1_world = -1.0
		y1_world = -1.0
		x2_world = 1.0
		y2_world = 1.0

	#translate to world origin
	translated = []
	a = 0
	while a < (len(polygons)):
		poly = []
		b = 0
		while b < (len(polygons[a])):
			row = create_row(polygons[a][b][0] - x1_world, polygons[a][b][1] - y1_world, polygons[a][b][2])
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
			if(b<4):
				row = create_row(translated[a][b][0] * ((viewport_x_upper - viewport_x_lower)/(x2_world - x1_world)), translated[a][b][1] * ((viewport_y_upper - viewport_y_lower)/(y2_world - y1_world)), translated[a][b][2])
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
			row = create_row(scaled[a][b][0] + viewport_x_lower, scaled[a][b][1] + viewport_y_lower, scaled[a][b][2])
			poly.append(row)
			b = b + 1

		transformed_list.append(poly)
		a = a + 1
	#
	#print(transformed_list)
	fill_polygon(transformed_list)


def fill_polygon(transformed_list):
	list_of_intersections = []
	#print(len(transformed_list))
	a = 0
	while a < len(transformed_list):
		list_points = transformed_list[a]

		#find ymin
		b = 0
		y_min = sys.float_info.max
		while b < len(list_points):
			num = list_points[b][1]
			if(round(num) < round(y_min)):
				y_min = num
			b = b + 1

		#find ymax
		b = 0
		y_max = -100
		while b < len(list_points):
			num = list_points[b][1]
			if(round(num) > round(y_max)):
				y_max = num
			b = b + 1

		#print(y_max, y_min)
		#create edges list and intersection points
		c = int(y_min)
		while c <= int(y_max):
			list_edges.append([])
			list_of_intersections.append([])
			c = c + 1

		d = 0
		while d < (len(list_points)-1):
			
			y_min_edge = transformed_list[a][d][1]
			y_max_edge = transformed_list[a][d+1][1]
			#print(y_max_edge, y_min_edge)
			e = int(y_min)
			while e <= int(y_max):
				if(((round(e) >= round(y_min_edge) and round(e) < round(y_max_edge)) or (round(e) >= round(y_max_edge) and round(e) < round(y_min_edge))) and round(y_min_edge) != round(y_max_edge)):
					row = []

					row.append(float(transformed_list[a][d][0]))
					row.append(y_min_edge)
					row.append(float(transformed_list[a][d+1][0]))
					row.append(y_max_edge)

					list_edges[int(e-y_min)].append(row)
				e = e + 1
			d = d+1
		
		e = int(y_min)
		while e <= int(y_max):
			list_of_intersections = []
			f = int(y_min)
			while f <= int(y_max):
				list_of_intersections.append([])
				f = f + 1
			
			f = 0
			while f < len(list_edges[int(e-y_min)]):
				x1 = list_edges[int(e-y_min)][f][0]
				y1 = list_edges[int(e-y_min)][f][1]
				x2 = list_edges[int(e-y_min)][f][2]
				y2 = list_edges[int(e-y_min)][f][3]

				#calculate intersection
				row = []
				row.append(x1 + ((x2-x1)/(y2-y1))*(e - y1))
				row.append(float(e))

				list_of_intersections[int(e-y_min)].append(row)

				f = f + 1
			#
			#print(list_of_intersections)
			list_of_intersections = sorting(list_of_intersections)
			#print(list_of_intersections)
			fill_scan(list_points, list_of_intersections)
			e = e + 1

		#print(list_of_intersections)
		list_edges.clear()
		list_of_intersections = []
		a = a + 1

def fill_scan(list_points, list_of_intersections):
	if(parallel):
		z_near = 0
		z_far = -1
	else:
		z_near = (z_prp - front)/(back - z_prp)
		z_far = -1
	#print(front)
	g = 0
	#print(len(transformed_list))
	while g < len(list_of_intersections):
		h = 0
		while h < len(list_of_intersections[g]):
			x1 = float(list_of_intersections[g][h][0])
			y1 = float(list_of_intersections[g][h][1])
			x2 = float(list_of_intersections[g][h+1][0])
			y2 = float(list_of_intersections[g][h+1][1])

			point = x1
			#print(x1, y1, x2, y2, point)
			while point <= x2:
				z = find(list_points, x1, y1, x2, y2, point, y1)
				
				if(point < 0):
					point = 0
				if(point > 500):
					point = 500

				if(y1 < 0):
					y1 = 0
				if(y1 > 500):
					y1 = 500
				
				#print(z, z_far, z_near)
				if(z < front and z > z_buffer[round(y1)][round(point)]):
					z_buffer[round(y1)][round(point)] = z
					#print(z)

					color_shade = int(20 * (z - z_far)/(z_near - z_far))
					#print(z, z_far, z_near)
					if(color_shade > 20):
						color_shade = 20
					if(color_shade < 0):
						color_shade = 0
					#print(color_shade)	
					number = (get_color(color_shade))

					if(color == "red"):
						pbm_file[round(y1)][round(point)] = "%s 0 0" % number
					elif(color == "green"):
						pbm_file[round(y1)][round(point)] = "0 %s 0" % number
					elif(color == "blue"):
						pbm_file[round(y1)][round(point)] = "0 0 %s" % number
				point = point + 1
			h= h + 2
		g = g + 1

def get_color(num):
	if (num == 0):
		return 0
	if (num == 1):
		return 20
	if (num == 2):
		return 30
	if (num == 3):
		return 40
	if (num == 4):
		return 50
	if (num == 5):
		return 60
	if (num == 6):
		return 65
	if (num == 7):
		return 85
	if (num == 8):
		return 95
	if (num == 9):
		return 105
	if (num == 10):
		return 110
	if (num == 11):
		return 115
	if (num == 12):
		return 135
	if (num == 13):
		return 155
	if (num == 14):
		return 175
	if (num == 15):
		return 180
	if (num == 16):
		return 200
	if (num == 17):
		return 205
	if (num == 18):
		return 225
	if (num == 19):
		return 235
	if (num == 20):
		return 255


def find(transformed_list, x_1, y_1, x_2, y_2, point, y_1p):
	#print(transformed_list)
	x1 = float(transformed_list[0][0])
	y1 = float(transformed_list[0][1])
	z1 = float(transformed_list[0][2])

	x2 = float(transformed_list[1][0])
	y2 = float(transformed_list[1][1])
	z2 = float(transformed_list[1][2])

	x3 = float(transformed_list[2][0])
	y3 = float(transformed_list[2][1])
	z3 = float(transformed_list[2][2])

	a_1 = float(math.sqrt((x_1 - x1)*(x_1 - x1) + (y_1 - y1)*(y_1 - y1)))
	#print(x_1, x1, y_1, y1)
	a_2 = float((math.sqrt((x2 - x1)*(x2 - x1) + (y2 - y1) * (y2 - y1))))
	#print(len(transformed_list))
	z_a = float(z1 + (a_1/a_2) * (z2 - z1))

	b_1 = float(math.sqrt((x_2 - x1) * (x_2 - x1) + (y_2 - y1) * (y_2 - y1)))
	b_2 = float(math.sqrt((x3 - x1)*(x3 - x1) + (y3 - y1)*(y3 - y1)))

	z_b = float(z1 + (b_1/b_2) * (z3 - z1))

	p_1 = float(math.sqrt((point - x_1)*(point - x_1) + (y_1p - y_1)*(y_1p - y_1)))
	p_2 = float(math.sqrt((x_2 - x_1)*(x_2 - x_1) + (y_2 - y_1)*(y_2 - y_1)))
	#print(z_a, p_1, p_2, z_b, z_a)
	if(p_2 != 0):
		zp = float(z_a + (p_1/p_2) * (z_b - z_a))
	else:
		zp = float(z_a)
	return zp;

def sorting(inter):
	for a in range(len(inter)):
		if inter[a]:
			inter[a] = sorted(inter[a], key=lambda x : x[0])
	return inter

def draw():
	print("P3")
	print("#p3.ppm") #change this
	print("%s %s" % (width, height))
	print("255")
	for d in reversed(pbm_file):
		print (" ".join(str(e) for e in d))
		if(d == (width)):
			print("\"")


#read in parameters
for x in range(len(sys.argv)):

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

	#floating point coordinate of the Front (Near) plane in VRC coordinates
	if sys.argv[x] == "-F":
		front = float(sys.argv[x+1])

	#floating point coordinate of the Back (Far) plane in VRC coordinates
	if sys.argv[x] == "-B":
		back = float(sys.argv[x+1])

	#name of the first SMF model. Its base color is "Maxval 0 0" (red)
	if sys.argv[x] == "-f":
		postscript_file = str(sys.argv[x+1])

	#name of the second SMF model. Its base color is "0 Maxval 0" (green)
	if sys.argv[x] == "-g":
		second_SMF = str(sys.argv[x+1])
	
	#name of the third SMF model. Its base color is "0 0 Maxval " (blue).
	if sys.argv[x] == "-i":
		third_SMF = str(sys.argv[x+1])

height = 501
width = 501
list_points = []
clipper_1 = [x_lower, y_lower]
clipper_2 = [x_lower, y_upper]
clipper_3 = [x_upper, y_upper]
clipper_4 = [x_upper, y_lower]
pbm_file = [["0 0 0" for i in range(width)] for j in range(height)]
z_buffer = [[-1 for i in range(width)] for j in range(height)]

color = "red"
read_psfile(postscript_file) #red
d = z_prp/(back - z_prp)

transformations()
projection()
create_polygons()
final_transformation()

if(second_SMF != ""): #green
	color = "green"
	vertices.clear()
	List = []
	face = []
	transformed_list = []
	polygons = []

	read_psfile(second_SMF)
	transformations()

	projection()
	create_polygons()
	final_transformation()


if(third_SMF != ""):
	color = "blue"
	vertices.clear()
	List = []
	face = []
	transformed_list = []
	polygons = []

	read_psfile(third_SMF)
	transformations()

	projection()
	create_polygons()
	final_transformation()


draw()