# -*- coding: utf-8 -*-
"""
Created on Wed Feb  5 08:23:33 2025

@author: Drew.Bennett


Advanced Navigation Packet Protocol

network packets are usually big endian
"""

import struct
from collections import namedtuple
import math
import csv
import os
    


#packet header like: Longitudinal Redundancy Check: u8
#packet ID: u8
#packet length: u8
#CRC : u16 : 16-bit cyclical redundancy check: 
header = namedtuple('header', ['LRC', 'packetId', 'length', 'CRC'])
def readHeader(b):
    return header._make(struct.unpack('>BBBH',b))



rawGnss = namedtuple('rawGnss', ['time', 'microSeconds', 'lat','lon','height', 'NVel','EVel','DVel','latDev','lonDev','hDev',
                                 'tilt','heading','tiltDev','headingDev','status'])
#https://docs.advancednavigation.com/certus/ANPP/RawGNSSPacket.htm
#angles in radians
#velocities in m/s
def readRawGnss(b):
    return rawGnss._make(struct.unpack('<IIdddffffffffffH',b))


#51
odometer = namedtuple('odometer', ['pulseCount','distance','speed','slip','active'])
def readOdometerState(b):
    return odometer._make(struct.unpack("<ifffBxxx",b))



#odometer
#def readOdometer(b):

position = namedtuple('position', ['lon', 'lat', 'alt', 'seconds','microSeconds','lastOdometer'])

def readAnpp(filePath):
    types = {}
    with open(filePath,'rb') as f:        
        h = True
        lastOdometer = None
        while h:
            try:
                h = readHeader(f.read(5))
                data = f.read(h.length)
                
                if h.packetId == 29:
                    d = readRawGnss(data)
                    yield position(math.degrees(d.lon),math.degrees(d.lat),d.height,d.time,d.microSeconds,lastOdometer)
                    
                if h.packetId == 51:
                    d = readOdometerState(data)
                   # print(d)
                    lastOdometer = d.distance
                    
                    
                    
                types[h.packetId] = h.length               
            except Exception as e:
                h = False
                print(e)
    print(sorted(types.keys()))
        
    
#only used for testing.
def anppToCsv(inputFile):
    outFile  = os.path.splitext(inFile)[0] + '.csv'
    with open(outFile,'w',newline='') as out:
        writer = csv.writer(out)
        writer.writerow(position._fields)#header
        writer.writerows(readAnpp(inFile))    
        
        
        
        


if __name__ in ('__main__','__console__'):
    inFile = r'C:\Users\drew.bennett\Documents\athens_airport\data\2024-10-17\20241017_03\2024-10-17 01h41m32s Gipsi2 Module 1 20241017_03 001.anpp'
    anppToCsv(inFile)

    

#, lon=23.966526363822943 lat=37.952772245293325