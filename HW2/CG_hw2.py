#!/usr/bin/env python3

import sys
from math import sin, cos, radians
List = []
window_list = []
vertices_List = []
scaling_list = []
rotation_list = []
transformed_list = []
new_transformed_list = []
clipped_list = []
pbm_file = []

#python code to read file and output lines in terminal
def read_psfile(filename):
	with open(filename, 'r') as Lines:
		#takes the lines in between BEGIN and END
		for line in Lines:
			if line.strip() == "%%%BEGIN":
				break

		for line1 in Lines:
			if line1.strip() == "%%%END" or line1.strip() == "stroke":
				break

			else: #write how to ignore a blank line
				line_num = line1.split()
				List.append(line_num)

	length = (len(List))
	for x in range(length):
		x_cord = int(List[x][0])
		y_cord = int(List[x][1])
		coordinates = (x_cord,y_cord)
		vertices_List.append(coordinates)

def transformations():
	length = (len(vertices_List))
	#print(vertices_List)
	#scaling (multiply every linear dimension by the same factor)
	for x in range(length):
		scale_edit = [(int(vertices_List[x][0])*scaling_factor), (int(vertices_List[x][1])*scaling_factor)]
		scaling_list.append(scale_edit)
	#print(scaling_list)
		
	#counter clockwise rotation
	for x in range(length):
		x1 = float((scaling_list[x][0]))
		y1 = float((scaling_list[x][1]))
		x1_prime = (x1 * cos((rotation))) - (y1 * sin((rotation)))
		y1_prime = (x1 * sin((rotation))) + (y1 * cos((rotation)))

		rotation_edit = [x1_prime, y1_prime]
		rotation_list.append(rotation_edit)
	#print(rotation_list)

	#translation in x and y direction
	for x in range(length):
		transformed_edit = [((rotation_list[x][0]) + x_translation), ((rotation_list[x][1]) + y_translation)]
		transformed_list.append(transformed_edit)
	#print(transformed_list)

def x_intersection(clipper_x1, clipper_y1, clipper_x2, clipper_y2, x1, y1, x2, y2):
	num = (clipper_x1*clipper_y2 - clipper_y1*clipper_x2) * (x1-x2) - (clipper_x1-clipper_x2) * (x1*y2 - y1*x2)
	den = (clipper_x1-clipper_x2) * (y1-y2) - (clipper_y1-clipper_y2) * (x1-x2)
	number = int(num/den)
	return number

def y_intersection(clipper_x1, clipper_y1, clipper_x2, clipper_y2, x1, y1, x2, y2):
	num = (clipper_x1*clipper_y2 - clipper_y1*clipper_x2) * (y1-y2) - (clipper_y1-clipper_y2) * (x1*y2 - y1*x2)
	den = (clipper_x1-clipper_x2) * (y1-y2) - (clipper_y1-clipper_y2) * (x1-x2)
	number = int(num/den)
	return number

def region_code(x,y):
	region = 0

	#checking left of window. If yes, add 1
	if(x < x_lower):
		region = region + 1

	#checking right of window. If yes, add 2
	if (x > x_upper):
		region = region + 2

	#checking below window. If yes, add 4
	if (y < y_lower):
		region = region + 4

	#checking above window. If yes, add 8
	if (y > y_upper):
		region = region + 8

	return region

