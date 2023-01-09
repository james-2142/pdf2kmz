import os
import zipfile


def genkmz(of, ipath):
    if1 = os.path.join(ipath, 'doc.kml')
    if2 = os.path.join(ipath, 'files')

    zip = zipfile.ZipFile(of, "w")

    arcname = os.path.basename(if1)
    dname = os.path.dirname(if1)
    zip.write(if1, arcname)

    for filename in os.listdir(if2):
        fname = os.path.join(if2, filename)
        pname = os.path.relpath(if2, dname)
        arcname = os.path.join(pname, filename)
        zip.write(fname, arcname)

    zip.close()
