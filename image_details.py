import os
from qgis.core import QgsRasterLayer,QgsCoordinateReferenceSystem
import processing



    

class imageDetails:
    
    def __init__(self,run,imageId,filePath,layerName='',groups=[]):
        self.filePath = filePath
        self.layerName = layerName #string name for layer
        self.groups = groups   #list of strings representing group for layer
        self.run = run
        self.imageId = imageId

    
    def toLayer(self,createOverview=False):
        crs = QgsCoordinateReferenceSystem('EPSG:27700')
        layer = QgsRasterLayer(self.filePath, self.layerName)
        layer.setCrs(crs)
    
        if createOverview and not layer.dataProvider().hasPyramids():
            print('creating overview')
            layer = createOverView(layer)
        
        return layer
    
    
    def __eq__(self,other):
        return self.filePath==other.filePath and self.layerName==other.self.layerName and self.groups==other.groups and self.run==other.run and self.imageId==other.imageId
    
    #self<other
    #order by run,imageId
    def __lt__(self,other):
        if self.run<other.run:
            return True
    
        if self.imageId<other.imageId:
            return True
    
    
    
def imageDetailsfromPath(filePath,folder,createOverview=True):
    filePath = filePath
    name = generateLayerName(filePath)
    g = generateGroups(filePath,folder)
    return imageDetails(filePath,name,g,createOverview)
    
    
def getFiles(folder,exts=None):
    for root, dirs, files in os.walk(folder, topdown=False):
        for f in files:
            if os.path.splitext(f)[1] in exts or exts is None:
                yield os.path.join(root,f)
            



#name for layer
def generateLayerName(filePath):
    return os.path.splitext(os.path.basename(filePath))[0]
    
    
#list of strings representing group hierarchy.
#same as folder hierarchy
def generateGroups(file,folder):
    folder = os.path.dirname(folder)
    file = os.path.dirname(file)
    
    p = os.path.relpath(file,folder)
    
    return p.split(os.sep)


#[{filePath,layerName,groups}] for each tif in folder.
def detailsFromFolder(folder,createOverview=True):
    return [imageDetailsfromPath(f,folder,createOverview) for f in getFiles(folder,'.tif')]


#create pyramid/overviews for faster rendering
def createOverView(layer):
    #layer.dataProvider().buildPyramids()?
    params = { 'CLEAN' : False, 'EXTRA' : '', 'FORMAT' : 1, 'INPUT' : layer, 'LEVELS' : '4', 'RESAMPLING' : 0 }
    #does not create .ovr file with clean=True. bug?
    
    r = processing.run('gdal:overviews',params)
    
    layer2 = QgsRasterLayer(r['OUTPUT'], layer.name())
    layer2.setCrs(layer.crs())
    return layer2
    
    

