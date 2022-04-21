from image_loader import generate_details


def testGenerateRun():
    file = r'C:/Users/drew.bennett/Documents/mfv_images/LEEMING DREW/TIF Images\MFV2_01\ImageInt\MFV2_01_ImageInt_000000.tif'
    result = generate_details.generateRun(file)
    assert result=='MFV2_01'
    
def testGenerateRun2():
    file = r'IntensityWithoutOverlay,TXY_Y,1,6,D:\TIF Images\TXY_Y\ImageInt\TXY_Y_ImageInt_000018.tif' 
    result = generate_details.generateRun(file)
    assert result=='TXY_Y'

 
if __name__=='__main__' or __name__=='__console__':
    testGenerateRun()
    testGenerateRun2()