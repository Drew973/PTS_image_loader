# -*- coding: utf-8 -*-

# Resource object code
#
# Created by: The Resource Compiler for PyQt5 (Qt v5.15.2)
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore

qt_resource_data = b"\
\x00\x00\x01\x01\
\x89\
\x50\x4e\x47\x0d\x0a\x1a\x0a\x00\x00\x00\x0d\x49\x48\x44\x52\x00\
\x00\x00\x17\x00\x00\x00\x18\x08\x06\x00\x00\x00\x11\x7c\x66\x75\
\x00\x00\x00\x01\x73\x52\x47\x42\x00\xae\xce\x1c\xe9\x00\x00\x00\
\x04\x67\x41\x4d\x41\x00\x00\xb1\x8f\x0b\xfc\x61\x05\x00\x00\x00\
\x09\x70\x48\x59\x73\x00\x00\x0e\xc3\x00\x00\x0e\xc3\x01\xc7\x6f\
\xa8\x64\x00\x00\x00\x96\x49\x44\x41\x54\x48\x4b\xed\x96\x41\x0e\
\x80\x20\x0c\x04\x8b\x7c\x86\xff\xff\x8f\xa8\x8d\xa0\x08\x4b\x39\
\xb4\x3d\x98\x38\x89\x81\x28\x6e\x96\xc1\x83\x61\x3f\x21\x27\xb6\
\x32\xba\xf0\x87\x43\x54\x07\x1a\x42\x28\xb3\x87\x36\x4e\xd5\x9c\
\x83\xa4\x6e\x6a\x2d\x6d\xfb\x94\x52\x99\x5d\x98\x69\xc9\x39\x53\
\x8c\xf1\xb5\x93\x3b\x1c\xf9\x43\xd4\x97\xdb\xf5\xb3\x7e\x83\x16\
\x5e\xd8\x5f\x88\x7a\x7f\xf6\x9c\x81\xce\x6b\xab\xd5\x6e\xa4\x60\
\xc6\xf5\x3b\x1f\xc2\xfb\xd6\xab\xf6\x12\x53\xe7\x16\x88\xce\xb5\
\xc0\xf0\x6f\x36\xb7\x0a\x66\xe0\x81\xb6\xa3\x06\xa8\xc5\x0a\xa8\
\x85\x5b\x5b\xe8\x71\x3d\x50\xc7\x5f\x0b\xa2\x03\xeb\xb0\x53\x84\
\x1b\xb3\x81\xac\x00\x00\x00\x00\x49\x45\x4e\x44\xae\x42\x60\x82\
\
"

qt_resource_name = b"\
\x00\x07\
\x07\x3b\xe0\xb3\
\x00\x70\
\x00\x6c\x00\x75\x00\x67\x00\x69\x00\x6e\x00\x73\
\x00\x0c\
\x0c\x33\x81\xa2\
\x00\x69\
\x00\x6d\x00\x61\x00\x67\x00\x65\x00\x5f\x00\x6c\x00\x6f\x00\x61\x00\x64\x00\x65\x00\x72\
\x00\x08\
\x0a\x61\x5a\xa7\
\x00\x69\
\x00\x63\x00\x6f\x00\x6e\x00\x2e\x00\x70\x00\x6e\x00\x67\
"

qt_resource_struct_v1 = b"\
\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x01\
\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x02\
\x00\x00\x00\x14\x00\x02\x00\x00\x00\x01\x00\x00\x00\x03\
\x00\x00\x00\x32\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\
"

qt_resource_struct_v2 = b"\
\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x01\
\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x02\x00\x00\x00\x01\x00\x00\x00\x02\
\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x14\x00\x02\x00\x00\x00\x01\x00\x00\x00\x03\
\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x32\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\
\x00\x00\x01\x80\x02\xe1\x1f\xb3\
"

qt_version = [int(v) for v in QtCore.qVersion().split('.')]
if qt_version < [5, 8, 0]:
    rcc_version = 1
    qt_resource_struct = qt_resource_struct_v1
else:
    rcc_version = 2
    qt_resource_struct = qt_resource_struct_v2

def qInitResources():
    QtCore.qRegisterResourceData(rcc_version, qt_resource_struct, qt_resource_name, qt_resource_data)

def qCleanupResources():
    QtCore.qUnregisterResourceData(rcc_version, qt_resource_struct, qt_resource_name, qt_resource_data)

qInitResources()
