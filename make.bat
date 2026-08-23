@echo off
setlocal
REM  usage:  make.bat [easy^|std^|hard] [count] [set-number]
REM  4th arg = seed (different seed = different variant)
REM  example: make.bat hard 50 3 0
set MIX=%~1
set NUM=%~2
set SETNO=%~3
set SD=%~4
if "%MIX%"==""   set MIX=std
if "%NUM%"==""   set NUM=50
if "%SETNO%"=="" set SETNO=1
if "%SD%"==""    set SD=0
set TPAT_SEED=%SD%

echo [1/3] building question bank ...
python gen.py
if errorlevel 1 goto err

echo [2/3] building sheet ...
node build.js --mix %MIX% --n %NUM% --set %SETNO% --out out\TPAT3_%MIX%_%SETNO%_s%SD%.docx
if errorlevel 1 goto err

echo [3/3] converting to pdf ...
set SOF=
where soffice >nul 2>nul && set SOF=soffice
if "%SOF%"=="" if exist "C:\Program Files\LibreOffice\program\soffice.exe" set SOF="C:\Program Files\LibreOffice\program\soffice.exe"
if "%SOF%"=="" if exist "C:\Program Files (x86)\LibreOffice\program\soffice.exe" set SOF="C:\Program Files (x86)\LibreOffice\program\soffice.exe"
if not "%SOF%"=="" (
  %SOF% --headless --convert-to pdf --outdir out out\TPAT3_%MIX%_%SETNO%_s%SD%.docx
) else (
  echo     LibreOffice not found - open the .docx in Word and Save as PDF
)

echo.
echo DONE - look in the "out" folder
goto end

:err
echo.
echo FAILED - read the message above

:end
endlocal
