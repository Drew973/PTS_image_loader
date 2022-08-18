import os




from qgis.utils import iface
import logging
logger = logging.getLogger(__name__)


def loadFrameData(file):
    logger.debug('loadFrameData(%s)',file)
    name = os.path.splitext(os.path.basename(file))[0]
    uri = 'file:///{file}?type=csv&delimiter=;&maxFields=10000&detectTypes=yes&wktField=wkt&geomType=Polygon&crs=EPSG:27700&spatialIndex=no&subsetIndex=no&watchFile=no'.format(file=file)
    layer = iface.addVectorLayer(uri, name, "delimitedtext")
    #apply some formatting here...
    return layer
    
    
def testLoadFrameData():
    file = r'C:\Users\drew.bennett\Documents\mfv_images\LEEMING DREW\Spatial Data\Text Files\MFV2_01 Spatial Frame Data.txt'
    #better to add file to plugin test folder.
    
    
    loadFrameData(file)