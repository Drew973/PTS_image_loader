# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 07:46:39 2024

@author: Drew.Bennett
"""



from os.path import dirname,join,abspath,normpath

folder = dirname(__file__)

uiFile = join(folder , 'image_loader_dockwidget_base.ui')

helpPath = r'file:/'+abspath(join(folder,'help','help.html'))
runsFromLayerHelp = r'file:/'+abspath(join(folder,'help','runs_from_layer.html'))



iconPath = join(folder,'icon.png')
      
dbFile = join(folder,'images.db')



crackStyle = join(folder,'layer_styles','cracking.qml')

centerStyle = join(folder,'layer_styles','center_line.qml')

#centerStyle = os.path.join(os.path.dirname(__file__),'center_line.qml')


makeVrt = normpath(join(folder , 'make_vrt.bat'))

georeference = normpath(join(folder , 'georeference.bat'))
