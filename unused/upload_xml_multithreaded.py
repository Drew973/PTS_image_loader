# -*- coding: utf-8 -*-
"""
Created on Thu Feb 29 09:45:10 2024

@author: Drew.Bennett
"""
from image_loader.dims import WIDTH,HEIGHT 
from image_loader.db_functions import prepareQuery,defaultDb,runQuery,createDb
from qgis.utils import iface
from qgis.core import QgsTask
import xml.etree.ElementTree as ET
from qgis.core import Qgis
from image_loader import task_dialog


def toFloat(v,default = None):
    try:
        return float(v)
    except:
        return default


def toInt(v,default = None):
    try:
        return int(v)
    except:
        return default


#y value in xml to m
#image y in mm.
#top is ?

def m(frame,imageY):
    return HEIGHT * (frame-1) + imageY * 0.001


#x value in xml to offset
#imageX in mm. offset in m.
def offset(imageX):
    return WIDTH * 0.5 - imageX * 0.001


#convert x and y to m,offset
def xyFromNode(node,sectionId):
    x = toFloat(node.find('X').text)
    y = toFloat(node.find('Y').text)
    if x is not None and y is not None:
        return '{m} {of}'.format(m = m(sectionId,y),of = offset(x))


            
class uploadXmlTask(QgsTask):
    
    def __init__(self,files):
        super().__init__("Upload XML files", QgsTask.CanCancel)
        self.files = files
        self.exception = None
            
    def finished(self, result):
        """This function is called automatically when the task is completed and is
        called from the main thread so it is safe to interact with the GUI etc here"""
        if result is False:
            if self.exception is not None:
                iface.messageBar().pushMessage(str(self.exception))
            else:
                iface.messageBar().pushMessage('Task was cancelled')
        else:
            iface.messageBar().pushMessage('Task Complete')

            

    def run(self):
        db = None
        try:
            db = createDb(name = 'other image_loader connection')

            runQuery('delete from cracks',db = db)
            count = len(self.files)
            cq = prepareQuery('INSERT OR ignore into cracks(section_id,crack_id,len,depth,width,geom) values (?,?,?,?,?,ST_LineFromText(?,0))',db)
            rq = prepareQuery('INSERT OR ignore into rut(frame,chainage,wheelpath,depth,width,x_section,type,deform,geom) values (?,?,?,?,?,?,?,?,PolyFromText(?,0))',db)
            for fileNumber,f in enumerate(self.files):
                db.transaction()

                tree = ET.parse(f)
                root = tree.getroot()
                
                sectionIds = [int(sectionId.text) for sectionId in root.iter('SectionID')]
                
                subcount = len(sectionIds) * 51
                
                
                #1 per frame. len(frames)
                for i,resultFrame in enumerate(root.iter('LcmsAnalyserResultFrame')):
                    
                    
                    sectionId = sectionIds[i]
                    for c in resultFrame.iter('Crack'):
                        if self.isCanceled():
                            return False
                        
                        crackId = toInt(c.find('CrackID').text)
                        length = toFloat(c.find('Length').text)
                        width = toFloat(c.find('WeightedWidth').text)
                        depth = toFloat(c.find('WeightedDepth').text)
                        #xy = [(toFloat(n.find('X').text),toFloat(n.find('Y').text)) for n in crack.iter('Node')]
                    #    xy = [n.find('X').text +' '+n.find('Y').text for n in crack.iter('Node')]
                        xy = [xyFromNode(n,sectionId) for n in c.iter('Node')]
                        xy = [a for a in xy if a is not None]
                        wkt = 'LINESTRING ({xy})'.format(xy = ', '.join(xy))
                        #yield [sectionId,crackId,length,width,depth,wkt]
                       # yield crack(sectionId,crackId,length,width,depth,wkt)

                        cq.bindValue(0,sectionId)
                        cq.bindValue(1,crackId)
                        cq.bindValue(2,length)
                        cq.bindValue(3,width)
                        cq.bindValue(4,depth)
                        cq.bindValue(5,wkt)
                        cq.exec()
                        
                        
                    #ruting every 10 cm. len(frames) * 50
                    for i,rutNode in enumerate(root.iter('RutInformation')):#JointList

                        sectionId = sectionIds[i]
                       # print(i,rutNode)
                        sectionId = sectionIds[i]
                        for rutMeasurement in rutNode.iter('RutMeasurement'):
                            if self.isCanceled():
                                return False
                            
                            
                            rutWidth = float(rutMeasurement.find('Width').text)#mm
                            wheelpath = rutMeasurement.find('LaneSide').text
                            if rutWidth >0 :
                                
                                chainage = float(rutMeasurement.find('Position').text)
                                xSection = float(rutMeasurement.find('CrossSection').text)
                                
                                if wheelpath == "Left":
                                    left = (WIDTH*1000 / 4) - (rutWidth / 2)
                                    right = (WIDTH*1000 / 4) + (rutWidth / 2)
                                else:
                                    left = ((WIDTH*1000 / 4) * 3) - (rutWidth / 2)
                                    right = ((WIDTH*1000 / 4) * 3) + (rutWidth / 2)
                                    
                           #     if i == 1 :
                                    #print('left',left,'right',right)
                            
                                #m as x,offset as y
                                wkt = 'POLYGON(({b} {l}, {t} {l}, {t} {r}, {b} {r}, {b} {l}))'.format(b = chainage,t = chainage+0.1,l = offset(left),r = offset(right))
                                depth = float(rutMeasurement.find('Depth').text)
                
                                rq.bindValue(0,sectionId)
                                rq.bindValue(1,chainage)
                                rq.bindValue(2,rutMeasurement.find('LaneSide').text)
                                rq.bindValue(3,depth)
                                rq.bindValue(4,rutWidth)
                                rq.bindValue(5,xSection)
                                rq.bindValue(6,int(rutMeasurement.find('Type').text))
                                rq.bindValue(7,float(rutMeasurement.find('PercentDeformation').text))
                                rq.bindValue(8,wkt)
                                rq.exec()
                                                        
                self.setProgress(int(100*(fileNumber+1)/count))
                db.commit()
          
            return True
        except Exception as e:
            self.exception = e
            return False
        finally:
            if db is not None:
                db.close()
        
        def wasCanceled(self):
            return self.isCanceled()                
            
        
        def finished(self, result):
            if result:
                iface.messageBar().pushMessage("Image_loader", "loaded XML files", level=Qgis.Info)
            else:
                iface.messageBar().pushMessage("Image_loader", "Error loading XML files", level=Qgis.Info)

#import time
def uploadXML(files,parent = None):
    defaultDb().close()
    d = task_dialog.taskDialog(parent = parent)
    d.setLabelText('Loading XML files...')
    d.show()
    d.startTask(uploadXmlTask(files = files))
    
  
    
    
    
    
    
if __name__ in ('__console__','__main__'):
    f = r'D:\RAF_BENSON\Data\2024-01-08\MFV1_007\Run 7\LCMS Module 1\Results\XML Files\2024-01-08 13h29m23s Video Module 2 MFV1_007 ACD 000.xml'
    f2 = r'D:\RAF_BENSON\Data\2024-01-08\MFV1_004\Run 4\LCMS Module 1\Results\XML Files\2024-01-08 11h50m48s Video Module 2 MFV1_004 ACD 001.xml'
    files = [f,f2]
    uploadXML(files,parent = iface.mainWindow())
    #t = taskMock(files)
    #t.run()
   # print('exception',t.exception)