
from image_loader.models.image_model.details import imageDetails

def test():  
    testFolder = r'C:\Users\drew.bennett\Documents\mfv_images\LEEMING DREW\TIF Images\MFV2_01\ImageInt'
    tifs = [os.path.join(testFolder,f) for f in os.listdir(testFolder) if os.path.splitext(f)[-1]=='.tif']
    print(len(tifs))
    details = [imageDetails(t) for t in tifs]
    return details
    
d = test()