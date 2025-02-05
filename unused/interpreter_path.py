# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 09:00:33 2025

@author: Drew.Bennett
"""

from PyQt5.QtCore import QProcess



p = QProcess()
p.start('python "import sys"')
p.waitForFinished()

print(p.program())#python rather than path to interpreter.