import os
from image_loader.models.details.image_details import imageDetails
from osgeo import ogr


def addDetails(ds,details):
    if ds is not None:
        layer = ds.GetLayer('details')
        featureDefn = layer.GetLayerDefn()
        for d in details:
            feature = ogr.Feature(featureDefn)
            feature.SetField("run", d['run'])
            feature.SetField("image_id",d['imageId'])
            feature.SetField("name", d['name'])
            feature.SetField("file_path", d['filePath'])
            feature.SetField("groups", str(d['groups']))
            feature.SetGeometry(d['boundingBox'])
            layer.CreateFeature(feature)
        feature = None
    
def test1():
    file = r'C:\Users\drew.bennett\Documents\image_loader\test.gpkg'
    ds = ogr.GetDriverByName('GPKG').Open(file, 1) # 0 means read-only. 1 means writeable.

    data = [{'run':'test','filePath':'path','imageId':0,'name':'test_name','groups':'[]','boundingBox':None}]
    addDetails(ds,data)
    del ds
        
        
def test2():
    file = r'C:\Users\drew.bennett\Documents\image_loader\test.gpkg'
    ds = ogr.GetDriverByName('GPKG').Open(file, 1) # 0 means read-only. 1 means writeable.

    testFolder = r'C:\Users\drew.bennett\Documents\image_loader\mfv_images\LEEMING DREW\TIF Images\MFV2_01\ImageInt'
    tifs = [os.path.join(testFolder,f) for f in os.listdir(testFolder) if os.path.splitext(f)[-1]=='.tif']
    details = [imageDetails(t) for t in tifs]
    addDetails(ds,details)
        
if __name__=='__console__':
    test2()