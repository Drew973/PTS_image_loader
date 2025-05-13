# -*- coding: utf-8 -*-
"""
Created on Mon Mar 10 15:25:17 2025

@author: Drew.Bennett
"""


from PyQt5.QtSql import QSqlTableModel
from PyQt5.QtCore import Qt
from image_loader import db_functions
from PyQt5.QtWidgets import QApplication
from io import StringIO
import csv
from image_loader.backend import corrections_functions , gps_functions
from image_loader import settings

copyCols = ['frame','line','pixel','new_chainage','new_offset']


class correctionsModel(QSqlTableModel):
    
    
    def __init__(self , parent=None):
        super().__init__(parent , db_functions.defaultDb())
        self.runPk : int = -1
        self.setTable('corrections')
        self.setSort(self.fieldIndex('frame') , Qt.AscendingOrder)
        self.setEditStrategy(QSqlTableModel.OnFieldChange)
        self.select()


    def setRun(self , runPk:int):
        #print('setRun',runPk)
        if runPk >= 0:
           # filt = 'frame >= (select start_frame from runs where runs.pk = {pk}) and frame <= (select end_frame from runs where runs.pk = {pk})'.format(pk = runPk)
            filt = 'run = {pk}'.format(pk = runPk)
        else:
            filt = ''
        self.setFilter(filt)
        #self.select()
      #  print('filt',filt,'rowCount:',self.rowCount())

        
        self.runPk = runPk


    #updates or inserts correction.
    def setCorrection(self , row , frame : int , line : int , pixel : int , m : float, offset : float):
                
        
        t = settings.transformFromDestCrs(4326)

        p = t.transform(gps_functions.point(m = m , offset = offset))
        
        if row >= 0:
            self.setData(self.index(row,self.fieldIndex('frame')),frame)
            self.setData(self.index(row,self.fieldIndex('line')),line)
            self.setData(self.index(row,self.fieldIndex('pixel')),pixel)
            self.setData(self.index(row,self.fieldIndex('new_chainage')),m)
            self.setData(self.index(row,self.fieldIndex('new_offset')),offset)
            self.setData(self.index(row,self.fieldIndex('lon')),p.x())
            self.setData(self.index(row,self.fieldIndex('lat')),p.y())

            
            
            self.sort(self.fieldIndex('frame') , Qt.AscendingOrder)
        else:
            corrections_functions.insertCorrection(frame = frame ,
                                                   line = line,
                                                   pixel = pixel,
                                                   m = m ,
                                                   offset = offset,
                                                   lon = p.x(),
                                                   lat = p.y(),
                                                   run = self.runPk)
            self.select()



    #copy data at row indexes to clipboard 
    def copyRows(self , rows: list):
        t = ''
        cols = [self.fieldIndex(f) for f in copyCols]
        for row in rows:
            data = [str(self.index(row,c).data()) for c in cols]
            t += '\t'.join(data) + '\n'
        QApplication.clipboard().setText(t)



    def paste(self):
        t = StringIO(QApplication.clipboard().text())
        reader = csv.DictReader(t , dialect = csv.excel_tab , fieldnames = copyCols)
        for d in reader:        
            corrections_functions.insertCorrection(frame = int(d['frame']) ,
                                                   line = int(d['line']) , 
                                                   pixel = int(d['pixel']) ,
                                                   m = float(d['new_chainage']) , 
                                                   offset = float(d['new_offset']),
                                                   run = self.runPk
                                                   )
        self.select()



    def drop(self,pks):
        corrections_functions.dropCorrections(pks)
        self.select()



#'select pk , original_m , new_m , original_offset , new_offset from corrections''


if __name__ == '__console__':
    m = correctionsModel()
    print('rowCount' , m.rowCount())