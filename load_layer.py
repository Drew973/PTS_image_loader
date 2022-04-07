
from qgis.core import QgsProject
from qgis.core import QgsRasterLayer,QgsCoordinateReferenceSystem
import processing

from image_loader import group_functions



#groups: groups.groups object
def loadLayer(filePath,layerName,groups,createOverview=False,hide=False,expand=False):
    
    crs = QgsCoordinateReferenceSystem('EPSG:27700')
    layer = QgsRasterLayer(filePath, layerName)
    layer.setCrs(crs)
    
    if createOverview and not layer.dataProvider().hasPyramids():
        print('creating overview')
        layer = createOverView(layer)
        
    group = group_functions.getGroup(groups)
        
    group.addLayer(layer)
        
    QgsProject.instance().addMapLayer(layer,False)#don't immediatly add to legend
    
    node = group.findLayer(layer)
    node.setItemVisibilityChecked(hide)                
    node.setExpanded(expand)
        
    return layer
    



#create pyramid/overviews for faster rendering
def createOverView(layer):
    #layer.dataProvider().buildPyramids()?
    params = { 'CLEAN' : False, 'EXTRA' : '', 'FORMAT' : 1, 'INPUT' : layer, 'LEVELS' : '4', 'RESAMPLING' : 0 }
    #does not create .ovr file with clean=True. bug?
    
    r = processing.run('gdal:overviews',params)
    
    layer2 = QgsRasterLayer(r['OUTPUT'], layer.name())
    layer2.setCrs(layer.crs())
    return layer2