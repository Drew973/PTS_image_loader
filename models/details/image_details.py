
import os
import csv
import json

from qgis.core import QgsProject,QgsGeometry
from qgis.core import QgsRasterLayer,QgsCoordinateReferenceSystem

from image_loader.models.details import generate_details
from image_loader.functions import group_functions,raster_extents


'''
    boundingBox : QgsGeometry polygon
    use QgsGeometry.isNull() to test if have bounding box
'''



class imageDetails:
    
    def __init__(self,filePath,run=None,imageId=None,name=None,groups=None,boundingBox=None):
        
        self.filePath = filePath
        
        if run is None:
            run = generate_details.generateRun(filePath)
        self.run = str(run)
           
        if imageId is None:
            imageId = generate_details.generateImageId(filePath)
        self.imageId = int(imageId)
            
        if name is None:
            name = generate_details.generateLayerName(filePath)
        self.name = str(name)
            
        #list
        if groups is None:
            groups = generate_details.generateGroups2(self.run,generate_details.generateType(filePath))#str
            
        if isinstance(groups,str):
            groups = json.loads(groups)
            
        self.groups = list(groups)
   
        if boundingBox is None:
            boundingBox = QgsGeometry()
        self.boundingBox = boundingBox
        #isinstance(d[0]['boundingBox'],QgsGeometry)
    
    
    
    def findExtents(self):
        if self.boundingBox.isNull():
            self.boundingBox = raster_extents.rasterExtents(self.filePath)
    
    
    def __getitem__ (self,key):
        if key == 'filePath':
            return self.filePath
            
        if key == 'run':
            return self.run
       
        if key == 'imageId':
            return self.imageId   
    
        if key == 'name':
            return self.name   

        if key == 'groups':
            return self.groups
        
        if key == 'groupsString':
            return json.dumps(self.groups)       
        
        if key =='boundingBox':
            return self.boundingBox

        if key =='wkt':
            return self.boundingBox.asWkt()

        raise KeyError('imageDetails has no item {0}'.format(key))



    def __eq__(self,other):
        return self.filePath==other.filePath and self.layerName==other.self.layerName and self.groups==other.groups and self.run==other.run and self.imageId==other.imageId
    
 
    
    def __repr__(self):
        d = {'filePath':self.filePath,'run':self.run,'imageId':self.imageId,'name':self.name,'groups':self.groups}
        return '<imageDetails:{}>'.format(d)



    #load layer. expand expands group. show renders image.
    def load(self,show=True,expand=False,crs=QgsCoordinateReferenceSystem('EPSG:27700')):
        layer = QgsRasterLayer(self.filePath, self.name)
        layer.setCrs(crs)
        
        group = group_functions.getGroup(self.groups)
        group.addLayer(layer)
                
        QgsProject.instance().addMapLayer(layer,False)#don't immediatly add to legend
            
        node = group.findLayer(layer)
        node.setItemVisibilityChecked(show)
        node.setExpanded(expand)
        return layer



def getFiles(folder,exts=None):
    for root, dirs, files in os.walk(folder, topdown=False):
        for f in files:
            if os.path.splitext(f)[1] in exts or exts is None:
                yield os.path.normpath(os.path.join(root,f))
                
     
        
     
 #lookup value from dict, returning default if not present
def find(d,k,default=None):
    if k in d:
        return d[k]
    return default



#column named filepath. optional columns:imageId,name,groups
#names are case insensitive.
def fromCsv(file):
    folder = os.path.dirname(file)
    
    with open(file,'r',encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [name.lower().replace('_','') for name in reader.fieldnames]#lower case keys/fieldnames                 
        for d in reader:
            
            if os.path.isabs(d['filepath']):
                filePath = d['filepath']
            else:
                filePath = os.path.join(folder,d['filepath'])
             
            yield imageDetails(filePath=filePath,run=find(d,'runid'),imageId=find(d,'imageid'),name=find(d,'name'),
                               groups=find(d,'groups'),boundingBox=find(d,'extents'))


    
        

