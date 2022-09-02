# -*- coding: utf-8 -*-
"""
Created on Wed Aug 24 10:03:13 2022

@author: Drew.Bennett
"""

from osgeo import gdal,ogr
import os

class imagesInterface:
    
    
    def __init__(self):        
        self.setFile(None)
    
    
    def setFile(self,file):
        driver = ogr.GetDriverByName('GPKG')
        ds = driver.Open(file, 1) # 0 means read-only. 1 means writeable.
        #if ds is None:
         #   raise ValueError('could not open datasource')   
        self._setDataSource(ds)
        
        
    #create or replace geopackage and set file to this.
    def createGeopackage(self,file):
        driver = ogr.GetDriverByName('GPKG')#exists
    
        if driver is None:
            raise KeyError('GPKG driver not found')
        # Remove output shapefile if it already exists
        if os.path.exists(file):
            driver.DeleteDataSource(file)
        driver.CreateDataSource(file)
        
        self._setDataSource(driver.Open(file, 1)) # 0 means read-only. 1 means writeable.
        
        if self.dataSource() is not None:
            layer = self.dataSource().CreateLayer('details', geom_type=ogr.wkbPolygon )
            layer = self.dataSource().GetLayer('details')
        
            fields = [ogr.FieldDefn("file_path", ogr.OFTString),
            ogr.FieldDefn("run", ogr.OFTString),
            ogr.FieldDefn("image_id", ogr.OFTInteger),
            ogr.FieldDefn("name", ogr.OFTString),
            ogr.FieldDefn("groups", ogr.OFTString)
            ]
            layer.CreateFields(fields)#layer.GetLayerDefn()
            layer = None
        
   
    def dataSource(self):
        return self._ds
    
    
    def _setDataSource(self,ds):
        self._ds = ds
    
    
    def addFolder(self,folder):
        pass
        
        
    def addDetails(self,details):
        if self.dataSource() is not None:
            layer = self.dataSource().GetLayer('details')
    
            featureDefn = layer.GetLayerDefn()
            
            for d in details:
                feature = ogr.Feature(featureDefn)
                feature.SetField("run", d['run'])
                feature.SetField("image_id",d['imageId'])
                feature.SetField("name", d['name'])
                feature.SetField("groups", d['groups'])
                feature.SetGeometry(d['boundingBox'])
                layer.CreateFeature(feature)
                
            feature = None
    
    
    def load(self):
        pass
    
    
    
def test():
    dbFile = r'C:\Users\drew.bennett\Documents\image_loader\test.gpkg'

    i = imagesInterface()
    i.createGeopackage(dbFile)
    
    
    
    