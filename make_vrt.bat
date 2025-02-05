

rem %1 = vrtFile , %2 = textfile
gdalbuildvrt -input_file_list %2  -overwrite -r nearest %1  
rem "ERROR 1: No input dataset specified" with non existant text file
rem gdaladdo %1 -r nearest --config COMPRESS_OVERVIEW DEFLATE 16 32 64 128 256 512