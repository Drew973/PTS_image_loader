import os

from image_loader import correction_dialog,corrections_model,db_functions,test

d = correction_dialog.correctionDialog()

model = corrections_model.correctionsModel()
db_functions.loadGps(file = os.path.join(test.testFolder,'1_007','MFV1_007-rutacd-1.csv'),db = model.database())
d.setIndex(model.index(0,0))
d.show()