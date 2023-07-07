# -*- coding: utf-8 -*-
"""
Created on Thu Jun 22 15:18:48 2023

@author: Drew.Bennett
"""

from PyQt5.QtCore import Qt,QModelIndex
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QStandardItemModel
from image_loader import db_functions



'''
QSQLQueryModel always seems to change row count when query set.
this causes runBox to change currentIndex.
results in changing to 1st run whenever updating data.

replaced with QStandardItemModel to prevent this.
might also make natural sort easier.
'''



#bool -> QColor
def color(marked):
    if marked:
        return QColor('yellow')
    else:
        return QColor('white')   
    
import numpy

    
    

class runsModel(QStandardItemModel):
    
    
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setColumnCount(1)


    def clear(self):
        super().clear()
        self.setColumnCount(1)


   # def addRun(self,run):
    #    existing = [self.index(row,0).data() for row in range(self.rowCount())]        
     #   if not run in existing:
       #     self.appendRow()
        
        

    def addRuns(self,runs):
        runs = numpy.unique(numpy.array([str(run) for run in runs]))
        existing = [self.index(row,0).data() for row in range(self.rowCount())]        
        toAdd = [run for run in runs if not run in existing]        
        if toAdd:
            rc = self.rowCount()            
            self.insertRows(rc,len(toAdd),QModelIndex())#row,count,parent #True
            for i,run in enumerate(toAdd):
                index = self.index(i+rc,0,QModelIndex())
                self.setData(index,str(run))
       
        
        
     #sych with database... 
    def select(self):
        
        print('select')

        q = '''
       select run
        ,max(marked) = 1 as has_marked
        from images group by run 
        '''
        #union
        #select run,False from corrections group by run
        #order by run
        query = db_functions.runQuery(q)
        
        data = {}
        
        while query.next():
            data[str(query.value(0))] = bool(query.value(1))

        for row in reversed(range(self.rowCount())):
            index = self.index(row,0)
            run = index.data()
            if run in data:
                self.setData(index,color(data[run]),Qt.BackgroundColorRole)#BackgroundColorRole
                del data[run]
            else:
                self.takeRow(row)
        
        #print(data)
        #existing runs already removed from data
        self.insertRows(0,len(data))
        for i,run in enumerate(data):
            index = self.index(i,0)
            self.setData(index,run)
            self.setData(index,color(data[run]),Qt.BackgroundColorRole)

       # self.sort(0)# todo: natural sort
            

            
        
def test():
    from PyQt5.QtWidgets import QComboBox
    
   # db_functions.createDb()
    m = runsModel()
   # m.select()
    
    #m.setStringList(['a','b','c'])
    #m.setData(m.index(1,0),QColor('yellow'),Qt.EditRole)
    
    b = QComboBox()
    b.setModel(m)
    m.addRuns(['a','b'])
    m.addRuns(['b','c'])

    b.show()
    return b
    
if __name__ in ('__main__','__console__'):
    b = test()