
from image_loader import image
from image_loader.measure_to_point import measureToPoint

def test():
    f = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\test\inputs\2023-01-20 15h26m34s LCMS Module 1 000000.jpg'
    to = r'C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\test\outputs\0000.tif'
        
    im = image.image(file = f)
    im.startM = 0.1
        
    layer = QgsProject.instance().mapLayersByName('MFV1_021-rutacd-1')[0]
    field = 'Chainage (km)'
    im.startPoint = measureToPoint(layer = layer,field=field , m = im.startM)
    print(im.startPoint)
test()
