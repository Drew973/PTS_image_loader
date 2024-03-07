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


#geom with ch as x and offset as y
def parseXML(f):
    tree = ET.parse(f)
    root = tree.getroot()
    sectionIds = [int(sectionId.text) for sectionId in root.iter('SectionID')]
    for i,resultFrame in enumerate(root.iter('LcmsAnalyserResultFrame')):
        sectionId = sectionIds[i]
        for crack in resultFrame.iter('Crack'):
            crackId = toInt(crack.find('CrackID').text)
            length = toFloat(crack.find('Length').text)
            width = toFloat(crack.find('WeightedWidth').text)
            depth = toFloat(crack.find('WeightedDepth').text)
            #xy = [(toFloat(n.find('X').text),toFloat(n.find('Y').text)) for n in crack.iter('Node')]
        #    xy = [n.find('X').text +' '+n.find('Y').text for n in crack.iter('Node')]
            xy = [xyFromNode(n,sectionId) for n in crack.iter('Node')]
            xy = [a for a in xy if a is not None]
            wkt = 'LINESTRING ({xy})'.format(xy = ', '.join(xy))
            yield [sectionId,crackId,length,width,depth,wkt]
    
    
def uploadXML(files):
    db = defaultDb()
    q = prepareQuery('INSERT OR ignore into cracks(section_id,crack_id,len,depth,width,geom) values (?,?,?,?,?,ST_LineFromText(?,0))',db)
    for f in files:
        #print('uploading ' + f)
        db.transaction()
        for row in parseXML(f):
            q.bindValue(0,row[0])
            q.bindValue(1,row[1])
            q.bindValue(2,row[2])
            q.bindValue(3,row[3])
            q.bindValue(4,row[4])
            q.bindValue(5,row[5])
            q.exec()
        db.commit()
        
        
if __name__ in ('__console__','__main__'):
    f = r'D:\RAF_BENSON\Data\2024-01-08\MFV1_007\Run 7\LCMS Module 1\Results\XML Files\2024-01-08 13h29m23s Video Module 2 MFV1_007 ACD 000.xml'
    for r in parseXML(f):
        print(r)
        print('')
            
        
#CrackInformation,CrackList,Crack,node,x&y

#in RoadSectionInfo.SectionID

#section 1 is 1st LcmsAnalyserResultFrame node
