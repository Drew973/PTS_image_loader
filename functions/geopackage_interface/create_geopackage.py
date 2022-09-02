from osgeo import gdal,ogr
import os

gdal.UseExceptions()#raise exceptions where problem

#working with geopackage from qgis tricky.
#might be easier to go directly through gdal.

'''
create geopackage.replaces existing file.

'''
def createGeopackage(file):
    driver = ogr.GetDriverByName('GPKG')#exists

    if driver is None:
        raise KeyError('GPKG driver not found')
    # Remove output shapefile if it already exists
    if os.path.exists(file):
        driver.DeleteDataSource(file)
    driver.CreateDataSource(file)
    
    ds = driver.Open(file, 1) # 0 means read-only. 1 means writeable.
    if ds is None:
        raise ValueError('could not open datasource "{file}"'.format(file=file))
    
    layer = ds.CreateLayer('details', geom_type=ogr.wkbPolygon )
    layer = ds.GetLayer('details')

    fields = [ogr.FieldDefn("file_path", ogr.OFTString),
    ogr.FieldDefn("load", ogr.OFSTBoolean),
    ogr.FieldDefn("run", ogr.OFTString),
    ogr.FieldDefn("image_id", ogr.OFTInteger),
    ogr.FieldDefn("name", ogr.OFTString),
    ogr.FieldDefn("groups", ogr.OFTString)
    ]
    layer.CreateFields(fields)#layer.GetLayerDefn()
    layer = None
    return ds

def test():    
    dbFile = r'C:\Users\drew.bennett\Documents\image_loader\test.gpkg'
    createGeopackage(dbFile)

if __name__=='__console__':
    test()    

