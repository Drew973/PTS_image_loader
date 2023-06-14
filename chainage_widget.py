# -*- coding: utf-8 -*-
"""
Created on Fri May 13 08:40:35 2022

@author: Drew.Bennett



QDoubleSpinBox with:
    option to display marker on map
    set value from map click



needs model to map double to point. with:

    XYToFloat(index,x,y) method
    point is in self.crs
    
    floatToXY(index,value) method. returns (x,y) in model crs
    floatToXY
    
    
    units for chainage.  
    

"""

from PyQt5.QtWidgets import QDoubleSpinBox
from PyQt5.QtCore import QModelIndex


from qgis.gui import QgsMapToolEmitPoint, QgsVertexMarker
from qgis.utils import iface
from qgis.core import QgsCoordinateTransform, QgsProject, QgsPointXY


class marker(QgsVertexMarker):
    # point in project crs
    def __init__(self, point):
        super().__init__(iface.mapCanvas())
        self.setIconSize(20)
        self.setPenWidth(5)
        self.setCenter(point)


class chainageWidget(QDoubleSpinBox):

    def __init__(self, parent=None , mapTool=None):
        super().__init__(parent)
        self.setIndex(QModelIndex())
        
        if mapTool is None:
            self.mapTool = QgsMapToolEmitPoint(iface.mapCanvas())
        else:
            self.mapTool = mapTool
            
        self.markers = []
        #self.mapTool.canvasClicked.connect(self.setFromPoint)
        self.valueChanged.connect(self.updateMarkers)
        self.setSingleStep(0.01)  # 1m
        self.setDecimals(2)
        self.setValue(self.value())


    '''
    set index (QModelIndex).
    index and it's model is used to convert between points and values
    need index in networkModel for section chainage as depends on section.
    any index for run_chainage as only need run and value.
    '''
    def setIndex(self, index):
        
      #  print('setIndex',index)
        self._index = index
        if hasattr(index.model(),'allowedRange'):
            r = index.model().allowedRange(index)
            self.setRange(r[0],r[1])
        try:
            self.setValue(float(index.data()))
        except:
            pass


    def index(self):
        return self._index
    
    
    def getIndex(self):
        return self._index
  
    
  
    # happens after focusOutEvent
    def setFromPoint(self, point):
    #    print('setFromPoint', point)

        if point is not None:
            index = self.getIndex()
            m = index.model()
            if m is not None:
                v = m.pointToFloat(pt=point, crs=QgsProject.instance().crs(), index=index)
                if isinstance(v, float):
                    self.setValue(v)


    #arrows do not call setValue.
    def updateMarkers(self, val):
      #  print('updateMarkers ',val)
        self.removeMarkers()
        i = self.getIndex()
        m = i.model()
        if m is not None:
            transform = QgsCoordinateTransform(m.crs(i), QgsProject.instance().crs(),
                                               QgsProject.instance())  # transform to project crs
            points = [transform.transform(pt) for pt in m.floatToPoints(val, i)]
            # self.marker.setCenter(transform.transform(pt))#needs to be in project crs
            self.markers = [marker(pt) for pt in points]

       # self.index().model().setData(self.index(),val)


    def focusInEvent(self, event):
        iface.mapCanvas().setMapTool(self.mapTool)
     #   self.tool.lastPoint = None
        # self.marker.show()
        for m in self.markers:
            m.show()
        return super().focusInEvent(event)


    # after:
       # chainageDelegate.setModelData
    # happens before setFromPoint and before delegate destroys widget
    def focusOutEvent(self, event):
       # print('chainageWidget.focusOutEvent', event)
       # print(type(event))
        iface.mapCanvas().unsetMapTool(self.mapTool)
        self.hideMarkers()
        #self.removeMarkers()


    def hideMarkers(self):
        for m in self.markers:
            m.hide()


    def removeMarkers(self):
       # print('remove markers')
        for m in self.markers:
            iface.mapCanvas().scene().removeItem(m)


    def deleteLater(self):
      #  print('chainageWidget.deleteLater')
        self.removeMarkers()
        #iface.mapCanvas().unsetMapTool(self.mapTool)
        return super().deleteLater()




  #  def closeEvent(self,event):
   #     print('closeEvent',event.type())
      #  return super().closeEvent(event)