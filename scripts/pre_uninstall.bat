@echo off
REM SCLab-App pre-uninstall cleanup (Windows)
REM Removes Start Menu shortcuts created during post-install.

setlocal enabledelayedexpansion

IF "%PREFIX%"=="" (
  echo WARNING: PREFIX is not set. Continuing cleanup best-effort.
)

set LOGDIR=%PREFIX%\var\log\sclab-app
set LOGFILE=%LOGDIR%\pre_uninstall.log
if not exist "%LOGDIR%" mkdir "%LOGDIR%" 2>nul

set APPDATA_DIR=%APPDATA%
set START_MENU_DIR=%APPDATA_DIR%\Microsoft\Windows\Start Menu\Programs\SCLab-App

(
  echo ==== SCLab-App pre_uninstall start (Windows) ====
  echo PREFIX=%PREFIX%
  echo START_MENU_DIR=%START_MENU_DIR%

  if exist "%START_MENU_DIR%\SCLab-App.lnk" del /f /q "%START_MENU_DIR%\SCLab-App.lnk"
  if exist "%START_MENU_DIR%\SCLab-App Dashboard.lnk" del /f /q "%START_MENU_DIR%\SCLab-App Dashboard.lnk"
  if exist "%START_MENU_DIR%\SCLab-App Server.lnk" del /f /q "%START_MENU_DIR%\SCLab-App Server.lnk"

  REM Remove the folder if empty
  if exist "%START_MENU_DIR%" (
    dir /b "%START_MENU_DIR%" | findstr . >nul || rmdir "%START_MENU_DIR%"
  )

  echo ==== SCLab-App pre_uninstall end (Windows) ====
) 1>>"%LOGFILE%" 2>&1

exit /b 0
