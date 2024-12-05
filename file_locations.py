# -*- coding: utf-8 -*-
"""
Created on Wed Dec  4 07:46:39 2024

@author: Drew.Bennett
"""



from os.path import dirname,join,abspath

folder = dirname(__file__)

uiFile = join(folder , 'image_loader_dockwidget_base.ui')

helpPath = r'file:/'+abspath(join(folder,'help','help.html'))

iconPath = join(folder,'icon.png')
      
dbFile = join(folder,'images.db')