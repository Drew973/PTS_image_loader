
rem copies data used by image_loader from source folder (%1) to destination folder(%2)
cd /D %1
XCOPY *.jpg %2 /S /Y
XCOPY *.acdx %2 /S /Y
XCOPY "*rutacd*.csv" %2 /S /Y