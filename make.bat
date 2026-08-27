@echo off
chcp 65001 >nul
setlocal
REM  ออกชีทครบชุด: นักเรียน + ครู + แปลง PDF
REM  make.bat [easy^|std^|hard] [จำนวนข้อ] [เลขชุด] [seed] [วิชา]
REM  ตัวอย่าง: make.bat std 20 1
REM           make.bat std 20 1 0 tgat2
set MIX=%~1
set NUM=%~2
set SETNO=%~3
set SD=%~4
set SUBJ=%~5
if "%MIX%"==""   set MIX=std
if "%NUM%"==""   set NUM=20
if "%SETNO%"=="" set SETNO=1
if "%SD%"==""    set SD=0
if "%SUBJ%"==""  set SUBJ=tpat3
set TPAT_SEED=%SD%
set BASE=out\%SUBJ%_%MIX%_%SETNO%

echo [1/4] สร้างคลังโจทย์ ...
python gen.py
if errorlevel 1 goto err

echo [2/4] ประกอบชีทนักเรียน ...
node build.js --subject %SUBJ% --mix %MIX% --n %NUM% --set %SETNO% --out "%BASE%_นักเรียน.docx"
if errorlevel 1 goto err

echo [3/4] ประกอบฉบับครู (มีเฉลย) ...
node build.js --subject %SUBJ% --mix %MIX% --n %NUM% --set %SETNO% --key --out "%BASE%_ครู.docx"
if errorlevel 1 goto err

echo [4/4] แปลงเป็น PDF ด้วย Word ...
powershell -ExecutionPolicy Bypass -File topdf.ps1 "%BASE%_นักเรียน.docx" "%BASE%_ครู.docx"

echo.
echo เสร็จแล้ว ดูในโฟลเดอร์ out
goto end

:err
echo.
echo ล้มเหลว - อ่านข้อความด้านบน

:end
endlocal
