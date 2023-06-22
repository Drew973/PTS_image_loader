import os

from image_loader import correction_dialog,corrections_model,db_functions,test


def testDialog():
    db_functions.createDb()
    d = correction_dialog.correctionDialog()
    model = corrections_model.correctionsModel()
    db_functions.loadGps(file = os.path.join(test.testFolder,'1_007','MFV1_007-rutacd-1.csv'),db = model.database())
    d.setModel(model)
    d.show()
    #model.database().close()
   # model.database().close()
if __name__ == '__console__':
    testDialog()