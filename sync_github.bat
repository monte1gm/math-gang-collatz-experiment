@echo off
setlocal

cd /d "%~dp0"

set "GIT=%~dp0.tools\mingit\cmd\git.exe"

if not exist "%GIT%" (
    echo Portable Git was not found at:
    echo %GIT%
    echo.
    echo Use .tools\mingit\cmd\git.exe directly or reinstall portable Git.
    pause
    exit /b 1
)

echo Current repository status:
"%GIT%" status --short --branch
echo.

set "MSG=%~1"
if "%MSG%"=="" (
    set /p MSG=Commit message [Update project]: 
)
if "%MSG%"=="" set "MSG=Update project"

"%GIT%" add .
if errorlevel 1 (
    echo Failed to stage changes.
    pause
    exit /b 1
)

"%GIT%" diff --cached --quiet
if errorlevel 1 (
    "%GIT%" commit -m "%MSG%"
    if errorlevel 1 (
        echo Commit failed.
        pause
        exit /b 1
    )
) else (
    echo No new changes to commit.
)

"%GIT%" push -u origin main
if errorlevel 1 (
    echo Push failed.
    pause
    exit /b 1
)

echo.
echo GitHub sync complete.
pause
