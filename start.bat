@echo off

cd /d %~dp0

if exist .venv\Lib\site-packages\ujson*.pyd (
  (
    .venv\Scripts\activate.bat
    python pyeamu.py
  )
) else (
  (
    python -m venv .venv
    .venv\Scripts\activate.bat
    pip install -U -r requirements.txt
    python pyeamu.py
  )
)

echo:
echo Install python with "Add python.exe to PATH" checked
echo https://www.python.org/ftp/python/3.11.1/python-3.11.1-amd64.exe
echo:

pause
