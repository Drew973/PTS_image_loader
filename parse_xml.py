import xml.etree.ElementTree as ET


f = r'C:\Users\drew.bennett\Documents\mfv_images\LEEMING DREW\Data\MFV2_02\Run 4\LCMS Module 1\Results\XML Files\2022-03-03 13h15m08s Video Module 2 MFV_02 ACD 000.xml'
tree = ET.parse(f)
root = tree.getroot()

for child in root[48]:
    print(child.tag, child.attrib)