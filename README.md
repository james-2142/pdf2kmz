# pdf2kmz
pdf2kmz is a small collection of python scripts that convert a GeoPDF or GeoTIF map to a kmz file that can be used in Garmin GPS's that support custom maps.

## Dependencies

pdf2kmz requires Python, the GDAP-python bindings and the GDAL scripts to run.

On Windows 10, OSGeo4W versions 2.18, 3.18 & 3.24.1 have been tested to work.

Under Linux, Linux Mint 20.2 has been tested which will require the following installed:
- Python3
- Python3-gdal
- Gdal-bin

## Installation

The scripts don't need to be installed anywhere specific, just download or clone the repository to your local machine.

## How to run

Under Linux, `PYTHONPATH` should be set to the location where `gdal_retile.py` is found, eg:

`export PYTHONPATH=/usr/bin`

To convert a GeoPDF or GeoTIF file to kmz:

`python3 pdf2kmz.py -i INPUT_FILE`

which will output the kmz file in the same directory as `INPUT_FILE`.

There are plenty of options to refine the conversion, including clipping, tiling, scaling and image quality options.  The defaults should be sufficient, though some clipping option should probably be used to remove unwanted areas of the map.

## Usage

```
python3 pdf2kmz.py -h
Usage: pdf2kmz.py \[options\]

Options:
       -i INPUT_FILE |--input=INPUT_FILE : pdf or tif file to convert to kmz
       -o OUT_DIR |--outdir=OUT_DIR      : output directory
       -f|--force                        : force overwrite of output kmz file if it exists
       -v|--verbose                      : increase verbosity
       -h|--help                         : show this help message

Clip options:
       -c|--clip                         : auto clip
       -n|--neatline                     : use embedded neatline to clip
       --srcwin xoff,yoff,xsize,ysize    : subwindow to clip in pixels/lines
       --projwin ulx,uly,lrx,lry         : subwindow to clip in georeferenced coordinates
       -b THRESH|--border THRESH         : border threshold for auto clipping (default=100,0-255)

PDF to TIF conversion options:
       -d DPI|--dpi=DPI                  : tif output resolution (default=250)

TIF to JPEG conversion options:
       -q QUAL |--quality=QUAL           : JPEG quality (default=80)

Tiling options:
       -m NUM|--maxtiles=NUM             : maximum number of tiles (default=100)
       -r RES|--maxtileres=RES           : maximum tile resolution (default=1048576)
       -p PROFILE|--profile=PROFILE      : gps profile to use (default, etrex, montana, monterra, oregon, gpsmap)
       -M|--mintilesize                  : use the smallest (default=largest) tile size within constraints
       -S RATIO|--squareratio=RATIO      : only select candidate tilings that have this ratio or less (default=1.2)

Scaling options:
       -s SCALE|--scale=SCALE            : percentage to scale the image
       -a ALG|--algorithm=ALG            : resampling algorithm (default=lanczos)

Temporary directory options:
       -t TEMP|--tmpdir=TEMP             : temporary directory
       -k|--keep                         : keep temporary files
```

## Running in parallel

While pdf2kmz does not itself run in parallel (it is already very quick), if you have a large number of GeoPDF/GeoTIFs to convert then they can be processed simultaneously.

On Windows use Mparallel and run:

dir /b .\pdf\*.pdf | Mparallel.exe --stdin --pattern "python3 pdf2kmz.py -i .\pdf\{{0}}" --count=2

On Linux we can use xargs:

ls ./pdf/*.pdf | xargs -n 1 -P 2 -I {} python3 pdf2kmz.py -i ./pdf/{}

## Issues

I've only tested this using Vicmap 20k products with my own Garmin eTrex 20x, your mileage may vary with other maps.

The auto-clipping feature `-c` tries to find the outer gridlines of the map and use that to clip.  It works well with the Vicmap products, and may work with other maps.  Clip using the neatline (if available) if this doesn't work is an option.

# License

pdf2kmz is licensed under the MIT License - see [LICENSE](LICENSE)

# Links

* You can find this project here: https://github.com/james-2142/pdf2kmz
* To get OSGeo4W head over to: https://trac.osgeo.org/osgeo4w/
* Download MParallel portable binary at: https://github.com/lordmulder/MParallel/releases/download/1.0.4/mparallel.2016-06-08.bin-win64.zip
* To get Linux Mint goto: https://linuxmint.com/download.php
* An alternative to this project is GarminCustomMaps plugin for QGIS:(https://github.com/NINAnor/GarminCustomMaps
* How to upload you custom maps and technical details from Garmin: https://support.garmin.com/en-AU/?faq=cVuMqGHWaM7wTFWMkPNLN9

