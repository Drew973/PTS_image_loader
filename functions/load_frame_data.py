import os
from qgis.utils import iface
from qgis.core import QgsField
import logging
from PyQt5.QtCore import QVariant



logger = logging.getLogger(__name__)


'''
    treats all fields as strings.
    fileName incorrectly interpreted as date with detectTypes=yes.
    seems to ignore field types when specified with field=name:type(length,precision)
    specify with .csvt?
'''

def loadFrameData(file):
    logger.debug('loadFrameData(%s)',file)
    name = os.path.splitext(os.path.basename(file))[0]
    uri = 'file:///{file}?type=csv&delimiter=;&maxFields=100&detectTypes=no&wktField=wkt&geomType=Polygon&crs=EPSG:27700&spatialIndex=no&subsetIndex=no&watchFile=no'.format(file=file)
    layer = iface.addVectorLayer(uri, name, "delimitedtext")
    #apply some formatting here...don't have style files yet.
    
    #add virtual field with run.
    #regexp_substr("FileName",'MFV\\S*\\s')
    field = QgsField('run', QVariant.String)
    e = "regexp_substr(\"FileName\",'MFV\\\S*\\\s')"
    layer.addExpressionField(e, field)
    return layer
    
    
    
def testLoadFrameData():
    file = r'C:\Users\drew.bennett\Documents\mfv_images\LEEMING DREW\Spatial Data\Text Files\MFV2_01 Spatial Frame Data.txt'
    #better to add file to plugin test folder.    
    loadFrameData(file)
    
if __name__=='__console__':
    testLoadFrameData()