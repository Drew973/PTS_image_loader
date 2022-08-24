
from qgis.core import QgsField,QgsFeature,QgsGeometry

fields = QgsFields()
fields.append(QgsField('run',QVariant.String))
fields.append(QgsField('fileName',QVariant.String))
fields.append(QgsField('sectionId',QVariant.Int))
fields.append(QgsField('fromStation_m',QVariant.Int))
fields.append(QgsField('toStation_m',QVariant.Int))



def toFeat(line,run):
    try:
        row = line.strip().split(';')
        feat = QgsFeature(fields)
        feat.setAttributes([run,
        row[0],#fileName
        int(row[1]),#sectionId
        int(row[2]),#fromStation_m
        int(row[3])])#toStation_m
        
        feat.setGeometry(QgsGeometry.fromWkt(row[4]))
       # print(feat.geometry())#valid
        return feat
    except:
        pass
        
def features(file,run):
    for line in file.readlines():
        feat = toFeat(line,run)
        if feat is not None:
            yield feat

def loadFrameLayer(file):
    run = 'MFV2_01'
    #uri = 'Polygon?crs=epsg:27700&field=run:string(40)&field=fileName:string(50)&field=sectionId:int&field=fromStation_m:int&field=toStation_m:int'
    uri = 'Polygon?crs=epsg:27700'
    layer = iface.addVectorLayer(uri, run, "memory")
    layer.dataProvider().addAttributes(fields)
    layer.updateFields()
        
    with open(file,'r') as f:
        layer.dataProvider().addFeatures(features(f,run))
        
    layer.commitChanges()

            


frames = r'C:\Users\drew.bennett\Documents\image_loader\mfv_images\LEEMING DREW\Spatial Data\Text Files\MFV2_01 Spatial Frame Data.txt'    
    
loadFrameLayer(frames)