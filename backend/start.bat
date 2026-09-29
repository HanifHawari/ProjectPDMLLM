@echo off
cd /d "%~dp0"
echo ============================================
echo   FitMind AI Backend - Starting Server...
echo ============================================
echo.

REM Gunakan virtual environment aktif project
if not exist .venv\Scripts\python.exe (
    echo [ERROR] Virtual environment .venv tidak ditemukan!
    exit /b 1
)

REM Cek .env
if not exist .env (
    echo [ERROR] File .env tidak ditemukan!
    echo Silakan copy .env.example ke .env lalu isi konfigurasi yang diperlukan
    pause
    exit /b 1
)

REM Jalankan FastAPI
echo [OK] Virtual environment aktif
echo [OK] Menjalankan server di http://localhost:8000
echo [OK] API Docs: http://localhost:8000/docs
echo.
echo Tekan CTRL+C untuk stop server
echo.

".venv\Scripts\python.exe" main.py
pause