def sutherland():
#	print("transofrmed list:")
#	print(transformed_list)
	size_clipper = len(window_list)
	size_polygon = len(transformed_list)
	for a in range(size_clipper):
		b = (a+1) % size_clipper
		clipper_x1 = window_list[a][0]
		clipper_y1 = window_list[a][1]
		clipper_x2 = window_list[b][0]
		clipper_y2 = window_list[b][1]
		#print(a,b)
		new_size = 0
		for c in range(size_polygon):
			d = (c+1) % size_polygon
			x1 = float((transformed_list[c][0]))
			y1 = float((transformed_list[c][1]))
			x2 = float((transformed_list[d][0]))
			y2 = float((transformed_list[d][1]))
			#print(x1, y1, x2, y2)
			first_pos = (clipper_x2 - clipper_x1) * (y1 - clipper_y1) - (clipper_y2-clipper_y1) * (x1-clipper_x1)
			second_pos = (clipper_x2 - clipper_x1) * (y2-clipper_y1) - (clipper_y2-clipper_y1) * (x2-clipper_x1)

			#if both points are inside
			if(first_pos < 0 and second_pos < 0):
				sutherland_list[new_size][0] = x2
				sutherland_list[new_size][1] = y2
				new_size = new_size + 1
				#print("new")
			#	print(x2, y2)

			#if only first point is outside
			elif(first_pos >= 0 and second_pos < 0):
				sutherland_list[new_size][0] = x_intersection(clipper_x1, clipper_y1, clipper_x2, clipper_y2, x1, y1, x2, y2)
				sutherland_list[new_size][1] = y_intersection(clipper_x1, clipper_y1, clipper_x2, clipper_y2, x1, y1, x2, y2)
				new_size = new_size + 1
			#	print("new")
			#	print(x_intersection(clipper_x1, clipper_y1, clipper_x2, clipper_y2, x1, y1, x2, y2), y_intersection(clipper_x1, clipper_y1, clipper_x2, clipper_y2, x1, y1, x2, y2))

				sutherland_list[new_size][0] = x2
				sutherland_list[new_size][1] = y2
				new_size = new_size + 1
			#	print("new")
			#	print(x2, y2)

			#if only second point is outside
			elif(first_pos < 0 and second_pos >= 0):
				sutherland_list[new_size][0] = x_intersection(clipper_x1, clipper_y1, clipper_x2, clipper_y2, x1, y1, x2, y2)
				sutherland_list[new_size][1] = y_intersection(clipper_x1, clipper_y1, clipper_x2, clipper_y2, x1, y1, x2, y2)
				new_size = new_size + 1
			#	print("new")
			#	print(x_intersection(clipper_x1, clipper_y1, clipper_x2, clipper_y2, x1, y1, x2, y2), y_intersection(clipper_x1, clipper_y1, clipper_x2, clipper_y2, x1, y1, x2, y2))

		size_polygon= new_size
		#print(size_polygon)
		if (len(transformed_list) != (new_size)):
			diff = new_size - (len(transformed_list))
			point = [0,0]
			for a in range(diff):
				transformed_list.append(point)

		for e in range(len(transformed_list)):
			transformed_list[e][0] = [0][0]
			transformed_list[e][1] = [0][0]

		for e in range(size_polygon):
			transformed_list[e][0] = sutherland_list[e][0]
			transformed_list[e][1] = sutherland_list[e][1]
	
	for f in range(size_polygon):
		point = ([sutherland_list[f][0], sutherland_list[f][1]])
		new_transformed_list.append(point)

def clipping():
	#print(new_transformed_list)
	for a in range(len(new_transformed_list) - 1):
		x1 = float((new_transformed_list[a][0]))
		y1 = float((new_transformed_list[a][1]))
		x2 = float((new_transformed_list[a+1][0]))
		y2 = float((new_transformed_list[a+1][1]))

		#region_code for the points
		point1_region = region_code(x1, y1)
		point2_region = region_code(x2, y2)
		inside_region = False

		while True:
			#if both points are outside region
			if ((point1_region & point2_region) != 0):
				break

			#if both points are inside region
			elif (point1_region == 0 and point2_region == 0):
				inside_region = True
				break

			#line needs to be clipped
			else:
				x = float(0)
				y = float(0)

				#figuring out which point is outside
				if point1_region != 0:
					outside_point = point1_region
				else:
					outside_point = point2_region

				#find intersection point using slope formula
				if (outside_point & 8) >= 1:
					x = slope_formula(x1, x2,y_upper,y1,y2)
					y = y_upper

				elif (outside_point & 4) >= 1:
					x = slope_formula(x1, x2,y_lower,y1,y2) 
					y = y_lower
					
				elif (outside_point & 2) >= 1:
					y = slope_formula(y1, y2,x_upper,x1,x2)
					x = x_upper

				elif (outside_point & 1) >= 1:
					y = slope_formula(y1, y2,x_lower,x1,x2) 
					x = x_lower

				if outside_point == point1_region:
					x1 = x
					y1 = y
					point1_region = region_code(x1, y1)

				else:
					x2 = x
					y2 = y
					point2_region = region_code(x2, y2)

		if inside_region:	
			clipped_line = [x1, y1, x2, y2]
			clipped_list.append(clipped_line)


