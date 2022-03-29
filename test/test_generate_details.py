from image_loader import generate_details


def testGenerateRun():
    file = r'C:/Users/drew.bennett/Documents/mfv_images/LEEMING DREW/TIF Images\MFV2_01\ImageInt\MFV2_01_ImageInt_000000.tif'
    result = generate_details.generateRun(file)
    assert result=='MFV2_01'
    
    
if __name__=='__main__' or __name__=='__console__':
    testGenerateRun()