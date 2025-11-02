@echo off
setlocal enabledelayedexpansion

REM ACC Livery Manifest Builder - Windows Batch Script
REM Usage: rebuild_manifest.bat <liveries_folder> [league_name] [version]

if "%1"=="" (
    echo ACC Livery Manifest Builder
    echo.
    echo Usage: rebuild_manifest.bat ^<liveries_folder^> [league_name] [version]
    echo.
    echo Examples:
    echo   rebuild_manifest.bat "C:\path\to\liveries"
    echo   rebuild_manifest.bat "C:\path\to\liveries" "My League" "2.0.0"
    echo.
    pause
    exit /b 1
)

setlocal
set LIVERIES_FOLDER=%1
set LEAGUE_NAME=%2
set VERSION=%3

if "!LEAGUE_NAME!"=="" set LEAGUE_NAME=GT3 Championship
if "!VERSION!"=="" set VERSION=1.0.0

REM Get the directory where this script is located
set SCRIPT_DIR=%~dp0

echo.
echo ====================================
echo ACC Livery Manifest Builder
echo ====================================
echo.
echo Liveries Folder: !LIVERIES_FOLDER!
echo League Name:     !LEAGUE_NAME!
echo Version:         !VERSION!
echo.

REM Run the Python script
python "!SCRIPT_DIR!build_manifest.py" "!LIVERIES_FOLDER!" -l "!LEAGUE_NAME!" -v "!VERSION!" -o "!SCRIPT_DIR!"

if %errorlevel% equ 0 (
    echo.
    echo ====================================
    echo Manifest built successfully!
    echo ====================================
) else (
    echo.
    echo ====================================
    echo Error building manifest
    echo ====================================
)

echo.
pause
