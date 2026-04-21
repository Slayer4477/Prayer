@echo off
title O'rnatish - Namoz Vaqtlari

echo.
echo  === NAMOZ VAQTLARI - O'RNATISH ===
echo.

cd /d "%~dp0"

REM ── dist papkasi borligini tekshirish ─────────────────────────────────────
if not exist "%~dp0dist\NamozVaqtlari.exe" (
    echo XATO: dist\NamozVaqtlari.exe topilmadi.
    echo Avval build.bat ni ishga tushiring.
    pause & exit /b
)

REM ── D:\Prayer papkasini yaratish ──────────────────────────────────────────
echo [1/3] D:\Prayer papkasi yaratilmoqda...
if not exist "D:\Prayer" mkdir "D:\Prayer"
echo       OK

REM ── dist ichidagi hamma narsani D:\Prayer ga ko'chirish ──────────────────
echo [2/3] Fayllar D:\Prayer ga ko'chirilmoqda...
xcopy /Y /E /I "%~dp0dist\*" "D:\Prayer\" >nul
echo       OK

REM ── Autostart ga qo'shish (joriy foydalanuvchi) ───────────────────────────
echo [3/3] Autostart ga qo'shilmoqda...
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\Run" ^
    /v "NamozVaqtlari" ^
    /t REG_SZ ^
    /d "D:\Prayer\NamozVaqtlari.exe" ^
    /f >nul
echo       OK

echo.
echo =============================================
echo  O'RNATISH TUGADI!
echo.
echo  Fayl joyi   : D:\Prayer\NamozVaqtlari.exe
echo  Autostart   : Yoqildi (Windows bilan birga ishga tushadi)
echo  Hozir ishga : Tushirilmoqda...
echo =============================================
echo.

start "" "D:\Prayer\NamozVaqtlari.exe"