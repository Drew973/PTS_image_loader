
rem %1 = folder %2 = filelist

cd /D %1
dir *.acdx *.anpp *.jpg *rutacd*.csv /b /s > %2