def slope_formula(num1, num2,region,numb1,numb2):
	return (num1 + (num2-num1)*(region-numb1)/(numb2-numb1))

def dda():
	#set every pixel to 0
	pbm_file = [[0 for i in range(width)] for j in range(height)]
	#print("clipped:")
	#print(clipped_list)
	#print(len(clipped_list))
	if(len(clipped_list) == 0):
		print("P1")
		print("#test.pbm") #change this
		print("%s %s" % (width, height))
		for d in reversed(pbm_file):
			print (" ".join(str(e) for e in d))
			if(d == (width)):
				print("\"")
	else:
		for a in range(len(clipped_list)+1):
			#print(a)
			if(a == len(clipped_list)):
				x1 = float((clipped_list[a-1][2]))
				y1 = float((clipped_list[a-1][3]))
				x2 = float((clipped_list[0][0]))
				y2 = float((clipped_list[0][1]))
			else:
				x1 = float((clipped_list[a][0]))
				y1 = float((clipped_list[a][1]))
				x2 = float((clipped_list[a][2]))
				y2 = float((clipped_list[a][3]))

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
			#if (length > 0):
			else:
				xinc = (dx/(length))
				yinc = (dy/(length))

			#if((x1 == x2) and dy<0):
			#	yinc = (dy)/length

			x = int(round(x1))
			y = int(round(y1))
			#print(x,y)

			#pbm_file[(y-y_lower)][(x-x_lower)] = 1
			#print(y-y_lower, x-x_lower)
			#print (pbm_file)

			for c in range(int(length)):
				x = x + xinc
				y = y + yinc
				x_point = round(x - x_lower)
				y_point = round(y - y_lower)
				#print(x_point, y_point)
				if(not(x < x_lower or y < y_lower or x > x_upper or y > y_upper)):
					pbm_file[y_point][x_point] = 1
			
		#	print (pbm_file)
		
		print("P1")
		print("#test.pbm") #change this
		print("%s %s" % (width, height))
		for d in reversed(pbm_file):
		#	print (" ".join(str(e) for e in d))
			if(d == (width)):
				print("\"")

postscript_file = "hw2_a.ps"
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

#read in parameters
for x in range(len(sys.argv)):
	#postscript file name
	if sys.argv[x] == "-f":
		postscript_file = sys.argv[x+1]
	
	#float specifying the scaling factor in both dimensions 
	# about the world origin. (1.0)
	if sys.argv[x] == "-s":
		scaling_factor = float(sys.argv[x+1])

	#integer specifying the number of degrees for a 
	# counter-clockwise rotation about the world origin. (0)
	if sys.argv[x] == "-r":
		rotation = radians(int(sys.argv[x+1]))

	#integer specifying a translation in the x dimension. (0)
	if sys.argv[x] == "-m":
		x_translation = int(sys.argv[x+1])

	#integer specifying a translation in the y dimension. (0)
	if sys.argv[x] == "-n":
		y_translation = int(sys.argv[x+1])
	
	#integer lower bound in the x dimension of the world window (0)
	if sys.argv[x] == "-a":
		x_lower = int(sys.argv[x+1])

	#integer lower bound in the y dimension of the world window (0)
	if sys.argv[x] == "-b":
		y_lower = int(sys.argv[x+1])

	#integer upper bound in the x dimension of the world window (499)
	if sys.argv[x] == "-c":
		x_upper = int(sys.argv[x+1])

	#integer upper bound in the y dimension of the world window (499)
	if sys.argv[x] == "-d":
		y_upper = int(sys.argv[x+1])
height = y_upper - y_lower + 1
width = x_upper - x_lower + 1
clipper_1 = [x_lower, y_lower]
clipper_2 = [x_lower, y_upper]
clipper_3 = [x_upper, y_upper]
clipper_4 = [x_upper, y_lower]
window_list.append(clipper_1)
window_list.append(clipper_2)
window_list.append(clipper_3)
window_list.append(clipper_4)
sutherland_list = [[0 for i in range(2)] for j in range(30)]


read_psfile(postscript_file)
transformations()
sutherland()
clipping()
dda()