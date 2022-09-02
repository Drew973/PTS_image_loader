import os
from image_loader.models.details.image_details import imageDetails

def test():
    testFolder = r'C:\Users\drew.bennett\Documents\image_loader\mfv_images\LEEMING DREW\TIF Images\MFV2_01\ImageInt'
    tifs = [os.path.join(testFolder,f) for f in os.listdir(testFolder) if os.path.splitext(f)[-1]=='.tif']
    print(len(tifs))
    details = [imageDetails(t,boundingBox=None) for t in tifs]
    return details
    


if __name__=='__console__':
    d = test()