# -*- coding: utf-8 -*-
"""
Created on Thu Aug 18 09:14:45 2022

@author: Drew.Bennett



https://forum.qt.io/topic/122486/creating-a-column-of-editable-checkbox-in-qtableview-using-qitemdelegate/3
"""

from PyQt5 import QtCore
from PyQt5.QtWidgets import QStyledItemDelegate
from PyQt5.QtCore import QVariant
from PyQt5.QtWidgets import QStyleOptionButton,QStyle,QApplication



def toBool(v):
    if isinstance(v,bool):
        return v
    
    if isinstance(v,QVariant):
        return v.toBool()
       
    return bool(v)


class checkBoxDelegate(QStyledItemDelegate):
    """
    A delegate that places a fully functioning QCheckBox in every
    cell of the column to which it's applied
    """
    def __init__(self, parent=None):
        super().__init__(parent=parent)

    def createEditor(self, parent, option, index):
        '''
        Important, otherwise an editor is created if the user clicks in this cell.
        ** Need to hook up a signal to the model
        '''
        return None

    def paint(self, painter, option, index):
        '''
        Paint a checkbox without the label.
        '''
        

        check_box_style_option = QStyleOptionButton()

        if index.flags() & QtCore.Qt.ItemIsEditable:
            check_box_style_option.state |= QStyle.State_Enabled
        else:
            check_box_style_option.state |= QStyle.State_ReadOnly

        
        if toBool(index.data()):
            check_box_style_option.state |= QStyle.State_On
        else:
            check_box_style_option.state |= QStyle.State_Off

        check_box_style_option.rect = self.getCheckBoxRect(option)

        # this will not run - hasFlag does not exist
        #if not index.model().hasFlag(index, QtCore.Qt.ItemIsEditable):
            #check_box_style_option.state |= QStyle.State_ReadOnly

        check_box_style_option.state |= QStyle.State_Enabled

        QApplication.style().drawControl(QStyle.CE_CheckBox, check_box_style_option, painter)



    def editorEvent(self, event, model, option, index):
        '''
        Change the data in the model and the state of the checkbox
        if the user presses the left mousebutton or presses
        Key_Space or Key_Select and this cell is editable. Otherwise do nothing.
        '''
       # print 'Check Box editor Event detected : '
      #  print event.type()
        if not index.flags() & QtCore.Qt.ItemIsEditable:
            return False

     #   print 'Check Box editor Event detected : passed first check'
        # Do not change the checkbox-state
        if event.type() == QtCore.QEvent.MouseButtonPress:
          return False
        if event.type() == QtCore.QEvent.MouseButtonRelease or event.type() == QtCore.QEvent.MouseButtonDblClick:
            if event.button() != QtCore.Qt.LeftButton or not self.getCheckBoxRect(option).contains(event.pos()):
                return False
            if event.type() == QtCore.QEvent.MouseButtonDblClick:
                return True
        elif event.type() == QtCore.QEvent.KeyPress:
            if event.key() != QtCore.Qt.Key_Space and event.key() != QtCore.Qt.Key_Select:
                return False
        else:
            return False

        # Change the checkbox-state
        self.setModelData(None, model, index)
        return True


    def setModelData (self, editor, model, index):
        '''
        The user wanted to change the old state in the opposite.
        '''
       # print 'SetModelData'
        newValue = not toBool(index.data())
       # print 'New Value : {0}'.format(newValue)
        model.setData(index, newValue, QtCore.Qt.EditRole)



    def getCheckBoxRect(self, option):
        check_box_style_option = QStyleOptionButton()
        check_box_rect = QApplication.style().subElementRect(QStyle.SE_CheckBoxIndicator, check_box_style_option, None)
        check_box_point = QtCore.QPoint (option.rect.x() +
                            option.rect.width() / 2 -
                            check_box_rect.width() / 2,
                            option.rect.y() +
                            option.rect.height() / 2 -
                            check_box_rect.height() / 2)
        return QtCore.QRect(check_box_point, check_box_rect.size())