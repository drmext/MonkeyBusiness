@echo off

TITLE MB

cd /d %~dp0

py --version 3 >nul 2>&1
if errorlevel 1 goto install

if not exist .venv\Scripts\activate.bat (
    py -m venv .venv
    .venv\Scripts\activate.bat
    py -m pip install -r requirements.txt
    py main.py
) else (
    .venv\Scripts\activate.bat
    py main.py
)

goto :EOF

:install
echo https://www.python.org/downloads/
echo Install Python with "Add python.exe to PATH" checked
echo:
echo Install the previous version if latest is 3.xx.0
echo - libraries may be broken on 3.xx.0
echo - don't install pre-release version
echo:

pause
