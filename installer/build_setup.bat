@echo off
setlocal

cd /d "%~dp0.."

echo Building PDIE setup.exe from %CD%
echo.

py -m pip install -e ".[installer]"
if errorlevel 1 goto :error

py installer\build_setup.py
if errorlevel 1 goto :error

echo.
echo Created installer: %CD%\dist\installer\setup.exe
exit /b 0

:error
echo.
echo Failed to build setup.exe. Make sure Python, pip, and Inno Setup 6 are installed.
exit /b 1
