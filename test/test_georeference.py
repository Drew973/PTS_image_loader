



import subprocess


prog  = r"C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\georeference.py"
ip  = r"C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\test\1_007\ImageInt\2023-01-21 10h08m11s LCMS Module 1 002703.jpg"
op = r"C:\Users\drew.bennett\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\image_loader\test\1_007\ImageInt\2023-01-21 10h08m11s LCMS Module 1 002703.tif"
gcp = '[(462300.01615393226, 190869.12957674067, 0, 1250), (462304.614797396, 190867.14791712712, 0, 0), (462298.4124963682, 190865.46511464956, 1038, 1250), (462303.0479257499, 190863.46757566952, 1038, 0)]'

command = 'python "{prog}" "{ip}" "{op}" "{gcp}" 27700'.format(prog = prog, ip = ip, op = op, gcp = gcp)






output = subprocess.run(command,capture_output=True)
print(output)