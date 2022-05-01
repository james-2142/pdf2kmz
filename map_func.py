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

def find_map_trim(ifile,border_threshold,fudge):
	border = border_threshold

	Image.MAX_IMAGE_PIXELS = None
	img = Image.open(ifile).convert("L")
	arr = np.array(img)
	
	ny = np.size(arr,0)
	nx = np.size(arr,1)

	yl_border_width = 0
	for yp in range(ny):
		sum = np.sum(arr[yp,:])
		if (sum == border ):
			yl_border_width += 1
		else:
			break

	yr_border_width = ny
	for yp in reversed(range(ny)):
		sum = np.sum(arr[yp,:])
		if (sum == border ):
			yr_border_width -= 1
		else:
			break

	xl_border_width = 0
	for xp in range(nx):
		sum = np.sum(arr[1:,xp])
		if (sum == border ):
			xl_border_width += 1
		else:
			break

	xr_border_width = nx
	for xp in reversed(range(nx)):
		sum = np.sum(arr[:,xp])
		if (sum == border ):
			xr_border_width -= 1
		else:
			break
			
	return [xl_border_width+fudge,yl_border_width+fudge,xr_border_width-xl_border_width-2*fudge+1,yr_border_width-yl_border_width-2*fudge+1,nx,ny]