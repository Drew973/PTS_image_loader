


for %%f in (*.tif) do (
    echo %%~nf
	::gdal_translate -of Rasterlite -b 1 "%%~nf.tif" RASTERLITE:test.sqlite,table="%%~nf" -co DRIVER=PNG
	gdal_translate -of Rasterlite -b 1 "%%~nf.tif" RASTERLITE:test.sqlite,table="%%~nf" -co COMPRESS=JPEG -co QUALITY=90
)


