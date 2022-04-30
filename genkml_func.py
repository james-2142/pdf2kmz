#!/usr/bin/env python

import os
import fnmatch
try:
	from osgeo import gdal
	from osgeo import ogr
	from osgeo import osr
except:
	import gdal
	import ogr
	import osr

def genkml(ipath,tgt_epsg):
	topo, ext = os.path.splitext(os.path.basename(ipath))

	ver = gdal.__version__
	maj_ver = int(ver.split(".")[0])

	fh = open(ipath + os.sep + "doc.kml",'w')
	fh.write("""<?xml version="1.0" encoding="iso-8859-1"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
<Document>
<name>%s</name>"""
	% topo)

	for filename in fnmatch.filter( os.listdir(ipath), '*.tif'):

		name, ext = os.path.splitext(os.path.basename(filename))

# Thanks to James for the post on Stackexchange for this transform which is licensed under CC BY-SA 2.5 for which the following is modified from.
# https://gis.stackexchange.com/a/201320

		src = gdal.Open(ipath + os.sep + filename)
		xp = src.RasterXSize
		yp = src.RasterYSize
		proj = src.GetProjection()

		ulx, xsize, _, uly, _, ysize  = src.GetGeoTransform()
		lrx = ulx + xp*xsize
		lry = uly + yp*ysize

		src = None

		src_ref = osr.SpatialReference()
		src_ref.ImportFromWkt(proj)

		tgt_ref = osr.SpatialReference()
		if maj_ver >= 3:
			tgt_ref.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)
		tgt_ref.ImportFromEPSG(tgt_epsg)

		coord_transform = osr.CoordinateTransformation(src_ref, tgt_ref)
		w, n, _ = coord_transform.TransformPoint(ulx, uly)
		e, s, _ = coord_transform.TransformPoint(lrx, lry)

		fh.write("""
<Folder>
<name>%s</name>"""
		% name)

		fh.write("""
<GroundOverlay>
<drawOrder>%d</drawOrder>"""
		% 1)

		fh.write("""
<Icon>
<href>files/%s.jpg</href>"""
		% name)

		fh.write("""
</Icon>
<LatLonBox>
<north>%.15g</north>
<south>%.15g</south>
<east>%.15g</east>
<west>%.15g</west>"""
		%( n, s, e, w ) )

		fh.write("""
</LatLonBox>
</GroundOverlay>
</Folder>""" )
		
	fh.write("""
</Document>
</kml>""")
