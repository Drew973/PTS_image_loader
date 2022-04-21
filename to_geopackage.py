
#db Will be created if it doesnt exist
def toGeopackage(file,db):
    #table = 'images' #Adjust this line to change how the output rasters are named
    table = os.path.splitext(os.path.basename(file))[0]
    print(table)
    return processing.run("gdal:translate", {'INPUT':file,'TARGET_CRS':'ESPG:27700','NODATA':None,
    'COPY_SUBDATASETS':False,'OPTIONS':'',
    'EXTRA':'-co APPEND_SUBDATASET=YES -co RASTER_TABLE={0}'.format(table),'DATA_TYPE':0,'OUTPUT':db})
   
def getFiles(folder,exts=None):
    for root, dirs, files in os.walk(folder, topdown=False):
        for f in files:
            if os.path.splitext(f)[1] in exts or exts is None:
                yield os.path.join(root,f)

db = r'C:\Users\drew.bennett\Documents\mfv_images\test\test.gpkg'
#p = r'C:\Users\drew.bennett\Documents\mfv_images\LEEMING DREW\TIF Images\MFV2_01\ImageInt\MFV2_01_ImageInt_000003.tif'

#r = toGeopackage(p,db)
folder = r'C:\Users\drew.bennett\Documents\mfv_images\LEEMING DREW\TIF Images\MFV2_01\ImageInt'
for i,f in enumerate(getFiles(folder,['.tif'])):
    if i<1000:
        print(f)
        toGeopackage(f,db)
    
    