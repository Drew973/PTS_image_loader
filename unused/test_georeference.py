
from image_loader.georeference import georeferenceSubprocess


def test():
    from qgis.utils import iface
    PIXELS = 1038
    LINES = 1250

    gcps = [ gdal.GCP(354936.334,322907.213,0,0,0),#tl
            gdal.GCP(354937.341,322903.420,0,PIXELS,0),#tr
            gdal.GCP(354931.769,322906.206,0,0,LINES),#bl
            gdal.GCP(354932.608,322902.245,0,PIXELS,LINES)]

    #f = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\test\inputs\2023-01-20 15h26m34s LCMS Module 1 000002.jpg'
    f = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\test\inputs\2023-01-20 15h26m34s LCMS Module 1 000001.jpg'

   # georeference(f,gcps)
    #ds = None

    print('result',georeferenceSubprocess(f,gcps))

    iface.addRasterLayer(f,str('test'))

if __name__ == '__console__':
    test()