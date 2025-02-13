# -*- coding: utf-8 -*-
"""
Created on Thu Feb 29 09:45:10 2024

@author: Drew.Bennett
"""
from image_loader.dims import WIDTH, HEIGHT
from image_loader.db_functions import prepareQuery, defaultDb
from image_loader.type_conversions import asBool,asInt,asFloat

from qgis.utils import iface
import xml.etree.ElementTree as ET
from PyQt5.QtWidgets import QProgressDialog, QApplication
import numpy as np
import os
import gzip
from qgis.core import Qgis




# y value in xml to m
# image y in mm.
# top is ?

def m(frame, imageY):
    return HEIGHT * (frame-1) + imageY * 0.001


# x value in xml to offset
# imageX in mm. offset in m.
def offset(imageX):
    return WIDTH * 0.5 - imageX * 0.001


# convert x and y to m,offset
def xyFromNode(node, sectionId):
    x = asFloat(node.find('X').text)
    y = asFloat(node.find('Y').text)
    if x is not None and y is not None:
        return '{m} {of}'.format(m=m(sectionId, y), of=offset(x))


#wkt str for polygon from iterable like [(x,y)]
def polyWkt(points):
    newPoints = []
    
    for p in points:
        newPoints.append('{x} {y}'.format(x=p[0],y=p[1]))
    
    if newPoints[0] != newPoints[-1]:
        newPoints.append(newPoints[0])
    
    return 'POLYGON(({p}))'.format(p=','.join(newPoints))

#points = [[0,0],[10,10],[10,0]]
#print(polyWkt(points))



def loadJoints(root, sectionIds,db):
    tjq = prepareQuery(
        query = 'insert OR ignore into transverse_joint_faulting(frame,joint_id,joint_offset,faulting,width,mo_wkb) values (?,?,?,?,?,AsBinary(PolyFromText(?)))',
        db = db)

    # joints
    for i, frame in enumerate(root.iter('LcmsAnalyserResultFrame')):
        #some frames don't have jointList.
        sectionId = sectionIds[i]
        #print('sectionId',sectionId)
        
        for jointList in frame.iter('JointList'):

            # print('sectionId',sectionId)
            for joint in jointList.iter('Joint'):
                xVals = np.fromstring(joint.find('FaultMeasurementPositionsX').text,sep = ' ')
                widths = np.fromstring(joint.find('WidthMeasurements').text,sep = ' ')
                faultMeasurements = np.fromstring(joint.find('FaultMeasurements').text,sep = ' ')
    
                for periNum, perimeter in enumerate(joint.iter('Perimeter')):
                    
                    
                    try:
                        jointId = joint.find('JointID').text
                        xVal = float(xVals[periNum])
        
                        nodes = []
                        for node in perimeter.iter('Node'):
                            x = float(node.find('X').text)
                            y = float(node.find('Y').text)
                            nodes.append((x, y))
                            
                            
                            
                        # if x>0 make triangle by averageing first and 2nd point else 3rd and 4th
                        if len(nodes) == 4:
                            if xVal>0:
                                points = np.array([[0.5*(nodes[0][0]+nodes[1][0]),0.5*(nodes[0][1]+nodes[1][1])],
                                          nodes[2],
                                          nodes[3]],dtype = float)
                            else:
                                points = np.array([[0.5*(nodes[2][0]+nodes[3][0]),0.5*(nodes[2][1]+nodes[3][1])],
                                          nodes[0],
                                          nodes[1]],dtype = float)
                                
                            #print('xypoints',points)
                            # m as x,offset as y
                            offsets = np.array([offset(x) for x in points[:,0]])
                            mVals = np.array([m(sectionId,y) for y in points[:,1]])
                            points[:,1] = offsets
                            points[:,0] = mVals
    
                            tjq.bindValue(0, int(sectionId))
                            tjq.bindValue(1, int(jointId))
                            tjq.bindValue(2, int(xVals[periNum]))#offset
                            tjq.bindValue(3, float(faultMeasurements[periNum]))#faulting
                            tjq.bindValue(4, float(widths[periNum]))#width
                            tjq.bindValue(5, polyWkt(points))#wkt
                            #print(polyWkt(points))
                            
                            #print(tjq.boundValues())
                            tjq.exec()
                            
                            
                        if len(nodes)>0 and len(nodes)<4:
                            print('wrong number of nodes',len(nodes))
                    except Exception as e:
                        print(e)
                    


