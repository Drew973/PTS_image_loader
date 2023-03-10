# -*- coding: utf-8 -*-
"""
Created on Thu Mar  9 14:38:37 2023

@author: Drew.Bennett
"""


#from qgis.core import QgsPointXY#QgsRasterLayer,QgsProject,QgsPoint#


WIDTH = 4.0
PIXELS = 1038
LINES = 1250
#LENGTH = 5.0


class image:
    
    def __init__(self,imageId=-1,file='',georeferenced='',groups=[],run=''):
        self.imageId = imageId
        self.file = file
        self.georeferenced = georeferenced
        self.groups = groups
        self.run = run 
        
    
    
    #remake georeferenced raster    
    def remake(self,startPoint,endPoint):
        pass
    
    #laod into QGIS
    def load(self):
        pass
    
    #self<other
    def __lt__(self,other):
        
        if self.run<other.run:
            return True
        
        if self.imageId<other.imageId:
            return True
        
     #   if self.file<other.file:
          #  return True
        #
        return False
        
        
      #  return self.run <= other.run and self.imageId<other.imageId
        
        
    def __eq__(self,other):
        return self.run == other.run and self.imageId == other.imageId and self.file == other.file
    
    
    def __repr__(self):
        d = {'imageId':self.imageId,'run':self.run,'file':self.file,'georeferenced':self.georeferenced,'groups':self.groups}
        return 'image:'+str(d)
    
    
#calculate GCPs from 

#startPoint:QgsPoint,endPoint:Qgspoint -> gdal.GCP
def GCPs(startPoint,endPoint):
    pass




import unittest


class testImage(unittest.TestCase):
        
    def setUp(self):
        pass

    def testSort(self):
        images = [image(run = 'a',imageId = 10),
                  image(run = 'a',imageId = 1),
                  image(run = 'b',imageId = 11)]
       
        images2 = sorted(images)
        print(images2)
     #   for i in images2:
     #       print(i.run)


if __name__ in ['__console__','__main__']:
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(testImage)
    unittest.TextTestRunner().run(suite)