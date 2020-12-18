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
y_mins = []
y_maxs = []
clipped_individual = []
not_horizontal = []
sutherland_list = [[0 for i in range(2)] for j in range(200)]
postscript_file = "hw3_split.ps"
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
viewport_x_upper = 200
viewport_y_upper = 200

#python code to read file and output lines in terminal
def read_psfile(filename):
	with open(filename, 'r') as Lines:
		#takes the lines in between BEGIN and END
		for line in Lines:
			if line.strip() == "%%%BEGIN":
				break

		for line1 in Lines:
			if line1.strip() == "%%%END":
				break

			else: #write how to ignore a blank line
				line_num = line1.split()
				List.append(line_num)

		length = (len(List))
		#print(List)
		for x in range(length):
			if(List[x]):
				if (List[x][0]) ==  "stroke":
					#print("vertices_List")
					#print(vertices_List)
					transformations()
					#print("transformed_list")
					#print(transformed_list)
					sutherland()
					#print("new_transformed_list")
					#print(new_transformed_list)
					clipping()
					#print("clipped_list")
					#print(clipped_list)
					if (len(clipped_list) == 0):
						vertices_List.clear()
						scaling_list.clear()
						rotation_list.clear()
						transformed_list.clear()
						new_transformed_list.clear()
						clipped_list.clear()
						not_horizontal.clear()
						y_mins.clear()
						y_maxs.clear()
						list_points.clear()
						clipped_individual.clear()
					else:
						worldview()
						#print(clipped_list)
						ymins()
						ymaxs()
						#print(y_mins)
						dda()
						#print(list_points)
						fill_polygon(list_points)
						vertices_List.clear()
						scaling_list.clear()
						rotation_list.clear()
						transformed_list.clear()
						new_transformed_list.clear()
						clipped_list.clear()
						y_mins.clear()
						y_maxs.clear()
						not_horizontal.clear()
						list_points.clear()
						clipped_individual.clear()

				else:
					x_cord = int(List[x][0])
					y_cord = int(List[x][1])
					coordinates = (x_cord,y_cord)						
					#print(coordinates)
					vertices_List.append(coordinates)
		#print("clipped:")
		#ßßprint(clipped_list)
		

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
#	print("transformed:")
#	print(transformed_list)

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
	sutherland_list = [[0 for i in range(2)] for j in range(200)]
	size_clipper = len(window_list)
	size_polygon = len(transformed_list)
	#print(transformed_list)
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

			#print(sutherland_list)
			#if both points are inside
			if(first_pos < 0 and second_pos < 0):
				if(c == 0):
					sutherland_list[new_size][0] = x1
					sutherland_list[new_size][1] = y1
					new_size = new_size + 1
					sutherland_list[new_size][0] = x2
					sutherland_list[new_size][1] = y2
					
				else:
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
		#print(transformed_list)
		for e in range(size_polygon):
			transformed_list[e][0] = sutherland_list[e][0]
			transformed_list[e][1] = sutherland_list[e][1]
	#print(sutherland_list)
	for f in range(size_polygon):
		point = ([sutherland_list[f][0], sutherland_list[f][1]])
		new_transformed_list.append(point)

	point = ([sutherland_list[0][0], sutherland_list[0][1]])
	new_transformed_list.append(point)
	
#	print("sutherland:")
	#print(new_transformed_list)
def clipping():
	#print("new transformed:")
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
			#print(clipped_line)
			clipped_list.append(clipped_line)

def slope_formula(num1, num2,region,numb1,numb2):
	return (num1 + (num2-num1)*(region-numb1)/(numb2-numb1))

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

def ymins():
	#print(clipped_list)
	for a in range(len(clipped_list)):
		y1 = clipped_list[a][1]
		y2 = clipped_list[a][3]
		if y1 < y2:
			point = (clipped_list[a][1], clipped_list[a][0])
			y_mins.append(point)
		elif y2 < y1:
			point = (clipped_list[a][3], clipped_list[a][2])
			y_mins.append(point)
	#print(y_mins)

def ymaxs():
	for a in range(len(clipped_list)):
		y1 = clipped_list[a][1]
		y2 = clipped_list[a][3]
	if y1 > y2:
		point = (clipped_list[a][1], clipped_list[a][0])
		y_maxs.append(point)
	elif y2 > y1:
		point = (clipped_list[a][3], clipped_list[a][2])
		y_maxs.append(point)