class uploadXmlDialog(QProgressDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAutoClose(False)
        self.setLabelText('Uploading XML files...')


    def uploadFiles(self, files):
        
        self.setRange(0, len(files))
        for i, f in enumerate(files):
            self.setValue(i)
            if self.wasCanceled():
                return
            QApplication.processEvents()
            try: 
                self.uploadFile(f)
            except Exception as e:
                iface.messageBar().pushMessage("Image_loader", 'Error loading {f}. {e}'.format(e = str(e),f = f), level=Qgis.Info)



    def loadCracks(self,root, sectionIds,db):
        cq = prepareQuery('INSERT OR ignore into cracks(section_id,crack_id,len,depth,width,wkt) values (?,?,?,?,?,?)', db)
        # cracks
        # 1 per frame. len(frames)
        for i, resultFrame in enumerate(root.iter('LcmsAnalyserResultFrame')):
            sectionId = sectionIds[i]
            for c in resultFrame.iter('Crack'):
                if self.wasCanceled():
                    return False
                crackId = asInt(c.find('CrackID').text)
                length = asFloat(c.find('Length').text)
                width = asFloat(c.find('WeightedWidth').text)
                depth = asFloat(c.find('WeightedDepth').text)
                xy = [xyFromNode(n, sectionId) for n in c.iter('Node')]
                xy = [a for a in xy if a is not None]
                wkt = 'LINESTRING ({xy})'.format(xy=', '.join(xy))
                cq.bindValue(0, sectionId)
                cq.bindValue(1, crackId)
                cq.bindValue(2, length)
                cq.bindValue(3, width)
                cq.bindValue(4, depth)
                cq.bindValue(5, wkt)
                cq.exec()
                
                          
    def loadRuts(self, root, sectionIds, db):
        
        rq = prepareQuery(
            'INSERT OR ignore into rut(frame,chainage,wheelpath,depth,width,x_section,type,deform,mo_wkb) values (?,?,?,?,?,?,?,?,AsBinary(PolyFromText(?,0)))', db)

        
        # ruting every 10 cm.
        for i, rutNode in enumerate(root.iter('RutInformation')):
            sectionId = sectionIds[i]
           # print(i,rutNode)
            for n, rutMeasurement in enumerate(rutNode.iter('RutMeasurement')):
                if self.wasCanceled():
                    return False

                rutWidth = float(rutMeasurement.find('Width').text)  # mm
                wheelpath = rutMeasurement.find('LaneSide').text
                if rutWidth > 0:

                    chainage = float(rutMeasurement.find('Position').text)
                    xSection = float(
                        rutMeasurement.find('CrossSection').text)

                    if wheelpath == "Left":
                        left = (WIDTH*1000 / 4) - (rutWidth / 2)
                        right = (WIDTH*1000 / 4) + (rutWidth / 2)
                    else:
                        left = ((WIDTH*1000 / 4) * 3) - (rutWidth / 2)
                        right = ((WIDTH*1000 / 4) * 3) + (rutWidth / 2)

               #     if i == 1 :
                        # print('left',left,'right',right)

                    # m as x,offset as y
                    wkt = 'POLYGON(({b} {l}, {t} {l}, {t} {r}, {b} {r}, {b} {l}))'.format(
                        b=chainage, t=chainage+0.1, l=offset(left), r=offset(right))
                    depth = float(rutMeasurement.find('Depth').text)

                    rq.bindValue(0, sectionId)
                    rq.bindValue(1, chainage)
                    rq.bindValue(2, rutMeasurement.find('LaneSide').text)
                    rq.bindValue(3, depth)
                    rq.bindValue(4, rutWidth)
                    rq.bindValue(5, xSection)
                    rq.bindValue(6, int(rutMeasurement.find('Type').text))
                    rq.bindValue(
                        7, float(rutMeasurement.find('PercentDeformation').text))
                    rq.bindValue(8, wkt)
                    rq.exec()

                       
    def uploadFile(self, file):
        # self.setLabelText('uploading {f}'.format(f = file))
        #acdx is actually gzip file
        
        ext = os.path.splitext(file)[-1]
        
        if ext == '.acdx':
            with gzip.open(file,'rb') as f:
                text = f.read().decode(encoding='utf-8')
               # print(text[0:100])
                root = ET.fromstring(text)
                
        if ext == '.xml':
            root = ET.parse(file).getroot()
            
        sectionIds = [int(sectionId.text) for sectionId in root.iter('SectionID')]        
        
        db = defaultDb()
        db.transaction()
        try:
            loadJoints(root, sectionIds, db)
            self.loadCracks(root, sectionIds, db)
            self.loadRuts(root, sectionIds, db)
            db.commit()
            return True

        except Exception as e:
            self.exception = e
            db.rollback()
            raise e
            return False



def uploadXML(files, parent=None):
 #   defaultDb().close()
   # d = task_dialog.taskDialog(parent = parent)
    d = uploadXmlDialog(parent=parent)

    # d.setLabelText('Loading XML files...')
    d.show()
   # d.startTask(uploadXmlTask(files = files))
    d.uploadFiles(files)
    d.close()


if __name__ in ('__console__', '__main__'):
  #  f = r'D:\RAF_BENSON\Data\2024-01-08\MFV1_001\Run 1\LCMS Module 1\Results\XML Files\2024-01-08 10h43m46s Video Module 2 MFV1_001 ACD 012.xml'
 #   f = r'D:\RAF_BENSON\Data\2024-01-08\MFV1_007\Run 7\LCMS Module 1\Results\XML Files\2024-01-08 13h29m23s Video Module 2 MFV1_007 ACD 000.xml'
    # f2 = r'D:\RAF_BENSON\Data\2024-01-08\MFV1_004\Run 4\LCMS Module 1\Results\XML Files\2024-01-08 11h50m48s Video Module 2 MFV1_004 ACD 001.xml'
    f = r'C:\Users\drew.bennett\Documents\temp\acdx_files\2024-01-08 10h43m46s Video Module 2 MFV1_001 ACD 000.acdx'

    
   
    files = [f]
    uploadXML(files, parent=iface.mainWindow())
    # t = taskMock(files)
    # t.run()
   # print('exception',t.exception)
