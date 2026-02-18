@echo off
echo ================================================
echo    OMEGA v4 TITANIUM - QUICK START
echo ================================================
echo.

:: Check Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found!
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

echo [OK] Python found
echo.

:: Check if .env exists
if not exist ".env" (
    echo [SETUP NEEDED] Creating .env file...
    copy .env.template .env
    echo.
    echo ================================================
    echo   IMPORTANT: Edit .env file now!
    echo ================================================
    echo.
    echo 1. Open .env in notepad
    echo 2. Add your GEMINI_API_KEY
    echo 3. Change passwords
    echo 4. Save and close
    echo.
    notepad .env
)

:: Install dependencies
echo ================================================
echo   Installing dependencies...
echo ================================================
pip install -r requirements.txt
echo.

:: Run app
echo ================================================
echo   Starting OMEGA v4 TITANIUM...
echo ================================================
echo.
echo App will open in your browser at:
echo http://localhost:8501
echo.
echo Press Ctrl+C to stop the server
echo.

streamlit run app.py

pause