def dda():
	#print(clipped_list)
	for a in range(len(clipped_list)):
		x1 = int((clipped_list[a][0]))
		y1 = int((clipped_list[a][1]))
		x2 = int((clipped_list[a][2]))
		y2 = int((clipped_list[a][3]))

		#print(x1, y1, x2, y2)
		dx = (x2-x1)
		dy = (y2-y1)
		
		if(dy != 0):
			point = (y1, x1)
			not_horizontal.append(point)
			point = (y2, x2)
			not_horizontal.append(point)
		
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
		x_2 = int(round(x2))
		y_2 = int(round(y2))
		#print(y, x)
		point = (y, x)
		point2 = (y_2, x_2)
		pbm_file[y][x] = 1

		for c in range(int(length)):
			x_point = round(x)
			y_point = round(y)
			point = (y_point, x_point)
			if(yinc != 0 and y_point != round(y + yinc)):
				if(point not in list_points):
					list_points.append(point)
			x = x + xinc
			y = y + yinc
			pbm_file[y_point][x_point] = 1
		x_point = round(x)
		y_point = round(y)
		point = (y_point, x_point)
		if(yinc != 0 and y_point != round(y + yinc)):
			list_points.append(point)
			
	#print(not_horizontal)
	#print(list_points) #without all of the horizontal points

def fill_polygon(list_points):
	fill_list = []
#	print(y_mins)
	list_points = sorted(list_points, key=lambda k: [k[0], k[1]])
	
	#print(list_points)
	#print(not_horizontal)
	y_min = list_points[0][0]
	y_max = list_points[len(list_points)-1][0]
	count = y_min
	#print(y_min, y_max)
#if you get to an edge point, check the slopes of the lines connecting it. It slope is up and sideways, down and sideways, positie and sideays, negative nand isdeays, etc

	#get rid of edge points
	for a in range(len(not_horizontal)):
		if((not_horizontal[a][0]) == y_min or (not_horizontal[a][0]) == y_max):
			point = (not_horizontal[a][0],not_horizontal[a][1])
			#print(point)
			list_points.append(point)

		#if((not_horizontal[a]) not in list_points):
		#			point = (not_horizontal[a][0],not_horizontal[a][1])
		#			list_points.append(point)

		if((not_horizontal[a]) in y_mins):
			point = (not_horizontal[a][0],not_horizontal[a][1])
			list_points.append(point)

		if((not_horizontal[a]) in y_maxs):
			point = (not_horizontal[a][0],not_horizontal[a][1])
			list_points.append(point)
			#print(clipped_individual[a])		

	#for a in range(len(not_horizontal)-1):
	#	if(not_horizontal[a][0] == not_horizontal[a+1][0]):
			#if(not_horizontal[a-1][1] == not_horizontal[a][1]):
				#print(not_horizontal[a][0])


	list_points = sorted(list_points , key=lambda k: [k[0], k[1]])

#	print(list_points)
	while (count <= y_max):
		working_with = []
		for c in range(len(list_points)):
			if(list_points[c][0] == count):
				point = list_points[c]
				working_with.append(point)

		#if(len(working_with) > 2):		
			#print(working_with)

		if (len(working_with) % 2 == 0):
			#print(len(working_with) % 2)
			while(len(working_with) > 0):
				#print(working_with)
				x1 = working_with[0][1]
				x2 = working_with[1][1]
			#	print(x1,x2)
				while (x1 <= x2):
				#	print(x1)
					pbm_file[count][x1] = 1
					x1 = x1 + 1
				working_with.pop(0)
				working_with.pop(0)

		else:
			while(len(working_with) > 0):
				#print(working_with)
				#print(clipped_individual)

				if(len(working_with) == 2):
					x1 = working_with[0][1]
					x2 = working_with[1][1]
					while (x1 <= x2):
					#	print(x1)
						pbm_file[count][x1] = 1
						x1 = x1 + 1
					working_with.pop(0)
					working_with.pop(0)

				elif(len(working_with) == 1):
					working_with.pop(0)

				else:
					if(working_with[0] in not_horizontal): 
						working_with.pop(0)

					elif(working_with[0] not in not_horizontal):
						#	print(working_with)
						x1 = working_with[0][1]
						x2 = working_with[1][1]
						if(x2 - x1 == 1):
							working_with.pop(1)
					#	print(x1,x2)
						else:
							while (x1 <= x2):
							#	print(x1)
								pbm_file[count][x1] = 1
								x1 = x1 + 1
							#print(working_with)
							working_with.pop(0)
							working_with.pop(0)
		count = count + 1

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

height = 501
width = 501
list_points = []
clipper_1 = [x_lower, y_lower]
clipper_2 = [x_lower, y_upper]
clipper_3 = [x_upper, y_upper]
clipper_4 = [x_upper, y_lower]
window_list.append(clipper_1)
window_list.append(clipper_2)
window_list.append(clipper_3)
window_list.append(clipper_4)
pbm_file = [[0 for i in range(width)] for j in range(height)]

read_psfile(postscript_file)
draw()
