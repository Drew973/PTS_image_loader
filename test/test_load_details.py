from qgis.core import QgsApplication
from image_loader.image_model import details
from image_loader import load_details


d = details.imageDetails(r'C:/Users/drew.bennett/Documents/mfv_images/LEEMING DREW/TIF Images/MFV2_01/ImageInt/MFV2_01_ImageInt_000000.tif')
d2 = details.imageDetails(r'C:/Users/drew.bennett/Documents/mfv_images/LEEMING DREW/TIF Images/MFV2_01/ImageInt/MFV2_01_ImageInt_000001.tif')

t = load_details.loadDetailsTask([d,d2])
QgsApplication.taskManager().addTask(t)

print(d)