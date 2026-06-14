@echo off
echo ============================================
echo   FitMind AI Backend - Starting Server...
echo ============================================
echo.

REM Aktifkan virtual environment
call venv\Scripts\activate.bat

REM Cek .env
if not exist .env (
    echo [ERROR] File .env tidak ditemukan!
    echo Silakan copy .env.example ke .env dan isi GEMINI_API_KEY
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

python main.py
pause
