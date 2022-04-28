#!/usr/bin/env python

import sys
from PIL import Image
import numpy as np

def find_map_extent(ifile,border_threshold):
	border = border_threshold

	Image.MAX_IMAGE_PIXELS = None
	img = Image.open(ifile).convert("L")
	arr = np.array(img)
	arr = 255 - arr
	
	ny = np.size(arr,0)
	nx = np.size(arr,1)

	border_width = 0
	yu_found = False
	for yp in range(ny):
		ave = np.average(arr[yp,:])
		if (ave >= border ):
			border_width += 1
		elif(border_width >= 1 ):
			if (not yu_found):
				yu = yp
				yu_found = True
			else:
				yl = yp-border_width-1
			border_width = 0
		else:
			border_width = 0

	border_width = 0
	xl_found = False
	for xp in range(nx):
		ave = np.average(arr[:,xp])
		if (ave >= border ):
			border_width += 1
		elif(border_width >= 1 ):
			if (not xl_found):
				xl = xp
				xl_found = True
			else:
				xr = xp-border_width-1
			border_width = 0
		else:
			border_width = 0
			
	return [xl,yu,xr-xl+1,yl-yu+1]
