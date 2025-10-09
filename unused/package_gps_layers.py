from PyQt5.QtWidgets import QFileDialog
from image_loader.backend.gps_functions import parseCsv
import os
import re



def packageFiles(files):
    for f in files:
        name = os.path.splitext(os.path.basename(f))[0]
        print(name)
        for m,lat,lon,alt in parseCsv(f):
            pass    



urls = QFileDialog.getOpenFileUrls(caption = "GPS files",filter = "rutacd csv (*rutacd*.csv);;csv (*.csv);;anpp (*.anpp)")#QUrl
files = [u.toLocalFile() for u in urls[0]]

packageFiles(files)

#frame,start chain, end chain, linestring.