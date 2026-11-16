@echo off
chcp 65001 >nul
if not exist "%~dp0tools\st_find.ps1" (
  echo Сначала распакуйте архив: правый клик по ZIP - "Извлечь все", затем запустите Uninstall.bat из распакованной папки.
  echo Unzip the archive first: right-click the ZIP - "Extract All", then run Uninstall.bat from the unpacked folder.
  echo.
  pause
  exit /b 1
)
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0tools\st_find.ps1" uninstall %*
echo.
pause
