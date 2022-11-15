@echo off

cd /d %~dp0

if exist .venv\Lib\site-packages\six.py (
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
echo Install python and check "Add python.exe to PATH"
echo https://www.python.org/ftp/python/3.10.8/python-3.10.8-amd64.exe
echo:

pause
