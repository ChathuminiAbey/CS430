#!/usr/bin/env python3

import sys
from math import sin, cos, radians
List = []
scaling_list = []
rotation_list = []
transformed_list = []
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
			if line1.strip() == "%%%END":
				break

			else: #write how to ignore a blank line
				line_num = line1.split()
				List.append(line_num)

def transformations():
	length = (len(List))

	#scaling (multiply every linear dimension by the same factor)
	for x in range(length):
		scale_edit = [(int(List[x][0])*scaling_factor), (int(List[x][1])*scaling_factor), (int(List[x][2])*scaling_factor), (int(List[x][3])*scaling_factor)]
		scaling_list.append(scale_edit)
		
	#counter clockwise rotation
	for x in range(length):
		x1 = float((scaling_list[x][0]))
		y1 = float((scaling_list[x][1]))
		x2 = float((scaling_list[x][2]))
		y2 = float((scaling_list[x][3]))
		x1_prime = (x1 * cos((rotation))) - (y1 * sin((rotation)))
		y1_prime = (x1 * sin((rotation))) + (y1 * cos((rotation)))
		x2_prime = (x2 * cos((rotation))) - (y2 * sin((rotation)))
		y2_prime = (x2 * sin((rotation))) + (y2 * cos((rotation)))

		rotation_edit = [x1_prime, y1_prime, x2_prime, y2_prime]
		rotation_list.append(rotation_edit)

	#translation in x and y direction
	for x in range(length):
		transformed_edit = [((rotation_list[x][0]) + x_translation), ((rotation_list[x][1]) + y_translation), ((rotation_list[x][2]) + x_translation), ((rotation_list[x][3]) + y_translation)]
		transformed_list.append(transformed_edit)

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

def clipping():
	for a in range(len(transformed_list)):
		x1 = float((transformed_list[a][0]))
		y1 = float((transformed_list[a][1]))
		x2 = float((transformed_list[a][2]))
		y2 = float((transformed_list[a][3]))

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
				x = float(1)
				y = float(1)

				#figuring out which point is outside
				if point1_region != 0:
					outside_point = point1_region
				else:
					outside_point = point2_region

				#find intersection point using slope formula
				if outside_point & 8:
					x = slope_formula(x1, x2,y_upper,y1,y2)
					y = y_upper

				elif outside_point & 4:
					x = slope_formula(x1, x2,y_lower,y1,y2) 
					y = y_lower
					
				elif outside_point & 2:
					y = slope_formula(y1, y2,x_upper,x1,x2)
					x = x_upper

				elif outside_point & 1:
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
	
def slope_formula(x1, x2,region,y1,y2):
	return (x1 + (x2-x1)*(region-y1)/(y2-y1))

def dda():
	#set every pixel to 0
	pbm_file = [[0 for i in range(height)] for j in range(width)]
	#print(clipped_list)
	#print (pbm_file)
	#print (width, height)

	for a in range(len(clipped_list)):
		x1 = float((clipped_list[a][0]))
		y1 = float((clipped_list[a][1]))
		x2 = float((clipped_list[a][2]))
		y2 = float((clipped_list[a][3]))

		dx = float((x2-x1))
		dy = float((y2-y1))
		
		if (abs(dx) > abs(dy)):
			length = abs(dx)
		else:
			length = abs(dy)

		if (length > 0):
			xinc = float(dx/float(length))
			yinc = float(dy/float(length))

		x = float(x1)
		y = float(y1)
		#print((x),(y))
		#print (int(abs((x-x_upper))), int(abs((y-y_upper))))
		#print int(abs(round(x))), int(abs(round(y)))
		if(int(abs(round(x))-x_lower)<x_upper-x_lower and int(abs(round(x))-x_lower)> x_lower and int(abs(round(y))-y_lower) < y_upper - y_lower and int(abs(round(y))-y_lower) > y_lower):
			pbm_file[int(abs(round(y)))-y_lower][int(abs(round(x)))-x_lower] = 1
		#print (pbm_file)

		for c in range(int(length)):
			x = x + xinc
			y = y + yinc
			x_point = int(round(x)) - x_lower
			y_point = int(round(y)) - y_lower
			
			if(x_point<x_upper-x_lower and x_point> x_lower and y_point < y_upper-y_lower and y_point > y_lower):
				#print x_point, y_point
				pbm_file[((y_point))][((x_point))] = 1
				#print (y_point, x_point)
		
	#	print (pbm_file)
	
	print("P1")
	print("#test.pbm") #change this
	print("%s %s" % (height, width))
	for bla in reversed(pbm_file):
		print (" ".join(str(b) for b in bla))
		if(bla == (height)):
			print("\"")

	#get line from finished list

			

postscript_file = "hw1.ps"
scaling_factor = float(1.0)
rotation = int(0)
x_translation = int(0)
y_translation = int(0)
x_lower = int(0)
y_lower = int(0)
x_upper = int(499)
y_upper = int(499)
height = y_upper - y_lower + 1
width = x_upper - x_lower + 1

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
#print("Postscript File Name: " + postscript_file)
#print("Scaling factor: %f"  % scaling_factor)
#print("Counter clockwise rotation: "  + str(rotation))
#print("X Translation: "  + str(x_translation))
#print("Y Translation: "  + str(y_translation))
#print("Lower bound in the x dimension: "  + str(x_lower))
#print("Lower bound in the y dimension: "  + str(y_lower))
#print("Upper bound in the x dimension: "  + str(x_upper))
#print("Upper bound in the y dimension: "  + str(y_upper))

read_psfile(postscript_file)
transformations()
clipping()
dda()