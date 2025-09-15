@echo off
REM SCLab-App post-install wrapper for Windows (NSIS)
REM Uses Python from the installed PREFIX to run setup_sclab_app.py and logs output.

setlocal enabledelayedexpansion

IF "%PREFIX%"=="" (
  echo ERROR: PREFIX is not set. This script must be run by Constructor during install.
  exit /b 1
)

set LOGDIR=%PREFIX%\var\log\sclab-app
set LOGFILE=%LOGDIR%\post_install.log
if not exist "%LOGDIR%" mkdir "%LOGDIR%"

REM Resolve this script directory
set SCRIPT_DIR=%~dp0
if "%SCRIPT_DIR:~-1%"=="\" set SCRIPT_DIR=%SCRIPT_DIR:~0,-1%

set PYWIN=%PREFIX%\python.exe
set SETUP_PY_PREFIX=

(
  echo ==== SCLab-App post_install start (Windows) ====
  echo PREFIX=%PREFIX%
  echo SCRIPT_DIR=%SCRIPT_DIR%
  echo PATH=%PATH%

  if exist "%PYWIN%" (
    echo Using Python: %PYWIN%
    "%PYWIN%" -c "import sys,platform; print('Python', sys.version); print('Platform', platform.platform())"
    echo Running setup_sclab_app.py...
    "%PYWIN%" "%PREFIX%\setup\setup_sclab_app.py"
  ) else (
    echo ERROR: Python interpreter not found at %PYWIN%
    dir "%PREFIX%" 2^>NUL
    exit /b 1
  )
  echo ==== SCLab-App post_install end (Windows) ====
) 1>>"%LOGFILE%" 2>&1

exit /b 0
