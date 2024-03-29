#!/usr/bin/env python3

from __future__ import print_function

import csv
import fnmatch
import getopt
import os
import shutil
import sys
import tempfile

import numpy as np
from osgeo import gdal
from osgeo_utils import gdal_retile

import genkml_func
import genkmz_func
import map_func
import tile_func


# temp directory
def create_tempdir(prefix, bdir):
    dprefix = prefix + "."
    tempd = tempfile.mkdtemp(prefix=dprefix, dir=bdir)
    return tempd


# cleanup temp directory
def cleanup_tempdir(tempd, keep):
    if not keep:
        shutil.rmtree(tempd)


# gdalwarp
def gdalwarp(ifile, ofile, nodata):
    src = gdal.Open(ifile)
    # EPSG:54004 == EPSG:3395
    opt = gdal.WarpOptions(dstSRS="EPSG:3395", resampleAlg="near", dstNodata=nodata)
    gdal.Warp(ofile, src, options=opt)


# gdal_retile
def gdalretile(ifile, opath, xps, yps):
    retile_argv = ["gdal_retile.py", "-q", "-ps", str(xps), str(yps), "-targetDir", opath, ifile]
    if 'osgeo_utils.gdal_retile' in sys.modules:
        gdal_retile.main(retile_argv)
    else:
        gdal_retile(retile_argv)


# tif2jpg
def tif2jpg(ipath, opath, maxsize):
    gdal.SetConfigOption("GDAL_PAM_ENABLED", "NO")
    opt = gdal.TranslateOptions(options="-of JPEG -co QUALITY=" + str(JPEG_QUALITY))
    for filename in fnmatch.filter(os.listdir(ipath), '*.tif'):
        ifile = ipath + os.sep + filename
        name, ext = os.path.splitext(os.path.basename(filename))
        ofile = opath + os.sep + name + ".jpg"
        src = gdal.Open(ifile)
        gdal.Translate(ofile, src, options=opt)

        fsize = os.path.getsize(ofile)
        if fsize > MAX_JPEG_SIZE:
            print("WARNING: jpeg tile larger than MAX_JPEG_SIZE: %s %d" % (os.path.basename(ofile), fsize))


# clip
def clip(ifile, ofile, xoff, yoff, xsize, ysize, proj):
    if proj:
        opt_str = "-projwin "
    else:
        opt_str = "-srcwin "
    opt_str += str(xoff) + " " + str(yoff) + " " + str(xsize) + " " + str(ysize) + " -of GTiff"
    opt = gdal.TranslateOptions(options=opt_str)

    src = gdal.Open(ifile)
    gdal.Translate(ofile, src, options=opt)


def clipbycutline(ifile, ofile, tempd, neatline):
    ds = gdal.Open(ifile)

    if not neatline:
        neatline = ds.GetMetadata()['NEATLINE']
        cutline = tempd + os.sep + "cutline.csv"
        header = ['record', 'wkt']
        row = [1, "%s" % neatline]

        with open(cutline, 'w', newline='') as fh:
            writer = csv.writer(fh)
            writer.writerow(header)
            writer.writerow(row)
    else:
        cutline = neatline

    opt = gdal.WarpOptions(options="-crop_to_cutline -cutline \"%s\"" % cutline)
    gdal.PushErrorHandler('CPLQuietErrorHandler')
    gdal.Warp(ofile, ds, options=opt)
    gdal.PopErrorHandler()


# pdf2tif
def pdf2tif(ifile, ofile):
    gdal.SetConfigOption("GDAL_PDF_DPI", str(GDAL_PDF_DPI))
    gdal.SetConfigOption("GDAL_SWATH_SIZE", "1000000000")

    src = gdal.Open(ifile)
    obj = gdal.Translate(ofile, src)
    del obj


