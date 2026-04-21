@echo off
title EXE Builder - Namoz Vaqtlari

echo.
echo  === NAMOZ VAQTLARI - EXE yaratish ===
echo.

cd /d "%~dp0"

python --version >nul 2>&1
if errorlevel 1 (
    echo XATO: Python topilmadi. python.org dan o'rnating.
    pause & exit /b
)

if not exist "namoz_vaqtlari.py" (
    echo XATO: namoz_vaqtlari.py topilmadi.
    echo build.bat ni namoz_vaqtlari.py bilan bir papkaga qo'ying.
    pause & exit /b
)

echo [1/3] pygame numpy pyinstaller o'rnatilmoqda...
pip install pyinstaller pygame numpy --quiet --upgrade
echo       OK

echo.
echo [2/3] EXE yaratilmoqda, 1-3 daqiqa kuting...
echo.

if exist "namoz.ico" (
    python -m PyInstaller --onefile --windowed --name "NamozVaqtlari" --icon="namoz.ico" --clean --noconfirm namoz_vaqtlari.py >nul 2>&1
) else (
    python -m PyInstaller --onefile --windowed --name "NamozVaqtlari" --clean --noconfirm namoz_vaqtlari.py >nul 2>&1
)

if errorlevel 1 (
    echo XATO: EXE yaratilmadi.
    echo Quyidagini qo'lda bajaring:
    echo   python -m PyInstaller --onefile --windowed --name NamozVaqtlari namoz_vaqtlari.py
    pause & exit /b
)

echo [3/3] Qo'shimcha fayllar ko'chirilmoqda...
if exist "config.json"      copy /Y "config.json"      "dist\" >nul
if exist "times_cache.json" copy /Y "times_cache.json" "dist\" >nul
if exist "namoz.ico"        copy /Y "namoz.ico"        "dist\" >nul
echo       OK

echo.
echo =====================================
echo  TAYYOR!  dist\NamozVaqtlari.exe
echo  Endi install.bat ni ishga tushiring.
echo =====================================
echo.
start "" "%~dp0dist"
pause