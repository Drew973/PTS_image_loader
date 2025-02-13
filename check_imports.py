# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 13:50:42 2024

@author: Drew.Bennett
"""


from PyQt5.QtWidgets import QMessageBox
from image_loader import file_locations
import subprocess



def checkImports() -> bool:
    try:
        import scipy
        return True
    except ImportError:
        reply = QMessageBox.question(None , 'Image loader:' , 'missing required libraries(scipy). Setup now?' , QMessageBox.Yes|QMessageBox.No)
        if reply == QMessageBox.Yes:
            subprocess.run(file_locations.setup)
            
            
            return True
        return False



if __name__ in ('__main__','__console__'):
    #checkImports()
    reply = QMessageBox.question(None , 'Image loader:' , 'missing required libraries(scipy). Setup now?' , QMessageBox.Yes|QMessageBox.No)
    if reply == QMessageBox.Yes:
        subprocess.run(file_locations.setup)