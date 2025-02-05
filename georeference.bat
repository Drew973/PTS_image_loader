@echo off
rem %1:inputFile,%2:intermediate file, %3:outputFile %4:gcp list like '-gcp 0 0 462304.614797396 190867.14791712712 -gcp 1038 1250 462298.4124963682 190865.46511464956' %5 srid
rem could add && gdalmanage delete "%~3%". performance hit.

rem gdal_translate "%~1" "%~2" %~4 -b 1 -b 2 -b 3 -b mask -a_nodata 0 -a_srs %5 && gdalwarp -r mode -of COG -tps -overwrite -co quality=90 -co compress=jpeg -co OVERVIEWS=IGNORE_EXISTING -co ADD_ALPHA=YES -wm 10 "%~2" "%~3" --config COMPRESS_OVERVIEW LZW 


gdal_translate "%~1" "%~2" %~4 -b 1 -a_nodata 0 -a_srs %5 && gdalwarp -r mode -of COG -tps -overwrite -co compress=deflate -co OVERVIEWS=IGNORE_EXISTING -wm 10 "%~2" "%~3" --config COMPRESS_OVERVIEW deflate 


@echo on