



import subprocess

command = 'python "C:\\Users/drew.bennett/AppData/Roaming/QGIS/QGIS3\\profiles\\default/python/plugins\\image_loader\\georeference.py" "D:\\RAF_BENSON\\Data\\2024-01-08\\MFV1_001\\Run 1\\LCMS Module 1\\Images\\IntensityWithoutOverlay\\2024-01-08 10h43m46s LCMS Module 1 000056.jpg" "D:\\RAF_BENSON\\Data\\2024-01-08\\MFV1_001\\Run 1\\LCMS Module 1\\Images\\IntensityWithoutOverlay\\2024-01-08 10h43m46s LCMS Module 1 000056_warped.tif" "[(462300.01615393226, 190869.12957674067, 0, 1250), (462304.614797396, 190867.14791712712, 0, 0), (462298.4124963682, 190865.46511464956, 1038, 1250), (462303.0479257499, 190863.46757566952, 1038, 0)]"'



output = subprocess.run(command,capture_output=True)
print(output)