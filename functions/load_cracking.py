import os
from qgis.utils import iface
from image_loader.layer_styles import styles



def loadCracking(file):
    name = os.path.splitext(os.path.basename(file))[0]
    uri = 'file:///{file}?type=csv&delimiter=;&maxFields=10000&detectTypes=yes&wktField=wkt&geomType=Line&crs=EPSG:27700&spatialIndex=no&subsetIndex=no&watchFile=no'.format(file=file)
    layer = iface.addVectorLayer(uri, name, "delimitedtext")
    #apply some formatting here...
    layer.loadNamedStyle(styles.crackStyle)
    return layer
    
    

def testloadCrackingData():
    from image_loader.test import test
    file = os.path.join(test.testFolder,'example2','Spatial Data','Text Files','MFV2_15 Spatial Crack Data.txt')    
    loadCracking(file)
    
    
if __name__ == '__console__':
    testloadCrackingData()
    