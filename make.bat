@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion
REM  ออกชีทครบชุด: นักเรียน + ครู เป็น PDF
REM  make.bat [easy^|std^|hard] [จำนวนข้อ] [เลขชุด] [seed] [วิชา]
set MIX=%~1
set NUM=%~2
set SETNO=%~3
set SD=%~4
set SUBJ=%~5
if "%MIX%"==""   set MIX=std
if "%NUM%"==""   set NUM=50
if "%SETNO%"=="" set SETNO=1
if "%SD%"==""    set SD=0
if "%SUBJ%"==""  set SUBJ=tpat3
set TPAT_SEED=%SD%

REM  easy/std/hard -> Beginner/Medium/Advanced
if "%MIX%"=="easy" set LV=Beginner
if "%MIX%"=="std"  set LV=Medium
if "%MIX%"=="hard" set LV=Advanced
if "%LV%"=="" (echo mix ต้องเป็น easy ^| std ^| hard & goto end)

REM  ชื่อวิชาตัวใหญ่
set UP=%SUBJ%
if "%SUBJ%"=="tpat3" set UP=TPAT3
if "%SUBJ%"=="tgat2" set UP=TGAT2
if "%SUBJ%"=="tpat3phys" set UP=TPAT3

REM  ชื่อวีค ใช้ในชื่อโฟลเดอร์และชื่อไฟล์
set WK=คณิต
if "%SUBJ%"=="tpat3phys" set WK=ฟิสิกส์
if "%SUBJ%"=="tgat2" set WK=เหตุผล

REM  รูปแบบชื่อ: [วิชา] วีค ชุดที่ N  ระดับความยากไม่อยู่ในชื่อแล้ว
REM  ดาวยังพิมพ์อยู่บนหัวกระดาษในตัวไฟล์เหมือนเดิม
set NAME=[%UP%] %WK% ชุดที่ %SETNO%
set DIR=out\%NAME%
set STU=%DIR%\%NAME%
set KEY=%DIR%\%NAME% Key
if not exist "%DIR%" mkdir "%DIR%"

echo [1/4] สร้างคลังโจทย์ ...
python gen.py
if errorlevel 1 goto err

echo [2/4] ประกอบชีทนักเรียน ...
node build.js --subject %SUBJ% --mix %MIX% --n %NUM% --set %SETNO% --out "%STU%.docx"
if errorlevel 1 goto err

echo [3/4] ประกอบฉบับครู ...
node build.js --subject %SUBJ% --mix %MIX% --n %NUM% --set %SETNO% --key --out "%KEY%.docx"
if errorlevel 1 goto err

echo [4/5] แปลงเป็น PDF ...
powershell -ExecutionPolicy Bypass -File topdf.ps1 "%STU%.docx" "%KEY%.docx"
del "%STU%.docx" "%KEY%.docx" 2>nul

echo [5/5] ทำรูปให้คม (Word บีบรูปเหลือ 200 dpi ตอน export) ...
python sharpen.py "%STU%.pdf" "%KEY%.pdf"

echo.
echo เสร็จแล้ว  ->  %DIR%
goto end

:err
echo.
echo ล้มเหลว - อ่านข้อความด้านบน

:end
endlocal