# gdalscale
def gdalscale(ifile, ofile, scale, resample_alg):
    opt_str = "-outsize %d%% %d%% -scale -r %s" % (scale, scale, resample_alg)
    opt = gdal.TranslateOptions(options=opt_str)

    src = gdal.Open(ifile)
    gdal.Translate(ofile, src, options=opt)


# remove_rotation
def remove_rotation(ifile, ofile):
    src = gdal.Open(ifile)
    gdal.Warp(ofile, src)


def Usage():
    print("Usage: pdf2kmz.py [options]")
    print("")
    print("Options:")
    print("       -i INPUT_FILE |--input=INPUT_FILE : pdf or tif file to convert to kmz")
    print("       -o OUT_DIR |--outdir=OUT_DIR      : output directory")
    print("       -f | --force                      : force overwrite of output kmz/tif file if it exists")
    print("       -v | --verbose                    : increase verbosity")
    print("       -h | --help                       : show this help message")
    print("")
    print("Clip options:")
    print("       -c | --clip                       : auto clip")
    print("       -n | --neatline                   : use embedded neatline to clip")
    print("       -N NEATFILE |--nfile=NEATFILE     : use neatline csv file to clip")
    print("       --srcwin xoff,yoff,xsize,ysize    : subwindow to clip in pixels/lines")
    print("       --projwin ulx,uly,lrx,lry         : subwindow to clip in georeferenced coordinates")
    print("       -b PIXELS |--border PIXELS        : additional pixels to remove when auto clipping (default=5)")
    print("       -B PIXELS | -black-border=PIXELS  : additional pixels to remove when clipping the black border (default=5)")
    print("")
    print("PDF to TIF conversion options:")
    print("       -d DPI |--dpi=DPI                 : tif output resolution (default=250)")
    print("       -C | --convert_to_tif             : only convert PDF to TIF")
    print("")
    print("TIF to JPEG conversion options:")
    print("       -q QUAL | --quality=QUAL          : JPEG quality (default=80)")
    print("")
    print("Tiling options:")
    print("       -m NUM | --maxtiles=NUM           : maximum number of tiles (default=100)")
    print("       -r RES | --maxtileres=RES         : maximum tile resolution (default=1048576)")
    print("       -p PROFILE | --profile=PROFILE    : gps profile to use (default, etrex, montana, monterra, oregon, gpsmap)")
    print("       -M | --mintilesize                : use the smallest (default=largest) tile size within constraints")
    print("       -S RATIO | --squareratio=RATIO    : only select candidate tilings that have this ratio or less (default=1.2)")
    print("")
    print("Scaling options:")
    print("       -s SCALE | --scale=SCALE          : percentage to scale the image")
    print("       -a ALG | --algorithm=ALG          : resampling algorithm (default=lanczos)")
    print("")
    print("Warp options:")
    print("       -R | --remove-nodata              : remove nodata attribute")
    print("")
    print("Temporary directory options:")
    print("       -t TEMP | --tmpdir=TEMP           : temporary directory")
    print("       -k | --keep                       : keep temporary files")
    print("")


