import sys

from osgeo import gdal


def find_tiles(xp, xtiles):
    div = 1
    xt = xp
    xtl = -1
    while xt > 1:
        xt = xp // div + (xp % div > 0)
        if xt != xtl:
            xtiles.append(xt)
        div = div + 1
        xtl = xt


def get_tile_size(filename, maxtiles, maxres, sort_dir, square_ratio):
    src = gdal.Open(filename)
    xp = src.RasterXSize
    yp = src.RasterYSize

    xtiles = []
    ytiles = []
    find_tiles(xp, xtiles)
    find_tiles(yp, ytiles)

    cnt = 0
    tiles = []
    for xtile in xtiles:
        xt = xp // xtile + (xp % xtile > 0)
        if xt * xtile < xp:
            sys.exit()

        for ytile in ytiles:
            np = xtile * ytile
            yt = yp // ytile + (yp % ytile > 0)

            if yt * ytile < yp:
                sys.exit()

            if np < maxres and xtile < square_ratio * ytile and ytile < square_ratio * xtile and xt * yt <= maxtiles:
                tiles.append((xt, yt, xt * yt, xtile, ytile, np, xp, yp, xp * yp))

                cnt = cnt + 1

    tiles.sort(key=lambda x: sort_dir * x[5])

    if len(tiles) == 0:
        return None
    else:
        return tiles[0]
