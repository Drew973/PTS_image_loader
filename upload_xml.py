# -*- coding: utf-8 -*-
"""
Created on Thu Feb 29 09:45:10 2024

@author: Drew.Bennett
"""
from image_loader.dims import WIDTH,HEIGHT 
from image_loader.db_functions import prepareQuery,defaultDb

import xml.etree.ElementTree as ET

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


# x value in xml to offset
def offset(imageX):
    return WIDTH * 0.5 - imageX * 0.001


#convert x and y to m,offset
def xyFromNode(node,sectionId):
    x = toFloat(node.find('X').text)
    y = toFloat(node.find('Y').text)
    if x is not None and y is not None:
        return '{m} {of}'.format(m = m(sectionId,y),of = offset(x))


from collections import namedtuple

crack = namedtuple("crack", "sectionId,crackId,length,width,depth,wkt") # class
rut = namedtuple("rut", "frame,chainage,wheelpath,depth,width,xSection,tp,pctDeform,wkt") # class


#xml files have ~5000 lines of text per 5m frame. LOL.

#geom with ch as x and offset as y
def parseXML(f):
    tree = ET.parse(f)
    root = tree.getroot()
    
    sectionIds = [int(sectionId.text) for sectionId in root.iter('SectionID')]
    
    for i,resultFrame in enumerate(root.iter('LcmsAnalyserResultFrame')):
        sectionId = sectionIds[i]
        for c in resultFrame.iter('Crack'):
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
            yield crack(sectionId,crackId,length,width,depth,wkt)
            
            
    for i,rutNode in enumerate(root.iter('RutInformation')):#JointList
        sectionId = sectionIds[i]
       # print(i,rutNode)
        sectionId = sectionIds[i]
        for rutMeasurement in rutNode.iter('RutMeasurement'):
            rutWidth = float(rutMeasurement.find('Width').text)*0.001#mm
            wheelpath = rutMeasurement.find('LaneSide').text
            if rutWidth >0 :
                
             #   chainage = m(sectionId,float(rutMeasurement.find('Position').text))
                chainage = float(rutMeasurement.find('Position').text)
                xSection = float(rutMeasurement.find('CrossSection').text)
                
                if wheelpath == "Left":
                    left = offset((WIDTH / 4) - (rutWidth / 2))
                    right = offset((WIDTH / 4) + (rutWidth / 2))
                else:
                    left = offset(((WIDTH / 4) * 3) - (rutWidth / 2))
                    right = offset(((WIDTH / 4) * 3) + (rutWidth / 2))

            
                wkt = 'POLYGON(({b} {l}, {t} {l}, {t} {r}, {b} {r}, {b} {l}))'.format(b = chainage,t = chainage+xSection,l = left,r=right )


                yield rut(frame = sectionId,
                chainage = chainage,
                wheelpath = rutMeasurement.find('LaneSide').text,
                depth = rutMeasurement.find('Depth').text,
                width = rutWidth,
                xSection = xSection,
                tp = rutMeasurement.find('Type').text,
                pctDeform = rutMeasurement.find('PercentDeformation').text,
                wkt = wkt
                )
            
           
def uploadXML(files):
    db = defaultDb()
    cq = prepareQuery('INSERT OR ignore into cracks(section_id,crack_id,len,depth,width,geom) values (?,?,?,?,?,ST_LineFromText(?,0))',db)
    rq = prepareQuery('INSERT OR ignore into rut(frame,chainage,wheelpath,depth,width,x_section,type,deform,geom) values (?,?,?,?,?,?,?,?,PolyFromText(?,0))',db)
    for f in files:
        #print('uploading ' + f)
        db.transaction()
        for row in parseXML(f):
            if isinstance(row,crack):
                for i,v in enumerate(row):
                    cq.bindValue(i,row[i])
                cq.exec()
            if isinstance(row,rut):
                for i,v in enumerate(row):
                    rq.bindValue(i,row[i])
                rq.exec()
        db.commit()
        
        
if __name__ in ('__console__','__main__'):
    f = r'D:\RAF_BENSON\Data\2024-01-08\MFV1_007\Run 7\LCMS Module 1\Results\XML Files\2024-01-08 13h29m23s Video Module 2 MFV1_007 ACD 000.xml'
    for i,r in enumerate(parseXML(f)):
        if isinstance(r,rut) and i<1000:
            print(r)
        #print(r)
       # print('')
            
        
#CrackInformation,CrackList,Crack,node,x&y

#in RoadSectionInfo.SectionID

#section 1 is 1st LcmsAnalyserResultFrame node