def main(args=None):
    global GDAL_PDF_DPI
    global JPEG_QUALITY
    global MAX_TILES
    global MAX_TILE_RES
    global IMAGE_SCALE
    global RESAMPLE_ALG
    global SORT_DIR
    global SQUARE_RATIO
    global MAX_JPEG_SIZE
    global CLIP_OFFSET
    global BORDER_OFFSET
    global WARP_NODATA

    Ifile = False
    Odir = False
    Tdir = False
    Nfile = False
    Force = False
    Keep = False
    AutoClip = False
    Neatline = False
    Srcwin = False
    Projwin = False
    Verbose = False
    Tiles = False
    Profile = False
    Scale = False
    Algorithm = False
    odir = ""
    tdir = ""
    nfile = None
    btmpdir = None
    Tif = False

    gps_profiles = {'default': 100, 'etrex': 100, 'montana': 500, 'monterra': 99, 'oregon': 500, 'gpsmap': 500}
    resample_mthds = ["nearest", "average", "rms", "bilinear", "cubic", "cupicspline", "lanczos", "mode"]

    try:
        short_args = "-hi:o:fkd:q:cnm:r:vp:s:a:t:MS:b:N:CB:R"
        long_args = ["help", "input=", "outdir=", "force", "keep", "dpi=", "quality=", "clip", "neatline", "maxtiles=",
                     "maxtileres=", "verbose", "profile=", "scale=", "algorithm=", "tmpdir=", "mintilesize",
                     "squareratio=", "border=", "srcwin=", "projwin=", "nfile=", "convert_to_tif", "black-border=",
                     "remove-nodata"]
        opts, args = getopt.getopt(sys.argv[1:], short_args, long_args)
    except getopt.GetoptError as err:
        Usage()
        print(err)
        return 1

    for o, a in opts:
        if o in ("-h", "--help"):
            Usage()
            return 0
        elif o in ("-i", "--input"):
            Ifile = True
            ifile = a
        elif o in ("-o", "--outdir"):
            Odir = True
            odir = a
        elif o in ("-t", "--tmpdir"):
            Tdir = True
            tdir = a
        elif o in ("-N", "--neatlinefile"):
            Nfile = True
            nfile = a
        elif o in ("-f", "--force"):
            Force = True
        elif o in ("-k", "--keep"):
            Keep = True
        elif o in ("-C", "--convert_to_tif"):
            Tif = True
        elif o in ("-d", "--dpi"):
            try:
                GDAL_PDF_DPI = int(a)
            except:
                Usage()
                print("dpi must be an integer")
                return 1
        elif o in ("-q", "--quality"):
            try:
                JPEG_QUALITY = int(a)
                if JPEG_QUALITY < 0 or JPEG_QUALITY > 100:
                    Usage()
                    print("quality must be between 0 and 100")
                    return 1
            except:
                Usage()
                print("quality must be an integer")
                return 1
        elif o in ("-c", "--clip"):
            AutoClip = True
        elif o in ("-n", "--neatline"):
            Neatline = True
        elif o == "--srcwin":
            Srcwin = True
            try:
                win = np.array(a.split(","), int)
            except:
                Usage()
                print("srcwin must be an integer")
                return 1
            if len(win) != 4:
                Usage()
                print("srcwin has 4 arguments")
                return 1
            if any(win < 0):
                Usage()
                print("srcwin arguments must be 0 or greater")
                return 1
        elif o == "--projwin":
            Projwin = True
            try:
                win = np.array(a.split(","), float)
            except:
                Usage()
                print("projwin must be a float")
                return 1
            if len(win) != 4:
                Usage()
                print("projwin has 4 arguments")
                return 1
            if any(win < 0):
                Usage()
                print("projwin arguments must be 0 or greater")
                return 1
        elif o in ("-m", "--maxtiles"):
            Tiles = True
            MAX_TILES = int(a)
        elif o in ("-r", "--maxtileres"):
            MAX_TILE_RES = int(a)
        elif o in ("-v", "--verbose"):
            Verbose = True
        elif o in ("-p", "--profile"):
            Profile = True
            if a in gps_profiles:
                MAX_TILES = int(gps_profiles[a])
            else:
                Usage()
                print("unknown gps profile")
                print("supported profiles are: %s" % list(gps_profiles.keys()))
                return 1
        elif o in ("-s", "--scale"):
            Scale = True
            try:
                IMAGE_SCALE = int(a)
                if IMAGE_SCALE < 0:
                    Usage()
                    print("quality must be greater than 0")
                    return 1
            except:
                Usage()
                print("image scale must be an integer")
                return 1
        elif o in ("-a", "--algorithm"):
            Algorithm = True
            RESAMPLE_ALG = a
        elif o in ("-M", "--mintilesize"):
            SORT_DIR = 1
        elif o in ("-S", "--squareratio"):
            try:
                SQUARE_RATIO = float(a)
            except:
                Usage()
                print("squareratio must be a float")
                return 1
        elif o in ("-b", "--border"):
            try:
                CLIP_OFFSET = int(a)
                if CLIP_OFFSET < 0:
                    Usage()
                    print("auto clip border offset must be greater than 0")
                    return 1
            except:
                Usage()
                print("auto clip border offset must be an integer")
                return 1
        elif o in ("-B", "--black-border"):
            try:
                BORDER_OFFSET = int(a)
                if BORDER_OFFSET < 0:
                    Usage()
                    print("black border offset must be greater than 0")
                    return 1
            except:
                Usage()
                print("black border offset must be an integer")
                return 1
        elif o in ("-R", "--remove-nodata"):
            WARP_NODATA = "None"
        else:
            Usage()
            print("unknown option", o, a)
            return 1

    if not Ifile:
        Usage()
        print("option [-i|--input] required")
        return 1
    else:
        if Verbose:
            print("Input file = %s" % ifile)

    if Nfile:
        if not os.path.isfile(nfile):
            Usage()
            print("neatline file does not exist: %s" % nfile)
            return 1

    if (AutoClip and Srcwin) or (AutoClip and Projwin) or (Srcwin and Projwin):
        Usage()
        print("only specify one clipping option")
        return 1

    if (Neatline and Srcwin) or (Neatline and Projwin) or (Neatline and AutoClip):
        Usage()
        print("only specify one clipping option")
        return 1

    if (Nfile and Srcwin) or (Nfile and Projwin) or (Nfile and Neatline) or (Nfile and AutoClip):
        Usage()
        print("only specify one clipping option")
        return 1

    if Tiles and Profile:
        Usage()
        print("gps profile cannot be specified with maxtiles")
        return 1

    if Algorithm:
        if not RESAMPLE_ALG in resample_mthds:
            Usage()
            print("invalid resampling algorithm %s" % resample_mthds)
            return 1

    if not Odir:
        name, ext = os.path.splitext(os.path.basename(ifile))
        odir = os.path.dirname(os.path.realpath(ifile))
    else:
        if os.path.isdir(odir):
            name, ext = os.path.splitext(os.path.basename(ifile))
        else:
            try:
                os.mkdir(odir)
                name, ext = os.path.splitext(os.path.basename(ifile))
            except:
                Usage()
                print("cannot create output directory")
                return 1

    if Verbose:
        print("Output directory = %s" % odir)

    if not Tif:
        kmzfile = odir + os.sep + name + ".kmz"
        if os.path.exists(kmzfile):
            if os.path.isfile(kmzfile):
                if not Force:
                    Usage()
                    print("output file %s exists, -f to force overwrite" % kmzfile)
                    return 1
            else:
                Usage()
                print("output file %s exists but is not a regular file" % kmzfile)
                return 1

    if Tif:
        ofile = odir + os.sep + name + ".tif"
        if os.path.exists(ofile):
            if os.path.isfile(ofile):
                if not Force:
                    Usage()
                    print("output file %s exists, -f to force overwrite" % ofile)
                    return 1
            else:
                Usage()
                print("output file %s exists but is not a regular file" % ofile)
                return 1
    else:
        if Tdir:
            if os.path.isdir(tdir):
                btmpdir = os.path.realpath(tdir)
            else:
                Usage()
                print("temporary directory base is not an existing directory")
                return 1

        ""
        tempd = create_tempdir(name, btmpdir)

        if Verbose:
            print("Temporary directory: %s" % tempd)

    if ext.lower() == ".pdf":
        if not Tif:
            path = tempd + os.sep + "tif"
            if not os.path.isdir(path):
                os.mkdir(path)
            ofile = path + os.sep + name + ".tif"

        if Verbose:
            print("Coverting input pdf to tif with dpi = %d" % GDAL_PDF_DPI)

        pdf2tif(ifile, ofile)

        if Tif:
            return 1
    elif ext.lower() in (".tif", ".tiff"):
        if Verbose:
            if Tif:
                print("Input file already in tif format: %s" % ifile)
                return 1
            else:
                print("Input file in tif format: %s" % ifile)
        ofile = ifile

    if AutoClip:
        ifile = ofile
        path = tempd + os.sep + "clipped"
        if not os.path.isdir(path):
            os.mkdir(path)
        name, ext = os.path.splitext(os.path.basename(ifile))
        ofile = path + os.sep + name + ext

        if Verbose:
            print("Using auto clip with offset=%d" % CLIP_OFFSET)

        xoff, yoff, xsize, ysize = map_func.find_map_extent(ifile, CLIP_OFFSET)

        if Verbose:
            print("auto clip offset (%d,%d) and size (%d,%d)" % (xoff, yoff, xsize, ysize))

        clip(ifile, ofile, xoff, yoff, xsize, ysize, False)
    elif Srcwin:
        ifile = ofile
        path = tempd + os.sep + "clipped"
        if not os.path.isdir(path):
            os.mkdir(path)
        name, ext = os.path.splitext(os.path.basename(ifile))
        ofile = path + os.sep + name + ext
        xoff, yoff, xsize, ysize = win

        if Verbose:
            if Projwin:
                print("clip using projwin offset (%d %d) and size (%d %d)" % (xoff, yoff, xsize, ysize))
            else:
                print("clip using srcwin offset (%d %d) and size (%d %d)" % (xoff, yoff, xsize, ysize))

        clip(ifile, ofile, xoff, yoff, xsize, ysize, Projwin)

    if Projwin:
        ifile = ofile
        path = tempd + os.sep + "rotated"
        if not os.path.isdir(path):
            os.mkdir(path)
        ofile = path + os.sep + name + ".tif"

        if Verbose:
            print("Removing rotation from input file")

        remove_rotation(ifile, ofile)

    if Neatline:
        ifile = ofile
        path = tempd + os.sep + "clipped"
        if not os.path.isdir(path):
            os.mkdir(path)
        name, ext = os.path.splitext(os.path.basename(ifile))
        ofile = path + os.sep + name + ext

        if Verbose:
            print("Using neatline to clip")

        clipbycutline(ifile, ofile, tempd, nfile)
    elif Nfile:
        ifile = ofile
        path = tempd + os.sep + "clipped"
        if not os.path.isdir(path):
            os.mkdir(path)
        name, ext = os.path.splitext(os.path.basename(ifile))
        ofile = path + os.sep + name + ext

        if Verbose:
            print("Using neatline csv file to clip")

        clipbycutline(ifile, ofile, tempd, nfile)
    elif Projwin:
        ifile = ofile
        path = tempd + os.sep + "clipped"
        if not os.path.isdir(path):
            os.mkdir(path)
        name, ext = os.path.splitext(os.path.basename(ifile))
        ofile = path + os.sep + name + ext
        xoff, yoff, xsize, ysize = win

        if Verbose:
            if Projwin:
                print("clip using projwin offset (%d %d) and size (%d %d)" % (xoff, yoff, xsize, ysize))
            else:
                print("clip using srcwin offset (%d %d) and size (%d %d)" % (xoff, yoff, xsize, ysize))

        clip(ifile, ofile, xoff, yoff, xsize, ysize, Projwin)

    ifile = ofile
    path = tempd + os.sep + "warped"
    if not os.path.isdir(path):
        os.mkdir(path)
    name, ext = os.path.splitext(os.path.basename(ifile))
    ofile = path + os.sep + name + ext

    if Verbose:
        print("Running gdalwarp")

    gdalwarp(ifile, ofile, WARP_NODATA)

    xoff, yoff, xsize, ysize, nx, ny = map_func.find_map_trim(ofile, 0, BORDER_OFFSET)
    if xoff - BORDER_OFFSET != 0 or yoff - BORDER_OFFSET != 0 or xoff + xsize + BORDER_OFFSET - 1 != nx or yoff + ysize + BORDER_OFFSET - 1 != ny:
        ifile = ofile
        path = tempd + os.sep + "border"
        if not os.path.isdir(path):
            os.mkdir(path)
        name, ext = os.path.splitext(os.path.basename(ifile))
        ofile = path + os.sep + name + ext

        if Verbose:
            print("auto clip black border (%d,%d) and size (%d,%d) on image (%d,%d)" % (xoff, yoff, xsize, ysize, nx, ny))

        clip(ifile, ofile, xoff, yoff, xsize, ysize, False)
    else:
        if Verbose:
            print("a black border does not exist - skipping")

    if Scale:
        ifile = ofile
        path = tempd + os.sep + "rescaled"
        if not os.path.isdir(path):
            os.mkdir(path)

        name, ext = os.path.splitext(os.path.basename(ifile))
        ofile = path + os.sep + name + ext

        if Verbose:
            print("Rescaling image with scale = %s%% and resampling method = %s" % (IMAGE_SCALE, RESAMPLE_ALG))

        gdalscale(ifile, ofile, IMAGE_SCALE, RESAMPLE_ALG)

    path = tempd + os.sep + "tiled"
    if not os.path.isdir(path):
        os.mkdir(path)

    if Verbose:
        print("Maximum number of tiles = %d" % MAX_TILES)
        print("Maximum tile resolution = %d" % MAX_TILE_RES)

    ts = tile_func.get_tile_size(ofile, MAX_TILES, MAX_TILE_RES, SORT_DIR, SQUARE_RATIO)
    if ts == None:
        Usage()
        print("tiling not found")
        cleanup_tempdir(tempd, Keep)
        return 1
    else:
        if Verbose:
            print("retiling with %dx%d tile" % (ts[3], ts[4]))
        gdalretile(ofile, path, ts[3], ts[4])

        if Verbose:
            print("retiled with %d tiles (%dx%d)" % (ts[2], ts[0], ts[1]))

    opath = path + os.sep + "files"
    if not os.path.isdir(opath):
        os.mkdir(opath)

    if Verbose:
        print("Converting tiled tif files to jpeg with a quality of %s" % JPEG_QUALITY)

    tif2jpg(path, opath, MAX_JPEG_SIZE)

    if Verbose:
        print("Generating kml file")

    genkml_func.genkml(path, 4326)

    if Verbose:
        print("Generating kmz = %s" % kmzfile)

    genkmz_func.genkmz(kmzfile, path)

    cleanup_tempdir(tempd, Keep)

    return 0


# Global vars
###############################################################################
# Copy and paste from gdal_retile.py - see LICENSE file
###############################################################################
Verbose = False
Quiet = False
CreateOptions = []
Names = []
TileWidth = 256
TileHeight = 256
Overlap = 0
Format = 'GTiff'
BandType = None
Driver = None
Extension = None
MemDriver = None
TileIndexFieldName = 'location'
TileIndexName = None
TileIndexDriverTyp = "Memory"
CsvDelimiter = ";"
CsvFileName = None
Source_SRS = None
TargetDir = None
ResamplingMethod = gdal.GRA_NearestNeighbour
Levels = 0
PyramidOnly = False
LastRowIndx = -1
UseDirForEachRow = False
###############################################################################

# Global vars
GDAL_PDF_DPI = 250
JPEG_QUALITY = 80
MAX_TILES = 100
MAX_TILE_RES = 1048576
IMAGE_SCALE = 100
RESAMPLE_ALG = "lanczos"
SORT_DIR = -1
SQUARE_RATIO = 1.2
MAX_JPEG_SIZE = 3000000
CLIP_OFFSET = 5
BORDER_OFFSET = 5
WARP_NODATA = None

if __name__ == '__main__':
    sys.exit(main(sys.argv))
