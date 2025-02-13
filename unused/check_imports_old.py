# -*- coding: utf-8 -*-
"""
Created on Thu Nov 21 13:50:42 2024

@author: Drew.Bennett
"""










from PyQt5.QtWidgets import QMessageBox

import pip

python3 -m ensurepip --default-pip


def checkScipy() -> bool:
    try:
        import scipy
        return True
    except ImportError:
        reply = QMessageBox.question(None , 'missing library:' , 'missing scipy. Install it now?' , QMessageBox.Yes|QMessageBox.No)
        if reply == QMessageBox.Yes:
            pip.main(['install', 'scipy'])
            return True
        return False


def checkImports():
    return checkScipy()


if __name__ in ('__main__','__console__'):
    checkScipy()