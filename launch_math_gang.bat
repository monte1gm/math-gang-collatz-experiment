@echo off
setlocal

cd /d "%~dp0"

set "PYTHON_CMD="

where py >nul 2>nul
if %ERRORLEVEL%==0 (
    set "PYTHON_CMD=py -3"
) else (
    where python >nul 2>nul
    if %ERRORLEVEL%==0 (
        set "PYTHON_CMD=python"
    )
)

if not defined PYTHON_CMD (
    echo Python 3 was not found. Install Python 3, then run this launcher again.
    pause
    exit /b 1
)

echo Installing Python dependencies...
%PYTHON_CMD% -m pip install -r requirements.txt
if errorlevel 1 (
    echo Dependency installation failed.
    pause
    exit /b 1
)

echo Starting Math Gang Collatz Experiment...
echo Browser will open at http://localhost:5000/app

start "" /b cmd /c "timeout /t 3 /nobreak >nul & start http://localhost:5000/app"

%PYTHON_CMD% backend\app.py

pause
