@echo off

cd /d %~dp0

if exist .venv\Lib\site-packages\ujson*.pyd (
    (
        REM goto :make_venv_portable
        :start_server
        .venv\Scripts\activate.bat && python pyeamu.py
    )
) else (
    (
        :create_venv
        python -m venv .venv
        .venv\Scripts\activate.bat
        pip install -U -r requirements.txt
        python pyeamu.py
    )
)

echo:
echo Install python with "Add python.exe to PATH" checked
echo https://www.python.org/ftp/python/3.11.2/python-3.11.2-amd64.exe
echo:

pause

goto :eof

:make_venv_portable
set pyvenv="%~dp0.venv\pyvenv.cfg"
set pyvenvtemp="%~dp0.venv\pyvenv.tmp"
for /f "tokens=*" %%i in ('python -V') do set pyver=%%i
for /f %%i in ('where python') do set pypath=%%i
set v=home version executable command
for %%a in (%v%) do for /f "tokens=*" %%i in ('findstr /b %%a %pyvenv%') do set %%a=%%i
if exist %pyvenvtemp% del %pyvenvtemp%
setlocal enabledelayedexpansion
(
    for /f "tokens=1* delims=:" %%a in ('findstr /n "^" %pyvenv%') do (
        set "line=%%b"
        if "!line!"=="%home%" (set line=home = %pypath:~0,-11%)
        if "!line!"=="%version%" (set line=version = %pyver:~7%)
        if "!line!"=="%executable%" (set line=executable = %pypath%)
        if "!line!"=="%command%" (set line=command = %pypath% -m venv %~dp0.venv)
        echo(!line!
    )
) > %pyvenvtemp%
endlocal
del %pyvenv%
rename %pyvenvtemp% pyvenv.cfg

set activate="%~dp0.venv\Scripts\activate.bat"
set activatetemp="%~dp0.venv\Scripts\activate.tmp"
for /f "tokens=*" %%i in ('findstr "VIRTUAL_ENV=" %activate%') do set virtual=%%i
if exist %activatetemp% del %activatetemp%
setlocal enabledelayedexpansion
(
    for /f "tokens=1* delims=:" %%a in ('findstr /n "^" %activate%') do (
        set "line=%%b"
        if "!line!"=="%virtual%" (set line=set VIRTUAL_ENV=%~dp0.venv)
        if "!line!"=="END" (set line=:END)
        echo(!line!
    )
) > %activatetemp%
endlocal
del %activate%
rename "%activatetemp%" activate.bat
goto :start_server
