@echo off
REM ACCSync Build Script for Windows

echo ========================================
echo ACCSync - C# WPF Build Script
echo ========================================

REM Check if .NET SDK is installed
dotnet --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: .NET SDK is not installed or not in PATH
    echo Download from: https://dotnet.microsoft.com/download/dotnet/8.0
    pause
    exit /b 1
)

echo.
echo Choose build option:
echo 1) Development Build (for testing)
echo 2) Release Build (optimized)
echo 3) Publish as standalone executable
echo.
set /p choice="Enter your choice (1-3): "

if "%choice%"=="1" (
    echo Building development version...
    dotnet build
    echo Build complete! Run with: dotnet run
) else if "%choice%"=="2" (
    echo Building release version...
    dotnet build -c Release
    echo Build complete!
) else if "%choice%"=="3" (
    echo Publishing as standalone executable...
    dotnet publish -c Release -o output
    echo.
    echo SUCCESS! Executable created at: output\ACCSync.exe
    echo You can now distribute this .exe file independently
) else (
    echo Invalid choice
    exit /b 1
)

pause
