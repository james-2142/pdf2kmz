# pdf2kmz
pdf2kmz is a small collection of python scripts that convert a GeoPDF or GeoTIF map to a kmz file that can be used in Garmin GPS's that support custom maps.

## Dependencies

pdf2kmz requires Python, the GDAP-python bindings and the GDAL scripts to run.

On Windows 10, QGIS Standalone Installer can be used to install the required dependencies.  This is the recommended method. Versions 2.18.18, 3.18.2 & 3.24.1 have been tested to work.

OSGeo4W Network Installer can also be used to install the necessary dependencies if a custom install of QGIS/OSGeo4W is required.

Under Linux, Linux Mint 20.2 has been tested which will require the following installed:
- Python3
- Python3-gdal
- Gdal-bin

## Installation

The scripts don't need to be installed anywhere specific, just download a zip file of the repository or clone it to your local machine.

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
Usage: pdf2kmz.py [options]

Options:
       -i INPUT_FILE |--input=INPUT_FILE : pdf or tif file to convert to kmz
       -o OUT_DIR |--outdir=OUT_DIR      : output directory
       -f|--force                        : force overwrite of output kmz/tif file if it exists
       -v|--verbose                      : increase verbosity
       -h|--help                         : show this help message

Clip options:
       -c|--clip                         : auto clip
       -n|--neatline                     : use embedded neatline to clip
       -N NEATFILE |--nfile=NEATFILE     : use neatline csv file to clip
       --srcwin xoff,yoff,xsize,ysize    : subwindow to clip in pixels/lines
       --projwin ulx,uly,lrx,lry         : subwindow to clip in georeferenced coordinates
       -b THRESH|--border THRESH         : border threshold for auto clipping (default=100,0-255)

PDF to TIF conversion options:
       -d DPI|--dpi=DPI                  : tif output resolution (default=250)
       -C | --convert_to_tif             : only convert PDF to TIF

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

On Windows use `Mparallel.exe` and run:

`dir /b .\pdf\*.pdf | Mparallel.exe --stdin --pattern "python3 pdf2kmz.py -i .\pdf\{{0}}" --count=2`

On Linux we can use `xargs`:

`ls ./pdf/*.pdf | xargs -n 1 -P 2 -I {} python3 pdf2kmz.py -i ./pdf/{}`

## Neatline file format

The neatline file format is a csv that stores a polygon in WKT format to define the area to be clipped.   Below is an example that defines a closed polygon in UTM coordinates.

```
record,wkt
1, "POLYGON ((315295.11 6236035.46, 338376.1 6236459.5, 338613.335 6222603.120, 315562.949 6222181.446, 315295.11 6236035.46))"
```

## Testing

Because I don't want you to get lost, you should test that the generated kmz file displays correctly before you use it in the field.

* Load the kmz into QGIS Desktop.  It will only import the kml file, and will display bounding boxes for all of the tiles.  If you keep the intermediate files `-k` you can also import the image in the `warped` subdirectory.  The bounding boxes from the kml file should overlap the warped image nicely.  You can also use the `QuickMapServices` plugin to load the OSM maps layer.  The features should overlap with the OSM map.

* Load the kmz into Garmins's BaseCamp software and verify that the map is oriented as it should.  You can do this by comparing it to base map or creating a custom map using another method.

* Load the custom map onto you GPS, then zoom and pan until you can see the map.  Verify that it is oriented correctly against the basemap.

Always have a backup navigation method in the field - electronic devices and batteries fail.

## Testing Notes

I've tested this using Vicmap 25k products with BaseCamp and QGIS and with my own Garmin eTrex 20x.  I've tested with the NSW e-Topo 25k products with BaseCamp and QGIS.

The auto-clipping feature `-c` tries to find the outer gridlines of the map and use that to clip.  It works well with the Vicmap and NSW e-Topo products, and may work with other maps.  Clip using the neatline (if available) if this doesn't work.

The Vicmap neatline aligns with the outer gridlines, so works very well at removing whitespace and legends.  The neatline for the NSW e-Topo does not align with the gridlines, and sits well outside, and isn't suitable for clipping.  Use the auto-clipping option or specify one of the alternatives.

The sample Tasmap 50k TIF has been tested in QGIS and BaseCamp and looks ok.  The sample only includes a map, not any legend area, so the auto clip isn't much use.  The TIF also has a nodata value set to 256, which is outside the normal range - I'm unsure the consequences of this apart from the empty areas being white rather than black as with the Vic and NSW maps.

Not all errors are handled gracefully at this stage.

# License

pdf2kmz is licensed under the MIT License - see [LICENSE](LICENSE)

# Links

* You can find this project on [GitHub](https://github.com/james-2142/pdf2kmz)
* Download the QGIS Standalone installer [here](https://www.qgis.org/en/site/forusers/download.html)
* To get OSGeo4W installer head over to their trac [page](https://trac.osgeo.org/osgeo4w/)
* Download MParallel portable binary [here](https://github.com/lordmulder/MParallel/releases/download/1.0.4/mparallel.2016-06-08.bin-win64.zip)
* Download Linux Mint [here](https://linuxmint.com/download.php)
* How to upload your custom maps and technical details from [Garmin](https://support.garmin.com/en-AU/?faq=cVuMqGHWaM7wTFWMkPNLN9)
* NSW Spatial Services Topographic Maps [Six Maps e-Topo](https://maps.six.nsw.gov.au/etopo.html)
* Vicmap Topographic Maps [portal](https://vicmaptopo.land.vic.gov.au/#/discover-map)


