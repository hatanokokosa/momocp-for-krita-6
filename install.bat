@echo off
setlocal
set "SRC=%~dp0"
set "KRITA=%APPDATA%\krita"
set "DEST=%KRITA%\pykrita"
echo Installing Momo Color Picker source files for Krita 6 ...
if not exist "%DEST%" mkdir "%DEST%"
xcopy /E /I /Y "%SRC%hsv_picker" "%DEST%\hsv_picker\" >nul
rem Never install the old Windows-only NumPy vendor tree from an older archive.
if exist "%DEST%\hsv_picker\vendor" rmdir /S /Q "%DEST%\hsv_picker\vendor"
copy /Y "%SRC%hsv_picker.desktop" "%DEST%\hsv_picker.desktop" >nul
if not exist "%KRITA%\actions" mkdir "%KRITA%\actions"
copy /Y "%SRC%hsv_picker\actions\hsv_picker.action" "%KRITA%\actions\hsv_picker.action" >nul
echo.
echo This installer copies plugin files only. It does not install NumPy.
echo Windows Krita 6 support is unverified; use the Nix wrapper on Linux for a supported deployment.
echo Restart Krita, then enable it in: Settings ^> Configure Krita ^> Python Plugin Manager.
echo Restart Krita once more to activate the plugin.
pause
