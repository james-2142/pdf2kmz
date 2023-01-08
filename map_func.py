import sys
from PIL import Image
import numpy as np

def find_map_extent(ifile,fudge):

	Image.MAX_IMAGE_PIXELS = None
	img = Image.open(ifile).convert("L")
	arr = 255 - np.array(img)
	
	ny = np.size(arr,0)
	nx = np.size(arr,1)

	ave = -1
	yu = -1
	for yp in range(0,int(ny/2)):
		ave_t = np.average(arr[yp,:])
		if (ave_t >= ave ):
			ave = ave_t
			yu = yp

	ave = -1
	yl = -1
	for yp in reversed(range(int(ny/2),ny)):
		ave_t = np.average(arr[yp,:])
		if (ave_t >= ave ):
			ave = ave_t
			yl = yp

	ave = -1
	xl = -1
	for xp in range(0,int(nx/2)):
		ave_t = np.average(arr[:,xp])
		if (ave_t >= ave ):
			ave = ave_t
			xl = xp

	ave = -1
	xr = -1
	for xp in reversed(range(int(nx/2),nx)):
		ave_t = np.average(arr[:,xp])
		if (ave_t >= ave ):
			ave = ave_t
			xr = xp
		
	return [xl+fudge,yu+fudge,xr-xl-2*fudge+1,yl-yu-2*fudge+1]

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
